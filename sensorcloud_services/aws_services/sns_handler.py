import boto3
import json
from django.conf import settings

sns_client = boto3.client('sns', region_name='us-east-1')
TOPIC_NAME = "UserRegistrationTopic"


def get_sns_topic_arn():
    """Returns SNS topic ARN from settings or creates one as fallback."""
    try:
        return settings.SNS_TOPIC_ARN
    except AttributeError:
        print("⚠️ SNS_TOPIC_ARN not found in settings. Creating fallback topic...")
        return create_sns_topic()


def create_sns_topic():
    """Create SNS topic (only used as a fallback)."""
    try:
        response = sns_client.create_topic(Name=TOPIC_NAME)
        print(f"✅ Fallback SNS topic created: {response['TopicArn']}")
        return response['TopicArn']
    except Exception as e:
        print(f"⚠️ Error creating SNS topic: {e}")
        return None


def subscribe_email_to_sns(email, topic_arn):
    """Subscribe the given email to the SNS topic."""
    try:
        sns_client.subscribe(
            TopicArn=topic_arn,
            Protocol='email',
            Endpoint=email
        )
        print(f"✅ Subscribed {email} to SNS topic.")
    except Exception as e:
        print(f"⚠️ Error subscribing email: {e}")


def send_email_via_sns(email, account_id, username, role, sns_topic_arn):
    """Send a JSON-formatted email via SNS with account_id, username, and role."""
    try:
        payload = json.dumps({
            "email": email,
            "username": username,
            "role": role,
            "account_id": account_id
        }, indent=4)

        sns_client.publish(
            TopicArn=sns_topic_arn,
            Subject="Your User Registration Details",
            Message=f"Hello {username},\n\nYour registration is successful. Please find your account details below:\n\n{payload}",
        )
        print(f"✅ JSON email sent to {email} with role and username")
    except Exception as e:
        print(f"⚠️ Error sending email via SNS: {e}")
