#!/usr/bin/env python3
"""
Create Demo Users and Shops
Creates 3 users and 5 shops with realistic demo content
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from passlib.context import CryptContext
import uuid

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MongoDB connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")

async def create_demo_data():
    """Create demo users and shops"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🚀 Creating Demo Users and Shops...")
    print("=" * 60)
    
    # Demo Users
    demo_users = [
        {
            "id": str(uuid.uuid4()),
            "full_name": "Max Mustermann",
            "email": "max@beispiel.de",
            "password": "max123456",
            "role": "shop_owner"
        },
        {
            "id": str(uuid.uuid4()),
            "full_name": "Lisa Schmidt",
            "email": "lisa@beispiel.de",
            "password": "lisa123456",
            "role": "shop_owner"
        },
        {
            "id": str(uuid.uuid4()),
            "full_name": "Thomas Weber",
            "email": "thomas@beispiel.de",
            "password": "thomas123456",
            "role": "shopper"
        }
    ]
    
    created_users = []
    print("\n👤 Creating Users...")
    print("-" * 60)
    
    for user_data in demo_users:
        # Check if user already exists
        existing = await db.users.find_one({"email": user_data["email"]})
        if existing:
            print(f"⚠️  User {user_data['email']} already exists, skipping...")
            created_users.append({
                "id": str(existing["_id"]),
                "email": user_data["email"],
                "role": existing["role"]
            })
            continue
        
        # Hash password
        hashed_password = pwd_context.hash(user_data["password"])
        
        # Create user document
        user_doc = {
            "_id": user_data["id"],
            "full_name": user_data["full_name"],
            "email": user_data["email"],
            "password": hashed_password,  # Use 'password' field name
            "role": user_data["role"],
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.users.insert_one(user_doc)
        created_users.append({
            "id": user_data["id"],
            "email": user_data["email"],
            "role": user_data["role"]
        })
        
        print(f"✅ Created: {user_data['full_name']} ({user_data['email']})")
        print(f"   Role: {user_data['role']}")
        print(f"   Password: {user_data['password']}")
        print()
    
    # Get shop owners
    shop_owners = [u for u in created_users if u["role"] == "shop_owner"]
    
    # Demo Shops
    demo_shops = [
        {
            "name": "Modeboutique Eleganz",
            "website": "https://modeboutique-eleganz.de",
            "category": "Bekleidung",
            "description": "Hochwertige Mode für jeden Anlass. Von Business bis Casual - bei uns finden Sie das perfekte Outfit. Nachhaltige Materialien und faire Produktion.",
            "email": "info@modeboutique-eleganz.de",
            "phone": "+49 30 12345678",
            "address": "Kurfürstendamm 123, 10719 Berlin",
            "owner_id": shop_owners[0]["id"],
            "logo": "",
            "image": ""
        },
        {
            "name": "TechWorld Electronics",
            "website": "https://techworld-electronics.de",
            "category": "Computer, Unterhaltungselektronik & Zubehör",
            "description": "Ihr Experte für Computer, Smartphones und Unterhaltungselektronik. Neueste Technologie zu fairen Preisen mit kompetenter Beratung und schnellem Versand.",
            "email": "service@techworld.de",
            "phone": "+49 89 98765432",
            "address": "Leopoldstraße 45, 80802 München",
            "owner_id": shop_owners[0]["id"],
            "logo": "",
            "image": ""
        },
        {
            "name": "BioBauernhof Grünland",
            "website": "https://biobauernhof-gruenland.de",
            "category": "Lebensmittel",
            "description": "Frische Bio-Lebensmittel direkt vom Bauernhof. Regional, saisonal und 100% bio-zertifiziert. Obst, Gemüse, Milchprodukte und mehr in Premium-Qualität.",
            "email": "kontakt@gruenland-bio.de",
            "phone": "+49 761 55566677",
            "address": "Hauptstraße 89, 79098 Freiburg",
            "owner_id": shop_owners[1]["id"] if len(shop_owners) > 1 else shop_owners[0]["id"],
            "logo": "",
            "image": ""
        },
        {
            "name": "Heimwerker-Paradies",
            "website": "https://heimwerker-paradies.de",
            "category": "Baumarkt",
            "description": "Alles für Haus und Garten. Werkzeuge, Baumaterialien, Gartengeräte und mehr. Professionelle Beratung und günstige Preise für Heimwerker und Profis.",
            "email": "info@heimwerker-paradies.de",
            "phone": "+49 221 44455566",
            "address": "Industriestraße 12, 50823 Köln",
            "owner_id": shop_owners[1]["id"] if len(shop_owners) > 1 else shop_owners[0]["id"],
            "logo": "",
            "image": ""
        },
        {
            "name": "Schmuckstudio Brillant",
            "website": "https://schmuckstudio-brillant.de",
            "category": "Schmuck & Uhren",
            "description": "Exklusiver Schmuck und edle Uhren. Individuelle Anfertigung nach Ihren Wünschen. Gold, Silber, Diamanten - Handwerkskunst auf höchstem Niveau.",
            "email": "beratung@brillant-schmuck.de",
            "phone": "+49 40 77788899",
            "address": "Jungfernstieg 34, 20095 Hamburg",
            "owner_id": shop_owners[0]["id"],
            "logo": "",
            "image": ""
        }
    ]
    
    print("\n🏪 Creating Shops...")
    print("-" * 60)
    
    for shop_data in demo_shops:
        # Check if shop already exists
        existing = await db.shops.find_one({"name": shop_data["name"]})
        if existing:
            print(f"⚠️  Shop '{shop_data['name']}' already exists, skipping...")
            continue
        
        # Create shop document
        shop_doc = {
            "_id": str(uuid.uuid4()),
            "name": shop_data["name"],
            "website": shop_data["website"],
            "category": shop_data["category"],
            "description": shop_data["description"],
            "email": shop_data["email"],
            "phone": shop_data["phone"],
            "address": shop_data["address"],
            "owner_id": shop_data["owner_id"],
            "logo": shop_data["logo"],
            "image": shop_data["image"],
            "rating": 4.5 + (len(shop_data["name"]) % 5) * 0.1,  # Random rating between 4.5-5.0
            "review_count": (len(shop_data["name"]) % 20) + 5,  # Random review count 5-25
            "is_verified": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.shops.insert_one(shop_doc)
        
        print(f"✅ Created: {shop_data['name']}")
        print(f"   Category: {shop_data['category']}")
        print(f"   Website: {shop_data['website']}")
        print(f"   Owner: {shop_data['owner_id']}")
        print()
    
    # Print Summary
    print("\n" + "=" * 60)
    print("✅ Demo Data Created Successfully!")
    print("=" * 60)
    
    print("\n📋 LOGIN CREDENTIALS:")
    print("-" * 60)
    print("\n👤 SHOP OWNERS (können Shops verwalten):")
    print("   1. Max Mustermann")
    print("      Email:    max@beispiel.de")
    print("      Passwort: max123456")
    print()
    print("   2. Lisa Schmidt")
    print("      Email:    lisa@beispiel.de")
    print("      Passwort: lisa123456")
    print()
    print("🛍️  CUSTOMER (kann Bewertungen schreiben):")
    print("   3. Thomas Weber")
    print("      Email:    thomas@beispiel.de")
    print("      Passwort: thomas123456")
    print()
    print("-" * 60)
    print("\n🏪 CREATED SHOPS:")
    for i, shop in enumerate(demo_shops, 1):
        print(f"   {i}. {shop['name']} ({shop['category']})")
    print()
    print("=" * 60)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_demo_data())
