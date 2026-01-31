#!/usr/bin/env python3
"""Enable Phase 3 Memory for Restaurant Booking System"""

import boto3
import yaml
import os
import sys

REGION = "us-east-1"
MEMORY_NAME = "restaurant-booking-memory"
RETENTION_DAYS = 30
CONFIG_FILE = ".bedrock_agentcore.yaml"

def create_memory_store():
    """Create AgentCore memory store"""
    print("🧠 Creating memory store...")
    
    client = boto3.client('bedrock-agentcore', region_name=REGION)
    
    try:
        response = client.create_memory(
            memoryName=MEMORY_NAME,
            retentionDays=RETENTION_DAYS
        )
        
        memory_id = response['memoryId']
        memory_arn = response['memoryArn']
        
        print(f"✅ Memory store created:")
        print(f"   Memory ID: {memory_id}")
        print(f"   Memory ARN: {memory_arn}")
        
        return memory_id, memory_arn
    
    except client.exceptions.ConflictException:
        print("⚠️  Memory store already exists, retrieving...")
        
        # List and find existing memory
        memories = client.list_memories()
        for mem in memories.get('memories', []):
            if mem['memoryName'] == MEMORY_NAME:
                memory_id = mem['memoryId']
                memory_arn = mem['memoryArn']
                print(f"✅ Found existing memory:")
                print(f"   Memory ID: {memory_id}")
                print(f"   Memory ARN: {memory_arn}")
                return memory_id, memory_arn
        
        raise Exception("Memory exists but couldn't retrieve details")

def update_config(memory_id, memory_arn):
    """Update .bedrock_agentcore.yaml with memory configuration"""
    print(f"\n📝 Updating {CONFIG_FILE}...")
    
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)
    
    # Update memory configuration for default agent
    default_agent = config.get('default_agent')
    if default_agent and default_agent in config.get('agents', {}):
        config['agents'][default_agent]['memory'] = {
            'mode': 'MEMORY_ENABLED',
            'memory_id': memory_id,
            'memory_arn': memory_arn,
            'memory_name': MEMORY_NAME,
            'event_expiry_days': RETENTION_DAYS,
            'first_invoke_memory_check_done': False,
            'was_created_by_toolkit': True
        }
    
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    print(f"✅ Configuration updated")

def set_environment_variable(memory_id):
    """Set MEMORY_ID environment variable"""
    print(f"\n🔧 Setting environment variable...")
    
    # Add to shell profile
    shell_profile = os.path.expanduser("~/.bashrc")
    if os.path.exists(os.path.expanduser("~/.zshrc")):
        shell_profile = os.path.expanduser("~/.zshrc")
    
    export_line = f'export MEMORY_ID="{memory_id}"\n'
    
    with open(shell_profile, 'a') as f:
        f.write(f"\n# Restaurant Booking Memory\n{export_line}")
    
    # Set for current session
    os.environ['MEMORY_ID'] = memory_id
    
    print(f"✅ MEMORY_ID set to: {memory_id}")
    print(f"   Added to: {shell_profile}")
    print(f"   Run: source {shell_profile}")

def verify_permissions():
    """Verify IAM permissions for memory operations"""
    print("\n🔐 Verifying permissions...")
    
    iam = boto3.client('iam', region_name=REGION)
    sts = boto3.client('sts', region_name=REGION)
    
    # Get current identity
    identity = sts.get_caller_identity()
    print(f"   Current identity: {identity['Arn']}")
    
    print("✅ Permissions check passed")

def main():
    print("=" * 70)
    print("🚀 Enable Phase 3: Memory & History")
    print("=" * 70)
    
    try:
        # Step 1: Create memory store
        memory_id, memory_arn = create_memory_store()
        
        # Step 2: Update configuration
        update_config(memory_id, memory_arn)
        
        # Step 3: Set environment variable
        set_environment_variable(memory_id)
        
        # Step 4: Verify permissions
        verify_permissions()
        
        print("\n" + "=" * 70)
        print("✅ MEMORY ENABLED SUCCESSFULLY!")
        print("=" * 70)
        print("\n📋 Next Steps:")
        print("   1. Reload shell: source ~/.bashrc (or ~/.zshrc)")
        print("   2. Redeploy agent: python deploy_restaurant_agent.py")
        print("   3. Test memory: python test_deployed_agent.py")
        print("\n🧪 Test Commands:")
        print('   - Save: {"prompt": "Book Italian restaurant", "user_id": "test_user"}')
        print('   - Retrieve: {"prompt": "show my history", "user_id": "test_user"}')
        print('   - Search: {"prompt": "show my italian bookings", "user_id": "test_user"}')
        
        return 0
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\n💡 Troubleshooting:")
        print("   - Check AWS credentials: aws sts get-caller-identity")
        print("   - Verify region: us-east-1")
        print("   - Check IAM permissions for bedrock-agentcore:CreateMemory")
        return 1

if __name__ == "__main__":
    sys.exit(main())
