#!/usr/bin/env python3
"""
Script to create test users for TrustedShops Clone
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from auth import get_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']

async def create_test_users():
    """Create test users for development."""
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    test_users = [
        {
            "full_name": "Admin User",
            "email": "admin@trustedshops.com",
            "password": get_password_hash("admin123"),
            "role": "admin",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True,
            "two_factor_enabled": False
        },
        {
            "full_name": "Shop Owner",
            "email": "owner@shop.com",
            "password": get_password_hash("owner123"),
            "role": "shop_owner",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True,
            "two_factor_enabled": False
        },
        {
            "full_name": "Test Customer",
            "email": "customer@test.com",
            "password": get_password_hash("customer123"),
            "role": "shopper",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True,
            "two_factor_enabled": False
        }
    ]
    
    print("Creating test users...")
    
    for user in test_users:
        # Check if user exists
        existing = await db.users.find_one({"email": user["email"]})
        
        if existing:
            print(f"✓ User {user['email']} already exists")
        else:
            result = await db.users.insert_one(user)
            print(f"✓ Created user: {user['email']} (role: {user['role']})")
    
    print("\n" + "="*60)
    print("TEST USER CREDENTIALS")
    print("="*60)
    print("\n1. ADMIN USER:")
    print("   Email:    admin@trustedshops.com")
    print("   Password: admin123")
    print("   Role:     admin")
    print("\n2. SHOP OWNER:")
    print("   Email:    owner@shop.com")
    print("   Password: owner123")
    print("   Role:     shop_owner")
    print("\n3. CUSTOMER:")
    print("   Email:    customer@test.com")
    print("   Password: customer123")
    print("   Role:     shopper")
    print("\n" + "="*60)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_test_users())
