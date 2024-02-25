import boto3
import json

def lambda_handler(event, context):
    ec2_resource = boto3.resource('ec2')
    
    # Make a list of existing volumes
    all_volumes = ec2_resource.volumes.all()
    volumes = [volume.volume_id for volume in all_volumes]
    
    # Find snapshots without existing volume
    snapshots = ec2_resource.snapshots.filter(OwnerIds=['self'])
    
    # Create list of all orphaned snapshots
    osl =[]
    print('\n * * * Snapshot list is * * *')
    for snapshot in snapshots:
        if snapshot.volume_id not in volumes:
            osl.append(snapshot.id)
            print('\n Snapshot ID is :-    ' + snapshot.id)
            if snapshot.tags:
                for tag in snapshot.tags:
                    if tag['Key'] == 'Name':
                        value = tag['Value']
                        print('\n Snapshot Tags are '+ tag['Key'] + ", value = " + value)
                    else:
                        print('\n This Snapshot has no Name tag')
                        break
    
    print('* * * Total ORPHANED Snapshots are:-    '+str(len(osl)) + ' * * *')
    print(3*'\n')
    print('Now checking for EBS Volumes')
    
    vol_status={"Name":"status","Values":["available"]}
    #Create list for all volumes in available state
    avl = []
    print('\n * * * EBS Volumes list is * * *')
    for vol in ec2_resource.volumes.filter(Filters=[vol_status]):
        vol_id = vol.id
        volume = ec2_resource.Volume(vol.id)
        avl.append(vol.id)
        print('\n Volume ID is:-    '+vol_id)
        if vol.tags:
            for tag in vol.tags:
                if tag['Key']=='Name':
                    value=tag['Value']
                    print('\n Volume Tags are:-    '+tag['Key']+",value = "+value)
                else:
                    print('\n Volume has no Name tags')
                    break
    print('\n * * * Total AVAILABLE (Unattached) EBS Volumes are:-    ' + str(len(avl)) + ' * * *')
    
    return {"statusCode": 200, "body": json.dumps("LAMBDA SUCCESSFULLY EXECUTED. RESULTS ARE . . . ")}
