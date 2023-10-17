import subprocess
import re
from pyzabbix import ZabbixMetric, ZabbixSender

pattern_server = r'\nServer\s*=\s*([a-zA-Z0-9.-]+)'
pattern_hostname = r'\nHostname\s*=\s*([a-zA-Z0-9.-]+)'

key = "apt.number_of_upgradable_packages"


try:
    zabbix_agent = subprocess.check_output("apt list --installed | grep zabbix-agent", shell=True, universal_newlines=True)
    if "zabbix-agent2" in zabbix_agent:
        config_file = "/etc/zabbix/zabbix_agent2.conf"
    else:
        config_file = "/etc/zabbix/zabbix_agentd.conf"
except:
    print("No zabbix agent found.")
    exit(1)


file = open(config_file, "r")
config = file.read()

server_ip = re.search(pattern_server, config)
if server_ip:
    server_ip = server_ip.group(1)
else:
    exit(1)

hostname = re.search(pattern_hostname, config)
if hostname:
    hostname = hostname.group(1)
else:
    exit(1)

output = subprocess.check_output("apt list --upgradable", shell=True, universal_newlines=True)
number_of_packages = output.count("\n") -1

metrics = []
m = ZabbixMetric(hostname, key, number_of_packages)
metrics.append(m)
zbx = ZabbixSender(server_ip)
zbx.send(metrics)