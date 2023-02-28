variable "aws_key_name" {
  description = "The key name to use for ssh"
  type        = string
}

variable "server_ip_address" {
  description = "The IP address of the server to connect to"
  type = string
}

variable "aws_security_group" {
  type = string
}

variable "client_name" {
  description = "Value of the Name tag for the EC2 client instance"
  type        = string
  default     = "TestingClient"
}

variable "client_docker_image" {
  description = "The docker image to run on the client"
  type        = string
  default     = "jaxbysaloosh/tester"
}

variable "client_output_log_dir" {
  description = "The location to store logs on the client"
  type        = string
  default     = "/etc/test_logs/"
}

variable "shadowsocks_port" {
  description = "The port to use for shadowsocks"
  type        = number
  default     = 8080
}

variable "shadowsocks_password" {
  description = "The password to use for shadowsocks"
  type        = string
  default     = "fdajfdal4324324FDSFDSFD%$@$%@$#@"
}

# TODO: update the default value
variable "num_sites_to_visit" {
  description = "The number of websites to visit during the experiment. Will pick the top N sites."
  type        = number
  default     = 10
}

# TODO: update default value
variable "experiment_log_suffix" {
  description = "A string to appened to the log files name. Used to differentiate experiments"
  type        = string
  default     = "test"
}
