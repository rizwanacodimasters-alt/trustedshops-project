from fastapi import APIRouter, HTTPException, status, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from models import ReviewCreate, ReviewUpdate, Review, LowStarProofUpload
from auth import get_current_user_email
from datetime import datetime, timedelta
from bson import ObjectId
from typing import Optional
import math
from utils.content_filter import check_content, should_require_proof, calculate_trust_score_grade

router = APIRouter(prefix="/reviews", tags=["Reviews"])

def get_db():
    from server import db
    return db

def format_user_name(full_name: str) -> str:
    """
    Format user name to show first name + last name initial.
    Example: "Sarah Klein" -> "Sarah K."
    """
    if not full_name:
        return "Verifizierter Kunde"
    
    name_parts = full_name.strip().split()
    
    if len(name_parts) == 0:
        return "Verifizierter Kunde"
    elif len(name_parts) == 1:
        # Only first name
        return name_parts[0]
    else:
        # First name + Last name initial
        first_name = name_parts[0]
        last_initial = name_parts[-1][0].upper()
        return f"{first_name} {last_initial}."

async def update_shop_rating(shop_id: str, db: AsyncIOMotorDatabase):
    """
    Update shop rating based on VERIFIED reviews from last 12 months only.
    Following Trusted Shops model.
    """
    # Calculate date 12 months ago
    twelve_months_ago = datetime.utcnow() - timedelta(days=365)
    
    pipeline = [
        {
            "$match": {
                "shop_id": shop_id,
                "review_type": "verified",  # Only verified reviews count
                "status": {"$in": ["published", "approved"]},  # Only published/approved
                "created_at": {"$gte": twelve_months_ago}  # Last 12 months only
            }
        },
        {
            "$group": {
                "_id": None,
                "avg_rating": {"$avg": "$rating"},
                "count": {"$sum": 1}
            }
        }
    ]
    
    result = await db.reviews.aggregate(pipeline).to_list(1)
    
    if result:
        avg_rating = round(result[0]["avg_rating"], 2)
        count = result[0]["count"]
    else:
        avg_rating = 0.0
        count = 0
    
    # Calculate Trusted Shops grade
    grade_info = calculate_trust_score_grade(avg_rating)
    
    # Handle both ObjectId and UUID string
    try:
        shop_obj_id = ObjectId(shop_id) if ObjectId.is_valid(shop_id) else shop_id
    except:
        shop_obj_id = shop_id
    
    await db.shops.update_one(
        {"_id": shop_obj_id},
        {
            "$set": {
                "rating": avg_rating,
                "review_count": count,
                "trust_grade": grade_info['grade'],
                "trust_label": grade_info['label']
            }
        }
    )

