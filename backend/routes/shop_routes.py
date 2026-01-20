from fastapi import APIRouter, HTTPException, status, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from models import ShopCreate, ShopUpdate, Shop
from auth import get_current_user_email
from datetime import datetime
from bson import ObjectId
from typing import List, Optional
import math

router = APIRouter(prefix="/shops", tags=["Shops"])

def get_db():
    from server import db
    return db

@router.get("", response_model=dict)
async def get_shops(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all shops with pagination and filters."""
    # Build query
    query = {}
    if category:
        query["category"] = category
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    # Get total count
    total = await db.shops.count_documents(query)
    
    # Calculate pagination
    skip = (page - 1) * limit
    pages = math.ceil(total / limit) if total > 0 else 1
    
    # Get shops
    cursor = db.shops.find(query).skip(skip).limit(limit).sort("created_at", -1)
    shops = await cursor.to_list(length=limit)
    
    # Convert ObjectId to string
    for shop in shops:
        shop["id"] = str(shop["_id"])
        del shop["_id"]
    
    return {
        "data": shops,
        "total": total,
        "page": page,
        "pages": pages
    }

@router.get("/{shop_id}", response_model=Shop)
async def get_shop(shop_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get single shop by ID - supports both ObjectId and UUID formats."""
    shop = None
    
    # Try ObjectId format first (24-char hex string)
    if ObjectId.is_valid(shop_id):
        try:
            shop = await db.shops.find_one({"_id": ObjectId(shop_id)})
        except:
            pass
    
    # If not found, try as string _id (UUID format)
    if not shop:
        shop = await db.shops.find_one({"_id": shop_id})
    
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shop not found with ID: {shop_id}"
        )
    
    # Convert _id to id for response
    shop["id"] = str(shop["_id"])
    del shop["_id"]
    
    return shop

@router.post("", response_model=Shop, status_code=status.HTTP_201_CREATED)
async def create_shop(
    shop_data: ShopCreate,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new shop (requires shop_owner or admin role)."""
    # Get current user
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user has shop_owner or admin role
    if user.get("role") not in ["shop_owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only shop owners and admins can create shops. Please register as a business owner."
        )
    
    # Create shop document
    shop_dict = shop_data.dict()
    shop_dict.update({
        "owner_id": str(user["_id"]),
        "rating": 0.0,
        "review_count": 0,
        "is_verified": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    
    # Insert shop
    result = await db.shops.insert_one(shop_dict)
    shop_dict["id"] = str(result.inserted_id)
    
    # Remove _id field to avoid validation error
    if "_id" in shop_dict:
        del shop_dict["_id"]
    
    return shop_dict

@router.put("/{shop_id}", response_model=Shop)
async def update_shop(
    shop_id: str,
    shop_data: ShopUpdate,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update shop (owner only)."""
    if not ObjectId.is_valid(shop_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid shop ID"
        )
    
    # Get current user
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get shop
    shop = await db.shops.find_one({"_id": ObjectId(shop_id)})
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shop not found"
        )
    
    # Check ownership
    if shop["owner_id"] != str(user["_id"]) and user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this shop"
        )
    
    # Update shop
    update_data = {k: v for k, v in shop_data.dict(exclude_unset=True).items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.shops.update_one(
        {"_id": ObjectId(shop_id)},
        {"$set": update_data}
    )
    
    # Return updated shop
    updated_shop = await db.shops.find_one({"_id": ObjectId(shop_id)})
    updated_shop["id"] = str(updated_shop["_id"])
    
    # Remove _id field to avoid serialization error
    if "_id" in updated_shop:
        del updated_shop["_id"]
    
    return updated_shop

@router.delete("/{shop_id}")
async def delete_shop(
    shop_id: str,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete shop (owner only)."""
    if not ObjectId.is_valid(shop_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid shop ID"
        )
    
    # Get current user
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get shop
    shop = await db.shops.find_one({"_id": ObjectId(shop_id)})
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shop not found"
        )
    
    # Check ownership
    if shop["owner_id"] != str(user["_id"]) and user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this shop"
        )
    
    # Delete shop and its reviews
    await db.shops.delete_one({"_id": ObjectId(shop_id)})
    await db.reviews.delete_many({"shop_id": shop_id})
    
    return {"message": "Shop deleted successfully"}
