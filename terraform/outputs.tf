
# TODO: these are all hardcoded to AWS instance. Update to use whatever server is running.

# output "server_id" {
#   description = "ID of the EC2 client instance"
#   value       = aws_instance.test_server.id
# }

# output "server_public_ip" {
#   description = "Public IP address of the EC2 client instance"
#   value       = aws_instance.test_server.public_ip
# }

output "server_public_dns" {
  description = "Public DNS address of the EC2 client instance"
  value       = length(aws_instance.test_server) > 0 ? aws_instance.test_server[*].public_dns : null
}

# output "client_id" {
#   description = "ID of the EC2 client instance"
#   value       = aws_instance.test_client.id
# }

# output "client_public_ip" {
#   description = "Public IP address of the EC2 client instance"
#   value       = aws_instance.test_client.public_ip
# }

# output "client_public_dns" {
#   description = "Public DNS address of the EC2 client instance"
#   value       = aws_instance.test_client.public_dns
# }



output "server_digitalocean" {
  value = digitalocean_droplet.test_server.ipv4_address
}

output client_ip_address {
  value = module.test_client.ip_address
}
