# TODO: we don't plan to (afaik) run clients in AWS, so this is just for testing.
resource "aws_instance" "test_client" {
  ami                         = "ami-052efd3df9dad4825"
  instance_type               = "t2.micro"
  subnet_id                   = "subnet-0e9bc6742971742ac"
  associate_public_ip_address = true
  key_name                    = var.aws_key_name
  security_groups             = ["${var.aws_security_group}"]

  # Need to wait for the server to spin up before starting the client so that it has something to connect to.
  # depends_on = [aws_instance.test_server, digitalocean_droplet.test_server]

  user_data = <<-EOL
  #!/bin/bash -xe

  echo "hello world!"

  # TODO: don't hardcode this to the AWS server. Needs to be whatever server is running.
  echo "${var.server_ip_address}" > /tmp/test_server_ip

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
       --name=mice-client \
       --volume ${var.client_output_log_dir}:/home/browser/mount \
       ${var.client_docker_image} \
       --shadowsocks=libev \
       --server-host=${var.server_ip_address} \
       --server-port=${var.shadowsocks_port} \
       --ss-pass=${var.shadowsocks_password} \
       --ss-method=aes-256-gcm \
       --socks-local-port=9050 \
       --ss-fast-open=true \
       /home/browser/scripts/top-10k.csv ${var.num_sites_to_visit} /home/browser/mount ${var.experiment_log_suffix}

  EOL

  tags = {
    Name = var.client_name
  }
}
