import os
import time
import paramiko
import platform
import re
import myfunctions

debug = "false"
os_type = "Comware"
subnet = "10.11.204."
#command_comware = "system-view\nlldp global tlv-enable basic-tlv management-address-tlv interface Vlan-interface 204\nsave force\n" 
#command_aoscx = "config term\naruba-central support-mode\nlldp management-ipv4-address " + hostname + "\nwr memory\n"
command_comware = "\n" 
command_aoscx = "\n"

for i in range(2,10):
    hostname = str(subnet) + str(i)
    response = myfunctions.check_ping(hostname, attempts = 1, silent = False)    
    if response :
        pingstatus = "Network Active"
        print (hostname + " active")
        i = 1
        # Try to connect to SW.
        # Retry a few times if it fails.
        flag = "false"
        while True:
            if debug == "true":
                print("Trying to connect to " + hostname + " i=" + str(i))
            try:
                ssh = paramiko.SSHClient()
                ssh.load_system_host_keys()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname, port=22, username="mead", password="IsfedaCsr!")
                print("Connected to SW " + hostname)
                flag = "true"
                break
            except paramiko.AuthenticationException:
                print("Authentication failed when connecting to " + hostname)
                error = "SSH - Authentication failed,"
                i += 1
                flag = "false"
            except:
                print("Could not SSH to " + hostname + " waiting for it to start")
                i += 1
                flag = "false"
            # If we could not connect within time limit
            if i == 2:
                print("Could not connect to host. Giving up")
                error = "SSH - Could not connect to host."
                flag = "false"
                break
        if flag == "true":
            remote_shell = ssh.invoke_shell()
            time.sleep(2)
            remote_shell.send("show version")
            time.sleep(2)
            output = remote_shell.recv(5000).decode('ascii')
            if not re.search("ArubaOS-CX", output):
                # Aruba OS CX 
                first_line = 2
                command = command_aoscx                            
            else:
                # Comware OS
                first_line = 12
                command = command_comware
            remote_shell.send(command)
            time.sleep(3)
            output = remote_shell.recv(5000).decode('ascii')
            mylist = output.split("\r\n")
            print("SW configuration log:\n---------")
            j = 0
            for i in mylist:
                if j > first_line:
                    print(i)
                j += 1
            print("---------")
            print("Disconnected from SW " + hostname)
    else:
        pingstatus = "Network Error"
        print (hostname + " inactive")
