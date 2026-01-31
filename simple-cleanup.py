#!/usr/bin/env python3
"""
Simple cleanup script for old gateway resources
"""

import boto3
from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient

def cleanup_cognito_resources():
    """Clean up old Cognito resources"""
    
    region_name = boto3.session.Session().region_name
    cognito_client = boto3.client('cognito-idp', region_name=region_name)
    
    # Old Cognito resources
    old_user_pool_id = "us-east-1_gHW2Os29E"
    old_domain_prefix = "agentcore-32febcd3"  # Corrected domain
    
    print("🧹 Cleaning up old Cognito resources...")
    
    try:
        # First, delete the domain
        print(f"🚀 Deleting domain: {old_domain_prefix}")
        try:
            cognito_client.delete_user_pool_domain(
                Domain=old_domain_prefix,
                UserPoolId=old_user_pool_id
            )
            print("✅ Domain deleted")
        except Exception as e:
            print(f"⚠️  Domain: {str(e)}")
        
        # Then delete the user pool
        print(f"🚀 Deleting User Pool: {old_user_pool_id}")
        try:
            cognito_client.delete_user_pool(UserPoolId=old_user_pool_id)
            print("✅ User Pool deleted")
        except Exception as e:
            print(f"⚠️  User Pool: {str(e)}")
            
    except Exception as e:
        print(f"❌ Cleanup error: {str(e)}")

def list_current_resources():
    """List current gateway and Cognito resources"""
    
    region_name = boto3.session.Session().region_name
    cognito_client = boto3.client('cognito-idp', region_name=region_name)
    
    print("\n📋 Current Cognito User Pools:")
    try:
        response = cognito_client.list_user_pools(MaxResults=10)
        pools = response.get('UserPools', [])
        
        if pools:
            for pool in pools:
                pool_id = pool.get('Id')
                pool_name = pool.get('Name')
                print(f"  - {pool_name} ({pool_id})")
        else:
            print("  No user pools found")
            
    except Exception as e:
        print(f"⚠️  Could not list user pools: {str(e)}")

if __name__ == "__main__":
    print("🧹 Cleaning up old TestGateway Cognito resources")
    print("=" * 50)
    
    # Clean up old resources
    cleanup_cognito_resources()
    
    # List remaining resources
    list_current_resources()
    
    print("\n✅ Cleanup completed!")
    print("Current RestaurantAppGateway remains active and ready for use.")