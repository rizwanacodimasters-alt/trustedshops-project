from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from models import StatisticsResponse

router = APIRouter(prefix="/statistics", tags=["Statistics"])

def get_db():
    from server import db
    return db

@router.get("", response_model=StatisticsResponse)
async def get_statistics(db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get platform statistics."""
    # Count users (shoppers)
    user_count = await db.users.count_documents({"role": "shopper"})
    
    # Count shops
    shop_count = await db.shops.count_documents({})
    
    # Count reviews as proxy for transactions
    review_count = await db.reviews.count_documents({})
    
    # Format numbers
    def format_number(num):
        if num >= 1000000:
            return f"{num / 1000000:.1f} Million".replace(".0", "")
        elif num >= 1000:
            return f"{num / 1000:.1f}K".replace(".0", "")
        return str(num)
    
    return StatisticsResponse(
        shoppers=format_number(user_count),
        shops=format_number(shop_count),
        dailyTransactions=format_number(review_count)
    )
