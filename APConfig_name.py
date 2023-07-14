import requests
import json
import sys 
import re
import myfunctions

debug = "false"

# Get credential from json file
cred_file = open('input_credentials.json')
cred_data = json.load(cred_file)
client_id = str(cred_data['client_id'])
client_secret = str(cred_data['client_secret'])
token = str(cred_data['access_token']) 
refresh_token = str(cred_data['refresh_token'])
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

ap_name = sys.argv[1]
print ("Reconfigure AP: "+str(sys.argv[1])+"")

if not re.search("^[a-zA-Z0-9\-\_\/]+$", ap_name):
    print("ERROR: expeted AP name")
    sys.exit(1)

# Get AP serial from AP name
data_obj = myfunctions.get_apSerial_from_apName(token, ap_name, debug)
json_obj = json.loads(data_obj)
if "error" in json_obj:
	print(str(json_obj['error']))
	print("Abort")
	sys.exit(2)
ap_serial = str(json_obj['ap_serial'])
print("AP serial: " + ap_serial)

# Get AP configuration
auth_token = "Bearer " + token + ""
url = "https://apigw-eucentral3.central.arubanetworks.com/configuration/v1/ap_settings_cli/" + ap_serial
headers = {"Content-type": "application/json", "Accept": "text/plain", "Authorization": auth_token}
r = requests.get(url, headers=headers)
if r.status_code !=200:
    print("Failed to get AP configuration")
    print("Error code: " + str(r.status_code) )
    sys.exit(2)

if debug == "true":
    print(r.text)
#N.B.: r.text is not in json format, its an array of string

# Modify the config: swarm-mode and uplink-vlan
newdata = r.text.replace("[","")
newdata = newdata.replace("]","")
newdata = newdata.split("\n")
myarr = []
data = "{ \"clis\": [ "
for x in newdata:
    if x != "" and x != ",":
        x = str(x).replace("swarm-mode cluster", "swarm-mode standalone")
        x = str(x).replace("uplink-vlan 202", "uplink-vlan 1")
        data = data + x
        #print("-->" + data + "\n")
data = data + " ] }"
if debug == "true":
    print(data)

# Post the modified configuration
data = json.loads(data)
url = "https://apigw-eucentral3.central.arubanetworks.com/configuration/v1/ap_settings_cli/" + ap_serial
headers = {"Content-type": "application/json", "Accept": "text/plain", "Authorization": auth_token}
r = requests.post(url, data=json.dumps(data), headers=headers)
if r.status_code !=200:
    print("Failed to reconfigure AP")
    sys.exit(3)

print("Succesfully reconfigured the AP. \nWait for the configuration to be pushed and reboot it.")
