import json
import boto3
import uuid
from botocore.exceptions import ClientError
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from datetime import datetime, timezone
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt

# Initialize AWS Services
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
devices_table = dynamodb.Table("Devices")
users_table = dynamodb.Table("Users")  # For fetching user details

class DeviceListView(View):
    """Handles retrieving all devices from DynamoDB."""

    def get(self, request):
        try:
            response = devices_table.scan()
            devices = response.get("Items", [])

            return JsonResponse({"devices": devices}, status=200)
        except ClientError as e:
            print(f"⚠️ DynamoDB Scan Error: {e}")
            return JsonResponse({"error": "Failed to fetch devices"}, status=500)

class DeviceDetailView(View):
    """Handles retrieving a single device by its ID."""

    def get(self, request, device_id):
        try:
            response = devices_table.get_item(Key={"device_id": device_id})
            device = response.get("Item")

            if not device:
                return JsonResponse({"error": "Device not found"}, status=404)

            return JsonResponse(device, status=200)
        except ClientError as e:
            print(f"⚠️ DynamoDB Query Error: {e}")
            return JsonResponse({"error": "Failed to fetch device"}, status=500)

class DashboardView(View):
    """Displays the device dashboard for a logged-in user."""

    def get(self, request):
        user_email = request.GET.get("email")
        if not user_email:
            return JsonResponse({"error": "Missing user email"}, status=400)

        try:
            # ✅ Corrected: Query users instead of scanning
            user_response = users_table.query(
                IndexName="EmailIndex",  
                KeyConditionExpression="email = :email",
                ExpressionAttributeValues={":email": {"S": user_email}}
            )
            user_items = user_response.get("Items", [])

            if not user_items:
                return JsonResponse({"error": "User not found"}, status=404)

            user = user_items[0]
            account_id = user.get("account_id", {}).get("S", "Unknown")
            role = user.get("role", {}).get("S", "User")
            print(f"✅ Fetched Account ID: {account_id}")

            # ✅ Corrected: Query devices instead of scanning
            device_response = devices_table.query(
                IndexName="AccountIdIndex",
                KeyConditionExpression="account_id = :account_id",
                ExpressionAttributeValues={":account_id": {"S": account_id}}
            )
            devices = device_response.get("Items", [])

            if not devices:
                return JsonResponse({"error": "Device not found"}, status=404)

            print(f"✅ Devices Found: {devices}")

            # Prepare device list for UI rendering
            device_list = [
                {
                    "device_id": device.get("device_id", {}).get("S", ""),
                    "name": device.get("name", {}).get("S", ""),
                    "status": device.get("status", {}).get("S", "N/A"),
                    "last_data_received": device.get("last_data_received", {}).get("S", "N/A"),
                    "battery_level": device.get("battery_level", {}).get("N", "N/A"),
                    "temperature": device.get("temperature", {}).get("N", "N/A"),
                    "humidity": device.get("humidity", {}).get("N", "N/A"),
                }
                for device in devices
            ]

            return render(
                request, "dashboard.html",
                {"devices": device_list, "user_email": user_email, "user_role": role}
            )

        except ClientError as e:
            print(f"⚠️ DynamoDB Query Error: {e}")
            return JsonResponse({"error": "Error fetching devices"}, status=500)

class DeviceDataAPI(View):
    """Handles fetching device data for real-time updates."""

    def get(self, request):
        device_id = request.GET.get("device_id")
        if not device_id:
            return JsonResponse({"error": "Missing device_id"}, status=400)

        try:
            response = devices_table.get_item(Key={"device_id": device_id})
            device = response.get("Item")

            if not device:
                return JsonResponse({"error": "Device not found"}, status=404)

            return JsonResponse(device, status=200)
        except ClientError as e:
            print(f"⚠️ DynamoDB Query Error: {e}")
            return JsonResponse({"error": "Failed to fetch device data"}, status=500)

@csrf_exempt  # ✅ Disable CSRF for API endpoint
def register_device(request):
    """Registers a new device linked to a user's account."""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        body = json.loads(request.body.decode("utf-8"))
        required_fields = ["name", "email"]

        if not all(field in body for field in required_fields):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        user_email = body["email"]

        # ✅ Query Users Table using EmailIndex
        user_response = users_table.query(
            IndexName="EmailIndex",
            KeyConditionExpression="email = :email",
            ExpressionAttributeValues={":email": {"S": user_email}}
        )

        user_items = user_response.get("Items", [])

        if not user_items:
            print(f"⚠️ User with email {user_email} not found in Users table!")
            return JsonResponse({"error": "User not found"}, status=404)

        # # ✅ Ensure correct extraction of `account_id`
        account_id = user_items[0].get("account_id", "unknown")
        if isinstance(account_id, dict) and "S" in account_id:
            account_id = account_id["S"]

        print(f"✅ Assigning Device to Account ID: {account_id}")

        device_id = body.get("device_id", str(uuid.uuid4()))
        created_at = datetime.utcnow().isoformat()
        
        # ✅ Ensure correct extraction of `account_id`
    #     if "account_id" in user_items[0]:  # Check if 'account_id' exists
    #         account_id = user_items[0]["account_id"]
    
    # # If it's a DynamoDB string type, extract the value
    #     if isinstance(account_id, dict) and "S" in account_id:
    #         account_id = account_id["S"]
    #     else:
    #         print(f"⚠️ Warning: No account_id found for email {user_email}.")
    #         account_id = "unknown"  # Set to unknown only if it doesn't exist

    #     print(f"✅ Assigning Device to Account ID: {account_id}")

    #     device_id = body.get("device_id", str(uuid.uuid4()))
    #     created_at = datetime.utcnow().isoformat()

        # Convert float values to Decimal for DynamoDB
        for key, value in body.items():
            if isinstance(value, float):
                body[key] = Decimal(str(value))

        # ✅ Ensure `account_id` is saved correctly
        device_data = {
            "device_id": {"S": device_id},
            "name": {"S": body["name"]},
            "email": {"S": user_email},
            "account_id": {"S": account_id},
            "status": {"S": "Disconnected"},
            "temperature": {"N": str(body.get("temperature", "0"))},
            "humidity": {"N": str(body.get("humidity", "0"))},
            "battery_level": {"N": str(body.get("battery_level", "0"))},
            "created_at": {"S": created_at}
        }

        # Save to DynamoDB
        devices_table.put_item(Item=device_data)
        print(f"✅ Device Registered Successfully: {device_data}")

        return JsonResponse({"message": "Device registered successfully", "device_id": device_id})

    except Exception as e:
        print(f"⚠️ Error Registering Device: {str(e)}")
        return JsonResponse({"error": "Internal server error"}, status=500)
