# AWS Service Catalog Route53 Public Zone

A CloudFormation and Lambda-based solution for managing Route53 public hosted zones across AWS accounts via Service Catalog.

## Overview

This project provides CloudFormation templates and Lambda functions to create and manage Route53 public hosted zones. It's designed to work with AWS Service Catalog, allowing organizations to create standardized DNS zone management solutions across multiple AWS accounts.

## Components

- **rsc-r53-zone.yaml**: Main CloudFormation template that creates Route53 hosted zones and sets up cross-account management
- **lambda-role.yaml**: CloudFormation template to deploy the IAM role needed in the destination account
- **lambda.py**: Python code for the Lambda function that manages Route53 records

## Prerequisites

- Multiple AWS accounts
- AWS Service Catalog set up
- Python 3.12
- AWS CLI configured

## Setup Instructions

### Destination Account Setup

1. Deploy the `lambda-role.yaml` template in the destination account:
   ```
   aws cloudformation deploy --template-file lambda-role.yaml --stack-name route53-lambda-role --capabilities CAPABILITY_NAMED_IAM
   ```

2. Note the role ARN from the output.

### Source Account Setup

1. Replace all occurrences of `<DESTINATION_ACCOUNT_ID>` in the `rsc-r53-zone.yaml` template with the actual AWS account ID.

2. Deploy the template as a Service Catalog product or directly via CloudFormation:
   ```
   aws cloudformation deploy --template-file rsc-r53-zone.yaml --stack-name r53-zone-product --capabilities CAPABILITY_NAMED_IAM --parameter-overrides HostedZoneName=yourdomain.example.com
   ```

## Usage

When deployed, the solution:
1. Creates a public Route53 hosted zone in the source account
2. Obtains the NS records for the zone
3. Using the Lambda function, creates/updates corresponding NS records in the destination account

## Development

To modify or develop this project:

```bash
# Clone the repository
git clone https://github.com/yourusername/aws-service-catalog-route53-public-zone.git

# Install dependencies
pip install -r requirements.txt

# Run linting and type checking
mypy lambda.py
cfn-lint *.yaml
```

## License

MIT License (see LICENSE file for details)