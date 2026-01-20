from fastapi import APIRouter, HTTPException, status, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from models_extended import OrderCreate, Order
from auth import get_current_user_email
from datetime import datetime
from bson import ObjectId
from typing import Optional
import math

router = APIRouter(prefix="/orders", tags=["Orders"])

def get_db():
    from server import db
    return db

@router.post("", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new order (authenticated users)."""
    # Get current user
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate shop exists
    if not ObjectId.is_valid(order_data.shop_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid shop ID"
        )
    
    shop = await db.shops.find_one({"_id": ObjectId(order_data.shop_id)})
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shop not found"
        )
    
    # Create order
    order_dict = order_data.dict()
    order_dict["user_id"] = str(user["_id"])
    order_dict["created_at"] = datetime.utcnow()
    order_dict["updated_at"] = datetime.utcnow()
    
    # Calculate protection amount (up to 20000 EUR)
    if order_dict["buyer_protection"]:
        order_dict["protection_amount"] = min(order_dict["amount"], 20000.0)
    
    result = await db.orders.insert_one(order_dict)
    order_dict["id"] = str(result.inserted_id)
    
    return order_dict

@router.get("", response_model=dict)
async def get_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status_filter: Optional[str] = None,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get user's orders."""
    # Get current user
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Build query
    query = {"user_id": str(user["_id"])}
    if status_filter:
        query["status"] = status_filter
    
    # Get total count
    total = await db.orders.count_documents(query)
    
    # Calculate pagination
    skip = (page - 1) * limit
    pages = math.ceil(total / limit) if total > 0 else 1
    
    # Get orders with shop details
    pipeline = [
        {"$match": query},
        {"$sort": {"created_at": -1}},
        {"$skip": skip},
        {"$limit": limit},
        {
            "$lookup": {
                "from": "shops",
                "let": {"shop_id": {"$toObjectId": "$shop_id"}},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$_id", "$$shop_id"]}}}
                ],
                "as": "shop_info"
            }
        }
    ]
    
    orders = await db.orders.aggregate(pipeline).to_list(limit)
    
    # Format orders
    for order in orders:
        order["id"] = str(order["_id"])
        del order["_id"]
        
        if order["shop_info"]:
            shop = order["shop_info"][0]
            order["shop_name"] = shop["name"]
            order["shop_logo"] = shop.get("logo", "")
        
        del order["shop_info"]
    
    return {
        "data": orders,
        "total": total,
        "page": page,
        "pages": pages
    }

@router.get("/{order_id}", response_model=Order)
async def get_order(
    order_id: str,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get single order by ID."""
    if not ObjectId.is_valid(order_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order ID"
        )
    
    # Get current user
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    order = await db.orders.find_one({
        "_id": ObjectId(order_id),
        "user_id": str(user["_id"])
    })
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    order["id"] = str(order["_id"])
    return order
