from rest_framework.views import APIView

from rest_framework import status
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from .models import UserModel
from .serializers import UserRegisterSerializer, UserLoginSerializer

class RegisterUserView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user_id = UserModel.create_user(**serializer.validated_data)
            return Response({"message": "User registered successfully", "user_id": user_id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginUserView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = UserModel.get_user_by_email(email)

            if user and UserModel.verify_password(password, user['password']):
                return Response({"message": "Login successful", "role": user['role'], "account_id": user['account_id']})
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def login_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = UserModel.get_user_by_email(email)

        if user and UserModel.verify_password(password, user["password"]):
            request.session["user_id"] = user["id"]
            request.session["role"] = user["role"]
            return redirect("dashboard")
        else:
            return render(request, "users/login.html", {"error": "Invalid email or password."})
    
    return render(request, "users/login.html")

@csrf_exempt
def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        role = request.POST["role"]

        if UserModel.get_user_by_email(email):
            return render(request, "users/register.html", {"error": "Email already exists."})

        user_id, account_id = UserModel.create_user(username, email, password, role)
        request.session["user_id"] = user_id
        request.session["role"] = role
        request.session["account_id"] = account_id  # Store account ID in session

        return redirect("dashboard")

    return render(request, "users/register.html")
    
def dashboard_view(request):
    return render(request, "users/dashboard.html")

def logout_view(request):
    logout(request)  # Clears session
    return redirect("login")  # Redirects user to login page after logout