#đây là dictionaryt chứa một list các dictionary khác
instances = {'instances': [{'name': 'vm1', 'image': 'ubuntu-server', 'cpu': 2, 'ram': 2, 'disk': 30, 'networks': [{'name': 'net1', 'ip': '192.168.1.10'}]}, {'name': 's2', 'image': 'ubuntu-server-focal', 'cpu': 2, 'ram': 4, 'disk': 40, 'networks': [{'name': 'net2', 'ip': '192.168.2.10'}]}]}
# Access the first instance in the list
first_instance = instances['instances'][0]
print(first_instance)  # vm1