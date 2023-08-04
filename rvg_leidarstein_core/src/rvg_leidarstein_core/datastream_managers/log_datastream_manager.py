#!/usr/bin/env python3

"""
This is the 'log_datastream_manager' module.

It provides the LogDatastreamManager class, which is a specialized version of 
DatastreamManager that includes the ability to log and process incoming messages 
from a data stream.

The LogDatastreamManager inherits from the DatastreamManager class and extends 
its functionality by adding logging capabilities to write the received 
datastream messages to a log file.
"""
from rvg_leidarstein_core.datastream_managers.decrypter import decrypter
from rvg_leidarstein_core.datastream_managers.datastream_manager import (
    datastream_manager,
)
from tqdm import tqdm


class log_datastream_manager(datastream_manager):
    """
    LogDatastreamManager class extends the DatastreamManager class to include 
    logging capabilities.

    The LogDatastreamManager inherits from the DatastreamManager class and adds 
    logging functionality
    to write the received datastream messages to a log file.

    Args:
        path (str): The file path where the log datastream messages will be written.
        loop_limit (int): The limit for recursive iteration loops on parsing. Default is 1.
        verbosity (tuple): A tuple of booleans indicating the verbosity of different log levels.
                           Default is (False, False, False, False, False).
        decrypter (class): The Decrypter class or a subclass to handle decryption of messages.
                           Default is decrypter (from datastream_managers.decrypter).
        drop_ais_messages (bool): Whether to drop AIS messages or not. Default is True.
        prefixFilter (list): A list of message prefixes to filter incoming messages. Default is an empty list.
        suffixFilter (str): A suffix filter for messages. Default is an empty string.
    """

    def __init__(
        self,
        path,
        loop_limit=1,
        verbosity=(False, False, False, False, False),
        decrypter=decrypter,
        drop_ais_messages=True,
        prefixFilter=[],
        suffixFilter="",
    ):
        self.parse_complete = False
        self.prefixFilter = prefixFilter
        self.suffixFilter = suffixFilter
        self.extended_msg_suffix = "_ext"
        # decrypter
        self._decrypter = decrypter

        # method for capping the size of this object might be necessary
        # that or figure out how to throw it to the heap
        self.parsed_msg_list = []

        # incoming ais messages will be ignored if True
        self.drop_ais_messages = drop_ais_messages
        self._running = False

        # keep track of the buffered messages in bytes, doesnt
        # seem to grow at a concerning rate if at all
        self.parsed_msg_list_size = 0

        # [['bad_1','good_1'],['bad_2','good_2'],..,['bad_n','good_n']]
        self.bad_eol_separators = [["\\r", "\r"], ["\\n", "\n"]]
        self.eol_separator = "\r\n"
        self.msg_begin_identifiers = ["!", "$"]

        # Variables for identifying messages
        self.parsed_msg_tags = []
        self.unknown_msg_tags = []

        # This variable sets the limit for recursive iteration loops on parse
        self._loop_limit = loop_limit

        # Variables for console output
        self._raw_verbose = verbosity[0]
        self._tag_verbose = verbosity[1]
        self._unparsed_tag_verbose = verbosity[2]
        self._parsed_message_verbose = verbosity[3]
        self._parse_error_verbose = verbosity[4]

        self.path = path

        # Variables for AIS Decoding
        self.talker = ["!AIVDM", "!AIVDO"]
        self.max_id = 10
        self._buffer = [None] * self.max_id

    def start(self):
        """
        Start processing the datastream messages and log them.

        This method reads the datastream messages from the log file specified in
        the 'path' parameter during initialization. It processes each message by
        parsing it using the '_parse_message' method. The processing of messages
        continues until all lines in the log file have been processed.

        Once the processing is complete, the 'parse_complete' attribute is set 
        to True.

        Returns:
            None
        """
        print("LogDatastreamManager running.")
        self._running = True
        file = open(self.path, "r")
        lines = file.readlines()
        for line in tqdm(lines):
            if not self._running:
                return
            raw_msg = line.encode(encoding="ascii")
            if self._raw_verbose:
                print(raw_msg)
            self._parse_message(raw_msg)
        self.parse_complete = True

        print("LogDatastreamManager Stopped.")
