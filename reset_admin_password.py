#!/usr/bin/env python3
"""
Reset admin password
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import bcrypt
from pathlib import Path
from dotenv import load_dotenv
import os

async def reset_admin():
    """Reset admin password."""
    
    # Load environment
    env_path = Path(__file__).parent / 'backend' / '.env'
    load_dotenv(env_path)
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'test_database')
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("🔑 Resetting Admin Password...")
    
    # Find admin
    admin = await db.users.find_one({"role": "admin"})
    
    if not admin:
        print("❌ No admin found! Creating new admin...")
        
        # Create new admin
        hashed_password = bcrypt.hashpw("Admin2024!".encode('utf-8'), bcrypt.gensalt())
        
        admin_doc = {
            "full_name": "Administrator",
            "email": "admin@trustedshops.de",
            "password": hashed_password.decode('utf-8'),
            "role": "admin",
            "email_verified": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        }
        
        await db.users.insert_one(admin_doc)
        print(f"✅ Admin created!")
        print(f"   Email: admin@trustedshops.de")
        print(f"   Password: Admin2024!")
    else:
        # Update password
        new_password = "Admin2024!"
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        await db.users.update_one(
            {"_id": admin["_id"]},
            {"$set": {"password": hashed_password.decode('utf-8'), "email_verified": True}}
        )
        
        print(f"✅ Admin password reset successfully!")
        print()
        print("="*60)
        print("🔐 ADMIN ZUGANGSDATEN:")
        print("="*60)
        print(f"   Name: {admin.get('full_name', 'Admin User')}")
        print(f"   Email: {admin['email']}")
        print(f"   Passwort: {new_password}")
        print(f"   Rolle: admin")
        print("="*60)
    
    client.close()

if __name__ == "__main__":
    from datetime import datetime
    asyncio.run(reset_admin())
