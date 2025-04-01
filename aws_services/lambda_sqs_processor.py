import json
import boto3
import uuid
from decimal import Decimal
from datetime import datetime

# Initialize AWS Services
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("Devices")
sqs = boto3.client("sqs", region_name="us-east-1")
SQS_QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/932875213474/DeviceDataQueue"

def lambda_handler(event, context):
    """Handles both API Gateway and SQS events."""
    print(f"🔹 Received Event: {json.dumps(event)}")

    if "httpMethod" in event:  # API Gateway Request
        return handle_api_gateway_request(event)
    if "Records" in event:  # SQS Message Processing
        return handle_sqs_messages(event)

    return {"statusCode": 400, "body": json.dumps({"error": "Invalid event format"})}

def handle_api_gateway_request(event):
    """Handles API Gateway request & pushes device data to SQS."""
    try:
        body = json.loads(event["body"])
        device_id = body.get("device_id", str(uuid.uuid4()))
        body["device_id"] = device_id  # Ensure device_id is set

        # Send to SQS
        response = sqs.send_message(QueueUrl=SQS_QUEUE_URL, MessageBody=json.dumps(body))
        print(f"✅ Sent to SQS: {response}")

        return {"statusCode": 201, "body": json.dumps({"message": "Device data sent to SQS", "device_id": device_id})}

    except Exception as e:
        print(f"⚠️ API Gateway Error: {str(e)}")
        return {"statusCode": 400, "body": json.dumps({"error": "Invalid request format"})}

def handle_sqs_messages(event):
    """Processes device data received from SQS."""
    try:
        for record in event["Records"]:
            body = json.loads(record["body"])
            print(f"📥 Processing SQS Message: {body}")
            result = register_device(body)
            print(f"✅ DynamoDB Insert Result: {result}")

        return {"statusCode": 200, "body": json.dumps({"message": "SQS Event Processed"})}

    except Exception as e:
        print(f"⚠️ SQS Processing Error: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

def register_device(device_data):
    """Registers or updates a device in DynamoDB."""

    device_id = device_data.get("device_id", str(uuid.uuid4()))
    name = device_data.get("name", "Unknown Device")
    email = device_data.get("email", "Unknown Email")
    account_id = device_data.get("account_id", "Unknown")  # Ensure account_id is present

    # 🔹 Convert float values to Decimal for DynamoDB
    for key, value in device_data.items():
        if isinstance(value, float):
            device_data[key] = Decimal(str(value))

    # 🔹 Handle NULL values and replace them with default values
    item = {
        "device_id": device_id,
        "name": name,
        "email": email,
        "account_id": account_id,
        "status": device_data.get("status", "Disconnected"),  # Default status
        "temperature": device_data.get("temperature", "N/A"),
        "humidity": device_data.get("humidity", "N/A"),
        "co2_level": device_data.get("co2_level", "N/A"),
        "air_quality": device_data.get("air_quality", "N/A"),
        "latitude": device_data.get("latitude", "0.0"),
        "longitude": device_data.get("longitude", "0.0"),
        "altitude": device_data.get("altitude", "0"),
        "battery_level": device_data.get("battery_level", "0"),
        "uptime": device_data.get("uptime", "0"),
        "power_usage": device_data.get("power_usage", "0"),
        "voltage": device_data.get("voltage", "0"),
        "created_at": datetime.utcnow().isoformat()  # ✅ Proper timestamp format
    }

    # 🔹 Save to DynamoDB
    try:
        table.put_item(Item=item)
        print(f"✅ Successfully inserted into DynamoDB: {item}")
        return {"message": "Device registered successfully", "device_id": device_id}
    except Exception as e:
        print(f"⚠️ DynamoDB Write Error: {str(e)}")
        return {"error": str(e)}