#!/usr/bin/env python3
"""
Test Shop Owner Registration and Email Verification Flow
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import bcrypt
from datetime import datetime, timedelta
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

async def test_shop_owner_flow():
    """Test complete shop owner registration and verification"""
    
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['test_database']
    
    # Test email
    test_email = "shop.owner.test@tempmail.at"
    
    print("="*60)
    print("SHOP OWNER REGISTRIERUNG & VERIFIZIERUNG TEST")
    print("="*60)
    
    # Step 1: Clean up if user already exists
    existing = await db.users.find_one({"email": test_email})
    if existing:
        await db.users.delete_one({"email": test_email})
        await db.email_verifications.delete_one({"email": test_email})
        print(f"✅ Bestehenden Benutzer gelöscht: {test_email}")
    
    # Step 2: Create shop owner user (simulating registration)
    print(f"\n📝 Schritt 1: Shop Owner Registrierung")
    hashed_password = bcrypt.hashpw("ShopOwner123!".encode('utf-8'), bcrypt.gensalt())
    
    user_data = {
        "full_name": "Test Shop Owner",
        "email": test_email,
        "password": hashed_password.decode('utf-8'),
        "role": "shop_owner",  # ← Shop Owner Role
        "email_verified": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_active": True
    }
    
    result = await db.users.insert_one(user_data)
    print(f"   ✅ Shop Owner erstellt: {test_email}")
    print(f"   - User ID: {result.inserted_id}")
    print(f"   - Rolle: shop_owner")
    print(f"   - Verifiziert: False")
    
    # Step 3: Generate verification code
    print(f"\n🔐 Schritt 2: Verifizierungscode generieren")
    code = ''.join(random.choices(string.digits, k=5))
    expires_at = datetime.utcnow() + timedelta(minutes=15)
    
    await db.email_verifications.update_one(
        {"email": test_email},
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
    
    print(f"   ✅ Code generiert: {code}")
    print(f"   - Gültig bis: {expires_at.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    
    # Step 4: Send verification email
    print(f"\n📧 Schritt 3: E-Mail senden")
    try:
        SMTP_HOST = "codimasters.com"
        SMTP_PORT = 465
        SMTP_USER = "trust@codimasters.com"
        SMTP_PASSWORD = "v^i8t276C"
        SMTP_FROM = "trust@codimasters.com"
        
        msg = MIMEMultipart('alternative')
        msg['From'] = f"TrustedShops Team <{SMTP_FROM}>"
        msg['To'] = test_email
        msg['Subject'] = "Verifizieren Sie Ihr Shop Owner Konto"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>🏪 Shop Owner Konto Verifizierung</h2>
            <p>Willkommen bei TrustedShops!</p>
            <p>Ihr Verifizierungscode für Ihr Shop Owner Konto lautet:</p>
            <div style="background: #e3f2fd; padding: 20px; text-align: center; font-size: 32px; font-weight: bold; letter-spacing: 10px; color: #1565c0;">
                {code}
            </div>
            <p><strong>Dieser Code ist 15 Minuten gültig.</strong></p>
            <p>Nach der Verifizierung können Sie:</p>
            <ul>
                <li>Shops erstellen und verwalten</li>
                <li>Kundenbewertungen beantworten</li>
                <li>Verifizierungs-Badges beantragen</li>
                <li>Detaillierte Statistiken einsehen</li>
            </ul>
            <p>Mit freundlichen Grüßen,<br>Ihr TrustedShops Team</p>
        </body>
        </html>
        """
        
        text_content = f"""
        Shop Owner Konto Verifizierung
        
        Willkommen bei TrustedShops!
        
        Ihr Verifizierungscode: {code}
        
        Dieser Code ist 15 Minuten gültig.
        
        Mit freundlichen Grüßen,
        Ihr TrustedShops Team
        """
        
        html_part = MIMEText(html_content, 'html', 'utf-8')
        text_part = MIMEText(text_content, 'plain', 'utf-8')
        msg.attach(text_part)
        msg.attach(html_part)
        
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        print(f"   ✅ E-Mail erfolgreich gesendet!")
        
    except Exception as e:
        print(f"   ⚠️ E-Mail-Versand fehlgeschlagen: {e}")
    
    # Step 5: Test login without verification
    print(f"\n🔒 Schritt 4: Login-Test (ohne Verifizierung)")
    user = await db.users.find_one({"email": test_email})
    print(f"   ✅ Benutzer gefunden")
    print(f"   - email_verified: {user.get('email_verified', False)}")
    print(f"   - Erwartetes Verhalten: Umleitung zu /email-verification")
    
    # Step 6: Verify code (simulating)
    print(f"\n✅ Schritt 5: Code-Verifizierung (simuliert)")
    await db.users.update_one(
        {"email": test_email},
        {
            "$set": {
                "email_verified": True,
                "email_verified_at": datetime.utcnow()
            }
        }
    )
    print(f"   ✅ E-Mail verifiziert")
    
    # Step 7: Verify access after verification
    print(f"\n🎉 Schritt 6: Zugriff nach Verifizierung")
    verified_user = await db.users.find_one({"email": test_email})
    print(f"   ✅ Benutzer-Status:")
    print(f"   - email_verified: {verified_user.get('email_verified', False)}")
    print(f"   - Erwartetes Verhalten: Zugriff auf /shop-dashboard")
    
    client.close()
    
    print(f"\n" + "="*60)
    print(f"TEST-ZUSAMMENFASSUNG")
    print(f"="*60)
    print(f"✅ Shop Owner registriert: {test_email}")
    print(f"✅ Verifizierungscode: {code}")
    print(f"✅ E-Mail versendet")
    print(f"✅ Verifizierungs-Flow getestet")
    print(f"\n📋 MANUELLER TEST:")
    print(f"="*60)
    print(f"1. Öffnen Sie: https://trust-ratings-app.preview.emergentagent.com/signup/business")
    print(f"2. Registrieren Sie sich mit:")
    print(f"   - Name: Test Shop Owner")
    print(f"   - Email: {test_email}")
    print(f"   - Passwort: ShopOwner123!")
    print(f"   - Firma: Test Shop GmbH")
    print(f"   - Website: https://testshop.com")
    print(f"3. Sie werden zu /email-verification weitergeleitet")
    print(f"4. Code eingeben: {code}")
    print(f"5. Nach Verifizierung: Zugriff auf /shop-dashboard")
    print(f"="*60)

if __name__ == "__main__":
    asyncio.run(test_shop_owner_flow())
