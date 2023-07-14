#!/usr/bin/python3
import requests
import json
import sys 
import time
import re
import paramiko
import os.path
import platform
from pathlib import Path

def refresh_my_token(client_id, client_secret, refresh_token):    
    print("Token expired. Trying to refresh it ...", file=sys.stderr)
    #print ("client id: " + client_id + "")
    ref_url = "https://apigw-eucentral3.central.arubanetworks.com/oauth2/token?client_id=" + client_id + "&client_secret=" + client_secret + "&grant_type=refresh_token&refresh_token=" + refresh_token + ""
    ref_headers = {"Content-type": "application/json", "Accept": "application/json"}
    r = requests.post(ref_url, headers=ref_headers)
    if r.status_code == 200:
        #print("Refreshed", file=sys.stderr)
        # Update credentials
        cred_data = json.loads(r.text)
        token = str(cred_data['access_token']) 
        refresh_token = str(cred_data['refresh_token'])
        myreturn = '{ "error": "0", "access_token": "' + token + '", "refresh_token": "' + refresh_token + '" }'
    else:
        myreturn = '{ "error": "' + str(r.status_code) + '" }'
    return myreturn



def list_labels(auth_token):    
    url = "https://apigw-eucentral3.central.arubanetworks.com/central/v1/labels?category_id=1"
    headers = {"Content-type": "application/json", "Accept": "application/json", "Authorization": auth_token}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        myreturn = '{ "error": "' + str(r.status_code) + '" }'
    else:
        myreturn = r.text
    return myreturn



def exec_ap_command(auth_token, serial, command):    
    url = "https://apigw-eucentral3.central.arubanetworks.com/device_management/v1/device/" + serial + "/action/" + command + ""
    headers = {"Content-type": "application/json", "Accept": "application/json", "Authorization": auth_token}
    r = requests.post(url, headers=headers)
    if r.status_code != 200:
        myreturn = '{ "error": "' + str(r.status_code) + '" }'
    else:
        myreturn = r.text
    return myreturn

def get_AP_lldp_neighbor(host, ap_username, ap_password, debug):
    if debug == "true":
        if not os.path.isdir("log"):
            os.mkdir("log")
        logfile = Path("log/" + str(host) + ".log")
        paramiko.util.log_to_file(logfile)
    error = ""
    command = "show ap debug lldp neighbor interface eth0\n"
    print("AP IP address: " + str(host) + "", file=sys.stderr)
    i = 1
    # Try to connect to AP.
    # Retry a few times if it fails.
    while True:
        if debug == "true":
            print("Trying to connect to " + host + " i=" + str(i))
        try:
            ssh = paramiko.SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, port=22, username=ap_username, password=ap_password)
            print("Connected to AP " + host)
            break
        except paramiko.AuthenticationException:
            print("Authentication failed when connecting to " + host)
            error = "SSH - Authentication failed,"
        except:
            print("Could not SSH to " + host + " waiting for it to start")
            i += 1
            time.sleep(2)
        # If we could not connect within time limit
        if i == 3:
            print("Could not connect to host. Giving up")
            error = "SSH - Could not connect to host."
    
    remote_shell = ssh.invoke_shell()
    time.sleep(2)
    remote_shell.send(command)
    time.sleep(4)
    output = remote_shell.recv(5000).decode('ascii')
    mylist = output.split("\r\n")
    remote_hostname = ""
    remote_ip = ""
    remote_int = ""
    for i in mylist:
        if debug == "true":
            print(i)
        myregex = "^\s*Interface description:[a-zA-Z0-9\-\_\s]+,\sID:\s([a-zA-Z0-9\/]+),.*$"
        result = re.search(myregex, i)
        if result:
            remote_int = result.group(1)
        myregex = "Management\s+address\:\s*([0-9\.]+)"
        result = re.search(myregex, i)
        if result:
            remote_ip = result.group(1)
        myregex = "System\sname:\s*([a-zA-Z0-9\-\_]+)"
        result = re.search(myregex, i)
        if result:
            remote_hostname = result.group(1)
    if remote_ip == "" and remote_hostname == "":
        print("ERROR: cannot find remote IP or hostname")
        error = "Cannot find remote IP or hostname"
    myregex = "HPD-SW-NOM-([0-9]{1,3})"
    result = re.search(myregex, remote_hostname)    
    if result:
        sw_os = "Comware"
        if remote_ip ==  "" and result:
            remote_ip = "10.11.205." + result.group(1) 
    else: 
        myregex = "HP-SW-NOM-([0-9]{1,3})"
        result = re.search(myregex, remote_hostname)        
        if result:
            sw_os = "AOS-CX"  
            if remote_ip ==  "" and result:
                remote_ip = "10.11.204." + result.group(1)  
        else:
            error = "Cannot identify switch OS"        
    ssh.close()  
    print("Disconnected from AP " + host)
    # Disconnected from ap
    if error:
        myreturn = '{ "error": "' + error + '" }'
    else:
        myreturn = '{ "remote_ip": "' + str(remote_ip) + '", "remote_hostname": "' + str(remote_hostname) + '", "remote_int": "' + str(remote_int) + '", "sw_os": "' + str(sw_os) + '" }'
    return myreturn



