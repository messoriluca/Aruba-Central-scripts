import requests
import json
import sys 
import myfunctions

debug = "false"

if len(sys.argv) != 2:
    print ("ERRORE: occorre passare una label")
    sys.exit(1)

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

newlabel = sys.argv[1]

auth_token = "Bearer " + token + ""
url = "https://apigw-eucentral3.central.arubanetworks.com/central/v1/labels"
data = { "category_id": 1, "label_name":  newlabel  }
if debug == "true":
    print("New json object: " + str(data))
headers = {"Content-type": "application/json", "Accept": "text/plain", "Authorization": auth_token}
r = requests.post(url, data=json.dumps(data), headers=headers)

if r.status_code !=200:
    print("Failed to create label", file=sys.stderr)
    print("Error code: " + str(r.status_code) )
    sys.exit(1)

print("Successfuly created label")
if debug == "true":
    json_obj = json.loads(r.text)
    print('Category id: ', json_obj['category_id'])
    print('Label id: ', json_obj['label_id'])
    print('Label name: ', json_obj['label_name'])
