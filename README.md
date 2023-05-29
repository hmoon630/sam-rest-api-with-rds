# SAM REST API with RDS

This AWS SAM(Serverless Application Model) application demonstrates CRUD actions.

Since this application connects to AWS RDS, VPC integration is needed.
So, some components must be pre-built before deploying SAM application.
- VPC Subnets (if internet connection is required, the NAT gateway must be provisioned)
- Security group for lambda function
- MySQL compatible RDS with proper database and table
- A secret which contains `host`, `username`, `password`, `database` for connecting RDS

## Description

The only valid python version is `python3.10` since Lambda layer build uses this version.
Or you can build and deploy using Docker container, `public.ecr.aws/sam/build-python3.10:latest`. Refer to this [registry](https://gallery.ecr.aws/sam)

This app will deploy API Gateway, Lambda function and Lambda layer.

Detailed API spec is defined in `openapi.yaml`.

## Usage

To deploy application, execute sam commands.

```bash
sam build
sam deploy
```

## CI / CD Pipeline

To build CI/CD Pipeline, just create CodeCommit, CodeBuild, CodePipeline.

CodeBuild may require some permissions to deploy CloudFormation template. Followings are required permissions.

- Default codebuild permission (created by AWS console)
- cloudwatch:*
- ec2:*
- iam:*
- s3:*
- codedeploy*
- cloudformation:*
- lambda:*
