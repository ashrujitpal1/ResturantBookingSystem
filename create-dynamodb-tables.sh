#!/bin/bash

# DynamoDB Table Creation Script for Restaurant Booking System
# Make sure AWS CLI is configured with proper credentials and region

echo "Creating DynamoDB tables for Restaurant Booking System..."

# 1. Create Restaurants Table
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
    'IndexName=CityIndex,KeySchema=[{AttributeName=city,KeyType=HASH},{AttributeName=rating,KeyType=RANGE}],Projection={ProjectionType=ALL}' \
    'IndexName=CuisineIndex,KeySchema=[{AttributeName=cuisine,KeyType=HASH},{AttributeName=rating,KeyType=RANGE}],Projection={ProjectionType=ALL}' \
  --billing-mode PAY_PER_REQUEST

echo "Waiting for Restaurants table to be active..."
aws dynamodb wait table-exists --table-name Restaurants

# 2. Create Users Table
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
    'IndexName=MobileIndex,KeySchema=[{AttributeName=mobileNo,KeyType=HASH}],Projection={ProjectionType=ALL}' \
    'IndexName=UsernameIndex,KeySchema=[{AttributeName=username,KeyType=HASH}],Projection={ProjectionType=ALL}' \
  --billing-mode PAY_PER_REQUEST

echo "Waiting for Users table to be active..."
aws dynamodb wait table-exists --table-name Users

# 3. Create Bookings Table
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
    'IndexName=UserBookingsIndex,KeySchema=[{AttributeName=userId,KeyType=HASH},{AttributeName=createdAt,KeyType=RANGE}],Projection={ProjectionType=ALL}' \
    'IndexName=RestaurantBookingsIndex,KeySchema=[{AttributeName=restaurantId,KeyType=HASH},{AttributeName=bookingDate,KeyType=RANGE}],Projection={ProjectionType=ALL}' \
    'IndexName=DateIndex,KeySchema=[{AttributeName=bookingDate,KeyType=HASH},{AttributeName=bookingTime,KeyType=RANGE}],Projection={ProjectionType=ALL}' \
  --billing-mode PAY_PER_REQUEST

echo "Waiting for Bookings table to be active..."
aws dynamodb wait table-exists --table-name Bookings

# 4. Create Payments Table
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
    'IndexName=BookingPaymentIndex,KeySchema=[{AttributeName=bookingId,KeyType=HASH}],Projection={ProjectionType=ALL}' \
    'IndexName=UserPaymentIndex,KeySchema=[{AttributeName=userId,KeyType=HASH},{AttributeName=paymentDate,KeyType=RANGE}],Projection={ProjectionType=ALL}' \
  --billing-mode PAY_PER_REQUEST

echo "Waiting for Payments table to be active..."
aws dynamodb wait table-exists --table-name Payments

echo "All tables created successfully!"

# List all tables to verify
echo "Listing all DynamoDB tables:"
aws dynamodb list-tables

echo "Table creation completed!"