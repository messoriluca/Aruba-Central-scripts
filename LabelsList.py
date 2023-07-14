#!/usr/bin/python3
import requests
import json
import sys 
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

auth_token = "Bearer " + token + ""
url = "https://apigw-eucentral3.central.arubanetworks.com/central/v1/labels?category_id=1"
headers = {"Content-type": "application/json", "Accept": "application/json", "Authorization": auth_token}
r = requests.get(url, headers=headers)
print("Status code: " + str(r.status_code) + "", file=sys.stderr)

if r.status_code != 200:
    print("Failed to list label. Status code: " + str(r.status_code), file=sys.stderr)
    if r.status_code == 401:
        print("Token is expired. Refresh it.")
        sys.exit(1)
    else:
        print("ERROR: Generic", file=sys.stderr)
        sys.exit(2)

if debug == "true": 
	print("Labels: " + r.text, file=sys.stderr)
print("List label")
json_obj = json.loads(r.text)
num = json_obj['count']
print('Number of labels: ' + str(num))
for x in range(0, num):
    print(str(json_obj['labels'][x]['label_id']) + " " + str(json_obj['labels'][x]['label_name']))
