import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails via SMTP."""
    
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST')
        self.smtp_port = int(os.getenv('SMTP_PORT', 465))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.smtp_from = os.getenv('SMTP_FROM')
        self.smtp_from_name = os.getenv('SMTP_FROM_NAME', 'TrustedShops')
        
        # Validate configuration
        if not all([self.smtp_host, self.smtp_user, self.smtp_password, self.smtp_from]):
            logger.error("SMTP configuration is incomplete. Check environment variables.")
            raise ValueError("SMTP configuration is incomplete")
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send an email via SMTP.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text fallback (optional)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.smtp_from_name} <{self.smtp_from}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add text part (fallback)
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            # Add HTML part
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Connect to SMTP server (SSL on port 465)
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication failed: {e}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error occurred: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_verification_email(self, to_email: str, verification_code: str) -> bool:
        """Send email verification code.
        
        Args:
            to_email: User's email address
            verification_code: 5-digit verification code
            
        Returns:
            bool: True if email sent successfully
        """
        subject = "Verifizieren Sie Ihre E-Mail-Adresse"
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="de">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>E-Mail Verifizierung</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 40px auto;
                    background-color: #ffffff;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px 20px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                    font-weight: 600;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .verification-code {{
                    background-color: #f8f9fa;
                    border: 2px dashed #667eea;
                    border-radius: 8px;
                    padding: 20px;
                    text-align: center;
                    margin: 30px 0;
                }}
                .code {{
                    font-size: 36px;
                    font-weight: bold;
                    color: #667eea;
                    letter-spacing: 8px;
                    font-family: 'Courier New', monospace;
                }}
                .info {{
                    background-color: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .info p {{
                    margin: 5px 0;
                    font-size: 14px;
                    color: #856404;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                    color: #6c757d;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background-color: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                    font-weight: 600;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 E-Mail Verifizierung</h1>
                </div>
                <div class="content">
                    <p>Hallo,</p>
                    <p>Vielen Dank für Ihre Registrierung bei TrustedShops! Um Ihre E-Mail-Adresse zu verifizieren, verwenden Sie bitte den folgenden Code:</p>
                    
                    <div class="verification-code">
                        <p style="margin: 0 0 10px 0; font-size: 14px; color: #6c757d;">Ihr Verifizierungscode:</p>
                        <div class="code">{verification_code}</div>
                    </div>
                    
                    <div class="info">
                        <p><strong>⏱️ Wichtig:</strong></p>
                        <p>• Dieser Code ist 15 Minuten gültig</p>
                        <p>• Sie haben maximal 5 Versuche zur Eingabe</p>
                        <p>• Falls Sie diese E-Mail nicht angefordert haben, können Sie sie ignorieren</p>
                    </div>
                    
                    <p style="margin-top: 30px;">Geben Sie den Code auf der Verifizierungsseite ein, um Ihr Konto zu aktivieren.</p>
                    
                    <p style="margin-top: 30px; color: #6c757d; font-size: 14px;">
                        Mit freundlichen Grüßen,<br>
                        Ihr TrustedShops Team
                    </p>
                </div>
                <div class="footer">
                    <p>Dies ist eine automatisch generierte E-Mail. Bitte antworten Sie nicht auf diese Nachricht.</p>
                    <p>&copy; 2025 TrustedShops. Alle Rechte vorbehalten.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        E-Mail Verifizierung
        
        Hallo,
        
        Vielen Dank für Ihre Registrierung bei TrustedShops!
        
        Ihr Verifizierungscode: {verification_code}
        
        Wichtig:
        - Dieser Code ist 15 Minuten gültig
        - Sie haben maximal 5 Versuche zur Eingabe
        - Falls Sie diese E-Mail nicht angefordert haben, können Sie sie ignorieren
        
        Mit freundlichen Grüßen,
        Ihr TrustedShops Team
        
        ---
        Dies ist eine automatisch generierte E-Mail.
        © 2025 TrustedShops. Alle Rechte vorbehalten.
        """
        
        return self.send_email(to_email, subject, html_content, text_content)

# Lazy initialization
_email_service_instance = None

def get_email_service() -> EmailService:
    """Get or create the email service singleton instance."""
    global _email_service_instance
    if _email_service_instance is None:
        _email_service_instance = EmailService()
    return _email_service_instance
