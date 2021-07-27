from __future__ import annotations

import logging

import six


def truncate(value, n):
    value = six.ensure_text(value)
    return value if len(value) <= n - 3 else f"{value[: n - 3]}..."


def color(level):
    if level == logging.ERROR:
        return red
    elif level == logging.WARNING:
        return yellow
    elif level == logging.DEBUG:
        return green
    else:
        return lambda x: x


def red(o):
    return f"\033[91m{o}\033[0m"


def green(o):
    return f"\033[92m{o}\033[0m"


def yellow(o):
    return f"\033[93m{o}\033[0m"


def blue(o):
    return f"\033[94m{o}\033[0m"
