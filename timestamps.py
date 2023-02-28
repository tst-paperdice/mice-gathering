"""
Use example:
python3 timestamps.py docker-logs.txt fixed-docker-logs.txt
"""

import sys
import datetime


def convert_line(line):
    try:
        date = datetime.datetime.strptime(f"UTC {line[1:20]}", "%Z %Y-%m-%d %H:%M:%S")
        return f" {date.timestamp()}{line[20:]}"
    except ValueError as e:
        return line


if __name__ == "__main__":
    input_fn = sys.argv[1]
    output_fn = sys.argv[2]
    with open(output_fn, "w") as ofd:
        with open(input_fn, "r") as ifd:
            for line in ifd.readlines():
                ofd.write(convert_line(line))
