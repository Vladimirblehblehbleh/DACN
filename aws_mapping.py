# aws_mapping.py

# Bảng tra cứu AMI
image_to_ami = {
    "ubuntu-server": "ami-0c55b159cbfafe1f0",
    "ubuntu-server-focal": "ami-042e828730a8e686c"
}

# Bảng tra cứu instance_type từ cpu/ram
cpu_ram_to_instance_type = {
    (2, 2): "t2.small",
    (2, 4): "t2.medium"
}

# Template cho từng loại resource
templates = {
    "instances": '''resource "aws_instance" "{name}" {{
  ami = "{ami}"
  instance_type = "{instance_type}"
  key_name = "{key_name}"
  vpc_security_group_ids = ["{vpc_security_group_ids}"]
  subnet_id = "aws_subnet.{subnet_name}.id"
  private_ip = "{private_ip}"
  associate_public_ip_address = {associate_public_ip}
  tags = {{ Name = "{name}" }}
}}''',
    "networks": '''resource "aws_vpc" "{name}" {{
  cidr_block = "{cidr}"
  tags = {{ Name = "{name}" }}
}}
resource "aws_subnet" "{name}" {{
  vpc_id = aws_vpc.{name}.id
  cidr_block = "{cidr}"
  tags = {{ Name = "{name}_subnet" }}
}}''',
    "routers": '''resource "aws_internet_gateway" "{name}" {{
  vpc_id = aws_vpc.{vpc_name}.id
  tags = {{ Name = "{name}_igw" }}
}}
resource "aws_route_table" "{name}" {{
  vpc_id = aws_vpc.{vpc_name}.id
  route {{
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.{name}.id
  }}
  tags = {{ Name = "{name}" }}
}}'''
}

# Hàm ánh xạ dữ liệu
def map_resource(section, item):
    if section == "instances":
        data = {
            "name": item["name"],
            "ami": image_to_ami.get(item.get("image", "ubuntu-server"), "ami-default"),
            "instance_type": cpu_ram_to_instance_type.get((item.get("cpu", 1), item.get("ram", 1)), "t2.micro"),
            "key_name": item.get("key_name", "my-key"),
            "vpc_security_group_ids": item.get("vpc_security_group_ids", "sg-default"),
            "subnet_name": item["networks"][0]["name"] if "networks" in item and item["networks"] else "default",
            "private_ip": item["networks"][0]["ip"] if "networks" in item and item["networks"] else "10.0.0.10",
            "associate_public_ip": item.get("associate_public_ip_address", "true")
        }
    elif section == "networks":
        data = {
            "name": item["name"],
            "cidr": item["cidr"]
        }
    elif section == "routers":
        data = {
            "name": item["name"],
            "vpc_name": item["networks"][0]["name"] if "networks" in item and item["networks"] else "default"
        }
    return templates[section].format(**data)