import json
import boto3

#define region
region = 'region_id'
ec2 = boto3.client('ec2', region_name=region)

def lambda_handler(event, context):
    instances = event["instances"].split(',')
    action = event["action"]
    
    #define state changes - start, starting, stopped, stopping etc
    if action == 'Start':
        print("STARTING your instance_name instance having id: " + str(instances))
        ec2.start_instances(InstanceIds=instances)
        response = "Successfully started your instance_name instance having id: " + str(instances)
    elif action == 'Stop':
        print("STOPPING your instance_name instance having id: " + str(instances))
        ec2.stop_instances(InstanceIds=instances)
        response = "Successfully stopped your instance_name instance having id: " + str(instances)
    
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
