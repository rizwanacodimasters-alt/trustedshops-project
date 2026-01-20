from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from models_extended import ShopVerification
from auth import get_current_user_email
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/shop-verification", tags=["Shop Verification"])

def get_db():
    from server import db
    return db

@router.post("/request/{shop_id}")
async def request_verification(
    shop_id: str,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Request shop verification."""
    # Get current user
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate shop
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
    
    # Check ownership
    if shop["owner_id"] != str(user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Check if already verified
    if shop.get("is_verified", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Shop is already verified"
        )
    
    # Check for existing pending verification
    existing = await db.shop_verifications.find_one({
        "shop_id": shop_id,
        "status": "pending"
    })
    
    if existing:
        return {
            "message": "Verification request already exists",
            "status": "pending"
        }
    
    # Create verification request
    verification = {
        "shop_id": shop_id,
        "status": "pending",
        "verification_type": "manual",
        "created_at": datetime.utcnow()
    }
    
    result = await db.shop_verifications.insert_one(verification)
    verification["id"] = str(result.inserted_id)
    
    # Remove _id field to avoid serialization error
    if "_id" in verification:
        del verification["_id"]
    
    return {
        "message": "Verification requested successfully",
        "verification": verification
    }

@router.post("/approve/{shop_id}")
async def approve_verification(
    shop_id: str,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Approve shop verification (admin only)."""
    # Get current user
    user = await db.users.find_one({"email": email})
    if not user or user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Update verification
    await db.shop_verifications.update_one(
        {"shop_id": shop_id, "status": "pending"},
        {
            "$set": {
                "status": "verified",
                "verified_by": str(user["_id"]),
                "verified_at": datetime.utcnow()
            }
        }
    )
    
    # Update shop
    await db.shops.update_one(
        {"_id": ObjectId(shop_id)},
        {"$set": {"is_verified": True}}
    )
    
    return {"message": "Shop verified successfully"}

@router.post("/reject/{shop_id}")
async def reject_verification(
    shop_id: str,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Reject shop verification (admin only)."""
    # Get current user
    user = await db.users.find_one({"email": email})
    if not user or user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Update verification
    await db.shop_verifications.update_one(
        {"shop_id": shop_id, "status": "pending"},
        {
            "$set": {
                "status": "rejected",
                "rejected_by": str(user["_id"]),
                "rejected_at": datetime.utcnow()
            }
        }
    )
    
    return {"message": "Verification request rejected"}

@router.get("/all")
async def get_all_verification_requests(
    status_filter: str = "pending",  # pending, verified, rejected, all
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all verification requests (admin only)."""
    # Get current user
    user = await db.users.find_one({"email": email})
    if not user or user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Build query
    query = {}
    if status_filter and status_filter != "all":
        query["status"] = status_filter
    
    # Get verification requests with shop details
    pipeline = [
        {"$match": query},
        {"$sort": {"created_at": -1}},
        {
            "$lookup": {
                "from": "shops",
                "let": {"shop_id": {"$toObjectId": "$shop_id"}},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$_id", "$$shop_id"]}}},
                    {"$project": {"name": 1, "website": 1, "category": 1, "owner_id": 1}}
                ],
                "as": "shop_info"
            }
        }
    ]
    
    verifications = await db.shop_verifications.aggregate(pipeline).to_list(None)
    
    # Format and enrich data
    result = []
    for verification in verifications:
        verification["id"] = str(verification["_id"])
        del verification["_id"]
        
        if verification.get("shop_info") and len(verification["shop_info"]) > 0:
            shop = verification["shop_info"][0]
            verification["shop_name"] = shop.get("name", "Unknown")
            verification["shop_website"] = shop.get("website", "")
            verification["shop_category"] = shop.get("category", "")
            
            # Get owner info
            owner_id = shop.get("owner_id")
            if owner_id:
                owner = await db.users.find_one({"id": owner_id})
                if owner:
                    verification["owner_name"] = owner.get("full_name", "Unknown")
                    verification["owner_email"] = owner.get("email", "")
        else:
            verification["shop_name"] = "Unknown"
            verification["shop_website"] = ""
            verification["shop_category"] = ""
            verification["owner_name"] = "Unknown"
            verification["owner_email"] = ""
        
        del verification["shop_info"]
        result.append(verification)
    
    return {
        "data": result,
        "total": len(result)
    }

@router.get("/status/{shop_id}")
async def get_verification_status(
    shop_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get shop verification status."""
    shop = await db.shops.find_one({"_id": ObjectId(shop_id)})
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shop not found"
        )
    
    verification = await db.shop_verifications.find_one(
        {"shop_id": shop_id},
        sort=[("created_at", -1)]
    )
    
    return {
        "shop_id": shop_id,
        "is_verified": shop.get("is_verified", False),
        "verification_status": verification["status"] if verification else "not_requested",
        "verified_at": verification.get("verified_at") if verification else None
    }
