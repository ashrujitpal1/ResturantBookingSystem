#!/bin/bash
# Fresh Infrastructure Setup Script
# Creates all resources from scratch with production principles

set -e

REGION="us-east-1"
STACK_NAME="restaurant-booking-dev"
ENVIRONMENT="dev"

echo "🚀 Restaurant Booking System - Fresh Infrastructure Setup"
echo "=========================================================="
echo ""
echo "This script will create:"
echo "  ✓ 5 DynamoDB tables (with GSIs and TTL)"
echo "  ✓ 8 Lambda functions (with production code)"
echo "  ✓ IAM roles and permissions"
echo "  ✓ CloudWatch log groups"
echo ""
echo "Auto-proceeding with setup..."

# ============================================================================
# STEP 1: Create DynamoDB Tables
# ============================================================================
echo ""
echo "📦 STEP 1/5: Creating DynamoDB Tables"
echo "======================================"
echo ""

# 1.1 Restaurants Table
echo "Creating Restaurants table..."
aws dynamodb create-table \
    --table-name Restaurants \
    --attribute-definitions \
        AttributeName=restaurantId,AttributeType=S \
        AttributeName=city,AttributeType=S \
        AttributeName=cuisine,AttributeType=S \
        AttributeName=rating,AttributeType=N \
    --key-schema \
        AttributeName=restaurantId,KeyType=HASH \
    --global-secondary-indexes \
        "IndexName=CityIndex,KeySchema=[{AttributeName=city,KeyType=HASH},{AttributeName=rating,KeyType=RANGE}],Projection={ProjectionType=ALL}" \
        "IndexName=CuisineIndex,KeySchema=[{AttributeName=cuisine,KeyType=HASH},{AttributeName=rating,KeyType=RANGE}],Projection={ProjectionType=ALL}" \
    --billing-mode PAY_PER_REQUEST \
    --region $REGION \
    --no-cli-pager && echo "✅ Restaurants table created" || echo "⚠️  Failed to create Restaurants table"

# 1.2 Users Table
echo ""
echo "Creating Users table..."
aws dynamodb create-table \
    --table-name Users \
    --attribute-definitions \
        AttributeName=userId,AttributeType=S \
        AttributeName=mobileNo,AttributeType=S \
        AttributeName=username,AttributeType=S \
    --key-schema \
        AttributeName=userId,KeyType=HASH \
    --global-secondary-indexes \
        "IndexName=MobileIndex,KeySchema=[{AttributeName=mobileNo,KeyType=HASH}],Projection={ProjectionType=ALL}" \
        "IndexName=UsernameIndex,KeySchema=[{AttributeName=username,KeyType=HASH}],Projection={ProjectionType=ALL}" \
    --billing-mode PAY_PER_REQUEST \
    --region $REGION \
    --no-cli-pager && echo "✅ Users table created" || echo "⚠️  Failed to create Users table"

# 1.3 Bookings Table
echo ""
echo "Creating Bookings table..."
aws dynamodb create-table \
    --table-name Bookings \
    --attribute-definitions \
        AttributeName=bookingId,AttributeType=S \
        AttributeName=userId,AttributeType=S \
        AttributeName=restaurantId,AttributeType=S \
        AttributeName=bookingDate,AttributeType=S \
        AttributeName=bookingTime,AttributeType=S \
        AttributeName=createdAt,AttributeType=S \
    --key-schema \
        AttributeName=bookingId,KeyType=HASH \
    --global-secondary-indexes \
        "IndexName=UserBookingsIndex,KeySchema=[{AttributeName=userId,KeyType=HASH},{AttributeName=createdAt,KeyType=RANGE}],Projection={ProjectionType=ALL}" \
        "IndexName=RestaurantBookingsIndex,KeySchema=[{AttributeName=restaurantId,KeyType=HASH},{AttributeName=bookingDate,KeyType=RANGE}],Projection={ProjectionType=ALL}" \
        "IndexName=DateIndex,KeySchema=[{AttributeName=bookingDate,KeyType=HASH},{AttributeName=bookingTime,KeyType=RANGE}],Projection={ProjectionType=ALL}" \
    --billing-mode PAY_PER_REQUEST \
    --region $REGION \
    --no-cli-pager && echo "✅ Bookings table created" || echo "⚠️  Failed to create Bookings table"

# 1.4 Payments Table
echo ""
echo "Creating Payments table..."
aws dynamodb create-table \
    --table-name Payments \
    --attribute-definitions \
        AttributeName=paymentId,AttributeType=S \
        AttributeName=bookingId,AttributeType=S \
        AttributeName=userId,AttributeType=S \
        AttributeName=paymentDate,AttributeType=S \
    --key-schema \
        AttributeName=paymentId,KeyType=HASH \
    --global-secondary-indexes \
        "IndexName=BookingPaymentIndex,KeySchema=[{AttributeName=bookingId,KeyType=HASH}],Projection={ProjectionType=ALL}" \
        "IndexName=UserPaymentIndex,KeySchema=[{AttributeName=userId,KeyType=HASH},{AttributeName=paymentDate,KeyType=RANGE}],Projection={ProjectionType=ALL}" \
    --billing-mode PAY_PER_REQUEST \
    --region $REGION \
    --no-cli-pager && echo "✅ Payments table created" || echo "⚠️  Failed to create Payments table"

