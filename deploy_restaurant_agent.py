"""
Restaurant Discovery Agent - Deployment Script
Deploy to AWS Bedrock AgentCore Runtime
"""

import boto3
import json
import random
import string
from datetime import datetime

# Configuration
REGION = "us-east-1"
AGENT_NAME = "restaurant_discovery_agent"  # Use underscores, not hyphens
PROJECT_FOLDER = "restaurant_agent_runtime"

print("=" * 80)
print("🚀 Restaurant Discovery Agent - AgentCore Runtime Deployment")
print("=" * 80)

# Step 1: Load Gateway Configuration
print("\n📋 Step 1: Loading Gateway Configuration...")
try:
    with open('agentcore-gateway-config.json', 'r') as f:
        config = json.load(f)
    
    GATEWAY_ID = config['gateway_id']
    GATEWAY_URL = config['gateway_url']
    COGNITO_INFO = config['client_info']
    
    print(f"✅ Gateway ID: {GATEWAY_ID}")
    print(f"✅ Gateway URL: {GATEWAY_URL}")
except Exception as e:
    print(f"❌ Failed to load config: {e}")
    exit(1)

# Step 2: Create IAM Role for AgentCore Runtime
print("\n📋 Step 2: Creating IAM Role for AgentCore Runtime...")

iam_client = boto3.client('iam', region_name=REGION)
sts_client = boto3.client('sts', region_name=REGION)
account_id = sts_client.get_caller_identity()["Account"]

role_name = f"{AGENT_NAME}-runtime-role"

trust_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": ["bedrock.amazonaws.com", "bedrock-agentcore.amazonaws.com"]
            },
            "Action": "sts:AssumeRole"
        }
    ]
}

try:
    role = iam_client.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(trust_policy),
        Description=f"Execution role for {AGENT_NAME}"
    )
    role_arn = role['Role']['Arn']
    print(f"✅ Created role: {role_arn}")
    
    # Attach policies
    iam_client.attach_role_policy(
        RoleName=role_name,
        PolicyArn="arn:aws:iam::aws:policy/AmazonBedrockFullAccess"
    )
    iam_client.attach_role_policy(
        RoleName=role_name,
        PolicyArn="arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
    )
    print("✅ Attached AmazonBedrockFullAccess policy")
    print("✅ Attached AmazonEC2ContainerRegistryReadOnly policy")
    
except iam_client.exceptions.EntityAlreadyExistsException:
    role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
    print(f"✅ Using existing role: {role_arn}")

# Step 3: Create Memory Store
print("\n📋 Step 3: Creating AgentCore Memory Store...")

from bedrock_agentcore.memory import MemoryClient

memory_client = MemoryClient(region_name=REGION)
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
memory_name = f"RestaurantDiscovery_{timestamp}"

# Create memory role
memory_role_name = f"{AGENT_NAME}-memory-role"

try:
    memory_role = iam_client.create_role(
        RoleName=memory_role_name,
        AssumeRolePolicyDocument=json.dumps(trust_policy),
        Description=f"Memory role for {AGENT_NAME}"
    )
    memory_role_arn = memory_role['Role']['Arn']
    print(f"✅ Created memory role: {memory_role_arn}")
    
    iam_client.attach_role_policy(
        RoleName=memory_role_name,
        PolicyArn="arn:aws:iam::aws:policy/AmazonBedrockFullAccess"
    )
    
    # Wait for IAM role to propagate
    import time
    print("⏳ Waiting for IAM role to propagate (10 seconds)...")
    time.sleep(10)
    
except iam_client.exceptions.EntityAlreadyExistsException:
    memory_role_arn = f"arn:aws:iam::{account_id}:role/{memory_role_name}"
    print(f"✅ Using existing memory role: {memory_role_arn}")

# Create memory
try:
    print(f"Creating memory: {memory_name}...")
    memory = memory_client.create_memory_and_wait(
        name=memory_name,
        description="Restaurant Discovery Agent Memory",
        strategies=[],
        event_expiry_days=30,
        memory_execution_role_arn=memory_role_arn,
        max_wait=300,
        poll_interval=10
    )
    
    memory_id = memory['memoryId']
    print(f"✅ Memory created: {memory_id}")
    
    # Update config
    config['memory_id'] = memory_id
    config['memory_role_arn'] = memory_role_arn
    
    with open('agentcore-gateway-config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Updated configuration file")
    
except Exception as e:
    print(f"⚠️ Memory creation: {e}")
    memory_id = config.get('memory_id', '')

# Step 4: Deploy to AgentCore Runtime
print("\n📋 Step 4: Deploying to AgentCore Runtime...")
print("Using Starter Toolkit for deployment...")

try:
    from bedrock_agentcore_starter_toolkit.notebook import Runtime
    
    runtime = Runtime()
    
    print("Configuring runtime...")
    runtime.configure(
        entrypoint=f"{PROJECT_FOLDER}/restaurant_workflow.py",
        requirements_file=f"{PROJECT_FOLDER}/requirements.txt",
        agent_name=AGENT_NAME,
        auto_create_ecr=True,
        execution_role=role_arn
    )
    
    print("Launching agent...")
    runtime.launch()
    
    print("✅ Agent deployed successfully!")
    
    # Step 5: Test Deployment
    print("\n📋 Step 5: Testing Deployment...")
    
    test_payload = {
        "prompt": "Find Italian restaurants in New York",
        "user_id": "test_user_001",
        "session_id": "test_session_001",
        "search_params": {
            "city": "New York",
            "cuisine": "Italian"
        }
    }
    
    print("Invoking agent with test payload...")
    response = runtime.invoke(payload=test_payload)
    
    print(f"\n✅ Test Result: {response.get('status')}")
    print(f"📍 Intent: {response.get('intent')}")
    print(f"🍽️ Restaurants Found: {len(response.get('restaurant_results', []))}")
    print(f"\n📝 Response:\n{response.get('final_response')}")
    
    print("\n" + "=" * 80)
    print("🎉 Deployment Complete!")
    print("=" * 80)
    print(f"\n📦 Agent Name: {AGENT_NAME}")
    print(f"🌐 Gateway URL: {GATEWAY_URL}")
    print(f"🧠 Memory ID: {memory_id}")
    print(f"🔑 Role ARN: {role_arn}")
    print("\n✅ Ready for production use!")
    
except Exception as e:
    print(f"❌ Deployment failed: {e}")
    import traceback
    traceback.print_exc()
    
    print("\n📝 Manual Deployment Instructions:")
    print("1. Build Docker image:")
    print(f"   docker build -t {AGENT_NAME} {PROJECT_FOLDER}/")
    print("\n2. Tag for ECR:")
    print(f"   docker tag {AGENT_NAME}:latest {account_id}.dkr.ecr.{REGION}.amazonaws.com/{AGENT_NAME}:latest")
    print("\n3. Push to ECR:")
    print(f"   docker push {account_id}.dkr.ecr.{REGION}.amazonaws.com/{AGENT_NAME}:latest")
