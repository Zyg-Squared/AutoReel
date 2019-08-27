#!/usr/bin/python3
###########
### File Name : python3 ./scripts/phish_cast.py  --bucketname exampleBucketName --campaignid 00001-example --action create --keyid AKIA__KEYID_EXAMPLE  --key 0101010101010101010101010 --region us-west-2 --accountid 016298199999
### Usage : python3 ./scripts/phish_setup.py --bucketname exampleBucketName --domainname exampleDomainName.com  --keyid AKIA__KEYID_EXAMPLE  --key 0101010101010101010101010 --region us-west-2 --accountid 016298199999
### Prerequiste Info : Use this script after the AutoReel prequisties are complete and phish_setup.py has been run successfully
### Description : Creates a SQS Message to create or delete an AutoReel Stack ( GoPhish installed and auto-configured on a Lightsail instance with automated campaign building, reporting, and scheduling. Onboard postfix server installed and auto-configured to handle mail sending)
### 
############

import json
import boto3
import time
import dateutil.tz
import datetime
from datetime import datetime,timedelta
from botocore.errorfactory import ClientError
import argparse
from collections import OrderedDict



############################ Creates SQS Message to Trigger either the phish_create_instances or phish_delete_instances ############################
def send_sqs_message(bucketname="", campaignid="", region="", accountid="", queue_name="", ACCESS_KEY_ID="", ACCESS_KEY="" ):
    try:                
        sqs = boto3.client(
            'sqs',
            region_name=region,
            aws_access_key_id=str(ACCESS_KEY_ID),
            aws_secret_access_key=str(ACCESS_KEY)
        )        
        
        # Send message to SQS queue

        queue_url = 'https://sqs.'+region+'.amazonaws.com/'+accountid+'/'+queue_name
        response = sqs.send_message(
			QueueUrl=queue_url, 
			MessageBody=( 
				'Cast Log - Bucketname: '+str(bucketname)+'  campaignid: '+str(campaignid)
			), 
			MessageAttributes={
				'bucketname': {
					'StringValue': str(bucketname),
					'DataType': 'String'
				},
				'campaignid': {
					'StringValue': str(campaignid),
					'DataType': 'String'
				}
			}
		)		
 
        #print "update_device_log "+ str(deviceid)
        return "success"
    except Exception as es:
        print('__EXCEPTION__send_sqs_message log - Bucketname: '+str(bucketname)+'  campaignid: '+str(campaignid)+' exception: '+str(es))
        return "failed"     
    
############################ - End Function

    
############################ Creates a SQS Message to create or delete an AutoReel Stack ############################        
if __name__== "__main__":
    try:    
        parser = argparse.ArgumentParser()
        parser.add_argument("--bucketname", "-b", help="bucket where JSON config files will be stored")
        parser.add_argument("--campaignid", "-c", help="00001-example")
        parser.add_argument("--action", "-a", help="create or delete")
        parser.add_argument("--keyid", "-i", help="AWS IAM Programmatic ACCESS_KEY_ID")
        parser.add_argument("--key", "-k", help="AWS IAM Programmatic ACCESS_KEY")
        parser.add_argument("--region", "-r", help="AWS Region")
        parser.add_argument("--accountid", "-t", help="AWS Account ID Number")
        args = parser.parse_args()
        bucketname     = str(args.bucketname)
        campaignid     = str(args.campaignid)
        action     = str(args.action)
        ACCESS_KEY_ID  = str(args.keyid)
        ACCESS_KEY     = str(args.key)
        region         = str(args.region)
        accountid      = str(args.accountid)
    

        #ACCESS_KEY_ID   = "Insert the AWS IAM Programmatic ACCESS_KEY_ID" #or comment this out and use CLI Arguments
        #ACCESS_KEY      = "Insert the AWS IAM Programmatic ACCESS_KEY" #or comment this out and use CLI Arguments
        #region          = "us-east-1" #or comment this out and use CLI Arguments
        #accountid       = "016798119999" #or comment this out and use CLI Arguments
        
        queue_name    = "phish_"+str(action)+"_instance"
        if action == "create" or action == "delete":
            UTC_time = str(datetime.now()).replace(" ", "_")
            print("Start time UTC:"+str(UTC_time))   
            print("Response: "+send_sqs_message(bucketname, campaignid, region, accountid, queue_name, ACCESS_KEY_ID, ACCESS_KEY))
        else: 
            print("Action must be either \"create\" or \"delete\"")
    except Exception as ex:
        print("Exception:"+str(ex))

print("Program Complete")
############################ - End Function