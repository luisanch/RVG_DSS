---
author:
- Luis Fernando Sanchez Martin [^1]
date: July 2023
title: Message Reference
---

## Message Reference 

The following section will contain a description of the messages being
received ad transmitted by the components executing the threads and
processes described in the previous section.

## Websocket Message Reference

The WebSocket sends messages when prompted by other modules. This
component also receives messages from the frontend, these are the
feedback for the `core` module.

Message for simulation type:

        {
          type: "datain",
          content: {
            message_id: "data_mode",
            val: "value",
          },
        }

Inputs for 4DOF simulation:

        {
          type: "datain",
          content: {
            message_id: "control_azi",
            val: value,
          },
        };

        {
          type: "datain",
          content: {
            message_id: "control_thrust",
            val: value,
          },
        };

## Datastream Manager Message Reference

### Input 

The input of the `datastream_manager` can be any of the strings
described in the appendix

### Output 

the output of this component is a list containing the objects as parsed
by the `pyais` and `pynmea2` libraries. An example of a AIS object is

        MessageType1(
        msg_type=1, 
        repeat=0, 
        mmsi=257131220,
        status=
        <NavigationStatus.Undefined: 15>, 
        turn=<TurnRate.NO_TI_DEFAULT: -128.0>, 
        speed=0.0, 
        accuracy=True, 
        lon=10.361998, 
        lat=63.432855, 
        course=360.0, 
        heading=511, 
        second=36, 
        maneuver=<ManeuverIndicator.NotAvailable: 0>, 
        spare_1=b'\x00', 
        raim=True,
        radio=66921
        )

The NMEA object depends on the kind of message that is being received
and it contains the relevant attributes and values. An example of a NMEA
object for a GPRMC message is:

        GPRMC(
        timestamp=datetime.time(16, 23, 17, 500000, tzinfo=datetime.timezone.utc)
        status='A', 
        lat='6326.3036',
        lat_dir='N', 
        lon='01024.5386', 
        lon_dir='E', 
        spd_over_grnd=0.0,
        true_course=195.5,
        datestamp=datetime.date(2023, 8, 6), 
        mag_variation='4.7', 
        mag_var_dir='E', 
        mode_indicator='A', 
        nav_status='S'
        )

## Serializer Message Reference

### Input 

The serializer takes as input the list of objects provided by the
`datastream_manager`

### Output 

The output of the `fast_serializer` is a list composed of the serialized
NMEA and AIS messages (dictionaries). The following messages can be
expected to be in the output list of the component:

AIS message:

    {
    'msg_type': 1, 
    'repeat': 0,
    'mmsi': 258342000, 
    'status': <NavigationStatus.Moored: 5>, 
    'turn': 0.0, 
    'speed': 0.0, 
    'accuracy': True, 
    'lon': 10.408968, 
    'lat': 63.453595, 
    'course': 335.2, 
    'heading': 449, 
    'second': 0, 
    'maneuver': <ManeuverIndicator.NotAvailable: 0>, 
    'spare_1': b'\x00', 
    'raim': False, 
    'radio': 0, 
    'unix_time': 1691340458.702, 
    'seq_num': 11449976,
    'src_id': 2, 
    'src_name': '@10.0.8.10:35481', 
    'message_id': '!AIVDO_ext_258342000'
    }

NMEA GPRMC message:

    {
    'timestamp': datetime.time(16, 47, 37, 500000,...),
    'status': 'A', 
    'lat': '6326.3037', 
    'lat_dir': 'N', 
    'lon': '01024.5381', 
    'lon_dir': 'E', 
    'spd_over_grnd': 0.0, 
    'true_course': 190.8,
    'datestamp': datetime.date(2023, 8, 6), 
    'mag_variation': '4.7',
    'mag_var_dir': 'E', 
    'mode_indicator': 'A', 
    'nav_status': 'S', 
    'unix_time': 1691340457.962,
    'seq_num': 11449967, 
    'src_id': 1, 
    'src_name': 'a10.0.8.1', 
    'message_id': '$GPRMC_ext'
    }

