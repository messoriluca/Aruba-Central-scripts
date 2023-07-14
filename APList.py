#!/usr/bin/python3
import requests
import json
import sys
import os
from tabulate import tabulate
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
url = "https://apigw-eucentral3.central.arubanetworks.com/monitoring/v2/aps?limit=1000"
headers = {"Content-type": "application/json", "Accept": "application/json", "Authorization": auth_token}
r = requests.get(url, headers=headers)
if debug:
    print("Status code: " + str(r.status_code) + "")

if r.status_code != 200:
    print("Failed to get APs list.")
    if r.status_code == 401:
        print("Token is expired. Refresh it.")
        sys.exit(1)
    else:
        print("ERROR: Generic")
        sys.exit(2)

current_working_directory = os.getcwd()
appdata_path = current_working_directory + '/appdata/'
isExist = os.path.exists(appdata_path)
if debug == "true":
    print("Is appdata directory existing? " + str(isExist))
if not isExist:
    os.makedirs(appdata_path)
    if debug:
        print("Appdata directory created.")

aps_data_file = appdata_path + "aps_list.csv"
json_obj = json.loads(r.text)
num = json_obj['count']
print('Number of APs: ' + str(num))
myaps = json_obj['aps']
aps_file = open(aps_data_file, 'w')
print("Name,Serial,AP address,status", file=aps_file)
data = []
for x in range(0, num):
    if debug == "true":
        print(str(myaps[x]['name']) + " " + str(myaps[x]['serial']) + " " + str(myaps[x]['ip_address']) + " " + str(myaps[x]['status']) )
    print(str(myaps[x]['name']) + "," + str(myaps[x]['serial']) + "," + str(myaps[x]['ip_address']) + "," + str(myaps[x]['status']), file=aps_file)
    data.append([ str(x + 1),str(myaps[x]['name']), str(myaps[x]['serial']), str(myaps[x]['group_name']), str(myaps[x]['ip_address']), str(myaps[x]['status']) ])
aps_file.close()
headers = [ "Num","AP Name","Serial","Current group","IP address","Status" ]
print(tabulate(data, headers, tablefmt='orgtbl'))

aps_data_file = appdata_path + "aps_list.json"
aps_file = open(aps_data_file, 'w')
json.dump(myaps, aps_file, indent=4)
aps_file.close()
print("APs list file saved")
