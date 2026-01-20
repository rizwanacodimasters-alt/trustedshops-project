from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from auth import get_current_user_email
from datetime import datetime, timedelta
from bson import ObjectId

router = APIRouter(prefix="/admin/dashboard", tags=["Admin - Dashboard"])

def get_db():
    from server import db
    return db

async def check_admin(email: str, db: AsyncIOMotorDatabase):
    """Check if user is admin."""
    user = await db.users.find_one({"email": email})
    if not user or user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user

@router.get("/overview")
async def get_admin_dashboard_overview(
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get admin dashboard overview (admin only)."""
    await check_admin(email, db)
    
    # Get counts
    total_users = await db.users.count_documents({})
    active_users = await db.users.count_documents({"is_active": True})
    total_shops = await db.shops.count_documents({})
    verified_shops = await db.shops.count_documents({"is_verified": True})
    pending_verifications = await db.shop_verifications.count_documents({"status": "pending"})
    total_reviews = await db.reviews.count_documents({})
    total_orders = await db.orders.count_documents({})
    
    # Get user role distribution
    user_roles = {}
    for role in ["shopper", "shop_owner", "admin"]:
        count = await db.users.count_documents({"role": role})
        user_roles[role] = count
    
    # Get shop status distribution
    shop_statuses = {}
    for status_val in ["active", "suspended", "pending_review", "banned"]:
        count = await db.shops.count_documents({"status": status_val})
        shop_statuses[status_val] = count
    
    # Get recent activity (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_users_30d = await db.users.count_documents({"created_at": {"$gte": thirty_days_ago}})
    new_shops_30d = await db.shops.count_documents({"created_at": {"$gte": thirty_days_ago}})
    new_reviews_30d = await db.reviews.count_documents({"created_at": {"$gte": thirty_days_ago}})
    new_orders_30d = await db.orders.count_documents({"created_at": {"$gte": thirty_days_ago}})
    
    # Get security alerts
    active_security_alerts = await db.security_alerts.count_documents({"resolved": False})
    critical_alerts = await db.security_alerts.count_documents({
        "resolved": False,
        "severity": "critical"
    })
    
    # Get top shops by rating
    top_shops = await db.shops.find(
        {"review_count": {"$gt": 0}}
    ).sort("rating", -1).limit(10).to_list(10)
    
    for shop in top_shops:
        shop["id"] = str(shop["_id"])
        del shop["_id"]
    
    # Get recent users
    recent_users = await db.users.find(
        {},
        {"password": 0}
    ).sort("created_at", -1).limit(10).to_list(10)
    
    for user in recent_users:
        user["id"] = str(user["_id"])
        del user["_id"]
    
    # Get pending shop verifications
    pending_shops = await db.shops.find(
        {"is_verified": False}
    ).limit(10).to_list(10)
    
    for shop in pending_shops:
        shop["id"] = str(shop["_id"])
        del shop["_id"]
    
    return {
        "statistics": {
            "total_users": total_users,
            "active_users": active_users,
            "total_shops": total_shops,
            "verified_shops": verified_shops,
            "pending_verifications": pending_verifications,
            "total_reviews": total_reviews,
            "total_orders": total_orders,
            "active_security_alerts": active_security_alerts,
            "critical_alerts": critical_alerts
        },
        "user_roles": user_roles,
        "shop_statuses": shop_statuses,
        "recent_activity": {
            "new_users_30d": new_users_30d,
            "new_shops_30d": new_shops_30d,
            "new_reviews_30d": new_reviews_30d,
            "new_orders_30d": new_orders_30d
        },
        "top_shops": top_shops,
        "recent_users": recent_users,
        "pending_shops": pending_shops
    }

@router.get("/security-alerts")
async def get_security_alerts(
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get all security alerts (admin only)."""
    await check_admin(email, db)
    
    alerts = await db.security_alerts.find(
        {"resolved": False}
    ).sort("created_at", -1).limit(50).to_list(50)
    
    for alert in alerts:
        alert["id"] = str(alert["_id"])
        del alert["_id"]
        
        # Get user info
        if alert.get("user_id"):
            user = await db.users.find_one({"_id": ObjectId(alert["user_id"])}, {"full_name": 1, "email": 1})
            if user:
                alert["user_name"] = user["full_name"]
                alert["user_email"] = user["email"]
    
    return {"alerts": alerts}

@router.post("/security-alerts/{alert_id}/resolve")
async def resolve_security_alert(
    alert_id: str,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Resolve security alert (admin only)."""
    await check_admin(email, db)
    
    from bson import ObjectId
    await db.security_alerts.update_one(
        {"_id": ObjectId(alert_id)},
        {"$set": {"resolved": True, "resolved_at": datetime.utcnow()}}
    )
    
    return {"message": "Alert resolved successfully"}
