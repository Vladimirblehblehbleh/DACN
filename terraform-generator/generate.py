import json
import uuid
import sys
import os
import shutil
from datetime import datetime
from validate_json import validate_topology_file
import terraform_templates as tf_tpl
import subprocess

class TerraformGenerator:
    def __init__(self, provider, num_copies=1):
        self.provider = provider.lower()
        self.num_copies = num_copies
        self.topology = None
        self.validated_resources = None
        self.run()

    def run(self):
        print(f"\n=== Start generating files for {self.provider.upper()} ===")
        if not self.load_and_validate_topology():
            sys.exit(1)
        self.validate_resources()
        self.generate_configs()
        print("\n=== COMPLETED ===")

    def load_and_validate_topology(self):
        # Validate topology.json against schema and IP/CIDR logic
        print("\nChecking topology.json...")
        is_valid, errors = validate_topology_file("topology.json", self.provider)
        if not is_valid:
            print("\n=== VALIDATION ERROR ===")
            for error in errors:
                print(f"- {error}")
            return False
        try:
            with open("topology.json", "r") as f:
                self.topology = json.load(f)
            print("Topology file is valid")
            return True
        except Exception as e:
            print(f"\nError reading file: {str(e)}")
            return False

    def validate_resources(self):
        # Validate cloud-specific resource names (e.g. image, flavor, AMI)
        if self.provider == "aws":
            from validate_aws import AWSUtils
            self.validated_resources = AWSUtils().validate_resources(self.topology)
        elif self.provider == "openstack":
            from validate_openstack import validate_resources
            self.validated_resources = validate_resources(self.topology)
            if not self.validated_resources.get('valid', False):
                print("\n=== RESOURCE VALIDATION FAILED ===")
                for msg in self.validated_resources.get('messages', []):
                    print(f"- {msg}")
                sys.exit(1)


    def build_validated_map(self, suffix=""):
        # Build a dictionary of instance names mapped to validated resource info
        validated_map = {}
        if self.validated_resources and 'instances' in self.validated_resources:
            for inst in self.validated_resources['instances']:
                orig_name = inst['original_spec']['name']
                full_name = f"{orig_name}_{suffix}" if suffix else orig_name
                if self.provider == "openstack":
                    validated_map[full_name] = {
                        "image": inst['image'],
                        "flavor": inst['flavor']
                    }
                elif self.provider == "aws":
                    validated_map[full_name] = {
                        "ami": inst['ami'],
                        "instance_type": inst['instance_type']
                    }
        return validated_map

    def generate_config_content(self, validated_map):
        # Generate main.tf content depending on provider
        if self.provider == "aws":
            return (
                tf_tpl.aws_terraform_block() + "\n" +
                tf_tpl.aws_provider_block() + "\n" +
                tf_tpl.aws_locals_block() + "\n" +
                tf_tpl.aws_network_module_block() + "\n" +
                tf_tpl.aws_security_group_block() + "\n" +
                tf_tpl.aws_instance_module_block(validated_map) + "\n" +
                tf_tpl.aws_bastion_block()
            )
        elif self.provider == "openstack":
            return (
                tf_tpl.os_terraform_block() + "\n" +
                tf_tpl.os_provider_block() + "\n" +
                tf_tpl.os_locals_block() + "\n" +
                tf_tpl.os_network_module_block() + "\n" +
                tf_tpl.os_instance_module_block(validated_map)
            )

    def generate_configs(self):
        # Create N Terraform folders with modified topology and config
        with open('topology.json', 'r') as f:
            original_topology = json.load(f)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        main_folder = os.path.join("../terraform-projects", f"{self.provider}_{timestamp}")
        os.makedirs(main_folder, exist_ok=True)

        if os.path.exists("run_terraform.py"):
            shutil.copy("run_terraform.py", os.path.join(main_folder, "run_terraform.py"))

        for _ in range(self.num_copies):
            suffix = str(uuid.uuid4())[:6]
            dir_name = f"{self.provider}_{suffix}"
            full_path = os.path.join(main_folder, dir_name)
            self.create_provider_directory(full_path, original_topology, suffix)

        # Run `terraform apply` after generating all folders
        subprocess.run(
            ["python3", "run_terraform.py", "apply"],
            cwd=main_folder,
            check=True
        )

    def create_provider_directory(self, dir_path, original_topology, suffix):
        # Copy template folder, modify topology, write main.tf
        try:
            shutil.copytree(self.provider, dir_path)
            modified_topology = self.modify_topology(original_topology, suffix)
            with open(os.path.join(dir_path, 'topology.json'), 'w') as f:
                json.dump(modified_topology, f, indent=2)
            validated_map = self.build_validated_map(suffix)
            config_content = self.generate_config_content(validated_map)
            with open(os.path.join(dir_path, 'main.tf'), 'w', encoding='utf-8') as f:
                f.write(config_content)
            print(f" Successfully created: {dir_path}")
        except Exception as e:
            print(f" Error creating {dir_path}: {str(e)}")
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)

    def modify_topology(self, topology, suffix):
        # Add suffix to all names in topology (instance, network, router)
        modified = json.loads(json.dumps(topology))
        for inst in modified.get('instances', []):
            inst['name'] = f"{inst['name']}_{suffix}"
            for net in inst.get('networks', []):
                net['name'] = f"{net['name']}_{suffix}"

        for net in modified.get('networks', []):
            net['name'] = f"{net['name']}_{suffix}"

        for router in modified.get('routers', []):
            router['name'] = f"{router['name']}_{suffix}"
            for net in router.get('networks', []):
                net['name'] = f"{net['name']}_{suffix}"
        return modified


# -------------------------- Entry Point --------------------------
if __name__ == "__main__":
    print("""
========================
TERRAFORM CONFIG GENERATOR
========================""")

    if len(sys.argv) < 2 or sys.argv[1].lower() not in ["aws", "openstack"]:
        print("\n[ERROR] Usage: python3 generate.py [aws|openstack] [num_copies]")
        sys.exit(1)

    provider = sys.argv[1].lower()
    num_copies = 1

    if len(sys.argv) > 2:
        try:
            num_copies = int(sys.argv[2])
            if num_copies < 1:
                raise ValueError
        except ValueError:
            print("\n[ERROR] Number of copies must be a positive integer")
            sys.exit(1)

    try:
        TerraformGenerator(provider, num_copies)
    except KeyboardInterrupt:
        print("\n=== PROGRAM TERMINATED ===")
    except Exception as e:
        print(f"\n=== UNEXPECTED ERROR ===\n{str(e)}")
        sys.exit(1)
