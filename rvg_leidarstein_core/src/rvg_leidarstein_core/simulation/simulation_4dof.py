#!/usr/bin/env python3
"""
simulation_4dof.py

This module provides the `simulation_4dof` class, which extends the `simulation_server` 
class to simulate the movement and behavior of a 4-degrees-of-freedom (4DOF) 
maneuvering vessel. It uses a mathematical model (`Module_RVGManModel4DOF`)
to calculate the vessel's position and orientation based on inputs such as speed,
course, and current conditions. The simulation generates AIS-like messages for
the maneuvering vessel, and the messages are sent via a WebSocket to be relayed
to the environment for visualization and collision avoidance. 
"""
import math
from datetime import datetime
import numpy as np
from time import time
from model4dof.models.RVG_maneuvering4DOF import Module_RVGManModel4DOF as model
from ..data_relay.rvg_leidarstein_websocket import rvg_leidarstein_websocket
from ..colav.colav_manager import colav_manager
from ..serializers.serializer import serializer
from .simulation_server import simulation_server


class simulation_4dof(simulation_server):
    """
    A class that extends the `simulation_server` to simulate the movement and 
    behavior of a 4-degrees-of-freedom (4DOF) maneuvering vessel. It utilizes a 
    mathematical model (`Module_RVGManModel4DOF`) to calculate the vessel's position 
    and orientation based on inputs such as speed, course, and current conditions. 
    The simulation generates AIS-like messages for the maneuvering vessel, and these 
    messages are sent via a WebSocket to be relayed to the environment for visualization
    and collision avoidance.

    Parameters:
    ----------
    websocket : rvg_leidarstein_websocket
        The WebSocket object used to send AIS-like messages to the environment. 
        Default is rvg_leidarstein_websocket.
    serializer : serializer
        The serializer object used to handle the AIS-like messages for the simulation. 
        Default is serializer.
    distance_filter : float, optional
        The distance threshold used to filter AIS-like messages. Messages with positions 
        too far from the initial position
        of the vessel will be ignored. Default is None, meaning no distance filtering.
    predicted_interval : int, optional
        The time interval in seconds for predicting the vessel's position. 
        Default is 30 seconds.
    colav_manager : colav_manager, optional
        The colav_manager object used for collision avoidance. Default is colav_manager.
    filt_order : int, optional
        The order of the Butterworth filter used for data filtering. Default is 3.
    filt_cutfreq : float, optional
        The cutoff frequency of the Butterworth filter. Default is 0.1.
    filt_nyqfreq : float, optional
        The Nyquist frequency of the Butterworth filter. Default is 0.5.
    tmax : int, optional
        The maximum simulation time in seconds. Default is 1 second.
    dt : float, optional
        The time step used in the simulation. Default is 0.1 seconds.
    rvg_init : dict, optional
        A dictionary containing initial parameters for the vessel's state. 
        The dictionary should include the following keys:
        'lat', 'lat_dir', 'lon', 'lon_dir', 'spd_over_grnd', 'true_course', 
        'azi_d', 'revs'. Default is an empty dictionary.
    send_msg_filter : list of str, optional
        A list of message types to be filtered when sending AIS-like messages. 
        Only messages with types present in this list will be sent. Default is ['!AI'].

    Attributes:
    -----------
    The class has various attributes to store simulation parameters, vessel state, 
    and history of AIS-like messages. Some of the important attributes include:

    ais_history : dict
        A dictionary to store the history of AIS-like messages for each vessel.
    state : numpy.ndarray
        An 8-element array representing the vessel's state. The elements are 
        [x, y, z, phi, theta, psi, u, v], where (x, y, z)
        are position coordinates, (phi, theta, psi) are Euler angles, and (u, v) 
        are linear velocity components.
    nu : numpy.ndarray
        A 4-element array representing the vessel's linear and angular velocities. 
        The elements are [u, v, p, r], where (u, v) are linear velocities, and 
        (p, r) are angular velocities.
    eta : numpy.ndarray
        A 4-element array representing the vessel's position and orientation. 
        The elements are [x, y, phi, psi], where (x, y) are position coordinates, 
        and (phi, psi) are Euler angles.
    sim_timer : float
        A timer to keep track of the simulation time.
    sim_buffer : list
        A list to store the buffered AIS-like messages for the simulation.
    """

    def __init__(
        self,
        websocket=rvg_leidarstein_websocket,
        serializer=serializer,
        distance_filter=None,
        predicted_interval=30,
        colav_manager=colav_manager,
        filt_order=3,
        filt_cutfreq=0.1,
        filt_nyqfreq=0.5,
        tmax=1,
        dt=0.1,
        rvg_init={},
        send_msg_filter=["!AI"],
    ):
        super(simulation_4dof, self).__init__(
            serializer,
            websocket,
            distance_filter,
            predicted_interval,
            colav_manager,
            filt_order,
            filt_cutfreq,
            filt_nyqfreq,
        )

        self._send_msg_filter = send_msg_filter
        self._running = False
        self.ais_history = dict()
        self.ais_history_len = 30
        self.rvg_init = rvg_init
        self.parV, self.parA = model.DefaultModelData()
        self.tmax = tmax
        self.dt = dt  # time step
        self.lat = rvg_init["lat"]
        self.lat_dir = rvg_init["lat_dir"]
        self.o_lat = self.transform.deg_2_dec(self.lat, self.lat_dir)
        self.lon = rvg_init["lon"]
        self.lon_dir = rvg_init["lon_dir"]
        self.o_lon = self.transform.deg_2_dec(self.lon, self.lon_dir)
        self.Uc = rvg_init["spd_over_grnd"]  # current speed
        self.betac = rvg_init["true_course"] * math.pi / 180  # current direction
        self.azi = rvg_init["azi_d"]
        self.v = rvg_init["spd_over_grnd"]
        self.revs = rvg_init["revs"]
        self.azi_sat = np.pi / 8
        self.seqnum = 0
        self.state = np.zeros(8)
        self.nu = np.array([self.Uc, 0, 0, 0])  # u v p r
        self.eta = np.array([0, 0, 0, self.betac])  # x y phi psi
        self.sim_timer = 0
        self.sim_buffer = []

    def spoof_gpgga_msg(self, timestamp, lon, lat, alt=12.6):
        """
        Generate a spoofed GPGGA NMEA message with the provided timestamp, latitude, 
        longitude, and altitude.

        Parameters:
        -----------
        timestamp : float
            The timestamp in UNIX time format for the generated message.
        lon : float
            The longitude in decimal degrees for the generated message.
        lat : float
            The latitude in decimal degrees for the generated message.
        alt : float, optional
            The altitude in meters for the generated message. Default is 12.6 meters.

        Returns:
        --------
        dict
            A dictionary representing the spoofed GPGGA message containing various 
            attributes like latitude, longitude,
            altitude, etc.
        """
        lat_ddm, lat_dir = self.transform.dec_2_deg(lat, direction="lat")
        lon_ddm, lon_dir = self.transform.dec_2_deg(lon, direction="lon")
        dtime = datetime.fromtimestamp(timestamp)

        msg = {
            "timestamp": dtime.time(),
            "lat": lat_ddm,
            "lat_dir": lat_dir,
            "lon": lon_ddm,
            "lon_dir": lon_dir,
            "gps_qual": 1,
            "num_sats": "10",
            "horizontal_dil": "1.0",
            "altitude": alt,
            "altitude_units": "M",
            "geo_sep": "41.4",
            "geo_sep_units": "M",
            "age_gps_data": "",
            "ref_station_id": "",
            "unix_time": timestamp,
            "seq_num": self.seqnum,
            "src_id": 3,
            "src_name": "@10.0.8.10:34340",
            "message_id": "$GPGGA",
        }
        self.seqnum = self.seqnum + 1
        return msg

    def spoof_gprmc(self, timestamp, lon, lat, speed, course):
        """
        Generate a spoofed GPRMC NMEA message with the provided timestamp, latitude, 
        longitude, speed, and course.

        Parameters:
        -----------
        timestamp : float
            The timestamp in UNIX time format for the generated message.
        lon : float
            The longitude in decimal degrees for the generated message.
        lat : float
            The latitude in decimal degrees for the generated message.
        speed : float
            The speed over ground in meters per second for the generated message.
        course : float
            The true course angle in degrees for the generated message.

        Returns:
        --------
        dict
            A dictionary representing the spoofed GPRMC message containing various 
            attributes like latitude, longitude,
            speed over ground, true course, etc.
        """
        lat_ddm, lat_dir = self.transform.dec_2_deg(lat, direction="lat")
        lon_ddm, lon_dir = self.transform.dec_2_deg(lon, direction="lon")
        dtime = datetime.fromtimestamp(timestamp)
        speed = self.transform.mps_to_kn(speed)
        msg = {
            "timestamp": dtime.time(),
            "status": "A",
            "lat": lat_ddm,
            "lat_dir": lat_dir,
            "lon": lon_ddm,
            "lon_dir": lon_dir,
            "spd_over_grnd": speed,
            "true_course": course,
            "datestamp": dtime.date(),
            "mag_variation": "4.7",
            "mag_var_dir": "E",
            "unknown_0": "A",
            "unknown_1": "S",
            "unix_time": timestamp,
            "seq_num": self.seqnum,
            "src_id": 3,
            "src_name": "a10.0.8.1",
            "message_id": "$GPRMC",
        }
        self.seqnum = self.seqnum + 1
        return msg

    def spoof_psimsns(self, timestamp, roll, yaw, pitch=0):
        """
        Generate a spoofed PSIMSNS message with the provided timestamp, roll angle, 
        yaw angle, and optional pitch angle.

        Parameters:
        -----------
        timestamp : float
            The timestamp in UNIX time format for the generated message.
        roll : float
            The roll angle of the vessel in degrees for the generated message.
        yaw : float
            The yaw angle of the vessel in degrees for the generated message.
        pitch : float, optional
            The pitch angle of the vessel in degrees for the generated message. 
            Default is 0 degrees.

        Returns:
        --------
        dict
            A dictionary representing the spoofed PSIMSNS message containing various 
            attributes like roll, yaw, pitch, etc.
        """
        dtime = datetime.fromtimestamp(timestamp)
        msg = {
            "msg_type": "SNS",
            "timestamp": dtime.time(),
            "unknown_1": "",
            "tcvr_num": "1",
            "tdcr_num": "1",
            "roll_deg": roll,
            "pitch_deg": pitch,
            "heave_m": "0.00",
            "head_deg": yaw,
            "empty_1": "",
            "unknown_2": "40",
            "unknown_3": "0.000",
            "empty_2": "",
            "checksum": "M121",
            "unix_time": timestamp,
            "seq_num": self.seqnum,
            "src_id": 1,
            "src_name": "@10.0.8.10:39816",
            "message_id": "$PSIMSNS",
        }
        self.seqnum = self.seqnum + 1
        return msg

    def convert_simulation(self, x, timestamps):
        """
        Convert the simulation results into a list of spoofed messages based on 
        the provided simulation state 'x' and timestamps.

        Parameters:
        -----------
        x : numpy array
            The simulation state containing the vessel's position, velocity, and 
            other relevant parameters.
        timestamps : numpy array
            An array of timestamps corresponding to each state in the simulation.

        Returns:
        --------
        list
            A list of spoofed messages, including PSIMSNS, GPGGA, and GPRMC messages.
        """
        out = []
        for i, timestamp in enumerate(timestamps):
            if i % int(len(timestamps) / 2) == 0:
                n, e, roll, psi, surge, sway = x[0:6, i]
                roll = roll * (180 / math.pi)
                psi = psi * (180 / math.pi)
                lat, lon = self.transform.xyz_to_coords(e, n, self.o_lat, self.o_lon)
                speed = math.sqrt(surge**2 + sway**2)
                course = psi + math.atan2(sway, surge) * (180 / math.pi)
                out.append(self.spoof_psimsns(timestamp, roll, psi))
                out.append(self.spoof_gpgga_msg(timestamp, lon, lat))
                out.append(self.spoof_gprmc(timestamp, lon, lat, speed, course))
        return out

    def run_simulation(self):
        """
        Run the 4-degree-of-freedom (4DOF) simulation.

        Returns:
        --------
        tuple
            A tuple containing two elements:
            1. numpy array: A 2D array containing the simulation results (vessel's 
                position, velocity, etc.) over time.
            2. numpy array: An array of timestamps corresponding to each state in 
                the simulation.
        """
        tvec = np.linspace(0, self.tmax, int(self.tmax / self.dt) + 1)

        # dict containing simulation param
        parS = {"dt": self.dt, "Uc": 0, "betac": 0}
        # =============================================================================
        # Initial conditions and allocate memory
        # =============================================================================
        azi = self.azi * math.pi / 180
        thrust_state = np.array([azi, self.revs])  # azimuth angle and revs
        x = np.concatenate((self.eta, self.nu, thrust_state))
        x_out = np.zeros([len(x), len(tvec)])
        simulationStart = time()
        for i1, t in enumerate(tvec):
            # store results
            x_out[:, i1] = x
            u = thrust_state
            # time integration
            Fw = np.zeros(4)

            # ToDo: sometimes it hiccups here, figure out why
            try:
                x = model.int_RVGMan4(x, u, Fw, self.parV, self.parA, parS)
            except:
                pass

        timestamps = tvec + simulationStart
        # sort output
        out = x_out[0:6, :]
        self.eta = x[0:4]
        self.nu = x[4:8]
        return out, timestamps

    def check_incoming_controls(self):
        """
        Check for incoming control data from the websocket and update the vessel's 
        azimuth angle and thrust values accordingly.

        This method checks for the presence of "control_azi" and "control_thrust" 
        keys in the received_data dictionary of the websocket. If these keys are 
        present, it updates the vessel's azimuth angle (self.azi) and thrust value 
        (self.revs) with the corresponding values received from the websocket.

        Returns:
        --------
        None
        """
        if "control_azi" in self.websocket.received_data:
            self.azi = self.websocket.received_data["control_azi"]
        if "control_thrust" in self.websocket.received_data:
            self.revs = self.websocket.received_data["control_thrust"]

    def start(self):
        """
        Start the simulation.

        This method runs the main loop of the simulation. While the simulation is 
        running, it continuously checks for incoming control data from the websocket 
        using the `check_incoming_controls` method. If there is data in the buffer, 
        it checks whether it matches any of the filters specified in `_send_msg_filter`. 
        If a match is found, it sends the data using the `_send` method and removes 
        it from the buffer. It also runs the 4-degree-of-freedom simulation using the 
        `run_simulation` method and converts the results to spoofed messages using 
        the `convert_simulation` method. The simulation results are stored in the 
        `sim_buffer`. When the simulation time exceeds the maximum time (tmax), 
        the next set of 4DOF simulation data is sent using `_send` method from the 
        `sim_buffer` based on their timestamps.

        Returns:
        --------
        None
        """
        self._running = True
        print("Simulation 4DOF Client running...")

        while self._running:
            self.check_incoming_controls()
            if len(self._buffer):  # check if rt data should be sent 
                for filter in self._send_msg_filter:
                    if self._buffer[0]["message_id"].find(filter) == 0:
                        self._send(self._buffer[0])
                self.pop_buffer(0)

            if time() > self.sim_timer + self.tmax:  # get 4dof sim data
                out, timestamps = self.run_simulation()
                self.sim_timer = timestamps[0]
                self.sim_buffer = self.convert_simulation(out, timestamps)

            # send 4dof sim data for rvg
            if len(self.sim_buffer) and time() > self.sim_buffer[0]["unix_time"]:
                self._send(self.sim_buffer[0])
                self.sim_buffer.pop(0)
