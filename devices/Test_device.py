import requests
import json
import time

# Change this to your actual Cloud9 environment URL
BASE_URL = "http://localhost:8080/api/devices/"

# Test device details
test_device = {
    "name": "Test Sensor",
    "account_id": "001"  # Use a valid account ID
}

def test_create_device():
    """Test creating a new device."""
    print("🔄 Creating a new device...")
    response = requests.post(BASE_URL, json=test_device)
    if response.status_code == 201:
        device_id = response.json().get("device_id")
        print(f" Device created successfully! Device ID: {device_id}")
        return device_id
    else:
        print(f"❌ Failed to create device: {response.text}")
        return None

def test_get_devices():
    """Test fetching all devices for an account."""
    print("\n🔄 Fetching all devices...")
    response = requests.get(BASE_URL, params={"account_id": test_device["account_id"]})
    if response.status_code == 200:
        devices = response.json()
        print(f"✅ Retrieved {len(devices)} devices:")
        for device in devices:
            print(json.dumps(device, indent=4))
    else:
        print(f"❌ Failed to fetch devices: {response.text}")

def test_update_device(device_id):
    """Test updating a device with new sensor data."""
    print(f"\n🔄 Updating device {device_id} with sensor data...")
    update_data = {
        "temperature": 24.5,
        "humidity": 60,
        "battery_level": 50  # Should set status to "Active"
    }
    response = requests.put(f"{BASE_URL}{device_id}/", json=update_data)
    if response.status_code == 200:
        print(f"✅ Device {device_id} updated successfully!")
    else:
        print(f"❌ Failed to update device: {response.text}")

def test_get_device(device_id):
    """Test retrieving a specific device."""
    print(f"\n🔄 Fetching device {device_id}...")
    response = requests.get(f"{BASE_URL}{device_id}/")
    if response.status_code == 200:
        device = response.json()
        print("✅ Device details:")
        print(json.dumps(device, indent=4))
    else:
        print(f"❌ Failed to fetch device: {response.text}")

def test_auto_status_update(device_id):
    """Test if the device status changes to Idle after 60 minutes."""
    print(f"\n⏳ Simulating device inactivity for status update...")
    time.sleep(2)  # Simulating wait time (Use actual wait time in real cases)
    
    response = requests.get(f"{BASE_URL}{device_id}/")
    if response.status_code == 200:
        device = response.json()
        print("🔄 Checking device status after simulated inactivity...")
        print(json.dumps(device, indent=4))
        if device["status"] == "Idle":
            print(f"✅ Device {device_id} is correctly set to Idle after inactivity!")
        else:
            print(f"⚠️ Device status is {device['status']} instead of 'Idle'.")
    else:
        print(f"❌ Failed to fetch device: {response.text}")

def test_delete_device(device_id):
    """Test deleting a device."""
    print(f"\n🔄 Deleting device {device_id}...")
    response = requests.delete(f"{BASE_URL}{device_id}/")
    if response.status_code == 200:
        print(f"✅ Device {device_id} deleted successfully!")
    else:
        print(f"❌ Failed to delete device: {response.text}")

if __name__ == "__main__":
    print("🚀 Running Device API Tests...\n")
    
    # Step 1: Create a device
    device_id = test_create_device()
    if device_id:
        # Step 2: Get all devices
        test_get_devices()

        # Step 3: Update the device with sensor data
        test_update_device(device_id)

        # Step 4: Fetch the device details
        test_get_device(device_id)

        # Step 5: Simulate status auto-update (Idle mode)
        test_auto_status_update(device_id)

        # Step 6: Delete the device
        test_delete_device(device_id)

    print("\n🎉 All tests completed!")
