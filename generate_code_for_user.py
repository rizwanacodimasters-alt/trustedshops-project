#!/usr/bin/env python3
"""
Generate verification code for existing user
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import random
import string

async def generate_code_for_user(email):
    """Generate and store verification code for user"""
    
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['test_database']
    
    # Check if user exists
    user = await db.users.find_one({"email": email})
    
    if not user:
        print(f"❌ Benutzer nicht gefunden: {email}")
        client.close()
        return
    
    print(f"✅ Benutzer gefunden: {email}")
    print(f"   - Name: {user.get('full_name')}")
    print(f"   - Rolle: {user.get('role')}")
    print(f"   - Verifiziert: {user.get('email_verified', False)}")
    
    # Generate 5-digit code
    code = ''.join(random.choices(string.digits, k=5))
    expires_at = datetime.utcnow() + timedelta(minutes=15)
    
    # Store in database
    await db.email_verifications.update_one(
        {"email": email},
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
    
    print(f"\n🔐 NEUER VERIFIZIERUNGSCODE GENERIERT:")
    print(f"   Code: {code}")
    print(f"   Gültig bis: {expires_at.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"   Versuche: 0/5")
    
    print(f"\n" + "="*60)
    print(f"SO VERIFIZIEREN SIE IHRE E-MAIL:")
    print(f"="*60)
    print(f"1. Öffnen Sie: https://trust-ratings-app.preview.emergentagent.com/signin")
    print(f"2. Melden Sie sich an mit:")
    print(f"   - Email: {email}")
    print(f"   - Passwort: TestPassword123!")
    print(f"3. Oder gehen Sie direkt zu:")
    print(f"   https://trust-ratings-app.preview.emergentagent.com/email-verification")
    print(f"4. Geben Sie den Code ein: {code}")
    print(f"="*60)
    
    # Send email via SMTP
    print(f"\n📧 Sende E-Mail an {email}...")
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        SMTP_HOST = "codimasters.com"
        SMTP_PORT = 465
        SMTP_USER = "trust@codimasters.com"
        SMTP_PASSWORD = "v^i8t276C"
        SMTP_FROM = "trust@codimasters.com"
        
        msg = MIMEMultipart('alternative')
        msg['From'] = f"TrustedShops Team <{SMTP_FROM}>"
        msg['To'] = email
        msg['Subject'] = "Ihr Verifizierungscode"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>🔐 E-Mail Verifizierung</h2>
            <p>Ihr Verifizierungscode lautet:</p>
            <div style="background: #f0f0f0; padding: 20px; text-align: center; font-size: 32px; font-weight: bold; letter-spacing: 10px;">
                {code}
            </div>
            <p><strong>Dieser Code ist 15 Minuten gültig.</strong></p>
            <p>Mit freundlichen Grüßen,<br>Ihr TrustedShops Team</p>
        </body>
        </html>
        """
        
        text_content = f"""
        E-Mail Verifizierung
        
        Ihr Verifizierungscode lautet: {code}
        
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
        
        print(f"✅ E-Mail erfolgreich gesendet!")
        print(f"   Bitte prüfen Sie Ihr Postfach (auch Spam-Ordner)")
        
    except Exception as e:
        print(f"⚠️ E-Mail-Versand fehlgeschlagen: {e}")
        print(f"   Aber der Code ist in der Datenbank gespeichert!")
    
    client.close()

if __name__ == "__main__":
    email = "mdbvwjr849@tempmail.at"
    asyncio.run(generate_code_for_user(email))
