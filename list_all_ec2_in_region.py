'''
This Lambda function will help to list all EC2 instances present in a given region
For this code to work, following will be needed -
1. IAM permissions for Lambda to read EC2 details
2. Cloudwatch permission to log details

Expected Output will be similar to - 

INIT_START Runtime Version: python:3.13.v13	Runtime Version ARN: arn:aw05f1b7c
Current IST time is 16:06
[INFO]	2025-02-24T10:36:56.295Z	80e4d914-beb1-4b4d-be34-740750c12314	Found credentials in environment variables.
[WARNING]	2025-02-24T10:36:59.489Z	80e4d914-beb1-4b4d-be34-740750c12314	Instance with ID i-06f4 has no tags.
[INFO]	2025-02-24T10:36:59.489Z	80e4d914-beb1-4b4d-be34-740750c12314	Instances information retrieved successfully
[{'InstanceId': 'i-0365f', 'Name': 'Monitoring_Server', 'State': 'stopped', 'AvailabilityZone': 'us-east-1b'}, {'InstanceId': 'i-06af4', 'Name': None, 'State': 'running', 'AvailabilityZone': 'us-east-1c'}]
END RequestId:
'''

import boto3
import logging
import json
import datetime

utc_now = datetime.datetime.utcnow()
ist_offset = datetime.timedelta(hours=5, minutes=30)

# Convert UTC time to IST
ist_now = utc_now + ist_offset
current_time = ist_now.strftime('%H:%M')
print("Current IST time is", current_time)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Specify the region
    region = 'us-east-1'
    ec2 = boto3.client('ec2', region_name=region)
    
    try:
        # Describe EC2 instances
        response = ec2.describe_instances()
    except boto3.exceptions.Boto3Error as e:
        # Log the error if describe_instances fails
        logger.error(f"Error describing instances: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error describing instances: {e}")  # Convert to JSON string
        }
    
    instances_info = []
    
    try:
        # Iterate through each reservation
        for reservation in response['Reservations']:
            # Iterate through each instance in the reservation
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']  # Get instance ID
                instance_state = instance['State']['Name']  # Get instance state
                instance_az = instance['Placement']['AvailabilityZone'] #show instance Availability zone
                
                # Get the instance name from tags (if tags are present)
                instance_name = None
                if 'Tags' in instance:
                    for tag in instance['Tags']:
                        if tag['Key'] == 'Name':
                            instance_name = tag['Value']
                            break
                else:
                    # Log if the instance has no tags
                    logger.warn(f"Instance with ID {instance_id} has no tags.")
                
                # Append instance details to the list
                instances_info.append({
                    'InstanceId': instance_id,
                    'Name': instance_name,
                    'State': instance_state,
                    'AvailabilityZone': instance_az 
                })
    except Exception as e:
        # Log any error that occurs during instance processing
        logger.error(f"Error processing instances: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error processing instances: {e}")  # Convert to JSON string
        }
    
    # Log success message
    logger.info("Instances information retrieved successfully")
    print(instances_info)
    return {
        'statusCode': 200,
        'body': json.dumps(instances_info)  # Convert to JSON string
    }