import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2.describe_regions()['Regions']]
    running_servers = []
    already_stopped_servers = []
    lambda_stopped_servers = []
    failed_servers = []

    for region in regions:
        ec2 = boto3.client('ec2', region_name=region)
        
        # List of all running EC2 servers
        instances = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                running_servers.append({'InstanceId': instance['InstanceId'], 'Name': instance.get('Tags', [{'Key': 'Name', 'Value': 'N/A'}])[0]['Value'], 'Region': region})
        
        # List of all EC2 servers already in a stopped state
        instances = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}])
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                already_stopped_servers.append({'InstanceId': instance['InstanceId'], 'Name': instance.get('Tags', [{'Key': 'Name', 'Value': 'N/A'}])[0]['Value'], 'Region': region})
        
        # Stop running EC2 servers
        for server in running_servers:
            try:
                ec2.stop_instances(InstanceIds=[server['InstanceId']])
                lambda_stopped_servers.append(server)
            except Exception as e:
                failed_servers.append({'InstanceId': server['InstanceId'], 'Name': server['Name'], 'Region': server['Region'], 'Error': str(e)})
    
    print("List of all running EC2 servers:")
    for server in running_servers:
        print(server)
    
    print("\n\t List of all EC2 servers that Lambda has stopped:")
    for server in lambda_stopped_servers:
        print(server)
    
    print("\n\t List of all EC2 servers Lambda failed to stop:")
    for server in failed_servers:
        print(server)
    
    print("\n\t  List of all EC2 servers already in a stopped state:")
    for server in already_stopped_servers:
        print(server)