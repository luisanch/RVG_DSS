#!/usr/bin/env python3
"""
simulation_server_replay.py

This module provides the `simulation_server_replay` class, which extends the 
`simulation_server` class to enable data replay from a log file. It reads messages 
from a log datastream manager, sorts them based on timestamps, and replays them in the
order they were recorded, simulating real-time data stream behavior. The replay 
speed is adjusted based on the actual time difference between messages in the log file.
"""

from rvg_leidarstein_core.datastream_managers.log_datastream_manager import (
    log_datastream_manager,
)
from rvg_leidarstein_core.serializers.fast_serializer import fast_serializer
from rvg_leidarstein_core.simulation.simulation_server import simulation_server
from rvg_leidarstein_core.data_relay.rvg_leidarstein_websocket import (
    rvg_leidarstein_websocket,
)
from rvg_leidarstein_core.colav.colav_manager import colav_manager
from time import time


class simulation_server_replay(simulation_server):
    """
    Simulation Server with Data Replay.

    This class extends the `simulation_server` and adds the capability to replay
    messages from a log file. It replays messages stored in a log file by using
    the `log_datastream_manager` and simulates the behavior of a live data stream.

    Parameters:
    - serializer (fast_serializer, optional): The serializer to use for processing
        incoming messages. Default is fast_serializer.
    - log_datastream_manager (log_datastream_manager, optional): The log datastream
        manager responsible for replaying messages from the log file. Default is
        log_datastream_manager.
    - websocket (rvg_leidarstein_websocket, optional): The WebSocket connection
        manager to send processed messages. Default is rvg_leidarstein_websocket.
    - distance_filter (float, optional): The distance filter to check if a message
        is within the specified distance of the Gunnerus vessel. Default is None.
    - predicted_interval (int, optional): The interval (in seconds) for predicting
        the position of AIS messages. Default is 30.
    - colav_manager (colav_manager, optional): The COLAV manager to update AIS and
        Gunnerus data. Default is colav_manager.
    - filt_order (int, optional): The order of the Butterworth filter used for
        filtering data. Default is 3.
    - filt_cutfreq (float, optional): The cutoff frequency for the Butterworth
        filter. Default is 0.1.
    - filt_nyqfreq (float, optional): The Nyquist frequency for the Butterworth
        filter. Default is 0.5.

    Attributes:
    - _log_datastream_manager (log_datastream_manager): The log datastream manager
        responsible for replaying messages from the log file.
    - log_datastream_path (str): The path to the log datastream file.
    - replay_start_time (float): The start time of the data replay in seconds since the epoch.
    - replay_factor (float): The factor to adjust the replay speed.
        A value greater than 1 makes the replay faster, while a value less than
        1 makes it slower.

    Methods:
    - replay(): Start replaying the messages from the log file.
    - set_replay_speed(factor): Set the replay speed factor.
    - start(): Start processing and sending messages from the log file.

    """

    def __init__(
        self,
        serializer=fast_serializer,
        log_datastream_manager=log_datastream_manager,
        websocket=rvg_leidarstein_websocket,
        distance_filter=None,
        predicted_interval=30,
        colav_manager=colav_manager,
        filt_order=3,
        filt_cutfreq=0.1,
        filt_nyqfreq=0.5,
    ):
        super(simulation_server_replay, self).__init__(
            serializer,
            websocket,
            distance_filter,
            predicted_interval,
            colav_manager,
            filt_order,
            filt_cutfreq,
            filt_nyqfreq,
        )
        self._log_datastream_manager = log_datastream_manager

    def start(self):
        """
        Start processing and replaying messages from the log file.

        This method starts the simulation server with data replay and processes
        the messages read from the log file. It replays the messages in the order
        of their timestamps, simulating the behavior of a live data stream.
        The replay speed is determined by the actual time difference between
        messages in the log file.

        """
        self._running = True
        print("Simulation Replay Client running...")
        sortedList = None
        index = 0
        time_of_first_message = 0
        start_time = 0
        while self._running:
            if (
                self._log_datastream_manager.parse_complete
                and not self._serializer.bufferBusy
            ):
                if sortedList is None:
                    sortedList = sorted(self._buffer, key=lambda d: d["seq_num"])
                    time_of_first_message = sortedList[index]["unix_time"]
                    start_time = time()
                else:
                    simulation_time = time_of_first_message + (time() - start_time)
                    if simulation_time > self._buffer[index]["unix_time"]:
                        self._send(self._buffer[index])
                        index += 1
                        if index >= len(sortedList):
                            print("loop repeat", start_time - time())
                            self.clear_ais_history()
                            index = 0
                            start_time = time()
            # self.pop_buffer(0)
