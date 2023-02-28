"""
Use example:
python3 base64_client_logs.py test_1668206406.log fixed-test_1668206406.log
"""

import sys
import base64


def decode(line):
    try:
        prefix, b64_str = line.split("base64 encoded stack trace: b'")
        b64_str = b64_str[:-1]
        return f"{prefix}{base64.b64decode(b64_str)}\n"
    except ValueError:
        return line


if __name__ == "__main__":
    input_fn = sys.argv[1]
    output_fn = sys.argv[2]
    with open(output_fn, "w") as ofd:
        with open(input_fn, "r") as ifd:
            for line in ifd.readlines():
                ofd.write(decode(line))
