from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from models import UserCreate, UserLogin, User, UserResponse, Token, LoginResponse
from auth import get_password_hash, verify_password, create_access_token, get_current_user_email
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_db():
    from server import db
    return db

@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Admins are automatically verified, others need email verification
    is_admin = user_data.role == "admin"
    email_verified = is_admin  # Admins are auto-verified
    
    # Create user document
    user_dict = {
        "full_name": user_data.full_name,
        "email": user_data.email,
        "password": hashed_password,
        "role": user_data.role,
        "email_verified": email_verified,  # Admins auto-verified
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_active": True
    }
    
    # Insert user
    result = await db.users.insert_one(user_dict)
    user_dict["_id"] = str(result.inserted_id)
    
    # Create access token
    access_token = create_access_token(data={"sub": user_data.email})
    
    # Return user and token
    user_response = UserResponse(
        id=user_dict["_id"],
        full_name=user_dict["full_name"],
        email=user_dict["email"],
        role=user_dict["role"],
        email_verified=email_verified,  # Return actual verification status
        created_at=user_dict["created_at"]
    )
    
    return LoginResponse(
        user=user_response,
        token=Token(access_token=access_token)
    )

@router.post("/login", response_model=LoginResponse)
async def login(credentials: UserLogin, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Login user."""
    # Find user
    user = await db.users.find_one({"email": credentials.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token (allow login even if not verified)
    access_token = create_access_token(data={"sub": user["email"]})
    
    # Return user and token with verification status
    user_response = UserResponse(
        id=str(user["_id"]),
        full_name=user["full_name"],
        email=user["email"],
        role=user["role"],
        email_verified=user.get("email_verified", False),
        created_at=user["created_at"]
    )
    
    return LoginResponse(
        user=user_response,
        token=Token(access_token=access_token)
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get current authenticated user."""
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=str(user["_id"]),
        full_name=user["full_name"],
        email=user["email"],
        role=user["role"],
        email_verified=user.get("email_verified", False),
        created_at=user["created_at"]
    )
