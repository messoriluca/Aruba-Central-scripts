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
if len(sys.argv) != 3:
    print("ERROR: wrong number of parameters")
    print("" + sys.argv[0] + " <AP serials> <Group Name>")
    print("APs serials separated by comma without spaces. Es. AP001/1,AO002/3")
    sys.exit(1)

ap_names = sys.argv[1]
grp_name = sys.argv[2]

if not re.search("^[a-zA-Z0-9\-\_\/\,]+$", ap_names):
    print("ERROR: list of AP names expeted")
    sys.exit(1)

if not re.search("^[a-zA-Z0-9\-\_]+$", grp_name):
    print("ERROR: group name expeted")
    sys.exit(1)

print("AP names: " + ap_names)
# Get AP serials from AP name
ap_list = ap_names.split(",")
ap_serials = ""
for ap_name in ap_list:
    if debug == "true":
        print("AP name: " + ap_name)
    data_obj = myfunctions.get_apSerial_from_apName(token, ap_name, debug)
    json_obj = json.loads(data_obj)
    if "error" in json_obj:
        print(ap_name + "- " + str(json_obj['error']))
        if json_obj['error'] == "Token is expired. Refresh it.":
            print("Abort")
            sys.exit(2)
    else:
        if ap_serials == "":
            ap_serials = str(json_obj['ap_serial'])
        else:
            ap_serials = ap_serials + "," + str(json_obj['ap_serial'])

if debug == "true":
    print("AP serials: " + str(ap_serials))

ap_serial = []
for x in ap_serials.split(","):
    ap_serial.append(x)

if len(ap_serial) == 0:
    print("APs not found. Exit.")
    sys.exit(2)

print("Existing APs serials: " + str(ap_serial) + "")

# Move AP using API
print("Trying to move APs")
auth_token = "Bearer " + token + ""
url = "https://apigw-eucentral3.central.arubanetworks.com/configuration/v1/devices/move" 
headers = {"Content-type": "application/json", "Accept": "application/json", "Authorization": auth_token}
data = { "group": grp_name, "serials":  ap_serial  }
r = requests.post(url, data=json.dumps(data), headers=headers)

if r.status_code == 200:
    print("APs moved")
else:
    print("Failed to move APs")
    sys.exit(3)
