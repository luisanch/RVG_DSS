#!/usr/bin/env python3
"""
Module: fast_serializer

Description:
This module contains the FastSerializer class, which is a subclass of the Serializer class. 
FastSerializer provides a fast and efficient method to serialize datastream messages using 
DataFrame aliases and metadata.

The FastSerializer class inherits attributes and methods from the Serializer class and 
overrides some of them to improve serialization performance.
"""

from rvg_leidarstein_core.serializers.serializer import serializer
from rvg_leidarstein_core.datastream_managers.datastream_manager import (
    datastream_manager,
)


class fast_serializer(serializer):
    def __init__(
        self,
        save_headers,
        df_aliases,
        datastream_manager=datastream_manager,
        overwrite_headers=False,
        verbose=False,
    ):
        """
        Fast serializer for datastream messages.

        This class extends the 'Serializer' class to provide faster serialization
        of datastream messages. It is designed to work with a 'datastream_manager'
        for receiving and parsing messages and creating DataFrames for serialization.

        Args:
            save_headers (tuple): A tuple containing two elements: a boolean
                                indicating whether to save DataFrame headers or
                                not, and the directory path where DataFrame
                                headers should be saved as CSV files.
            df_aliases (dict): A dictionary that maps DataFrame aliases (keys) to
                                lists of attribute names (values). This mapping
                                defines how DataFrame columns will be created and
                                named during serialization.
            datastream_manager (datastream_manager, optional): An instance of the
                                'datastream_manager' class that will be used
                                for receiving and parsing messages. Defaults to
                                'datastream_manager'.
            overwrite_headers (bool, optional): If True, DataFrame headers will
                                be overwritten even if they already exist.
                                Defaults to False.
            verbose (tuple, optional): A tuple containing two boolean values:
                                the first one indicating whether to enable log
                                verbosity for the serializer, and the second one
                                indicating whether to enable log verbosity for
                                the buffer data. Defaults to False for both.

        Note:
            If 'overwrite_headers' is set to False, the serializer will attempt
            to load DataFrame headers from the specified directory during class
            initialization. The DataFrame headers should be saved as CSV files
            in that directory.

        Attributes:
            df_aliases (dict): A dictionary that maps DataFrame aliases to lists
                                of attribute names.
            def_unk_atr_name (str): The name for unknown attributes (used when
                                mapping DataFrame columns).
            bufferBusy (bool): A flag to indicate if the buffer is busy (during
                                serialization).
            _datastream_manager (datastream_manager): An instance of the 'datastream_manager'
                                class used for receiving and parsing messages.
            sorted_data (list): A list to store sorted data.
            _running (bool): A flag to indicate whether the serializer is running
                                or stopped.
            _save_headers (bool): A boolean indicating whether to save DataFrame
                                headers or not.
            _headers_path (str): The directory path where DataFrame headers should
                                be saved as CSV files.
            _buffer_data (list): A list to store parsed message data received from
                                the datastream manager.
            _overwrite_headers (bool): A boolean indicating whether to overwrite
                                DataFrame headers if they already exist.
            _log_verbose (bool): A boolean indicating whether to enable log
                                verbosity for the serializer.
            _buffer_verbose (bool): A boolean indicating whether to enable log
                                verbosity for the buffer data.
            metadata_atr_names (tuple): A tuple containing attribute names
                                ('unix_time', 'seq_num', 'src_id', 'src_name') for
                                the metadata of parsed messages.
        """
        # attribute aliases for incoming messages
        self.df_aliases = df_aliases

        # define name for unknown atribute
        self.def_unk_atr_name = "unknown_"
        self.bufferBusy = False
        self._datstream_manager = datastream_manager
        self.sorted_data = []
        self._running = False
        self._save_headers = save_headers[0]
        self._headers_path = save_headers[1]
        self._buffer_data = datastream_manager.parsed_msg_list
        self._overwrite_headers = overwrite_headers
        self._log_verbose = verbose[0]
        self._buffer_verbose = verbose[1]
        self.metadata_atr_names = ("unix_time", "seq_num", "src_id", "src_name")

        if not self._overwrite_headers:
            self._load_headers()

    def _serialize_data(self, message):
        """
        Serialize a single datastream message.

        This method takes a single datastream message in the form of a tuple and
        serializes its attributes based on the provided DataFrame aliases and
        metadata. The serialized message is added to the 'sorted_data' list.

        Args:
            message (tuple): A tuple containing the following elements:
                             - msg_id (str): The message identifier.
                             - msg_atr (list): A list of attribute names for the message.
                             - msg_values (list): A list of attribute values for the message.
                             - unkown_msg_data (list): A list of unknown message data (if any).
                             - metadata (tuple, None): A tuple containing metadata information for the message
                                                      (or None if no metadata is present).

        Note:
            This method is called internally during the serialization process
            and should not be called directly.

        """
        msg_id, msg_atr, msg_values, unkown_msg_data, metadata = message

        # ToDo: Probably very inefficient
        if len(unkown_msg_data) > 1:
            msg_values.extend(unkown_msg_data)

            for i, _ in enumerate(unkown_msg_data):
                atr_name = self.def_unk_atr_name + str(i)
                msg_atr.append(atr_name)

        # ToDo: awful, inefficient, do better check and skip redundancy
        if msg_id in self.df_aliases:
            alias_list = self.df_aliases[msg_id]
            if len(alias_list) == len(msg_atr):
                for i, alias in enumerate(alias_list):
                    msg_atr[i] = alias

        # ToDo: Probably very inefficient x2
        if metadata is not None:
            msg_values.extend(metadata)
            msg_atr.extend(self.metadata_atr_names)

        message = dict(zip(msg_atr, msg_values))
        message["message_id"] = msg_id
        self.sorted_data.append(message)
        return

    def _serialize_buffered_message(self):
        """
        Serialize a buffered datastream message.

        This method serializes a datastream message from the buffered data
        (parsed_msg_list) of the datastream manager. The serialized message is
        added to the 'sorted_data' list of the serializer.

        Note:
            This method is called internally during the serialization process
            and should not be called directly.
        """
        if len(self._buffer_data) < 1:
            self.bufferBusy = False
            if self._buffer_verbose:
                print("Buffer Empty")
            return

        self.bufferBusy = True
        _message = self._buffer_data[-1][1]
        msg_id = self._buffer_data[-1][0]

        if msg_id.find("!AI") == 0:
            msg_atr, msg_values, unkown_msg_data, mmsi = self._get_ais_attributes(
                _message
            )
            msg_id = msg_id + "_" + str(mmsi)
        else:
            msg_atr, msg_values, unkown_msg_data = self._get_nmea_attributes(_message)

        if len(self._buffer_data[-1]) == 3:
            metadata = self._buffer_data[-1][2]
        else:
            metadata = None

        message = (msg_id, msg_atr, msg_values, unkown_msg_data, metadata)

        self._serialize_data(message)
        self._datstream_manager.pop_parsed_msg_list()

    def start(self):
        """
        Start the FastSerializer.

        This method starts the FastSerializer's serialization process. It
        continuously calls the '_serialize_buffered_message' method to serialize
        buffered datastream messages until the '_running' attribute is set to False.

        Note:
            This method should be called after initializing the FastSerializer
            to begin the serialization process.

        """
        self._running = True
        print("FastSerializer running.")

        while self._running:
            self._serialize_buffered_message()
        # ToDo: handle loose ends on terminating process.
        print("FastSerializer stopped.")
