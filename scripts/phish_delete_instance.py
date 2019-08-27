#!/usr/bin/python3
###########
### File Name : phish_delete_instance.py
### Usage : python3 ./scripts/phish_delete_instance.py 
### Prerequiste Info : Use this script in the Lambda created by phish_setup.py and after AutoReel prequisties are complete 
### Description : Deletes theLightsail instance, detaches static IPs, closes ports, deletes IAM credentials, removes everything needed for automated campaign building, reporting, and scheduling related to the campaign/instance.
### 
############

import boto3
import time
import json
import secrets
import string
import botocore
from botocore.errorfactory import ClientError
from collections import OrderedDict



############################ Gets AutoReel Campaign JSON Data ############################
def get_phish_campaign_configs(bucketname="",campaignid=""):
    phish_campaign_config_s3_name  =   "campaigns/"+str(campaignid)+".json"
    phish_campaign_config_local_name   = "/tmp/"+str(campaignid)+".json"
    phish_campaign_config_exists = 0   
    s3 = boto3.client('s3')
    try:
        s3.head_object(Bucket=bucketname, Key=phish_campaign_config_s3_name)
        phish_campaign_config_exists = 1
    except ClientError:
        print("not found - campaign config")
        pass
    if phish_campaign_config_exists == 1:
        s3.download_file(bucketname, phish_campaign_config_s3_name, phish_campaign_config_local_name)    
        with open(phish_campaign_config_local_name) as config_file:
            configs = json.load(config_file, object_pairs_hook=OrderedDict)     
        return configs
    else:
        return "failed" 
############################ - End Function


        
############################ Gets AutoReel Template JSON Data ############################
def get_phish_template_configs(bucketname="",template=""):
    phish_template_config_s3_name  =   "templates/"+str(template)+"/"+str(template)+".json"
    phish_template_config_local_name   = "/tmp/"+str(template)+".json"
    phish_template_config_exists = 0   
    
    print("s3name:"+str(phish_template_config_s3_name))
    print("template:"+str(template))
    
    s3 = boto3.client('s3')
    try:
        s3.head_object(Bucket=bucketname, Key=phish_template_config_s3_name)
        phish_template_config_exists = 1
    except ClientError:
        print("not found - template config")
        pass
    if phish_template_config_exists == 1:
        
        print("found template config")
        s3.download_file(bucketname, phish_template_config_s3_name, phish_template_config_local_name)    
        with open(phish_template_config_local_name) as config_file:
            configs = json.load(config_file, object_pairs_hook=OrderedDict)     
        return configs
    else:
        return "failed" 
############################ - End Function



############################ Deletes all resources needs for a single campaign/instance ############################
def lambda_handler(event, context):

    # HYBRID TRIGGER - SQS MESSAGE POINTING TO S3 BUCKET
    ###################################################################################################
    #Get IDs from SQS 
    campaignid = event['Records'][0]['messageAttributes']['campaignid']['stringValue']
    bucketname = event['Records'][0]['messageAttributes']['bucketname']['stringValue']

    #Get Campaign JSON config in S3
    campaign_config = get_phish_campaign_configs(bucketname=bucketname,campaignid=campaignid)

    #Campaign Template Config    
    region = campaign_config["region"]
    targetgroup = campaign_config["targetgroup"]
    template = campaign_config["template"]
    print("region:"+str(region))
    
    
    #Get Template JSON config in S3
    template_config = get_phish_template_configs(bucketname=bucketname,template=template)
    
    #Phishing Template Config
    subject_name = template_config["subject_name"]
    domain = template_config["domain"]
    domainprefix = template_config["domainprefix"]
    subdomain = domainprefix+"."+domain
    smtp_username = template_config["smtp_username"]
    smtp_address = template_config["smtp_address"]
    redirect_url_text = template_config["redirect_url"]
    landing_page_url = template_config["landing_page_url"]    
    ###################################################################################################
    
    ipname = str(campaignid)+"-ip"
    instancename = str(campaignid)+"-instance"
    username = str(campaignid)+"-user"
    policyname = str(campaignid)+"-policy"
    
    # Create AWS Clients
    route53 = boto3.client('route53')
    lightsail = boto3.client('lightsail', region_name = region)
    iam = boto3.client('iam')

    try:
        response = iam.detach_user_policy(
            UserName=username,
            PolicyArn='arn:aws:iam::016798119685:policy/'+policyname
        )
    except Exception as e:
        print("Exception: "+str(e))
        pass   
    try:    
        response4 = iam.list_access_keys(
            UserName=username
        )
        useraccesskey = str(response4['AccessKeyMetadata'][0]['AccessKeyId'])
    except Exception as e:
        print("Exception: "+str(e))
        pass  

    try:    
        response = iam.delete_access_key(
            UserName=username,
            AccessKeyId=useraccesskey
        )
    except Exception as e:
        print("Exception: "+str(e))
        pass  

    try:    
        response = iam.delete_user(
            UserName=username
        )
    except Exception as e:
        print("Exception: "+str(e))
        pass  

    try:    
        response = iam.delete_policy(
            PolicyArn='arn:aws:iam::016798119685:policy/'+policyname
        )    
    except Exception as e:
        print("Exception: "+str(e))
        pass  
    try:    
        response = lightsail.get_static_ip(
            staticIpName=ipname
        )

        instanceip = str(response['staticIp']['ipAddress'])    
    except Exception as e:
        print("response:"+str(response))
        print("Exception:"+str(e))
        pass  

    try:    
        response = lightsail.detach_static_ip(
            staticIpName=ipname
        )
    except Exception as e:
        print("response:"+str(response))
        print("Exception:"+str(e))
        pass  

    try:    
        response = lightsail.release_static_ip(
            staticIpName=ipname
        )
    except Exception as e:
        print("response:"+str(response))
        print("Exception:"+str(e))
        pass  

    try:  
        response = lightsail.delete_instance(
            instanceName=instancename
        )
    except Exception as e:
        print("response:"+str(response))
        print("Exception:"+str(e))
        pass  

    try:  
        zoneinfo = route53.list_hosted_zones()
        for zone in zoneinfo.get('HostedZones'):
            if zone['Name'] == domain+'.':
                zone_id = zone['Id'].split('/')[-1]
                
        hosted_zone_id = '/hostedzone/'+zone_id

        change_batch_payload = {
            'Changes': [
                {
                    'Action': 'DELETE',
                    'ResourceRecordSet': 
                {
                    'Name':subdomain,
                    'Type':'A',
                    'TTL': 60,
                            'ResourceRecords': [
                                {
                                    'Value': instanceip
                                },
                            ],
                }
                },
            ]
        }

        response10 = route53.change_resource_record_sets(
            HostedZoneId=hosted_zone_id, ChangeBatch=change_batch_payload
        )
    except Exception as e:
        print("response:"+str(response))
        print("Exception:"+str(e))
        pass  
    
    
    print("deletion successful for template:"+ template+ " campaignid:"+campaignid + " domain:"+subdomain+ " instancename:"+instancename+ " ipname:"+ipname)
    return "success"

############################ - End Function