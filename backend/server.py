from fastapi import FastAPI, APIRouter, Request
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path

# Import route modules
from routes import (
    auth_routes, 
    shop_routes, 
    review_routes, 
    statistics_routes,
    order_routes,
    dashboard_routes,
    shop_verification_routes,
    review_response_routes,
    search_routes,
    admin_user_routes,
    admin_shop_routes,
    admin_dashboard_routes,
    admin_review_routes,
    proof_upload_routes,
    billing_routes,
    customer_dashboard_routes,
    customer_profile_routes,
    fake_shop_checker_routes,
    security_monitoring_routes,
    email_verification_routes
)

# Load .env for local development only
if os.getenv("RAILWAY_ENV") != "production":
    from dotenv import load_dotenv
    ROOT_DIR = Path(__file__).parent
    load_dotenv(ROOT_DIR / ".env")

# -------------------------------
# App & Logging Setup
# -------------------------------
app = FastAPI(
    title="TrustedShops Clone API",
    description="Full-stack TrustedShops clone with user authentication, shop management, and review system",
    version="1.0.0"
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# -------------------------------
# API Router
# -------------------------------
api_router = APIRouter(prefix="/api")

@api_router.get("/")
async def root():
    return {
        "message": "TrustedShops Clone API",
        "status": "running",
        "version": "1.0.0"
    }

# Include all route modules
api_router.include_router(auth_routes.router)
api_router.include_router(shop_routes.router)
api_router.include_router(review_routes.router)
api_router.include_router(statistics_routes.router)
api_router.include_router(order_routes.router)
api_router.include_router(dashboard_routes.router)
api_router.include_router(shop_verification_routes.router)
api_router.include_router(review_response_routes.router)
api_router.include_router(search_routes.router)
api_router.include_router(billing_routes.router)
api_router.include_router(customer_dashboard_routes.router)
api_router.include_router(customer_profile_routes.router)
api_router.include_router(fake_shop_checker_routes.router)
api_router.include_router(admin_user_routes.router)
api_router.include_router(admin_shop_routes.router)
api_router.include_router(admin_dashboard_routes.router)
api_router.include_router(admin_review_routes.router)
api_router.include_router(security_monitoring_routes.router)
api_router.include_router(email_verification_routes.router)
api_router.include_router(proof_upload_routes.router)

app.include_router(api_router)

# -------------------------------
# CORS Middleware
# -------------------------------
origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Startup / Shutdown Events
# -------------------------------
@app.on_event("startup")
async def startup_event():
    """Connect to MongoDB and create indexes"""
    mongo_url = os.getenv("MONGO_URL")
    db_name = os.getenv("DB_NAME", "trusted_shops_clone")  # default DB

    if not mongo_url:
        raise RuntimeError("❌ MONGO_URL environment variable is missing!")

    # Connect to MongoDB
    app.state.mongo_client = AsyncIOMotorClient(
        mongo_url,
        serverSelectionTimeoutMS=5000  # Fail fast if unreachable
    )
    app.state.db = app.state.mongo_client[db_name]

    # Test connection
    try:
        await app.state.mongo_client.admin.command("ping")
        logger.info(f"✅ Connected to MongoDB: {db_name}")
    except Exception as e:
        logger.error(f"❌ Could not connect to MongoDB: {e}")
        raise e

    # Create indexes
    db = app.state.db
    try:
        await db.users.create_index("email", unique=True)
        await db.users.create_index("role")
        await db.users.create_index("is_active")
        await db.shops.create_index("owner_id")
        await db.shops.create_index("category")
        await db.shops.create_index("is_verified")
        await db.shops.create_index("rating")
        await db.shops.create_index("status")
        await db.reviews.create_index("shop_id")
        await db.reviews.create_index("user_id")
        await db.reviews.create_index([("user_id", 1), ("shop_id", 1)], unique=True)
        await db.orders.create_index("user_id")
        await db.orders.create_index("shop_id")
        await db.orders.create_index("order_number", unique=True)
        await db.shop_verifications.create_index("shop_id")
        await db.review_responses.create_index("review_id", unique=True)
        await db.review_responses.create_index("shop_id")
        await db.login_history.create_index("user_id")
        await db.login_history.create_index("timestamp")
        await db.user_sessions.create_index("user_id")
        await db.user_sessions.create_index("is_active")
        await db.security_alerts.create_index("user_id")
        await db.security_alerts.create_index("resolved")
        logger.info("✅ Database indexes created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create indexes: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Close MongoDB connection"""
    logger.info("Shutting down TrustedShops Clone API...")
    client = getattr(app.state, "mongo_client", None)
    if client:
        client.close()

# -------------------------------
# Helper function for routes
# -------------------------------
def get_db(request: Request):
    """Access the MongoDB database from any route"""
    return request.app.state.db
