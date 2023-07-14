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
    print("APs serials separated by comma without spaces. Es. CNMVK00001,CNMVK00002")
    sys.exit(1)

ap_serials = sys.argv[1]
grp_name = sys.argv[2]

if not re.search("^[A-Z0-9\,]+$", ap_serials):
    print("ERROR: list of serials expeted")
    sys.exit(1)

if not re.search("^[a-zA-Z0-9\-\_]+$", grp_name):
    print("ERROR: group name expeted")
    sys.exit(1)

# Verify the serials:
# - get the list of APs using an API call 
ap_list = ap_serials.split(",")
auth_token = "Bearer " + token + ""
url = "https://apigw-eucentral3.central.arubanetworks.com/monitoring/v2/aps?limit=1000"
headers = {"Content-type": "application/json", "Accept": "application/json", "Authorization": auth_token}
r = requests.get(url, headers=headers)
if debug == "true":
    print("Status code: " + str(r.status_code) + "")

if r.status_code != 200:
    print("Failed to get APs list.")
    if r.status_code == 401:
        print("Token is expired. Refresh it.")
        sys.exit(1)
    else:
        print("ERROR. Status code: " + r.status_code)
        sys.exit(2)

# - verify that AP are in the list
json_obj = json.loads(r.text)
ap_num = json_obj['count']
if debug == "true": 
    print('Number of APs: ' + str(ap_num))
myaps = json_obj['aps']
ap_serial = []
for x in range(0, ap_num):
    for y in ap_list:
        if str(myaps[x]['serial']) == y:
            ap_serial.append(str(myaps[x]['serial']))
            break
if len(ap_serial) == 0:
    print("APs not found. Exit.")
    sys.exit(2)

if len(ap_list) != len(ap_serial):
    print("Given serials: " + str(ap_serials) + "")
    print("Existing APs serials: " + str(ap_serial) + "")
else:
    print("All AP serials found")

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
