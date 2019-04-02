"""
Module for JAR manifest.
"""

import os

from collections import OrderedDict
from six import BytesIO


class ManifestKeyException(Exception):

    pass


class ManifestSection(OrderedDict):

    primary_key = "Name"

    def __init__(self, name=None):
        OrderedDict.__init__(self)
        self[self.primary_key] = name

    def store(self, stream, linesep=os.linesep):
        """
        Serialize this section and write it to a binary stream
        """

        for k, v in self.items():
            write_key_val(stream, k, v, linesep)

        stream.write(linesep.encode('utf-8'))

    def get_data(self, linesep=os.linesep):
        """
        Serialize the section and return it as bytes
        :return bytes
        """

        stream = BytesIO()
        self.store(stream, linesep)
        return stream.getvalue()


class Manifest(ManifestSection):
    """
    Represents a Java Manifest as an ordered dictionary containing
    the key:value pairs from the main section of the manifest, and
    zero or more sub-dictionaries of key:value pairs representing the
    sections following the main section. The sections are referenced
    by the value of their 'Name' pair, which must be unique to the
    Manifest as a whole.
    """

    primary_key = "Manifest-Version"

    def __init__(self, version="1.0", linesep=None):
        # can't use super, because we're a child of a non-object
        ManifestSection.__init__(self, version)
        self.sub_sections = OrderedDict([])
        self.linesep = linesep

    def store(self, stream, linesep=None):
        """
        Serialize the Manifest to a binary stream
        """

        # either specified here, specified on the instance, or the OS
        # default
        linesep = linesep or self.linesep or os.linesep

        ManifestSection.store(self, stream, linesep)
        for sect in sorted(self.sub_sections.values()):
            sect.store(stream, linesep)

    def get_data(self, linesep=None):
        """
        Serialize the entire manifest and return it as bytes
        :return bytes
        """

        linesep = linesep or self.linesep or os.linesep

        stream = BytesIO()
        self.store(stream, linesep)
        return stream.getvalue()

    def clear(self):
        """
        removes all items from this manifest, and clears and removes all
        sub-sections
        """

        for sub in self.sub_sections.values():
            sub.clear()
        self.sub_sections.clear()

        ManifestSection.clear(self)

    def __del__(self):
        self.clear()


def write_key_val(stream, key, val, linesep=os.linesep):
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

    if not (0 < len(key) < 69):
        raise ManifestKeyException("bad key length", key)

    if len(key) + len(val) > 68:
        kvbuffer = BytesIO(b": ".join((key, val)))

        # first grab 70 (which is 72 after the trailing newline)
        stream.write(kvbuffer.read(70))

        # now only 69 at a time, because we need a leading space and a
        # trailing \n
        part = kvbuffer.read(69)
        while part:
            stream.write(linesep + b" ")
            stream.write(part)
            part = kvbuffer.read(69)
        kvbuffer.close()

    else:
        stream.write(key)
        stream.write(b": ")
        stream.write(val)

    stream.write(linesep)

#
# The end.
