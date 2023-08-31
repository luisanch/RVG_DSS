#!/usr/bin/env python3

"""
Module: cbf_poly

This module contains the 'cbf_poly' class, a subclass of 'cbf_4dof', providing control barrier function functionality
for a four-degree-of-freedom (4DOF) system with polygonal domains.

Classes:
- cbf_poly: A subclass of 'cbf_4dof' that provides control barrier function functionality
            for a 4DOF system with polygonal domains.
"""

import math
import numpy as np
from rvg_leidarstein_core.simulation.simulation_transform import simulation_transform
from rvg_leidarstein_core.colav.CBF_4DOF import cbf_4dof
from ..colav.colav_types import CBF_Data

from time import time
from model4dof.models.RVG_maneuvering4DOF import Module_RVGManModel4DOF as model


class cbf_poly(cbf_4dof):
    """
    The 'cbf_poly' class is a subclass of 'cbf_4dof' that provides control
    barrier functionality for a four-degree-of-freedom (4DOF) system with polygonal domains.
    """

    def __init__(
        self,
        safety_radius_m,
        k1=1,
        k2=1,
        k3=1,
        lam=0.5,
        dt=0.2,
        gamma_2=40,
        gamma_1=0.2,
        t_tot=600,
        rd_max=1,
        max_rd=0.18,
        transform=simulation_transform(),
        hyst_w=0.00000001,
    ):
        """
        Initialize the cbf_poly object with the specified parameters.

        Parameters:
            safety_radius_m (float): Safety radius in meters.
            k1 (float, optional): CBF parameter k1. Default is 1.
            k2 (float, optional): CBF parameter k2. Default is 1.
            k3 (float, optional): CBF parameter k3. Default is 1.
            lam (float, optional): CBF parameter lambda. Default is 0.5.
            dt (float, optional): Time step for control barrier function calculation. Default is 0.2 seconds.
            gamma_2 (float, optional): CBF parameter gamma_2. Default is 40.
            gamma_1 (float, optional): CBF parameter gamma_1. Default is 0.2.
            t_tot (float, optional): Total time for CBF calculation. Default is 600 seconds.
            rd_max (float, optional): Maximum value for nominal control rd. Default is 1.
            max_rd (float, optional): Maximum value for rd. Default is 0.18.
            transform (object, optional): Object for coordinate transformations. Default is simulation_transform().
        """
        super(cbf_poly, self).__init__(
            safety_radius_m,
            k1=k1,
            k2=k2,
            k3=k3,
            lam=lam,
            dt=dt,
            gamma_2=gamma_2,
            gamma_1=gamma_1,
            t_tot=t_tot,
            rd_max=rd_max,
            max_rd=max_rd,
            transform=transform,
        )
        self._hyst_w = hyst_w
        self._len_factor = 2.5

    def _sort_data(self):
        """
        Sort and organize the data for processing.

        Returns:
            Tuple: A tuple containing sorted and organized data arrays.
        """
        p = self._gunn_data.p
        u = self._gunn_data.u
        z = self._gunn_data.z
        tq = self._gunn_data.tq
        po = np.zeros((2, self._ais_data_len))
        zo = np.zeros((2, self._ais_data_len))
        uo = np.zeros((self._ais_data_len))
        encounters = [None] * self._ais_data_len
        vessels_len = [None] * self._ais_data_len

        for idx, ais_item in enumerate(self._ais_data):
            po[0, idx] = ais_item.po_x
            po[1, idx] = ais_item.po_y
            uo[idx] = ais_item.uo
            zo[:, idx] = ais_item.zo.T
            encounters[idx] = ais_item.encounter
            vessels_len[idx] = ais_item.length

        return p, u, z, tq, po, zo, uo, encounters, vessels_len

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
        converted_data = CBF_Data(
            p=geo,
            maneuver_start=cbf_data.maneuver_start,
        )

        for line_group in cbf_data.domain_lines:
            converted_line_group = []

            for line in line_group:
                x1 = line["x1"]
                x2 = line["x2"]
                y1 = line["y1"]
                y2 = line["y2"]
                lat1, lon1 = self._transform.xyz_to_coords(x1, y1, lat_o, lon_o)
                lat2, lon2 = self._transform.xyz_to_coords(x2, y2, lat_o, lon_o)
                converted_line_group.append([[lon1, lat1], [lon2, lat2]])

            converted_data.domains.append(converted_line_group)
        return converted_data

    def _get_translated_domains(self, po, zo, encounters, domains, vessels_len):
        """
        Translate and convert domain data to geographic coordinates.

        Parameters:
            po (np.array): Array containing position data.
            zo (np.array): Array containing direction data.
            encounters (list): List of encounter types.
            domains (list): List of domain data.
            vessels_len (list): List of vessel lengths.

        Returns:
            list: List of translated domain data.
        """
        domain_lines = []
        for idx, encounter in enumerate(encounters):
            domain = domains[encounter]
            len = vessels_len[idx]
            pi = po[:, idx]
            ds = np.array(domain["d"]) * len
            zo_init = zo[:, idx]

            course_o = math.atan2(zo_init[0], zo_init[1])

            z_list = zip(domain["z1"], domain["z2"])
            lines = []

            for jdx, z in enumerate(z_list):
                angle = math.atan2(z[0], z[1])
                d = ds[jdx]
                rot = angle + course_o
                sx = pi[0] + d * math.sin(rot)
                sy = pi[1] + d * math.cos(rot)
                slope = (sy - pi[1]) / (sx - pi[0])

                line_length = len * self._len_factor

                ex1 = sx
                ey1 = sy + line_length
                ex2 = sx
                ey2 = sy - line_length

                if slope != 0:
                    p_slope = -1 / slope
                    ex1 = sx + (line_length) / math.sqrt(1 + p_slope * p_slope)
                    ey1 = sy + p_slope * (ex1 - sx)
                    ex2 = sx - (line_length) / math.sqrt(1 + p_slope * p_slope)
                    ey2 = sy - p_slope * (ex1 - sx)

                line = {"x1": ex1, "y1": ey1, "x2": ex2, "y2": ey2}
                lines.append(line)
            domain_lines.append(lines)

        return domain_lines

    def _apply_domain(self, domain, vessel_length, zo_init):
        """
        Apply the selected domain to the own vessel.

        Parameters:
            domain (dict): Domain data.
            vessel_length (float): Vessel length.
            zo_init (np.array): Initial direction data.

        Returns:
            tuple: Tuple containing transformed direction and distance vector.
        """
        domain_len = len(domain["d"])
        dq = np.array(domain["d"]) * vessel_length
        tq_d = np.zeros((2, domain_len))
        course_o = math.atan2(zo_init[0], zo_init[1])
        z_list = zip(domain["z1"], domain["z2"])
        for idx, z in enumerate(z_list):
            angle = math.atan2(z[0], z[1])
            rot = angle + course_o
            tq_d[0][idx] = math.sin(rot)
            tq_d[1][idx] = math.cos(rot)
        return tq_d, dq

    def _select_active_constraint(
        self, tq_d, dq, pe, u, uo, z, zo, B1_p, B2_p, h_p, rd_n
    ):
        """
        Select the active constraint for control barrier function calculation.

        Parameters:
            tq_d (np.array): Vector containing desired orientation.
            dq (np.array): Vector containing distance data.
            pe (np.array): Vector containing position error.
            u (float): Surge velocity.
            uo (float): Surge velocity of other vessels.
            z (np.array): Vector containing orientation data.
            zo (np.array): Vector containing direction data.
            B1_p (float): Previous value of B1.
            B2_p (float): Previous value of B2.
            h_p (int): Previous value of h.
            rd_n (float): Nominal control value.

        Returns:
            tuple: Tuple containing selected active constraint values.
        """
        B1 = dq.T - (tq_d.T @ (pe)).flatten()
        B1_dot = (-tq_d.T @ (u * z - uo * zo)).flatten()
        B2 = B1_dot + (1 / self._gamma_1) * B1
        initializing = False

        if B1_p is None or B2_p is None:
            initializing = True
            B1_p = B1[0]
            B2_p = B2[0]

        if B1_p > 0:
            max_B1 = B1_p
        else:
            max_B1 = 0

        H1 = np.where(B1 <= max_B1)
        if initializing:
            H2 = np.where(B2 <= B2_p)
        else:
            H2 = np.where(B2 <= B2_p - self._hyst_w)
        H = np.intersect1d(H1, H2)

        if H.size > 1:
            h = H[0]
        elif H.size == 0:
            h = h_p
        else:
            h = H

        LfB2 = (1 / self._gamma_1) * B1_dot[h]
        LgB2 = -tq_d[:, h].T @ (u * self._S @ z)
        B2_dot = (LgB2 * rd_n) + LfB2

        return B1[h], B1_dot[h], B2[h], B2_dot, LfB2, LgB2, h

    def _process_data(
        self, domains, encounters, vessels_len, p, u, z, tq, po, zo, uo, ret_var
    ):
        """
        Process the data for control barrier function calculation.

        Parameters:
            p (np.array): Array containing position data.
            u (float): Surge velocity.
            z (np.array): Vector containing orientation.
            tq (np.array): Vector containing desired orientation.
            po (np.array): Array containing position of other vessels.
            zo (np.array): Array containing direction of other vessels.
            uo (np.array): Array containing surge velocity of other vessels.
            ret_var (object): Return variable.

        Returns:
            CBF_Data: Object containing processed control barrier function data.
        """

        self._running = True
        start_time = time()
        maneuver_start = None

        t = 0
        hist_p = np.zeros((2, self._hist_len))

        po_dot = np.multiply(zo, uo)
        po_vec = (
            po.T.reshape((-1, 1))
            + np.arange(self._hist_len) * po_dot.T.reshape((-1, 1)) * self._dt
        )

        parS = {"dt": self.dt, "Uc": 0, "betac": 0}
        # initialize eta and nu
        yaw = math.atan2(z[0], z[1])
        eta = np.array([0, 0, 0, yaw])  # North East Yaw Roll
        nu = np.array([u, 0, 0, 0])  # surge sway yaw roll velocities
        azi, revs = self.infer_azi_revs(u, z)
        thrust_state = np.array([azi, revs])
        x = np.concatenate((eta, nu, thrust_state))
        B1 = None
        B2 = None
        encounter = None
        h = None

        for t in range(self._hist_len):
            if not self._running:
                return None
            hist_p[:, t] = p.T
            rd_n = self._get_nominal_control(z, tq)
            pe = p - po_vec[:, t].reshape(2, -1, order="F")
            pe_norm = np.linalg.norm(pe, axis=0)
            closest = np.argmin(pe_norm)

            if encounters[closest] != encounter:
                # reset for new domain
                B1 = None
                B2 = None

            encounter = encounters[closest]  # get encounter type
            domain = domains[encounter]
            vessel_len = vessels_len[closest]
            ei = pe[:, closest].reshape((2, 1))
            zi = zo[:, closest].reshape((2, 1))
            tq_d, dq = self._apply_domain(domain, vessel_len, zi)
            ui = uo[closest]
            (B1, _, B2, B2_dot, LfB2, LgB2, h) = self._select_active_constraint(
                tq_d=tq_d,
                dq=dq,
                pe=ei,
                u=u,
                uo=ui,
                z=z,
                zo=zi,
                B1_p=B1,
                B2_p=B2,
                h_p=h,
                rd_n=rd_n,
            )

            if B2_dot <= -(1 / self._gamma_2) * B2:
                rd = rd_n
            else:
                a = LfB2 + LgB2 * rd_n + (1 / self._gamma_2) * B2
                b = LgB2
                rd = rd_n - (a @ b.T) / (b * b.T + self._epsilon)
                if maneuver_start is None:
                    maneuver_start = t * self._dt

            azi = self._get_azi(x[8], rd, azi)
            thrust_state = [azi, revs]
            Fw = np.zeros(4)
            x = model.int_RVGMan4(x, thrust_state, Fw, self.parV, self.parA, parS)
            p[0, 0] = x[1]
            p[1, 0] = x[0]
            z[0, 0] = math.sin(x[3])
            z[1, 0] = math.cos(x[3])
            z = z / np.linalg.norm(z)

        if maneuver_start is not None:
            start_maneuver_at = start_time + maneuver_start
        else:
            start_maneuver_at = -1
        translated_domains = self._get_translated_domains(
            po, zo, encounters, domains, vessels_len
        )
        cbf_data = CBF_Data(
            p=hist_p,
            maneuver_start=start_maneuver_at,
            domain_lines=translated_domains,
        )
        ret_var.put(cbf_data)
        return cbf_data
