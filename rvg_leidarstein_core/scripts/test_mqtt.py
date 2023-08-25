#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from typing import Any
import pynmea2
import pyais
import paho.mqtt.client as mqtt
import datetime


class GunnerusTCPClientParser:
    def __init__(self):
        pass

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        _client = args[0]
        _userdata = args[1]
        _message = args[2]

        if len(out := _message.payload.decode().split(" ", 1)) != 2:
            print(f"Invalid message {_message.payload.decode()}")
            return

        timestamp, msg = out

        dt = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        print(f"{dt} {msg}")

        try:
            if msg[0] == "$":
                GunnerusTCPClientParser.__parse_nmea(msg)

            elif msg[0] == "!":
                GunnerusTCPClientParser.__parse_ais(msg)
            else:
                print("Unknown")
        except Exception as e:
            print(e)

    @staticmethod
    def __parse_nmea(msg):
        parsed = pynmea2.parse(msg)

    @staticmethod
    def __parse_ais(msg):
        decoded = pyais.decode(msg)


def main():
    parser = GunnerusTCPClientParser()

    broker_address = "mqtt.gunnerus.it.ntnu.no"

    client = mqtt.Client("gunnerus_nmea_reader")

    client.connect(broker_address)

    client.on_message = parser

    client.subscribe("gunnerus/NMEA/#")

    client.loop_start()

    while True:
        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
        exit(0)