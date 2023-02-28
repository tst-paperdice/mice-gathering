variable "server_name" {
  description = "Value of the Name tag for the EC2 server instance"
  type        = string
  default     = "TestingServer"
}

variable "client_name" {
  description = "Value of the Name tag for the EC2 client instance"
  type        = string
  default     = "TestingClient"
}

variable "server_docker_image" {
  description = "The docker image to run on the server"
  type        = string
  default     = "jaxbysaloosh/webapp"
}

variable "client_docker_image" {
  description = "The docker image to run on the client"
  type        = string
  default     = "jaxbysaloosh/tester"
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

variable "server_output_log_dir" {
  description = "The location to store logs on the server"
  type        = string
  default     = "/etc/test_logs/"
}

variable "client_output_log_dir" {
  description = "The location to store logs on the client"
  type        = string
  default     = "/etc/test_logs/"
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

variable "module_source" {
  type = string
  default = "./client/"
}