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
ap_username = str(cred_data['ap_username'])
ap_password = str(cred_data['ap_password'])
sw_username = str(cred_data['sw_username'])
sw_password = str(cred_data['sw_password'])
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
if r.status_code == 200:
    print("Token is valid. Exit.")
    sys.exit(0)

# Token expired ... trying to refresh
print ("Trying to refresh the token")
json_data = myfunctions.refresh_my_token(client_id, client_secret, refresh_token)
if debug == "true":
    print("New token: " + json_data)
cred_data = json.loads(json_data)
myerror = str(cred_data['error'])
if  myerror == "0":
    print("Refreshed")
    # Update credentials
    token = str(cred_data['access_token']) 
    refresh_token = str(cred_data['refresh_token'])
    # Update credential file
    cred_file = open('input_credentials.json', 'w')
    json_data = '{ "client_id": "' + client_id + '", "client_secret": "' + client_secret + '", "access_token": "' + token + '", "refresh_token": "' + refresh_token + '", '
    json_data = json_data + ' "ap_username": "' + ap_username + '", "ap_password": "' + ap_password + '", "sw_username": "' + sw_username + '", "sw_password": "' + sw_password + '" }'
    if debug == "true": 
        print(json_data)
    json_object = json.loads(json_data)
    json.dump(json_object, cred_file, indent=4)
    cred_file.close()
    print("Token refreshed")
else:
    print("ERROR: Refresh failed")
    sys.exit(3)