def reconfigure_sw_interface(host, os_type, username, password, interf, debug):
    if debug == "true":
        if not os.path.isdir("log"):
            os.mkdir("log")
        logfile = Path("log/" + str(host) + ".log")
        paramiko.util.log_to_file(logfile)    
    error = ""
    print("SW IP address: " + str(host) + "", file=sys.stderr)
    i = 1
    # Try to connect to SW.
    # Retry a few times if it fails.
    while True:
        if debug == "true":
            print("Trying to connect to " + host + " i=" + str(i))
        try:
            ssh = paramiko.SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, port=22, username=username, password=password)
            print("Connected to SW " + host)
            break
        except paramiko.AuthenticationException:
            print("Authentication failed when connecting to " + host)
            error = "SSH - Authentication failed,"
        except:
            print("Could not SSH to " + host + " waiting for it to start")
            i += 1
            time.sleep(2)
        # If we could not connect within time limit
        if i == 3:
            print("Could not connect to host. Giving up")
            error = "SSH - Could not connect to host."
    
    remote_shell = ssh.invoke_shell()
    time.sleep(2)
    if os_type == "Comware":
        #command = "system-view\nInterface " + interf + "\nport trunk pvid vlan 202\nport trunk permit vlan 202\nundo port trunk permit vlan 1\nexit\nsave force\n"
        first_line = 12
        command = "system-view\nInterface " + interf + "\ndisplay this\nexit\nsave force\n" 
    else:
        #command = "config term\naruba-central support-mode\ninterface " + interf + "\nvlan trunk native 202\nvlan trunk allowed 202\nexit\nwr memory\n"
        first_line = 2
        command = "config term\naruba-central support-mode\ninterface " + interf + "\n show running-config interface " + interf + "\nexit\nwr memory\n"
    remote_shell.send(command)
    time.sleep(4)
    output = remote_shell.recv(5000).decode('ascii')
    mylist = output.split("\r\n")
    remote_hostname = ""
    remote_ip = ""
    remote_int = ""
    print("SW configuration log:\n---------")
    j = 0
    for i in mylist:
        if j > first_line:
            print(i)
        j += 1
    print("---------")
    print("Disconnected from SW " + host)
    return 




def get_apSerial_from_apName(token, ap_name, debug):
	error = ""
	auth_token = "Bearer " + token + ""
	url = "https://apigw-eucentral3.central.arubanetworks.com/monitoring/v2/aps?limit=1000"
	headers = {"Content-type": "application/json", "Accept": "application/json", "Authorization": auth_token}
	r = requests.get(url, headers=headers)
	if debug == "true":
		print("Status code: " + str(r.status_code) + "")
	
	if r.status_code != 200:
		error = "Failed to get APs list."
		if r.status_code == 401:
			error = "Token is expired. Refresh it."
		else:
			error = "ERROR: Generic error. Status code: " + str(r.status_code)
	else:
	    json_obj = json.loads(r.text)
	    num = json_obj['count']
	    if debug == "true": 
	    	print('Number of APs: ' + str(num))
	    myaps = json_obj['aps']
	    ap_serial = ""
	    for x in range(0, num):
	    	if str(myaps[x]['name']) == ap_name:
	    		ap_serial = str(myaps[x]['serial'])
	    		break
	    if ap_serial == "":
	    	error = "AP not found."
	    else:
	    	if debug == "true":
	    		print("AP found. Serial: " + ap_serial + "")
	if error:
		myreturn = '{ "error": "' + error + '" }'
	else:
		myreturn = '{ "ap_serial": "' + str(ap_serial) + '" }'
	return myreturn
 


def check_ping(hostname, attempts = 1, silent = False):
    parameter = '-n' if platform.system().lower()=='windows' else '-c'
    filter = ' | findstr /i "TTL"' if platform.system().lower()=='windows' else ' | grep "ttl"'
    if (silent):
        silent = ' > NUL' if platform.system().lower()=='windows' else ' >/dev/null'
    else:
        silent = ''
    response = os.system('ping ' + parameter + ' ' + str(attempts) + ' ' + hostname + filter + silent)
    if response == 0:
        return True
    else:
        return False

