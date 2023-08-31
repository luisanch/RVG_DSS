#!/usr/bin/env python3
"""
Module: mqtt_datastream_manager

Description:
This module defines the 'mqtt_datastream_manager' class, which manages the reception
and parsing of datastream messages from MQTT broker. It can handle NMEA and AIS messages,
and provides methods for decoding, parsing, and managing the received messages.

Note:
- This module provides functionality to interact with MQTT datastream messages. ses.
"""

import pynmea2
import pyais
import paho.mqtt.client as mqtt
from typing import Any


class mqtt_datastream_manager:
    def __init__(
        self,
        verbose=False,
        broker_address="mqtt.gunnerus.it.ntnu.no",
        client_id="gunnerus_nmea_reader",
        topic="gunnerus/NMEA/#",
    ):
        """
        Initialize MQTT Datastream Manager.

        Args:
            verbose (bool): If True, enables verbose mode to print additional information.
            broker_address (str): Address of the MQTT broker to connect to.
            client_id (str): Client ID for the MQTT client.
            topic (str): Topic to subscribe for receiving datastream messages.

        Returns:
            None
        """
        self.verbose = verbose
        self.broker_address = broker_address
        self.topic = topic
        self.client = mqtt.Client(client_id=client_id)
        self.client.on_message = self._decode
        self.client.reconnect_delay_set(min_delay=1, max_delay=10)
        self.parsed_msg_list = []
        self.reconnect_delay = 2
        self.client.connect(self.broker_address)
        self.client.subscribe(self.topic)

    @staticmethod
    def __parse_nmea(msg):
        """
        Parse NMEA message.

        Args:
            msg (str): NMEA message to parse.

        Returns:
            pynmea2.ParsedLine: Parsed NMEA message object.
        """
        parsed = pynmea2.parse(msg)
        return parsed

    @staticmethod
    def __parse_ais(msg):
        """
        Parse AIS message.

        Args:
            msg (str): AIS message to parse.

        Returns:
            dict: Decoded AIS message object.
        """
        decoded = pyais.decode(msg)
        return decoded

    def _decode(self, *args: Any, **kwds: Any) -> Any:
        """
        Callback function to decode and handle received MQTT messages.

        Args:
            *args: Positional arguments passed to the callback.

        Returns:
            None
        """
        _client = args[0]
        _userdata = args[1]
        _message = args[2]

        if len(out := _message.payload.decode().split(" ", 1)) != 2 and self.verbose:
            print(f"Invalid message {_message.payload.decode()}")
            return

        timestamp, msg = out
        msg_id = msg.split(",")[0]
        try:
            if msg[0] == "$":
                message = (msg_id, mqtt_datastream_manager.__parse_nmea(msg))
            elif msg[0] == "!":
                message = (msg_id, mqtt_datastream_manager.__parse_ais(msg))
            else:
                message = None
                if self.verbose:
                    print("Unknown")
        except Exception as e:
            message = None
            if self.verbose:
                print(e)

        if message is not None:
            self.parsed_msg_list.append(message)

    def pop_parsed_msg_list(self, index=None):
        """
        Remove and return the last parsed message from the parsed_msg_list.

        Args:
            index (int): Optional index to specify which message to pop. If None,
            the last message will be removed.

        Returns:
            None
        """
        if len(self.parsed_msg_list) < 1:
            return

        if index is not None:
            self.parsed_msg_list.pop(index)
            return
        else:
            self.parsed_msg_list.pop()
            return

    def stop(self):
        """
        Stop the MQTT Datastream Manager.

        Returns:
            None
        """
        self._running = False
        return

    def start(self):
        """
        Start the MQTT Datastream Manager.

        Returns:
            None
        """
        print("MQTT DatastreamManager running.")
        self._running = True

        while self._running:
            self.client.loop()
        self.client.disconnect()
