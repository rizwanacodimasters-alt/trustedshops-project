from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from auth import get_current_user_email
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter(prefix="/security", tags=["Security Monitoring"])

def get_db():
    from server import db
    return db

@router.get("/login-logs")
async def get_login_logs(
    limit: int = 50,
    days: int = 7,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get login logs (admin only)."""
    # Verify admin
    user = await db.users.find_one({"email": email})
    if not user or user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get login logs from last N days
    since_date = datetime.utcnow() - timedelta(days=days)
    
    login_logs = await db.login_history.find(
        {"timestamp": {"$gte": since_date}}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    
    # Enrich with user info
    result = []
    for log in login_logs:
        log["id"] = str(log["_id"])
        del log["_id"]
        
        # Get user info
        if log.get("user_id"):
            user_info = await db.users.find_one({"id": log["user_id"]})
            if user_info:
                log["user_name"] = user_info.get("full_name", "Unknown")
                log["user_email"] = user_info.get("email", "")
                log["user_role"] = user_info.get("role", "")
        else:
            log["user_name"] = "Unknown"
            log["user_email"] = log.get("email", "")
            log["user_role"] = "Unknown"
        
        result.append(log)
    
    return {
        "data": result,
        "total": len(result),
        "days": days
    }

@router.get("/failed-logins")
async def get_failed_logins(
    limit: int = 50,
    days: int = 7,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get failed login attempts (admin only)."""
    # Verify admin
    user = await db.users.find_one({"email": email})
    if not user or user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get failed login attempts
    since_date = datetime.utcnow() - timedelta(days=days)
    
    failed_logins = await db.login_history.find({
        "success": False,
        "timestamp": {"$gte": since_date}
    }).sort("timestamp", -1).limit(limit).to_list(limit)
    
    # Format results
    result = []
    for log in failed_logins:
        log["id"] = str(log["_id"])
        del log["_id"]
        result.append(log)
    
    # Calculate statistics
    total_failed = len(result)
    unique_ips = len(set(log.get("ip_address", "") for log in result if log.get("ip_address")))
    unique_emails = len(set(log.get("email", "") for log in result if log.get("email")))
    
    return {
        "data": result,
        "total": total_failed,
        "unique_ips": unique_ips,
        "unique_emails": unique_emails,
        "days": days
    }

@router.get("/suspicious-activities")
async def get_suspicious_activities(
    limit: int = 50,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get suspicious activities (admin only)."""
    # Verify admin
    user = await db.users.find_one({"email": email})
    if not user or user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get security alerts
    alerts = await db.security_alerts.find(
        {"resolved": False}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    # Format results
    result = []
    for alert in alerts:
        alert["id"] = str(alert["_id"])
        del alert["_id"]
        
        # Get user info if available
        if alert.get("user_id"):
            user_info = await db.users.find_one({"id": alert["user_id"]})
            if user_info:
                alert["user_name"] = user_info.get("full_name", "Unknown")
                alert["user_email"] = user_info.get("email", "")
        
        result.append(alert)
    
    return {
        "data": result,
        "total": len(result)
    }

@router.get("/ip-tracking")
async def get_ip_tracking(
    days: int = 7,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get IP tracking statistics (admin only)."""
    # Verify admin
    user = await db.users.find_one({"email": email})
    if not user or user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Get login logs for IP analysis
    since_date = datetime.utcnow() - timedelta(days=days)
    
    login_logs = await db.login_history.find(
        {"timestamp": {"$gte": since_date}}
    ).to_list(None)
    
    # Analyze IP addresses
    ip_stats = {}
    for log in login_logs:
        ip = log.get("ip_address", "Unknown")
        if ip not in ip_stats:
            ip_stats[ip] = {
                "ip_address": ip,
                "total_attempts": 0,
                "successful_logins": 0,
                "failed_logins": 0,
                "unique_users": set(),
                "last_seen": log.get("timestamp")
            }
        
        ip_stats[ip]["total_attempts"] += 1
        if log.get("success"):
            ip_stats[ip]["successful_logins"] += 1
        else:
            ip_stats[ip]["failed_logins"] += 1
        
        if log.get("user_id"):
            ip_stats[ip]["unique_users"].add(log["user_id"])
        
        # Update last seen
        if log.get("timestamp") > ip_stats[ip]["last_seen"]:
            ip_stats[ip]["last_seen"] = log.get("timestamp")
    
    # Convert to list and format
    result = []
    for ip, stats in ip_stats.items():
        stats["unique_users"] = len(stats["unique_users"])
        stats["risk_score"] = calculate_risk_score(stats)
        result.append(stats)
    
    # Sort by risk score
    result.sort(key=lambda x: x["risk_score"], reverse=True)
    
    return {
        "data": result[:50],  # Top 50 IPs
        "total": len(result),
        "days": days
    }

def calculate_risk_score(stats):
    """Calculate risk score for an IP address."""
    score = 0
    
    # High number of failed logins
    if stats["failed_logins"] > 10:
        score += 50
    elif stats["failed_logins"] > 5:
        score += 30
    elif stats["failed_logins"] > 2:
        score += 10
    
    # Failed login ratio
    if stats["total_attempts"] > 0:
        fail_ratio = stats["failed_logins"] / stats["total_attempts"]
        if fail_ratio > 0.8:
            score += 30
        elif fail_ratio > 0.5:
            score += 20
    
    # Multiple unique users from same IP (suspicious)
    if stats["unique_users"] > 5:
        score += 20
    elif stats["unique_users"] > 3:
        score += 10
    
    return min(score, 100)

@router.post("/resolve-alert/{alert_id}")
async def resolve_security_alert(
    alert_id: str,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Mark security alert as resolved (admin only)."""
    # Verify admin
    user = await db.users.find_one({"email": email})
    if not user or user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Update alert
    from bson import ObjectId
    result = await db.security_alerts.update_one(
        {"_id": ObjectId(alert_id)},
        {
            "$set": {
                "resolved": True,
                "resolved_by": str(user["_id"]),
                "resolved_at": datetime.utcnow()
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    return {"message": "Alert marked as resolved"}

@router.get("/statistics")
async def get_security_statistics(
    days: int = 7,
    email: str = Depends(get_current_user_email),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get security statistics overview (admin only)."""
    # Verify admin
    user = await db.users.find_one({"email": email})
    if not user or user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    since_date = datetime.utcnow() - timedelta(days=days)
    
    # Total logins
    total_logins = await db.login_history.count_documents({
        "timestamp": {"$gte": since_date}
    })
    
    # Successful logins
    successful_logins = await db.login_history.count_documents({
        "timestamp": {"$gte": since_date},
        "success": True
    })
    
    # Failed logins
    failed_logins = await db.login_history.count_documents({
        "timestamp": {"$gte": since_date},
        "success": False
    })
    
    # Unresolved security alerts
    security_alerts = await db.security_alerts.count_documents({
        "resolved": False
    })
    
    # Unique IPs
    login_logs = await db.login_history.find({
        "timestamp": {"$gte": since_date}
    }).to_list(None)
    unique_ips = len(set(log.get("ip_address", "") for log in login_logs if log.get("ip_address")))
    
    return {
        "total_logins": total_logins,
        "successful_logins": successful_logins,
        "failed_logins": failed_logins,
        "security_alerts": security_alerts,
        "unique_ips": unique_ips,
        "days": days,
        "success_rate": round((successful_logins / total_logins * 100) if total_logins > 0 else 0, 2)
    }
