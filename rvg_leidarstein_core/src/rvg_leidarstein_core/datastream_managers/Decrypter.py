#!/usr/bin/env python3

""" 
Handles the decryption of messages using RSA encryption.

The Decrypter class takes an RSA public key, and it can decrypt messages that are encrypted
using the corresponding private key. It supports assembling fragmented messages and decoding them
into their original form.
"""
from Crypto.PublicKey import RSA
from base64 import b64decode
import os
import re


class decrypter:
    """
    Decrypter class handles the decryption of messages using RSA encryption.

    Args:
        key_path (str): The file path to the RSA public key. (Currently unused)
        talker (str): The talker ID of the encrypted messages. Default is "!U9SEC".
        field_num (int): The number of fields in the encrypted message. Default is 5.
        max_id (int): The maximum message ID allowed for assembling fragments. Default is 10.
    """

    def __init__(self, key_path, talker="!U9SEC", field_num=5, max_id=10):
        self.talker = talker
        self.key_path = key_path  # this will go unused until further revision
        self._key_string = """-----BEGIN RSA PUBLIC KEY-----
MIGJAoGBAPBiv6NqkzAIVEEmhJM45ZeGQclj4bsOgL49j++lm3GlmjilBvxw47Lv
KJ2cxMzyfaT2/f1H8Q6ObOCebmc0SeKeAzkdJj2Qw2ydBYG6xz747mQOD0al0THo
e5lCfv/EFRhnka1IlNBFrMrA/LKYsDVy019nGcfoQrv40Eao3XK/AgMBAAE=
-----END RSA PUBLIC KEY-----"""  # temporary solution

        self._buffer = [None] * max_id
        self._keyring = {}
        self._field_num = field_num

    def _assemble(self, raw_msg):
        """
        Assemble a fragmented message from the raw message.

        Args:
            raw_msg (bytes): The raw message received from the data stream.

        Returns:
            str: The assembled message content as a string.
        """
        decoded = raw_msg.decode(encoding="ascii")

        # check if receiving only one message
        assert len(decoded.split(",")) == self._field_num

        talker_id, msg_len, msg_seq, msg_id, content = decoded.split(",")
        msg_len = int(msg_len)
        msg_seq = int(msg_seq) - 1
        msg_id = int(msg_id)

        # check if talker is correct
        assert talker_id.count(self.talker)

        if self._buffer[msg_id] is None:
            self._buffer[msg_id] = [None] * msg_len

        self._buffer[msg_id][msg_seq] = content.strip()

        full_content = ""
        if None in self._buffer[msg_id]:
            return full_content
        else:
            full_content = full_content.join(self._buffer[msg_id])
            self._buffer[msg_id] = None
            return full_content

    def _get_key_cypher(self, full_content):
        """
        Extract the RSA public key and the encrypted content from the full content.

        The full content should be in the format: "key_name;cypher_text".

        Args:
            full_content (str): The full content of the encrypted message.

        Returns:
            tuple: A tuple containing the RSA public key (as an RSA key object) and
                   the encrypted content (as bytes).
        """
        seq = full_content.split(";")
        key_name, content = seq[0], seq[1:]

        key_name = key_name.strip() + ".key.pub"
        # use regex
        key_name = key_name.replace("/", "_").replace(" ", "_")

        if len(content) > 1:
            content = "".join(content)

        cypher = content[0].encode("ascii")

        if key_name in self._keyring:
            key = self._keyring[key_name]
        else:
            # fix this when the key issue is sorted out
            # key_path = os.path.join(self.key_path, key_name)
            # key_string = open(key_path, "r").read()

            key = RSA.importKey(self._key_string)
            self._keyring[key_name] = key

        return key, cypher

    def _clean_message(self, decrypted):
        """
        Clean up the decrypted message, extract metadata, and return the metadata 
        and the message.

        Args:
            decrypted (bytes): The decrypted message as bytes.

        Returns:
            tuple: A tuple containing the metadata (unix_time, seq_num, src_id, src_name) 
            as a tuple and the cleaned message content (as a string or bytes, depending on the message format).
        """
        decrypted = decrypted.decode("ascii", "backslashreplace")
        decrypted = re.sub(r"([\\][x][a-z0-9]{2})+", "", decrypted)
        decrypted = decrypted[1:]
        seq = decrypted.split(";")
        metadata_str, msg = seq[0], seq[1:]
        if len(msg) > 1:
            msg = "".join(msg)
        unix_time, seq_num, src_id, src_name = metadata_str.split(",")

        metadata = (
            float(unix_time[1:]),  # bit is appended to string somehow
            int(seq_num),
            int(src_id),
            src_name,
        )

        if type(msg) is list:
            msg = msg[0]

        return metadata, msg

    def decrypt(self, raw_msg):
        """
        Decrypt and clean up the raw message.

        Args:
            raw_msg (bytes): The raw message received from the data stream.

        Returns:
            tuple: A tuple containing the metadata (unix_time, seq_num, src_id, src_name)
            as a tuple and the cleaned message content (as a string or bytes,
            depending on the message format).
            If the decryption fails or the message is incomplete, an empty 
            string is returned.
        """
        full_content = self._assemble(raw_msg)
        if full_content == "":
            return ""

        key, cypher = self._get_key_cypher(full_content)
        raw_cipher_data = b64decode(cypher)
        decrypted = key.encrypt(raw_cipher_data, 0)
        clean = self._clean_message(decrypted[0])
        return clean
