#!/usr/bin/env python3

"""
simulation_server.py

A server class for managing simulation data, transformations, and communication.

"""

import numpy as np
from scipy.signal import butter, filtfilt
import json
from .simulation_transform import simulation_transform
from ..serializers.serializer import serializer
from ..data_relay.rvg_leidarstein_websocket import rvg_leidarstein_websocket
from ..colav.colav_manager import colav_manager
import math


class simulation_server:
    """
    A server class for managing simulation data, transformations, and communication.

    Parameters:
    - serializer: The serializer class to use for data serialization (Default: serializer).
    - websocket: The WebSocket class for communication (Default: rvg_leidarstein_websocket).
    - distance_filter: A filter function for processing distance data (Default: None).
    - predicted_interval: The time interval for predicting future states (Default: 30 seconds).
    - colav_manager: The Collision Avoidance Manager class (Default: colav_manager).
    - filt_order: The order of the Butterworth filter for data filtering (Default: 3).
    - filt_cutfreq: The cutoff frequency of the Butterworth filter (Default: 0.1 Hz).
    - filt_nyqfreq: The Nyquist frequency of the Butterworth filter (Default: 0.5 Hz).

    Attributes:
    - _serializer: The serializer instance for data serialization.
    - _buffer: The buffer containing sorted simulation data.
    - _running: A boolean flag indicating if the simulation server is running.
    - transform: An instance of the simulation_transform class for coordinate transformations.
    - ais_history: A dictionary to store AIS message history for collision avoidance.
    - ais_history_len: The maximum length of AIS message history to retain.
    - distance_filter: A filter function for processing distance data (if provided).
    - gunnerus_lat: Latitude of the Gunnerus vessel (if available).
    - gunnerus_lon: Longitude of the Gunnerus vessel (if available).
    - websocket: An instance of the WebSocket class for communication with external systems.
    - _colav_manager: An instance of the Collision Avoidance Manager class.
    - _predicted_interval: The time interval for predicting future states.
    - _butter_b: The numerator coefficients of the Butterworth filter.
    - _butter_a: The denominator coefficients of the Butterworth filter.
    - rvg_state: A dictionary containing the state information of the RVG vessel.
    - rvg_heading: The heading information of the RVG vessel (if available).

    """

    def __init__(
        self,
        serializer=serializer,
        websocket=rvg_leidarstein_websocket,
        distance_filter=None,
        predicted_interval=30,
        colav_manager=colav_manager,
        filt_order=3,
        filt_cutfreq=0.1,
        filt_nyqfreq=0.5,
    ):
        self._serializer = serializer
        self._buffer = serializer.sorted_data
        self._running = False
        self.transform = simulation_transform()
        self.ais_history = dict()
        self.ais_history_len = 30
        self.distance_filter = distance_filter
        self.gunnerus_lat = None
        self.gunnerus_lon = None
        self.websocket = websocket
        self._colav_manager = colav_manager
        self._predicted_interval = predicted_interval
        self._butter_b, self._butter_a = butter(
            filt_order, filt_cutfreq / filt_nyqfreq, btype="low"
        )
        self.rvg_state = {}
        self.rvg_heading = None

    def clear_ais_history(self):
        """
        Clear the AIS message history.

        This method clears the AIS message history stored in the 'ais_history'
        attribute.

        """
        self.ais_history.clear()

    def _has_data(self, msg):
        """
        Check if a message has latitude and longitude data.

        Parameters:
        - msg (dict): The message to check.

        Returns:
        - bool: True if the message has latitude and longitude data, False otherwise.

        """
        msg_keys = msg.keys()
        has_data = "lat" in msg_keys and "lon" in msg_keys
        return has_data

    def _has_prop(self, msg, prop=""):
        """
        Check if a message has a specific property.

        Parameters:
        - msg (dict): The message to check.
        - prop (str): The property to check for.

        Returns:
        - bool: True if the message has the specified property, False otherwise.

        """
        msg_keys = msg.keys()
        has_data = prop in msg_keys
        return has_data

    def _is_moving(self, msg):
        """
        Check if a message represents a moving object.

        Parameters:
        - msg (dict): The message to check.

        Returns:
        - bool: True if the message contains course and speed data, False otherwise.

        """
        msg_keys = msg.keys()
        has_data = "course" in msg_keys and "speed" in msg_keys
        return has_data

    def stop(self):
        """
        Stop the simulation server.

        This method sets the '_running' attribute to False, which stops the simulation server.

        """
        self._running = False
        print("Simulation Client stopped")

    def dist(self, p, q):
        """
        Calculate the Euclidean distance between two points in 2D space.

        Parameters:
        - p (tuple): The coordinates of the first point in the form (latitude, longitude).
        - q (tuple): The coordinates of the second point in the form (latitude, longitude).

        Returns:
        - float: The distance between the two points.

        """
        return math.sqrt((q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2)

    def _validate_coords(self, msg, distance):
        """
        Validate if a message is within a specified distance from a reference point.

        Parameters:
        - msg (dict): The message to check.
        - distance (float): The maximum distance in meters for the message to be
                            considered valid.

        Returns:
        - bool: True if the message is within the specified distance, False otherwise.

        """
        if self.gunnerus_lat is None or self.gunnerus_lon is None:
            return False

        if msg["message_id"].find("!AI") == 0:
            if self._has_data(msg):
                lat = float(msg["lat"])
                lon = float(msg["lon"])

                p = [lat, lon]
                q = [self.gunnerus_lat, self.gunnerus_lon]

                return self.dist(p, q) < distance

        return False

    def _set_predicted_position(self, msg):
        """
        Set the predicted position of a moving object after a specified time interval.

        This method calculates the predicted latitude and longitude of a moving
        object after a specified time interval based on its current course and speed. '
        The predicted latitude and longitude are added to the message as "lat_p"
        and "lon_p" properties, respectively.

        Parameters:
        - msg (dict): The message representing the moving object.

        """
        if self._is_moving(msg) and msg["speed"] > 0:
            speed = self.transform.kn_to_mps(msg["speed"])
            x = math.sin(math.radians(msg["course"])) * speed * self._predicted_interval
            y = math.cos(math.radians(msg["course"])) * speed * self._predicted_interval

            lat_p, lon_p = self.transform.xyz_to_coords(
                x, y, float(msg["lat"]), float(msg["lon"])
            )
            msg["lat_p"] = lat_p
            msg["lon_p"] = lon_p

    def _lp_filter_data(self, data=[]):
        """
        Apply a low-pass filter to a list of data.

        This method applies a low-pass filter to the input data using a
        Butterworth filter.

        Parameters:
        - data (list): The list of data to be filtered.

        Returns:
        - numpy.array: The filtered data.

        """
        if len(data) < 15:
            return None
        data = np.array(data)
        filtered_data = filtfilt(self._butter_b, self._butter_a, data)
        return filtered_data

    def _set_history(self, msg):
        """
        Set and update the historical position and course information for AIS messages.

        This method updates the historical position and course information for
        AIS messages. It maintains a history of latitude, longitude, and course
        data for each AIS message based on their message ID. The method applies
        a low-pass filter to smooth the position and course data if available.

        Parameters:
        - msg (dict): The AIS message dictionary containing "lat" (latitude) and
        "lon" (longitude) properties.

        """
        if msg["message_id"].find("!AI") == 0:
            if self._has_data(msg):
                message_id = msg["message_id"]
                lat = float(msg["lat"])
                lon = float(msg["lon"])
                has_course = self._has_prop(msg, "course")

                if has_course:
                    course = float(msg["course"])

                if message_id in self.ais_history.keys():
                    self.ais_history[message_id]["lon_history"].append(lon)
                    filt_lon = self._lp_filter_data(
                        self.ais_history[message_id]["lon_history"]
                    )
                    self.ais_history[message_id]["lat_history"].append(lat)
                    filt_lat = self._lp_filter_data(
                        self.ais_history[message_id]["lat_history"]
                    )

                    if filt_lon is not None and filt_lat is not None:
                        filtered_pos = np.array([filt_lon, filt_lat]).T.tolist()
                        self.ais_history[message_id]["pos_history"] = filtered_pos
                    else:
                        unfiltered_pos = np.array(
                            [
                                self.ais_history[message_id]["lon_history"],
                                self.ais_history[message_id]["lat_history"],
                            ]
                        ).T.tolist()
                        self.ais_history[message_id]["pos_history"] = unfiltered_pos

                    if has_course:
                        self.ais_history[message_id]["course_history"].append(course)
                        filtered_course = self._lp_filter_data(
                            self.ais_history[message_id]["course_history"]
                        )
                        if filtered_course is not None:
                            self.ais_history[message_id][
                                "filtered_course"
                            ] = filtered_course[-1]
                        else:
                            self.ais_history[message_id]["filtered_course"] = course

                    if (
                        len(self.ais_history[message_id]["lon_history"])
                        > self.ais_history_len
                    ):
                        self.ais_history[message_id]["lon_history"].pop(0)
                    if (
                        len(self.ais_history[message_id]["lat_history"])
                        > self.ais_history_len
                    ):
                        self.ais_history[message_id]["lat_history"].pop(0)

                    if has_course and (
                        len(self.ais_history[message_id]["course_history"])
                        > self.ais_history_len
                    ):
                        self.ais_history[message_id]["course_history"].pop(0)
                else:
                    self.ais_history[message_id] = dict()
                    self.ais_history[message_id]["lon_history"] = [lon]
                    self.ais_history[message_id]["lat_history"] = [lat]
                    self.ais_history[message_id]["pos_history"] = []

                    if has_course:
                        self.ais_history[message_id]["course_history"] = [course]
                        self.ais_history[message_id]["filtered_course"] = course

                msg["pos_history"] = self.ais_history[message_id]["pos_history"]
                if has_course:
                    msg["course"] = self.ais_history[message_id]["filtered_course"]

    def _compose_msg(self, msg, msg_type="datain"):
        """
        Compose a JSON message to be sent via the WebSocket.

        This method prepares the incoming message (msg) to be sent via the WebSocket
        as a JSON string. It sets the historical position information and the predicted
        position for AIS messages, and then converts the message into a JSON format.

        Parameters:
        - msg (dict): The message dictionary to be composed.
        - msg_type (str, optional): The type of the message. Default is "datain".

        Returns:
        - str: The JSON-encoded message.

        """
        return json.dumps({"type": msg_type, "content": msg}, default=str)

    def _compose_ais_msg(self, msg, msg_type="datain"):
        """
        Compose a JSON message to be sent via the WebSocket.

        This method prepares the incoming message (msg) to be sent via the WebSocket
        as a JSON string. It sets the historical position information and the predicted
        position for AIS messages, and then converts the message into a JSON format.

        Parameters:
        - msg (dict): The message dictionary to be composed.
        - msg_type (str, optional): The type of the message. Default is "datain".

        Returns:
        - str: The JSON-encoded message.

        """
        self._set_history(msg)
        self._set_predicted_position(msg)
        return json.dumps({"type": msg_type, "content": msg}, default=str)

    def _set_gunnerus_coords(self, msg):
        """
        Set the latitude and longitude for the Gunnerus vessel.

        This method sets the latitude and longitude coordinates for the Gunnerus
        vessel based on the provided message. The latitude and longitude are converted
        from degrees to decimal format and stored in the class variables.

        Parameters:
        - msg (dict): The message dictionary containing "lat" (latitude) and "lon"
        (longitude) properties. Additionally, the "lat_dir" and "lon_dir" properties
        represent the direction of latitude and longitude.

        """
        self.gunnerus_lon = self.transform.deg_2_dec(float(msg["lon"]), msg["lon_dir"])
        self.gunnerus_lat = self.transform.deg_2_dec(float(msg["lat"]), msg["lat_dir"])

    def _send(self, message):
        """
        Send the message via WebSocket and perform additional actions for specific
        message types.

        This method sends the provided message via WebSocket if the message's
        coordinates are valid. For valid AIS messages, it updates the AIS data in
        the COLAV manager. For specific message types, it updates the Gunnerus data
        in the COLAV manager and stores the vessel's heading.

        Parameters:
        - message (dict): The message dictionary to be sent.

        """
        if message["message_id"] == "$PSIMSNS":
            self.rvg_heading = message["head_deg"]
            if self.websocket.enable:
                json_msg = self._compose_msg(message)
                self.websocket.send(json_msg)

        if message["message_id"] == "$GPGGA":
            if self.websocket.enable:
                json_msg = self._compose_msg(message)
                self.websocket.send(json_msg)

        if message["message_id"] == "$GPRMC":
            self._set_gunnerus_coords(message)
            self._colav_manager.update_gunnerus_data(message)
            self.rvg_state = message
            if self.websocket.enable:
                json_msg = self._compose_msg(message)
                self.websocket.send(json_msg)

        if self._validate_coords(message, self.distance_filter):
            valid_ais_msg = message["message_id"].find("!") == 0 and self._has_data(
                message
            )

            if valid_ais_msg:
                self._colav_manager.update_ais_data(message)

            if self.websocket.enable:
                json_msg = self._compose_ais_msg(message)
                self.websocket.send(json_msg)

    def pop_buffer(self, index=None):
        """
        Pop a message from the buffer.

        This method removes a message from the buffer list. If an index is
        provided, it removes the message at that index. If no index is provided,
        it removes the last message from the buffer list.

        Parameters:
        - index (int, optional): The index of the message to be removed from the
        buffer. Default is None.

        Returns:
        - dict: The removed message.

        """
        if len(self._buffer) < 1:
            return

        if index is not None:
            return self._buffer.pop(index)
        else:
            return self._buffer.pop()

    def start(self):
        """
        Start processing and sending messages from the buffer.

        This method starts the main loop to process and send messages from the buffer.
        It continuously checks if there are messages in the buffer, and if so, it sends the first message,
        performs necessary updates, and then removes the sent message from the buffer.
        The loop continues as long as the `_running` attribute is True.

        """
        self._running = True
        print("Simulation Client running...")

        while self._running:
            if len(self._buffer):
                self._send(self._buffer[0])
                self.pop_buffer(0)
