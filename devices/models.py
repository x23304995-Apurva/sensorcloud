import boto3
from botocore.exceptions import ClientError
import uuid
from datetime import datetime, timezone
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table_name = "Devices"

# Function to create the table with GSI if it doesn't exist
def create_devices_table():
    try:
        existing_tables = dynamodb.meta.client.list_tables()['TableNames']
        if table_name not in existing_tables:
            print(f"🔧 Creating DynamoDB table: {table_name}...")
            table = dynamodb.create_table(
                TableName=table_name,
                AttributeDefinitions=[
                    {'AttributeName': 'device_id', 'AttributeType': 'S'},
                    {'AttributeName': 'account_id', 'AttributeType': 'S'}  # Required for GSI
                ],
                KeySchema=[{'AttributeName': 'device_id', 'KeyType': 'HASH'}],
                BillingMode='PAY_PER_REQUEST',
                GlobalSecondaryIndexes=[
                    {
                        "IndexName": "AccountIdIndex",
                        "KeySchema": [{"AttributeName": "account_id", "KeyType": "HASH"}],
                        "Projection": {"ProjectionType": "ALL"}
                    }
                ]
            )
            table.wait_until_exists()
            print(f"✅ Table '{table_name}' created successfully with GSI 'AccountIdIndex'.")
        else:
            print(f"✅ Table '{table_name}' already exists.")
            ensure_gsi_exists()
    except ClientError as e:
        print(f" Error checking/creating DynamoDB table: {e}")


def ensure_gsi_exists():
    """Checks if the 'AccountIdIndex' GSI exists and creates it if missing."""
    table = dynamodb.Table(table_name)

    try:
        # ✅ Prevent NoneType error
        existing_indexes = table.global_secondary_indexes or []  # Ensures it's a list
        index_names = [index["IndexName"] for index in existing_indexes]

        if "AccountIdIndex" not in index_names:
            print("⚠️ AccountIdIndex not found. Creating it now...")

            # ✅ Create GSI for account_id
            response = dynamodb.meta.client.update_table(
                TableName=table_name,
                AttributeDefinitions=[
                    {"AttributeName": "account_id", "AttributeType": "S"}
                ],
                GlobalSecondaryIndexUpdates=[
                    {
                        "Create": {
                            "IndexName": "AccountIdIndex",
                            "KeySchema": [
                                {"AttributeName": "account_id", "KeyType": "HASH"}
                            ],
                            "Projection": {"ProjectionType": "ALL"},
                        }
                    }
                ],
            )

            print("✅ AccountIdIndex is being created. This may take a few minutes.")

        else:
            print("✅ AccountIdIndex already exists.")

    except ClientError as e:
        print(f"⚠️ Error checking/creating GSI: {e}")

# Ensure the table and GSI exist at startup
create_devices_table()

# Define Device Model
class DeviceModel:
    table = dynamodb.Table(table_name)

    @staticmethod
    def create_device(name, account_id, registered_by):
        """Registers a new IoT device in DynamoDB with the user who registered it."""
        device_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        device_data = {
            'device_id': device_id,
            'name': name,
            'account_id': account_id,
            'status': 'Disconnected',
            'registered_by': registered_by,  # Store user who registered the device
            'temperature': None,
            'humidity': None,
            'created_at': timestamp,
            'last_modified': timestamp
        }

        DeviceModel.table.put_item(Item=device_data)
        return device_id
