provider "aws" {
  # Add provider configuration here
}

resource "aws_vpc" "net2" {
  cidr_block = "192.168.2.0/24"
  tags = { Name = "net2" }
}
resource "aws_subnet" "net2" {
  vpc_id = aws_vpc.net2.id
  cidr_block = "192.168.2.0/24"
  tags = { Name = "net2_subnet" }
}
resource "aws_vpc" "net1" {
  cidr_block = "192.168.1.0/24"
  tags = { Name = "net1" }
}
resource "aws_subnet" "net1" {
  vpc_id = aws_vpc.net1.id
  cidr_block = "192.168.1.0/24"
  tags = { Name = "net1_subnet" }
}
resource "aws_internet_gateway" "R1" {
  vpc_id = aws_vpc.net2.id
  tags = { Name = "R1_igw" }
}
resource "aws_route_table" "R1" {
  vpc_id = aws_vpc.net2.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.R1.id
  }
  tags = { Name = "R1" }
}
resource "aws_instance" "vm1" {
  ami = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.small"
  key_name = "my-key"
  vpc_security_group_ids = ["sg-default"]
  subnet_id = "aws_subnet.net1.id"
  private_ip = "192.168.1.10"
  associate_public_ip_address = true
  tags = { Name = "vm1" }
}
resource "aws_instance" "s2" {
  ami = "ami-042e828730a8e686c"
  instance_type = "t2.medium"
  key_name = "my-key"
  vpc_security_group_ids = ["sg-default"]
  subnet_id = "aws_subnet.net2.id"
  private_ip = "192.168.2.10"
  associate_public_ip_address = true
  tags = { Name = "s2" }
}