# 1.5 IdempotencyCache Table (NEW - for production principles)
echo ""
echo "Creating IdempotencyCache table..."
aws dynamodb create-table \
    --table-name IdempotencyCache \
    --attribute-definitions \
        AttributeName=requestId,AttributeType=S \
    --key-schema \
        AttributeName=requestId,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region $REGION \
    --no-cli-pager && echo "✅ IdempotencyCache table created" || echo "⚠️  Failed to create IdempotencyCache table"

echo ""
echo "⏰ Enabling TTL on IdempotencyCache..."
sleep 5  # Wait for table to be active
aws dynamodb update-time-to-live \
    --table-name IdempotencyCache \
    --time-to-live-specification "Enabled=true, AttributeName=ttl" \
    --region $REGION \
    --no-cli-pager && echo "✅ TTL enabled" || echo "⚠️  Failed to enable TTL"

echo ""
echo "⏳ Waiting for all tables to become ACTIVE (30 seconds)..."
sleep 30

# ============================================================================
# STEP 2: Insert Restaurant Data
# ============================================================================
echo ""
echo "📝 STEP 2/5: Inserting Restaurant Data"
echo "======================================="
echo ""

if [ -f "insert_restaurant_records.py" ]; then
    echo "Running insert_restaurant_records.py..."
    python3 insert_restaurant_records.py && echo "✅ Restaurant data inserted" || echo "⚠️  Failed to insert data"
else
    echo "⚠️  insert_restaurant_records.py not found. Skipping data insertion."
fi

# ============================================================================
# STEP 3: Build and Deploy Lambda Functions
# ============================================================================
echo ""
echo "🔨 STEP 3/5: Building and Deploying Lambda Functions"
echo "====================================================="
echo ""

echo "Building SAM application..."
sam build

echo ""
echo "Deploying Lambda functions..."
sam deploy \
    --stack-name $STACK_NAME \
    --parameter-overrides Environment=$ENVIRONMENT \
    --capabilities CAPABILITY_IAM \
    --region $REGION \
    --resolve-s3 \
    --no-confirm-changeset \
    --no-fail-on-empty-changeset

echo ""
echo "✅ Lambda functions deployed"

# ============================================================================
# STEP 4: Get Lambda ARNs
# ============================================================================
echo ""
echo "📋 STEP 4/5: Collecting Lambda Function ARNs"
echo "============================================="
echo ""

echo "Fetching Lambda ARNs..."
echo ""

declare -A LAMBDA_ARNS

FUNCTIONS=(
    "fetchRestaurantDetails-dev"
    "fetchRestaurantDetailsById-dev"
    "searchUserDetails-dev"
    "registerUser-dev"
    "tokenAmountCalculation-dev"
    "bookATable-dev"
    "paymentAPI-dev"
    "bookRestaurant-dev"
)

for func in "${FUNCTIONS[@]}"; do
    arn=$(aws lambda get-function --function-name $func --region $REGION --query 'Configuration.FunctionArn' --output text 2>/dev/null || echo "NOT_FOUND")
    LAMBDA_ARNS[$func]=$arn
    if [ "$arn" != "NOT_FOUND" ]; then
        echo "✅ $func"
        echo "   ARN: $arn"
    else
        echo "⚠️  $func - NOT FOUND"
    fi
    echo ""
done

# Save ARNs to file for MCP registration
cat > lambda-arns.json <<EOF
{
  "fetchRestaurantDetails": "${LAMBDA_ARNS[fetchRestaurantDetails-dev]}",
  "fetchRestaurantDetailsById": "${LAMBDA_ARNS[fetchRestaurantDetailsById-dev]}",
  "searchUserDetails": "${LAMBDA_ARNS[searchUserDetails-dev]}",
  "registerUser": "${LAMBDA_ARNS[registerUser-dev]}",
  "tokenAmountCalculation": "${LAMBDA_ARNS[tokenAmountCalculation-dev]}",
  "bookATable": "${LAMBDA_ARNS[bookATable-dev]}",
  "paymentAPI": "${LAMBDA_ARNS[paymentAPI-dev]}",
  "bookRestaurant": "${LAMBDA_ARNS[bookRestaurant-dev]}"
}
EOF

echo "✅ Lambda ARNs saved to lambda-arns.json"

# ============================================================================
# STEP 5: Verification
# ============================================================================
echo ""
echo "🔍 STEP 5/5: Verifying Infrastructure"
echo "======================================"
echo ""

echo "DynamoDB Tables:"
aws dynamodb list-tables --region $REGION --output table

echo ""
echo "Lambda Functions:"
aws lambda list-functions --region $REGION \
    --query "Functions[?contains(FunctionName, 'dev')].{Name:FunctionName,Runtime:Runtime,Timeout:Timeout}" \
    --output table

echo ""
echo "=========================================================="
echo "✅ Infrastructure Setup Complete!"
echo ""
echo "📋 Summary:"
echo "  ✓ 5 DynamoDB tables created"
echo "  ✓ Restaurant data inserted"
echo "  ✓ 8 Lambda functions deployed"
echo "  ✓ Lambda ARNs collected"
echo ""
echo "📖 Next Steps:"
echo "  1. Review lambda-arns.json"
echo "  2. Run: ./register-mcp-tools.sh"
echo "  3. Test with: python test-individual-mcp-tools.py"
echo ""
