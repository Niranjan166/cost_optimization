## **Identifying Stale EBS Snapshots**

EBS snapshots accumulate over time and continue to incur storage costs even after their associated EC2 instances or volumes are deleted or detached. Cleaning this up manually across an AWS account is repetitive and inefficient.

This project uses an AWS Lambda function to automate the cleanup. The function fetches all EBS snapshots owned by the account and checks each one against the list of active EC2 instances (running and stopped). If a snapshot's volume is no longer attached to any active instance — or if the volume no longer exists — the snapshot is identified as stale and deleted. This runs automatically on a schedule via EventBridge, requiring zero manual intervention and reducing unnecessary storage spend.
________________________________________
**Tech**: Python · AWS Lambda · Amazon EC2 · Amazon EBS · EventBridge · IAM
