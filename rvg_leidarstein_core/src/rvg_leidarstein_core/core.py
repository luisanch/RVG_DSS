from threading import Thread
import pathlib
import os
from datetime import datetime
import easygui
from rvg_leidarstein_core.datastream_managers.tcp_datastream_manager import (
    tcp_datastream_manager,
)
from rvg_leidarstein_core.datastream_managers.log_datastream_manager import (
    log_datastream_manager,
)
from rvg_leidarstein_core.serializers.fast_serializer import fast_serializer
from rvg_leidarstein_core.colav.colav_manager import colav_manager
from rvg_leidarstein_core.simulation.simulation_manager import simulation_manager
from rvg_leidarstein_core.data_relay.rvg_leidarstein_websocket import rvg_leidarstein_websocket
from rvg_leidarstein_core.datastream_managers.decrypter import decrypter


class core:
    def __init__(
        self, colav_manager=colav_manager, websocket=rvg_leidarstein_websocket, log_file=None
    ):
        # Todo: add flush() functionality across related classes to purge data
        # and prevent stack overflow / slowdown over extended use
        self.abs_path = pathlib.Path(__file__).parent.resolve()

        # Settings/address for gunnerus datastream
        # global: fagitrelay.it.ntnu.no
        # local: gunnerus.local
        self.address = ("fagitrelay.it.ntnu.no", 25508)
        self.buffer_size = 4096
        self.loop_limit = 1
        self.log_file = log_file
        # raw_verbose, tag_verbose, unparsed_tag_verbose,
        # parsed_message_verbose, parse_error_verbose
        self.verbosity = (False, False, False, False, False)
        self.now = datetime.now()
        self.date_time = self.now.strftime("%m%d%y_%H-%M-%S")
        self.save_logs = False
        self.log_time = 60
        self.log_name = (
            "./datastream_" + self.date_time + "_" + str(self.log_time) + "s.txt"
        )
        self.log_path = os.path.join(self.abs_path, "DataStreams", self.log_name)
        self.log_stream = (self.log_path, self.log_time, self.save_logs)
        self.colav_manager = colav_manager
        self.key_path = os.path.join(self.abs_path, "rvg_dss", "key")
        self.datastream_decrypter = decrypter(key_path=self.key_path)
        self.websocket = websocket
        # if True a log can be selected and used as the data source
        self.stream_saved_log = False
        self.drop_ais_message = False

        # automatically true if using a log file as an arg
        if self.log_file is not None:
            self.stream_saved_log = True
            self.load_path = self.log_file

        # filter for messages: mesages not including these strings are dropped
        self.prefixFilter = ["$PSIMSNS", "!AI", "$GPGGA", "$GPRMC"]
        self.suffixFilter = "_ext"

        # Select and initialize DatastreamManager
        if self.stream_saved_log:
            if self.log_file is None:
                self.load_path = easygui.fileopenbox()

            self.datastream_manager = log_datastream_manager(
                path=self.load_path,
                verbosity=self.verbosity,
                decrypter=self.datastream_decrypter,
                drop_ais_messages=self.drop_ais_message,
                prefixFilter=self.prefixFilter,
                suffixFilter=self.suffixFilter,
            )
        else:
            self.datastream_manager = tcp_datastream_manager(
                address=self.address,
                buffer_size=self.buffer_size,
                verbosity=self.verbosity,
                log_stream=self.log_stream,
                decrypter=self.datastream_decrypter,
                drop_ais_messages=self.drop_ais_message,
                prefixFilter=self.prefixFilter,
                suffixFilter=self.suffixFilter,
            )

        # Initialize Serializer
        self.headers_path = os.path.join(self.abs_path, "./serializers/headers")
        self.save_headers = (True, self.headers_path)

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
            ],
            "$PSIMSNS_ext": [
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
            ],
        }

        self.overwrite_headers = True
        self.dl_verbose = (False, False)

        self.serializer = fast_serializer(
            datastream_manager=self.datastream_manager,
            save_headers=self.save_headers,
            df_aliases=self.df_aliases,
            overwrite_headers=self.overwrite_headers,
            verbose=self.dl_verbose,
        )

        # Initialize Simulation Manager
        self.distance_filter = 1  # geodetic degree

        # dummy_gunnerus is now the origin for 4dof sim
        self.dummy_gunnerus = {
            "lat": 6326.3043,
            "lat_dir": "E",
            "lon": 1024.5395,
            "lon_dir": "N",
            "true_course": -40,
            "spd_over_grnd": 0,
            "revs": 100,
            "azi_d": 0,
        }

        self.dummy_vessel = {
            "lon": 10.411565,
            "lat": 63.44141,
            "course": 135,
            "heading": 190,
            "speed": 0,
            "mmsi": 3143757,
            "message_id": "!AI_ext_dummy",
            "pos_history": [[10.482652, 63.473148]],
        }

        self.run_4DOF_sim = True

        self.simulation_manager = simulation_manager(
            datastream_manager=self.datastream_manager,
            serializer=self.serializer,
            websocket=self.websocket,
            distance_filter=self.distance_filter,
            Colav_Manager=self.colav_manager,
            rvg_init=self.dummy_gunnerus,
            tmax=1,
            dt=0.2,
            predicted_interval=60,
            mode="4dof",
        )

        # Select 'Simulation' source: saved log, 4dof, or rt
        if self.stream_saved_log:
            self.simulation_manager.set_simulation_type(
                self.simulation_manager.mode_replay
            )
        elif self.run_4DOF_sim:
            self.simulation_manager.set_simulation_type(self.simulation_manager.mode_4dof)
        else:
            self.simulation_manager.set_simulation_type(self.simulation_manager.mode_rt)

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
