
SensorCloud - README

### Project Overview
SensorCloud is an IoT device management platform built using AWS and Django. The system allows users to register and manage IoT devices, monitor real-time sensor data, and receive notifications based on device status changes. The platform leverages various AWS services like SNS, DynamoDB, Lambda, API Gateway, SQS, EventBridge, and S3 to ensure scalability, reliability, and seamless operation.

### Dependencies

To run the SensorCloud project, make sure to install the following dependencies:

### Python Dependencies
- Django: Web framework for building the application.
  ```
  pip install django
  ```
- Django REST Framework: For building the API layer.
  ```
  pip install djangorestframework
  ```
- boto3: AWS SDK for Python, required to interact with AWS services.
  ```
  pip install boto3
  ```
- django-cors-headers: To handle Cross-Origin Resource Sharing (CORS).
  ```
  pip install django-cors-headers
  ```
- djangorestframework-simplejwt: For JWT-based authentication (if used).
  ```
  pip install djangorestframework-simplejwt
  ```
- django-environ: For handling environment variables in Django.
  ```
  pip install django-environ
  ```
- requests: For making HTTP requests (for API Gateway communication).
  ```
  pip install requests
  ```
- boto3: To interact with AWS services such as SQS, SNS, DynamoDB, Lambda, and S3.
  ```
  pip install boto3
  ```

## AWS Service Configuration

SensorCloud uses several AWS services, and you need to configure them before deployment.

### 1. AWS IAM (Identity and Access Management)
- IAM Roles: Ensure the application has access to required AWS services like SNS, SQS, Lambda, and DynamoDB. Create an IAM role with permissions for each service and attach it to your Lambda functions.

### 2. AWS DynamoDB
- DynamoDB Tables: Create the following tables in DynamoDB to store user and device data:
  - Users: Stores user data (e.g., username, email, account_id).
  - Devices: Stores device data (e.g., device name, account_id, status).
  - Ensure to use Global Secondary Indexes (GSI) for querying devices by account_id.

### 3. AWS SNS (Simple Notification Service)
- SNS Topics: Set up SNS topics for sending notifications about device status changes or new user registrations. Subscribe email addresses or endpoints to these topics.

### 4. AWS Lambda
- Lambda Functions: Create Lambda functions to process tasks such as:
  - Device status updates
  - User registration handling
  - Ensure these functions are triggered by events such as incoming data from devices, user actions, or scheduled tasks.

### 5. AWS API Gateway
- API Gateway Endpoints: Set up endpoints to handle device data ingestion and other API calls.
  - Create REST API resources and methods to communicate with the backend.

### 6. AWS SQS (Simple Queue Service)
- SQS Queues: Use SQS to queue incoming data from devices for processing by AWS Lambda.
  - Set up a queue for device data ingestion and processing.

### 7. AWS EventBridge
- EventBridge Rules: Set up rules to trigger Lambda functions periodically (e.g., every hour) for tasks like updating device statuses.

### 8. AWS S3
- S3 Buckets: Use S3 for storing Lambda code and logs. Ensure proper access permissions are configured for Lambda functions to retrieve the code from S3.

## Deployment Steps


### 1. Clone the Repository
Clone the project repository to your local machine or server:
```
git clone https://github.com/x23304995-Apurva/sensorcloud.git
```

### 2. Install Dependencies
Navigate to the project folder and install the required dependencies:
```
cd sensorcloud
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a .env file in the project root and configure the following environment variables:
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_REGION
- DYNAMODB_TABLE_USERS
- DYNAMODB_TABLE_DEVICES

### 4. Apply Migrations
Apply the Django database migrations to set up the database schema:
```
python manage.py migrate
```

### 5. Run the Development Server
Start the Django development server to test locally:
```
python manage.py runserver
```

### 6. Set up AWS Resources
1. Create DynamoDB Tables: Create the Users and Devices tables in DynamoDB.
2. Set up SNS Topics: Create topics for notifications.
3. Deploy Lambda Functions: Upload and deploy Lambda code via S3 or directly in the AWS Lambda console.
4. API Gateway: Set up API Gateway endpoints for handling incoming requests.
5. SQS Queues: Create SQS queues for handling device data.

### 7. Deploy to Production
For production deployment, use AWS Elastic Beanstalk to deploy the SensorCloud Django application, or deploy the backend manually using EC2 instances or other services. Ensure that all necessary AWS permissions are configured for access to SNS, Lambda, DynamoDB, and other services.

## Configuration Files

### 1. settings.py (Django)
Ensure that the settings in `settings.py` are correctly configured for AWS integration, such as database settings, CORS headers, and AWS credentials.

### 2. .env File
The .env file should contain your AWS credentials and configuration settings:
```
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_REGION=us-east-1
DYNAMODB_TABLE_USERS=users_table
DYNAMODB_TABLE_DEVICES=devices_table
```

### 3. AWS IAM Policy
Ensure that the IAM role attached to your Lambda functions includes the following permissions:
- sns:Publish
- dynamodb:PutItem
- sqs:SendMessage
- lambda:InvokeFunction

## License
This project is licensed under the MIT License - see the LICENSE file for details.
