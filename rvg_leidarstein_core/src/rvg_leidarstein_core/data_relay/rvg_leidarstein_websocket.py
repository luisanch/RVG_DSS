#!/usr/bin/env python3
"""
rvg_leidarstein_websocket.py

Module for handling WebSocket communication with the RVG Leidarstein system.
"""
import websocket
import json


class rvg_leidarstein_websocket:
    """
    WebSocket class for communication with the RVG Leidarstein system.
    Parameters:
    address (str): The address of the WebSocket server to connect to.
    enable (bool): Flag to enable or disable the WebSocket communication. Default is True.
    receive_filters (list): List of message IDs to filter when receiving data. Default includes "control_azi","control_thrust", and "data_mode".
    """

    def __init__(
        self,
        address,
        enable=True,
        receive_filters=["control_azi", "control_thrust", "data_mode", "cbf_domains"],
    ):
        self.address = address
        self.enable = enable
        self.received_data = {}
        self._receive_filters = receive_filters
        self.running = False

        if enable:
            websocket.enableTrace(False)
            self.ws = websocket.create_connection(address)

    def send(self, json_msg):
        """
        Send a JSON-formatted message over the WebSocket.

        Parameters:
            json_msg (str): The JSON-formatted message to be sent.
        """
        if self.enable: 
            self.ws.send(json_msg)

    def recieve(self):
        """
        Receive data from the WebSocket.

        Returns:
            str: The received data in JSON format.
        """
        return self.ws.recv()

    def start(self):
        """
        Start receiving and filtering data from the WebSocket server.
        """
        self.running = True

        while self.running:
            raw = self.ws.recv()
            msg = json.loads(raw)

            if msg["type"] == "datain":
                msg_id = msg["content"]["message_id"]

                for filter in self._receive_filters:
                    if msg_id == filter:

                        val = msg["content"]["val"]
                        self.received_data[msg_id] = val 

    def close(self):
        """
        Close the WebSocket connection.
        """
        self.running = False
        if self.enable:
            self.ws.close()