NMEA PSIMSNS message:

    {
    'msg_type': 'SNS', 
    'timestamp': '164742.292',
    'unknown_1': '', 
    'tcvr_num': '1', 
    'tdcr_num': '1',
    'roll_deg': '0.28',
    'pitch_deg': '-0.82', 
    'heave_m': '0.01', 
    'head_deg': '199.44', 
    'empty_1': '', 
    'unknown_2': '40', 
    'unknown_3': '0.001',
    'empty_2': '', 
    'checksum': 'M121', 
    'unix_time': 1691340458.27,
    'seq_num': 11449970,
    'src_id': 3,
    'src_name': '@10.0.8.10:39816',
    'message_id': '$PSIMSNS_ext'
    }

NMEA GPGGA message:

    {
    'timestamp': datetime.time(16, 47, 37, 500000,...),
    'lat': '6326.3037', 
    'lat_dir': 'N',
    'lon': '01024.5381', 
    'lon_dir': 'E', 
    'gps_qual': 1,
    'num_sats': '11', 
    'horizontal_dil': '0.7', 
    'altitude': 14.2,
    'altitude_units': 'M',
    'geo_sep': '41.4', 
    'geo_sep_units': 'M', 
    'age_gps_data': '',
    'ref_station_id': '', 
    'unix_time': 1691340458.274,
    'seq_num': 11449971, 
    'src_id': 1, 
    'src_name': '@10.0.8.10:42796',
    'message_id': '$GPGGA_ext'
    }

It is worth noting that the following attributes are appended to the
messages as part of the encrypted data being relayed by the Olex
computer:

-   `'unix_time'`

-   `'seq_num'`

-   `'src_id'`

-   `'src_name'`

## Simulation Manager Message Reference

### Input 

The input for the `simulation_manager` is the list of dictionaries
provided by the `fast_serializer`

### Output 

The output of this component is strings of JSON messages for the
WebSocket to relay. Additionally, this component keeps track of the
latest data for each type of message and updates the Colav Manager
attributes.

AIS message example:

    {
    "type": "datain", 
    "content": {
        "msg_type": 1,
        "repeat": 0,
        "mmsi": 258342000, 
        "status": 5, 
        "turn": 0.0,
        "speed": 0.0,
        "accuracy": true,
        "lon": 10.408952, 
        "lat": 63.45423,
        "course": 72.8,
        "heading": 262,
        "second": 1,
        "maneuver": 0, 
        "spare_1": "b'\\x00'",
        "raim": false, 
        "radio": 0, 
        "unix_time": 1691353146.021,
        "seq_num": 11595825,
        "src_id": 2, 
        "src_name": "@10.0.8.10:35481", 
        "message_id": "!AIVDO_ext_258342000",
        "pos_history": [[10.408952, 63.454228], (...), [10.408952, 63.45423]]
        }
    }

NMEA PSIMSNS message:

    {
    "type": "datain", 
    "content": {
        "msg_type": "SNS", 
        "timestamp": "22:19:07.837150", 
        "unknown_1": "", 
        "tcvr_num": "1", 
        "tdcr_num": "1", 
        "roll_deg": 0.0, 
        "pitch_deg": 0, 
        "heave_m": "0.00", 
        "head_deg": -40.0, 
        "empty_1": "", 
        "unknown_2": "40", 
        "unknown_3": "0.000", 
        "empty_2": "", 
        "checksum": "M121", 
        "unix_time": 1691353147.8371496, 
        "seq_num": 39, 
        "src_id": 1, 
        "src_name": "@10.0.8.10:39816",
        "message_id": "$PSIMSNS_ext"
        }
    }

NMEA GPGGA message:

    {
    "type": "datain", 
    "content": {
        "timestamp": "22:19:07.837150", 
        "lat": 6326.305279636112, 
        "lat_dir": "N", 
        "lon": 1024.5376641753296,
        "lon_dir": "E", 
        "gps_qual": 1, 
        "num_sats": "10",
        "horizontal_dil": "1.0",
        "altitude": 12.6,
        "altitude_units": "M",
        "geo_sep": "41.4", 
        "geo_sep_units": "M",
        "age_gps_data": "", 
        "ref_station_id": "", 
        "unix_time": 1691353147.8371496,
        "seq_num": 40, 
        "src_id": 3,
        "src_name": "@10.0.8.10:34340",
        "message_id": "$GPGGA_ext"
        }
    }

