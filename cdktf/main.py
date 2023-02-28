#!/usr/bin/env python
import os
import random
from constructs import Construct
from cdktf import (
    App,
    TerraformStack,
    TerraformOutput,
    SSHProvisionerConnection,
    RemoteExecProvisioner,
    TerraformVariable,
)
from cdktf_cdktf_provider_aws import AwsProvider, ec2
from cdktf_cdktf_provider_aws.vpc import (
    InternetGateway,
    Vpc,
    SecurityGroup,
    SecurityGroupIngress,
    SecurityGroupEgress,
    Subnet,
    RouteTable,
    RouteTableAssociation,
    RouteTableRoute,
)

from cdktf_cdktf_provider_digitalocean import (
    DigitaloceanProvider,
    Droplet,
    DataDigitaloceanSshKey,
)

from servers.DigitalOceanServer import DigitalOceanServer
from clients.AWSClient import AWSClient

from shadowsocks_port import get_random_shadowsocks_port
from docker_utils import generate_docker_run_command


class DigitalOceanStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        # TODO: make this an enum or something
        # protocol = "obfs"
        # protocol = "shadowsocks"
        protocol = "endpoints"

        shadowsocks_password: str = "fdajfdal4324324FDSFDSFD%$@$%@$#@"  # TODO: default to random generated if not provided
        # shadowsocks_port = get_random_shadowsocks_port()

        shadowsocks_port = get_random_shadowsocks_port()
        # shadowsocks_port.add_validation(
        #     condition=lambda x: x >= 9000 and x <= 11000,
        #     error_message="port must be in the range [9000, 10000]",
        # )
        output_log_dir = "/etc/test_logs/"

        # endpoints_script_file_path = f"obfs-json/obfs-{random.randint(1, 100)}.json"
        # endpoints_script_file_path = f"obfs-json/adv-39.json"
        # endpoints_script_file_path = f"obfs-json/input-0.json"
        # endpoints_script_file_path = f"obfs-json/input-22.json"
        # endpoints_script_file_path = "scripts2/scripts2-input-0.json"
        endpoints_script_file_path = TerraformVariable(
            self,
            "endpoints_script_file_path",
            # default="",
            type="string",
            nullable=False,
        )

        docker_run_command = generate_docker_run_command(
            "server",
            protocol,
            shadowsocks_password=shadowsocks_password,
            shadowsocks_port=shadowsocks_port,
            output_log_dir=output_log_dir,
            endpoints_script_file_path=endpoints_script_file_path.string_value,
        )

        server = DigitalOceanServer(
            self,
            docker_run_command=docker_run_command,
            output_log_dir=output_log_dir,
        )

        num_sites_to_visit = 25

        docker_run_command = generate_docker_run_command(
            "client",
            protocol,
            shadowsocks_password=shadowsocks_password,
            shadowsocks_port=shadowsocks_port,
            num_sites_to_visit=num_sites_to_visit,
            server_ip_address=server.public_ip_address,
            output_log_dir=output_log_dir,
            endpoints_script_file_path=endpoints_script_file_path.string_value,
        )

        _client = AWSClient(self, docker_run_command=docker_run_command, output_log_dir=output_log_dir)

        TerraformOutput(
            self,
            "shadowsocks_port",
            description="The port used by shadowsocks",
            value=shadowsocks_port,
        )

        TerraformOutput(
            self,
            "protocol",
            description="The protocol used for the experiment",
            value=protocol,
        )

        TerraformOutput(
            self,
            "endpoints_script_file_path_output",
            description="The traffic script used by the endpoints",
            value=endpoints_script_file_path,
        )

        


app = App()
# MyStack(app, "mice_gather_infra_aws")
DigitalOceanStack(app, "mice_gathering_infra")

app.synth()
