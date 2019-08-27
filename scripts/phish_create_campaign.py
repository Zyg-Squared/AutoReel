#!/usr/bin/python3
###########
### File Name : phish_create_campaign.py
### Usage : python3 ./scripts/phish_create_campaign.py -c 00001-example
### Prerequiste Info : This should only be used on a Lightsail instance built with phish_create_instance.py from Lambda. The script requires packages from instance-requirements.txt and an INI file built from the Lambda. 
### Description : Reads configurations from INIs files pointing to S3 Buckets with Templates and Campaign Configurations. Creates Campaign components and fires campaign. Fired from root cron job based on the campaign_name.json file's launch date configuration.
### 
############

from gophish import Gophish
from gophish.models import *
import sqlite3
import configparser
#import secrets
import requests
import codecs
import simplejson as json
import csv
import boto3
import botocore
import argparse
from datetime import timedelta
from botocore.errorfactory import ClientError
from collections import OrderedDict



############################ Gets AutoReel Campaign JSON Data ############################
def get_phish_campaign_configs(bucketname="", campaignid="", useraccesskey="", usersecret=""):
    print("get_phish_campaign_configs")
    phish_campaign_config_s3_name  =   "campaigns/"+str(campaignid)+".json"
    phish_campaign_config_local_name   = "/tmp/"+str(campaignid)+".json"
    phish_campaign_config_exists = 0  
    s3 = boto3.client(
        's3',
        aws_access_key_id=useraccesskey,
        aws_secret_access_key=usersecret
    )
    
    try:
        s3.head_object(Bucket=bucketname, Key=phish_campaign_config_s3_name)
        phish_campaign_config_exists = 1
    except ClientError as e:
        print("not found - campaign config"+str(e))
        pass
    if phish_campaign_config_exists == 1:
        s3.download_file(bucketname, phish_campaign_config_s3_name, phish_campaign_config_local_name)    
        with open(phish_campaign_config_local_name) as config_file:
            configs = json.load(config_file, object_pairs_hook=OrderedDict)     
        return configs
    else:
        return "failed" 
############################ - End Function 



############################ Gets AutoReel Campaign Target Data ############################
def get_phish_campaign_targets(bucketname="", campaignid="", useraccesskey="", usersecret=""):
    phish_campaign_targets_s3_name  =   "campaigns/"+str(campaignid)+".csv"
    phish_campaign_targets_local_name   = "/tmp/"+str(campaignid)+".csv"
    phish_campaign_targets_exists = 0   
    s3 = boto3.client(
        's3',
        aws_access_key_id=useraccesskey,
        aws_secret_access_key=usersecret
    )
    
    try:
        s3.head_object(Bucket=bucketname, Key=phish_campaign_targets_s3_name)
        phish_campaign_targets_exists = 1
    except ClientError:
        print("not found - targets")
        pass
    if phish_campaign_targets_exists == 1:
        s3.download_file(bucketname, phish_campaign_targets_s3_name, phish_campaign_targets_local_name)   
        targets = []
        with open(phish_campaign_targets_local_name, 'r') as targets_file:  
            target_csvreader = csv.reader(targets_file, delimiter=',', quotechar='"')
            for row in target_csvreader:
                targets.append(User(first_name=str(row[0]), last_name=str(row[1]), position=str(row[2]), email=str(row[3]))) 
        return targets
    else:
        return "failed" 
############################ - End Function 



############################ Gets AutoReel Template JSON Data ############################    
def get_phish_template_configs(bucketname="", template="", useraccesskey="", usersecret=""):
    phish_template_config_s3_name  =   "templates/"+str(template)+"/"+str(template)+".json"
    phish_template_config_local_name   = "/tmp/"+str(template)+".json"
    phish_template_config_exists = 0      
    s3 = boto3.client(
        's3',
        aws_access_key_id=useraccesskey,
        aws_secret_access_key=usersecret
    )
    
    try:
        s3.head_object(Bucket=bucketname, Key=phish_template_config_s3_name)
        phish_template_config_exists = 1
    except ClientError:
        print("not found - template config")
        pass
    if phish_template_config_exists == 1:
        #print("found template config")
        s3.download_file(bucketname, phish_template_config_s3_name, phish_template_config_local_name)    
        with open(phish_template_config_local_name) as config_file:
            configs = json.load(config_file, object_pairs_hook=OrderedDict)     
        return configs
    else:
        return "failed"         
