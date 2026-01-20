from fastapi import APIRouter, HTTPException, status, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field
from typing import Optional, Dict
from auth import get_current_user_email
from datetime import datetime
import os
try:
    from emergentintegrations.payments.stripe.checkout import (
        StripeCheckout,
        CheckoutSessionResponse,
        CheckoutStatusResponse,
        CheckoutSessionRequest,
    )
    BILLING_AVAILABLE = True
except Exception:
    StripeCheckout = None
    CheckoutSessionResponse = None
    CheckoutStatusResponse = None
    CheckoutSessionRequest = None
    BILLING_AVAILABLE = False

router = APIRouter(prefix="/billing", tags=["Billing"])

def get_db():
    from server import db
    return db

# Predefined subscription plans
SUBSCRIPTION_PLANS = {
    "basic": {"name": "Basic", "price": 9.99, "currency": "usd"},
    "professional": {"name": "Professional", "price": 29.99, "currency": "usd"},
    "enterprise": {"name": "Enterprise", "price": 99.99, "currency": "usd"}
}

class CreateCheckoutRequest(BaseModel):
    plan_id: str = Field(..., description="Plan ID (basic, professional, enterprise)")
    origin_url: str = Field(..., description="Frontend origin URL")

@router.get("/plans")
async def get_plans():
    """Get available subscription plans."""
    return {"plans": SUBSCRIPTION_PLANS}

@router.post("/checkout")
async def create_checkout_session(
    request: CreateCheckoutRequest,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create Stripe checkout session for subscription."""
    if not BILLING_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Billing integrations not installed"
        )
    # Validate plan
    if request.plan_id not in SUBSCRIPTION_PLANS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan ID"
        )
    
    # Get user
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    plan = SUBSCRIPTION_PLANS[request.plan_id]
    
    # Initialize Stripe
    stripe_api_key = os.environ.get("STRIPE_API_KEY")
    if not stripe_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stripe API key not configured"
        )
    
    # Build success and cancel URLs
    success_url = f"{request.origin_url}/billing/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{request.origin_url}/shop-dashboard"
    
    # Create webhook URL (construct from origin)
    # For development, we'll use the same origin
    webhook_url = f"{request.origin_url}/api/webhook/stripe"
    
    try:
        stripe_checkout = StripeCheckout(
            api_key=stripe_api_key,
            webhook_url=webhook_url
        )
        
        # Create checkout session
        checkout_request = CheckoutSessionRequest(
            amount=plan["price"],
            currency=plan["currency"],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": str(user["_id"]),
                "user_email": email,
                "plan_id": request.plan_id,
                "plan_name": plan["name"]
            }
        )
        
        session: CheckoutSessionResponse = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Store payment transaction
        transaction = {
            "session_id": session.session_id,
            "user_id": str(user["_id"]),
            "user_email": email,
            "plan_id": request.plan_id,
            "plan_name": plan["name"],
            "amount": plan["price"],
            "currency": plan["currency"],
            "payment_status": "pending",
            "status": "initiated",
            "created_at": datetime.utcnow()
        }
        
        await db.payment_transactions.insert_one(transaction)
        
        return {
            "url": session.url,
            "session_id": session.session_id
        }
    
    except Exception as e:
        print(f"Error creating checkout session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}"
        )

@router.get("/checkout/status/{session_id}")
async def get_checkout_status(
    session_id: str,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get checkout session status."""
    if not BILLING_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Billing integrations not installed"
        )
    # Get transaction
    transaction = await db.payment_transactions.find_one({"session_id": session_id})
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    # Check if already processed
    if transaction.get("payment_status") == "paid":
        return {
            "status": "complete",
            "payment_status": "paid",
            "plan_name": transaction.get("plan_name")
        }
    
    # Check with Stripe
    stripe_api_key = os.environ.get("STRIPE_API_KEY")
    webhook_url = "https://example.com/webhook"  # Placeholder
    
    try:
        stripe_checkout = StripeCheckout(
            api_key=stripe_api_key,
            webhook_url=webhook_url
        )
        
        checkout_status: CheckoutStatusResponse = await stripe_checkout.get_checkout_status(session_id)
        
        # Update transaction if payment is complete
        if checkout_status.payment_status == "paid" and transaction.get("payment_status") != "paid":
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "payment_status": "paid",
                        "status": "complete",
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Update user subscription
            await db.users.update_one(
                {"email": email},
                {
                    "$set": {
                        "subscription_plan": transaction.get("plan_id"),
                        "subscription_status": "active",
                        "subscription_updated_at": datetime.utcnow()
                    }
                }
            )
        
        return {
            "status": checkout_status.status,
            "payment_status": checkout_status.payment_status,
            "amount_total": checkout_status.amount_total,
            "currency": checkout_status.currency
        }
    
    except Exception as e:
        print(f"Error checking checkout status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check checkout status"
        )

@router.post("/webhook/stripe")
async def stripe_webhook(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if not BILLING_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Billing integrations not installed"
        )
    """Handle Stripe webhooks."""
    body = await request.body()
    signature = request.headers.get("Stripe-Signature")
    
    stripe_api_key = os.environ.get("STRIPE_API_KEY")
    webhook_url = "https://example.com/webhook"  # Placeholder
    
    try:
        stripe_checkout = StripeCheckout(
            api_key=stripe_api_key,
            webhook_url=webhook_url
        )
        
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        # Handle webhook event
        if webhook_response.payment_status == "paid":
            transaction = await db.payment_transactions.find_one(
                {"session_id": webhook_response.session_id}
            )
            
            if transaction and transaction.get("payment_status") != "paid":
                # Update transaction
                await db.payment_transactions.update_one(
                    {"session_id": webhook_response.session_id},
                    {
                        "$set": {
                            "payment_status": "paid",
                            "status": "complete",
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                
                # Update user subscription
                user_email = transaction.get("user_email")
                if user_email:
                    await db.users.update_one(
                        {"email": user_email},
                        {
                            "$set": {
                                "subscription_plan": transaction.get("plan_id"),
                                "subscription_status": "active",
                                "subscription_updated_at": datetime.utcnow()
                            }
                        }
                    )
        
        return {"status": "success"}
    
    except Exception as e:
        print(f"Webhook error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook processing failed"
        )

@router.get("/subscription")
async def get_subscription(
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get user's current subscription."""
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    plan_id = user.get("subscription_plan", "basic")
    plan = SUBSCRIPTION_PLANS.get(plan_id, SUBSCRIPTION_PLANS["basic"])
    
    return {
        "plan_id": plan_id,
        "plan_name": plan["name"],
        "price": plan["price"],
        "currency": plan["currency"],
        "status": user.get("subscription_status", "active"),
        "updated_at": user.get("subscription_updated_at")
    }

@router.get("/transactions")
async def get_transactions(
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get user's payment transactions."""
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    transactions = await db.payment_transactions.find(
        {"user_email": email}
    ).sort("created_at", -1).limit(10).to_list(10)
    
    for transaction in transactions:
        transaction["id"] = str(transaction["_id"])
        del transaction["_id"]
    
    return {"transactions": transactions}
