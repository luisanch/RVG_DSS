#!/usr/bin/env python3

"""
Module: colav_manager

Description:
Control and Collision Avoidance (COLAV) manager responsible for coordinating
the ARPA (Automatic Radar Plotting Aid) and the control barrier function (CBF) modules.
"""

from rvg_leidarstein_core.data_relay.rvg_leidarstein_websocket import (
    rvg_leidarstein_websocket,
)
from rvg_leidarstein_core.simulation.simulation_transform import simulation_transform
from .ARPA import arpa
from .CBF_Poly import cbf_poly
from .encounter_classifier import encounter_classifier
import json
import time
import numpy as np
from dataclasses import asdict


class colav_manager:
    def __init__(
        self,
        enable=True,
        update_interval=1,
        safety_radius_m=25,
        safety_radius_tol=1.5,
        max_d_2_cpa=2000,
        gunnerus_mmsi="",
        websocket=rvg_leidarstein_websocket,
        print_comp_t=False,
        prediction_t=600,
    ):
        """
        Initialize the Collision Avoidance (COLAV) manager.

        Args:
            enable (bool): Flag to enable or disable the COLAV manager. Default is True.
            update_interval (float): Time interval (in seconds) for updating the COLAV system. Default is 1 second.
            safety_radius_m (float): Safety radius in meters for collision avoidance. Default is 200 meters.
            safety_radius_tol (float): Tolerance for the safety radius. Default is 1.5.
            max_d_2_cpa (float): Maximum distance to the closest point of approach. Default is 2000 meters.
            gunnerus_mmsi (str): MMSI (Maritime Mobile Service Identity) of the Gunnerus vessel.
            websocket (class): Websocket class for communication. Default is rvg_leidarstein_websocket.
            print_comp_t (bool): Flag to print computation time. Default is False.
            prediction_t (float): Prediction time in seconds for the COLAV system. Default is 600 seconds.

        Attributes:
            _cbf_message_id (str): Message ID for CBF data.
            _arpa_message_id (str): Message ID for ARPA data.
            _encounters_message_id (str): Message ID for encounters data.
            _gunnerus_data (dict): Gunnerus vessel data for COLAV system.
            _ais_data (dict): AIS (Automatic Identification System) data for COLAV system.
            websocket (class): Websocket class for communication.
            _running (bool): Flag to indicate whether the COLAV manager is running.
            enable (bool): Flag to enable or disable the COLAV manager.
            _update_interval (float): Time interval for updating the COLAV system.
            gunnerus_mmsi (str): MMSI of the Gunnerus vessel.
            _timeout (float): Timeout for updates.
            _transform (simulation_transform): Simulation transformation object.
            _prediction_interval (float): Prediction time interval.
            _safety_radius_m (float): Safety radius in meters.
            _safety_radius_tol (float): Tolerance for safety radius.
            _safety_radius_nm (float): Safety radius in nautical miles.
            _safety_radius_deg (float): Safety radius in degrees.
            _max_d_2_cpa (float): Maximum distance to the closest point of approach.
            print_c_time (bool): Flag to print computation time.
            prediction_t (float): Prediction time for the COLAV system.
            _encounter_classifiers (dict): Dictionary of encounter classifiers.
            _d_enter_up_cpa (float): Distance for entering upper CPA.
            _t_enter_up_cpa (float): Time for entering upper CPA.
            _t_enter_low_cpa (float): Time for entering lower CPA.
            _d_exit_low_cpa (float): Distance for exiting lower CPA.
            _t_exit_low_cpa (float): Time for exiting lower CPA.
            _t_exit_up_cpa (float): Time for exiting upper CPA.
            cbf_domains (dict): Dictionary containing CBF domains data.

        Note:
        - This class coordinates the ARPA and CBF modules for collision avoidance.
        - The attributes are initialized based on the provided arguments and defaults.
        """

        # Initialize message IDs and data storage
        self._cbf_message_id = "cbf"
        self._arpa_message_id = "arpa"
        self._encounters_message_id = "encounters"
        self._gunnerus_data = {}
        self._ais_data = {}

        # Initialize communication and configuration attributes
        self.websocket = websocket
        self._running = False
        self.enable = enable
        self._update_interval = update_interval
        self.gunnerus_mmsi = gunnerus_mmsi
        self._timeout = time.time() + update_interval
        self._transform = simulation_transform()
        self._prediction_interval = update_interval * 2
        self._safety_radius_m = safety_radius_m
        self._safety_radius_tol = safety_radius_tol
        self._safety_radius_nm = self._transform.m_to_nm(safety_radius_m)
        self._safety_radius_deg = self._transform.nm_to_deg(self._safety_radius_nm)
        self._max_d_2_cpa = max_d_2_cpa
        self.print_c_time = print_comp_t
        self.prediction_t = prediction_t
        self._encounter_classifiers = {}
        self._d_enter_up_cpa = safety_radius_m * 1.5
        self._t_enter_up_cpa = 600
        self._t_enter_low_cpa = 0
        self._d_exit_low_cpa = safety_radius_m * 2
        self._t_exit_low_cpa = 0
        self._t_exit_up_cpa = 650
        self.cbf_domains = {
            "SAFE": {
                "d": [],
                "z1": [],
                "z2": [],
            },
            "OVERTAKING_STAR": {
                "d": [],
                "z1": [],
                "z2": [],
            },
            "OVERTAKING_PORT": {
                "d": [],
                "z1": [],
                "z2": [],
            },
            "HEADON": {
                "d": [],
                "z1": [],
                "z2": [],
            },
            "GIVEWAY": {
                "d": [],
                "z1": [],
                "z2": [],
            },
            "STANDON": {
                "d": [],
                "z1": [],
                "z2": [],
            },
        }
        self.load_cbf_domain_data()

        # Initialize ARPA and CBF modules
        self._arpa = arpa(
            safety_radius_m=self._safety_radius_m,
            safety_radius_tol=self._safety_radius_tol,
            max_d_2_cpa=self._max_d_2_cpa,
            transform=self._transform,
            gunnerus_mmsi=self.gunnerus_mmsi,
        )

        self._cbf = cbf_poly(
            safety_radius_m=self._safety_radius_m,
            transform=self._transform,
            k2=0.5,
            k3=0.5,
            t_tot=self.prediction_t,
        )

    def update_cbf_domain_data(self):
        """
        Update the CBF domains data from the WebSocket communication.

        Returns:
            None
        """
        if "cbf_domains" in self.websocket.received_data:
            if self.cbf_domains == self.websocket.received_data["cbf_domains"]:
                return
            self.cbf_domains = self.websocket.received_data["cbf_domains"]
            json_object = json.dumps(self.cbf_domains, indent=4)
            with open("cbf_domains.json", "w") as outfile:
                outfile.write(json_object)

    def load_cbf_domain_data(self):
        """
        Load CBF domains data from a JSON file.

        Returns:
            None
        """
        # Opening JSON file
        f = open("cbf_domains.json")

        # returns JSON object as
        # a dictionary
        data = json.load(f)

        # Iterating through the json
        for key in data.keys():
            self.cbf_domains[key] = data[key]
        f.close()

    def compose_encounters_message(self):
        """
        Compose an encounters message for sending via WebSocket.

        Returns:
            str: Encounters message in JSON format.
        """
        vessel_ids = self._encounter_classifiers.keys()
        encounters = {}
        for mmsi in vessel_ids:
            encounters[mmsi] = self._encounter_classifiers[mmsi].encounter.value
        json = self._compose_colav_msg(encounters, self._encounters_message_id)
        return json

    def _update_encounter_classifiers(self, rvg_data, ais_data):
        """
        Update encounter classifiers based on AIS data.

        Args:
            rvg_data (RVGData): RVG vessel data.
            ais_data (list): List of AIS (Automatic Identification System) data.

        Returns:
            None
        """
        # Initialize AIS keys
        ais_keys = []

        # Iterate through AIS data to update classifiers
        for ais in ais_data:
            ais_keys.append(ais.mmsi)

            # Create a new encounter classifier if not already present
            if ais.mmsi not in self._encounter_classifiers:
                self._encounter_classifiers[ais.mmsi] = encounter_classifier(
                    d_enter_up_cpa=self._d_enter_up_cpa,
                    t_enter_up_cpa=self._t_enter_up_cpa,
                    t_enter_low_cpa=self._t_enter_low_cpa,
                    d_exit_low_cpa=self._d_exit_low_cpa,
                    t_exit_low_cpa=self._t_exit_low_cpa,
                    t_exit_up_cpa=self._t_exit_up_cpa,
                )

            if ais.mmsi in self._encounter_classifiers:
                # Update encounter classifier based on AIS data
                if ais.safety_params:
                    self._encounter_classifiers[ais.mmsi].get_encounter_type(
                        rvg_course=np.deg2rad(rvg_data.course),
                        ts_course=np.deg2rad(ais.course),
                        e=ais.x_at_r,
                        e_ts=ais.t_x_at_r,
                        n=ais.y_at_r,
                        n_ts=ais.t_y_at_r,
                        v_rvg=rvg_data.u,
                        v_ts=ais.uo,
                        d_at_cpa=self._safety_radius_m,
                        t_2_cpa=ais.t_2_r,
                    )

                else:
                    self._encounter_classifiers[ais.mmsi].get_encounter_type(
                        rvg_course=np.deg2rad(rvg_data.course),
                        ts_course=np.deg2rad(ais.course),
                        e=ais.x_at_cpa,
                        e_ts=ais.o_x_at_cpa,
                        n=ais.y_at_cpa,
                        n_ts=ais.o_y_at_cpa,
                        v_rvg=rvg_data.u,
                        v_ts=ais.uo,
                        d_at_cpa=ais.d_at_cpa,
                        t_2_cpa=ais.t_2_cpa,
                    )

        # Delete encounter classifiers that are no longer needed

        for key in ais_keys:
            if key not in self._encounter_classifiers:
                del self._encounter_classifiers[key]

    def augment_arpa_data(self, arpa_data):
        """
        Augment ARPA (Automatic Radar Plotting Aid) data with encounter information.

        Args:
            arpa_data (list): List of ARPA data entries.

        Returns:
            list: Augmented ARPA data with encounter information.
        """
        for arpa_entry in arpa_data:
            if arpa_entry.mmsi in self._encounter_classifiers:
                id = arpa_entry.mmsi
                arpa_entry.encounter = self._encounter_classifiers[id].encounter.id
                arpa_entry.length = 50  # entry points for width and bredth
                arpa_entry.width = 50  # entry points for width and bredth
        return arpa_data

    def sort_cbf_data(self):
        """
        Sort the control barrier function (CBF) data.

        Returns:
            tuple: A tuple containing the sorted data for the CBF computation.
        """
        return self._cbf._sort_data()

    def update_gunnerus_data(self, data):
        """
        Update the Gunnerus vessel data for the COLAV system.

        Parameters:
            data (dict): A dictionary containing the Gunnerus vessel data.

        Returns:
            None
        """
        self._gunnerus_data = data

    def update_ais_data(self, data):
        """
        Update the AIS (Automatic Identification System) data for the COLAV system.

        Parameters:
            data (dict): A dictionary containing the AIS data.

        Returns:
            None
        """

        message_id = data.message_id
        self._ais_data[message_id] = data

    def _reset_timeout(self):
        """
        Reset the update timeout.

        Returns:
            None
        """
        self._timeout = time.time() + self._update_interval

    def stop(self):
        """
        Stop the COLAV manager.

        Returns:
            None
        """
        self._running = False
        self._cbf.stop()
        print("Colav Manager: Stop")

    def _compose_colav_msg(self, msg, message_id):
        """
        Compose a COLAV message.

        Parameters:
            msg (dict): The message content.
            message_id (str): The message ID.

        Returns:
            str: The composed COLAV message.
        """
        msg_type = "datain"

        content = {"message_id": message_id, "data": msg}

        return json.dumps({"type": msg_type, "content": content}, default=str)

    def update(self):
        """
        Update the COLAV system.

        Returns:
            bool: True if data is available for ARPA and CBF computation, False otherwise.
        """
        self.update_cbf_domain_data()
        self._arpa.update_gunnerus_data(self._gunnerus_data)
        self._arpa.update_ais_data(self._ais_data)
        arpa_gunn_data, arpa_data = self._arpa.get_ARPA_parameters()
        data_is_available = arpa_data and arpa_gunn_data

        if data_is_available:
            self._update_encounter_classifiers(arpa_gunn_data, arpa_data)

            converted_arpa_data = self._arpa.convert_arpa_params(
                arpa_data, arpa_gunn_data
            )

            self.websocket.send(
                self._compose_colav_msg(converted_arpa_data, self._arpa_message_id)
            )
            self.websocket.send(self.compose_encounters_message())
            arpa_data = self.augment_arpa_data(arpa_data)
            self._cbf.update_cbf_data(arpa_gunn_data, arpa_data)
        return data_is_available

    def send_cbf_data(self, cbf_data):
        """
        Send the computed control barrier function (CBF) data.

        Parameters:
            cbf_data (dict): A dictionary containing the computed CBF data.

        Returns:
            None
        """
        converted_cbf_data = self._cbf.convert_data(cbf_data)
        compose_cbf = self._compose_colav_msg(
            asdict(converted_cbf_data), self._cbf_message_id
        )
        self.websocket.send(compose_cbf)

    def start(self):
        """
        Start the COLAV manager.

        Returns:
            None
        """
        if self.enable:
            self._running = True
            print("Colav Manager running...")
