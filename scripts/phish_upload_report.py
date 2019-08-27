#!/usr/bin/python3
###########
### File Name : phish_upload_report.py
### Usage : python3 ./scripts/phish_upload_report.py
### Prerequiste Info : Use this script in the Instance created by phish_cast.py
### Description : Uploads campaign data to centralized S3 bucket
### 
############

import logging
import boto3
from botocore.exceptions import ClientError
import argparse
import configparser



############################ Uploads S3 Object ############################
def put_phish_campaign_reports(bucketname="", campaignid="", useraccesskey="", usersecret=""):
    print("put_phish_campaign_reports")
    phish_campaign_report_s3_name  =   "reports/"+str(campaignid)+".xlsx"
    phish_campaign_report_local_name   = "/opt/gophish/reporting/"+str(campaignid)+"-campaign.xlsx"
    
    s3 = boto3.client(
        's3',
        aws_access_key_id=useraccesskey,
        aws_secret_access_key=usersecret
    )
    
    try:
        response = s3.upload_file(phish_campaign_report_local_name, bucketname, phish_campaign_report_s3_name)
        
    except Exception as ex:
        print("Exception:"+str(ex))
    else:
        return "failed" 
############################ - End Function

        
if __name__== "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--campaign", "-c", help="campaign to run")
        args = parser.parse_args()
        print("Campaign: "+str(args.campaign))        
        #Get Values from INI 
        config = configparser.ConfigParser()
        config.read('/opt/gophish/'+str(args.campaign)+'.ini')

        campaignid = config['default']['campaign']
        bucketname = config['default']['bucketname']
        useraccesskey = config['default']['useraccesskey']
        usersecret = config['default']['usersecret']
        
        #Get Campaign JSON config in S3
        campaign_report = put_phish_campaign_reports(bucketname=bucketname, campaignid=campaignid, useraccesskey=useraccesskey, usersecret=usersecret)

    except Exception as ex:
        print("Exception:"+str(ex))

print("Program Complete")
    