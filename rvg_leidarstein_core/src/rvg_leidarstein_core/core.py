#!/usr/bin/env python3

"""
core.py

This module contains the core class responsible for managing datastream, 
serializer, and simulation manager. It initializes and starts these components 
in separate threads.

Attributes:
-----------
- colav_manager: colav_manager
    The instance of the COLAV manager.
- websocket: rvg_leidarstein_websocket
    The instance of the WebSocket used for communication.
- log_file: str, optional
    The path to a log file if a log file should be used as the data source.
"""
from threading import Thread
from .serializers.serializer import serializer
from .colav.colav_manager import colav_manager
from .simulation.simulation_manager import simulation_manager
from .data_relay.rvg_leidarstein_websocket import rvg_leidarstein_websocket
from .datastream_managers.mqtt_datastream_manager import mqtt_datastream_manager
from .simulation.simulation_manager import RVG_Init


class core:
    """
    Core class for managing datastream, serializer, and simulation manager.

    This class is responsible for initializing and managing the datastream,
    serializer, and simulation manager. It also starts and stops the different
    components in separate threads.

    Parameters:
    -----------
    colav_manager : colav_manager
        The instance of the COLAV manager.
    websocket : rvg_leidarstein_websocket
        The instance of the WebSocket used for communication.
    log_file : str, optional
        The path to a log file if a log file should be used as the data source.

    Attributes:
    -----------
    (See __init__ method for attribute descriptions.)

    Methods:
    --------
    start() : None
        Start the datastream, serializer, and simulation manager in separate threads.
    stop() : None
        Stop the datastream, serializer, and simulation manager, and close the WebSocket.
    """

    def __init__(
        self, colav_manager=colav_manager, websocket=rvg_leidarstein_websocket
    ):
        self.colav_manager = colav_manager
        self.websocket = websocket
        self.datastream_manager = mqtt_datastream_manager()

        # Initialize Serializer
        # ToDo: create class for holding these tuples
        self.df_aliases = {
            "$PSIMSNS": [
                "msg_type",
                "timestamp",
                "unknown_1",
                "tcvr_num",
                "tdcr_num",
                "roll_deg",
                "pitch_deg",
                "heave_m",
                "head_deg",
                "empty_1",
                "unknown_2",
                "unknown_3",
                "empty_2",
                "checksum",
            ]
        }

        self.serializer = serializer(
            datastream_manager=self.datastream_manager, df_aliases=self.df_aliases
        )

        # Initialize Simulation Manager
        self.distance_filter = 1  # geodetic degree

        # dummy_gunnerus is now the origin for 4dof sim
        self.rvg_init = RVG_Init(
            lat=6326.3043,
            lat_dir="E",
            lon=1024.5395,
            lon_dir="N",
            true_course=-40,
            spd_over_grnd=0,
            revs=100,
            azi_d=0,
        )

        self.simulation_manager = simulation_manager(
            serializer=self.serializer,
            websocket=self.websocket,
            distance_filter=self.distance_filter,
            Colav_Manager=self.colav_manager,
            rvg_init=self.rvg_init,
            tmax=1,
            dt=0.2,
            predicted_interval=60,
            mode="rt",
        )

        # Create new threads
        self.thread_websocket_receive = Thread(target=self.websocket.start)
        self.thread_datastream = Thread(target=self.datastream_manager.start)
        self.thread_serialize_data = Thread(target=self.serializer.start)
        self.thread_sim_manager = Thread(target=self.simulation_manager.start)

    def start(self):
        if self.websocket.enable:
            self.thread_websocket_receive.start()
        self.thread_datastream.start()
        self.thread_serialize_data.start()
        self.thread_sim_manager.start()

    def stop(self):
        self.datastream_manager.stop()
        self.serializer.stop()
        self.simulation_manager.stop()
        self.websocket.close()
        print("Exiting...")
