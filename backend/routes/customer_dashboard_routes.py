from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
from datetime import datetime, timedelta
from auth import get_current_user_email
from bson import ObjectId

router = APIRouter(prefix="/customer", tags=["Customer Dashboard"])

def get_db():
    from server import db
    return db

@router.get("/dashboard")
async def get_customer_dashboard(
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get customer dashboard overview with statistics and recent activities."""
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = str(user["_id"])
    
    # Get reviews statistics
    reviews = await db.reviews.find({"user_id": user_id}).to_list(None)
    total_reviews = len(reviews)
    
    # Calculate average rating given
    avg_rating = sum(r.get("rating", 0) for r in reviews) / total_reviews if total_reviews > 0 else 0
    
    # Get recent reviews (last 5)
    recent_reviews = sorted(reviews, key=lambda x: x.get("created_at", datetime.min), reverse=True)[:5]
    
    # Format recent reviews
    formatted_reviews = []
    for review in recent_reviews:
        shop_id = review.get("shop_id")
        # Try to convert to ObjectId if it's a string
        try:
            if isinstance(shop_id, str):
                shop_id = ObjectId(shop_id)
        except:
            pass
        
        shop = await db.shops.find_one({"_id": shop_id})
        formatted_reviews.append({
            "id": str(review["_id"]),
            "shop_name": shop.get("name", "Unknown Shop") if shop else "Unknown Shop",
            "rating": review.get("rating"),
            "comment": review.get("comment", ""),
            "created_at": review.get("created_at"),
            "has_response": bool(review.get("response"))
        })
    
    # Get favorite shops count
    favorites = await db.favorites.count_documents({"user_id": user_id})
    
    # Get notifications count (unread)
    unread_notifications = await db.notifications.count_documents({
        "user_id": user_id,
        "read": False
    })
    
    return {
        "user": {
            "id": user_id,
            "full_name": user.get("full_name"),
            "email": user.get("email")
        },
        "statistics": {
            "total_reviews": total_reviews,
            "average_rating_given": round(avg_rating, 2),
            "favorite_shops": favorites,
            "unread_notifications": unread_notifications
        },
        "recent_reviews": formatted_reviews
    }

@router.get("/reviews")
async def get_my_reviews(
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db),
    sort_by: Optional[str] = "newest",
    shop_name: Optional[str] = None,
    search: Optional[str] = None
):
    """Get all reviews by the customer with filtering and sorting."""
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = str(user["_id"])
    
    # Get all reviews
    reviews = await db.reviews.find({"user_id": user_id}).to_list(None)
    
    # Enrich with shop data
    enriched_reviews = []
    for review in reviews:
        shop_id = review.get("shop_id")
        # Try to convert to ObjectId if it's a string
        try:
            if isinstance(shop_id, str):
                shop_id = ObjectId(shop_id)
        except:
            pass
        
        shop = await db.shops.find_one({"_id": shop_id})
        
        # Filter by shop name if provided
        if shop_name and shop:
            if shop_name.lower() not in shop.get("name", "").lower():
                continue
        
        # Create enriched review
        enriched_review = {
            "id": str(review["_id"]),
            "shop_id": str(review.get("shop_id")),
            "shop_name": shop.get("name", "Unknown Shop") if shop else "Unknown Shop",
            "shop_category": shop.get("category", "") if shop else "",
            "rating": review.get("rating"),
            "comment": review.get("comment", ""),
            "response": review.get("response", ""),
            "created_at": review.get("created_at"),
            "updated_at": review.get("updated_at"),
            "status": review.get("status", "published")
        }
        
        # Filter by search term
        if search:
            search_lower = search.lower()
            if not (search_lower in enriched_review["comment"].lower() or
                    search_lower in enriched_review["shop_name"].lower()):
                continue
        
        enriched_reviews.append(enriched_review)
    
    # Sort reviews
    if sort_by == "newest":
        enriched_reviews.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)
    elif sort_by == "oldest":
        enriched_reviews.sort(key=lambda x: x.get("created_at", datetime.min))
    elif sort_by == "highest":
        enriched_reviews.sort(key=lambda x: x.get("rating", 0), reverse=True)
    elif sort_by == "lowest":
        enriched_reviews.sort(key=lambda x: x.get("rating", 0))
    
    return {
        "reviews": enriched_reviews,
        "total": len(enriched_reviews)
    }

@router.get("/favorites")
async def get_favorites(
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get customer's favorite shops."""
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = str(user["_id"])
    
    # Get favorites
    favorites = await db.favorites.find({"user_id": user_id}).to_list(None)
    
    # Enrich with shop data
    favorite_shops = []
    for fav in favorites:
        shop_id = fav.get("shop_id")
        # Try to convert to ObjectId if it's a string
        try:
            if isinstance(shop_id, str):
                shop_id = ObjectId(shop_id)
        except:
            pass
        
        shop = await db.shops.find_one({"_id": shop_id})
        if shop:
            favorite_shops.append({
                "id": str(shop["_id"]),
                "name": shop.get("name"),
                "category": shop.get("category"),
                "rating": shop.get("rating", 0),
                "review_count": shop.get("review_count", 0),
                "is_verified": shop.get("is_verified", False),
                "added_at": fav.get("created_at")
            })
    
    return {"favorites": favorite_shops}

@router.post("/favorites/{shop_id}")
async def add_to_favorites(
    shop_id: str,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Add shop to favorites."""
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = str(user["_id"])
    
    # Check if shop exists
    shop = await db.shops.find_one({"_id": shop_id})
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    # Check if already favorited
    existing = await db.favorites.find_one({"user_id": user_id, "shop_id": shop_id})
    if existing:
        raise HTTPException(status_code=400, detail="Shop already in favorites")
    
    # Add to favorites
    favorite_doc = {
        "user_id": user_id,
        "shop_id": shop_id,
        "created_at": datetime.utcnow()
    }
    
    await db.favorites.insert_one(favorite_doc)
    
    return {"message": "Shop added to favorites"}

@router.delete("/favorites/{shop_id}")
async def remove_from_favorites(
    shop_id: str,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Remove shop from favorites."""
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = str(user["_id"])
    
    result = await db.favorites.delete_one({"user_id": user_id, "shop_id": shop_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    return {"message": "Shop removed from favorites"}

@router.get("/notifications")
async def get_notifications(
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db),
    unread_only: bool = False
):
    """Get customer notifications."""
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = str(user["_id"])
    
    query = {"user_id": user_id}
    if unread_only:
        query["read"] = False
    
    notifications = await db.notifications.find(query).sort("created_at", -1).limit(50).to_list(50)
    
    formatted_notifications = []
    for notif in notifications:
        formatted_notifications.append({
            "id": str(notif["_id"]),
            "type": notif.get("type", "info"),
            "title": notif.get("title", ""),
            "message": notif.get("message", ""),
            "read": notif.get("read", False),
            "created_at": notif.get("created_at")
        })
    
    return {"notifications": formatted_notifications}

@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Mark notification as read."""
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = str(user["_id"])
    
    result = await db.notifications.update_one(
        {"_id": notification_id, "user_id": user_id},
        {"$set": {"read": True}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification marked as read"}
