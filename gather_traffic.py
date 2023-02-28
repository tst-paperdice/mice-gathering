#!/usr/bin/env python3
import argparse
from base64 import b64encode
import json
import os
from pathlib import Path
from shutil import which
import signal
from stem import process as stem_process
import subprocess
import tempfile
import time
import traceback
import typing
from typing import Optional

import pandas as pd
from selenium import webdriver

BLANK_URL = "about:blank"
# TODO: rust
SHADOWSOCKS_CLIENT_TYPES = ["libev", "go"]


class Logger:
    def __init__(self, log_path: Path):
        self.log_file = log_path.open("w")
        self.first_line = True

    def log(self, event: str, url: Optional[str], comment: Optional[str]):
        """
        Logs an event to the log file

        Parameters
        event -- a compact name for what happened. snake_case is sort of expected but not enforced.
        url -- Optional. Relevant url to the event.
        comment -- Optional. Additional user-defined information.
        """
        # not every logged event has an url or comment so replace
        # None with empty string
        if url is None:
            url = ""
        if comment is None:
            comment = ""
        # We want to write a well-formed csv, so make sure fields
        # with a comma are wrapped
        if "," in event:
            event = f'"{event}"'
        if "," in url:
            url = f'"{url}"'
        if "," in comment:
            comment = f'"{comment}"'
        # Log the current time
        cur_time = time.time_ns()
        # Write newline if we're not on the first line
        if not self.first_line:
            self.log_file.write("\n")
        else:
            self.first_line = False
        # Write a log entry
        self.log_file.write(f"{cur_time},{event},{url},{comment}")
        # Flush (not because i'm concerned about it writing,
        # but because I'd like to use it to monitor progress)
        self.log_file.flush()

    def __del__(self):
        # perhaps not necessary but i am paranoid
        self.log_file.flush()
        self.log_file.close()
        self.log_file.__del__()
        self.log_file = None


