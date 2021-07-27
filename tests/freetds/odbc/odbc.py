"""
console application for sending commands to odbc applications
"""

from __future__ import annotations

import argparse
import binascii
import csv
import datetime
import getpass
import json
import re
import readline
import signal
import sys
from contextlib import closing

import pyodbc
import setproctitle
import six

from osirium import coerce
from osirium.support import output

assert readline


class Column:
    def __init__(
        self, name, type_code, display_size, internal_size, precision, scale, null_ok
    ):
        self.name = name
        self.type_code = type_code
        self.display_size = display_size
        self.internal_size = (internal_size,)
        self.precision = precision
        self.scale = scale
        self.null_ok = null_ok

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{self.name}({self.type_code})"


def fetchmany(cursor):
    while True:
        rows = cursor.fetchmany(100)
        if not rows:
            break
        yield from rows


class ByteArrayEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, bytearray):
            return "0x" + binascii.b2a_hex(memoryview(o))
        if isinstance(o, datetime.datetime):
            return coerce.to_isodate(o)
        return json.JSONEncoder.default(self, o)


def format(o):
    if isinstance(o, bytearray):
        return "0x" + six.ensure_str(binascii.b2a_hex(memoryview(o)))
    if isinstance(o, datetime.datetime):
        return coerce.to_isodate(o)
    return str(o)


def main():
    # ignore CTRL+C
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    try:
        parser = argparse.ArgumentParser(description="ODBC command line tool")

        def credentials(string):
            try:
                return (
                    re.compile("^(?P<uid>.*?)@(?P<server>.*)$")
                    .match(string)
                    .groupdict()
                )
            except Exception as e:
                print(str(e))
                raise argparse.ArgumentTypeError("invalid credentials")

        parser.add_argument(
            "credentials", metavar="<username>@<host>", type=credentials
        )
        parser.add_argument("--database", metavar="database")
        parser.add_argument("--instance", metavar="instance")
        parser.add_argument("--port", metavar="port", type=int)
        parser.add_argument("--driver", default="mssql", metavar="driver")
        parser.add_argument("--password", default=None, metavar="password")
        parser.add_argument("--tds_version", default="8.0", metavar="tds_version")

        args = parser.parse_args()

        kwargs = {key: value for key, value in args._get_kwargs() if value}
        kwargs.update(kwargs.pop("credentials"))

        setproctitle.setproctitle(
            "osirium: odbc [{}@{}]".format(kwargs["uid"], kwargs["server"])
        )

        kwargs["password"] = kwargs.get("password") or getpass.getpass("Password: ")

        with closing(pyodbc.connect(**kwargs)) as connection:
            while True:
                query = input(f"{args.driver}> ")
                if query == "exit":
                    break
                if query.startswith("autocommit"):
                    matchdata = re.match("^autocommit(?: (on|off))?$", query)
                    if not matchdata:
                        print(
                            output.red("Invalid syntax. Try: autocommit (on|off)"),
                            file=sys.stderr,
                        )
                    else:
                        if matchdata.group(1):
                            connection.autocommit = matchdata.group(1) == "on"
                        print("autocommit", "on" if connection.autocommit else "off")
                    continue
                try:
                    with closing(connection.execute(query)) as cursor:
                        while True:
                            if cursor.description:
                                out = csv.writer(sys.stdout)
                                out.writerow(
                                    [Column(*column) for column in cursor.description]
                                )
                                for row in fetchmany(cursor):
                                    out.writerow([format(v) for v in row])
                            if not cursor.nextset():
                                break
                except pyodbc.ProgrammingError as e:
                    print(e.args[-1], file=sys.stderr)
                except pyodbc.Error as e:
                    print(e.args[-1], file=sys.stderr)
    except pyodbc.Error as e:
        code = e.args[0]
        message = e.args[1]
        if code == "08S01":
            print(
                "Unable to connect: Adaptive Server is unavailable or does not exist. Please check host and port.",
                file=sys.stderr,
            )
        elif code == "08001":
            print(
                "Unable to connect to data source. Please check connection details.",
                file=sys.stderr,
            )
        else:
            print(message, file=sys.stderr)
    except Exception as e:
        print(str(e), file=sys.stderr)


if __name__ == "__main__":
    main()
