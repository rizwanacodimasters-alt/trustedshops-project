from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

# Order Models
class OrderBase(BaseModel):
    shop_id: str
    user_id: str
    order_number: str
    amount: float
    currency: str = "EUR"
    status: str = "pending"  # pending, completed, cancelled, refunded
    payment_method: str
    buyer_protection: bool = True
    protection_amount: float = 0.0

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

# Shop Verification Models
class ShopVerificationBase(BaseModel):
    shop_id: str
    status: str = "pending"  # pending, verified, rejected
    verification_type: str = "manual"  # manual, automatic
    notes: Optional[str] = None

class ShopVerification(ShopVerificationBase):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

# Review Response Models
class ReviewResponseBase(BaseModel):
    review_id: str
    response_text: str

class ReviewResponseCreate(ReviewResponseBase):
    pass

class ReviewResponse(ReviewResponseBase):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    shop_id: str
    responder_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

# Analytics Models
class ShopAnalytics(BaseModel):
    shop_id: str
    period: str  # daily, weekly, monthly
    total_reviews: int = 0
    average_rating: float = 0.0
    new_reviews: int = 0
    response_rate: float = 0.0
    views: int = 0
    date: datetime = Field(default_factory=datetime.utcnow)

# Subscription Models
class SubscriptionBase(BaseModel):
    user_id: str
    plan: str  # starter, professional, enterprise
    status: str = "active"  # active, cancelled, expired
    price: float

class Subscription(SubscriptionBase):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    auto_renew: bool = True

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
