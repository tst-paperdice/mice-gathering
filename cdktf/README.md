# CDKTF

## Prereqs

Install terraform cli.
https://learn.hashicorp.com/tutorials/terraform/install-cli

install node.js and npm using nvm (TODO: include instructions to install nvm)
```bash
nvm install --lts
```
https://nodejs.org/en/

Install cdktf
```bash
npm install --global cdktf-cli@latest
cdktf help

sudo -H python3 -m pip install --upgrade pipenv
```

### AWS Provider

You will need a file named `~/.aws/config` with a mice profile like
```txt
[profile mice]
region = us-east-1
output = json
```

and `~/.aws/credentials`
```txt
[mice]
aws_access_key_id = <ACCESS KEY ID>
aws_secret_access_key = <SECRET KEY>
```

## Initializing a Project



```bash
cdktf init --template="python" --local --project-name=mice-gathering --project-description="Spinning up infrastructure to measure real-world internet censorship." --enable-crash-reporting=false
# Add providers
cdktf provider add "aws@~>4.0"
cdktf provider add "digitalocean/digitalocean@~>2.0"

# Or, if the project is already initialized, pull the modules and providers.
cdktf get
pipenv install
```

For some providers you will need to update the `terraformProviders` field in [`cdktf.json`](cdktf.json). For example:
```json
{
  "language": "python",
  "app": "pipenv run python main.py",
  "projectId": "5fcb7a5e-0526-4405-9054-e77bf73de042",
  "sendCrashReports": "false",
  "terraformModules": [],
  "codeMakerOutput": "imports",
  "context": {
    "excludeStackIdFromLogicalIds": "true",
    "allowSepCharsInLogicalIds": "true"
  }
}
```

## Run It!

```bash
# TODO: find a cleaner way of setting this, probably user input or some config file or something
# Set your DigitalOcean token as an env var.
export DO_PAT=$(cat ~/projects/mice/do_pat.txt)

cdktf deploy --auto-approve

# View the outputs of the configuration.
cdktf output

# Check the progress.
CLIENT_IP=$(cat terraform.mice_gathering_infra.tfstate | jq -r .outputs.client_public_ip.value)
sed -i '' "/$CLIENT_IP/d" ~/.ssh/known_hosts
ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@${CLIENT_IP}
ssh ubuntu@${CLIENT_IP} "tail -f /etc/test_logs/*.log"

SERVER_IP=$(jq -r .outputs.server_public_ip.value terraform.mice_gathering_infra.tfstate)
ssh -i ~/.ssh/id_rsa_digital_ocean -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@${SERVER_IP}

SERVER_PORT=$(jq -r .outputs.shadowsocks_port.value terraform.mice_gathering_infra.tfstate)
netcat -zv ${SERVER_IP} ${SERVER_PORT}

# Tear down the configuration.
cdktf destroy --auto-approve
```

## References

### Provider source code

* CDKTF: ~/.local/share/virtualenvs/cdktf-*/lib/python3.9/site-packages/cdktf
* AWS: ~/.local/share/virtualenvs/cdktf-*/lib/python3.9/site-packages/cdktf_cdktf_provider_aws
* DigitalOcean: ~/.local/share/virtualenvs/cdktf-*/lib/python3.9/site-packages/cdktf_cdktf_provider_digitalocean

### Examples of censored sites for testing

https://en.greatfire.org/analyzer
https://en.greatfire.org/search/alexa-top-1000-domains

## Debugging

The generated json Terraform configuration can be found at this path.
```
cdktf/cdktf.out/stacks/mice_gathering_infra/cdk.tf.json
```

### Docker

If things are going wrong you can check the Docker logs on the VPS instances.
```bash
docker logs $(docker container ls | grep jaxbysaloosh | awk '{print $1}')
```

### AWS

The logs for the output of user data are located in `/var/log/cloud-init.lo`1 and `/var/log/cloud-init-output.log`.

## Troubleshooting

### Terraform doing weird or unexpected things

Check the file [`cdk.tf.json`](cdktf.out/stacks/mice_gathering_infra/cdk.tf.json) to make sure your code is being properly transformed into HCL.

### Error: Missing resource schema from provider

If you receive an error like this:

```
[2022-09-07T14:23:27.698] [ERROR] default - ╷
│ Error: Missing resource schema from provider
│ 
mice_gathering_infra  ╷
                      │ Error: Missing resource schema from provider
                      │ 
                      │ No resource schema found for aws_key_pair.
```

delete the state files

```bash
rm -rf *.tfstate*
```

and re-run the deploy command.

### Docker

#### Getting Docker Logs from Remote Host

DigitalOcean
```bash
ssh -i ~/.ssh/id_rsa_digital_ocean root@167.71.164.27 'docker logs $(docker container ls -a | grep server | cut -d " " -f 1)' &> docker-logs.txt
```