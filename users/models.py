import boto3
from botocore.exceptions import ClientError
import uuid
import bcrypt

# Initialize DynamoDB
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table_name = "Users"

# Function to create the table if it doesn't exist
def create_users_table():
    try:
        existing_tables = dynamodb.meta.client.list_tables()["TableNames"]
        if table_name not in existing_tables:
            print(f"🔧 Creating DynamoDB table: {table_name}...")
            table = dynamodb.create_table(
                TableName=table_name,
                AttributeDefinitions=[
                    {"AttributeName": "id", "AttributeType": "S"},  # UUID as string
                    {"AttributeName": "account_id", "AttributeType": "S"},  # UUID as string
                ],
                KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
                BillingMode="PAY_PER_REQUEST",
                GlobalSecondaryIndexes=[
                    {
                        "IndexName": "AccountIdIndex",
                        "KeySchema": [{"AttributeName": "account_id", "KeyType": "HASH"}],
                        "Projection": {"ProjectionType": "ALL"},
                    }
                ],
            )
            table.wait_until_exists()
            print(f"✅ Table '{table_name}' created successfully with GSI 'AccountIdIndex'.")
        else:
            print(f"✅ Table '{table_name}' already exists.")
            ensure_gsi_exists()
    except ClientError as e:
        print(f"⚠️ Error checking/creating DynamoDB table: {e}")

# Ensure GSI exists
def ensure_gsi_exists():
    """Checks if 'AccountIdIndex' exists, creates it if missing."""
    table = dynamodb.Table(table_name)

    try:
        existing_indexes = table.global_secondary_indexes or []  # Avoid NoneType error
        index_names = [index["IndexName"] for index in existing_indexes]

        if "AccountIdIndex" not in index_names:
            print("⚠️ AccountIdIndex not found. Creating it now...")
            response = dynamodb.meta.client.update_table(
                TableName=table_name,
                AttributeDefinitions=[{"AttributeName": "account_id", "AttributeType": "S"}],
                GlobalSecondaryIndexUpdates=[
                    {
                        "Create": {
                            "IndexName": "AccountIdIndex",
                            "KeySchema": [{"AttributeName": "account_id", "KeyType": "HASH"}],
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

# Ensure the table and index are created
create_users_table()

# Define UserModel
class UserModel:
    table = dynamodb.Table(table_name)

    @staticmethod
    def generate_account_id():
        """Generates a unique account ID using UUID."""
        return str(uuid.uuid4())  # Generates a unique identifier using UUID

    @staticmethod
    def create_user(username, email, password, role):
        """Registers a new user with a unique account ID."""
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        user_id = str(uuid.uuid4())  # Ensure this is a string (UUID)
        account_id = UserModel.generate_account_id()  # Account ID as UUID string

        try:
            UserModel.table.put_item(
                Item={
                    "id": user_id,  # Store UUID as string
                    "username": username,
                    "email": email,
                    "password": hashed_password,
                    "role": role,
                    "account_id": account_id,  # Save UUID as account_id
                }
            )
            return user_id, account_id
        except ClientError as e:
            print(f"⚠️ Error creating user: {e}")
            return None, None

    @staticmethod
    def get_user_by_email(email):
        """Fetches a user by email."""
        try:
            response = UserModel.table.scan(
                FilterExpression="email = :email", ExpressionAttributeValues={":email": email}
            )
            # Check if any items are found
            if response.get("Items"):
                return response["Items"][0]  # Return the first user if found
            else:
                return None  # Return None if no user is found
        except ClientError as e:
            print(f"⚠️ Error fetching user by email: {e}")
            return None

    @staticmethod
    def get_user_by_account_id(account_id):
        """Fetches a user by account ID using Global Secondary Index."""
        try:
            response = UserModel.table.query(
                IndexName="AccountIdIndex",
                KeyConditionExpression="account_id = :account_id",
                ExpressionAttributeValues={":account_id": account_id},
            )
            if response.get("Items"):
                return response["Items"][0]  # Return the first user if found
            else:
                return None  # Return None if no user is found
        except ClientError as e:
            print(f"⚠️ Error fetching user by account ID: {e}")
            return None

    @staticmethod
    def verify_password(input_password, stored_password):
        """Verifies if the input password matches the stored hashed password."""
        return bcrypt.checkpw(input_password.encode("utf-8"), stored_password.encode("utf-8"))
        
        
    @classmethod
    def get_user_by_id(cls, user_id):
        """New method to get user by UUID"""
        response = cls.table.get_item(Key={'id': user_id})
        return response.get('Item')
