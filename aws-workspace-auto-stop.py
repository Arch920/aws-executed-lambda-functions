import boto3
from datetime import datetime, timezone, timedelta

def get_new_jersey_time():
    new_jersey_tz = timezone(timedelta(hours=-4))  # Eastern Time Zone is UTC-4 during Daylight Saving Time (DST). Can use timezone according to use case. Not mandatory for function
    now = datetime.now(new_jersey_tz)
    current_time = now.strftime("%H:%M:%S")
    print("Current New Jersey Time =", current_time)

def lambda_handler(event, context):
    get_new_jersey_time()
    
    directory_id = 'dir_id'  # Add your directory ID here
    region = 'region_id'
    running_mode = 'AVAILABLE'

    # Event
    session = boto3.session.Session(
        aws_access_key_id='',  # Add your access key here
        aws_secret_access_key=''  # Add your secret access key here
    )
    

    ws = session.client('workspaces')
    workspaces = []

    def describe_workspaces(next_token=None):
        params = {
            'DirectoryId': directory_id,
            'NextToken': next_token
        } if next_token else {'DirectoryId': directory_id}

        response = ws.describe_workspaces(**params)
        workspaces.extend(response['Workspaces'])

        if 'NextToken' in response:
            describe_workspaces(next_token=response['NextToken'])

    describe_workspaces()

    for workspace in workspaces:
        if workspace['State'] in ['STOPPED']:
            print('Could not stop workspace for user: ' + workspace['UserName'] + ' as Workspace is already in STOPPED state')
            
        elif workspace['State'] == running_mode:
            tags = ws.describe_tags(ResourceId=workspace['WorkspaceId'])['TagList']
            #this code will work based on tags. If tag key & values are satisfied, then the worspaces will be stopped
            #eg of tags - Key: Project   Value: Demo1Project
            tag_values = [tag['Value'] for tag in tags if tag['Key'] == 'tag_key'] #tag key can be anything like Name, Team, Project, etc 
            if 'tag_value' in tag_values: #tage value can be like UserName, Finance Team/Dev team, Project1/Project2, etc
                ws.stop_workspaces(
                    StopWorkspaceRequests=[
                        {
                            'WorkspaceId': workspace['WorkspaceId'],
                        },
                    ]
                )
                print('Stopping WorkSpace for user: ' + workspace['UserName'])
            else:
                print('Skipping workspace with ID: {} and UserName: {}. No required tags found.'.format(workspace['WorkspaceId'], workspace['UserName']))
        else:
            print('Could not stop workspace for user: ' + workspace['UserName'])
