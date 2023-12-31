#!/usr/bin/env python3

"""
Module: cbf

This module contains the 'cbf' class, which provides control barrier functionality.
"""

import math
import numpy as np
import copy
from ..colav.colav_types import CBF_Data
from ..simulation.simulation_transform import simulation_transform
from time import time


class cbf:
    """
    The 'cbf' class provides control barrier functionality for collision avoidance.
    """

    def __init__(
        self,
        safety_radius_m,
        k1=1,
        lam=0.5,
        dt=0.2,
        gamma_2=40,
        gamma_1=0.2,
        t_tot=600,
        rd_max=1,
        max_rd=0.18,
        transform=simulation_transform(),
    ):
        """
        Initialize the cbf object with the specified parameters.

        Parameters:
            safety_radius_m (float): Safety radius in meters.
            k1 (float, optional): CBF parameter k1. Default is 1.
            lam (float, optional): CBF parameter lambda. Default is 0.5.
            dt (float, optional): Time step for control barrier function calculation. Default is 0.2 seconds.
            gamma_2 (float, optional): CBF parameter gamma_2. Default is 40.
            gamma_1 (float, optional): CBF parameter gamma_1. Default is 0.2.
            t_tot (float, optional): Total time for CBF calculation. Default is 600 seconds.
            rd_max (float, optional): Maximum value for nominal control rd. Default is 1.
            max_rd (float, optional): Maximum value for rd. Default is 0.18.
            transform (object, optional): Object for coordinate transformations. Default is simulation_transform().
        """
        self._safety_radius_m = safety_radius_m
        self._gunn_data = {}
        self._ais_data = {}
        self._ais_data_len = 0
        self._S = np.mat("0 -1; 1 0")
        self._k1 = k1
        self._lam = lam
        self._dt = dt
        self._gamma_2 = gamma_2
        self._gamma_1 = gamma_1
        self._epsilon = 0.000001
        self._t_tot = t_tot
        self._rd_max = rd_max
        self._hist_len = int(t_tot / dt)
        self._running = False
        self._max_rd = max_rd

        self._transform = transform

    def update_cbf_data(self, arpa_gunn_data, arpa_data):
        """
        Update the data for control barrier function calculation.

        Parameters:
            arpa_gunn_data (dict): ARPA gunnerus data.
            arpa_data (dict): ARPA data.

        Returns:
            None
        """
        self._gunn_data = copy.deepcopy(arpa_gunn_data)
        self._ais_data = copy.deepcopy(arpa_data)
        self._ais_data_len = len(self._ais_data)
        return

    def _sort_data(self):
        p = self._gunn_data.p
        u = self._gunn_data.u
        z = self._gunn_data.z
        tq = self._gunn_data.tq
        po = np.zeros((2, self._ais_data_len))
        zo = np.zeros((2, self._ais_data_len))
        uo = np.zeros((self._ais_data_len))

        for idx, ais_item in enumerate(self._ais_data):
            po[0, idx] = ais_item.po_x
            po[1, idx] = ais_item.po_y
            uo[idx] = ais_item.uo
            zo[:, idx] = ais_item.zo.T

        return p, u, z, tq, po, zo, uo

    def _get_nominal_control(self, z, tq):
        """
        Calculate the nominal control 'rd' turning rate based on the given input
        vectors 'z' and 'tq'.

        Parameters:
            z (numpy.array): Vector containing the current orientation information.
            tq (numpy.array): Vector containing the current target orientation
            information.

        Returns:
            float: The computed nominal control value 'rd'.
        """
        z_tilde = np.concatenate((tq, self._S @ tq), axis=1).T @ z
        rd = (-self._k1 * z_tilde[1]) / math.sqrt(1 - self._lam**2 * z_tilde[0] ** 2)
        return rd

    def _process_data(self, p, u, z, tq, po, zo, uo, ret_var):
        """
        Process the provided data to calculate control barrier function.

        Parameters:
            p (numpy.array): Vector containing the current position information.
            u (float): Current speed.
            z (numpy.array): Vector containing the current orientation information.
            tq (numpy.array): Vector containing the desired orientation information.
            po (numpy.array): Matrix containing AIS positions.
            zo (numpy.array): Matrix containing AIS orientation information.
            uo (numpy.array): Vector containing AIS speed information.
            ret_var (multiprocessing.Queue): A multiprocessing queue for returning the computed data.

        Returns:
            dict: A dictionary containing the computed control barrier function data.
        """
        self._running = True
        start_time = time()
        maneuver_start = None

        t = 0
        h_p = np.zeros((2, self._hist_len))

        po_dot = np.multiply(zo, uo)
        po_vec = (
            po.T.reshape((-1, 1))
            + np.arange(self._hist_len) * po_dot.T.reshape((-1, 1)) * self._dt
        )
        for t in range(self._hist_len):
            if not self._running:
                return None
            h_p[:, t] = p.T
            rd_n = self._get_nominal_control(z, tq)
            pe = p - po_vec[:, t].reshape(2, -1, order="F")
            pe_norm = np.linalg.norm(pe, axis=0)
            closest = np.argmin(pe_norm)
            ei = pe[:, closest].reshape((2, 1))
            norm_ei = pe_norm[closest]
            zi = zo[:, closest].reshape((2, 1))
            ui = uo[closest]
            B1 = self._safety_radius_m - norm_ei
            LfB1 = -(ei.T @ (u * z - ui * zi)) / norm_ei
            B2 = LfB1 + (1 / self._gamma_1) * B1
            LfB2 = (
                ((ei.T @ (u * z - ui * zi)) ** 2) / norm_ei**3
                - (np.linalg.norm((u * z - ui * zi), axis=0) ** 2) / norm_ei
                + (1 / self._gamma_1) * LfB1
            )
            LgB2 = (-u * ei.T @ self._S @ z) / norm_ei
            B2_dot = LfB2 + LgB2 * rd_n

            if B2_dot <= -(1 / self._gamma_2) * B2:
                rd = rd_n
            else:
                a = LfB2 + LgB2 * rd_n + (1 / self._gamma_2) * B2
                b = LgB2
                rd = rd_n - (a @ b.T) / (b * b.T + self._epsilon)
                if maneuver_start is None:
                    maneuver_start = t * self._dt

            if rd > self._max_rd:
                rd = self._max_rd
            elif rd < -self._max_rd:
                rd = -self._max_rd

            p = p + u * z * self._dt
            z = z + self._S @ z * rd * self._dt
            z = z / np.linalg.norm(z)
        if maneuver_start is not None:
            start_maneuver_at = start_time + maneuver_start
        else:
            start_maneuver_at = -1
        cbf_data = CBF_Data(p=h_p, maneuver_start=start_maneuver_at)
        ret_var.put(cbf_data)
        return cbf_data

    def convert_data(self, cbf_data):
        """
        Convert the computed control barrier function data to geographic coordinates.

        Parameters:
            cbf_data (dict): The dictionary containing the computed control barrier function data.

        Returns:
            dict: A dictionary containing the converted geographic coordinates.
        """
        lat_o = self._gunn_data.lat
        lon_o = self._gunn_data.lon
        geo = []
        for col in range(cbf_data.p.shape[1]):
            x = cbf_data.p[0, col]
            y = cbf_data.p[1, col]
            lat, lon = self._transform.xyz_to_coords(x, y, lat_o, lon_o)
            geo.append([lon, lat])

        converted_data = CBF_Data(p=geo, maneuver_start=cbf_data.maneuver_start)
        return converted_data

    def get_cbf_data(self):
        """
        Retrieve the computed control barrier function data.

        Returns:
            dict: A dictionary containing the computed control barrier function data.
        """
        p, u, z, tq, po, zo, uo = self._sort_data()
        cbf_data = self._process_data(p, u, z, tq, po, zo, uo)
        return cbf_data

    def stop(self):
        """
        Stop the control barrier function computation.

        Returns:
            None
        """
        self._running = False
