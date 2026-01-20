# API Contracts & Backend Implementation Plan

## Overview
This document outlines the API contracts, data models, and integration plan for the TrustedShops clone.

## Database Models

### 1. User Model
```python
{
    "_id": ObjectId,
    "full_name": str,
    "email": str (unique, indexed),
    "password": str (hashed),
    "role": str (enum: "shopper", "shop_owner", "admin"),
    "created_at": datetime,
    "updated_at": datetime,
    "is_active": bool
}
```

### 2. Shop Model
```python
{
    "_id": ObjectId,
    "name": str,
    "description": str,
    "logo": str (URL),
    "image": str (URL),
    "website": str,
    "category": str,
    "owner_id": ObjectId (ref: User),
    "rating": float (calculated from reviews),
    "review_count": int (calculated),
    "is_verified": bool,
    "created_at": datetime,
    "updated_at": datetime
}
```

### 3. Review Model
```python
{
    "_id": ObjectId,
    "user_id": ObjectId (ref: User),
    "shop_id": ObjectId (ref: Shop),
    "rating": int (1-5),
    "comment": str,
    "created_at": datetime,
    "updated_at": datetime
}
```

## API Endpoints

### Authentication APIs
- **POST /api/auth/register** - Register new user
  - Request: `{ full_name, email, password, role }`
  - Response: `{ user, token }`
  
- **POST /api/auth/login** - User login
  - Request: `{ email, password }`
  - Response: `{ user, token }`
  
- **GET /api/auth/me** - Get current user
  - Headers: `Authorization: Bearer <token>`
  - Response: `{ user }`

### Shop APIs
- **GET /api/shops** - Get all shops (with pagination & filters)
  - Query params: `page, limit, category, search`
  - Response: `{ shops: [], total, page, pages }`
  
- **GET /api/shops/:id** - Get single shop
  - Response: `{ shop }`
  
- **POST /api/shops** - Create new shop (authenticated, shop_owner only)
  - Request: `{ name, description, logo, image, website, category }`
  - Response: `{ shop }`
  
- **PUT /api/shops/:id** - Update shop (authenticated, owner only)
  - Request: `{ name, description, logo, image, website, category }`
  - Response: `{ shop }`
  
- **DELETE /api/shops/:id** - Delete shop (authenticated, owner only)
  - Response: `{ message }`

### Review APIs
- **GET /api/reviews** - Get all reviews (with pagination & filters)
  - Query params: `page, limit, shop_id, user_id`
  - Response: `{ reviews: [], total, page, pages }`
  
- **POST /api/reviews** - Create new review (authenticated)
  - Request: `{ shop_id, rating, comment }`
  - Response: `{ review }`
  
- **PUT /api/reviews/:id** - Update review (authenticated, owner only)
  - Request: `{ rating, comment }`
  - Response: `{ review }`
  
- **DELETE /api/reviews/:id** - Delete review (authenticated, owner only)
  - Response: `{ message }`

### Statistics APIs
- **GET /api/statistics** - Get platform statistics
  - Response: `{ shoppers, shops, dailyTransactions }`

## Frontend Integration Plan

### Files to Modify
1. **mockData.js** - Remove after backend integration
2. **API Service Layer** - Create `/frontend/src/services/api.js`
3. **Auth Context** - Create `/frontend/src/context/AuthContext.js`
4. **Update Components**:
   - Header.jsx - Use AuthContext
   - Home.jsx - Fetch real shops and reviews
   - SignIn.jsx - Call login API
   - SignUp.jsx - Call register API

### Mock Data Replacement
- Replace `mockShops` with API call to `/api/shops`
- Replace `mockReviews` with API call to `/api/reviews`
- Replace `statistics` with API call to `/api/statistics`
- Implement real authentication flow

## Security Considerations
- JWT token expiration: 7 days
- Password hashing with bcrypt
- Protected routes with middleware
- CORS configuration
- Input validation with Pydantic
- Rate limiting (optional for MVP)

## Error Handling
- Consistent error response format
- HTTP status codes
- Validation errors
- Authentication errors
- Not found errors