class Shadowsocks:
    def __init__(
        self,
        client_type: str,
        host: str,
        port: int,
        password: str,
        method: str,
        local_port: int,
        fast_open: Optional[bool] = None,
    ):
        # Acceptable client types
        # Check parameters
        if client_type not in SHADOWSOCKS_CLIENT_TYPES:
            raise Exception(f"{client_type} is not a valid shadowsocks client type")
        # Store parameters
        self.host = host
        self.port = port
        self.password = password
        self.method = method
        self.local_port = local_port
        self.client_type = client_type
        self.fast_open = fast_open
        # Store variable for the process
        self.shadowsocks_process = None
        # Config file reference. used for the libev client
        self.config_file = None
        # Log file. used so that we don't have to worry about memory and
        # Buffering issues in subprocess.PIPE
        self.log_file = None

    def start(self):
        # Sanity check
        if self.shadowsocks_process is not None:
            # Note, this will leave a zombie process. that's not good...
            # Should do cleanup
            raise Exception("Shadowsocks process already exists")
        # We want to do different things for different clients
        if self.client_type not in SHADOWSOCKS_CLIENT_TYPES:
            raise Exception(f"{client_type} is not a valid shadowsocks client type")
        if self.client_type == "libev":
            return self.start_libev()
        elif self.client_type == "go":
            return self.start_go()
        else:
            raise Exception("Unimplemented client type")

    def start_libev(self):
        # First, we want to construct a dict containing all our parameters
        # That will be converted to JSON
        config = dict(
            server=self.host,
            server_port=self.port,
            password=self.password,
            method=self.method,
            # TODO: should this be an option? i don't think so
            local_address="127.0.0.1",
            local_port=self.local_port,
        )
        if self.fast_open is None:
            config["fast_open"] = True
        else:
            config["fast_open"] = self.fast_open
        # Create a private temporary file for our config file
        # delete=False means it will not be deleted on .close()
        self.config_file = tempfile.NamedTemporaryFile(mode="w", delete=False)
        # Write the config to the file as json
        json.dump(config, self.config_file)
        # Close the file, also flushing it
        # We keep a reference to it though
        self.config_file.close()
        # Create a log file, similarly to how we create the config file
        # We want to get the first 3 lines of stdout because after which
        # We know that the server has been started. However, if a bunch of lines
        # get printed to a PIPE buffer, the process will freeze
        # until the output is consumed. So, we pipe it to a file
        # The problem is whether shadowsocks sufficiently buffers its output
        # Let us hope we don't run into that
        # We set the file to use buffering just in case
        self.log_file = tempfile.NamedTemporaryFile(mode="w", buffering=1, delete=False)
        # Start the shadowsocks process
        self.shadowsocks_process = subprocess.Popen(
            ["ss-local", "-c", self.config_file.name],
            stdout=self.log_file,
            stderr=subprocess.DEVNULL,
            universal_newlines=True,
        )
        # Read lines from the log file, but with a new handle
        # As of 3.3.5, it prints 2 lines on startup + 1 if tcp fast open is enabled
        lines = []
        with Path(self.log_file.name).open("r") as log_file:
            for _ in range(3 if config["fast_open"] else 2):
                line = log_file.readline()
                lines.append(line)
        # If this succeeds, we've started the shadowsocks process
        # Return the lines
        return lines

    def start_go(self):
        # go-shadowsocks2 uses a server string instead of a config file
        # Construct that
        server_string = f"ss://{self.method}:{self.password}@{self.host}:{self.port}"
        # Create a log file
        # We want to get the first line of stdout because after which
        # We know that the server has been started. However, if a bunch of lines
        # get printed to a PIPE buffer, the process will freeze
        # until the output is consumed. So, we pipe it to a file
        # The problem is whether shadowsocks sufficiently buffers its output
        # Let us hope we don't run into that
        # We set the file to use buffering just in case
        self.log_file = tempfile.NamedTemporaryFile(mode="w", buffering=1, delete=False)
        # Start the process
        self.shadowsocks_process = subprocess.Popen(
            [
                "go-shadowsocks2",
                "-c",
                server_string,
                "-socks",
                f":{self.local_port}",
                # verbose will print a message when the server starts.
                # It will also print a lot more messages
                # Hopefully printing to a file handles this
                "-verbose",
            ],
            stdout=subprocess.DEVNULL,
            stderr=self.log_file,
        )
        # Read 1 line from the log file, but with a new handle
        line = None
        with Path(self.log_file.name).open("r") as log_file:
            line = log_file.readline()
        # Return the line
        return [line]

    def stop(self):
        # Sanity check
        if self.shadowsocks_process is None:
            raise Exception(
                "Cannot stop shadowsocks process because we have no reference to one. Maybe it was already stopped?"
            )
        # We want to do different things for different clients
        result = None
        if self.client_type not in SHADOWSOCKS_CLIENT_TYPES:
            raise Exception(f"{client_type} is not a valid shadowsocks client type")
        if self.client_type == "libev":
            status = self.stop_libev()
        elif self.client_type == "go":
            status = self.stop_go()
        else:
            raise Exception("Unimplemented client type")
        # Delete the log file
        if self.log_file is None:
            raise Exception(
                "There should be a log file, but we don't have a reference to it"
            )
        os.remove(self.log_file.name)
        self.log_file = None
        # Return status from function
        return status

    def stop_libev(self):
        # Stop the process
        self.shadowsocks_process.send_signal(signal.SIGINT)
        # Wait for the process to die
        status = self.shadowsocks_process.wait()
        # Delete the config file
        if self.config_file is None:
            raise Exception(
                "There should be a config file, but we don't have a reference to it"
            )
        os.remove(self.config_file.name)
        self.config_file = None
        # Return the status code
        return status

    def stop_go(self):
        # Stop the process
        self.shadowsocks_process.send_signal(signal.SIGINT)
        # Wait for the process to die
        status = self.shadowsocks_process.wait()
        # Return the status code
        return status


