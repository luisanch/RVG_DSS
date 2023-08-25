#!/usr/bin/env python3

from rvg_leidarstein_core.core import core
from time import sleep, time 
from multiprocessing import Process, get_context
from rvg_leidarstein_core.colav.colav_manager import colav_manager
from rvg_leidarstein_core.data_relay.rvg_leidarstein_websocket import (
    rvg_leidarstein_websocket,
)

ws_enable = True
ws_address = "ws://127.0.0.1:8000"
websocket = rvg_leidarstein_websocket(ws_address, ws_enable)
gunnerus_mmsi = "258342000"

# Initialize ColavManager
colav_manager = colav_manager(
    enable=True,
    update_interval=5,
    websocket=websocket,
    gunnerus_mmsi=gunnerus_mmsi,
    dummy_gunnerus=None,
    dummy_vessel=None,
    safety_radius_m=200,
    safety_radius_tol=1.5,
    max_d_2_cpa=2000,
    print_comp_t=False,
    prediction_t=300,
)

# Initialize DataModel

rvg_data = core(
    websocket=websocket,
    colav_manager=colav_manager,
)

if __name__ == "__main__":
    process_cbf_data = colav_manager._cbf._process_data
    ctx = get_context("spawn")
    q = ctx.Queue()

    try:
        rvg_data.start()
        colav_manager.start()

        # CBF process is created here
        while True:
            if time() > colav_manager._timeout and colav_manager._running:
                start = time()
                if colav_manager.update():
                    # remember to add ocnidtion here for diff cbfs
                    (
                        p,
                        u,
                        z,
                        tq,
                        po,
                        zo,
                        uo,
                        encounters,
                        vessels_len,
                    ) = colav_manager.sort_cbf_data()
                    domains = colav_manager.cbf_domains
                    # CBF computation is run in a separate process
                    cbf_process = Process(
                        # here too
                        target=process_cbf_data,
                        args=(
                            domains,
                            encounters,
                            vessels_len,
                            p,
                            u,
                            z,
                            tq,
                            po,
                            zo,
                            uo,
                            q,
                        ),
                    )
                    cbf_process.start()
                    ret_var = q.get()
                    cbf_process.join()
                    colav_manager.send_cbf_data(ret_var)
                end = time()

                if colav_manager.print_c_time:
                    print("end update Arpa + CBF", end - start)

            # wait around, catch keyboard interrupt
            sleep(0.1)

    except KeyboardInterrupt:
        # terminate main thread
        rvg_data.stop()
        print("Exiting...")
