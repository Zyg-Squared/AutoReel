#!/usr/bin/python3
###########
### File Name : phish_api_test.py
### Usage : python3 ./scripts/phish_api_test.py 
### Prerequiste Info : Use this script after the AutoReel prequisties are complete and phish_setup.py has been run successfully
### Description : Handy script for running API Tests against GoPhish, not needed for Instance Setup/Configuration
### 
############
import requests
import simplejson as json
    
    
    
############################ Creates SQS Message to Trigger either the phish_create_instances or phish_delete_instances ############################    
domain_prefix = "www-example-login"
domain = "the-domain-you-bought.com"
port = "3333"
path = "/api/users/"
userid = "1"
api_key = "API_KEY_HERE"
url = "https://"+domain_prefix+"."+domain+":"+port+path+userid+"?api_key="+api_key

headers = {"Content-Type": "application/json"}

try:
    json_change = {
        "username": "admin",
        "role": "admin",
        "password": "new_admin_password!9"
    }
    api_data = json.dumps(json_change)


    response = requests.put(url, data=api_data, headers=headers)
    #response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print("Admin password updated")
    else:
        print("Failed:"+str(response))
        print(response.text)

except Exception as ex:
    print("Exception:"+str(ex)+" \n\nResponse:"+response+"\n\n")    
############################ - End Function