#!/usr/bin/python3
###########
### File Name : phish_create_instance.py
### Usage : python3 ./scripts/phish_create_instance.py 
### Prerequiste Info : Use this script in the Lambda created by phish_setup.py and after AutoReel prequisties are complete 
### Description : Builds a Lightsail instance, assigns static IPs, opens ports, creates IAM credentials, installs and configures everything needed for automated campaign building, reporting, and scheduling.
### 
############

import boto3
import time
import json
import secrets
import string
import boto3
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



############################ Creates everything needed for campaign/instance ############################    
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
    launch_date = campaign_config["launch_date"]
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
    port = "3333"
    
    # Generate SMTP Password
    smtp_password = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(25))
    admin_password = "ETC4d2HDsoyR425uHh"
    # Create AWS Clients
    route53 = boto3.client('route53')
    lightsail = boto3.client('lightsail', region_name = region)
    iam = boto3.client('iam')
    
    
    # Create user
    try:    
        response1 = iam.create_user(UserName=username)
    except Exception as e:
        print("Exception:"+str(e))
        pass      

    # Create user policy document
    try:
        
        Document_beforeboot={
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "S3R1",
                    "Effect": "Allow",
                    "Action": "s3:HeadBucket",
                    "Resource": "*"
                },
                {
                    "Sid": "S3R3",
                    "Effect": "Allow",
                    "Action": "s3:ListBucket",
                    "Resource": [
                        "arn:aws:s3:::"+bucketname+"/*",
                        "arn:aws:s3:::"+bucketname
                    ]
                },
                {
                    "Sid": "S3RW4",
                    "Effect": "Allow",
                    "Action": [
                        "s3:PutObject",
                        "s3:GetObject"
                    ],
                    "Resource": [
                        "arn:aws:s3:::"+bucketname+"/*"
                    ]
                }
            ]
        }
        

        response2 = iam.create_policy(PolicyName=policyname, PolicyDocument=json.dumps(Document_beforeboot))
    except Exception as e:
        print("Exception:"+str(e))
        pass              

    # Attach policy to user
    try:
        response3 = iam.attach_user_policy(UserName=username, PolicyArn='arn:aws:iam::'+str(boto3.client('sts').get_caller_identity()['Account'])+':policy/'+policyname
        )
    except Exception as e:
        print("Exception:"+str(e))
        pass          

    # Create user access keys
    try:    
        response4 = iam.create_access_key(UserName=username)

        useraccesskey = str(response4['AccessKey']['AccessKeyId'])
        usersecret = str(response4['AccessKey']['SecretAccessKey'])
    except Exception as e:
        print("Exception:"+str(e))
        pass  
    
    privatekey="""-----BEGIN PRIVATE KEY-----
-----END PRIVATE KEY-----"""
    
    fullchain="""-----BEGIN CERTIFICATE-----
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
-----END CERTIFICATE-----"""

    # Create lightsail instance
    try:        
        response5 = lightsail.create_instances(
            instanceNames=[
                instancename,
            ],
            availabilityZone=str(region)+'a',
            blueprintId='ubuntu_18_04',
            bundleId='nano_1_0',
            userData='sudo DEBIAN_FRONTEND=noninteractive apt-get -y update; sudo DEBIAN_FRONTEND=noninteractive apt-get -y install git gccgo-go unzip mailtools postfix python3 python3-pip; sudo mkdir -p /opt/gophish/reporting/ ; cd /opt/gophish/; sudo wget https://github.com/gophish/gophish/releases/download/v0.8.0/gophish-v0.8.0-linux-64bit.zip; sudo mv gophish-v0.8.0-linux-64bit.zip /opt/gophish/ ; sudo unzip /opt/gophish/gophish-v0.8.0-linux-64bit.zip -d /opt/gophish/ ; sudo echo \"'+fullchain+'\" > /opt/gophish/fullchain.pem ; sudo echo \"'+privatekey+'\" > /opt/gophish/privatekey.key ; sudo git clone https://github.com/Zyg-Squared/AutoReel.git; sudo mv /opt/gophish/AutoReel/service/gophish.service /lib/systemd/system/gophish.service; sudo mv /opt/gophish/AutoReel/service/config.json /opt/gophish/;  sudo sed -i \'s/__DOMAIN__/'+domain+'/g\' /opt/gophish/AutoReel/service/main.cf; sudo mv /opt/gophish/AutoReel/service/main.cf /etc/postfix/; sudo mv /opt/gophish/AutoReel/service/gophish.sh /root/gophish.sh; sudo chmod +x /root/gophish.sh; sudo git clone https://github.com/chrismaddalena/Goreport.git /opt/gophish/reporting/;  sudo service postfix reload; sudo echo \"[mail.'+domain+']:25 '+smtp_username+'@'+domain+':'+smtp_password+'\" >  sasl_passwd;  sudo cp sasl_passwd /etc/postfix/sasl/sasl_passwd ; sudo postmap /etc/postfix/sasl/sasl_passwd; sudo rm sasl_passwd ; sudo pip3 install -r /opt/gophish/AutoReel/script/instance-requirements.txt; sudo systemctl daemon-reload; sudo systemctl enable gophish.service; sudo echo \"[default]\ncampaign = '+str(campaignid)+'\ntemplate = '+template+'\nbucketname = '+bucketname+'\nuseraccesskey = '+useraccesskey+'\nusersecret = '+usersecret+'\nadmin_password = '+admin_password+'\nsmtp_password = '+smtp_password+'\" > /opt/gophish/'+str(campaignid)+'.ini; sudo crontab -l 2>/dev/null; echo \"*/5 * * * * cd /opt/gophish/reporting/ ; sudo python3 /opt/gophish/reporting/GoReport.py --id 1 --format excel --config /opt/gophish/reporting/gophish.json > /var/log/phish_campaign_report_'+str(campaignid)+'.log; sudo mv \'/opt/gophish/reporting/Gophish Results for '+str(campaignid)+'-campaign.xlsx\' /opt/gophish/reporting/'+str(campaignid)+'-campaign.xlsx; sudo python3 /opt/gophish/AutoReel/scripts/phish_upload_report.py -c '+str(campaignid)+' > /var/log/phish_upload_report_'+str(campaignid)+'.log; \n'+str(launch_date)+' sudo python3 /opt/gophish/AutoReel/scripts/phish_create_campaign.py -c '+str(campaignid)+'>/var/log/phish_create_campaign_'+str(campaignid)+'.log ; \" |sudo crontab - ;  sudo DEBIAN_FRONTEND=noninteractive apt-get -y update; sudo DEBIAN_FRONTEND=noninteractive apt-get -y upgrade; sudo service gophish start;  sudo reboot now; '
            )
    
    except Exception as e:
        print("Exception:"+str(e))
        pass           
    
    # Sleep while instance is going through startup
    time.sleep(60) 

    # Open HTTPS ports
    try:
        response6 = lightsail.open_instance_public_ports(
            portInfo={
                'fromPort': 3333,
                'toPort': 3333,
                'protocol': 'tcp'
            },
            instanceName=instancename
        )
    except Exception as e:
        print("Exception:"+str(e))
        pass      
        
    # Open HTTPS ports
    try:
        response6 = lightsail.open_instance_public_ports(
            portInfo={
                'fromPort': 80,
                'toPort': 80,
                'protocol': 'tcp'
            },
            instanceName=instancename
        )
    except Exception as e:
        print("Exception:"+str(e))
        pass      
        
    # Open HTTPS ports
    try:
        response6 = lightsail.open_instance_public_ports(
            portInfo={
                'fromPort': 443,
                'toPort': 443,
                'protocol': 'tcp'
            },
            instanceName=instancename
        )
    except Exception as e:
        print("Exception:"+str(e))
        pass      

    # Create Static IP
    try:    
        response7 = lightsail.allocate_static_ip(
            staticIpName=ipname
        )
    except Exception as e:
        print("Exception:"+str(e))
        pass      

    # Attach Static IP
    try:    
        response8 = lightsail.attach_static_ip(
            staticIpName=ipname,
            instanceName=instancename
        )
    except Exception as e:
        print("Exception:"+str(e))
        pass      

    # Get Static IP Address
    try:    
        response9 = lightsail.get_static_ip(
            staticIpName=ipname
        )

        instanceip = str(response9['staticIp']['ipAddress'])

    except Exception as e:
        print("Exception:"+str(e))
        pass      

    # Create the DNS records payload in Route53
    try:
        zoneinfo = route53.list_hosted_zones()
        for zone in zoneinfo.get('HostedZones'):
            if zone['Name'] == domain+'.':
                zone_id = zone['Id'].split('/')[-1]

        hosted_zone_id = '/hostedzone/'+zone_id

        change_batch_payload = {
            'Changes': [
                {
                    'Action': 'CREATE',
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
            HostedZoneId=hosted_zone_id, ChangeBatch=change_batch_payload)

    except Exception as e:
        print("Exception:"+str(e))
        pass      

    print("creation successful for "+ campaignid + " domain:"+subdomain)
    return "success"
############################ - End Function     