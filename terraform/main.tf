terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_security_group" "web_sg" {
  name        = "url-shortener-sg"
  description = "Allow SSH and HTTP traffic"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "app_server" {
  ami                    = var.ubuntu_ami
  instance_type          = var.instance_type
  vpc_security_group_ids = [aws_security_group.web_sg.id]

  user_data = <<-EOF
              #!/bin/bash
              apt-get update
              apt-get install -y docker.io docker-compose-v2 git
              systemctl start docker
              systemctl enable docker
              git clone https://github.com/werhogowich/url-shortener.git /opt/url-shortener
              cd /opt/url-shortener
              echo "POSTGRES_DB=shortener_db" >> .env
              echo "POSTGRES_USER=dima_admin" >> .env
              echo "POSTGRES_PASSWORD=super_secret_pass_123" >> .env
              echo "DATABASE_URL=postgresql://dima_admin:super_secret_pass_123@db:5432/shortener_db" >> .env
              docker compose up -d --build
              EOF

  tags = {
    Name = var.server_name
  }
}
