import requests
import json

# Change this to your Cloud9 environment URL
CLOUD9_HOST = "http://localhost:8080"

# API Endpoints
REGISTER_URL = f"{CLOUD9_HOST}/api/users/register/"
LOGIN_URL = f"{CLOUD9_HOST}/api/users/login/"

# Test User Data
test_user = {
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "Test@123",
    "role": "Engineer",
    "account_id": "acc001"
}

def test_api():
    print("🔄 Testing Registration API...")
    try:
        response = requests.post(REGISTER_URL, json=test_user, verify=False, timeout=10)
        print(f"📩 Register API Response: {response.status_code}")
        print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error in Registration API: {e}")

    print("\n🔄 Testing Login API...")
    try:
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        response = requests.post(LOGIN_URL, json=login_data, verify=False, timeout=10)
        print(f"📩 Login API Response: {response.status_code}")
        print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error in Login API: {e}")

if __name__ == "__main__":
    test_api()
