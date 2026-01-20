from fastapi import APIRouter, HTTPException, status, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from models_admin import ShopUpdateAdmin
from auth import get_current_user_email
from datetime import datetime
from bson import ObjectId
from typing import Optional
import math

router = APIRouter(prefix="/admin/shops", tags=["Admin - Shops"])

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
async def get_all_shops(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status_filter: Optional[str] = None,  # active, suspended, pending_review, banned
    verified: Optional[bool] = None,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all shops with filtering (admin only)."""
    await check_admin(email, db)
    
    # Build query
    query = {}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"website": {"$regex": search, "$options": "i"}}
        ]
    if status_filter:
        query["status"] = status_filter
    if verified is not None:
        query["is_verified"] = verified
    
    # Get total count
    total = await db.shops.count_documents(query)
    
    # Calculate pagination
    skip = (page - 1) * limit
    pages = math.ceil(total / limit) if total > 0 else 1
    
    # Get shops with owner details
    # Note: Using string-based lookup as owner_id might be stored as string
    pipeline = [
        {"$match": query},
        {"$sort": {"created_at": -1}},
        {"$skip": skip},
        {"$limit": limit},
        {
            "$lookup": {
                "from": "users",
                "localField": "owner_id",
                "foreignField": "id",
                "as": "owner_info"
            }
        }
    ]
    
    shops = await db.shops.aggregate(pipeline).to_list(limit)
    
    # Format shops
    for shop in shops:
        shop["id"] = str(shop["_id"])
        del shop["_id"]
        
        # Add owner info if available
        if shop.get("owner_info") and len(shop["owner_info"]) > 0:
            owner = shop["owner_info"][0]
            shop["owner_name"] = owner.get("full_name", "Unknown")
            shop["owner_email"] = owner.get("email", "")
            shop["owner_id_obj"] = str(owner.get("_id", ""))
        else:
            shop["owner_name"] = "Unknown Owner"
            shop["owner_email"] = ""
        
        # Remove lookup result
        if "owner_info" in shop:
            del shop["owner_info"]
        
        # Ensure default values
        shop["rating"] = shop.get("rating", 0.0)
        shop["review_count"] = shop.get("review_count", 0)
        shop["status"] = shop.get("status", "active")
    
    return {
        "data": shops,
        "total": total,
        "page": page,
        "pages": pages
    }

@router.get("/{shop_id}")
async def get_shop_detail(
    shop_id: str,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get detailed shop information (admin only)."""
    await check_admin(email, db)
    
    if not ObjectId.is_valid(shop_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid shop ID"
        )
    
    shop = await db.shops.find_one({"_id": ObjectId(shop_id)})
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shop not found"
        )
    
    shop["id"] = str(shop["_id"])
    del shop["_id"]
    
    # Get owner info
    owner = await db.users.find_one({"_id": ObjectId(shop["owner_id"])}, {"password": 0})
    if owner:
        owner["id"] = str(owner["_id"])
        del owner["_id"]
        shop["owner"] = owner
    
    # Get reviews
    reviews = await db.reviews.find({"shop_id": shop_id}).sort("created_at", -1).limit(20).to_list(20)
    for review in reviews:
        review["id"] = str(review["_id"])
        del review["_id"]
    shop["recent_reviews"] = reviews
    
    # Get verification status
    verification = await db.shop_verifications.find_one(
        {"shop_id": shop_id},
        sort=[("created_at", -1)]
    )
    if verification:
        verification["id"] = str(verification["_id"])
        del verification["_id"]
    shop["verification"] = verification
    
    return shop

@router.put("/{shop_id}")
async def update_shop(
    shop_id: str,
    shop_data: ShopUpdateAdmin,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update shop (admin only)."""
    await check_admin(email, db)
    
    if not ObjectId.is_valid(shop_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid shop ID"
        )
    
    shop = await db.shops.find_one({"_id": ObjectId(shop_id)})
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shop not found"
        )
    
    # Update shop
    update_data = {k: v for k, v in shop_data.dict(exclude_unset=True).items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.shops.update_one(
        {"_id": ObjectId(shop_id)},
        {"$set": update_data}
    )
    
    return {"message": "Shop updated successfully"}

@router.post("/{shop_id}/verify")
async def verify_shop(
    shop_id: str,
    notes: Optional[str] = None,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Verify shop (admin only)."""
    admin = await check_admin(email, db)
    
    if not ObjectId.is_valid(shop_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid shop ID"
        )
    
    # Update shop
    await db.shops.update_one(
        {"_id": ObjectId(shop_id)},
        {"$set": {"is_verified": True, "verified_at": datetime.utcnow()}}
    )
    
    # Update verification record
    await db.shop_verifications.update_one(
        {"shop_id": shop_id},
        {
            "$set": {
                "status": "verified",
                "verified_by": str(admin["_id"]),
                "verified_at": datetime.utcnow(),
                "notes": notes
            }
        },
        upsert=True
    )
    
    return {"message": "Shop verified successfully"}

@router.post("/{shop_id}/suspend")
async def suspend_shop(
    shop_id: str,
    reason: str,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Suspend shop (admin only)."""
    await check_admin(email, db)
    
    if not ObjectId.is_valid(shop_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid shop ID"
        )
    
    await db.shops.update_one(
        {"_id": ObjectId(shop_id)},
        {
            "$set": {
                "status": "suspended",
                "suspended_reason": reason,
                "suspended_at": datetime.utcnow()
            }
        }
    )
    
    return {"message": "Shop suspended successfully"}

@router.post("/{shop_id}/activate")
async def activate_shop(
    shop_id: str,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Activate shop (admin only)."""
    await check_admin(email, db)
    
    if not ObjectId.is_valid(shop_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid shop ID"
        )
    
    await db.shops.update_one(
        {"_id": ObjectId(shop_id)},
        {
            "$set": {"status": "active"},
            "$unset": {"suspended_reason": "", "suspended_at": ""}
        }
    )
    
    return {"message": "Shop activated successfully"}

@router.delete("/{shop_id}")
async def delete_shop(
    shop_id: str,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Permanently delete shop (admin only)."""
    await check_admin(email, db)
    
    if not ObjectId.is_valid(shop_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid shop ID"
        )
    
    # Delete shop and all related data
    await db.shops.delete_one({"_id": ObjectId(shop_id)})
    await db.reviews.delete_many({"shop_id": shop_id})
    await db.orders.delete_many({"shop_id": shop_id})
    await db.shop_verifications.delete_many({"shop_id": shop_id})
    
    return {"message": "Shop deleted successfully"}

@router.post("/{shop_id}/ban")
async def ban_shop(
    shop_id: str,
    reason: str,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Ban shop permanently (admin only)."""
    await check_admin(email, db)
    
    if not ObjectId.is_valid(shop_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid shop ID"
        )
    
    await db.shops.update_one(
        {"_id": ObjectId(shop_id)},
        {
            "$set": {
                "status": "banned",
                "banned_reason": reason,
                "banned_at": datetime.utcnow()
            }
        }
    )
    
    return {"message": "Shop banned successfully"}
