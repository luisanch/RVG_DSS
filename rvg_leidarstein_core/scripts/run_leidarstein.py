#!/usr/bin/env python3
"""
Module: main

Description:
This script serves as the entry point for the RVG Leidarstein application.
It initializes and coordinates various components of the application,
including data processing, communication with external systems, and collision avoidance.

Note:
- This script is meant to be executed as the main entry point of the application. 
"""

from rvg_leidarstein_core.core import core
from time import sleep, time
from multiprocessing import Process, get_context
from rvg_leidarstein_core.colav.colav_manager import colav_manager
from rvg_leidarstein_core.data_relay.rvg_leidarstein_websocket import (
    rvg_leidarstein_websocket,
)

# Configure WebSocket communication
ws_enable = True
ws_address = "ws://127.0.0.1:8000"
websocket = rvg_leidarstein_websocket(ws_address, ws_enable)

# Define Gunnerus ship's MMSI for collision avoidance
gunnerus_mmsi = "258342000"

# Initialize Collision Avoidance Manager (ColavManager)
colav_manager = colav_manager(
    enable=True,
    update_interval=5,
    websocket=websocket,
    gunnerus_mmsi=gunnerus_mmsi,
    safety_radius_m=200,
    safety_radius_tol=1.5,
    max_d_2_cpa=2000,
    print_comp_t=False,
    prediction_t=300,
)

# Initialize Core Data Model
rvg_data = core(
    websocket=websocket,
    colav_manager=colav_manager,
)

if __name__ == "__main__":
    # Prepare for multiprocessing
    process_cbf_data = colav_manager._cbf._process_data
    ctx = get_context("spawn")
    q = ctx.Queue()

    try:
        # Start core and collision avoidance components
        rvg_data.start()
        colav_manager.start()

        # Main loop for handling data processing and collision avoidance
        while True:
            if time() > colav_manager._timeout and colav_manager._running:
                start = time()
                if colav_manager.update():
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

                    # Send computed CBF data
                    colav_manager.send_cbf_data(ret_var)

                end = time()

                if colav_manager.print_c_time:
                    print("end update Arpa + CBF", end - start)

            # Wait for a short duration and handle keyboard interrupt
            sleep(0.1)

    except KeyboardInterrupt:
        # Terminate main threads
        rvg_data.stop()
        print("Exiting...")