@router.get("", response_model=dict)
async def get_reviews(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    shop_id: Optional[str] = None,
    user_id: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all reviews with pagination and filters."""
    # Build query
    query = {}
    if shop_id:
        query["shop_id"] = shop_id
    if user_id:
        query["user_id"] = user_id
    
    # Search in comment
    if search:
        query["comment"] = {"$regex": search, "$options": "i"}
    
    # Get total count
    total = await db.reviews.count_documents(query)
    
    # Calculate pagination
    skip = (page - 1) * limit
    pages = math.ceil(total / limit) if total > 0 else 1
    
    # Get reviews with user and shop details
    # Support both ObjectId and UUID string formats
    pipeline = [
        {"$match": query},
        {"$sort": {"created_at": -1}},
        {"$skip": skip},
        {"$limit": limit},
        {
            "$lookup": {
                "from": "users",
                "localField": "user_id",
                "foreignField": "id",
                "as": "user_info"
            }
        },
        {
            "$lookup": {
                "from": "shops",
                "localField": "shop_id",
                "foreignField": "id",
                "as": "shop_info"
            }
        }
    ]
    
    reviews = await db.reviews.aggregate(pipeline).to_list(limit)
    
    # Format reviews
    for review in reviews:
        review["id"] = str(review["_id"])
        del review["_id"]
        
        # Add user info
        if review.get("user_info") and len(review["user_info"]) > 0:
            user = review["user_info"][0]
            full_name = user.get("full_name", "")
            # Format name: "Sarah Klein" -> "Sarah K."
            review["user_name"] = format_user_name(full_name)
            # Create initials
            name_parts = full_name.split() if full_name else ["V", "K"]
            review["user_initials"] = "".join([part[0].upper() for part in name_parts[:2]])
        else:
            review["user_name"] = "Verifizierter Kunde"
            review["user_initials"] = "VK"
        
        # Add shop info
        if review.get("shop_info") and len(review["shop_info"]) > 0:
            shop = review["shop_info"][0]
            review["shop_name"] = shop.get("name", "Unknown")
            review["shop_website"] = shop.get("website", "")
        else:
            review["shop_name"] = "Unknown Shop"
            review["shop_website"] = ""
        
        # Clean up
        if "user_info" in review:
            del review["user_info"]
        if "shop_info" in review:
            del review["shop_info"]
    
    return {
        "data": reviews,
        "total": total,
        "page": page,
        "pages": pages
    }

@router.post("", response_model=Review, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new review (requires authentication)."""
    # Get current user
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate shop exists
    if not ObjectId.is_valid(review_data.shop_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid shop ID"
        )
    
    shop = await db.shops.find_one({"_id": ObjectId(review_data.shop_id)})
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shop not found"
        )
    
    # Check content filters
    is_clean, flags, reasons = check_content(review_data.comment, shop.get('industry'))
    if not is_clean:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Review enthält unzulässige Inhalte: {', '.join(reasons)}"
        )
    
    # Check for low-star rating (1-3 stars require proof)
    requires_proof = should_require_proof(review_data.rating)
    
    # Validate proof if required
    if requires_proof:
        from utils.content_filter import validate_proof_data
        is_valid, error_msg = validate_proof_data(
            review_data.proof_photos or [],
            review_data.proof_order_number or "",
            review_data.rating
        )
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
    
    initial_status = "pending" if requires_proof else "published"
    
    # Verify purchase if order_id provided
    is_verified_purchase = False
    verification_date = None
    review_type = "verified"
    
    if review_data.order_id:
        # Check if order exists and belongs to user
        order = await db.orders.find_one({
            "_id": ObjectId(review_data.order_id) if ObjectId.is_valid(review_data.order_id) else None,
            "user_id": str(user["_id"]),
            "shop_id": review_data.shop_id
        })
        
        if order:
            # Check order age (< 6 months)
            six_months_ago = datetime.utcnow() - timedelta(days=180)
            if order.get("created_at", datetime.utcnow()) >= six_months_ago:
                is_verified_purchase = True
                verification_date = datetime.utcnow()
                
                # Check if order already has a review
                existing_order_review = await db.reviews.find_one({
                    "order_id": review_data.order_id
                })
                if existing_order_review:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Diese Bestellung wurde bereits bewertet"
                    )
    
    # Check if user already reviewed this shop (without order)
    existing_review = await db.reviews.find_one({
        "user_id": str(user["_id"]),
        "shop_id": review_data.shop_id,
        "order_id": None  # Only check non-order reviews
    })
    if existing_review and not review_data.order_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sie haben diesen Shop bereits bewertet"
        )
    
    # Create review document
    review_dict = review_data.dict()
    review_dict.update({
        "user_id": str(user["_id"]),
        "review_type": review_type,
        "status": initial_status,
        "is_verified_purchase": is_verified_purchase,
        "verification_date": verification_date,
        "content_flags": flags,
        "is_flagged": len(flags) > 0,
        "proof_photos": review_data.proof_photos or [],
        "proof_order_number": review_data.proof_order_number,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    
    # Insert review
    result = await db.reviews.insert_one(review_dict)
    review_dict["id"] = str(result.inserted_id)
    
    # Remove _id field to avoid validation error
    if "_id" in review_dict:
        del review_dict["_id"]
    
    # Update shop rating
    await update_shop_rating(review_data.shop_id, db)
    
    # Add user and shop info
    full_name = user.get("full_name", "")
    review_dict["user_name"] = format_user_name(full_name)
    name_parts = full_name.split() if full_name else ["V", "K"]
    review_dict["user_initials"] = "".join([part[0].upper() for part in name_parts[:2]])
    review_dict["shop_name"] = shop["name"]
    review_dict["shop_website"] = shop["website"]
    
    return review_dict

@router.put("/{review_id}", response_model=Review)
async def update_review(
    review_id: str,
    review_data: ReviewUpdate,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update review (owner only)."""
    if not ObjectId.is_valid(review_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid review ID"
        )
    
    # Get current user
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get review
    review = await db.reviews.find_one({"_id": ObjectId(review_id)})
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Check ownership
    if review["user_id"] != str(user["_id"]) and user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this review"
        )
    
    # Prepare update data
    update_data = {k: v for k, v in review_data.dict(exclude_unset=True).items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    # Check if rating is being updated to 1-3 stars
    new_rating = review_data.rating if review_data.rating is not None else review.get("rating", 5)
    
    # Validate proof for low-star reviews (1-3 stars)
    if new_rating <= 3:
        from utils.content_filter import should_require_proof, validate_proof_data
        
        if should_require_proof(new_rating):
            # Use new proof data if provided, otherwise keep existing
            proof_photos = review_data.proof_photos if review_data.proof_photos is not None else review.get("proof_photos", [])
            proof_order_number = review_data.proof_order_number if review_data.proof_order_number is not None else review.get("proof_order_number", "")
            
            is_valid, error_msg = validate_proof_data(proof_photos, proof_order_number, new_rating)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_msg
                )
            
            # Set status back to pending if rating changed to 1-3 stars or proof changed
            if review.get("rating", 5) > 3 or review_data.proof_photos is not None or review_data.proof_order_number is not None:
                update_data["status"] = "pending"
    
    await db.reviews.update_one(
        {"_id": ObjectId(review_id)},
        {"$set": update_data}
    )
    
    # Update shop rating
    await update_shop_rating(review["shop_id"], db)
    
    # Get updated review with details
    updated_review = await db.reviews.find_one({"_id": ObjectId(review_id)})
    shop = await db.shops.find_one({"_id": ObjectId(review["shop_id"])})
    
    updated_review["id"] = str(updated_review["_id"])
    del updated_review["_id"]  # Remove _id to avoid serialization issues
    full_name = user.get("full_name", "")
    updated_review["user_name"] = format_user_name(full_name)
    name_parts = full_name.split() if full_name else ["V", "K"]
    updated_review["user_initials"] = "".join([part[0].upper() for part in name_parts[:2]])
    updated_review["shop_name"] = shop["name"]
    updated_review["shop_website"] = shop["website"]
    
    return updated_review

@router.delete("/{review_id}")
async def delete_review(
    review_id: str,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete review (owner only)."""
    if not ObjectId.is_valid(review_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid review ID"
        )
    
    # Get current user
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get review
    review = await db.reviews.find_one({"_id": ObjectId(review_id)})
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Check ownership
    if review["user_id"] != str(user["_id"]) and user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this review"
        )
    
    shop_id = review["shop_id"]
    
    # Delete review
    await db.reviews.delete_one({"_id": ObjectId(review_id)})
    
    # Update shop rating
    await update_shop_rating(shop_id, db)
    
    return {"message": "Review deleted successfully"}
