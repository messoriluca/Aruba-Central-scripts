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

if len(sys.argv) != 2:
    print("ERROR: wrong number of parameters")
    sys.exit(1)
#Label to delete
mylabel_name = sys.argv[1]

if re.search("^[0-9]+$", mylabel_name):
    print("ERROR: expeted label name (not ID)")
    sys.exit(1)

auth_token = "Bearer " + token + ""
json_data = myfunctions.list_labels(auth_token)
json_object = json.loads(json_data)
if "error" in json_object:
    if str(json_object['error']) == "401":
        print("Unauthorized access. Token must be refreshed.")
        sys.exit(2)
    else:
        print("Error getting label list. Error code: " + str(json_object['error']))
        sys.exit(3)

if json_object['count'] == 0:
    print("No label defined. Exit.")
    sys.exit(4)

arr_labels = json_object['labels']
for mylabel in arr_labels:
    if str(mylabel['label_name']) == mylabel_name:
        mylabel_id = str(mylabel['label_id'])

url = "https://apigw-eucentral3.central.arubanetworks.com/central/v1/labels/" + mylabel_id + ""
headers = {"Content-type": "application/json", "Accept": "application/json", "Authorization": auth_token}
r = requests.delete(url, headers=headers)

if r.status_code !=200:
    print("Failed to delete label. Status code: " + str(r.status_code), file=sys.stderr)
    sys.exit(5)

print("Successfuly deleted label")
