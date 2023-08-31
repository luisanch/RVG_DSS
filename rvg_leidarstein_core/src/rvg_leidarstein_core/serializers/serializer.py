#!/usr/bin/env python3
"""
Module: serializer

Description:
This module contains the `serializer` class, which is responsible for  serializing datastream messages.
"""


import datetime
from ..datastream_managers.mqtt_datastream_manager import mqtt_datastream_manager
from .serializer_types import AIS, GPGGA, GPRMC, PSIMSNS


class serializer:
    """
    The `serializer` class is designed for serialization of datastream messages.
    """
    def __init__(
        self,
        df_aliases,
        datastream_manager=mqtt_datastream_manager,
    ):
        """
        Initialize the serializer.

        Args:
            df_aliases (dict): A dictionary mapping DataFrame aliases to lists of attribute names.
            datastream_manager (datastream_manager, optional): Instance of the 'datastream_manager' class.
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

        Args:
            nmea_object (pynmea2.ParsedLine): Parsed NMEA message object.
            msg_id (str): Message identifier.

        Returns:
            tuple: Lists of attribute names, attribute values, and unknown message data.
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

        This method sets the '_running' flag to False, stopping the serialization process.
        """
        self._running = False
        print("Serializer stopped.")

    def _serialize_ais_data(self, id, ais_message):
        """
        Serialize AIS data.

        Args:
            id (str): Message identifier.
            ais_message: AIS message data.

        Returns:
            object: Serialized AIS message.
        """
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
        Serialize NMEA data.

        Args:
            message (tuple): Message tuple containing attributes, values, and metadata.

        Returns:
            object: Serialized NMEA message.
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
        Start the serializer.

        This method starts the Serializer's serialization process.
        """
        self._running = True
        print("FastSerializer running.")

        while self._running:
            self._serialize_buffered_message()
        # ToDo: handle loose ends on terminating process.
        print("FastSerializer stopped.")
