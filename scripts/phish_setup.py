#!/usr/bin/python3
###########
### File Name : phish_setup.py
### Usage : python3 ./scripts/phish_setup.py --bucketname exampleBucketName --domainname exampleDomainName.com  --keyid AKIA__KEYID_EXAMPLE  --key 0101010101010101010101010 --region us-west-2 --accountid 016298199999
### Prerequiste Info : Use this script to start using AutoReel
### Description : Creates AWS resources - buckets with example campaign templates/configurations, SQS Queues, Lambda Functions, IAM Roles/Policies
### 
############

import boto3
import json
import boto3
import time
import botocore
from botocore.errorfactory import ClientError
import zipfile
from shutil import copyfile
import argparse



############################ Creates S3 Bucket and uploads S3 Object ############################
def create_S3_bucket_and_objects(bucketname="", campaignid="",templateid="", region="", accountid="", ACCESS_KEY_ID="", ACCESS_KEY="" ):
    try:
        s3_client = boto3.client('s3',
            region_name=region,
            aws_access_key_id=str(ACCESS_KEY_ID),
            aws_secret_access_key=str(ACCESS_KEY)
        )
        try:
            # Create bucket used for storing templates, campaigns, targets, and reports
            response = s3_client.create_bucket(Bucket=bucketname, ACL= 'private')  
            print("response: "+str(response))                  
        except Exception as ex: # In case bucket already exists
            print("Exception:"+str(ex))  
            pass
            
        localfilename = "./templates/"+str(templateid)+"/"+str(templateid)+".json"
        s3keyfilename = "templates/"+str(templateid)+"/"+str(templateid)+".json"
        response = s3_client.upload_file(localfilename, bucketname, s3keyfilename)  
        print("response: "+str(response))        

        localfilename = "./templates/"+str(templateid)+"/"+str(templateid)+"-mail.html"
        s3keyfilename = "templates/"+str(templateid)+"/"+str(templateid)+"-mail.html"
        response = s3_client.upload_file(localfilename, bucketname, s3keyfilename)  
        print("response: "+str(response))        

        localfilename = "./templates/"+str(templateid)+"/"+str(templateid)+"-landing.html"
        s3keyfilename = "templates/"+str(templateid)+"/"+str(templateid)+"-landing.html"
        response = s3_client.upload_file(localfilename, bucketname, s3keyfilename)  
        print("response: "+str(response))        
        
        localfilename = "./campaigns/"+str(campaignid)+".json"
        s3keyfilename = "campaigns/"+str(campaignid)+".json"
        response = s3_client.upload_file(localfilename, bucketname, s3keyfilename)   
        print("response: "+str(response))              
        
        localfilename = "./campaigns/"+str(campaignid)+".csv"
        s3keyfilename = "campaigns/"+str(campaignid)+".csv"
        response = s3_client.upload_file(localfilename, bucketname, s3keyfilename)   
        print("response: "+str(response))        
        
        return "success"
    except Exception as ex:
        print("Exception:"+str(ex))  
        return "failure"        
############################ - End Function
        
        

