import os
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


class AWSClient:
    def __init__(
        self,
        scope: Construct,
        *,
        docker_run_command: str,
        output_log_dir: str,
    ):

        output_log_dir = "/etc/test_logs/"

        experiment_log_suffix = "test"

        region = "us-east-1"
        AwsProvider(scope, "AWS", profile="mice", region=region)

        mice_vpc = Vpc(
            scope,
            "MiceCustomVpc",
            cidr_block="10.32.0.0/16",
        )

        security_group_allow_all = SecurityGroup(
            scope,
            "mice_allow_all",
            description="Allow all traffic",
            vpc_id=mice_vpc.id,
            tags={"Name": "mice_allow_all"},
            ingress=[
                SecurityGroupIngress(
                    from_port=0,
                    to_port=65535,
                    protocol="tcp",
                    cidr_blocks=["0.0.0.0/0"],
                    ipv6_cidr_blocks=["::/0"],
                )
            ],
            egress=[
                SecurityGroupEgress(
                    from_port=0,
                    to_port=0,
                    protocol="-1",  # All protocols
                    cidr_blocks=["0.0.0.0/0"],
                    ipv6_cidr_blocks=["::/0"],
                )
            ],
        )

        mice_igw = InternetGateway(
            scope,
            "mice-gateway-cdktf",
            vpc_id=mice_vpc.id,
        )

        # Enable subnet to access the open internet by routing traffice to the internet
        # gateway.
        mice_route_table = RouteTable(
            scope,
            "mice-route-table-cdktf",
            vpc_id=mice_vpc.id,
            route=[
                RouteTableRoute(
                    cidr_block="0.0.0.0/0",
                    gateway_id=mice_igw.id,
                ),
                RouteTableRoute(
                    ipv6_cidr_block="::/0",
                    gateway_id=mice_igw.id,
                ),
            ],
            tags={"Name": "mice-route-table-cdktf"},
        )

        mice_subnet = Subnet(
            scope,
            "mice-subnet",
            vpc_id=mice_vpc.id,
            tags={"Name": "mice-subnet-cdktf"},
            cidr_block="10.32.128.0/20",
        )

        # Associate the route table with the subnet.
        mice_rta = RouteTableAssociation(
            scope,
            "mice-route-table-association",
            route_table_id=mice_route_table.id,
            subnet_id=mice_subnet.id,
        )

        # TODO: set the `public_key` based on user input, probably a path to a file.
        key_pair = ec2.KeyPair(
            scope,
            "deployer-key",
            public_key="TODO: paste your public key here",
        )

        user_data = f"""#!/bin/bash -xe
# Install docker.
# TODO: is there an AMI with Docker preinstalled?
sudo apt-get update
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update -y
apt-cache policy docker-ce
sudo apt install -y docker-ce

mkdir {output_log_dir}

{docker_run_command}

tcpdump -s 98 -i eth0 -w {output_log_dir}/capture-{experiment_log_suffix}.pcap &
        """

        # https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance
        self.instance = ec2.Instance(
            scope,
            "compute",
            ami="ami-052efd3df9dad4825",
            associate_public_ip_address=True,
            instance_type="t2.micro",
            tags={"Name": "test-client"},
            subnet_id=mice_subnet.id,
            security_groups=[security_group_allow_all.id],
            key_name=key_pair.key_name,
            user_data=user_data,
        )

        TerraformOutput(
            scope,
            "client_public_ip",
            description=f"public IP of the {type(self).__name__} instance",
            value=self.instance.public_ip,
        )

        # TerraformOutput(
        #     scope,
        #     "ec2_id",
        #     value=instance.id,
        # )

        # TerraformOutput(
        #     scope,
        #     "vpc_id",
        #     value=mice_vpc.id,
        # )

        # TerraformOutput(
        #     scope,
        #     "sg_id",
        #     value=security_group_allow_all.id,
        # )

        # TerraformOutput(
        #     scope,
        #     "subnet_id",
        #     value=mice_subnet.id,
        # )

        TerraformOutput(
            scope,
            "client_region",
            value=region,
        )

        TerraformOutput(
            scope,
            "client_hosting_service",
            description="The hosting service used for the client",
            value="AWS",  # TODO: or maybe use {type(self).__name__} instead
        )

        TerraformOutput(
            scope,
            "client_private_ip",
            description=f"private IP of the {type(self).__name__} instance",
            value=self.instance.private_ip,
        )
