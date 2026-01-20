from fastapi import APIRouter, HTTPException, status, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
import math
from constants import SHOP_CATEGORIES

router = APIRouter(prefix="/search", tags=["Search"])

def get_db():
    from server import db
    return db

@router.get("/shops")
async def search_shops(
    q: Optional[str] = None,
    category: Optional[str] = None,
    min_rating: Optional[float] = None,
    verified_only: bool = False,
    sort_by: str = "rating",  # rating, reviews, name
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Advanced shop search with filters."""
    # Build query
    query = {}
    
    if q:
        query["$or"] = [
            {"name": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
            {"website": {"$regex": q, "$options": "i"}}
        ]
    
    if category:
        query["category"] = category
    
    if min_rating:
        query["rating"] = {"$gte": min_rating}
    
    if verified_only:
        query["is_verified"] = True
    
    # Get total count
    total = await db.shops.count_documents(query)
    
    # Calculate pagination
    skip = (page - 1) * limit
    pages = math.ceil(total / limit) if total > 0 else 1
    
    # Determine sort order
    sort_field = "rating"
    sort_direction = -1
    
    if sort_by == "reviews":
        sort_field = "review_count"
    elif sort_by == "name":
        sort_field = "name"
        sort_direction = 1
    
    # Get shops
    cursor = db.shops.find(query).sort(sort_field, sort_direction).skip(skip).limit(limit)
    shops = await cursor.to_list(limit)
    
    # Format shops
    for shop in shops:
        shop["id"] = str(shop["_id"])
        del shop["_id"]
    
    return {
        "data": shops,
        "total": total,
        "page": page,
        "pages": pages,
        "filters": {
            "query": q,
            "category": category,
            "min_rating": min_rating,
            "verified_only": verified_only,
            "sort_by": sort_by
        }
    }

@router.get("/categories")
async def get_categories(db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get all available shop categories with counts."""
    # Return predefined categories with shop counts
    category_counts = []
    
    for cat in SHOP_CATEGORIES:
        count = await db.shops.count_documents({"category": cat})
        category_counts.append({
            "name": cat,
            "count": count
        })
    
    # Sort by count (descending), then alphabetically
    category_counts.sort(key=lambda x: (-x["count"], x["name"]))
    
    return {"categories": category_counts}

@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=20),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get search suggestions based on query."""
    # Search in shop names
    shops = await db.shops.find(
        {"name": {"$regex": f"^{q}", "$options": "i"}}
    ).limit(limit).to_list(limit)
    
    suggestions = []
    for shop in shops:
        suggestions.append({
            "type": "shop",
            "id": str(shop["_id"]),
            "name": shop["name"],
            "category": shop.get("category", "")
        })
    
    return {"suggestions": suggestions}
