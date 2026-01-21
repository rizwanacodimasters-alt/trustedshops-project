from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
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

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(
    title="TrustedShops Clone API",
    description="Full-stack TrustedShops clone with user authentication, shop management, and review system",
    version="1.0.0"
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Health check endpoint
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
# Admin routes
api_router.include_router(admin_user_routes.router)
api_router.include_router(admin_shop_routes.router)
api_router.include_router(admin_dashboard_routes.router)
api_router.include_router(admin_review_routes.router)
api_router.include_router(security_monitoring_routes.router)
api_router.include_router(email_verification_routes.router)
# Proof upload routes
api_router.include_router(proof_upload_routes.router)

# Include the router in the main app
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting TrustedShops Clone API...")
    logger.info(f"Connected to MongoDB: {db.name}")
    
    # Create indexes
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
    
    logger.info("Database indexes created successfully")

@app.on_event("shutdown")
async def shutdown_db_client():
    logger.info("Shutting down API...")
    client.close()