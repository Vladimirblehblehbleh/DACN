# openstack_mapping.py

image_to_name = {
    "ubuntu-server": "ubuntu-20.04",
    "ubuntu-server-focal": "ubuntu-20.04-focal"
}

cpu_ram_to_flavor = {
    (2, 2): "m1.small",
    (2, 4): "m1.medium"
}

templates = {
    "instances": '''resource "openstack_compute_instance_v2" "{name}" {{
  name = "{name}"
  image_name = "{image_name}"
  flavor_name = "{flavor_name}"
  key_pair = "{key_pair}"
  security_groups = ["{security_groups}"]
  network {{
    name = "{network_name}"
    fixed_ip_v4 = "{fixed_ip}"
  }}
}}''',
    "networks": '''resource "openstack_networking_network_v2" "{name}" {{
  name = "{name}"
  admin_state_up = "true"
}}
resource "openstack_networking_subnet_v2" "{name}" {{
  name = "{name}"
  network_id = openstack_networking_network_v2.{name}.id
  cidr = "{cidr}"
  gateway_ip = "{gateway_ip}"
  enable_dhcp = {enable_dhcp}
}}''',
    "routers": '''resource "openstack_networking_router_v2" "{name}" {{
  name = "{name}"
  admin_state_up = "true"
  external_network_id = "{external_network_id}"
}}
resource "openstack_networking_router_interface_v2" "{name}_int1" {{
  router_id = openstack_networking_router_v2.{name}.id
  subnet_id = openstack_networking_subnet_v2.{network1_name}.id
}}
resource "openstack_networking_router_interface_v2" "{name}_int2" {{
  router_id = openstack_networking_router_v2.{name}.id
  subnet_id = openstack_networking_subnet_v2.{network2_name}.id
}}'''
}

def map_resource(section, item):
    if section == "instances":
        data = {
            "name": item["name"],
            "image_name": image_to_name.get(item.get("image", "ubuntu-server"), "ubuntu-default"),
            "flavor_name": cpu_ram_to_flavor.get((item.get("cpu", 1), item.get("ram", 1)), "m1.tiny"),
            "key_pair": item.get("key_pair", "my-key"),
            "security_groups": item.get("security_groups", "default"),
            "network_name": item["networks"][0]["name"] if "networks" in item and item["networks"] else "default",
            "fixed_ip": item["networks"][0]["ip"] if "networks" in item and item["networks"] else "10.0.0.10"
        }
    elif section == "networks":
        data = {
            "name": item["name"],
            "cidr": item["cidr"],
            "gateway_ip": item.get("gateway_ip", "auto"),
            "enable_dhcp": "true" if item.get("enable_dhcp", False) else "false"
        }
    elif section == "routers":
        data = {
            "name": item["name"],
            "external_network_id": "external-net-id" if item.get("external", False) else "",
            "network1_name": item["networks"][0]["name"] if "networks" in item and len(item["networks"]) > 0 else "default",
            "network2_name": item["networks"][1]["name"] if "networks" in item and len(item["networks"]) > 1 else "default"
        }
    return templates[section].format(**data)