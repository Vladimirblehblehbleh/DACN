# generate.py
import json
from aws_mapping import image_to_ami, cpu_ram_to_instance_type

# Đọc JSON
with open("instance.json", "r") as f:
    instances = json.load(f)

# Hàm sinh HCL
def generate_hcl(instances):
    hcl = ""
    for item in instances["instances"]:
        resource_name = item["name"]
        hcl += f'resource "aws_instance" "{resource_name}" {{\n'
        
        # Lấy giá trị từ JSON và ánh xạ
        ami = image_to_ami.get(item.get("image", "ubuntu-server"), "ami-default")  # Dùng bảng tra cứu
        instance_type = cpu_ram_to_instance_type.get((item.get("cpu", 1), item.get("ram", 1)), "t2.micro")  # Tính từ cpu/ram
        key_name = item.get("key_name", "my-key")
        vpc_security_group_ids = item.get("vpc_security_group_ids", "sg-default")
        subnet_id = item.get("subnet_id", "subnet-default")
        private_ip = item["networks"][0]["ip"] if "networks" in item and item["networks"] else "10.0.0.10"
        associate_public_ip = item.get("associate_public_ip_address", "true")
        tags = f'tags = {{ Name = "{resource_name}" }}'

        # Điền vào template
        hcl += f'  ami = "{ami}"\n'
        hcl += f'  instance_type = "{instance_type}"\n'
        hcl += f'  key_name = "{key_name}"\n'
        hcl += f'  vpc_security_group_ids = ["{vpc_security_group_ids}"]\n'
        hcl += f'  subnet_id = "{subnet_id}"\n'
        hcl += f'  private_ip = "{private_ip}"\n'
        hcl += f'  associate_public_ip_address = {associate_public_ip}\n'
        hcl += f'  {tags}\n'
        
        hcl += '}\n'
    return hcl

# In kết quả ra terminal
hcl_content = generate_hcl(instances)
print(hcl_content)