NMEA GPRMC message:

    {
    "type": "datain", 
    "content": {
        "timestamp": "22:19:07.237150",
        "status": "A", 
        "lat": 6326.305135176538,
        "lat_dir": "N",
        "lon": 1024.5379348907738,
        "lon_dir": "E", 
        "spd_over_grnd": 1.0929829421120387, 
        "true_course": -40.0,
        "datestamp": "2023-08-06",
        "mag_variation": "4.7",
        "mag_var_dir": "E",
        "unknown_0": "A",
        "unknown_1": "S",
        "unix_time": 1691353147.2371497, 
        "seq_num": 38, 
        "src_id": 3, 
        "src_name": "a10.0.8.1",
        "message_id": "$GPRMC_ext"
        }
    }

## Colav Manager Message Reference

The `colav_manager` consists of two main components, the `arpa`
component for obtaining ARPA parameters and the `cbf` component for
obtaining the information related to Control Barrier Functions.

### Input 

This component acquires data by storing NMEA and AIS data as attributes
(`self._ais_data[mmsi] = data`, `self._gunnerus_data = data`). these
attributes are updated when new data is received by the Simulation
Manager.

Example of AIS data stored in the colav manager:

    self._ais_data[258342000] = {
        'msg_type': 1, 
        'repeat': 0,
        'mmsi': 258342000,
        'status': <NavigationStatus.Moored: 5>, 
        'turn': 0.0,
        'speed': 0.0, 
        'accuracy': True, 
        'lon': 10.40896, 
        'lat': 63.453905,
        'course': 79.2, 
        'heading': 266,
        'second': 1,
        'maneuver': <ManeuverIndicator.NotAvailable: 0>,
        'spare_1': b'\x00',
        'raim': False, 
        'radio': 0, 
        'unix_time': 1691355550.095,
        'seq_num': 11622741,
        'src_id': 2,
        'src_name': '@10.0.8.10:35481', 
        'message_id': '!AIVDO_ext_258342000', 
        'pos_history': [[10.408958, 63.453898], (...), [10.40896, 63.453905]]
        }

Similarly, the following data is stored for Gunnerus:

    self._gunnerus_data = {
        'timestamp': datetime.time(22, 59, 9, 616093),
        'status': 'A',
        'lat': 6326.305969691541,
        'lat_dir': 'N',
        'lon': 1024.5363710191984, 
        'lon_dir': 'E', 
        'spd_over_grnd': 1.5323130672165104, 
        'true_course': -40.0,
        'datestamp': datetime.date(2023, 8, 6),
        'mag_variation': '4.7',
        'mag_var_dir': 'E', 
        'unknown_0': 'A', 
        'unknown_1': 'S',
        'unix_time': 1691355549.6160932, 
        'seq_num': 53, 
        'src_id': 3, 
        'src_name': 'a10.0.8.1',
        'message_id': '$GPRMC_ext'
        }

This data is used by the ARPA component.

### Output 

The output of the Colav Manager is the information relayed via
WebSockets by the ARPA and CBF components.

### ARPA

### ARPA Input 

This component takes as input the data stored in the aforementioned
attributes.

### ARPA Output 

