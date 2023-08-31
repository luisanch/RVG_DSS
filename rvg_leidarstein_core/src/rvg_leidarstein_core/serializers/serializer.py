#!/usr/bin/env python3
"""
Module: serializer

Description:
This module contains the FastSerializer class, which is a subclass of the Serializer class. 
FastSerializer provides a fast and efficient method to serialize datastream messages using 
DataFrame aliases and metadata.

The FastSerializer class inherits attributes and methods from the Serializer class and 
overrides some of them to improve serialization performance.
"""


import datetime
from ..datastream_managers.mqtt_datastream_manager import mqtt_datastream_manager
from .serializer_types import AIS, GPGGA, GPRMC, PSIMSNS


class serializer:
    def __init__(
        self,
        df_aliases,
        datastream_manager=mqtt_datastream_manager,
    ):
        """
        Fast serializer for datastream messages.

        This class extends the 'Serializer' class to provide faster serialization
        of datastream messages. It is designed to work with a 'datastream_manager'
        for receiving and parsing messages and creating DataFrames for serialization.

        Args:
            df_aliases (dict): A dictionary that maps DataFrame aliases (keys) to
                                lists of attribute names (values). This mapping
                                defines how DataFrame columns will be created and
                                named during serialization.
            datastream_manager (datastream_manager, optional): An instance of the
                                'datastream_manager' class that will be used
                                for receiving and parsing messages. Defaults to
                                'datastream_manager'.


        Note:
            If 'overwrite_headers' is set to False, the serializer will attempt
            to load DataFrame headers from the specified directory during class
            initialization. The DataFrame headers should be saved as CSV files
            in that directory.

        Attributes:
            df_aliases (dict): A dictionary that maps DataFrame aliases to lists
                                of attribute names.
            def_unk_atr_name (str): The name for unknown attributes (used when
                                mapping DataFrame columns).
            bufferBusy (bool): A flag to indicate if the buffer is busy (during
                                serialization).
            _datastream_manager (datastream_manager): An instance of the 'datastream_manager'
                                class used for receiving and parsing messages.
            sorted_data (list): A list to store sorted data.
            _running (bool): A flag to indicate whether the serializer is running
                                or stopped.

            _buffer_data (list): A list to store parsed message data received from
                                the datastream manager.
            _overwrite_headers (bool): A boolean indicating whether to overwrite
                                DataFrame headers if they already exist.
        """
        # attribute aliases for incoming messages
        self.df_aliases = df_aliases

        # define name for unknown atribute
        self.def_unk_atr_name = "unknown_"
        self.bufferBusy = False
        self._datastream_manager = datastream_manager
        self.sorted_data = []
        self._running = False
        self._buffer_data = datastream_manager.parsed_msg_list

    def _get_nmea_attributes(self, nmea_object, msg_id):
        """
        Get attributes and values from a parsed NMEA message object.

        This method takes a parsed NMEA message object and extracts its attributes and values.
        For attributes with known names, they are included in the 'msg_atr' list along with their
        corresponding values in the 'msg_values' list. If the NMEA object contains additional
        data fields that are not defined in the NMEA message format, they are included in the
        'unknown_msg_data' list.

        Args:
            nmea_object (pynmea2.ParsedLine): The parsed NMEA message object.

        Returns:
            tuple: A tuple containing three lists: 'msg_atr' (attribute names),
            'msg_values' (attribute values), and 'unknown_msg_data' (additional
            data fields not defined in the NMEA message format).
        """

        t = type(nmea_object)
        msg_values = []
        msg_atr = []
        unkown_msg_data = []

        for i, v in enumerate(nmea_object.data):
            if i >= len(t.fields):
                unkown_msg_data.append(v)
                continue
            name = t.fields[i][1]
            msg_atr.append(name.replace(" ", ""))
            msg_values.append(getattr(nmea_object, name))

        if len(unkown_msg_data) > 1:
            msg_values.extend(unkown_msg_data)

            for i, _ in enumerate(unkown_msg_data):
                atr_name = self.def_unk_atr_name + str(i)
                msg_atr.append(atr_name)

        if msg_id in self.df_aliases:
            alias_list = self.df_aliases[msg_id]
            if len(alias_list) == len(msg_atr):
                for i, alias in enumerate(alias_list):
                    msg_atr[i] = alias

        return (msg_atr, msg_values)

    def stop(self):
        """
        Stop the serializer.

        This method sets the '_running' flag to False, stopping the serialization
        process.

        Returns:
            None
        """
        self._running = False
        print("Serializer stopped.")

    def _serialize_ais_data(self, id, ais_message):
        valid_message = (
            hasattr(ais_message, "lat")
            and hasattr(ais_message, "lon")
            and hasattr(ais_message, "mmsi")
        )

        if valid_message:
            msg_id = str(id) + str(ais_message.mmsi)
            new_obj = AIS(ais_message.lat, ais_message.lon, ais_message.mmsi, msg_id)
            if hasattr(ais_message, "course"):
                new_obj.course = ais_message.course
            if hasattr(ais_message, "heading"):
                new_obj.heading = ais_message.heading
            if hasattr(ais_message, "speed"):
                new_obj.speed = ais_message.speed
            return new_obj
        else:
            return None

    def _serialize_nmea_data(self, message):
        """
        Serialize a single datastream message.

        This method takes a single datastream message in the form of a tuple and
        serializes its attributes based on the provided DataFrame aliases and
        metadata. The serialized message is added to the 'sorted_data' list.

        Args:
            message (tuple): A tuple containing the following elements:
                             - msg_id (str): The message identifier.
                             - msg_atr (list): A list of attribute names for the message.
                             - msg_values (list): A list of attribute values for the message.
                             - unkown_msg_data (list): A list of unknown message data (if any).
                             - metadata (tuple, None): A tuple containing metadata information for the message
                                                      (or None if no metadata is present).

        Note:
            This method is called internally during the serialization process
            and should not be called directly.

        """
        msg_id, msg_atr, msg_values = message
        msg_atr.append("message_id")
        msg_values.append(msg_id)

        if msg_id == "$GPRMC":
            new_obj = GPRMC(*msg_values)
            return new_obj
        elif msg_id == "$GPGGA":
            new_obj = GPGGA(*msg_values)
            return new_obj
        elif msg_id == "$PSIMSNS":
            msg_values[1] = datetime.datetime.strptime(
                msg_values[1], "%H%M%S.%f"
            ).time()
            new_obj = PSIMSNS(*msg_values)
            return new_obj
        else:
            return None

    def _serialize_buffered_message(self):
        """
        Serialize a buffered datastream message.

        This method serializes a datastream message from the buffered data
        (parsed_msg_list) of the datastream manager. The serialized message is
        added to the 'sorted_data' list of the serializer.

        Note:
            This method is called internally during the serialization process
            and should not be called directly.
        """
        if len(self._buffer_data) < 1:
            self.bufferBusy = False
            return

        self.bufferBusy = True
        _message = self._buffer_data[-1][1]
        msg_id = self._buffer_data[-1][0]

        if msg_id.find("!") == 0:
            new_obj = self._serialize_ais_data(msg_id, _message)
        else:
            msg_atr, msg_values = self._get_nmea_attributes(_message, msg_id)
            message = (msg_id, msg_atr, msg_values)
            new_obj = self._serialize_nmea_data(message)

        if new_obj is not None:
            self.sorted_data.append(new_obj)
        self._datastream_manager.pop_parsed_msg_list()

    def start(self):
        """
        Start the Serializer.

        This method starts the Serializer's serialization process. It
        continuously calls the '_serialize_buffered_message' method to serialize
        buffered datastream messages until the '_running' attribute is set to False.

        Note:
            This method should be called after initializing the FastSerializer
            to begin the serialization process.

        """
        self._running = True
        print("FastSerializer running.")

        while self._running:
            self._serialize_buffered_message()
        # ToDo: handle loose ends on terminating process.
        print("FastSerializer stopped.")
