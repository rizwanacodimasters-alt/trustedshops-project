from fastapi import APIRouter, HTTPException, status, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from models import AdminReviewAction
from auth import get_current_user_email
from datetime import datetime
from bson import ObjectId
from typing import Optional

router = APIRouter(prefix="/admin/reviews", tags=["Admin - Reviews"])

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
async def get_all_reviews_admin(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    review_type: Optional[str] = None,  # verified, imported, unverified
    status_filter: Optional[str] = None,  # pending, approved, rejected, published
    is_flagged: Optional[bool] = None,
    shop_id: Optional[str] = None,
    search: Optional[str] = None,  # Search in comment, shop_name, user_name
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all reviews with admin filters."""
    await check_admin(email, db)
    
    # Build query
    query = {}
    if review_type:
        query["review_type"] = review_type
    if status_filter:
        query["status"] = status_filter
    if is_flagged is not None:
        query["is_flagged"] = is_flagged
    if shop_id:
        query["shop_id"] = shop_id
    
    # Text search in comment
    if search:
        query["comment"] = {"$regex": search, "$options": "i"}
    
    # Get total count
    total = await db.reviews.count_documents(query)
    
    # Calculate pagination
    skip = (page - 1) * limit
    pages = (total + limit - 1) // limit
    
    # Get reviews without aggregation to avoid ObjectId conversion issues
    # If search is provided, get more reviews for filtering after enrichment
    fetch_limit = limit * 3 if search else limit
    reviews = await db.reviews.find(query).sort("created_at", -1).skip(skip).limit(fetch_limit).to_list(None)
    
    # Manually enrich with user and shop info
    enriched_reviews = []
    for review in reviews:
        # Get user info
        try:
            user_id = review.get("user_id")
            if user_id:
                if ObjectId.is_valid(user_id):
                    user = await db.users.find_one({"_id": ObjectId(user_id)})
                else:
                    user = await db.users.find_one({"_id": user_id})
                
                if user:
                    review["user_name"] = user.get("full_name", "Unknown")
                    review["user_email"] = user.get("email", "")
        except Exception as e:
            print(f"Error fetching user: {e}")
            review["user_name"] = "Unknown"
            review["user_email"] = ""
        
        # Get shop info
        try:
            shop_id = review.get("shop_id")
            if shop_id:
                # Try as string first (UUID)
                shop = await db.shops.find_one({"_id": shop_id})
                
                # If not found, try as ObjectId
                if not shop and ObjectId.is_valid(shop_id):
                    shop = await db.shops.find_one({"_id": ObjectId(shop_id)})
                
                if shop:
                    review["shop_name"] = shop.get("name", "Unknown")
        except Exception as e:
            print(f"Error fetching shop: {e}")
            review["shop_name"] = "Unknown"
        
        # Add to enriched list
        enriched_reviews.append(review)
    
    # Filter by search term after enrichment (for shop_name and user_name)
    if search:
        search_lower = search.lower()
        enriched_reviews = [
            r for r in enriched_reviews
            if search_lower in r.get("comment", "").lower()
            or search_lower in r.get("shop_name", "").lower()
            or search_lower in r.get("user_name", "").lower()
        ]
        # Update total count after filtering
        total = len(enriched_reviews)
        pages = (total + limit - 1) // limit
        # Apply pagination
        enriched_reviews = enriched_reviews[:limit]
    
    # Format reviews
    for review in enriched_reviews:
        review["_id"] = str(review["_id"])
    
    return {
        "data": enriched_reviews,
        "total": total,
        "page": page,
        "pages": pages
    }

@router.get("/pending")
async def get_pending_reviews(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all pending reviews (low-star reviews awaiting approval)."""
    await check_admin(email, db)
    
    query = {"status": "pending"}
    
    # Get total count
    total = await db.reviews.count_documents(query)
    
    # Calculate pagination
    skip = (page - 1) * limit
    pages = (total + limit - 1) // limit
    
    # Get reviews
    reviews = await db.reviews.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(None)
    
    # Format reviews
    for review in reviews:
        review["_id"] = str(review["_id"])
        
        # Get user info
        try:
            user_id = review.get("user_id")
            if ObjectId.is_valid(user_id):
                user = await db.users.find_one({"_id": ObjectId(user_id)})
            else:
                user = await db.users.find_one({"_id": user_id})
            
            if user:
                review["user_name"] = user.get("full_name", "Unknown")
                review["user_email"] = user.get("email", "")
            else:
                review["user_name"] = "Unknown"
                review["user_email"] = ""
        except Exception as e:
            print(f"Error fetching user: {e}")
            review["user_name"] = "Unknown"
            review["user_email"] = ""
        
        # Get shop info
        try:
            shop_id = review.get("shop_id")
            # Try as string first (UUID)
            shop = await db.shops.find_one({"_id": shop_id})
            
            # If not found, try as ObjectId
            if not shop and ObjectId.is_valid(shop_id):
                shop = await db.shops.find_one({"_id": ObjectId(shop_id)})
            
            if shop:
                review["shop_name"] = shop.get("name", "Unknown")
            else:
                review["shop_name"] = "Unknown"
        except Exception as e:
            print(f"Error fetching shop: {e}")
            review["shop_name"] = "Unknown"
    
    return {
        "data": reviews,
        "total": total,
        "page": page,
        "pages": pages
    }

@router.post("/{review_id}/action")
async def admin_review_action(
    review_id: str,
    action_data: AdminReviewAction,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Approve or reject a pending review."""
    admin = await check_admin(email, db)
    
    # Validate review exists
    if not ObjectId.is_valid(review_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid review ID"
        )
    
    review = await db.reviews.find_one({"_id": ObjectId(review_id)})
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Update review status
    new_status = "approved" if action_data.action == "approve" else "rejected"
    
    update_data = {
        "status": new_status,
        "reviewed_by_admin": str(admin["_id"]),
        "review_date": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    if action_data.admin_notes:
        update_data["admin_notes"] = action_data.admin_notes
    
    await db.reviews.update_one(
        {"_id": ObjectId(review_id)},
        {"$set": update_data}
    )
    
    # Update shop rating if approved
    if action_data.action == "approve":
        from routes.review_routes import update_shop_rating
        await update_shop_rating(review["shop_id"], db)
    
    return {
        "success": True,
        "message": f"Review {action_data.action}d successfully",
        "new_status": new_status
    }

@router.delete("/{review_id}")
async def delete_review_admin(
    review_id: str,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete a review (admin only)."""
    await check_admin(email, db)
    
    if not ObjectId.is_valid(review_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid review ID"
        )
    
    review = await db.reviews.find_one({"_id": ObjectId(review_id)})
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Delete review
    await db.reviews.delete_one({"_id": ObjectId(review_id)})
    
    # Update shop rating
    from routes.review_routes import update_shop_rating
    await update_shop_rating(review["shop_id"], db)
    
    return {"success": True, "message": "Review deleted successfully"}
