#!/usr/bin/env python3
"""
Migration script to update existing reviews with new fields.
Run this once to update the database schema.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from datetime import datetime

async def migrate_reviews():
    """Update all existing reviews with new required fields."""
    
    # Load environment
    load_dotenv()
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ['DB_NAME']
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("🔄 Starting review migration...")
    
    # Get all reviews
    reviews = await db.reviews.find({}).to_list(None)
    print(f"📊 Found {len(reviews)} reviews to migrate")
    
    updated_count = 0
    
    for review in reviews:
        # Prepare update data
        update_data = {}
        
        # Add review_type if missing
        if "review_type" not in review:
            update_data["review_type"] = "verified"  # Mark existing as verified
        
        # Add status if missing
        if "status" not in review:
            update_data["status"] = "published"  # Existing reviews are published
        
        # Add verification fields if missing
        if "is_verified_purchase" not in review:
            update_data["is_verified_purchase"] = True  # Assume verified
        
        if "verification_date" not in review:
            update_data["verification_date"] = review.get("created_at", datetime.utcnow())
        
        # Add proof fields if missing
        if "proof_photos" not in review:
            update_data["proof_photos"] = []
        
        if "proof_chat_history" not in review:
            update_data["proof_chat_history"] = None
        
        if "proof_order_number" not in review:
            update_data["proof_order_number"] = None
        
        # Add moderation fields if missing
        if "content_flags" not in review:
            update_data["content_flags"] = []
        
        if "is_flagged" not in review:
            update_data["is_flagged"] = False
        
        if "flag_reason" not in review:
            update_data["flag_reason"] = None
        
        # Add admin review fields if missing
        if "admin_notes" not in review:
            update_data["admin_notes"] = None
        
        if "reviewed_by_admin" not in review:
            update_data["reviewed_by_admin"] = None
        
        if "review_date" not in review:
            update_data["review_date"] = None
        
        # Add unverified workflow fields if missing
        if "email" not in review:
            update_data["email"] = None
        
        if "verification_token" not in review:
            update_data["verification_token"] = None
        
        if "email_verified" not in review:
            update_data["email_verified"] = True  # Existing are verified
        
        # Add order fields if missing
        if "order_id" not in review:
            update_data["order_id"] = None
        
        if "order_reference" not in review:
            update_data["order_reference"] = None
        
        # Update review if there are changes
        if update_data:
            await db.reviews.update_one(
                {"_id": review["_id"]},
                {"$set": update_data}
            )
            updated_count += 1
    
    print(f"✅ Migration complete! Updated {updated_count} reviews")
    
    # Update shop ratings to use new calculation
    print("🔄 Recalculating shop ratings...")
    
    shops = await db.shops.find({}).to_list(None)
    
    for shop in shops:
        from routes.review_routes import update_shop_rating
        await update_shop_rating(str(shop["_id"]), db)
    
    print(f"✅ Recalculated ratings for {len(shops)} shops")
    
    client.close()
    print("🎉 All done!")

if __name__ == "__main__":
    asyncio.run(migrate_reviews())
