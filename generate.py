# generate.py
import json
from aws_mapping import map_resource

# Đọc JSON
with open("topology.json", "r") as f:
    topology = json.load(f)

# Sinh HCL
hcl = ""
for section in ["networks", "routers", "instances"]:  # Thứ tự: networks -> routers -> instances để đúng phụ thuộc
    if section in topology:
        hcl += "\n".join(map_resource(section, item) for item in topology[section]) + "\n"

# In ra terminal
print(hcl.strip())