############################ - End Function 


    
############################ Gets AutoReel Template Mail Html Data ############################       
def get_phish_template_mail_html(bucketname="", template="", useraccesskey="", usersecret=""):
    phish_template_mail_html_s3_name  =   "templates/"+str(template)+"/"+str(template)+"-mail.html"
    phish_template_mail_html_local_name   = "/tmp/"+str(template)+"-mail.html"
    phish_template_mail_html_exists = 0 
    s3 = boto3.client(
        's3',
        aws_access_key_id=useraccesskey,
        aws_secret_access_key=usersecret
    )
    
    try:
        s3.head_object(Bucket=bucketname, Key=phish_template_mail_html_s3_name)
        phish_template_mail_html_exists = 1
    except ClientError:
        print("not found - template mail html")
        pass
    if phish_template_mail_html_exists == 1:
        #print("found template mail html")
        s3.download_file(bucketname, phish_template_mail_html_s3_name, phish_template_mail_html_local_name)    
        with codecs.open(phish_template_mail_html_local_name, 'r', 'utf-8') as mail_html_file:
            mail_html_data = mail_html_file.read()
            
        return mail_html_data
    else:
        return "failed"  
############################ - End Function 

    
    
############################ Gets AutoReel Template Landing Page Html Data ############################      
def get_phish_template_landing_html(bucketname="",template="", useraccesskey="", usersecret=""):
    phish_template_landing_html_s3_name  =   "templates/"+str(template)+"/"+str(template)+"-landing.html"
    phish_template_landing_html_local_name   = "/tmp/"+str(template)+"-landing.html"
    phish_template_landing_html_exists = 0   
    s3 = boto3.client(
        's3',
        aws_access_key_id=useraccesskey,
        aws_secret_access_key=usersecret
    )
    
    try:
        s3.head_object(Bucket=bucketname, Key=phish_template_landing_html_s3_name)
        phish_template_landing_html_exists = 1
    except ClientError:
        print("not found - template landing html")
        pass
    if phish_template_landing_html_exists == 1:
        #print("found template landing html")
        s3.download_file(bucketname, phish_template_landing_html_s3_name, phish_template_landing_html_local_name)    
        with codecs.open(phish_template_landing_html_local_name, 'r', 'utf-8') as landing_html_file:
            landing_html_data = landing_html_file.read()
            
        return landing_html_data
    else:
        return "failed"   
############################ - End Function 



