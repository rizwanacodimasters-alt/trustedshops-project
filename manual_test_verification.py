#!/usr/bin/env python3
"""
Manual test to demonstrate email verification workflow
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import bcrypt
from datetime import datetime

async def create_test_user_and_get_code():
    """Create a test user and get verification code"""
    
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['test_database']
    
    # Email address
    test_email = "mdbvwjr849@tempmail.at"
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": test_email})
    
    if existing_user:
        print(f"✅ Benutzer existiert bereits: {test_email}")
        print(f"   - Name: {existing_user.get('full_name')}")
        print(f"   - Rolle: {existing_user.get('role')}")
        print(f"   - Verifiziert: {existing_user.get('email_verified', False)}")
    else:
        # Create new user
        hashed_password = bcrypt.hashpw("TestPassword123!".encode('utf-8'), bcrypt.gensalt())
        
        user_data = {
            "full_name": "Test User Tempmail",
            "email": test_email,
            "password": hashed_password.decode('utf-8'),
            "role": "shopper",
            "email_verified": False,
            "created_at": datetime.utcnow()
        }
        
        result = await db.users.insert_one(user_data)
        print(f"✅ Neuer Benutzer erstellt: {test_email}")
        print(f"   - User ID: {result.inserted_id}")
        print(f"   - Passwort: TestPassword123!")
    
    # Check if verification code exists
    verification = await db.email_verifications.find_one({"email": test_email})
    
    if verification:
        code = verification.get('code')
        expires_at = verification.get('expires_at')
        attempts = verification.get('attempts', 0)
        
        print(f"\n🔐 VERIFIZIERUNGSCODE:")
        print(f"   Code: {code}")
        print(f"   Läuft ab: {expires_at}")
        print(f"   Versuche verwendet: {attempts}/5")
        
        # Check if expired
        if datetime.utcnow() > expires_at:
            print(f"   ⚠️ Code ist abgelaufen!")
        else:
            print(f"   ✅ Code ist noch gültig")
    else:
        print(f"\n⚠️ Kein Verifizierungscode gefunden")
        print(f"   Bitte fordern Sie einen Code über die Web-App an:")
        print(f"   1. Gehen Sie zu /signup")
        print(f"   2. Registrieren Sie sich mit {test_email}")
        print(f"   3. Sie werden zu /email-verification weitergeleitet")
        print(f"   4. Der Code wird automatisch generiert und gesendet")
    
    client.close()
    
    print(f"\n" + "="*60)
    print(f"ANLEITUNG:")
    print(f"="*60)
    print(f"1. Öffnen Sie: https://trust-ratings-app.preview.emergentagent.com/signup")
    print(f"2. Registrieren Sie sich mit:")
    print(f"   - Name: Test User")
    print(f"   - Email: {test_email}")
    print(f"   - Passwort: TestPassword123!")
    print(f"3. Nach der Registrierung werden Sie zur E-Mail-Verifizierung weitergeleitet")
    print(f"4. Der Code wird:")
    print(f"   a) Per E-Mail an {test_email} gesendet")
    print(f"   b) Im Frontend als Toast-Nachricht angezeigt (DEV_MODE)")
    print(f"5. Geben Sie den Code ein, um Ihre E-Mail zu verifizieren")
    print(f"="*60)

if __name__ == "__main__":
    asyncio.run(create_test_user_and_get_code())
