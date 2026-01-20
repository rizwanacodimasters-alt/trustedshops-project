from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

# User Models
class UserBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    role: str = Field(default="shopper", pattern="^(shopper|shop_owner|admin)$")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class UserResponse(BaseModel):
    id: str
    full_name: str
    email: str
    role: str
    email_verified: bool = False
    created_at: datetime

# Shop Models
class ShopBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = Field(default="", min_length=0)
    logo: Optional[str] = Field(default="")
    image: Optional[str] = Field(default="")
    website: str
    category: str
    email: Optional[str] = Field(default="")
    phone: Optional[str] = Field(default="")
    address: Optional[str] = Field(default="")

class ShopCreate(ShopBase):
    pass

class ShopUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    logo: Optional[str] = None
    image: Optional[str] = None
    website: Optional[str] = None
    category: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class Shop(ShopBase):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    owner_id: str
    rating: float = 0.0
    review_count: int = 0
    is_verified: bool = False
    email: Optional[str] = Field(default="")
    phone: Optional[str] = Field(default="")
    address: Optional[str] = Field(default="")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

# Review Models
class ReviewBase(BaseModel):
    shop_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., min_length=10, max_length=1000)

class ReviewCreate(ReviewBase):
    order_id: Optional[str] = None
    order_reference: Optional[str] = None
    proof_photos: Optional[List[str]] = []
    proof_order_number: Optional[str] = None

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, min_length=10, max_length=1000)
    proof_photos: Optional[List[str]] = None
    proof_order_number: Optional[str] = None

class Review(ReviewBase):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str
    user_name: str = ""
    user_initials: str = ""
    shop_name: str = ""
    shop_website: str = ""
    
    # Review Type & Verification
    review_type: str = "verified"  # "verified", "imported", "unverified"
    order_id: Optional[str] = None
    order_reference: Optional[str] = None
    is_verified_purchase: bool = False
    verification_date: Optional[datetime] = None
    
    # Low-Star Verification (1-2 stars)
    status: str = "published"  # "pending", "approved", "rejected", "published"
    proof_photos: List[str] = []  # Base64 encoded images
    proof_chat_history: Optional[str] = None  # Base64 encoded file
    proof_order_number: Optional[str] = None
    admin_notes: Optional[str] = None
    reviewed_by_admin: Optional[str] = None
    review_date: Optional[datetime] = None
    
    # Unverified Workflow
    email: Optional[str] = None  # For unverified reviews
    verification_token: Optional[str] = None
    email_verified: bool = True
    
    # Content Moderation
    content_flags: List[str] = []
    is_flagged: bool = False
    flag_reason: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

# Low-Star Review Proof Upload
class LowStarProofUpload(BaseModel):
    review_id: str
    proof_photos: List[str] = Field(..., min_items=1, max_items=5)  # Base64 images
    proof_chat_history: str  # Base64 encoded file
    proof_order_number: str = Field(..., min_length=3)

# Admin Review Actions
class AdminReviewAction(BaseModel):
    action: str = Field(..., pattern="^(approve|reject)$")
    admin_notes: Optional[str] = None

# Token Models
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None

# Response Models
class LoginResponse(BaseModel):
    user: UserResponse
    token: Token

class PaginatedResponse(BaseModel):
    data: List
    total: int
    page: int
    pages: int

class StatisticsResponse(BaseModel):
    shoppers: str
    shops: str
    dailyTransactions: str
