# aws_mapping.py

# Bảng tra cứu AMI
image_to_ami = {
    "ubuntu-server": "ami-0c55b159cbfafe1f0",      # Ubuntu 20.04 us-east-1
    "ubuntu-server-focal": "ami-042e828730a8e686c"  # Ubuntu 20.04 Focal us-east-1
}

# Bảng tra cứu instance_type từ cpu/ram
cpu_ram_to_instance_type = {
    (2, 2): "t2.small",  # 2 CPU, 2GB RAM
    (2, 4): "t2.medium"  # 2 CPU, 4GB RAM
}