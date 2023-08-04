#!/usr/bin/env python3

"""
This is the 'serializer' module.

It provides the Serializer class, which is responsible for serializing datastream messages into
pandas DataFrames and optionally saving them to CSV files.

The Serializer takes a DatastreamManager instance as input and processes the parsed messages
received from the datastream. It provides options to save the headers of the DataFrame and the
DataFrame itself to separate CSV files.
"""


import pandas as pd
from os import listdir
from os.path import isfile, join


class sorted_data(object):
    def __getitem__(self, item):
        return getattr(self, item)


class serializer:
    """
    Serializer class handles the serialization of datastream messages into pandas 
    DataFrames.

    The Serializer takes a DatastreamManager instance as input and processes the 
    parsed messages received from the datastream. It provides options to save the 
    headers of the DataFrame and the DataFrame itself to separate CSV files.

    Args:
        datastream_manager (DatastreamManager): The DatastreamManager instance to receive parsed messages from.
        save_headers (tuple): A tuple containing a boolean flag for saving headers to CSV (True/False)
                              and the path (str) to the CSV file where headers will be saved.
        save_dataframes (tuple): A tuple containing a boolean flag for saving DataFrames to CSV (True/False)
                                 and the path (str) to the directory where DataFrame CSV files will be saved.
        df_aliases (dict): A dictionary mapping DataFrame names (aliases) to their corresponding parsed message tags.
                           Example: {'df1': 'TAG1', 'df2': 'TAG2'}
        overwrite_headers (bool): Whether to overwrite existing header CSV file or not. Default is False.
        verbose (tuple): A tuple containing two boolean flags for verbose logging. The first flag is for log verbosity
                         related to the log files ('save_headers' and 'save_dataframes'), and the second flag is for
                         buffer verbosity, which shows messages being processed. Default is (False, False).

    Attributes:
        def_unk_atr_name (str): The name to be used for unknown attributes (not found in 'df_aliases').
        metadata_atr_names (tuple): A tuple containing the attribute names for metadata information: unix_time, seq_num,
                                    src_id, and src_name.
    """
    def __init__(
        self,
        datastream_manager,
        save_headers,
        save_dataframes,
        df_aliases,
        overwrite_headers=False,
        verbose=False,
    ):

        # attribute aliases for incoming messages
        self.df_aliases = df_aliases

        # define name for unknown atribute
        self.def_unk_atr_name = "unknown_"

        self._datastream_manager = datastream_manager
        self.sorted_data = sorted_data()
        self._running = False
        self._save_headers = save_headers[0]
        self._headers_path = save_headers[1]
        self._save_df = save_dataframes[0]
        self._dataframes_path = save_dataframes[1]
        self._buffer_data = datastream_manager.parsed_msg_list
        self._overwrite_headers = overwrite_headers
        self._log_verbose = verbose[0]
        self._buffer_verbose = verbose[1]
        self.metadata_atr_names = ("unix_time", "seq_num", "src_id", "src_name")

        if not self._overwrite_headers:
            self._load_headers()

    def _get_nmea_attributes(self, nmea_object):
        """
        Get attributes and values from a parsed NMEA message object.

        This method takes a parsed NMEA message object and extracts its attributes and values.
        For attributes with known names, they are included in the 'msg_atr' list along with their
        corresponding values in the 'msg_values' list. If the NMEA object contains additional
        data fields that are not defined in the NMEA message format, they are included in the
        'unknown_msg_data' list.

        Args:
            nmea_object (pynmea2.ParsedLine): The parsed NMEA message object.

        Returns:
            tuple: A tuple containing three lists: 'msg_atr' (attribute names), 'msg_values' (attribute values),
                   and 'unknown_msg_data' (additional data fields not defined in the NMEA message format).
        """
        t = type(nmea_object)
        msg_values = []
        msg_atr = []
        unkown_msg_data = []

        for i, v in enumerate(nmea_object.data):
            if i >= len(t.fields):
                unkown_msg_data.append(v)
                continue
            name = t.fields[i][1]
            msg_atr.append(name)
            msg_values.append(getattr(nmea_object, name))

        return (msg_atr, msg_values, unkown_msg_data)

    def _get_ais_attributes(self, ais_object):
        """
        Get attributes and values from a parsed AIS message object.

        This method takes a parsed AIS message object and extracts its attributes
        and values. The attributes and values are stored in the 'msg_atr' and 
        'msg_values' lists, respectively. Additionally, the MMSI (Maritime Mobile Service Identity) 
        attribute is extracted separately from the AIS message object and included 
        in the 'msg_atr' and 'msg_values' lists.

        Args:
            ais_object (dict): The parsed AIS message object obtained from the 'ais_decode' function.

        Returns:
            tuple: A tuple containing four lists: 'msg_atr' (attribute names), 'msg_values' (attribute values),
                   an empty list (as there are no unknown attributes for AIS messages), and 'mmsi' (MMSI attribute value).
        """
        ais_dict = ais_object.asdict()
        msg_values = list(ais_dict.values())
        msg_atr = list(ais_dict.keys())
        mmsi = ais_dict["mmsi"]

        return (msg_atr, msg_values, [], mmsi)

    def _load_headers(self):
        """
        Load DataFrame headers from CSV files.

        This method loads DataFrame headers from .pkl files located in the 
        directory specified by 'save_headers' during the class initialization.
        The .pkl files should contain the headers (column names) of the DataFrames
        that will be created during serialization. The headers are loaded into 
        DataFrame objects and stored as attributes in the 'sorted_data' object. 
        The attribute names are based on the names of the messages received.

        Note:
            This method is automatically called during class initialization unless 
            'overwrite_headers' is set to True.

        Returns:
            None
        """
        headers = []
        names = []
        dir_list = listdir(self._headers_path)

        if len(dir_list) < 1:
            return

        print("Loading headers...")
        for name in dir_list:
            file = join(self._headers_path, name)
            if isfile(file):
                headers.append(file)
                names.append(name.split(".")[0])

        for name, file in zip(names, headers):
            df = pd.read_pickle(file)
            setattr(sorted_data, name, df)
        print("Headers Loaded.")

    def stop(self):
        """
        Stop the serializer.

        This method sets the '_running' flag to False, stopping the serialization
        process.

        Returns:
            None
        """
        self._running = False
        print("Serializer stopped.")

    def start(self):
        """
        Start the serializer.

        This method sets the '_running' flag to True, enabling the serialization 
        process to start. The serializer will begin processing the parsed messages 
        received from the datastream manager and create DataFrames according to 
        the DataFrame aliases provided during class initialization.

        Returns:
            None
        """
        self._running = True
        print("Serializer running.")
