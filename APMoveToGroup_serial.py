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
    print(cred_data, file=sys.stderr)
    print("client ID: " + client_id, file=sys.stderr)
    print("client secret: " + client_secret, file=sys.stderr)
    print("Token: " + token, file=sys.stderr)
    print("Refresh token: " + refresh_token, file=sys.stderr)
cred_file.close()

# Verify parameters
if len(sys.argv) != 3:
    print("ERROR: wrong number of parameters")
    print("" + sys.argv[0] + " <AP serial> <Group Name>")
    sys.exit(1)
if not re.search("^CN[A-Z0-9]{8}$", ap_serial):
    print("ERROR: serial number expeted")
    sys.exit(1)
if not re.search("^[a-zA-Z0-9\-\_]+$", grp_name):
    print("ERROR: group name expeted")
    sys.exit(1)

ap_serial = sys.argv[1]
grp_name = sys.argv[2]

# API call to move AP to group
auth_token = "Bearer " + token + ""
url = "https://apigw-eucentral3.central.arubanetworks.com/configuration/v1/devices/move" 
headers = {"Content-type": "application/json", "Accept": "application/json", "Authorization": auth_token}
data = { "group": grp_name, "serials":  [ap_serial]  }
r = requests.post(url, data=json.dumps(data), headers=headers)

if r.status_code == 200:
    print("AP Moved")
else:
    if r.status_code == 401:
        print("Unauthorized access. Token must be refreshed.")
        sys.exit(2)
    else:
        print("Failed to move AP", file=sys.stderr)
        sys.exit(3)
