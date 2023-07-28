from rvg_leidarstein_core.datastream_managers.log_datastream_manager import (
    log_datastream_manager,
)
from rvg_leidarstein_core.serializers.fast_serializer import fast_serializer
from rvg_leidarstein_core.simulation.simulation_server import simulation_server
from rvg_leidarstein_core.data_relay.rvg_leidarstein_websocket import rvg_leidarstein_websocket
from rvg_leidarstein_core.colav.colav_manager import colav_manager
from time import time


class simulation_server_replay(simulation_server):
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
