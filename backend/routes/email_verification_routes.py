from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from datetime import datetime, timedelta
import random
import string
import logging
from services.email_service import get_email_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/email-verification", tags=["Email Verification"])

def get_db():
    from server import db
    return db

class VerificationCodeRequest(BaseModel):
    email: str

class VerificationCodeVerify(BaseModel):
    email: str
    code: str

def generate_verification_code():
    """Generate a 5-digit verification code."""
    return ''.join(random.choices(string.digits, k=5))

@router.post("/send-code")
async def send_verification_code(
    request: VerificationCodeRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Send a 5-digit verification code to user's email."""
    # Check if user exists
    user = await db.users.find_one({"email": request.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already verified
    if user.get("email_verified", False):
        return {
            "message": "Email already verified",
            "already_verified": True
        }
    
    # Generate code
    code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=15)  # 15 minutes expiry
    
    # Store verification code
    await db.email_verifications.update_one(
        {"email": request.email},
        {
            "$set": {
                "code": code,
                "expires_at": expires_at,
                "created_at": datetime.utcnow(),
                "attempts": 0
            }
        },
        upsert=True
    )
    
    # Send verification email
    try:
        email_service = get_email_service()
        email_sent = email_service.send_verification_email(request.email, code)
        
        if not email_sent:
            logger.error(f"Failed to send verification email to {request.email}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification email. Please try again later."
            )
        
        logger.info(f"✅ Verification email sent successfully to {request.email}")
        
        # Include code in response for development/testing
        response_data = {
            "message": "Verification code sent to email",
            "expires_in_minutes": 15,
            "email": request.email
        }
        
        # In development mode, include the code in response
        import os
        if os.getenv('DEV_MODE', '').lower() == 'true':
            response_data["code"] = code
            logger.info(f"🔐 DEV MODE: Verification code for {request.email}: {code}")
        
        return response_data
        
    except ValueError as e:
        # SMTP configuration error
        logger.error(f"SMTP configuration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email service is not properly configured"
        )
    except Exception as e:
        logger.error(f"Unexpected error sending email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email"
        )

@router.post("/verify-code")
async def verify_code(
    request: VerificationCodeVerify,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Verify the 5-digit code."""
    # Get verification record
    verification = await db.email_verifications.find_one({"email": request.email})
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No verification code found. Please request a new code."
        )
    
    # Check if expired
    if datetime.utcnow() > verification["expires_at"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code has expired. Please request a new code."
        )
    
    # Check attempts (max 5)
    if verification.get("attempts", 0) >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed attempts. Please request a new code."
        )
    
    # Verify code
    if verification["code"] != request.code:
        # Increment attempts
        await db.email_verifications.update_one(
            {"email": request.email},
            {"$inc": {"attempts": 1}}
        )
        
        remaining = 5 - (verification.get("attempts", 0) + 1)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid verification code. {remaining} attempts remaining."
        )
    
    # Mark user as verified
    await db.users.update_one(
        {"email": request.email},
        {
            "$set": {
                "email_verified": True,
                "email_verified_at": datetime.utcnow()
            }
        }
    )
    
    # Delete verification record
    await db.email_verifications.delete_one({"email": request.email})
    
    return {
        "message": "Email verified successfully",
        "verified": True
    }

@router.get("/check-status/{email}")
async def check_verification_status(
    email: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Check if email is verified."""
    user = await db.users.find_one({"email": email})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "email": email,
        "verified": user.get("email_verified", False),
        "verified_at": user.get("email_verified_at")
    }
