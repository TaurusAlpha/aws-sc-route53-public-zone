from __future__ import annotations
from typing import TYPE_CHECKING
import boto3
import cfnresponse
if TYPE_CHECKING:
    from mypy.boto3.route53.client import Route53Client
    from mypy.boto3.sts.client import STSClient
    
def lambda_handler(event, context):
    try:
        # Setup for accessing Route 53
        sts_client = boto3.client('sts')
        assumed_role = sts_client.assume_role(RoleArn="arn:aws:iam::<DESTINATION_ACCOUNT_ID>:role/LambdaRoute53ManagementRole", RoleSessionName="R53UpdateSession")
        credentials = assumed_role['Credentials']
        route53 = boto3.client('route53',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'])
        ns_records = list(event['ResourceProperties']['NSRecords'].split(","))
        domain_name = event['ResourceProperties']['DomainName']
        if event['RequestType'] == 'Delete':
        # Handling deletion of NS records
        response = route53.change_resource_record_sets(
            HostedZoneId='DESTINATION_ZONE_ID', # Change this to your destination hosted zone ID
            ChangeBatch={
            'Changes': [{
                'Action': 'DELETE',
                'ResourceRecordSet': {
                'Name': domain_name,
                'Type': 'NS',
                'TTL': 300,
                'ResourceRecords': [{'Value': ns} for ns in ns_records]
                }
            }]
            }
        )
        cfnresponse.send(event, context, cfnresponse.SUCCESS, {"Message": "NS records deleted"})
        return

        # Handling creation/updation of NS records
        response = route53.change_resource_record_sets(
        HostedZoneId='DESTINATION_ZONE_ID',
        ChangeBatch={
            'Changes': [{
            'Action': 'UPSERT',
            'ResourceRecordSet': {
                'Name': domain_name,
                'Type': 'NS',
                'TTL': 300,
                'ResourceRecords': [{'Value': ns} for ns in ns_records]
            }
            }]
        }
        )
        cfnresponse.send(event, context, cfnresponse.SUCCESS, {"Message": "NS records updated"})
    except Exception as e:
        cfnresponse.send(event, context, cfnresponse.FAILED, {"Message": str(e)})