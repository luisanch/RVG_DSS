from rvg_leidarstein_core.simulation.simulation_server import simulation_server
from rvg_leidarstein_core.simulation.simulation_server_replay import (
    simulation_server_replay,
)
from rvg_leidarstein_core.simulation.simulation_4dof import simulation_4dof
from threading import Thread


class simulation_manager:
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
        msg_keys = msg.keys()
        has_data = prop in msg_keys
        return has_data

    def _format_init(self, msg, head):
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
        self.thread_sim_server.start()

    def stop_sim(self):
        self.simulation_server.stop()

    def stop(self):
        self.running = False
        self.stop_sim()

    def start(self):
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
