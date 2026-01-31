# DynamoDB Schema Design - Restaurant Booking System

## Table Structures

### 1. Restaurants Table
**Table Name**: `Restaurants`
**Primary Key**: `restaurantId` (String)

```json
{
  "restaurantId": "rest_001",
  "name": "Italian Bistro",
  "menuCard": [
    {
      "category": "Main Course",
      "items": ["Pasta Carbonara", "Margherita Pizza", "Risotto"]
    },
    {
      "category": "Appetizers", 
      "items": ["Bruschetta", "Antipasto Platter"]
    }
  ],
  "location": {
    "address": "123 Main St, Downtown",
    "city": "New York",
    "coordinates": {
      "lat": 40.7128,
      "lng": -74.0060
    }
  },
  "description": "Authentic Italian cuisine in the heart of downtown",
  "cuisine": "Italian",
  "priceRange": "$$",
  "rating": 4.5,
  "openHours": {
    "monday": "11:00-22:00",
    "tuesday": "11:00-22:00"
  },
  "capacity": 50,
  "createdAt": "2024-01-15T10:30:00Z"
}
```

**Global Secondary Indexes (GSI)**:
- `CityIndex`: Partition Key = `city`, Sort Key = `rating`
- `CuisineIndex`: Partition Key = `cuisine`, Sort Key = `rating`

### 2. Users Table
**Table Name**: `Users`
**Primary Key**: `userId` (String)

```json
{
  "userId": "user_001",
  "username": "john_doe",
  "mobileNo": "+1234567890",
  "email": "john@example.com",
  "userPreferences": {
    "cuisine": ["Italian", "Mexican"],
    "dietaryRestrictions": ["vegetarian"],
    "priceRange": "$$",
    "preferredMealTimes": ["dinner"]
  },
  "userCity": "New York",
  "registrationDate": "2024-01-10T09:15:00Z",
  "lastLoginDate": "2024-01-20T14:30:00Z"
}
```

**Global Secondary Indexes (GSI)**:
- `MobileIndex`: Partition Key = `mobileNo`
- `UsernameIndex`: Partition Key = `username`

### 3. Bookings Table
**Table Name**: `Bookings`
**Primary Key**: `bookingId` (String)

```json
{
  "bookingId": "booking_001",
  "restaurantId": "rest_001",
  "userId": "user_001",
  "userName": "john_doe",
  "userMobileNo": "+1234567890",
  "bookingDate": "2024-01-25",
  "bookingTime": "19:00",
  "mealType": "Dinner",
  "cityName": "New York",
  "noOfGuests": 4,
  "tokenAmount": 50.00,
  "bookingStatus": "confirmed",
  "bookingReference": "REF123456",
  "specialRequests": "Window seat preferred",
  "createdAt": "2024-01-20T15:45:00Z",
  "updatedAt": "2024-01-20T15:45:00Z"
}
```

**Global Secondary Indexes (GSI)**:
- `UserBookingsIndex`: Partition Key = `userId`, Sort Key = `createdAt`
- `RestaurantBookingsIndex`: Partition Key = `restaurantId`, Sort Key = `bookingDate`
- `DateIndex`: Partition Key = `bookingDate`, Sort Key = `bookingTime`

### 4. Payments Table
**Table Name**: `Payments`
**Primary Key**: `paymentId` (String)

```json
{
  "paymentId": "pay_001",
  "bookingId": "booking_001",
  "userId": "user_001",
  "restaurantId": "rest_001",
  "amount": 50.00,
  "currency": "USD",
  "paymentMethod": "credit_card",
  "paymentStatus": "completed",
  "transactionId": "txn_abc123",
  "paymentDate": "2024-01-20T15:50:00Z",
  "refundStatus": null,
  "refundAmount": null,
  "createdAt": "2024-01-20T15:50:00Z"
}
```

**Global Secondary Indexes (GSI)**:
- `BookingPaymentIndex`: Partition Key = `bookingId`
- `UserPaymentIndex`: Partition Key = `userId`, Sort Key = `paymentDate`

## DynamoDB Table Creation Commands

### Create Restaurants Table
```bash
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
    IndexName=CityIndex,KeySchema=[{AttributeName=city,KeyType=HASH},{AttributeName=rating,KeyType=RANGE}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5} \
    IndexName=CuisineIndex,KeySchema=[{AttributeName=cuisine,KeyType=HASH},{AttributeName=rating,KeyType=RANGE}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5} \
  --billing-mode PAY_PER_REQUEST
```

### Create Users Table
```bash
aws dynamodb create-table \
  --table-name Users \
  --attribute-definitions \
    AttributeName=userId,AttributeType=S \
    AttributeName=mobileNo,AttributeType=S \
    AttributeName=username,AttributeType=S \
  --key-schema \
    AttributeName=userId,KeyType=HASH \
  --global-secondary-indexes \
    IndexName=MobileIndex,KeySchema=[{AttributeName=mobileNo,KeyType=HASH}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5} \
    IndexName=UsernameIndex,KeySchema=[{AttributeName=username,KeyType=HASH}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5} \
  --billing-mode PAY_PER_REQUEST
```

### Create Bookings Table
```bash
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
    IndexName=UserBookingsIndex,KeySchema=[{AttributeName=userId,KeyType=HASH},{AttributeName=createdAt,KeyType=RANGE}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5} \
    IndexName=RestaurantBookingsIndex,KeySchema=[{AttributeName=restaurantId,KeyType=HASH},{AttributeName=bookingDate,KeyType=RANGE}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5} \
    IndexName=DateIndex,KeySchema=[{AttributeName=bookingDate,KeyType=HASH},{AttributeName=bookingTime,KeyType=RANGE}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5} \
  --billing-mode PAY_PER_REQUEST
```

### Create Payments Table
```bash
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
    IndexName=BookingPaymentIndex,KeySchema=[{AttributeName=bookingId,KeyType=HASH}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5} \
    IndexName=UserPaymentIndex,KeySchema=[{AttributeName=userId,KeyType=HASH},{AttributeName=paymentDate,KeyType=RANGE}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5} \
  --billing-mode PAY_PER_REQUEST
```

## Access Patterns

### Restaurant Search
- **Query by city**: Use `CityIndex` GSI
- **Query by cuisine**: Use `CuisineIndex` GSI
- **Get restaurant by ID**: Direct `get_item` on primary key

### User Management
- **Find user by mobile**: Use `MobileIndex` GSI
- **Find user by username**: Use `UsernameIndex` GSI
- **Get user preferences**: Direct `get_item` on primary key

### Booking Operations
- **Get user's bookings**: Use `UserBookingsIndex` GSI
- **Get restaurant's bookings for a date**: Use `RestaurantBookingsIndex` GSI
- **Check availability by date/time**: Use `DateIndex` GSI

### Payment Tracking
- **Get payment for booking**: Use `BookingPaymentIndex` GSI
- **Get user's payment history**: Use `UserPaymentIndex` GSI

## Cost Optimization
- Using **PAY_PER_REQUEST** billing mode for variable workloads
- **Projection Type = ALL** for GSIs to avoid additional queries
- Efficient query patterns to minimize read/write operations