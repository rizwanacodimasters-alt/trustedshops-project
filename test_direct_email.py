#!/usr/bin/env python3
"""
Direct SMTP test to diagnose email delivery issues
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import sys

# SMTP Configuration
SMTP_HOST = "codimasters.com"
SMTP_PORT = 465
SMTP_USER = "trust@codimasters.com"
SMTP_PASSWORD = "v^i8t276C"
SMTP_FROM = "trust@codimasters.com"
SMTP_FROM_NAME = "TrustedShops Team"

def send_test_email(to_email):
    """Send a test email to diagnose delivery"""
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM}>"
        msg['To'] = to_email
        msg['Subject'] = "Test E-Mail von TrustedShops"
        
        # HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>Test E-Mail</h2>
            <p>Dies ist eine Test-E-Mail, um die Zustellbarkeit zu prüfen.</p>
            <p>Wenn Sie diese E-Mail erhalten, funktioniert der SMTP-Server korrekt.</p>
            <p><strong>Empfänger:</strong> {to_email}</p>
            <p><strong>Zeitstempel:</strong> {import_datetime()}</p>
        </body>
        </html>
        """
        
        text_content = f"""
        Test E-Mail
        
        Dies ist eine Test-E-Mail, um die Zustellbarkeit zu prüfen.
        
        Wenn Sie diese E-Mail erhalten, funktioniert der SMTP-Server korrekt.
        
        Empfänger: {to_email}
        """
        
        # Attach parts
        text_part = MIMEText(text_content, 'plain', 'utf-8')
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(text_part)
        msg.attach(html_part)
        
        print(f"🔄 Verbinde mit SMTP Server: {SMTP_HOST}:{SMTP_PORT}")
        
        # Connect and send
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            print(f"✅ Verbindung hergestellt")
            
            print(f"🔐 Authentifizierung mit: {SMTP_USER}")
            server.login(SMTP_USER, SMTP_PASSWORD)
            print(f"✅ Authentifizierung erfolgreich")
            
            print(f"📧 Sende E-Mail an: {to_email}")
            result = server.send_message(msg)
            print(f"✅ E-Mail erfolgreich gesendet!")
            
            if result:
                print(f"⚠️ Einige Empfänger wurden abgelehnt: {result}")
            else:
                print(f"✅ Alle Empfänger akzeptiert")
                
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ SMTP Authentifizierungsfehler: {e}")
        return False
    except smtplib.SMTPRecipientsRefused as e:
        print(f"❌ Empfänger abgelehnt: {e}")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP Fehler: {e}")
        return False
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False

def import_datetime():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    test_email = "mdbvwjr849@tempmail.at"
    
    print("=" * 60)
    print("SMTP E-Mail Test")
    print("=" * 60)
    print(f"Von: {SMTP_FROM}")
    print(f"An: {test_email}")
    print(f"Server: {SMTP_HOST}:{SMTP_PORT}")
    print("=" * 60)
    print()
    
    success = send_test_email(test_email)
    
    print()
    print("=" * 60)
    if success:
        print("✅ TEST ERFOLGREICH")
        print("Bitte prüfen Sie Ihr E-Mail-Postfach (auch Spam-Ordner)")
    else:
        print("❌ TEST FEHLGESCHLAGEN")
        print("Siehe Fehlerdetails oben")
    print("=" * 60)
