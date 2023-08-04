#!/usr/bin/env python3

"""
This is the 'tcp_datastream_manager' module.

It provides the TCPDatastreamManager class, which is a specialized version of DatastreamManager
that handles receiving data from a TCP socket connection.

The TCPDatastreamManager inherits from the DatastreamManager class and extends its functionality
to handle the reception and processing of datastream messages from a TCP socket connection.
"""
import socket
import time
import select
from rvg_leidarstein_core.datastream_managers.decrypter import decrypter
from rvg_leidarstein_core.datastream_managers.datastream_manager import datastream_manager


class tcp_datastream_manager(datastream_manager):
    def __init__(
        self,
        address,
        buffer_size,
        loop_limit=1,
        verbosity=(False, False, False, False, False),
        log_stream=("datstream_5min.txt", 300, False),
        socket_timeout=5,
        decrypter=decrypter,
        drop_ais_messages=True,
        prefixFilter=[],
        suffixFilter="",
    ):
        """
        TCPDatastreamManager class extends the DatastreamManager class to handle 
        TCP socket connections.

        The TCPDatastreamManager inherits from the DatastreamManager class and
        adds functionality to handle receiving datastream messages from a TCP 
        socket connection.

        Args:
            address (tuple): The address of the TCP server to connect to, in the form of (host, port).
            buffer_size (int): The size of the buffer used to receive data from the socket.
            loop_limit (int): The limit for recursive iteration loops on parsing. Default is 1.
            verbosity (tuple): A tuple of booleans indicating the verbosity of different log levels.
                            Default is (False, False, False, False, False).
            log_stream (tuple): A tuple containing the log file name (str), the time interval (int) in seconds
                                for writing log data, and a boolean flag for enabling log streaming.
                                Default is ("datstream_5min.txt", 300, False).
            socket_timeout (float): The timeout in seconds for socket operations. Default is 5.0 seconds.
            decrypter (class): The Decrypter class or a subclass to handle decryption of messages.
                            Default is decrypter (from datastream_managers.decrypter).
            drop_ais_messages (bool): Whether to drop AIS messages or not. Default is True.
            prefixFilter (list): A list of message prefixes to filter incoming messages. Default is an empty list.
            suffixFilter (str): A suffix filter for messages. Default is an empty string.
        """

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

        # Variables for logging the UDP stream
        self.log_file_name = log_stream[0]
        self._seconds = log_stream[1]
        self._timeout = 0
        self._log_stream = log_stream[2]

        self._address = address
        self._buffer_size = buffer_size

        # This variable sets the limit for recursive iteration loops on parse
        self._loop_limit = loop_limit

        # Variables for console output
        self._raw_verbose = verbosity[0]
        self._tag_verbose = verbosity[1]
        self._unparsed_tag_verbose = verbosity[2]
        self._parsed_message_verbose = verbosity[3]
        self._parse_error_verbose = verbosity[4]

        self._socket_timeout = socket_timeout
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.connect(self._address)

        # Variables for AIS Decoding
        self.talker = ["!AIVDM", "!AIVDO"]
        self.max_id = 10
        self._buffer = [None] * self.max_id

    def start(self):
        """
        Start receiving and processing datastream messages from the TCP socket
        connection.

        This method begins receiving and processing datastream messages from the 
        TCP socket connection specified by the 'address' parameter during 
        initialization.

        If the 'log_stream' parameter was set to True during initialization, the 
        received messages are also logged to the file specified in the 
        'log_file_name' parameter. The logging continues for the duration of the
        'seconds' specified in the 'log_stream' parameter.

        Once the datastream processing or logging duration is complete, 
        the method will stop and return.

        Returns:
            None
        """
        print("TcpDatastreamManager running.")

        self._running = True

        if self._log_stream:
            self._timeout = time.time() + self._seconds
            f = open(self.log_file_name, "a")
            print("Opening save file:", self.log_file_name)

        ready = select.select([self._s], [], [], self._socket_timeout)

        if not ready[0]:
            print("Connection Timed out, closing...")

        while self._running and ready[0]:
            raw_msg = self._s.recv(self._buffer_size)
            lines = raw_msg.decode("ascii").splitlines()
            for line in lines:
                self._parse_message(line.encode("ascii"))

            if self._log_stream:
                f.write(raw_msg.decode(encoding="ascii"))

            if time.time() > self._timeout and self._log_stream:
                f.close()
                break

        if self._log_stream:
            print("writing done, closing file ", self.log_file_name)
            f.close()

        print("TcpDatastreamManager Stopped.")
