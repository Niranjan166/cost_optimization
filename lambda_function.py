import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')

    # Get all EBS snapshots
    response = ec2.describe_snapshots(OwnerIds=['self'])

    # Get all active EC2 instance IDs
    instances_response = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    active_instance_ids = set()

    for reservation in instances_response['Reservations']:
        for instance in reservation['Instances']:
            active_instance_ids.add(instance['InstanceId'])

    # Iterate through each snapshot and delete if it's not attached to any volume or the volume is not attached to a running instance
    for snapshot in response['Snapshots']:
        snapshot_id = snapshot['SnapshotId']
        volume_id = snapshot.get('VolumeId')

        if not volume_id:
            # Delete the snapshot if it's not attached to any volume
            ec2.delete_snapshot(SnapshotId=snapshot_id)
            print(f"Deleted EBS snapshot {snapshot_id} as it was not attached to any volume.")
        else:
            # Check if the volume still exists
            try:
                volume_response = ec2.describe_volumes(VolumeIds=[volume_id])
                if not volume_response['Volumes'][0]['Attachments']:
                    ec2.delete_snapshot(SnapshotId=snapshot_id)
                    print(f"Deleted EBS snapshot {snapshot_id} as it was taken from a volume not attached to any running instance.")
            except ec2.exceptions.ClientError as e:
                if e.response['Error']['Code'] == 'InvalidVolume.NotFound':
                    # The volume associated with the snapshot is not found (it might have been deleted)
                    ec2.delete_snapshot(SnapshotId=snapshot_id)
                    print(f"Deleted EBS snapshot {snapshot_id} as its associated volume was not found.")


#----------------------------------------------------------------
# import boto3

# def lambda_handler(event, context):

#     print("Starting EBS snapshot cleanup...")

#     ec2 = boto3.client('ec2')

#     # Get all EBS snapshots
#     response = ec2.describe_snapshots(OwnerIds=['self'])

#     print(f"Total snapshots found: {len(response['Snapshots'])}")

#     # Get all active EC2 instance IDs
#     instances_response = ec2.describe_instances(
#         Filters=[
#             {
#                 'Name': 'instance-state-name',
#                 'Values': ['running']
#             }
#         ]
#     )

#     active_instance_ids = set()

#     for reservation in instances_response['Reservations']:
#         for instance in reservation['Instances']:
#             active_instance_ids.add(instance['InstanceId'])

#     print(f"Running instances found: {len(active_instance_ids)}")

#     # Iterate snapshots
#     for snapshot in response['Snapshots']:

#         snapshot_id = snapshot['SnapshotId']
#         volume_id = snapshot.get('VolumeId')

#         print(f"Checking snapshot: {snapshot_id}")

#         if not volume_id:

#             # SAFE TESTING
#             print(f"[DRY RUN] Would delete snapshot {snapshot_id} (No volume attached)")

#             # REAL DELETE
#             # ec2.delete_snapshot(SnapshotId=snapshot_id)

#         else:

#             try:
#                 volume_response = ec2.describe_volumes(
#                     VolumeIds=[volume_id]
#                 )

#                 attachments = volume_response['Volumes'][0]['Attachments']

#                 if not attachments:

#                     print(f"[DRY RUN] Would delete snapshot {snapshot_id} (Unused volume)")

#                     # REAL DELETE
#                     # ec2.delete_snapshot(SnapshotId=snapshot_id)

#             except ec2.exceptions.ClientError as e:

#                 if e.response['Error']['Code'] == 'InvalidVolume.NotFound':

#                     print(f"[DRY RUN] Would delete snapshot {snapshot_id} (Volume deleted)")

#                     # REAL DELETE
#                     # ec2.delete_snapshot(SnapshotId=snapshot_id)

#                 else:
#                     print(f"Error occurred: {e}")

#     return {
#         'statusCode': 200,
#         'body': 'Snapshot cleanup completed'
#     }


# # Local Testing
# if __name__ == "__main__":

#     result = lambda_handler({}, None)

#     print(result)