def main(
    website_ranking_path: Path,
    num_websites: int,
    pcap_directory: Path,
    experiment_suffix: str,
    shadowsocks_client_type: Optional[str],
    shadowsocks_host: Optional[str],
    shadowsocks_port: Optional[int],
    shadowsocks_password: Optional[str],
    shadowsocks_method: Optional[str],
    shadowsocks_local_port: Optional[int],
    shadowsocks_fast_open: Optional[bool],
    tor: bool,
):
    # Read in the websites
    websites = pd.read_csv(
        website_ranking_path, names=["rank", "host"], dtype=dict(rank=int, host=str)
    )
    # Don't make assumptions about the order of the csv so we
    # sort it and take the `num_websites` top entries
    # Also, after that we no longer need the rank so filter to host
    websites = websites.nsmallest(num_websites, "rank").host
    # Store a time
    cur_time = int(time.time())
    # Create a logger path
    log_path = pcap_directory / f"{cur_time}_{experiment_suffix}.log"
    print(f"Saving logs to {log_path}")
    # Start the logger
    logger = Logger(log_path)
    # Create a store for chrome options
    chrome_options = webdriver.ChromeOptions()
    # notifications will cause the webdriver to freeze up. screw you kontan.co.id
    chrome_options.add_argument("--disable-notifications")
    # Tor and shadowsocks mutually exclusive
    if shadowsocks_client_type is not None and tor:
        raise Exception("Tor and shadowsocks are mutually exclusive")
    # Create a shadowsocks or tor handler (if relevant)
    shadowsocks = None
    tor_process = None
    if shadowsocks_client_type is not None:
        # Create the controller
        shadowsocks = Shadowsocks(
            client_type=shadowsocks_client_type,
            host=shadowsocks_host,
            port=shadowsocks_port,
            password=shadowsocks_password,
            method=shadowsocks_method,
            local_port=shadowsocks_local_port,
            fast_open=shadowsocks_fast_open,
        )
        # Start shadowsocks
        # TODO: also log config options in the comment
        logger.log("shadowsocks_start_begin", None, None)
        shadowsocks.start()
        logger.log("shadowsocks_start_end", None, None)
        # Put in chrome settings to use the proxy
        chrome_options.add_argument(
            f"--proxy-server=socks5://127.0.0.1:{shadowsocks_local_port}"
        )
        # Disable local dns resolution
        # chrome_options.add_argument("--host-resolver-rules=\"MAP * ~NOTFOUND , EXCLUDE localhost\"")
    elif tor:
        # Get path to obfs4proxy
        obfs4proxy_path = which("obfs4proxy")
        snowflake_client_path = which("client")
        snowflake_url = (
            "https://snowflake-broker.torproject.net.global.prod.fastly.net/"
        )
        snowflake_front = "cdn.sstatic.net"
        snowflake_ice = "stun:stun.l.google.com:19302,stun:stun.voip.blackberry.com:3478,stun:stun.altar.com.pl:3478,stun:stun.antisip.com:3478,stun:stun.bluesip.net:3478,stun:stun.dus.net:3478,stun:stun.epygi.com:3478,stun:stun.sonetel.com:3478,stun:stun.sonetel.net:3478,stun:stun.stunprotocol.org:3478,stun:stun.uls.co.za:3478,stun:stun.voipgate.com:3478,stun:stun.voys.nl:3478"
        # Set up config for tor
        bridges = [
            # "obfs4 200.137.221.188:43079 935531384E5977836D92A216067CE4611C930AE5 cert=eR7ymcKHJgwuqmMEY/VlwQJZ45hSU3PjNP47bHsYHweIY4lVBUDBnRlNC+wkyqYUHTj3EQ iat-mode=0",
            # "obfs4 185.224.139.190:6969 ECE44BF4A36AD8D54C43F9E2EC4868C17574C0D0 cert=8ufdqMpcttozHT57Q/0YCioM9ccl2WQ0ra/dKa73QtskBMgnM8vbRjuaSc4sWGN38rWQag iat-mode=0",
            # "obfs4 104.154.53.116:8080 D602B5BA662696701E337DAF91932E8FA656A049 cert=jFdkLcU2HndAapOp2AV6pLqcs2oZqhNq1u6JJ4fEe28LAS64q36CF/1zV3/8dbo8lgF0Lg iat-mode=0"
            "snowflake 0.0.3.0:1 2B280B23E1107BB62ABFC40DDCC8824814F80A72"
        ]
        tor_config = dict(
            UseBridges="1",
            # ClientTransportPlugin=f"obfs4 exec {obfs4proxy_path}",
            ClientTransportPlugin=f"snowflake exec {snowflake_client_path} -url {snowflake_url} -front {snowflake_front} -ice {snowflake_ice}",
            Bridge=bridges,
            Log=["NOTICE file tor.log"],
        )
        logger.log("tor_start_begin", None, None)
        tor_process = stem_process.launch_tor_with_config(
            config=tor_config, take_ownership=True
        )
        logger.log("tor_start_finish", None, None)
        # Put in chrome settings to use the proxy
        chrome_options.add_argument("--proxy-server=socks5://127.0.0.1:9050")
    # Chrome requires an x display
    if "DISPLAY" not in os.environ:
        os.environ["DISPLAY"] = ":0"
    # Start a selenium chrome driver
    # TODO: custom profile config to trim it down a bit
    logger.log("driver_start_begin", None, None)
    driver = webdriver.Chrome(options=chrome_options)
    logger.log("driver_start_end", None, None)

    # Kill tor
    if tor:
        logger.log("tor_stop_begin", None, None)
        tor_process.send_signal(signal.SIGINT)
        tor_process.wait()
        logger.log("tor_stop_end", None, None)
    # Iterate over websites
    for n, host in enumerate(websites):
        if tor:
            logger.log("tor_start_begin", None, None)
            while True:
                # Double check tor is dead
                try:
                    tor_process.send_signal(signal.SIGINT)
                    tor_process.wait()
                except:
                    pass
                # try to start tor
                tor_started = False
                try:
                    tor_process = stem_process.launch_tor_with_config(
                        config=tor_config, take_ownership=True
                    )
                    tor_started = True
                except:
                    pass
                if tor_started:
                    logger.log("tor_start_finish", None, None)
                    break
        # Create a url from the host
        # TODO: we have to think about http vs https here
        # What if the site doesn't have https, should we do http first?
        # Should we just test them all ahead of time?
        url = f"http://{host}"
        # We need to know exactly what time we navigated to the website,
        # so we can pick it out in the pcap. Log this
        logger.log("navigation_begin", url, f"{n+1}/{num_websites}")
        # Navigate to the url
        try:
            driver.get(url)
            # Log that we finished navigating to the url
            logger.log("navigation_end", url, f"{n+1}/{num_websites}")
        except Exception as ex:
            # Log that we finished navigating to the url
            tbs = b64encode(traceback.format_exc().encode("utf-8"))
            logger.log("navigation_failed", url, f"{n+1}/{num_websites} {tbs}")
        # Once the driver has determined that it's finished
        # navigating to the url, we want to navigate to about:blank
        # because websites often send additional traffic for analytics, etc
        # navigating to about:blank sets a blank slate. Theoretically, no
        # additional traffic should be sent after this has completed
        logger.log("navigation_begin", BLANK_URL, f"{n+1}/{num_websites}")
        driver.get(BLANK_URL)
        logger.log("navigation_end", BLANK_URL, f"{n+1}/{num_websites}")
        # Stop tor
        if tor:
            logger.log("tor_stop_begin", None, None)
            tor_process.send_signal(signal.SIGINT)
            tor_process.wait()
            logger.log("tor_stop_end", None, None)
    # Stop the webdriver
    logger.log("driver_close_begin", None, None)
    driver.close()
    logger.log("driver_close_end", None, None)
    # Stop shadowsocks
    if shadowsocks_client_type is not None:
        logger.log("shadowsocks_stop_begin", None, None)
        shadowsocks.stop()
        logger.log("shadowsocks_stop_end", None, None)


