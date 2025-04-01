import boto3
import time

# AWS Clients
apigateway = boto3.client("apigateway", region_name="us-east-1")
lambda_client = boto3.client("lambda", region_name="us-east-1")

# Lambda Function Name
LAMBDA_FUNCTION_NAME = "ProcessDeviceDataLambda"

# API Gateway Details
API_NAME = "SensorCloudAPI"
STAGE_NAME = "prod"

def create_api_gateway():
    """Creates an API Gateway REST API."""
    try:
        response = apigateway.create_rest_api(
            name=API_NAME,
            description="API Gateway for SensorCloud Device Registration",
            endpointConfiguration={"types": ["REGIONAL"]},
        )
        api_id = response["id"]
        print(f"✅ API Gateway '{API_NAME}' created with ID: {api_id}")
    except apigateway.exceptions.GoneException:
        print(f"⚠️ API Gateway '{API_NAME}' already exists. Using the existing one.")
        # If the API exists, use the existing one
        api_id = get_api_id()
    
    return api_id

def get_api_id():
    """Gets the API Gateway ID if it already exists."""
    response = apigateway.get_rest_apis()
    for api in response["items"]:
        if api["name"] == API_NAME:
            return api["id"]
    return None

def get_root_resource_id(api_id):
    """Fetches the root resource ID of the API Gateway."""
    resources = apigateway.get_resources(restApiId=api_id)
    return resources["items"][0]["id"]

def create_resource(api_id, parent_id, path_part):
    """Creates a resource under API Gateway."""
    response = apigateway.create_resource(
        restApiId=api_id,
        parentId=parent_id,
        pathPart=path_part,
    )
    resource_id = response["id"]
    print(f"✅ Created resource '/{path_part}' with ID: {resource_id}")
    return resource_id

def create_post_method(api_id, resource_id):
    """Creates a POST method on the resource."""
    apigateway.put_method(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod="POST",
        authorizationType="NONE",
    )
    print("✅ POST method created on '/register-device'")

def link_lambda_to_api(api_id, resource_id):
    """Links API Gateway to the Lambda function."""
    lambda_arn = f"arn:aws:lambda:us-east-1:932875213474:function:{LAMBDA_FUNCTION_NAME}"

    apigateway.put_integration(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod="POST",
        type="AWS_PROXY",
        integrationHttpMethod="POST",
        uri=f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{lambda_arn}/invocations",
    )
    print(f"✅ Linked API Gateway to Lambda '{LAMBDA_FUNCTION_NAME}'")

def deploy_api(api_id):
    """Deploys the API Gateway to a stage."""
    response = apigateway.create_deployment(
        restApiId=api_id,
        stageName=STAGE_NAME,
    )
    print(f"✅ API Gateway deployed to stage '{STAGE_NAME}'")
    return response

def add_permission_to_lambda():
    """Gives API Gateway permission to invoke the Lambda function."""
    lambda_arn = f"arn:aws:lambda:us-east-1:932875213474:function:{LAMBDA_FUNCTION_NAME}"

    try:
        lambda_client.add_permission(
            FunctionName=LAMBDA_FUNCTION_NAME,
            StatementId="APIGatewayInvoke",
            Action="lambda:InvokeFunction",
            Principal="apigateway.amazonaws.com",
            SourceArn=f"arn:aws:execute-api:us-east-1:932875213474:*/*/POST/register-device",
        )
        print(f"✅ API Gateway permission added to Lambda '{LAMBDA_FUNCTION_NAME}'")
    except lambda_client.exceptions.ResourceConflictException:
        print("⚠️ Permission already exists for API Gateway to invoke Lambda")

def get_api_url(api_id):
    """Returns the full API Gateway URL."""
    return f"https://{api_id}.execute-api.us-east-1.amazonaws.com/{STAGE_NAME}/register-device"

def setup_api_gateway():
    """Main function to set up API Gateway programmatically."""
    api_id = create_api_gateway()
    root_id = get_root_resource_id(api_id)
    resource_id = create_resource(api_id, root_id, "register-device")
    create_post_method(api_id, resource_id)
    link_lambda_to_api(api_id, resource_id)
    add_permission_to_lambda()
    deploy_api(api_id)
    
    api_url = get_api_url(api_id)
    print(f"🚀 API Gateway setup complete! Use this URL:\n{api_url}")

if __name__ == "__main__":
    setup_api_gateway()
