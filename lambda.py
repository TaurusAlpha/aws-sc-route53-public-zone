from __future__ import annotations
from typing import TYPE_CHECKING
import boto3
import cfnresponse  # type: ignore

if TYPE_CHECKING:
    from mypy_boto3_sts.client import STSClient
    from mypy_boto3_route53.client import Route53Client


def lambda_handler(event, context) -> None:
    try:
        # Setup for accessing Route 53
        sts_client: STSClient = boto3.client("sts")
        assumed_role = sts_client.assume_role(
            RoleArn="arn:aws:iam::<DESTINATION_ACCOUNT_ID>:role/LambdaRoute53ManagementRole",
            RoleSessionName="R53UpdateSession",
        )
        credentials = assumed_role["Credentials"]
        r53_client: Route53Client = boto3.client(
            "route53",
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"],
        )
        ns_records = event["ResourceProperties"]["NSRecords"].split(",")
        domain_name = event["ResourceProperties"]["DomainName"]
        
        # Handling deletion of NS records
        if event["RequestType"] == "Delete":
            response = r53_client.change_resource_record_sets(
                HostedZoneId=domain_name,
                ChangeBatch={
                    "Comment": f"Delete NS records for {domain_name}",
                    "Changes": [
                        {
                            "Action": "DELETE",
                            "ResourceRecordSet": {
                                "Name": domain_name,
                                "Type": "NS",
                                "TTL": 300,
                                "ResourceRecords": [{"Value": ns} for ns in ns_records],
                            },
                        }
                    ],
                },
            )
            cfnresponse.send(
                event,
                context,
                cfnresponse.SUCCESS,
                {"Message": f"NS records {ns_records} deleted"},
            )
            return

        # Handling creation/updation of NS records
        response = r53_client.change_resource_record_sets(
            HostedZoneId=domain_name,
            ChangeBatch={
                "Comment": f"Update NS records for {domain_name}",
                "Changes": [
                    {
                        "Action": "UPSERT",
                        "ResourceRecordSet": {
                            "Name": domain_name,
                            "Type": "NS",
                            "TTL": 300,
                            "ResourceRecords": [{"Value": ns} for ns in ns_records],
                        },
                    }
                ],
            },
        )
        cfnresponse.send(
            event,
            context,
            cfnresponse.SUCCESS,
            {"Message": f"NS records {ns_records} updated"},
        )
    except Exception as e:
        cfnresponse.send(event, context, cfnresponse.FAILED, {"Message": str(e)})
