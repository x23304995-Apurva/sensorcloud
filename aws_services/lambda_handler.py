import boto3
import botocore.exceptions 
import json
import zipfile
import os

AWS_REGION = "us-east-1"
LAMBDA_FUNCTION_NAME = "DeviceStatusUpdateLambda"
EXISTING_LAMBDA_ROLE_ARN = "arn:aws:iam::932875213474:role/LabRole"  # Replace with an existing role
S3_BUCKET_NAME = "sensorcloud-lambda-code"
S3_KEY = "lambda_function.zip"
DYNAMODB_TABLE_NAME = "Devices"

lambda_client = boto3.client("lambda", region_name=AWS_REGION)
s3_client = boto3.client("s3", region_name=AWS_REGION)
events_client = boto3.client("events", region_name=AWS_REGION)

def create_lambda_zip():
    """Creates a zip package for Lambda deployment."""
    lambda_code = """import boto3
import json
from datetime import datetime

DYNAMODB_TABLE_NAME = 'Devices'
AWS_REGION = 'us-east-1'

dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

def lambda_handler(event, context):
    current_time = datetime.utcnow()
    
    try:
        response = table.scan()
        devices = response.get('Items', [])

        for device in devices:
            device_id = device['device_id']
            last_data_received = device.get('last_data_received')
            battery_level = device.get('battery_level')

            if last_data_received:
                last_data_time = datetime.fromisoformat(last_data_received)
                time_diff = (current_time - last_data_time).total_seconds() / 60  # Convert to minutes
                
                if time_diff > 60 and device['status'] != 'Idle':
                    table.update_item(
                        Key={'device_id': device_id},
                        UpdateExpression='SET status = :status',
                        ExpressionAttributeValues={':status': 'Idle'}
                    )

            if battery_level is not None and battery_level < 10:
                table.update_item(
                    Key={'device_id': device_id},
                    UpdateExpression='SET status = :status',
                    ExpressionAttributeValues={':status': 'Error (Low Battery)'}
                )

        return {'statusCode': 200, 'body': json.dumps('Lambda function executed successfully')}

    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps(f'Error: {str(e)}')}
"""
    with open("lambda_function.py", "w") as f:
        f.write(lambda_code)

    with zipfile.ZipFile("lambda_function.zip", "w") as z:
        z.write("lambda_function.py")

    os.remove("lambda_function.py")  # Cleanup after zip creation
    print("✅ Lambda function packaged successfully.")

def create_s3_bucket():
    """Creates an S3 bucket if it doesn't exist."""
    try:
        s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
        print(f"✅ S3 bucket '{S3_BUCKET_NAME}' already exists.")
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"🔄 Creating S3 bucket '{S3_BUCKET_NAME}'...")

            if AWS_REGION == "us-east-1":
                s3_client.create_bucket(Bucket=S3_BUCKET_NAME)  # No location constraint needed
            else:
                s3_client.create_bucket(
                    Bucket=S3_BUCKET_NAME,
                    CreateBucketConfiguration={"LocationConstraint": AWS_REGION}
                )

            print(f"✅ S3 bucket '{S3_BUCKET_NAME}' created successfully.")
        else:
            print(f"⚠️ Error checking/creating S3 bucket: {e}")

def upload_lambda_to_s3():
    """Uploads the Lambda zip package to S3."""
    create_lambda_zip()
    create_s3_bucket()

    print(f"🔄 Uploading Lambda function to S3: {S3_BUCKET_NAME}/{S3_KEY}...")
    s3_client.upload_file("lambda_function.zip", S3_BUCKET_NAME, S3_KEY)
    print("✅ Lambda function uploaded to S3 successfully.")

def deploy_lambda_function():
    """Deploys or updates the AWS Lambda function without creating a new IAM Role."""
    upload_lambda_to_s3()

    try:
        response = lambda_client.create_function(
            FunctionName=LAMBDA_FUNCTION_NAME,
            Runtime="python3.9",
            Role=EXISTING_LAMBDA_ROLE_ARN,  # Use an existing IAM role
            Handler="lambda_function.lambda_handler",
            Code={"S3Bucket": S3_BUCKET_NAME, "S3Key": S3_KEY},
            Timeout=10,
            MemorySize=128,
        )
        print(f"✅ Lambda function '{LAMBDA_FUNCTION_NAME}' created successfully.")
    except lambda_client.exceptions.ResourceConflictException:
        print(f"⚠️ Lambda function '{LAMBDA_FUNCTION_NAME}' already exists. Updating instead...")
        response = lambda_client.update_function_code(
            FunctionName=LAMBDA_FUNCTION_NAME,
            S3Bucket=S3_BUCKET_NAME,
            S3Key=S3_KEY
        )
        print("✅ Lambda function updated successfully.")

def create_event_rule():
    """Creates an EventBridge (CloudWatch Event) rule to trigger Lambda every 1 hour."""
    rule_name = "DeviceStatusUpdateScheduler"

    try:
        response = events_client.put_rule(
            Name=rule_name,
            ScheduleExpression="rate(1 hour)",
            State="ENABLED",
            Description="Trigger Lambda function every hour to update device status.",
        )
        rule_arn = response["RuleArn"]
        
        lambda_arn = f"arn:aws:lambda:{AWS_REGION}:932875213474:function:{LAMBDA_FUNCTION_NAME}"

        events_client.put_targets(
            Rule=rule_name,
            Targets=[{"Id": "1", "Arn": lambda_arn}]
        )
        print("✅ CloudWatch Event rule created successfully.")
    except Exception as e:
        print(f"⚠️ Error creating EventBridge rule: {str(e)}")

if __name__ == "__main__":
    deploy_lambda_function()
    create_event_rule()
