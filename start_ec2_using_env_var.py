'''
For this code to work, following steps are needed - 
1. IAM permissions for Lambda to access EC2 actions, Cloudwatch permissoins to create logs. Create permissions as needed
2. Need to add environment variable & pass instance id in it for the code to work
3. Output will be similar to - 

Current IST time is 17:00
START RequestId: 850ajfgjsfuhsfhgd56aa06 Version: $LATEST
EC2 instance i-036someid35f is already running.
'''

import boto3
import datetime
import os
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Specify the instance ID
'''
Lines 25-29 will check if environment variable is set or not
Then it will log the fetched instance id
'''
instance_id = os.getenv('INSTANCE_ID')
if not instance_id:
    logging.error("INSTANCE_ID environment variable is not set.")
else:
    logging.info(f"Instance ID from env var is: {instance_id}")

# can change region
region = 'us-east-1'

utc_now = datetime.datetime.utcnow()
ist_offset = datetime.timedelta(hours=5, minutes=30)

# Convert UTC time to IST
ist_now = utc_now + ist_offset
current_time = ist_now.strftime('%H:%M')
print("Current IST time is", current_time)

def lambda_handler(event, context):
    ec2 = boto3.client('ec2', region_name=region)
    try:
        response = ec2.describe_instances(InstanceIds=[instance_id])
        #using reseervation to fetch instance name
        instance_state = response['Reservations'][0]['Instances'][0]['State']['Name']
        
        if instance_state == 'stopped':
            ec2.start_instances(InstanceIds=[instance_id])
            # start EC2 if it's in stopped state 
            print(f"EC2 instance {instance_id} started.") 
        elif instance_state == 'running':
            print(f"EC2 instance {instance_id} is already running.")
        else:
            logging.error(f"Unexpected instance state: {instance_state}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
