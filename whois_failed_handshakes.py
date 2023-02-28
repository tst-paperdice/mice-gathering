"""
Use example:
python3 whois.py docker-logs.txt whois.txt
"""

import sys
import subprocess
import re

IP_RE = re.compile("\d+\.\d+\.\d+\.\d+")


def lookup_failed_handshake(line):
    ip = IP_RE.search(line).group()
    whois_output = subprocess.check_output(f"whois {ip}", shell=True).decode()
    return whois_output


def is_failed_handshake_line(line):
    return "handshake with" in line


if __name__ == "__main__":
    input_fn = sys.argv[1]
    with open(input_fn, "r") as ifd:
        for line in ifd.readlines():
            if is_failed_handshake_line(line):
                print(lookup_failed_handshake(line))