############################ Creates all the campaign component and then fires the campaign ############################      
if __name__== "__main__":      
    try:   
        
        # HYBRID TRIGGER - INI FILE POINTING TO JSON CONFIG STORED IN S3 BUCKET
        ###################################################################################################
        parser = argparse.ArgumentParser()
        parser.add_argument("--campaign", "-c", help="campaign to run")
        args = parser.parse_args()
        print("Campaign: "+str(args.campaign))        
        #Get Values from INI 
        config = configparser.ConfigParser()
        config.read('/opt/gophish/'+str(args.campaign)+'.ini')

        campaignid = config['default']['campaign']
        bucketname = config['default']['bucketname']
        admin_password = config['default']['admin_password']
        smtp_password = config['default']['smtp_password']
        useraccesskey = config['default']['useraccesskey']
        usersecret = config['default']['usersecret']
        
        #Get Campaign JSON config in S3
        campaign_config = get_phish_campaign_configs(bucketname=bucketname, campaignid=campaignid, useraccesskey=useraccesskey, usersecret=usersecret)

        #Campaign Template Config    
        region = campaign_config["region"]
        targetgroup = campaign_config["targetgroup"]
        template_id = campaign_config["template"]
        
        #Get Template JSON config in S3
        template_config = get_phish_template_configs(bucketname=bucketname, template=template_id, useraccesskey=useraccesskey, usersecret=usersecret)

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

        # Connecting to the database file to pull api_key
        sqlite_file = '/opt/gophish/gophish.db'    # name of the sqlite database file
        conn = sqlite3.connect(sqlite_file)
        c = conn.cursor()
        c.execute('SELECT api_key FROM users WHERE username="admin"')
        API_KEY = str(c.fetchone()).replace("(\'","").replace("\',)","")
        
        #Admin password change
        #admin_password = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(25))
        port = "3333"
        path = "/api/users/"
        userid = "1"
        url = "https://"+subdomain+":"+port+path+userid+"?api_key="+API_KEY

        headers = {"Content-Type": "application/json"}

        try:
            json_change = {
                "username": "admin",
                "role": "admin",
                "password": admin_password
            }
            api_data = json.dumps(json_change)
            
            response = requests.put(url, data=api_data, headers=headers)

            if response.status_code == 200:
                print("Admin password updated")
            else:
                print("Failed:"+str(response))
                print(response.text) 

        except Exception as ex:
            print("Exception:"+str(ex))

        
        #Get CSV Target List from S3 and convert to User List
        targets = get_phish_campaign_targets(bucketname, campaignid, useraccesskey=useraccesskey, usersecret=usersecret) 
        
        #Get HTML from S3
        landing_html = get_phish_template_landing_html(bucketname, template_id, useraccesskey=useraccesskey, usersecret=usersecret)
        mail_html = get_phish_template_mail_html(bucketname, template_id, useraccesskey=useraccesskey, usersecret=usersecret)
        
        host = "https://"+subdomain+":"+port
        api = Gophish(API_KEY, host=host) #, verify=False)

        #Create variable names
        campaignName = campaignid+"-campaign"
        pageName = campaignid+"-page"
        groupName = campaignid+"-group" 
        templateName = campaignid+"-template"
        smtpName = campaignid+"-smtp"

        
        #Create Landing Page
        landingpage = Page(name=pageName, capture_credentials=True,capture_passwords=True, redirect_url=redirect_url_text, html=landing_html)
        page = api.pages.post(landingpage)
        print("page.id: "+str(page.id))

        #Create User Group
        group = Group(name=groupName, targets=targets)
        group = api.groups.post(group)
        print("group.id: "+str(group.id))

        #Create Mail Template
        mail_template = Template(name=templateName, subject=subject_name,  html=mail_html)

        template = api.templates.post(mail_template)
        print("template.id: "+str(template.id))
        
        #Create SMTP Profile - Can't send via SSL without a cert for the sending domain
        smtp = SMTP(name=smtpName)
        smtp.host = "localhost:25"
        smtp.from_address = smtp_address
        smtp.username = smtp_username
        smtp.password = smtp_password
        smtp.interface_type = "SMTP"
        smtp.ignore_cert_errors = True

        #Create Actual Campaign
        smtp = api.smtp.post(smtp)
        print("smtp.id: "+str(smtp.id))
        groups = [Group(name=groupName)]
        page = Page(name=pageName)
        template = Template(name=templateName)
        smtp = SMTP(name=smtpName)
        campaign = Campaign(
            name=campaignName, groups=groups, page=page,
            template=template, smtp=smtp, url=landing_page_url)

        campaign = api.campaigns.post(campaign)
        print("campaign.id: "+str(campaign.id))

        
        report_config = """
[Gophish]
gp_host: https://"""+subdomain+""":"""+port+"""
api_key: """+API_KEY+"""

[ipinfo.io]
ipinfo_token: <IPINFO_API_KEY>

[Google]
geolocate_key: <GEOLOCATE_API_KEY>"""
        report_config_file = open("/opt/gophish/reporting/gophish.json","w")#write mode 
        report_config_file.write(report_config) 
        report_config_file.close() 
        
    except Exception as ex:
        print("Exception:"+str(ex))

print("Program Complete")
############################ - End Function 