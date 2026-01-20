from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from models import LowStarProofUpload
from auth import get_current_user_email
from datetime import datetime
from bson import ObjectId
from utils.content_filter import validate_proof_data

router = APIRouter(prefix="/reviews", tags=["Reviews"])

def get_db():
    from server import db
    return db

@router.post("/{review_id}/upload-proof")
async def upload_proof_for_low_star_review(
    review_id: str,
    proof_data: LowStarProofUpload,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Upload proof for low-star review (1-2 stars).
    Required: product photos, chat history, order number.
    """
    # Get current user
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate review exists and belongs to user
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
    
    if review["user_id"] != str(user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only upload proof for your own reviews"
        )
    
    # Check if review is low-star (1-2)
    if review["rating"] > 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Proof upload is only required for 1-2 star reviews"
        )
    
    # Check if review is still pending
    if review["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Proof can only be uploaded for pending reviews"
        )
    
    # Validate proof data
    is_valid, error_msg = validate_proof_data(
        proof_data.proof_photos,
        proof_data.proof_chat_history,
        proof_data.proof_order_number
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Update review with proof
    await db.reviews.update_one(
        {"_id": ObjectId(review_id)},
        {
            "$set": {
                "proof_photos": proof_data.proof_photos,
                "proof_chat_history": proof_data.proof_chat_history,
                "proof_order_number": proof_data.proof_order_number,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return {
        "success": True,
        "message": "Nachweis erfolgreich hochgeladen. Ihre Bewertung wird von einem Administrator geprüft.",
        "review_id": review_id
    }

@router.get("/{review_id}/proof")
async def get_review_proof(
    review_id: str,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get proof data for a review (user must be owner or admin)."""
    # Get current user
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get review
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
    
    # Check permissions (owner or admin)
    if review["user_id"] != str(user["_id"]) and user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view proof for your own reviews"
        )
    
    # Return proof data
    return {
        "review_id": str(review["_id"]),
        "rating": review["rating"],
        "status": review["status"],
        "proof_photos": review.get("proof_photos", []),
        "proof_chat_history": review.get("proof_chat_history"),
        "proof_order_number": review.get("proof_order_number"),
        "admin_notes": review.get("admin_notes"),
        "reviewed_by_admin": review.get("reviewed_by_admin"),
        "review_date": review.get("review_date")
    }
