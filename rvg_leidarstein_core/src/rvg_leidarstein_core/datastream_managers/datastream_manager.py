import sys
import pynmea2
from pyais import decode as ais_decode
from rvg_leidarstein_core.datastream_managers.decrypter import decrypter


class datastream_manager:
    """
    DatastreamManager class manages incoming data streams and processes messages.

    Args:
        loop_limit (int): The limit for recursive iteration loops on parse. Default is 1.
        verbosity (tuple): A tuple of booleans representing different verbose levels.
                           Default is (False, False, False, False, False).
        log_stream (tuple): A tuple containing log file information. Default is
                            ("datstream_5min.txt", 300, False).
        socket_timeout (int): Timeout value for socket operations. Default is 5.
        decrypter (function): Function used for decryption. Default is the 'decrypter' function.
        drop_ais_messages (bool): If True, incoming AIS messages will be ignored. Default is True.
        prefixFilter (list): List of message prefixes used for filtering. Default is an empty list.
        suffixFilter (str): Message suffix used for filtering. Default is an empty string.
    """

    def __init__(
        self,
        loop_limit=1,
        verbosity=(False, False, False, False, False),
        log_stream=("datstream_5min.txt", 300, False),
        socket_timeout=5,
        decrypter=decrypter,
        drop_ais_messages=True,
        prefixFilter=[],
        suffixFilter="",
    ):
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

        # This variable sets the limit for recursive iteration loops on parse
        self._loop_limit = loop_limit

        # Variables for console output
        self._raw_verbose = verbosity[0]
        self._tag_verbose = verbosity[1]
        self._unparsed_tag_verbose = verbosity[2]
        self._parsed_message_verbose = verbosity[3]
        self._parse_error_verbose = verbosity[4]

        # Variables for AIS Decoding
        self.talker = ["!AIVDM", "!AIVDO"]
        self.max_id = 10
        self._buffer = [None] * self.max_id

    def _is_id_valid(self, msg_id):
        """
        Check if the message ID is valid based on the prefixFilter and suffixFilter.

        Args:
            msg_id (str): The message ID to be checked.

        Returns:
            bool: True if the message ID is valid, otherwise False.
        """
        for filter in self.prefixFilter:
            if msg_id.find(filter) == 0 and msg_id.find(self.suffixFilter) != 0:
                return True
        return False

    def pop_parsed_msg_list(self, index=None):
        """
        Remove and return the last parsed message from the parsed_msg_list.

        Args:
            index (int): Optional index to specify which message to pop. If None,
                         the last message will be removed.

        Returns:
            None
        """
        if len(self.parsed_msg_list) < 1:
            return

        if index is not None:
            self.parsed_msg_list.pop(index)
            return
        else:
            self.parsed_msg_list.pop()
            return

    def stop(self):
        """
        Stop the DatastreamManager from running.

        This method sets the internal '_running' flag to False, which will stop any ongoing
        data processing and message parsing.

        Returns:
            None
        """
        self._running = False
        return

    def _get_tag(self, raw_msg):
        """
        Extract the message tag from a raw message.

        Args:
            raw_msg (bytes): The raw message received from the data stream.

        Returns:
            str: The message tag extracted from the raw message.
                 If the tag cannot be extracted, it returns "unknown".
        """
        tag = "unknown"
        decoded_msg = raw_msg.decode(encoding="ascii")
        decoded_msg = decoded_msg.replace(self.eol_separator, "")

        for begin_identifier in self.msg_begin_identifiers:
            if decoded_msg[0] == begin_identifier:
                tag = decoded_msg.split(",")[0]
        return tag

    def _save_individual_tags(
        self, raw_msg, target_list, target_list_name, parsed_message=None, verbose=False
    ):
        """
        Save individual tags from the raw message to a target list.

        Args:
            raw_msg (bytes): The raw message received from the data stream.
            target_list (list): The list to which the extracted tags will be saved.
            target_list_name (str): The name of the target list for identification purposes.
            parsed_message (object): An optional parsed message object related to the raw_msg.
            verbose (bool): If True, additional information will be printed to the console.

        Returns:
            None
        """
        tag = self._get_tag(raw_msg)

        if target_list.count(tag) == 0:
            target_list.append(tag)
            if verbose:
                print("\r\n tag {} for {} list:".format(tag, target_list_name))
                print("{} \r\n has been added for message:".format(repr(target_list)))
                print(raw_msg)
                if parsed_message is not None:
                    print(
                        "saved parsed message is: {} \r\n".format(repr(parsed_message))
                    )

    def _update_data_object(
        self, parsed_msg, raw_msg, what, verbose=False, metadata=None
    ):
        """
        Update the data object with parsed message and related information.

        Args:
            parsed_msg (object): The parsed message obtained from the raw message.
            raw_msg (bytes): The raw message received from the data stream.
            what (str): Description of the parsed message (e.g., 'GGA', 'VTG', etc.).
            verbose (bool): If True, additional information will be printed to the console.
            metadata (object): An optional metadata object associated with the parsed_msg.

        Returns:
            None
        """
        tag = self._get_tag(raw_msg)

        if not self._is_id_valid(tag):
            return

        if metadata is not None:
            tag = tag + self.extended_msg_suffix
            self.parsed_msg_list.insert(0, (tag, parsed_msg, metadata))
        self.parsed_msg_list_size = sys.getsizeof(self.parsed_msg_list)
        if verbose:
            print(
                "type {}{} Message: {} , metadata: {}\n\n".format(
                    type(parsed_msg), what, repr(parsed_msg), metadata
                )
            )
        return

    def _fix_bad_eol(self, raw_msg):
        """
        Fix badly formatted end-of-line characters in the raw message.

        Args:
            raw_msg (bytes): The raw message received from the data stream.

        Returns:
            list: A list of strings with fixed end-of-line characters.
        """
        parsed_string = raw_msg.decode(encoding="ascii")

        # There's probably a better way to handle the bad double backslash
        for separator in self.bad_eol_separators:
            bad_separator = separator[0]
            good_separator = separator[1]
            while parsed_string.find(bad_separator) != -1:
                parsed_string = parsed_string.replace(bad_separator, good_separator)
        string_list = parsed_string.strip().split(self.eol_separator)
        return string_list

    def _fix_collated_msgs(self, raw_msg):
        """
        Fix collated messages in the raw message.

        Args:
            raw_msg (bytes): The raw message received from the data stream.

        Returns:
            list: A list of strings with fixed collated messages.
        """
        parsed_string = raw_msg.decode(encoding="ascii")
        for begin_identifier in self.msg_begin_identifiers:
            parsed_string = parsed_string.replace(
                begin_identifier, self.eol_separator + begin_identifier
            )

        string_list = parsed_string.strip().split(self.eol_separator)
        return string_list

    def _parse_nmea(self, raw_msg, metadata=None):
        """
        Parse an NMEA message from the raw message and update the data object.

        Args:
            raw_msg (bytes): The raw message received from the data stream.
            metadata (object): An optional metadata object associated with the raw_msg.

        Returns:
            None
        """
        decoded_msg = raw_msg.decode(encoding="ascii")
        parsed_msg = pynmea2.parse(decoded_msg)
        self._update_data_object(
            parsed_msg, raw_msg, "NMEA", self._parsed_message_verbose, metadata=metadata
        )
        self._save_individual_tags(
            raw_msg,
            self.parsed_msg_tags,
            "Succesfully Parsed",
            parsed_msg,
            self._tag_verbose,
        )

    def _assemble_ais(self, raw_msg):
        """
        Assemble an AIS message from the raw message fragments and decode it.

        Args:
            raw_msg (bytes): The raw message received from the data stream.

        Returns:
            object: The decoded AIS message as an object, or an empty string if the
                    message fragments are not complete yet.
        """
        decoded = raw_msg.decode(encoding="ascii")

        # check if receiving only one message
        # assert(len(decoded.split(',')) == self._field_num)

        talker_id, msg_len, msg_seq, msg_id, *content = decoded.split(",")
        if msg_id == "":
            return ais_decode(raw_msg)
        msg_len = int(msg_len)
        msg_seq = int(msg_seq) - 1
        msg_id = int(msg_id)

        # check if talker is correct

        if self._buffer[msg_id] is None:
            self._buffer[msg_id] = [None] * msg_len

        self._buffer[msg_id][msg_seq] = raw_msg

        full_content = ""
        if None in self._buffer[msg_id]:
            return full_content
        else:
            full_content = ais_decode(*self._buffer[msg_id])
            self._buffer[msg_id] = None
            return full_content

    def _parse_ais(self, raw_msg, metadata=None):
        """
        Parse an AIS message from the raw message and update the data object.

        Args:
            raw_msg (bytes): The raw message received from the data stream.
            metadata (object): An optional metadata object associated with the raw_msg.

        Returns:
            None
        """
        decoded = raw_msg.decode(encoding="ascii")

        assert decoded.find(self.talker[0]) == 0 or decoded.find(self.talker[1]) == 0
        if self.drop_ais_messages:
            return
        parsed_msg = self._assemble_ais(raw_msg)
        if parsed_msg == "":
            return
        else:
            self._save_individual_tags(
                raw_msg,
                self.parsed_msg_tags,
                "Succesfully Parsed",
                parsed_msg,
                self._tag_verbose,
            )
            self._update_data_object(
                parsed_msg,
                raw_msg,
                "AIS",
                self._parsed_message_verbose,
                metadata=metadata,
            )

    def _parse_list(self, raw_msg, list_callback, _loop_count):
        """
        Parse a list of messages from the raw message using the specified list_callback.

        Args:
            raw_msg (bytes): The raw message received from the data stream.
            list_callback (function): A callback function that parses the raw_msg
                                      and returns a list of strings containing messages.
            _loop_count (int): The current loop count for recursive iteration.

        Returns:
            int: The updated loop count after parsing the list.
        """
        assert _loop_count < self._loop_limit
        string_list = list_callback(raw_msg)
        assert len(string_list) > 1
        _loop_count += 1
        for entry in string_list:
            entry = entry + self.eol_separator
            entry_bin = entry.encode(encoding="ascii")
            self._parse_message(entry_bin, _loop_count)
        return _loop_count

    def _parse_message(self, raw_msg, _loop_count=0, metadata=None):
        """
        Parse a raw message and attempt to parse it as different message types.

        This method tries to parse the raw message as various message types (NMEA, AIS, etc.),
        and if parsing fails, it may attempt to decrypt the message or parse it as a list
        of messages. The method makes multiple attempts to parse the message until it is
        successfully processed or determined to be invalid.

        Args:
            raw_msg (bytes): The raw message received from the data stream.
            _loop_count (int): The current loop count for recursive iteration. Default is 0.
            metadata (object): An optional metadata object associated with the raw_msg.

        Returns:
            None
        """
        if self._raw_verbose:
            print(raw_msg.decode("ascii"), "\n\n")
        try:
            self._parse_nmea(raw_msg, metadata)
        except:
            try:
                self._parse_ais(raw_msg, metadata)
            except:
                try:
                    full_message = self._decrypter.decrypt(raw_msg)
                    if full_message != "":
                        metadata, msg = full_message
                        self._parse_message(msg.encode("ascii"), metadata=metadata)
                except:
                    try:
                        _loop_count = self._parse_list(
                            raw_msg, self._fix_bad_eol, _loop_count
                        )
                    except:
                        try:
                            _loop_count = self._parse_list(
                                raw_msg, self._fix_collated_msgs, _loop_count
                            )
                        except:
                            try:
                                self._save_individual_tags(
                                    raw_msg,
                                    self.unknown_msg_tags,
                                    "Parse Failed",
                                    verbose=self._unparsed_tag_verbose,
                                )
                                if self._parse_error_verbose:
                                    print("Unable to parse message: {}".format(raw_msg))
                            except:
                                if self._parse_error_verbose:
                                    print(
                                        "Unable to parse or save message tag: {}".format(
                                            raw_msg
                                        )
                                    )

    def start(self):
        """
        Start the DatastreamManager.

        This method simply prints a message indicating that the DatastreamManager
        has started.

        Returns:
            None
        """
        print("DatastreamManager Start.")
