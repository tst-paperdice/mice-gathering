terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  profile = "mice"
  region  = "us-east-1"
}

# Add your public key to the instance for SSH access.
resource "aws_key_pair" "deployer" {
  key_name   = "deployer-key"
  public_key = "TODO: add your public key here"
}

resource "aws_security_group" "allow_all" {
  name        = "allow_all"
  description = "Allow all traffic"
  vpc_id      = "vpc-0117f682f4c26a83f" # TODO: don't hardcode this. Create a VPC dynamically?

  ingress {
    from_port        = 0
    to_port          = 65535
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  ingress {
    from_port = -1
    to_port   = -1
    protocol  = "icmp"
  }

  ingress {
    from_port = -1
    to_port   = -1
    protocol  = "icmpv6"
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1" # All protocols
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = {
    Name = "allow_all"
  }
}

resource "aws_instance" "test_server" {
  count = 0
  ami                         = "ami-052efd3df9dad4825"
  instance_type               = "t2.micro"
  subnet_id                   = "subnet-0e9bc6742971742ac"
  associate_public_ip_address = true
  key_name                    = aws_key_pair.deployer.key_name
  security_groups             = ["${aws_security_group.allow_all.id}"]

  user_data = <<-EOL
  #!/bin/bash -xe

  echo "hello world!"

  # Install docker.
  # TODO: is there an AMI with Docker preinstalled?
  sudo apt-get update
  sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt update -y
  apt-cache policy docker-ce
  sudo apt install -y docker-ce

  mkdir ${var.client_output_log_dir}

  docker run \
    --name=mice-server \
    --env SS_SERVER_PORT=${var.shadowsocks_port} \
    --env SS_PASSWORD=${var.shadowsocks_password} \
    --volume ${var.client_output_log_dir}:/mount \
    --network=bridge \
    --publish ${var.shadowsocks_port}:${var.shadowsocks_port} \
    ${var.server_docker_image} \
    start-ss.sh

  EOL

  tags = {
    Name = var.server_name
  }
}


variable "do_token" {}
variable "pvt_key" {}

provider "digitalocean" {
  token = var.do_token
}

data "digitalocean_ssh_key" "terraform" {
  name = "mice"
}


resource "digitalocean_droplet" "test_server" {
  image  = "ubuntu-20-04-x64"
  name   = "test-server"
  region = "nyc3" # TODO: make this configurable base on user input. Make it generic to work across DO and AWS.
  size   = "s-1vcpu-1gb"
  # TODO: is it possible to pass a local ssh public key value instead?
  ssh_keys = [
    data.digitalocean_ssh_key.terraform.id
  ]

  connection {
    host        = self.ipv4_address
    user        = "root"
    type        = "ssh"
    private_key = file(var.pvt_key)
    timeout     = "2m"
  }

  provisioner "remote-exec" {
    inline = [
      "export PATH=$PATH:/usr/bin",
      "sudo apt update",
      "echo 'hello MICE world'",
      "sudo apt install -y apt-transport-https ca-certificates curl software-properties-common",
      "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg",
      "echo \"deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable\" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null",
      "sudo apt update -y",
      "apt-cache policy docker-ce",
      "sudo apt install -y docker-ce",
      "docker run -d --name=mice-server --env SS_SERVER_PORT=${var.shadowsocks_port} --env SS_PASSWORD=${var.shadowsocks_password} --volume ${var.client_output_log_dir}:/mount --network=bridge --publish ${var.shadowsocks_port}:${var.shadowsocks_port} ${var.server_docker_image} start-ss.sh"
    ]
  }
}

module "test_client" {
  source = "./client/"

  depends_on = [aws_instance.test_server, digitalocean_droplet.test_server]

  client_name = var.client_name
  server_ip_address = digitalocean_droplet.test_server.ipv4_address

  aws_key_name = aws_key_pair.deployer.key_name
  aws_security_group = aws_security_group.allow_all.id

}
