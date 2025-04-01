import json
import uuid
import boto3
from decimal import Decimal
from datetime import datetime
from botocore.exceptions import ClientError

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from users.models import UserModel


# Initialize AWS Services
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
devices_table = dynamodb.Table("Devices")
users_table = dynamodb.Table("Users")

class DeviceListView(View):
    def get(self, request):
        try:
            response = devices_table.scan()
            devices = response.get("Items", [])
            
            # Convert Decimal to float for JSON serialization
            for device in devices:
                for key in ['battery_level', 'temperature', 'humidity']:
                    if key in device and isinstance(device[key], Decimal):
                        device[key] = float(device[key])
            
            return JsonResponse({"devices": devices}, status=200)
        except ClientError as e:
            print(f"⚠️ DynamoDB Scan Error: {e}")
            return JsonResponse({"error": "Failed to fetch devices"}, status=500)


class DeviceDetailView(View):
    def get(self, request, device_id):
        try:
            response = devices_table.get_item(Key={"device_id": device_id})
            device = response.get("Item")
            if not device:
                return JsonResponse({"error": "Device not found"}, status=404)
            
            # Convert Decimal to float for JSON serialization
            for key in ['battery_level', 'temperature', 'humidity']:
                if key in device and isinstance(device[key], Decimal):
                    device[key] = float(device[key])
            
            return JsonResponse(device, status=200)
        except ClientError as e:
            print(f"⚠️ DynamoDB Query Error: {e}")
            return JsonResponse({"error": "Failed to fetch device"}, status=500)


class DashboardView(View):
    def get(self, request):
        # Get user email from session or request
        user_email = request.session.get('user_email') or request.GET.get("email")
        if not user_email:
            return redirect('login')  # Redirect to login if no email
        
        try:
            # Fetch user details
            user = UserModel.get_user_by_email(user_email)
            if not user:
                return JsonResponse({"error": "User not found"}, status=404)

            account_id = user.get('account_id')
            role = user.get('role', 'User')
            username = user.get('username', user_email.split('@')[0])

            # Fetch devices for this account
            device_response = devices_table.scan(
                FilterExpression="account_id = :account_id",
                ExpressionAttributeValues={":account_id": account_id}
            )
            devices = device_response.get("Items", [])

            # Prepare device stats
            total_devices = len(devices)
            online_devices = len([d for d in devices if d.get('status', '').lower() == 'online'])
            warning_devices = len([d for d in devices if d.get('status', '').lower() == 'warning'])
            offline_devices = total_devices - online_devices - warning_devices

            # Prepare device list with proper data types
            device_list = []
            for device in devices:
                device_list.append({
                    "device_id": device.get("device_id", "N/A"),
                    "name": device.get("name", "Unnamed Device"),
                    "status": device.get("status", "Offline").capitalize(),
                    "last_data_received": device.get("last_data_received", "Never"),
                    "battery_level": float(device.get("battery_level", 0)),
                    "temperature": float(device.get("temperature", 0)),
                    "humidity": float(device.get("humidity", 0)),
                })

            context = {
                "devices": device_list,
                "user_email": user_email,
                "user_role": role,
                "username": username,
                "stats": {
                    "total_devices": total_devices,
                    "online_devices": online_devices,
                    "warning_devices": warning_devices,
                    "offline_devices": offline_devices
                },
                "user": user  # Pass full user object
            }
            
            return render(request, "dashboard.html", context)

        except Exception as e:
            print(f"Error in DashboardView: {str(e)}")
            return JsonResponse({"error": "Internal server error"}, status=500)


class DeviceDataAPI(View):
    def get(self, request):
        device_id = request.GET.get("device_id")
        if not device_id:
            return JsonResponse({"error": "Missing device_id"}, status=400)

        try:
            response = devices_table.get_item(Key={"device_id": device_id})
            device = response.get("Item")
            if not device:
                return JsonResponse({"error": "Device not found"}, status=404)
            
            # Convert Decimal to float
            for key in ['battery_level', 'temperature', 'humidity']:
                if key in device and isinstance(device[key], Decimal):
                    device[key] = float(device[key])
            
            return JsonResponse(device, status=200)
        except ClientError as e:
            print(f"⚠️ DynamoDB Query Error: {e}")
            return JsonResponse({"error": "Failed to fetch device data"}, status=500)


@csrf_exempt
@require_POST
def register_device(request):
    """Registers a new device linked to a user's account."""
    try:
        data = json.loads(request.body.decode('utf-8'))
        
        # Validate required fields
        required_fields = ["name", "email", "account_id"]
        if not all(field in data for field in required_fields):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        # Verify user exists
        user = UserModel.get_user_by_account_id(data['account_id'])
        if not user:
            return JsonResponse({"error": "Invalid account_id"}, status=400)

        # Prepare device data
        device_id = data.get("device_id", str(uuid.uuid4()))
        created_at = datetime.utcnow().isoformat()
        
        device_data = {
            "device_id": device_id,
            "name": data["name"],
            "email": data["email"],
            "account_id": data["account_id"],
            "status": "Offline",
            "created_at": created_at,
            "last_data_received": "Never"
        }

        # Add optional fields with proper type conversion
        for field in ['temperature', 'humidity', 'battery_level']:
            if field in data and data[field] is not None:
                try:
                    device_data[field] = Decimal(str(data[field]))
                except:
                    device_data[field] = Decimal('0')

        # Save to DynamoDB
        devices_table.put_item(Item=device_data)
        
        # Convert Decimals to floats for response
        response_data = device_data.copy()
        for key in ['temperature', 'humidity', 'battery_level']:
            if key in response_data and isinstance(response_data[key], Decimal):
                response_data[key] = float(response_data[key])
        
        return JsonResponse({
            "message": "Device registered successfully",
            "device": response_data
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    except Exception as e:
        print(f"Error in register_device: {str(e)}")
        return JsonResponse({"error": f"Internal server error: {str(e)}"}, status=500)