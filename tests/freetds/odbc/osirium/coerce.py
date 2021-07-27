"""
coerce strings to various other types (ints, dates, gzips etc) in a more error
tolerant and permissive way than Python built-ins
"""

from __future__ import annotations

import datetime
import io
import random
import re
import struct

import six

random = random.SystemRandom()


class int32str:
    """Utility class for converting individual strings into netstrings."""

    Format = struct.Struct("<I")
    MAX_LENGTH = 1024 * 1024 * 1024

    def read(self, stream):
        length = stream.read(int32str.Format.size)
        if not length:
            return None
        (length,) = int32str.Format.unpack(length)
        assert int32str.MAX_LENGTH > length > 0
        data = stream.read(length)
        assert len(data) == length
        return data

    def unpack(self, value):
        (length,) = int32str.Format.unpack(value[: int32str.Format.size])
        assert int32str.MAX_LENGTH > length > 0
        data = value[int32str.Format.size : int32str.Format.size + length]
        assert len(data) == length
        return data

    def write(self, stream, value):
        stream.write(self.pack(value))

    def pack(self, value):
        value = six.ensure_binary(value)
        length = len(value)
        assert int32str.MAX_LENGTH > length > 0
        return int32str.Format.pack(length) + value


int32str = int32str()


class int32strs:
    """Utility class for converting lists of strings into single strings."""

    def unpack(self, values):
        buffer = io.BytesIO(values)
        while True:
            length = buffer.read(int32str.Format.size)
            if not length:
                return
            (length,) = int32str.Format.unpack(length)
            # assert (1024 * 1024) > length > 0
            data = buffer.read(length)
            assert len(data) == length
            yield data

    def pack(self, values):
        """Converts a list of strings into one string consisting of a series
        of netstrings, end to end.

        For example, ['ham', 'eggs'] becomes
        '\\x03\\x00\\x00\\x00ham\\x04\\x00\\x00\\x00eggs'.

        Note that the resulting string is not a netstring. It is simply a
        concatenation of a series of netstrings, and must be treated
        appropriately on the other side of the connection.
        """
        return b"".join([int32str.pack(value) for value in values])


int32strs = int32strs()


def first(values, default=None):
    return next(iter(values), default)


def splat(*args):
    return args


def from_pattern(pattern, type, *args):
    def coerce(value):
        decoded = six.ensure_str(value) if isinstance(value, bytes) else str(value)
        match = pattern.search(decoded)
        if match is not None:
            return type(match.group(1), *args)
        raise ValueError(f"unable to coerce {decoded!r} into a {type.__name__}")

    return coerce


to_int = from_pattern(re.compile("([-+]?[0-9]+)", re.IGNORECASE), int)

ESCAPE = re.compile(r'[\x00-\x1f\\"\b\f\n\r\t]')
SUBSTITUTIONS = {
    "\\": "\\\\",
    '"': '\\"',
    "\b": "\\b",
    "\f": "\\f",
    "\n": "\\n",
    "\r": "\\r",
    "\t": "\\t",
}


def from_isodate(value):
    return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")


def to_isodate(value):
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


for i in range(0x20):
    SUBSTITUTIONS.setdefault(chr(i), f"\\u{i:04x}")


def quote(s):
    def replace(match):
        return SUBSTITUTIONS[match.group(0)]

    return '"' + ESCAPE.sub(replace, str(s)) + '"'


def to_bool(value):
    value = value.decode("utf8") if isinstance(value, bytes) else str(value)
    if re.match("^(true)$", value, re.IGNORECASE):
        return True
    if re.match("^(false)$", value, re.IGNORECASE):
        return False
    raise ValueError("unable to coerce %r into a boolean", value)


# FIXME: yes. We actually have two functions that are named the same but do
# different things!
def to_bool_2(val):
    """Convert a passed value to a boolean The val passed could lready be
    boolean, or a string a numeric or an arbitrary object of None (False)
    """
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower() in ("yes", "true", "1", "t")
    if isinstance(val, int):
        return val != 0
    if val:
        return True
    return False


def as_list(o):
    return [o] if not isinstance(o, list) else o