if __name__ == "__main__":
    # Define and run an argument parser
    parser = argparse.ArgumentParser(
        description="Requests websites and gathers traffic"
    )
    parser.add_argument(
        "website_ranking_path",
        type=Path,
        help="Path to a csv of website rankings. Assumes no column headers and the columns in order rank,host where rank is an integer and host is a string",
    )
    parser.add_argument(
        "num_websites",
        type=int,
        help="Number of websites to navigate to. This program will choose websites sorted by rank.",
    )
    parser.add_argument(
        "pcap_directory",
        type=Path,
        help="Path to a directory to store pcaps and associated logs in. If it doesn't exist, it will be created",
    )
    parser.add_argument(
        "experiment_suffix",
        type=str,
        help="Suffix on pcap filenames. Filenames will look like '1631921353_suffix.pcapng'",
    )
    parser.add_argument(
        "-s",
        "--shadowsocks",
        required=False,
        dest="shadowsocks_client_type",
        type=str,
        choices=SHADOWSOCKS_CLIENT_TYPES,
        help="If specified, the gathering process will use shadowsocks. Must specify a client type",
    )
    parser.add_argument(
        "-t",
        "--tor",
        dest="tor",
        default=False,
        help="Whether to use Tor with obfs4. Mutually exclusive with shadowsocks",
        action="store_true",
    )
    # Start a shadowsocks argument group
    ss_group = parser.add_argument_group(
        title="required shadowsocks arguments",
        description="Arguments required when -s or --shadowsocks are specified",
    )
    ss_group.add_argument(
        "--ss-host",
        metavar="HOST",
        dest="shadowsocks_host",
        type=str,
        help="Shadowsocks host to connect to",
    )
    ss_group.add_argument(
        "--ss-port",
        metavar="PORT",
        dest="shadowsocks_port",
        type=int,
        help="Shadowsocks port for the host",
    )
    ss_group.add_argument(
        "--ss-pass",
        metavar="PASSWORD",
        dest="shadowsocks_password",
        type=str,
        help="Shadowsocks password",
    )
    ss_group.add_argument(
        "--ss-method",
        metavar="METHOD",
        dest="shadowsocks_method",
        type=str,
        help="Shadowsocks method. Note that this may be different between the libev and go clients, so make sure you choose accordingly.",
    )
    ss_group.add_argument(
        "--ss-local-port",
        metavar="PORT",
        dest="shadowsocks_local_port",
        type=int,
        help="Port to host the shadowsocks local SOCKS proxy on",
    )
    # Start a group for optional shadowsocks arguments
    ss_group_opt = parser.add_argument_group(
        title="optional shadowsocks arguments",
        description="Arguments optional when -s or --ss are specified",
    )
    ss_group_opt.add_argument(
        "--ss-fast-open",
        dest="shadowsocks_fast_open",
        type=bool,
        help="Whether to use TCP fast open. Only applies for the libev client",
    )
    # Parse arguments
    args = parser.parse_args()
    # Manually check the conditionally required arguments
    if args.shadowsocks_client_type is not None:
        if args.shadowsocks_host is None:
            parser.error("host is required if using shadowsocks")
        if args.shadowsocks_port is None:
            parser.error("port is required if using shadowsocks")
        if args.shadowsocks_password is None:
            parser.error("password is required if using shadowsocks")
        if args.shadowsocks_method is None:
            parser.error("method is required if using shadowsocks")
        if args.shadowsocks_local_port is None:
            parser.error("local port is required if using shadowsocks")
    # Call our main function
    main(
        website_ranking_path=args.website_ranking_path,
        num_websites=args.num_websites,
        pcap_directory=args.pcap_directory,
        experiment_suffix=args.experiment_suffix,
        shadowsocks_client_type=args.shadowsocks_client_type,
        shadowsocks_host=args.shadowsocks_host,
        shadowsocks_port=args.shadowsocks_port,
        shadowsocks_password=args.shadowsocks_password,
        shadowsocks_method=args.shadowsocks_method,
        shadowsocks_local_port=args.shadowsocks_local_port,
        shadowsocks_fast_open=args.shadowsocks_fast_open,
        tor=args.tor,
    )
