#!/usr/bin/env python3
"""
Create demo data: 5 users, 3 shops, reviews
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import bcrypt
from datetime import datetime, timedelta
import random
import os
from dotenv import load_dotenv

# Demo data
DEMO_USERS = [
    {
        "full_name": "Anna Schmidt",
        "email": "anna.schmidt@demo.de",
        "password": "Demo2024!",
        "role": "shopper"
    },
    {
        "full_name": "Max Müller",
        "email": "max.mueller@demo.de",
        "password": "Demo2024!",
        "role": "shopper"
    },
    {
        "full_name": "Lisa Weber",
        "email": "lisa.weber@demo.de",
        "password": "Demo2024!",
        "role": "shopper"
    },
    {
        "full_name": "Tom Fischer",
        "email": "tom.fischer@demo.de",
        "password": "Demo2024!",
        "role": "shopper"
    },
    {
        "full_name": "Sarah Klein",
        "email": "sarah.klein@demo.de",
        "password": "Demo2024!",
        "role": "shopper"
    }
]

DEMO_SHOPS = [
    {
        "name": "TechWorld Electronics",
        "description": "Premium Elektronik und Gadgets für Tech-Enthusiasten. Neueste Smartphones, Laptops, Smart Home Geräte und Zubehör.",
        "category": "Electronics",
        "website": "https://techworld-electronics.de",
        "email": "info@techworld-electronics.de",
        "phone": "+49 30 12345678",
        "address": "Berliner Str. 123, 10115 Berlin",
        "industry": "electronics"
    },
    {
        "name": "StyleBoutique Fashion",
        "description": "Moderne Mode für jeden Anlass. Hochwertige Kleidung, Schuhe und Accessoires für Damen und Herren.",
        "category": "Fashion",
        "website": "https://styleboutique-fashion.de",
        "email": "kontakt@styleboutique-fashion.de",
        "phone": "+49 89 98765432",
        "address": "Münchner Allee 45, 80331 München",
        "industry": "fashion"
    },
    {
        "name": "BioMarkt Organic",
        "description": "Ihr Bio-Supermarkt für gesunde Ernährung. Frisches Obst, Gemüse, Bio-Fleisch und vegane Produkte.",
        "category": "Food & Beverages",
        "website": "https://biomarkt-organic.de",
        "email": "service@biomarkt-organic.de",
        "phone": "+49 40 55566677",
        "address": "Hamburger Weg 78, 20095 Hamburg",
        "industry": "food"
    }
]

DEMO_REVIEWS = [
    # TechWorld Electronics Reviews
    {
        "shop_index": 0,
        "user_index": 0,
        "rating": 5,
        "comment": "Absolut fantastischer Shop! Habe ein neues Smartphone gekauft und der Service war hervorragend. Schnelle Lieferung, gut verpackt und das Gerät funktioniert einwandfrei. Sehr kompetente Beratung per E-Mail. Definitiv 5 Sterne!"
    },
    {
        "shop_index": 0,
        "user_index": 1,
        "rating": 4,
        "comment": "Guter Shop mit großer Auswahl an Elektronik. Preise sind fair und die Qualität stimmt. Ein Stern Abzug, weil die Lieferung etwas länger gedauert hat als angegeben, aber ansonsten top!"
    },
    {
        "shop_index": 0,
        "user_index": 2,
        "rating": 2,
        "comment": "Leider nicht zufrieden mit meiner Bestellung. Das Laptop hatte beim Auspacken bereits Kratzer und der Kundenservice hat sehr langsam reagiert. Musste mehrfach nachhaken."
    },
    {
        "shop_index": 0,
        "user_index": 3,
        "rating": 5,
        "comment": "Beste Erfahrung! Habe Smart Home Geräte bestellt und alles lief perfekt. Tolle Beratung, schneller Versand und die Geräte funktionieren super. Kann ich nur empfehlen!"
    },
    
    # StyleBoutique Fashion Reviews
    {
        "shop_index": 1,
        "user_index": 0,
        "rating": 5,
        "comment": "Wunderschöne Kleidung und exzellente Qualität! Habe ein Kleid für eine Hochzeit gekauft und es passt perfekt. Die Stoffe fühlen sich hochwertig an und die Verarbeitung ist top. Gerne wieder!"
    },
    {
        "shop_index": 1,
        "user_index": 1,
        "rating": 3,
        "comment": "Durchschnittlicher Fashion-Shop. Die Auswahl ist okay, aber nichts Besonderes. Preise sind etwas hoch für die Qualität. Lieferung war pünktlich, aber die Verpackung könnte besser sein."
    },
    {
        "shop_index": 1,
        "user_index": 3,
        "rating": 4,
        "comment": "Schöne Mode und gute Qualität. Habe mehrere Teile bestellt und die meisten passen gut. Ein Artikel musste zurückgeschickt werden, aber der Rückversand war unkompliziert. Insgesamt empfehlenswert!"
    },
    {
        "shop_index": 1,
        "user_index": 4,
        "rating": 1,
        "comment": "Sehr enttäuscht von diesem Shop. Die bestellten Schuhe waren in falscher Größe und die Farbe entsprach nicht dem Bild. Retourenprozess war kompliziert und der Support unfreundlich. Nicht empfehlenswert."
    },
    
    # BioMarkt Organic Reviews
    {
        "shop_index": 2,
        "user_index": 1,
        "rating": 5,
        "comment": "Hervorragender Bio-Markt! Frische Produkte, große Auswahl und alles in bester Bio-Qualität. Die Lieferung war pünktlich und die Produkte waren gut gekühlt verpackt. Sehr zufrieden!"
    },
    {
        "shop_index": 2,
        "user_index": 2,
        "rating": 4,
        "comment": "Guter Bio-Shop mit fairen Preisen. Das Obst und Gemüse ist immer frisch und schmeckt hervorragend. Manchmal sind einige Artikel ausverkauft, aber das ist bei Bio-Produkten normal. Empfehlenswert!"
    },
    {
        "shop_index": 2,
        "user_index": 3,
        "rating": 5,
        "comment": "Bester Bio-Lieferservice in der Stadt! Alles frisch, regional und in Top-Qualität. Die veganen Produkte sind besonders gut. Kundenservice ist freundlich und hilfsbereit. 5 Sterne!"
    },
    {
        "shop_index": 2,
        "user_index": 4,
        "rating": 2,
        "comment": "Hatte leider zwei schlechte Erfahrungen. Beim ersten Mal war das Gemüse nicht mehr ganz frisch und beim zweiten Mal fehlten Artikel in der Lieferung. Auf meine Reklamation wurde erst nach mehreren Tagen geantwortet."
    },
    {
        "shop_index": 2,
        "user_index": 0,
        "rating": 4,
        "comment": "Solide Bio-Qualität zu angemessenen Preisen. Die Auswahl ist gut und die meisten Produkte sind regional. Lieferung ist zuverlässig. Ein kleiner Kritikpunkt: Die Verpackung könnte umweltfreundlicher sein."
    }
]

async def create_demo_data():
    """Create demo users, shops, and reviews."""
    
    # Load environment
    from pathlib import Path
    env_path = Path(__file__).parent / 'backend' / '.env'
    load_dotenv(env_path)
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'test_database')
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("=" * 70)
    print("🎬 CREATING DEMO DATA")
    print("=" * 70)
    
    # Step 1: Create Users
    print("\n👤 Step 1: Creating 5 Demo Users...")
    created_users = []
    
    for user_data in DEMO_USERS:
        # Check if user exists
        existing = await db.users.find_one({"email": user_data["email"]})
        if existing:
            print(f"   ⚠️  User already exists: {user_data['email']}")
            created_users.append(existing)
            continue
        
        # Hash password
        hashed_password = bcrypt.hashpw(user_data["password"].encode('utf-8'), bcrypt.gensalt())
        
        # Create user
        user_doc = {
            "full_name": user_data["full_name"],
            "email": user_data["email"],
            "password": hashed_password.decode('utf-8'),
            "role": user_data["role"],
            "email_verified": True,  # Pre-verified for demo
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        }
        
        result = await db.users.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        created_users.append(user_doc)
        
        print(f"   ✅ Created: {user_data['full_name']} ({user_data['email']})")
    
    # Step 2: Create Shops
    print("\n🏪 Step 2: Creating 3 Demo Shops...")
    created_shops = []
    
    # Use first user as shop owner for all shops
    shop_owner = created_users[0]
    
    for shop_data in DEMO_SHOPS:
        # Check if shop exists
        existing = await db.shops.find_one({"name": shop_data["name"]})
        if existing:
            print(f"   ⚠️  Shop already exists: {shop_data['name']}")
            created_shops.append(existing)
            continue
        
        # Create shop
        shop_doc = {
            "name": shop_data["name"],
            "description": shop_data["description"],
            "category": shop_data["category"],
            "website": shop_data["website"],
            "email": shop_data["email"],
            "phone": shop_data["phone"],
            "address": shop_data["address"],
            "industry": shop_data["industry"],
            "owner_id": str(shop_owner["_id"]),
            "rating": 0.0,
            "review_count": 0,
            "is_verified": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.shops.insert_one(shop_doc)
        shop_doc["_id"] = result.inserted_id
        created_shops.append(shop_doc)
        
        print(f"   ✅ Created: {shop_data['name']} ({shop_data['category']})")
    
    # Step 3: Create Reviews
    print("\n⭐ Step 3: Creating Reviews...")
    
    for review_data in DEMO_REVIEWS:
        shop = created_shops[review_data["shop_index"]]
        user = created_users[review_data["user_index"]]
        
        # Check if review exists
        existing = await db.reviews.find_one({
            "shop_id": str(shop["_id"]),
            "user_id": str(user["_id"])
        })
        
        if existing:
            print(f"   ⚠️  Review already exists: {user['full_name']} → {shop['name']}")
            continue
        
        # Determine status (low-star reviews are pending)
        status = "pending" if review_data["rating"] <= 2 else "published"
        
        # Create review
        review_doc = {
            "shop_id": str(shop["_id"]),
            "user_id": str(user["_id"]),
            "rating": review_data["rating"],
            "comment": review_data["comment"],
            "review_type": "verified",
            "status": status,
            "is_verified_purchase": True,
            "verification_date": datetime.utcnow(),
            "content_flags": [],
            "is_flagged": False,
            "proof_photos": [],
            "proof_chat_history": None,
            "proof_order_number": None,
            "admin_notes": None,
            "reviewed_by_admin": None,
            "review_date": None,
            "email": None,
            "verification_token": None,
            "email_verified": True,
            "flag_reason": None,
            "order_id": None,
            "order_reference": None,
            "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            "updated_at": datetime.utcnow()
        }
        
        await db.reviews.insert_one(review_doc)
        
        status_emoji = "⏳" if status == "pending" else "✅"
        print(f"   {status_emoji} {user['full_name']} → {shop['name']}: {review_data['rating']}⭐ ({status})")
    
    # Step 4: Update shop ratings
    print("\n📊 Step 4: Calculating Shop Ratings...")
    
    # Calculate rating function inline
    async def update_shop_rating(shop_id, database):
        from datetime import timedelta
        
        twelve_months_ago = datetime.utcnow() - timedelta(days=365)
        
        pipeline = [
            {
                "$match": {
                    "shop_id": shop_id,
                    "review_type": "verified",
                    "status": {"$in": ["published", "approved"]},
                    "created_at": {"$gte": twelve_months_ago}
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
        
        result = await database.reviews.aggregate(pipeline).to_list(1)
        
        if result:
            avg_rating = round(result[0]["avg_rating"], 2)
            count = result[0]["count"]
        else:
            avg_rating = 0.0
            count = 0
        
        # Calculate grade
        if avg_rating >= 4.50:
            grade, label = 'A', 'Exzellent'
        elif avg_rating >= 3.50:
            grade, label = 'B', 'Gut'
        elif avg_rating >= 2.50:
            grade, label = 'C', 'Befriedigend'
        elif avg_rating >= 1.50:
            grade, label = 'D', 'Ausreichend'
        else:
            grade, label = 'F', 'Mangelhaft'
        
        await database.shops.update_one(
            {"_id": shop_id},
            {
                "$set": {
                    "rating": avg_rating,
                    "review_count": count,
                    "trust_grade": grade,
                    "trust_label": label
                }
            }
        )
    
    for shop in created_shops:
        await update_shop_rating(shop["_id"], db)
        
        # Get updated shop
        updated_shop = await db.shops.find_one({"_id": shop["_id"]})
        grade = updated_shop.get("trust_grade", "N/A")
        label = updated_shop.get("trust_label", "N/A")
        rating = updated_shop.get("rating", 0.0)
        count = updated_shop.get("review_count", 0)
        
        print(f"   ✅ {shop['name']}: {rating:.2f}⭐ (Grade {grade}: {label}) - {count} reviews")
    
    # Print summary
    print("\n" + "=" * 70)
    print("🎉 DEMO DATA CREATED SUCCESSFULLY!")
    print("=" * 70)
    
    print("\n📋 USER CREDENTIALS:")
    print("-" * 70)
    for user_data in DEMO_USERS:
        print(f"   Name: {user_data['full_name']}")
        print(f"   Email: {user_data['email']}")
        print(f"   Password: {user_data['password']}")
        print(f"   Role: {user_data['role']}")
        print()
    
    print("\n🏪 CREATED SHOPS:")
    print("-" * 70)
    for i, shop in enumerate(created_shops):
        updated_shop = await db.shops.find_one({"_id": shop["_id"]})
        print(f"{i+1}. {shop['name']}")
        print(f"   Category: {shop['category']}")
        print(f"   Rating: {updated_shop.get('rating', 0.0):.2f}⭐")
        print(f"   Grade: {updated_shop.get('trust_grade', 'N/A')} ({updated_shop.get('trust_label', 'N/A')})")
        print(f"   Reviews: {updated_shop.get('review_count', 0)}")
        print()
    
    print("\n⚠️  PENDING REVIEWS (require admin approval):")
    print("-" * 70)
    pending = await db.reviews.find({"status": "pending"}).to_list(None)
    if pending:
        for review in pending:
            user = await db.users.find_one({"_id": review["user_id"]})
            shop = await db.shops.find_one({"_id": review["shop_id"]})
            if user and shop:
                print(f"   • {user.get('full_name')} → {shop.get('name')}: {review['rating']}⭐")
    else:
        print("   None")
    
    print("\n" + "=" * 70)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_demo_data())
