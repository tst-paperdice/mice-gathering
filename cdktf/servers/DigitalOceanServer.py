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
from cdktf_cdktf_provider_digitalocean import (
    DigitaloceanProvider,
    Droplet,
    DataDigitaloceanSshKey,
)


class DigitalOceanServer:
    def __init__(
        self,
        stack: Construct,
        *,
        docker_run_command: str,
        output_log_dir: str,
    ):

        # Inputs
        # TODO: have user set these, or make them legit Terraform inputs.
        private_key_file_path: str = "~/.ssh/id_rsa_digital_ocean"
        experiment_log_suffix = "test"

        # TODO: let user configure how token is passed in.
        # digitalOceanAcessToken = TerraformVariable(
        #     stack,
        #     "DigitalOceanAcessToken",
        #     type="string",
        #     description="Access token for DigitalOcean"
        # )
        DigitaloceanProvider(stack, "DigitalOcean", token=os.environ["DO_PAT"])

        # This key has been preconfigued in the DigitalOcean account via the web UI.
        # TODO: is there a way to do this programatically?
        ssh_key = DataDigitaloceanSshKey(
            stack,
            "mice-ssh-key",
            name="mice-digital_ocean",
        )

        TerraformOutput(
            stack,
            f"ssh_key_digital_ocean",
            value=ssh_key,
        )

        pvt_key = None
        # TODO: let use set private key file location. Or just generate temporary key on the fly? https://stackoverflow.com/questions/2466401/how-to-generate-ssh-key-pairs-with-python
        # TODO: I had to add the corresponding public key to DigitalOcean via the web UI. Is there any way to do this programatically?
        with open(private_key_file_path, "r") as key_file:
            pvt_key = key_file.read()

        self.mice_droplet = Droplet(
            stack,
            "mice-droplet",
            image="ubuntu-20-04-x64",
            name="test-server-mice-jaxby-yolo",
            region="nyc3",
            size="s-1vcpu-1gb",
            ssh_keys=[str(ssh_key.id)],
            connection=SSHProvisionerConnection(
                type="ssh",
                host="${self.ipv4_address}",  # Reference a resource attribute.
                user="root",  # TODO: let user set user? Or keep track and provide easy way to run ssh?
                private_key=pvt_key,  # According to the docs this _should_ disable password ssh.
                # password="hard2guess&^%$#@!",
                timeout="2m",
            ),
            user_data = f"""#!/bin/bash -xe
set -x
echo 'hello MICE world FIRSTTTTTTT'
export PATH=$PATH:/usr/bin
sudo apt update
echo 'hello MICE world'
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update -y
apt-cache policy docker-ce
sudo apt install -y docker-ce
mkdir {output_log_dir}
nohup tcpdump -s 98 -i eth0 -w {output_log_dir}/capture-{experiment_log_suffix}.pcap &
{docker_run_command}
sleep 10
            """
        )

        TerraformOutput(
            stack,
            "server_public_ip",
            description=f"public IP of the {type(self).__name__} instance",
            value=self.mice_droplet.ipv4_address,
        )

        # TerraformOutput(
        #     stack,
        #     "server_shadowsocks_port",
        #     description="The port opened by shadowsocks on the server",
        #     value=shadowsocks_port,
        # )

        TerraformOutput(
            stack,
            "server_hosting_service",
            description="The hosting service used for the server",
            value="DigitalOcean",
        )

        TerraformOutput(
            stack,
            "server_private_ip",
            description=f"private IP of the {type(self).__name__} instance",
            value=self.mice_droplet.ipv4_address_private,
        )

    @property
    def public_ip_address(self):
        return self.mice_droplet.ipv4_address
