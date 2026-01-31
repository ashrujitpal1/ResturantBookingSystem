#!/usr/bin/env python3
"""Upload versioned prompts to S3"""

import boto3
import os
from pathlib import Path

PROMPT_BUCKET = "restaurant-booking-prompts"
REGION = "us-east-1"
PROMPTS_DIR = "prompts"

def create_bucket_if_not_exists(s3_client, bucket_name, region):
    """Create S3 bucket if it doesn't exist"""
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✅ Bucket {bucket_name} already exists")
    except:
        try:
            if region == "us-east-1":
                s3_client.create_bucket(Bucket=bucket_name)
            else:
                s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region}
                )
            print(f"✅ Created bucket: {bucket_name}")
        except Exception as e:
            print(f"❌ Failed to create bucket: {e}")
            return False
    return True

def upload_prompts():
    """Upload all versioned prompts to S3"""
    s3 = boto3.client('s3', region_name=REGION)
    
    # Create bucket if needed
    if not create_bucket_if_not_exists(s3, PROMPT_BUCKET, REGION):
        print("⚠️  Skipping upload - bucket creation failed")
        return
    
    # Upload all prompt files
    prompts_path = Path(PROMPTS_DIR)
    uploaded = 0
    
    for prompt_file in prompts_path.rglob("system_prompt.md"):
        # Get relative path for S3 key
        relative_path = prompt_file.relative_to(PROMPTS_DIR)
        s3_key = f"prompts/{relative_path}"
        
        try:
            s3.upload_file(
                str(prompt_file),
                PROMPT_BUCKET,
                str(s3_key),
                ExtraArgs={'ContentType': 'text/markdown'}
            )
            print(f"✅ Uploaded: {s3_key}")
            uploaded += 1
        except Exception as e:
            print(f"❌ Failed to upload {prompt_file}: {e}")
    
    print(f"\n📊 Summary: {uploaded} prompts uploaded to s3://{PROMPT_BUCKET}/")

def list_prompts():
    """List all prompts in S3"""
    s3 = boto3.client('s3', region_name=REGION)
    
    try:
        response = s3.list_objects_v2(Bucket=PROMPT_BUCKET, Prefix="prompts/")
        
        if 'Contents' in response:
            print(f"\n📋 Prompts in s3://{PROMPT_BUCKET}/:")
            for obj in response['Contents']:
                print(f"   - {obj['Key']}")
        else:
            print("No prompts found in S3")
    except Exception as e:
        print(f"❌ Failed to list prompts: {e}")

if __name__ == "__main__":
    print("🚀 Uploading versioned prompts to S3...")
    print(f"   Bucket: {PROMPT_BUCKET}")
    print(f"   Region: {REGION}\n")
    
    upload_prompts()
    list_prompts()
    
    print("\n✅ Prompt upload complete!")
    print(f"\n💡 To use prompts, set environment variable:")
    print(f"   export PROMPT_BUCKET={PROMPT_BUCKET}")
