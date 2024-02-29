#This code needs to be coupled with Eventbridge & SNS to complete execution. Cloudwatch can be used to store logs. Ensure necessary IAM Permissions are granted. 

import boto3

def lambda_handler(event, context):
    ec2 = boto3.resource("ec2")
    sns_client = boto3.client("sns")
    topic_arn = 'sns_topic_arn'
    message = "Unused Elastic IPs in AWS account can be released"
    print()

    unused_ips = {}
    
    for region in ec2.meta.client.describe_regions()["Regions"]:
        region_name = region["RegionName"]
        try:
            ec2conn = boto3.client("ec2", region_name=region_name)
            addresses = ec2conn.describe_addresses(
                Filters=[{"Name": "domain", "Values": ["vpc"]}]
            )["Addresses"]
            for address in addresses:
                if (
                    "AssociationId" not in address
                    and address["AllocationId"] not in unused_ips
                ):
                    unused_ips[address["AllocationId"]] = region_name
                    # ec2conn.release_address(AllocationId=address["AllocationId"])
                    print(
                        f"Unused Elastic IP {address['PublicIp']} in region {region_name}\n"
                    )
        except Exception as e:
            print(f"No access to region {region_name}: {e}")
    
    unused_ips_list = "\n".join(f"{ip} in region {region}" for ip, region in unused_ips.items())
    total_eips = len(unused_ips)
    print('\nTotal found EIP:', total_eips)
    message = f"Following unused Elastic IPs in AWS account can be released:\n\n{unused_ips_list}\n\nTotal found EIP: {total_eips}"
    
    response = sns_client.publish(TopicArn=topic_arn, Message=message)
    print("Message published")
    return response