The `arpa` component produces two main outputs, one made from the
resulting calculations converted to geodetic coordinates that are
relayed via websockets to the frontend:

    {
    "type": "datain",
    "content": {
        "message_id": "arpa",
            "data": {
                "2570221": {
                    "self_course": -40.0,         #rvg course
                    "course": 0,                  #targer ship course
                    "t_2_cpa": 558.8694955229263, #time to cpa
                    "lat_o": 63.442017999990306,  #origin lat of target vessel
                    "lon_o": 10.403963000013439,  #origin lon of target vessel
                    "uo": 0.0,                    #speed of target vessel
                    "zo": "[[0.]\n [1.]]",        #orientation of target vessel
                    "d_at_cpa": 66.63601614808934, #distance at cpa
                    "d_2_cpa": 465.2980767097945,   #distance to cpa
                    "lat_at_cpa": 63.4416337020036, #target vessel lat at cpa
                    "lon_at_cpa": 10.402940216628501, #target vessel lon at cpa
                    "lat_o_at_cpa": 63.442017999990306, #rvg lat at cpa
                    "lon_o_at_cpa": 10.403963000013439, #rvg lon at cpa
                    "safety_params": true, #true if rvg will get closer than saf rad at cpa
                    "t_2_r": 332.37490497999767, #time to safety radius 
                    "lat_o_at_r": 63.442017999990306, #rvg lat at safety rad
                    "lon_o_at_r": 10.403963000013439, #rvg lon at safety rad
                    "lat_at_r": 63.440337857723435,   #target vessel lon at safety rad
                    "lon_at_r": 10.405369196577027,   #target vessel lon at safety rad
                    "d_2_r": 276.7254346009467,       # distance before the safety radius
                    "safety_radius": 200
                            }, (...)
                "2572222": {
                    "self_course": -40.0,
                    "course": 0, 
                    "t_2_cpa": 767.8156155573266,
                    "lat_o": 63.44410799996819, 
                    "lon_o": 10.404103000027073,
                    "uo": 0.0,
                    "zo": "[[0.]\n [1.]]",
                    "d_at_cpa": 221.75117238015486, 
                    "d_2_cpa": 639.2603855615433, 
                    "lat_at_cpa": 63.442829109372276,
                    "lon_at_cpa": 10.400699235848839, 
                    "lat_o_at_cpa": 63.44410799996819, 
                    "lon_o_at_cpa": 10.404103000027073, 
                    "safety_params": false
                        }, 
                    }
                }
    }

And the data still in NED frame used for the CBF component for gunnerus:

         {
         'p': array([[0],[0]]), #position (located at origin)
         'u': 0.7882831342988617, #speed
         'ux': -0.5066986316521784, #speed x component
         'uy': 0.6038599146340541,  #speed y component
         'z': array([[-0.64278761], [ 0.76604444]]), #rvg orientation
         'tq': array([[-0.64278761],[ 0.76604444]]), #rvg target orientation
         'lon': 10.40893951698664, 
         'lat': 63.43843282819234, 
         'course': -40.0
         }

And the data in NED frame used for the CBF component for AIS vessels:

    [
        { #target vessel 1
        'po_x': -248.4036616045414, #starting x position 
        'po_y': 399.5323145183838,  #starting y position 
        'uo': 0.0,                  #speed
        'zo': array([[0.],[1.]]),   #orientation
        'uo_x': 0.0,                #speed x component
        'uo_y': 0.0,                #speed y component
        'course': 0,
        'mmsi': 2570221, 
        'cpa': {
            'd_at_cpa': 66.5261768192365,    # distance at cpa
            'd_2_cpa': 465.73030526343894,   # distance to cpa
            't_2_cpa': 590.8160215525639,    # time to cpa
            'x_at_cpa': -299.36566967886813, # target vessels x pos at cpa
            'y_at_cpa': 356.7701123391627,   # target vessels y pos at cpa
            'o_x_at_cpa': -248.4036616045414,# rvg x pos at cpa
            'o_y_at_cpa': 399.5323145183838  # rvg y pos at cpa
            }, 
        'safety_params': {
            't_2_r': 351.54739850532616,   # time to safety radius
            't_x_at_r': -248.4036616045414,# target vessel x at safety rad
            't_y_at_r': 399.5323145183838, # target vessel y at safety rad
            'x_at_r': -178.12858578353183, # rvg x at safety rad
            'y_at_r': 212.28538205125005,  # rvg y at safety rad
            'd_2_r': 277.11888514838944}   # distance to safety radius
            },
        { #target vessel n
        'po_x': -241.34943827321155, 
        'po_y': (...)
        }
        ]

## CBF

### CBF Input 

The input for the CBF is the NED data provided by the ARPA component as
mentioned in the previous subsection.

### CBF Output 

The output of the CBF component is a JSON message containing the
geodetic points required to draw the resulting trajectory.

        {
        "type": "datain", 
        "content": {
            "message_id": "cbf",
            "data": {
                "cbf": [[10.408939516986642, 63.43843282819234], (...),  
                        [10.408939516986642, 63.43843282819234]]
                    }
                }
        }

[^1]: luissanchezmtn@gmail.com 
 