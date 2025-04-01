import boto3
import zipfile
import os

AWS_REGION = "us-east-1"
LAMBDA_FUNCTION_NAME = "ProcessDeviceDataLambda"
S3_BUCKET_NAME = "sensorcloud-lambda-code"
S3_KEY = "lambda_sqs_processor.zip"
EXISTING_LAMBDA_ROLE_ARN = "arn:aws:iam::932875213474:role/LabRole"
SQS_QUEUE_ARN = f"arn:aws:sqs:{AWS_REGION}:932875213474:DeviceDataQueue"

lambda_client = boto3.client("lambda", region_name=AWS_REGION)
s3_client = boto3.client("s3", region_name=AWS_REGION)

def create_lambda_zip():
    """Creates a zip package for Lambda deployment."""
    with zipfile.ZipFile("lambda_sqs_processor.zip", "w") as z:
        z.write("lambda_sqs_processor.py")
    print("✅ Lambda function packaged successfully.")

def upload_lambda_to_s3():
    """Uploads the Lambda zip package to S3."""
    create_lambda_zip()
    print(f"🔄 Uploading Lambda function to S3: {S3_BUCKET_NAME}/{S3_KEY}...")
    s3_client.upload_file("lambda_sqs_processor.zip", S3_BUCKET_NAME, S3_KEY)
    print("✅ Lambda function uploaded to S3 successfully.")

def deploy_lambda_function():
    """Deploys AWS Lambda function for processing SQS messages."""
    upload_lambda_to_s3()
    
    try:
        response = lambda_client.create_function(
            FunctionName=LAMBDA_FUNCTION_NAME,
            Runtime="python3.9",
            Role=EXISTING_LAMBDA_ROLE_ARN,
            Handler="lambda_sqs_processor.process_sqs_messages",
            Code={"S3Bucket": S3_BUCKET_NAME, "S3Key": S3_KEY},
            Timeout=10,
            MemorySize=128,
        )
        print(f"✅ Lambda function '{LAMBDA_FUNCTION_NAME}' created successfully.")
    except lambda_client.exceptions.ResourceConflictException:
        print(f"⚠️ Lambda function '{LAMBDA_FUNCTION_NAME}' already exists. Updating instead...")
        lambda_client.update_function_code(
            FunctionName=LAMBDA_FUNCTION_NAME,
            S3Bucket=S3_BUCKET_NAME,
            S3Key=S3_KEY
        )
        print("✅ Lambda function updated successfully.")

if __name__ == "__main__":
    deploy_lambda_function()
