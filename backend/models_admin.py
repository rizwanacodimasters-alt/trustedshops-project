from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

# Login History Model
class LoginHistory(BaseModel):
    user_id: str
    email: str
    ip_address: str
    user_agent: str
    location: Optional[str] = None
    success: bool = True
    failure_reason: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {ObjectId: str}

# Session Model
class UserSession(BaseModel):
    user_id: str
    session_token: str
    ip_address: str
    user_agent: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    is_active: bool = True

    class Config:
        json_encoders = {ObjectId: str}

# Security Alert Model
class SecurityAlert(BaseModel):
    user_id: str
    alert_type: str  # suspicious_login, multiple_failed_attempts, unusual_activity
    severity: str  # low, medium, high, critical
    description: str
    ip_address: Optional[str] = None
    resolved: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {ObjectId: str}

# User Update Model (Admin)
class UserUpdateAdmin(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    two_factor_enabled: Optional[bool] = None

# Shop Update Model (Admin)
class ShopUpdateAdmin(BaseModel):
    name: Optional[str] = None
    is_verified: Optional[bool] = None
    status: Optional[str] = None  # active, suspended, pending_review, banned
    notes: Optional[str] = None
