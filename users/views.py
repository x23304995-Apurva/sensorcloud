
from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
import boto3
from users.models import UserModel
from devices.models import DeviceModel
from .serializers import UserRegisterSerializer, UserLoginSerializer
from sensorcloud_services.aws_services.sns_handler import get_sns_topic_arn, subscribe_email_to_sns, send_email_via_sns

sns_client = boto3.client('sns', region_name='us-east-1')

class RegisterUserView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user_id, account_id = UserModel.create_user(**serializer.validated_data)

            username = serializer.validated_data['username']
            email = serializer.validated_data['email']
            role = serializer.validated_data['role']

            if role in ['Manager', 'Engineer']:
                topic_arn = get_sns_topic_arn()
                subscribe_email_to_sns(email, topic_arn)
                send_email_via_sns(email, account_id, username, role, topic_arn)

            return Response(
                {"message": "User registered successfully", "user_id": user_id, "account_id": account_id},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = UserModel.get_user_by_email(email)

        if user and UserModel.verify_password(password, user["password"]):
            # Set all necessary session variables
            request.session["user_id"] = user["id"]  # UUID string
            request.session["email"] = user["email"]
            request.session["role"] = user["role"]
            request.session["account_id"] = user["account_id"]
            
            # Avoid using Django's auth system
            request.session.modified = True
            return redirect(f"/dashboard/?email={email}")

        return render(request, "login.html", {"error": "Invalid email or password."})
    
    return render(request, "login.html")

@csrf_exempt
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")

        if UserModel.get_user_by_email(email):
            return render(request, "register.html", {"error": "Email already exists."})

        user_id, account_id = UserModel.create_user(username, email, password, role)

        if role in ['Manager', 'Engineer']:
            topic_arn = get_sns_topic_arn()
            subscribe_email_to_sns(email, topic_arn)
            send_email_via_sns(email, account_id, username, role, topic_arn)

        request.session["user_id"] = user_id
        request.session["role"] = role
        request.session["account_id"] = account_id

        return redirect(f"/dashboard/?email={email}")

    return render(request, "register.html")

def dashboard_view(request):
    user_email = request.GET.get("email")
    if not user_email:
        return redirect("login")

    user = UserModel.get_user_by_email(user_email)
    if not user:
        return render(request, "dashboard.html", {"error": "User not found."})

    account_id = user.get("account_id")
    role = user.get("role")

    try:
        devices = DeviceModel.table.scan(
            FilterExpression="account_id = :account_id",
            ExpressionAttributeValues={":account_id": account_id}  # Ensure account_id is string/UUID
        ).get("Items", [])
    except Exception as e:
        return render(request, "dashboard.html", {"error": f"Failed to retrieve devices: {str(e)}"})

    if role == "Manager":
        for device in devices:
            registered_user = UserModel.get_user_by_account_id(device.get("account_id"))
            if registered_user:
                device["registered_by"] = {
                    "user_id": registered_user.get("id"),
                    "name": registered_user.get("username"),
                    "role": registered_user.get("role"),
                }

    return render(request, "dashboard.html", {"user": user, "devices": devices})

def accounts_view(request):
    try:
        # Check if user is logged in by checking session
        if 'user_id' not in request.session:
            return redirect('login')

        # Get current user from DynamoDB using email (since get_user_by_id doesn't exist)
        current_user_email = request.session.get('email')
        if not current_user_email:
            return redirect('login')

        current_user = UserModel.get_user_by_email(current_user_email)
        if not current_user:
            return render(request, "accounts.html", {"error": "User not found in database."})

        # Get all users from DynamoDB with pagination
        all_users = UserModel.table.scan().get('Items', [])
        paginator = Paginator(all_users, 10)
        page_number = request.GET.get('page')
        users_page = paginator.get_page(page_number)

        context = {
            'user': current_user,
            'users': users_page,
        }

        return render(request, "accounts.html", context)

    except Exception as e:
        print(f"Error in accounts_view: {e}")
        return render(request, "accounts.html", {"error": "An error occurred while loading accounts."})

def logout_view(request):
    try:
        # Clear all session data
        request.session.flush()
        return redirect("login")
    except Exception as e:
        print(f"Error during logout: {e}")
        return redirect("login")