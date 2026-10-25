variable "aws_region" {
  description = "Регион AWS, где создаётся сервер (Франкфурт)"
  type        = string
  default     = "eu-central-1"
}

variable "ubuntu_ami" {
  description = "ID образа операционной системы Ubuntu 24.04 в AWS"
  type        = string
  default     = "ami-0e872aee57663ae2d"
}

variable "instance_type" {
  description = "Размер (мощность) сервера EC2 (бесплатный тариф)"
  type        = string
  default     = "t2.micro"
}

variable "server_name" {
  description = "Имя нашего сервера в панели AWS"
  type        = string
  default     = "url-shortener-prod-server"
}
