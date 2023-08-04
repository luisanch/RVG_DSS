#!/usr/bin/env python3
"""
Module: simulation_manager

Description:
------------
The simulation_manager module provides a Simulation Manager to handle different 
simulation modes. It manages the setup and execution of the simulation server based 
on the selected mode.

Dependencies:
-------------
- threading

Classes:
--------
simulation_manager
"""
from rvg_leidarstein_core.simulation.simulation_server import simulation_server
from rvg_leidarstein_core.simulation.simulation_server_replay import (
    simulation_server_replay,
)
from rvg_leidarstein_core.simulation.simulation_4dof import simulation_4dof
from threading import Thread


class simulation_manager:
    """
    Simulation Manager to handle different simulation modes.

    Parameters:
    -----------
    datastream_manager : object
        An instance of the datastream manager used to handle incoming data.

    serializer : object
        An instance of the serializer used to serialize incoming data.

    websocket : object
        An instance of the websocket used for communication.

    distance_filter : float
        The distance threshold used for filtering incoming data.

    Colav_Manager : object
        An instance of the collision avoidance manager used for collision avoidance 
        handling.

    rvg_init : dict
        A dictionary containing the initial values of the vessel's parameters.

    tmax : float, optional
        The maximum simulation time, in seconds. Default is 1.

    dt : float, optional
        The time step for the simulation, in seconds. Default is 0.2.

    predicted_interval : float, optional
        The predicted interval for simulation, in seconds. Default is 60.

    mode : str, optional
        The simulation mode. Available options are "4dof", "replay", and "rt" 
        (real-time). Default is "4dof".

    Returns:
    --------
    None
    """

    def __init__(
        self,
        datastream_manager,
        serializer,
        websocket,
        distance_filter,
        Colav_Manager,
        rvg_init,
        tmax=1,
        dt=0.2,
        predicted_interval=60,
        mode="4dof",
    ):
        self.datastream_manager = datastream_manager
        self.serializer = serializer
        self.websocket = websocket
        self.distance_filter = distance_filter
        self.Colav_Manager = Colav_Manager
        self.rvg_init = rvg_init
        self.tmax = tmax
        self.dt = dt
        self.predicted_interval = predicted_interval
        self.mode_4dof = "4dof"
        self.mode_replay = "replay"
        self.mode_rt = "rt"
        self.mode = mode
        self.simulation_server = simulation_server
        self.running = False
        self.thread_sim_server = Thread(target=self.simulation_server.start)

    def _has_prop(self, msg, prop=""):
        """
        Check if a property exists in the given message.

        Parameters:
        -----------
        msg : dict
            The message to check for the property.

        prop : str, optional
            The property to check for. Default is an empty string.

        Returns:
        --------
        bool
            True if the property exists in the message, False otherwise.
        """
        msg_keys = msg.keys()
        has_data = prop in msg_keys
        return has_data

    def _format_init(self, msg, head):
        """
        Format the initialization message for simulation.

        Parameters:
        -----------
        msg : dict
            The message to be formatted.

        head : float
            The heading value to be included in the formatted message.

        Returns:
        --------
        dict
            The formatted message with updated values.
        """
        revs = self.rvg_init["revs"]
        azi = self.rvg_init["azi_d"]
        msg = self.simulation_server.rvg_state
        msg["lat"] = float(msg["lat"])
        msg["lon"] = float(msg["lon"])
        msg["true_course"] = float(head)
        msg["spd_over_grnd"] = float(msg["spd_over_grnd"])
        msg["azi_d"] = azi
        msg["revs"] = revs
        return msg

    def start_sim(self):
        """
        Start the simulation server.

        This method starts the simulation server by starting the thread responsible 
        for running the simulation.

        Returns:
        --------
        None
        """
        self.thread_sim_server.start()

    def stop_sim(self):
        """
        Stop the simulation server.

        This method stops the simulation server by calling its `stop` method.

        Returns:
        --------
        None
        """
        self.simulation_server.stop()

    def stop(self):
        """
        Stop the simulation manager.

        This method stops the simulation manager by setting the `running` flag to 
        False and stopping the simulation server.

        Returns:
        --------
        None
        """
        self.running = False
        self.stop_sim()

    def start(self):
        """
        Start the simulation manager.

        This method starts the simulation manager, which continuously checks for 
        changes in the data_mode received via WebSocket.
        If the data_mode changes, the simulation server type is updated accordingly.

        Returns:
        --------
        None
        """
        self.thread_sim_server = Thread(target=self.simulation_server.start)
        self.start_sim()
        self.running = True
        while self.running:
            has_new_msg = self._has_prop(self.websocket.received_data, "data_mode")
            if has_new_msg and self.websocket.received_data["data_mode"] != self.mode:
                mode = self.websocket.received_data["data_mode"]
                if mode == self.mode_4dof and self.mode == self.mode_rt:
                    self.rvg_init = self._format_init(
                        self.simulation_server.rvg_state,
                        self.simulation_server.rvg_heading,
                    )

                print("switching")
                self.mode = self.websocket.received_data["data_mode"]
                self.stop_sim()
                self.set_simulation_type(self.mode)
                self.thread_sim_server = Thread(target=self.simulation_server.start)
                self.start_sim()

    def set_simulation_type(self, mode):
        """
        Set the simulation server type.

        This method sets the simulation server type based on the given mode.

        Parameters:
        -----------
        mode : str
            The simulation mode to set. Can be one of "replay", "4dof", or "rt".

        Returns:
        --------
        None
        """
        if mode == self.mode_replay:
            self.simulation_server = simulation_server_replay(
                log_datastream_manager=self.datastream_manager,
                serializer=self.serializer,
                websocket=self.websocket,
                distance_filter=self.distance_filter,
                predicted_interval=self.predicted_interval,
                colav_manager=self.Colav_Manager,
            )
        elif mode == self.mode_4dof:
            self.simulation_server = simulation_4dof(
                websocket=self.websocket,
                serializer=self.serializer,
                distance_filter=self.distance_filter,
                colav_manager=self.Colav_Manager,
                tmax=self.tmax,
                dt=self.dt,
                rvg_init=self.rvg_init,
            )
        else:
            self.simulation_server = simulation_server(
                serializer=self.serializer,
                websocket=self.websocket,
                distance_filter=self.distance_filter,
                predicted_interval=self.predicted_interval,
                colav_manager=self.Colav_Manager,
            )
