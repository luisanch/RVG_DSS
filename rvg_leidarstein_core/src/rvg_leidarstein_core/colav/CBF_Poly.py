#!/usr/bin/env python3

"""
Module: cbf_4dof

This module contains the 'cbf_4dof' class, which is a subclass of the 'cbf' 
class and provides control barrier function functionality for a 
four-degree-of-freedom (4DOF) system.
"""

import math
import numpy as np
from rvg_leidarstein_core.simulation.simulation_transform import simulation_transform
from rvg_leidarstein_core.colav.CBF_4DOF import cbf_4dof

from time import time
from model4dof.models.RVG_maneuvering4DOF import Module_RVGManModel4DOF as model


class cbf_poly(cbf_4dof):
    """
    The 'cbf_4dof' class is a subclass of the 'cbf' class and provides control
    barrier functionality for a four-degree-of-freedom (4DOF) system.
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
    ):
        """
        Initialize the cbf_4dof object with the specified parameters.

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
        super(cbf_4dof, self).__init__(
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

    def set_domains(domain_data):
        pass

    def _process_data(self, p, u, z, tq, po, zo, uo, ret_var):
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
            dict: Dictionary containing processed control barrier function data.
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

        parS = {"dt": self.dt, "Uc": 0, "betac": 0}
        # initialize eta and nu
        yaw = math.atan2(z[0], z[1])
        eta = np.array([0, 0, 0, yaw])  # North East Yaw Roll
        nu = np.array([u, 0, 0, 0])  # surge sway yaw roll velocities
        azi, revs = self.infer_azi_revs(u, z)
        thrust_state = np.array([azi, revs])
        x = np.concatenate((eta, nu, thrust_state))

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
        cbf_data = {"p": h_p, "maneuver_start": start_maneuver_at}
        ret_var.put(cbf_data)
        return cbf_data
