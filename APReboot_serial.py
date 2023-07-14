import requests
import json
import sys 
import re
import time
#import paramiko 
import myfunctions

debug = "false"

# Get credential from json file
cred_file = open('input_credentials.json')
cred_data = json.load(cred_file)
client_id = str(cred_data['client_id'])
client_secret = str(cred_data['client_secret'])
token = str(cred_data['access_token']) 
refresh_token = str(cred_data['refresh_token'])
ap_username =  str(cred_data['ap_username'])
ap_password =  str(cred_data['ap_password'])
sw_username =  str(cred_data['sw_username'])
sw_password =  str(cred_data['sw_password'])
if debug == "true": 
    print(cred_data)
    print("client ID: " + client_id)
    print("client secret: " + client_secret)
    print("Token: " + token)
    print("Refresh token: " + refresh_token)
cred_file.close()

# Verify parameters
if len(sys.argv) != 2:
    print("ERROR: wrong number of parameters")
    sys.exit(1)
ap_serial = sys.argv[1]

if not re.search("^CN[0-9A-Z]{8}$", ap_serial):
    print("ERROR: expeted AP serial (not name)")
    sys.exit(1)

# Get AP IP address
auth_token = "Bearer " + token + ""
url = "https://apigw-eucentral3.central.arubanetworks.com/monitoring/v1/aps/" + ap_serial
headers = {"Content-type": "application/json", "Accept": "text/plain", "Authorization": auth_token}
r = requests.get(url, headers=headers)

if str(r.status_code) != "200":
    if str(r.status_code) == "401":
        print("Unauthorized access. Token must be refreshed.")
        sys.exit(2)
    else:
        print("Error getting AP details: " + str(r.status_code))
        print("Abort.")
        sys.exit(3)
json_obj = json.loads(r.text)
host = json_obj['ip_address']

# Get LLDP neighbor info from AP --> switch 
json_data = myfunctions.get_AP_lldp_neighbor(host, ap_username, ap_password, debug)
json_obj = json.loads(json_data)
if "error" in json_obj:
    print(json_obj['error'])
    print("Abort.")
    sys.exit(4)
# LLDP neighbor found
sw_ip = str(json_obj['remote_ip'])
sw_hostname = str(json_obj['remote_hostname'])
sw_int = str(json_obj['remote_int'])
sw_os = str(json_obj['sw_os'])
print("    Remote IP: " + sw_ip)
print("    Remote hostname: " + sw_hostname)
print("    Remote int: " + sw_int)
print("    Remote OS: " + sw_os)

# Reboot AP 
print("Rebooting AP")
url = "https://apigw-eucentral3.central.arubanetworks.com/device_management/v1/device/" + ap_serial + "/action/" + "reboot"
headers = {"Content-type": "application/json", "Accept": "text/plain", "Authorization": auth_token}
r = requests.post(url, headers=headers)
if str(r.status_code) != "200":
    if str(r.status_code) == "401":
        print("Unauthorized access. Token must be refreshed.")
        sys.exit(5)
    else:
        print("Error rebooting AP: " + str(r.status_code))
        sys.exit(6)
print("AP Rebooted")

# Waiting for rebooting command has effect
time.sleep(10)

# Reconfigure switch port on wich AP is connected
myfunctions.reconfigure_sw_interface(sw_ip, sw_os, sw_username, sw_password, sw_int, debug)

sys.exit(0)
