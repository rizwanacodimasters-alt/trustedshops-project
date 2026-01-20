from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from urllib.parse import urlparse
import re

router = APIRouter(prefix="/fake-check", tags=["Fake Shop Checker"])

def get_db():
    from server import db
    return db

class URLCheckRequest(BaseModel):
    url: str

class ShopCheckResult(BaseModel):
    is_registered: bool
    is_verified: bool
    shop_name: Optional[str] = None
    shop_id: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    category: Optional[str] = None
    trust_score: int  # 0-100
    warnings: List[str] = []
    recommendations: List[str] = []

def normalize_url(url: str) -> str:
    """Normalize URL for comparison."""
    url = url.strip().lower()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    parsed = urlparse(url)
    # Extract domain without www
    domain = parsed.netloc.replace('www.', '')
    return domain

def calculate_trust_score(shop: dict, is_registered: bool) -> tuple:
    """Calculate trust score and generate warnings/recommendations."""
    score = 0
    warnings = []
    recommendations = []
    
    if not is_registered:
        score = 20
        warnings.append("⚠️ Shop ist nicht in unserer Datenbank registriert")
        warnings.append("⚠️ Keine verifizierten Bewertungen vorhanden")
        recommendations.append("🔍 Prüfen Sie Online-Bewertungen auf anderen Plattformen")
        recommendations.append("📧 Achten Sie auf ein vollständiges Impressum mit Kontaktdaten")
        recommendations.append("🔒 Prüfen Sie ob die Website eine sichere HTTPS-Verbindung nutzt")
        recommendations.append("💳 Nutzen Sie sichere Zahlungsmethoden (PayPal, Käuferschutz)")
        return score, warnings, recommendations
    
    # Shop is registered
    score = 50
    
    if shop.get('is_verified'):
        score += 30
        recommendations.append("✅ Shop ist verifiziert")
    else:
        score += 10
        warnings.append("⚠️ Shop ist noch nicht verifiziert")
        recommendations.append("🔍 Warten Sie auf die Verifizierung oder prüfen Sie zusätzlich")
    
    # Rating impact
    rating = shop.get('rating', 0)
    if rating >= 4.5:
        score += 20
        recommendations.append(f"⭐ Sehr gute Bewertung: {rating:.1f}/5.0")
    elif rating >= 3.5:
        score += 10
        recommendations.append(f"⭐ Gute Bewertung: {rating:.1f}/5.0")
    elif rating >= 2.5:
        score += 5
        warnings.append(f"⚠️ Mittelmäßige Bewertung: {rating:.1f}/5.0")
    else:
        warnings.append(f"❌ Schlechte Bewertung: {rating:.1f}/5.0")
    
    # Review count
    review_count = shop.get('review_count', 0)
    if review_count > 50:
        recommendations.append(f"👥 Viele Bewertungen: {review_count} Kundenmeinungen")
    elif review_count > 10:
        recommendations.append(f"👥 Ausreichend Bewertungen: {review_count} Kundenmeinungen")
    elif review_count > 0:
        warnings.append(f"⚠️ Wenige Bewertungen: {review_count} Kundenmeinungen")
    else:
        warnings.append("⚠️ Noch keine Bewertungen vorhanden")
    
    return min(score, 100), warnings, recommendations

@router.post("/check", response_model=ShopCheckResult)
async def check_shop_url(
    request: URLCheckRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Check if a shop URL is registered and trustworthy."""
    
    try:
        domain = normalize_url(request.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Ungültige URL")
    
    # Search for shop by website domain
    shops = await db.shops.find().to_list(None)
    
    matched_shop = None
    for shop in shops:
        shop_domain = normalize_url(shop.get('website', ''))
        if domain in shop_domain or shop_domain in domain:
            matched_shop = shop
            break
    
    if matched_shop:
        trust_score, warnings, recommendations = calculate_trust_score(matched_shop, True)
        
        return ShopCheckResult(
            is_registered=True,
            is_verified=matched_shop.get('is_verified', False),
            shop_name=matched_shop.get('name'),
            shop_id=str(matched_shop['_id']),
            rating=matched_shop.get('rating'),
            review_count=matched_shop.get('review_count', 0),
            category=matched_shop.get('category'),
            trust_score=trust_score,
            warnings=warnings,
            recommendations=recommendations
        )
    else:
        trust_score, warnings, recommendations = calculate_trust_score({}, False)
        
        return ShopCheckResult(
            is_registered=False,
            is_verified=False,
            trust_score=trust_score,
            warnings=warnings,
            recommendations=recommendations
        )

@router.get("/statistics")
async def get_fake_shop_statistics(
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get statistics about registered shops."""
    
    total_shops = await db.shops.count_documents({})
    verified_shops = await db.shops.count_documents({"is_verified": True})
    total_reviews = await db.reviews.count_documents({})
    
    # Calculate average rating
    shops = await db.shops.find().to_list(None)
    avg_rating = sum(s.get('rating', 0) for s in shops) / len(shops) if shops else 0
    
    return {
        "total_shops": total_shops,
        "verified_shops": verified_shops,
        "total_reviews": total_reviews,
        "average_rating": round(avg_rating, 2)
    }
