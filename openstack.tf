provider "openstack" {
  # Add provider configuration here
}

resource "openstack_networking_network_v2" "net2" {
  name = "net2"
  admin_state_up = "true"
}
resource "openstack_networking_subnet_v2" "net2" {
  name = "net2"
  network_id = openstack_networking_network_v2.net2.id
  cidr = "192.168.2.0/24"
  gateway_ip = "192.168.2.1"
  enable_dhcp = false
}
resource "openstack_networking_network_v2" "net1" {
  name = "net1"
  admin_state_up = "true"
}
resource "openstack_networking_subnet_v2" "net1" {
  name = "net1"
  network_id = openstack_networking_network_v2.net1.id
  cidr = "192.168.1.0/24"
  gateway_ip = "192.168.1.1"
  enable_dhcp = false
}
resource "openstack_networking_router_v2" "R1" {
  name = "R1"
  admin_state_up = "true"
  external_network_id = "external-net-id"
}
resource "openstack_networking_router_interface_v2" "R1_int1" {
  router_id = openstack_networking_router_v2.R1.id
  subnet_id = openstack_networking_subnet_v2.net2.id
}
resource "openstack_networking_router_interface_v2" "R1_int2" {
  router_id = openstack_networking_router_v2.R1.id
  subnet_id = openstack_networking_subnet_v2.net1.id
}
resource "openstack_compute_instance_v2" "vm1" {
  name = "vm1"
  image_name = "ubuntu-20.04"
  flavor_name = "m1.small"
  key_pair = "my-key"
  security_groups = ["default"]
  network {
    name = "net1"
    fixed_ip_v4 = "192.168.1.10"
  }
}
resource "openstack_compute_instance_v2" "s2" {
  name = "s2"
  image_name = "ubuntu-20.04-focal"
  flavor_name = "m1.medium"
  key_pair = "my-key"
  security_groups = ["default"]
  network {
    name = "net2"
    fixed_ip_v4 = "192.168.2.10"
  }
}