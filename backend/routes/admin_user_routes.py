from fastapi import APIRouter, HTTPException, status, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from models_admin import UserUpdateAdmin, LoginHistory, SecurityAlert
from auth import get_current_user_email, get_password_hash
from datetime import datetime, timedelta
from bson import ObjectId
from typing import Optional
import math

router = APIRouter(prefix="/admin/users", tags=["Admin - Users"])

def get_db():
    from server import db
    return db

async def check_admin(email: str, db: AsyncIOMotorDatabase):
    """Check if user is admin."""
    user = await db.users.find_one({"email": email})
    if not user or user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user

@router.get("")
async def get_all_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    status: Optional[str] = None,  # active, inactive
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all users with filtering (admin only)."""
    await check_admin(email, db)
    
    # Build query
    query = {}
    if search:
        query["$or"] = [
            {"full_name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]
    if role:
        query["role"] = role
    if status:
        query["is_active"] = (status == "active")
    
    # Get total count
    total = await db.users.count_documents(query)
    
    # Calculate pagination
    skip = (page - 1) * limit
    pages = math.ceil(total / limit) if total > 0 else 1
    
    # Get users
    cursor = db.users.find(query, {"password": 0}).skip(skip).limit(limit).sort("created_at", -1)
    users = await cursor.to_list(limit)
    
    # Format users
    for user in users:
        user["id"] = str(user["_id"])
        del user["_id"]
        
        # Get user statistics
        user["total_reviews"] = await db.reviews.count_documents({"user_id": user["id"]})
        user["total_orders"] = await db.orders.count_documents({"user_id": user["id"]})
        
        if user["role"] == "shop_owner":
            user["total_shops"] = await db.shops.count_documents({"owner_id": user["id"]})
    
    return {
        "data": users,
        "total": total,
        "page": page,
        "pages": pages
    }

@router.get("/{user_id}")
async def get_user_detail(
    user_id: str,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get detailed user information (admin only)."""
    await check_admin(email, db)
    
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )
    
    user = await db.users.find_one({"_id": ObjectId(user_id)}, {"password": 0})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user["id"] = str(user["_id"])
    del user["_id"]
    
    # Get user statistics
    user["total_reviews"] = await db.reviews.count_documents({"user_id": user_id})
    user["total_orders"] = await db.orders.count_documents({"user_id": user_id})
    
    if user["role"] == "shop_owner":
        shops = await db.shops.find({"owner_id": user_id}).to_list(100)
        for shop in shops:
            shop["id"] = str(shop["_id"])
            del shop["_id"]
        user["shops"] = shops
    
    # Get recent login history
    login_history = await db.login_history.find(
        {"user_id": user_id}
    ).sort("timestamp", -1).limit(10).to_list(10)
    
    for entry in login_history:
        entry["id"] = str(entry["_id"])
        del entry["_id"]
    
    user["login_history"] = login_history
    
    # Get active sessions
    sessions = await db.user_sessions.find(
        {"user_id": user_id, "is_active": True}
    ).to_list(100)
    
    for session in sessions:
        session["id"] = str(session["_id"])
        del session["_id"]
    
    user["active_sessions"] = sessions
    
    # Get security alerts
    alerts = await db.security_alerts.find(
        {"user_id": user_id, "resolved": False}
    ).sort("created_at", -1).to_list(10)
    
    for alert in alerts:
        alert["id"] = str(alert["_id"])
        del alert["_id"]
    
    user["security_alerts"] = alerts
    
    return user

@router.put("/{user_id}")
async def update_user(
    user_id: str,
    user_data: UserUpdateAdmin,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update user (admin only)."""
    await check_admin(email, db)
    
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )
    
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user
    update_data = {k: v for k, v in user_data.dict(exclude_unset=True).items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    
    return {"message": "User updated successfully"}

@router.post("/{user_id}/suspend")
async def suspend_user(
    user_id: str,
    reason: Optional[str] = None,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Suspend/deactivate user (admin only)."""
    await check_admin(email, db)
    
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )
    
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_active": False, "suspended_reason": reason, "suspended_at": datetime.utcnow()}}
    )
    
    # Deactivate all sessions
    await db.user_sessions.update_many(
        {"user_id": user_id},
        {"$set": {"is_active": False}}
    )
    
    return {"message": "User suspended successfully"}

