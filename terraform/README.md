# Real World Testing

## TODO

As a best practice, use temporary security credentials (IAM roles) instead of access keys, and disable any AWS account root user access keys. For more information, see [Best Practices for Managing AWS Access Keys](https://docs.aws.amazon.com/general/latest/gr/aws-access-keys-best-practices.html) in the Amazon Web Services General Reference.

## Terraform

### Install

https://www.terraform.io/downloads

#### macOS

```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
```

#### Ubuntu / Debian

```bash
wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
```

### Hosting Providers

https://registry.terraform.io/

### Running

```bash
cd terraform/
# Initialize the project, e.g. download the required providers (e.g. AWS).
terraform init

# Optionally validate the Terraform configuration
terraform validate

# Spin up the infrastructure.
terraform apply -auto-approve \
  -var "do_token=${DO_PAT}" \
  -var "pvt_key=$HOME/.ssh/id_rsa"

# Show details about the newly created instance.
terraform show

# Get the output variables from the `apply` command. Useful for grabbing VPS IPs.
terraform output
# View a specific output variable.
terraform output instance_id

# Tear it all down.
terraform destroy -auto-approve \
  -var "do_token=${DO_PAT}" \
  -var "pvt_key=$HOME/.ssh/id_rsa"

# Using variables.
terraform apply -var "instance_name=MiceClient"
```

### Digital Ocean

You will need to
* [Create an access token](https://docs.digitalocean.com/reference/api/create-personal-access-token/)
* [Add your public ssh key](https://docs.digitalocean.com/products/droplets/how-to/add-ssh-keys/to-team/)

### CDKTF (Cloud Development Kit for Terraform)

CDKTF generates json Terraform configuration from code (in our case, Python).

```bash
npm install --global cdktf-cli@latest
# Confirm install and check version.
npm list --global

cdktf help
```