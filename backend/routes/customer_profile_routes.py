from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from auth import get_current_user_email
from passlib.context import CryptContext

router = APIRouter(prefix="/customer/profile", tags=["Customer Profile"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    from server import db
    return db

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    language: Optional[str] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

@router.get("")
async def get_profile(
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get customer profile information."""
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": str(user["_id"]),
        "full_name": user.get("full_name", ""),
        "email": user.get("email", ""),
        "phone": user.get("phone", ""),
        "address": user.get("address", ""),
        "language": user.get("language", "en"),
        "role": user.get("role", "shopper"),
        "created_at": user.get("created_at"),
        "updated_at": user.get("updated_at")
    }

@router.put("")
async def update_profile(
    profile_data: ProfileUpdate,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update customer profile."""
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = {k: v for k, v in profile_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.users.update_one(
        {"email": email},
        {"$set": update_data}
    )
    
    return {"message": "Profile updated successfully"}

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Change customer password."""
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify current password
    if not pwd_context.verify(password_data.current_password, user.get("password", "")):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Hash new password
    hashed_password = pwd_context.hash(password_data.new_password)
    
    await db.users.update_one(
        {"email": email},
        {"$set": {"password": hashed_password, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Password changed successfully"}

@router.delete("/account")
async def delete_account(
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete customer account."""
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = str(user["_id"])
    
    # Delete user data
    await db.users.delete_one({"email": email})
    await db.reviews.delete_many({"user_id": user_id})
    await db.favorites.delete_many({"user_id": user_id})
    await db.notifications.delete_many({"user_id": user_id})
    
    return {"message": "Account deleted successfully"}
