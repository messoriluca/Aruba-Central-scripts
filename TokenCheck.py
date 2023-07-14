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
    print(cred_data)
    print("client ID: " + client_id)
    print("client secret: " + client_secret)
    print("Token: " + token)
    print("Refresh token: " + refresh_token)
cred_file.close()

auth_token = "Bearer " + token + ""
url = "https://apigw-eucentral3.central.arubanetworks.com/central/v2/sites?calculate_total=true"
headers = {"Content-type": "application/json", "Accept": "application/json", "Authorization": auth_token}
r = requests.get(url, headers=headers)

if debug == "true": 
    print("Status code: " + str(r.status_code) + "")

if r.status_code == 200:
    print("Token is valid.")
else:
    if r.status_code == 401:
        print("Unauthorized access. Token must be refreshed.")
    else:
        print("Error code: " + str(r.status_code) + "") 