@router.post("/{user_id}/activate")
async def activate_user(
    user_id: str,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Activate user (admin only)."""
    await check_admin(email, db)
    
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )
    
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_active": True}, "$unset": {"suspended_reason": "", "suspended_at": ""}}
    )
    
    return {"message": "User activated successfully"}

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Permanently delete user (admin only)."""
    await check_admin(email, db)
    
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )
    
    # Delete user and all related data
    await db.users.delete_one({"_id": ObjectId(user_id)})
    await db.reviews.delete_many({"user_id": user_id})
    await db.orders.delete_many({"user_id": user_id})
    await db.user_sessions.delete_many({"user_id": user_id})
    await db.login_history.delete_many({"user_id": user_id})
    
    # If shop owner, delete or reassign shops
    await db.shops.delete_many({"owner_id": user_id})
    
    return {"message": "User deleted successfully"}

@router.post("/{user_id}/reset-password")
async def reset_user_password(
    user_id: str,
    new_password: str,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Reset user password (admin only)."""
    await check_admin(email, db)
    
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )
    
    # Hash new password
    hashed_password = get_password_hash(new_password)
    
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"password": hashed_password, "password_reset_at": datetime.utcnow()}}
    )
    
    # Deactivate all sessions for security
    await db.user_sessions.update_many(
        {"user_id": user_id},
        {"$set": {"is_active": False}}
    )
    
    return {"message": "Password reset successfully"}

@router.post("/{user_id}/change-role")
async def change_user_role(
    user_id: str,
    new_role: str,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Change user role (admin only)."""
    await check_admin(email, db)
    
    if new_role not in ["shopper", "shop_owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role"
        )
    
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )
    
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"role": new_role, "role_changed_at": datetime.utcnow()}}
    )
    
    return {"message": f"User role changed to {new_role}"}

@router.post("/{user_id}/sessions/{session_id}/terminate")
async def terminate_session(
    user_id: str,
    session_id: str,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Terminate specific user session (admin only)."""
    await check_admin(email, db)
    
    await db.user_sessions.update_one(
        {"_id": ObjectId(session_id), "user_id": user_id},
        {"$set": {"is_active": False}}
    )
    
    return {"message": "Session terminated successfully"}

@router.post("/{user_id}/sessions/terminate-all")
async def terminate_all_sessions(
    user_id: str,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Terminate all user sessions (admin only)."""
    await check_admin(email, db)
    
    result = await db.user_sessions.update_many(
        {"user_id": user_id},
        {"$set": {"is_active": False}}
    )
    
    return {"message": f"{result.modified_count} sessions terminated"}

@router.get("/{user_id}/login-history")
async def get_login_history(
    user_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get user login history (admin only)."""
    await check_admin(email, db)
    
    # Get total count
    total = await db.login_history.count_documents({"user_id": user_id})
    
    # Calculate pagination
    skip = (page - 1) * limit
    pages = math.ceil(total / limit) if total > 0 else 1
    
    # Get history
    history = await db.login_history.find(
        {"user_id": user_id}
    ).sort("timestamp", -1).skip(skip).limit(limit).to_list(limit)
    
    for entry in history:
        entry["id"] = str(entry["_id"])
        del entry["_id"]
    
    return {
        "data": history,
        "total": total,
        "page": page,
        "pages": pages
    }

@router.post("/{user_id}/2fa/enable")
async def enable_2fa(
    user_id: str,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Enable 2FA for user (admin only)."""
    await check_admin(email, db)
    
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"two_factor_enabled": True}}
    )
    
    return {"message": "2FA enabled successfully"}

@router.post("/{user_id}/2fa/disable")
async def disable_2fa(
    user_id: str,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Disable 2FA for user (admin only)."""
    await check_admin(email, db)
    
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"two_factor_enabled": False}}
    )
    
    return {"message": "2FA disabled successfully"}