############################ Creates a SQS Queue, IAM Role, IAM Policy, IAM Assume Role Policy, Lambda function, and an event source mapping from the SQS Queue ############################
def create_SQS_Triggered_lambda(region="", accountid="", functionname="", ACCESS_KEY_ID="", ACCESS_KEY="" ):        
    try:
        FunctionName        = str(functionname)
        FunctionARN         = "arn:aws:lambda:"+str(region)+":"+str(accountid)+":function:"+str(FunctionName)
        FunctionRuntime     = "python3.6"
        FunctionHandler     = "lambda_function.lambda_handler"
        FunctionRoleName    = str(FunctionName)+'_Lambda_Role'
        FunctionPolicyName  = str(FunctionName)+'_Lambda_Policy'
        FunctionRoleARN     = "arn:aws:iam::"+str(accountid)+":role/"+str(FunctionRoleName)
        FunctionPolicyARN   = "arn:aws:iam::"+str(accountid)+":policy/"+str(FunctionPolicyName)
        FunctionZipFile     = ""
        FunctionS3Bucket    = ""
        FunctionS3Key       = ""
        FunctionDescription = ""
        FunctionTimeout     = 150
        FunctionMemorySize  = 128
        FunctionPublish     = True
        FunctionEventSourceArn      = "arn:aws:sqs:"+str(region)+":"+str(accountid)+":"+str(FunctionName)
        FunctionSQStriggerEnabled   = True
        FunctionBatchSize   = 1

        #Create the Lambda Boto3 Client        
        lambda_client = boto3.client('lambda',
            region_name=region,
            aws_access_key_id=str(ACCESS_KEY_ID),
            aws_secret_access_key=str(ACCESS_KEY)
        )

        #Create the IAM Boto3 Client        
        iam_client = boto3.client('iam',
            region_name=region,
            aws_access_key_id=str(ACCESS_KEY_ID),
            aws_secret_access_key=str(ACCESS_KEY)
        )

        #Create the SQS Boto3 Client
        sqs_client = boto3.client('sqs',
            region_name=region,
            aws_access_key_id=str(ACCESS_KEY_ID),
            aws_secret_access_key=str(ACCESS_KEY)
        )

        #Create the queue
        response = sqs_client.create_queue(
            QueueName=FunctionName,
            Attributes={
                "MaximumMessageSize": "262144",
                "DelaySeconds": "0",
                "MessageRetentionPeriod": "345600",
                "VisibilityTimeout": "300",
                "KmsMasterKeyId": "alias/aws/sqs",
                "KmsDataKeyReusePeriodSeconds": "300"
          }
        )
        try:


            #Read in the IAM Policy 
            with open("./scripts/"+FunctionPolicyName+".json", 'r') as json_file:
                FunctionIAMPolicyDocument = json_file.read()

            #Read in the Assume Role Policy
            with open("./scripts/"+FunctionRoleName+".json", 'r') as json_file:
                FunctionRolePolicyDocument = json_file.read()

            #Create the IAM Policy for the Lambda to assume through the role
            response = iam_client.create_policy(
              PolicyName=FunctionPolicyName,
              PolicyDocument=FunctionIAMPolicyDocument
            )
            #print("response: "+str(response))

            # Sleep while policy is being created
            time.sleep(2) 

            #Create the Role Lambda will assume
            response = iam_client.create_role(
              RoleName=FunctionRoleName,
              AssumeRolePolicyDocument=FunctionRolePolicyDocument,
            )     
            #print("response: "+str(response))

            #Attach IAM Policy to Role
            response = iam_client.attach_role_policy(
                RoleName=FunctionRoleName,
                PolicyArn=FunctionPolicyARN
            )
            #print("response: "+str(response))

            #Allow lambda to assume the IAM Role/Policy created earlier
            response = iam_client.update_assume_role_policy(
                PolicyDocument=FunctionRolePolicyDocument,
                RoleName=FunctionRoleName,
            )
        except Exception as ex: # In case IAM Config already exists
            print("Exception:"+str(ex))  
            pass
        # Sleep while role policies are updating
        time.sleep(15) 
        try:

            #Rename the lambda functions and zip them
            copyfile("./scripts/"+str(FunctionName)+".py", "./lambda_function.py")
            lambda_zip = zipfile.ZipFile("./scripts/"+str(FunctionName)+'.zip', 'w')
            lambda_zip.write("./lambda_function.py", compress_type=zipfile.ZIP_DEFLATED)
            lambda_zip.close()

            #Create the lambda function
            response = lambda_client.create_function(
                FunctionName=FunctionARN,
                Runtime=FunctionRuntime,
                Role=FunctionRoleARN,
                Handler=FunctionHandler,
                Code={
                    'ZipFile': open("./scripts/"+str(FunctionName)+'.zip', 'rb').read()
                },
                Description=FunctionDescription,
                Timeout=FunctionTimeout,
                MemorySize=FunctionMemorySize,
                Publish=FunctionPublish
            )
        except Exception as ex: # In case lambda already exists
            print("Exception:"+str(ex))  
            pass
        #print("response: "+str(response))


        # Sleep while function is being created
        time.sleep(5) 
        try:
            #Setup SQS Trigger for Lambda
            response = lambda_client.create_event_source_mapping(
                EventSourceArn=FunctionEventSourceArn,
                FunctionName=FunctionARN,
                Enabled=FunctionSQStriggerEnabled,
                BatchSize=FunctionBatchSize
            )
        except Exception as ex: # In case source mapping already exists
            print("Exception:"+str(ex))  
            pass        
        #print("response: "+str(response))
        return "success"
    except Exception as ex:
        print("Exception:"+str(ex))
        return "failure"        
    
############################ - End Function
        
        
        
############################ Builds everything needed for quick setup/tear down of GoPhish Instances ############################
if __name__== "__main__":
    try:    
        parser = argparse.ArgumentParser()
        parser.add_argument("--bucketname", "-b", help="bucket where JSON config files will be stored")
        parser.add_argument("--domainname", "-c", help="the domain name you purhcase on route 53 or are managing via route53")
        parser.add_argument("--keyid", "-i", help="AWS IAM Programmatic ACCESS_KEY_ID")
        parser.add_argument("--key", "-k", help="AWS IAM Programmatic ACCESS_KEY")
        parser.add_argument("--region", "-r", help="AWS Region")
        parser.add_argument("--accountid", "-t", help="AWS Account ID Number")
        args = parser.parse_args()
        bucketname     = str(args.bucketname)
        domainname     = str(args.domainname)
        ACCESS_KEY_ID  = str(args.keyid)
        ACCESS_KEY     = str(args.key)
        region         = str(args.region)
        accountid      = str(args.accountid)
    
        #ACCESS_KEY_ID   = "Insert the AWS IAM Programmatic ACCESS_KEY_ID" #or comment this out and use CLI Arguments
        #ACCESS_KEY      = "Insert the AWS IAM Programmatic ACCESS_KEY" #or comment this out and use CLI Arguments
        #region          = "us-east-1" #or comment this out and use CLI Arguments
        #accountid       = "016798119999" #or comment this out and use CLI Arguments

        campaignid = "00001-example"
        templateid = "example"
        functionname_create = "phish_create_instance"
        functionname_delete = "phish_delete_instance"
        print("Response: "+create_S3_bucket_and_objects(bucketname, campaignid, templateid, region, accountid, ACCESS_KEY_ID, ACCESS_KEY ))
        print("Bucket and Example Objects created")
        print("Response: "+create_SQS_Triggered_lambda(region, accountid, functionname_create, ACCESS_KEY_ID, ACCESS_KEY ))
        print("phish_create_instance lambda created")
        print("Response: "+create_SQS_Triggered_lambda(region, accountid, functionname_delete, ACCESS_KEY_ID, ACCESS_KEY ))
        print("phish_delete_instance lambda created")

    except Exception as ex:
        print("Exception:"+str(ex))

print("Program Complete")
    
############################ - End Function  