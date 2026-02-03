#!/usr/bin/env python3
"""
Complete AgentCore Cleanup Script
Removes runtime, memory, Lambda functions, DynamoDB tables, and all AWS resources
"""

import boto3
import subprocess
import time
import sys
from botocore.exceptions import ClientError

REGION = "us-east-1"
AGENT_NAME = "restaurant_discovery_agent"
MEMORY_ID = "restaurant_booking_memory-aOsBjaAma6"
STACK_NAME = "restaurant-booking-dev"
ECR_REPO = f"bedrock-agentcore-{AGENT_NAME}"

TABLES = ["Restaurants", "Users", "Bookings", "Payments", "IdempotencyCache"]

def print_header(message):
    print(f"\n{'='*60}")
    print(f"  {message}")
    print(f"{'='*60}\n")

def print_step(step, total, message):
    print(f"\n🚀 Step {step}/{total}: {message}")

def confirm_cleanup():
    print_header("Restaurant Booking System - Complete Cleanup")
    print("⚠️  WARNING: This will delete ALL resources:")
    print("  - AgentCore Runtime (restaurant_discovery_agent)")
    print("  - AgentCore Memory (restaurant_booking_memory)")
    print("  - Lambda functions (8 functions)")
    print("  - DynamoDB tables (5 tables)")
    print("  - SAM CloudFormation stack")
    print("  - ECR repository")
    print("")
    
    response = input("Continue with cleanup? (yes/no): ")
    return response.lower() == "yes"

def undeploy_agentcore_runtime():
    """Undeploy AgentCore Runtime"""
    print_step(1, 5, "Undeploying AgentCore Runtime...")
    try:
        result = subprocess.run(
            ["bedrock-agentcore", "undeploy", "--agent-name", AGENT_NAME],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            print("  ✅ Runtime undeployed successfully")
            return True
        else:
            print(f"  ⚠️  Runtime undeploy warning: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("  ⚠️  Undeploy timeout - runtime may already be deleted")
        return False
    except Exception as e:
        print(f"  ⚠️  Runtime undeploy error: {e}")
        return False

def delete_agentcore_memory():
    """Delete AgentCore Memory"""
    print_step(2, 5, "Deleting AgentCore Memory...")
    try:
        bedrock = boto3.client('bedrock-agent', region_name=REGION)
        bedrock.delete_memory(memoryId=MEMORY_ID)
        print("  ✅ Memory deleted successfully")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print("  ⚠️  Memory not found (already deleted)")
        else:
            print(f"  ⚠️  Memory deletion error: {e}")
        return False
    except Exception as e:
        print(f"  ⚠️  Memory deletion error: {e}")
        return False

def delete_cloudformation_stack():
    """Delete SAM CloudFormation Stack"""
    print_step(3, 5, "Deleting SAM CloudFormation stack...")
    try:
        cfn = boto3.client('cloudformation', region_name=REGION)
        
        # Check if stack exists
        try:
            cfn.describe_stacks(StackName=STACK_NAME)
        except ClientError as e:
            if 'does not exist' in str(e):
                print("  ⚠️  Stack not found (already deleted)")
                return False
        
        # Delete stack
        cfn.delete_stack(StackName=STACK_NAME)
        print("  ✅ Stack deletion initiated")
        
        # Wait for deletion
        print("  ⏳ Waiting for stack deletion (2-3 minutes)...")
        waiter = cfn.get_waiter('stack_delete_complete')
        waiter.wait(
            StackName=STACK_NAME,
            WaiterConfig={'Delay': 10, 'MaxAttempts': 30}
        )
        print("  ✅ Stack deleted successfully")
        return True
        
    except ClientError as e:
        print(f"  ⚠️  Stack deletion error: {e}")
        return False
    except Exception as e:
        print(f"  ⚠️  Stack deletion error: {e}")
        return False

def delete_dynamodb_tables():
    """Delete DynamoDB Tables"""
    print_step(4, 5, "Deleting DynamoDB tables...")
    dynamodb = boto3.client('dynamodb', region_name=REGION)
    deleted_count = 0
    
    for table in TABLES:
        try:
            print(f"  Deleting: {table}")
            dynamodb.delete_table(TableName=table)
            print(f"    ✅ {table} deleted")
            deleted_count += 1
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"    ⚠️  {table} not found")
            else:
                print(f"    ⚠️  {table} error: {e}")
        except Exception as e:
            print(f"    ⚠️  {table} error: {e}")
    
    if deleted_count > 0:
        print(f"\n  ✅ Deleted {deleted_count}/{len(TABLES)} tables")
    return deleted_count > 0

def delete_ecr_repository():
    """Delete ECR Repository"""
    print_step(5, 5, "Deleting ECR repository...")
    try:
        ecr = boto3.client('ecr', region_name=REGION)
        ecr.delete_repository(repositoryName=ECR_REPO, force=True)
        print("  ✅ ECR repository deleted")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'RepositoryNotFoundException':
            print("  ⚠️  Repository not found (already deleted)")
        else:
            print(f"  ⚠️  Repository deletion error: {e}")
        return False
    except Exception as e:
        print(f"  ⚠️  Repository deletion error: {e}")
        return False

def verify_cleanup():
    """Verify cleanup completion"""
    print_header("Verifying Cleanup")
    
    # Check Lambda functions
    print("Lambda functions remaining:")
    try:
        lambda_client = boto3.client('lambda', region_name=REGION)
        response = lambda_client.list_functions()
        functions = [f['FunctionName'] for f in response['Functions'] 
                    if any(kw in f['FunctionName'].lower() for kw in ['restaurant', 'book', 'payment', 'user', 'token'])]
        
        if functions:
            for func in functions:
                print(f"  ⚠️  {func}")
        else:
            print("  ✅ No Lambda functions found")
    except Exception as e:
        print(f"  ⚠️  Error checking Lambda: {e}")
    
    # Check DynamoDB tables
    print("\nDynamoDB tables remaining:")
    try:
        dynamodb = boto3.client('dynamodb', region_name=REGION)
        response = dynamodb.list_tables()
        tables = [t for t in response['TableNames'] 
                 if any(kw in t for kw in ['Restaurant', 'User', 'Booking', 'Payment', 'Idempotency'])]
        
        if tables:
            for table in tables:
                print(f"  ⚠️  {table}")
        else:
            print("  ✅ No DynamoDB tables found")
    except Exception as e:
        print(f"  ⚠️  Error checking DynamoDB: {e}")

def main():
    if not confirm_cleanup():
        print("\n❌ Cleanup cancelled")
        sys.exit(0)
    
    print("\n🧹 Starting cleanup...\n")
    
    # Execute cleanup steps
    undeploy_agentcore_runtime()
    delete_agentcore_memory()
    delete_cloudformation_stack()
    delete_dynamodb_tables()
    delete_ecr_repository()
    
    # Verify cleanup
    verify_cleanup()
    
    # Summary
    print_header("Cleanup Complete!")
    print("📋 What was removed:")
    print("  ❌ AgentCore Runtime")
    print("  ❌ AgentCore Memory")
    print("  ❌ Lambda functions")
    print("  ❌ DynamoDB tables")
    print("  ❌ CloudFormation stack")
    print("  ❌ ECR repository")
    print("")
    print("📋 Next Steps:")
    print("  1. Review verification output above")
    print("  2. Update .bedrock_agentcore.yaml if needed")
    print("  3. Redeploy with: bedrock-agentcore deploy")
    print("")

if __name__ == "__main__":
    main()
