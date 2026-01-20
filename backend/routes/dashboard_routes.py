from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from auth import get_current_user_email
from bson import ObjectId
from datetime import datetime, timedelta

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

def get_db():
    from server import db
    return db

@router.get("/user")
async def get_user_dashboard(
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get user dashboard data."""
    # Get current user
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_id = str(user["_id"])
    
    # Get statistics
    total_orders = await db.orders.count_documents({"user_id": user_id})
    total_reviews = await db.reviews.count_documents({"user_id": user_id})
    
    # Get protected orders
    protected_orders = await db.orders.count_documents({
        "user_id": user_id,
        "buyer_protection": True
    })
    
    # Get recent orders
    recent_orders = await db.orders.find(
        {"user_id": user_id}
    ).sort("created_at", -1).limit(5).to_list(5)
    
    for order in recent_orders:
        order["id"] = str(order["_id"])
        del order["_id"]
    
    # Get recent reviews
    recent_reviews = await db.reviews.find(
        {"user_id": user_id}
    ).sort("created_at", -1).limit(5).to_list(5)
    
    for review in recent_reviews:
        review["id"] = str(review["_id"])
        del review["_id"]
    
    return {
        "user": {
            "id": user_id,
            "name": user["full_name"],
            "email": user["email"],
            "role": user["role"]
        },
        "statistics": {
            "total_orders": total_orders,
            "total_reviews": total_reviews,
            "protected_orders": protected_orders
        },
        "recent_orders": recent_orders,
        "recent_reviews": recent_reviews
    }

@router.get("/shop-owner")
async def get_shop_owner_dashboard(
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get shop owner dashboard data."""
    # Get current user
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user["role"] != "shop_owner" and user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Shop owner role required."
        )
    
    user_id = str(user["_id"])
    
    # Get user's shops
    shops = await db.shops.find({"owner_id": user_id}).to_list(100)
    
    total_shops = len(shops)
    verified_shops = sum(1 for shop in shops if shop.get("is_verified", False))
    
    # Calculate totals across all shops
    total_reviews = 0
    total_rating = 0.0
    shop_ids = []
    
    for shop in shops:
        shop["id"] = str(shop["_id"])
        shop_ids.append(shop["id"])
        total_reviews += shop.get("review_count", 0)
        total_rating += shop.get("rating", 0.0) * shop.get("review_count", 0)
        
        # Remove _id field to avoid serialization error
        if "_id" in shop:
            del shop["_id"]
    
    avg_rating = (total_rating / total_reviews) if total_reviews > 0 else 0.0
    
    # Get recent reviews for all shops
    recent_reviews = await db.reviews.find(
        {"shop_id": {"$in": shop_ids}}
    ).sort("created_at", -1).limit(10).to_list(10)
    
    for review in recent_reviews:
        review["id"] = str(review["_id"])
        del review["_id"]
    
    # Get reviews that need response
    unanswered_reviews = await db.reviews.find({
        "shop_id": {"$in": shop_ids}
    }).to_list(1000)
    
    # Check which reviews have responses
    unanswered_count = 0
    for review in unanswered_reviews:
        response = await db.review_responses.find_one({"review_id": str(review["_id"])})
        if not response:
            unanswered_count += 1
    
    # Analytics for last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_reviews_30d = await db.reviews.count_documents({
        "shop_id": {"$in": shop_ids},
        "created_at": {"$gte": thirty_days_ago}
    })
    
    return {
        "user": {
            "id": user_id,
            "name": user["full_name"],
            "email": user["email"],
            "role": user["role"]
        },
        "statistics": {
            "total_shops": total_shops,
            "verified_shops": verified_shops,
            "total_reviews": total_reviews,
            "average_rating": round(avg_rating, 2),
            "unanswered_reviews": unanswered_count,
            "new_reviews_30d": new_reviews_30d
        },
        "shops": shops,
        "recent_reviews": recent_reviews
    }
