import boto3
import json

AWS_REGION = "us-east-1"
SQS_QUEUE_NAME = "DeviceDataQueue"
sqs_client = boto3.client("sqs", region_name=AWS_REGION)

def create_sqs_queue():
    """Creates an SQS queue if it doesn't exist."""
    try:
        response = sqs_client.create_queue(
            QueueName=SQS_QUEUE_NAME,
            Attributes={
                "DelaySeconds": "0",
                "MessageRetentionPeriod": "86400",  # 1 day retention
                "VisibilityTimeout": "30",  # 30 seconds
            },
        )
        queue_url = response["QueueUrl"]
        print(f"✅ SQS queue '{SQS_QUEUE_NAME}' created successfully: {queue_url}")
        return queue_url
    except sqs_client.exceptions.QueueAlreadyExists:
        print(f"✅ SQS queue '{SQS_QUEUE_NAME}' already exists.")
        return get_sqs_queue_url()

def get_sqs_queue_url():
    """Fetches the URL of the existing SQS queue."""
    response = sqs_client.get_queue_url(QueueName=SQS_QUEUE_NAME)
    return response["QueueUrl"]

def send_message_to_sqs(device_data):
    """Sends device data to the SQS queue."""
    queue_url = get_sqs_queue_url()
    
    response = sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(device_data),
    )
    
    print(f"✅ Message sent to SQS queue: {response['MessageId']}")
    return response["MessageId"]

if __name__ == "__main__":
    create_sqs_queue()  # Create the SQS queue if it doesn't exist
