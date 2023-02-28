
output "ip_address" {
  value = aws_instance.test_client.public_ip
}
