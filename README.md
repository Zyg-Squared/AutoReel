AutoReel
=======
### AutoReel Open-Source Automated Phishing Platform - Start email security assessments in less than 6 minutes

AutoReel is an open-source phishing platform designed for ~lazy~ efficient penetration testers. This is primarily for spear-phishing during red-team vs blue-team security assessments. AutoReel uses one AWS lightsail instance per campaign to allow for the penetration testers to build a [GoPhish](https://github.com/gophish/gophish) server and launch a campaign in less than 6 minutes. 

AutoReel can be used to launch many GoPhish servers each with their own campaign. While each campaign is running, report data is uploaded to an S3 bucket using [Goreport](https://github.com/chrismaddalena/Goreport) every 5 minutes. 

AutoReel uses the following
 - Python3
 - [GoPhish](https://github.com/gophish/gophish)
 - [Goreport](https://github.com/chrismaddalena/Goreport)
 - Ubuntu
 - AWS - Lambda, SQS, IAM, S3, Route53, Lightsail, and Cloudwatch for logging


### Prerequisites:

 - AWS Account Setup
	 - This platform is built on AWS and is strongly coupled with it. You will need an AWS account that you  - can create resources in. 
	 - https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/

 - AWS IAM Account with Programmatic Access Keys
	 - Needs IAM, S3, SQS, and Lambda Read/Write/List Permissions to start with, then can be reduced to just SQS send message. 

 - Domain Registration
	 - https://aws.amazon.com/getting-started/tutorials/get-a-domain/
	 - This platform is built on AWS Route53 and is strongly coupled with it. You will need a domain name hosted in route53. 
	
 - Lets Encrypt
	 - https://certbot.eff.org/lets-encrypt/ubuntubionic-other 
	 - Encryption is important, ok?
	 - You will need to generate an SSL cert using certbot and insert it into the phish_create_instance.py
	 - I might add something later to make this piece easier, but I'd rather not deal with key material on certs. 
	
 - AWS Service limits
	 - Lightsail instance and static IPs
	 - This is dependant on how many campaigns you want to run at the same time. New AWS Accounts have Lightsail instance and Static IP limits set at 2 to start with. 
	 - https://docs.aws.amazon.com/general/latest/gr/aws_service_limits.html


### Install

Installation of AutoReel takes a few steps and dependencies. 


### Setup

    git clone https://github.com/Zyg-Squared/AutoReel.git

    cd ./AutoReel

    pip3 install -r ./requirements.txt

    echo "First Name,Last Name,Position,Email\nBob,Smith,,bob.smith@bobswebsite.com" > 00001-
    example.csv
    
    # nano ./campaigns/00001-example.json or nano ./campaigns/00001-example.json
    # Modify line 7 "launch_date": "5 2 27 8 *" to be "launch_date": "min hour day month *"
    # Example: If you want the launch date to be December 31st at 3:42pm you would use "launch_date": "42 15 31 12 *"

    python3 python3 ./scripts/phish_setup.py --bucketname exampleBucketName --domainname exampleDomainName.com  --keyid AKIA__KEYID_EXAMPLE  --key 0101010101010101010101010 --region us-west-2 --accountid 016298199999

    python3 ./scripts/phish_cast.py  --bucketname exampleBucketName --campaignid 00001-example --action create --keyid AKIA__KEYID_EXAMPLE  --key 0101010101010101010101010 --region us-west-2 --accountid 016298199999


### Documentation

Working on it....


### Future Work - ( that probably wont be done )
 - Campaign types: 
	 - Drive By
	 - Credential Harvesting
	 	- MFA Harvesting and replay
	 - Attachments
	 - This would be part of the template.json file 

 - Email Scheduling: 
	 - Using a cron to fire phish_create_campaign.py isn't the best method, but in the words of my favorite sysadmin/farmer "just rub some bash on it, it will be fine". 
	 - The datetime object using in gophish python api had an issue with invalid json and I needed to make this work. 

 - Terraform:
	 - phish_setup.py has a lot of functions that should use Terraform or Cloudformation. 
	 - These systems require a bit more dependences/permissions/prerequistes. 
	 - This was a bit cleaner until I find a decent Terraform template using S3 state files. 
	 - More info on Terraform incase some else wants to give it a shot
		 - https://learn.hashicorp.com/terraform/getting-started/install.html
		 - https://www.davidbegin.com/the-most-minimal-aws-lambda-function-with-python-terraform/

 - Lightsail Startup Script
	 - I know, its the best oneliner ever lol. I'll fix it, eventually....


### Issues

 - The future work section has some areas that need work. Other than that, let me know if you have any ideas for features or find a bug. Please [file an issue](https://github.com/Zyg-Squared/AutoReel/issues/new) and I'll look into it.


### License
```
AutoReel - Open-Source Phishing Platform

The MIT License (MIT)

Copyright (c) 2019 - 2019 Zyg-Squared LLC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software ("AutoReel Community Edition") and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```
