# generate.py
import json
import sys
from aws_mapping import map_resource as map_aws
from openstack_mapping import map_resource as map_openstack

# Chọn provider từ tham số dòng lệnh
if len(sys.argv) != 2 or sys.argv[1] not in ["1", "2"]:
    print("Usage: python generate.py <provider> (1 for AWS, 2 for OpenStack)")
    sys.exit(1)

provider = "aws" if sys.argv[1] == "1" else "openstack"
map_func = map_aws if provider == "aws" else map_openstack
output_file = f"{provider}.tf"

# Đọc JSON
with open("topology.json", "r") as f:
    topology = json.load(f)

# Sinh HCL
hcl = f'provider "{provider}" {{\n  # Add provider configuration here\n}}\n\n'
for section in ["networks", "routers", "instances"]:  # Thứ tự phụ thuộc
    if section in topology:
        hcl += "\n".join(map_func(section, item) for item in topology[section]) + "\n"

# In ra terminal và ghi file
print(hcl.strip())
with open(output_file, "w") as f:
    f.write(hcl.strip())
print(f"Đã tạo {output_file}")