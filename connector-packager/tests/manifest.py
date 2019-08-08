"""
Module for JAR manifest.
"""

import os

from collections import OrderedDict
from six import BytesIO
from connector_packager.version import __version__


MANIFEST_LINE_LENGTH = 70
MANIFEST_VERSION = "Manifest-Version"
VENDOR_KEY = "Created-By"
PACKAGING_TOOL_NAME = "Tableau Connector Packaging Tool "


class ManifestKeyException(Exception):

    pass


class ManifestSection:

    def __init__(self, name, value):
        self.dict = OrderedDict([])
        self.dict[name] = value

    def store(self, stream, linesep=os.linesep):

        for k, v in self.dict.items():
            write_key_val(stream, k, v, linesep)

    def get_data(self, linesep=os.linesep):

        stream = BytesIO()
        self.store(stream, linesep)
        return stream.getvalue()

    def clear(self):
        self.dict.clear()


class Manifest:
    """
    Represents a Java Manifest as an ordered dictionary containing
    the key:value pairs from the main section of the manifest, and
    zero or more sub-dictionaries of key:value pairs representing the
    sections following the main section.
    """

    def __init__(self, version="1.0", linesep=None):
        self.sections = []
        self.sections.append(ManifestSection(MANIFEST_VERSION, version))
        self.sections.append(ManifestSection(VENDOR_KEY, PACKAGING_TOOL_NAME + __version__))
        self.linesep = linesep

    def store(self, stream, linesep=None):
        """
        Serialize the Manifest to a binary stream
        """

        linesep = linesep or self.linesep or os.linesep

        for sect in self.sections:
            sect.store(stream, linesep)

        stream.write(linesep.encode('utf-8'))

    def get_data(self, linesep=None) -> bytes:
        """
        Serialize the entire manifest and return it as bytes
        :return bytes
        """

        # either specified here, specified on the instance, or the OS default
        linesep = linesep or self.linesep or os.linesep

        stream = BytesIO()
        self.store(stream, linesep)
        return stream.getvalue()

    def clear(self):
        """
        removes all items from this manifest, and clears and removes all
        sub-sections
        """
        self.sections.clear()

    def __del__(self):
        self.clear()


def write_key_val(stream, key: str, val: str, linesep=os.linesep):
    """
    The MANIFEST specification limits the width of individual lines to
    72 bytes (including the terminating newlines). Any key and value
    pair that would be longer must be split up over multiple
    continuing lines
    :type key, val: str in Py3, str or unicode in Py2
    :type stream: binary
    """

    key = key.encode('utf-8') or ""
    val = val.encode('utf-8') or ""
    linesep = linesep.encode('utf-8')

    # check key's length
    if not (0 < len(key) < MANIFEST_LINE_LENGTH - 1):
        raise ManifestKeyException("bad key length", key)

    if len(key) + len(val) > MANIFEST_LINE_LENGTH - 2:
        kv_buffer = BytesIO(b": ".join((key, val)))

        # first grab 70 (which is 72 after the trailing newline)
        stream.write(kv_buffer.read(MANIFEST_LINE_LENGTH))

        # now only 69 at a time, because we need a leading space and a
        # trailing \n
        part = kv_buffer.read(MANIFEST_LINE_LENGTH - 1)
        while part:
            stream.write(linesep + b" ")
            stream.write(part)
            part = kv_buffer.read(MANIFEST_LINE_LENGTH - 1)
        kv_buffer.close()

    else:
        stream.write(key)
        stream.write(b": ")
        stream.write(val)

    stream.write(linesep)
