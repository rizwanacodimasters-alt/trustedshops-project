from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from models_extended import ReviewResponseCreate, ReviewResponse
from auth import get_current_user_email
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/review-responses", tags=["Review Responses"])

def get_db():
    from server import db
    return db

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_review_response(
    response_data: ReviewResponseCreate,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a response to a review (shop owner only)."""
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
            detail="Shop owner role required"
        )
    
    # Get review
    if not ObjectId.is_valid(response_data.review_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid review ID"
        )
    
    review = await db.reviews.find_one({"_id": ObjectId(response_data.review_id)})
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Check if user owns the shop
    shop = await db.shops.find_one({"_id": ObjectId(review["shop_id"])})
    if not shop or (shop["owner_id"] != str(user["_id"]) and user["role"] != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to respond to this review"
        )
    
    # Check if response already exists
    existing = await db.review_responses.find_one({"review_id": response_data.review_id})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Response already exists for this review"
        )
    
    # Create response
    response_dict = response_data.dict()
    response_dict.update({
        "shop_id": review["shop_id"],
        "responder_id": str(user["_id"]),
        "created_at": datetime.utcnow()
    })
    
    result = await db.review_responses.insert_one(response_dict)
    
    # Create clean response without _id field
    clean_response = {
        "id": str(result.inserted_id),
        "review_id": response_dict["review_id"],
        "response_text": response_dict["response_text"],
        "shop_id": response_dict["shop_id"],
        "responder_id": response_dict["responder_id"],
        "created_at": response_dict["created_at"]
    }
    
    return clean_response

@router.get("/review/{review_id}")
async def get_review_response(
    review_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get response for a specific review."""
    response = await db.review_responses.find_one({"review_id": review_id})
    
    if not response:
        return None
    
    response["id"] = str(response["_id"])
    del response["_id"]
    
    # Get responder info
    responder = await db.users.find_one({"_id": ObjectId(response["responder_id"])})
    if responder:
        response["responder_name"] = responder["full_name"]
    
    return response

@router.delete("/{response_id}")
async def delete_review_response(
    response_id: str,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete a review response (owner only)."""
    if not ObjectId.is_valid(response_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid response ID"
        )
    
    # Get current user
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get response
    response = await db.review_responses.find_one({"_id": ObjectId(response_id)})
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Response not found"
        )
    
    # Check ownership
    if response["responder_id"] != str(user["_id"]) and user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this response"
        )
    
    await db.review_responses.delete_one({"_id": ObjectId(response_id)})
    
    return {"message": "Response deleted successfully"}
