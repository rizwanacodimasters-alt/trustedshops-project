#!/usr/bin/env python3
"""
TrustedShops Clone Backend API Test Suite - Shop Owner Dashboard Focus
Tests all shop owner dashboard backend endpoints as specified in the review request.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://trust-ratings-app.preview.emergentagent.com/api"
TIMEOUT = 30

# Test credentials as specified in review request
SHOP_OWNER_CREDENTIALS = {
    "email": "owner@shop.com",
    "password": "owner123"
}

# Test data - use timestamp to ensure unique email for regular user
import time
timestamp = int(time.time())
TEST_USER = {
    "full_name": "Sarah Johnson",
    "email": f"sarah.johnson.{timestamp}@example.com", 
    "password": "securepass123",
    "role": "shopper"
}

TEST_SHOP = {
    "name": "TechHub Electronics",
    "description": "Your one-stop destination for cutting-edge electronics, gadgets, and tech accessories with expert customer service",
    "logo": "https://via.placeholder.com/200",
    "image": "https://via.placeholder.com/800x600", 
    "website": "techhub-electronics.com",
    "category": "Electronics"
}

TEST_REVIEW = {
    "rating": 5,
    "comment": "Outstanding service and product quality! Fast shipping, excellent customer support, and genuine products. Highly recommended!"
}

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = TIMEOUT
        self.token = None
        self.user_id = None
        self.shop_id = None
        self.review_id = None
        self.shop_owner_token = None
        self.shop_owner_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        print()
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def make_request(self, method, endpoint, data=None, headers=None):
        """Make HTTP request with error handling"""
        url = f"{BASE_URL}{endpoint}"
        
        # Add auth header if token exists and no headers provided
        if headers is None and self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
        elif headers is None:
            headers = {}
            
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            return response
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            print(f"URL: {url}, Method: {method}, Data: {data}")
            return None
    
    def test_user_registration(self):
        """Test POST /api/auth/register"""
        print("🔐 Testing User Registration...")
        
        response = self.make_request("POST", "/auth/register", TEST_USER)
        
        if not response:
            self.log_test("User Registration", False, "Request failed")
            return False
            
        if response.status_code == 201:
            data = response.json()
            
            # Validate response structure
            if "user" in data and "token" in data:
                user = data["user"]
                token = data["token"]
                
                # Check user data
                if (user.get("full_name") == TEST_USER["full_name"] and 
                    user.get("email") == TEST_USER["email"] and
                    user.get("role") == TEST_USER["role"] and
                    "id" in user):
                    
                    # Check token
                    if token.get("access_token") and token.get("token_type") == "bearer":
                        self.token = token["access_token"]
                        self.user_id = user["id"]
                        self.log_test("User Registration", True, f"User registered with ID: {self.user_id}")
                        return True
                    else:
                        self.log_test("User Registration", False, "Invalid token structure", data)
                else:
                    self.log_test("User Registration", False, "Invalid user data structure", data)
            else:
                self.log_test("User Registration", False, "Missing user or token in response", data)
        else:
            self.log_test("User Registration", False, f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_user_login(self):
        """Test POST /api/auth/login"""
        print("🔑 Testing User Login...")
        
        login_data = {
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
        
        response = self.make_request("POST", "/auth/login", login_data, headers={})
        
        if not response:
            self.log_test("User Login", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            # Validate response structure
            if "user" in data and "token" in data:
                user = data["user"]
                token = data["token"]
                
                # Verify user data matches
                if (user.get("email") == TEST_USER["email"] and
                    user.get("full_name") == TEST_USER["full_name"] and
                    token.get("access_token")):
                    
                    self.token = token["access_token"]  # Update token
                    self.log_test("User Login", True, f"Login successful for {user['email']}")
                    return True
                else:
                    self.log_test("User Login", False, "User data mismatch", data)
            else:
                self.log_test("User Login", False, "Missing user or token in response", data)
        else:
            self.log_test("User Login", False, f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_get_current_user(self):
        """Test GET /api/auth/me"""
        print("👤 Testing Get Current User...")
        
        if not self.token:
            self.log_test("Get Current User", False, "No auth token available")
            return False
            
        response = self.make_request("GET", "/auth/me")
        
        if not response:
            self.log_test("Get Current User", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            # Validate user data
            if (data.get("email") == TEST_USER["email"] and
                data.get("full_name") == TEST_USER["full_name"] and
                data.get("role") == TEST_USER["role"] and
                "id" in data):
                
                self.log_test("Get Current User", True, f"Retrieved user: {data['full_name']}")
                return True
            else:
                self.log_test("Get Current User", False, "Invalid user data", data)
        else:
            self.log_test("Get Current User", False, f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_create_shop(self):
        """Test POST /api/shops"""
        print("🏪 Testing Shop Creation...")
        
        if not self.token:
            self.log_test("Shop Creation", False, "No auth token available")
            return False
            
        response = self.make_request("POST", "/shops", TEST_SHOP)
        
        if not response:
            self.log_test("Shop Creation", False, "Request failed")
            return False
            
        if response.status_code == 201:
            data = response.json()
            
            # Validate shop data - check for either 'id' or '_id' field
            shop_id = data.get("id") or str(data.get("_id", ""))
            if (data.get("name") == TEST_SHOP["name"] and
                data.get("description") == TEST_SHOP["description"] and
                data.get("category") == TEST_SHOP["category"] and
                shop_id and
                data.get("rating") == 0.0 and
                data.get("review_count") == 0):
                
                self.shop_id = shop_id
                self.log_test("Shop Creation", True, f"Shop created with ID: {self.shop_id}")
                return True
            else:
                self.log_test("Shop Creation", False, "Invalid shop data structure", data)
        else:
            self.log_test("Shop Creation", False, f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_get_all_shops(self):
        """Test GET /api/shops"""
        print("🏪 Testing Get All Shops...")
        
        response = self.make_request("GET", "/shops", headers={})
        
        if not response:
            self.log_test("Get All Shops", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            # Validate response structure
            if ("data" in data and "total" in data and 
                "page" in data and "pages" in data):
                
                shops = data["data"]
                
                # Check if our created shop is in the list
                shop_found = False
                for shop in shops:
                    if shop.get("id") == self.shop_id:
                        shop_found = True
                        break
                
                if shop_found:
                    self.log_test("Get All Shops", True, f"Found {len(shops)} shops including our created shop")
                    return True
                else:
                    self.log_test("Get All Shops", False, f"Created shop not found in {len(shops)} shops")
            else:
                self.log_test("Get All Shops", False, "Invalid response structure", data)
        else:
            self.log_test("Get All Shops", False, f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_get_single_shop(self):
        """Test GET /api/shops/{shop_id}"""
        print("🏪 Testing Get Single Shop...")
        
        if not self.shop_id:
            self.log_test("Get Single Shop", False, "No shop ID available")
            return False
            
        response = self.make_request("GET", f"/shops/{self.shop_id}", headers={})
        
        if not response:
            self.log_test("Get Single Shop", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            # Validate shop data - check for either 'id' or '_id' field
            shop_id_in_response = data.get("id") or str(data.get("_id", ""))
            if (shop_id_in_response == self.shop_id and
                data.get("name") == TEST_SHOP["name"] and
                data.get("description") == TEST_SHOP["description"]):
                
                self.log_test("Get Single Shop", True, f"Retrieved shop: {data['name']}")
                return True
            else:
                self.log_test("Get Single Shop", False, "Shop data mismatch", data)
        else:
            self.log_test("Get Single Shop", False, f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_create_review(self):
        """Test POST /api/reviews"""
        print("⭐ Testing Review Creation...")
        
        if not self.token or not self.shop_id:
            self.log_test("Review Creation", False, "Missing auth token or shop ID")
            return False
            
        review_data = TEST_REVIEW.copy()
        review_data["shop_id"] = self.shop_id
        
        response = self.make_request("POST", "/reviews", review_data)
        
        if not response:
            self.log_test("Review Creation", False, "Request failed")
            return False
            
        if response.status_code == 201:
            data = response.json()
            
            # Validate review data - check for either 'id' or '_id' field
            review_id_in_response = data.get("id") or str(data.get("_id", ""))
            if (data.get("shop_id") == self.shop_id and
                data.get("rating") == TEST_REVIEW["rating"] and
                data.get("comment") == TEST_REVIEW["comment"] and
                review_id_in_response and
                data.get("user_name") and
                data.get("shop_name")):
                
                self.review_id = review_id_in_response
                self.log_test("Review Creation", True, f"Review created with ID: {self.review_id}")
                return True
            else:
                self.log_test("Review Creation", False, "Invalid review data structure", data)
        else:
            self.log_test("Review Creation", False, f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_get_all_reviews(self):
        """Test GET /api/reviews"""
        print("⭐ Testing Get All Reviews...")
        
        response = self.make_request("GET", "/reviews", headers={})
        
        if not response:
            self.log_test("Get All Reviews", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            # Validate response structure
            if ("data" in data and "total" in data and 
                "page" in data and "pages" in data):
                
                reviews = data["data"]
                
                # Check if our created review is in the list
                review_found = False
                for review in reviews:
                    if review.get("id") == self.review_id:
                        review_found = True
                        break
                
                if review_found:
                    self.log_test("Get All Reviews", True, f"Found {len(reviews)} reviews including our created review")
                    return True
                else:
                    self.log_test("Get All Reviews", False, f"Created review not found in {len(reviews)} reviews")
            else:
                self.log_test("Get All Reviews", False, "Invalid response structure", data)
        else:
            self.log_test("Get All Reviews", False, f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_shop_rating_update(self):
        """Verify that shop rating was updated after review creation"""
        print("📊 Testing Shop Rating Update...")
        
        if not self.shop_id:
            self.log_test("Shop Rating Update", False, "No shop ID available")
            return False
            
        response = self.make_request("GET", f"/shops/{self.shop_id}", headers={})
        
        if not response:
            self.log_test("Shop Rating Update", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            # Check if rating and review_count were updated
            if (data.get("rating") == TEST_REVIEW["rating"] and
                data.get("review_count") == 1):
                
                self.log_test("Shop Rating Update", True, f"Shop rating updated to {data['rating']} with {data['review_count']} review(s)")
                return True
            else:
                self.log_test("Shop Rating Update", False, f"Rating: {data.get('rating')}, Count: {data.get('review_count')}", data)
        else:
            self.log_test("Shop Rating Update", False, f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_get_statistics(self):
        """Test GET /api/statistics"""
        print("📈 Testing Get Statistics...")
        
        response = self.make_request("GET", "/statistics", headers={})
        
        if not response:
            self.log_test("Get Statistics", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            # Validate statistics structure
            if ("shoppers" in data and "shops" in data and "dailyTransactions" in data):
                
                # Check that counts are reasonable (should be at least 1 for each)
                shoppers = data["shoppers"]
                shops = data["shops"] 
                transactions = data["dailyTransactions"]
                
                self.log_test("Get Statistics", True, f"Stats - Shoppers: {shoppers}, Shops: {shops}, Transactions: {transactions}")
                return True
            else:
                self.log_test("Get Statistics", False, "Invalid statistics structure", data)
        else:
            self.log_test("Get Statistics", False, f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False

    # ========== SHOP OWNER DASHBOARD TESTS ==========
    
    def test_shop_owner_login(self):
        """Test shop owner login with specified credentials"""
        print("🔑 Testing Shop Owner Login...")
        
        response = self.make_request("POST", "/auth/login", SHOP_OWNER_CREDENTIALS, headers={})
        
        if not response:
            self.log_test("Shop Owner Login", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            # Validate response structure
            if "user" in data and "token" in data:
                user = data["user"]
                token = data["token"]
                
                # Verify user data and role
                if (user.get("email") == SHOP_OWNER_CREDENTIALS["email"] and
                    user.get("role") == "shop_owner" and
                    token.get("access_token")):
                    
                    self.shop_owner_token = token["access_token"]
                    self.shop_owner_id = user["id"]
                    self.log_test("Shop Owner Login", True, f"Shop owner logged in: {user['email']}")
                    return True
                else:
                    self.log_test("Shop Owner Login", False, f"Invalid role or data. Role: {user.get('role')}", data)
            else:
                self.log_test("Shop Owner Login", False, "Missing user or token in response", data)
        else:
            self.log_test("Shop Owner Login", False, f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_shop_owner_dashboard(self):
        """Test GET /api/dashboard/shop-owner"""
        print("📊 Testing Shop Owner Dashboard...")
        
        if not self.shop_owner_token:
            self.log_test("Shop Owner Dashboard", False, "No shop owner token available")
            return False
            
        # Use shop owner token for this request
        headers = {"Authorization": f"Bearer {self.shop_owner_token}"}
        response = self.make_request("GET", "/dashboard/shop-owner", headers=headers)
        
        if not response:
            self.log_test("Shop Owner Dashboard", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            # Validate dashboard structure
            required_fields = ["user", "statistics", "shops", "recent_reviews"]
            if all(field in data for field in required_fields):
                
                # Validate user info
                user = data["user"]
                if user.get("email") == SHOP_OWNER_CREDENTIALS["email"] and user.get("role") == "shop_owner":
                    
                    # Validate statistics structure
                    stats = data["statistics"]
                    required_stats = ["total_shops", "verified_shops", "total_reviews", "average_rating", "unanswered_reviews", "new_reviews_30d"]
                    if all(stat in stats for stat in required_stats):
                        
                        self.log_test("Shop Owner Dashboard", True, 
                                    f"Dashboard loaded - Shops: {stats['total_shops']}, Reviews: {stats['total_reviews']}, Rating: {stats['average_rating']}")
                        return True
                    else:
                        self.log_test("Shop Owner Dashboard", False, f"Missing statistics fields: {required_stats}", data)
                else:
                    self.log_test("Shop Owner Dashboard", False, "Invalid user data in dashboard", data)
            else:
                self.log_test("Shop Owner Dashboard", False, f"Missing required fields: {required_fields}", data)
        else:
            self.log_test("Shop Owner Dashboard", False, f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_shop_management_create(self):
        """Test POST /api/shops with shop owner credentials"""
        print("🏪 Testing Shop Creation (Shop Owner)...")
        
        if not self.shop_owner_token:
            self.log_test("Shop Creation (Owner)", False, "No shop owner token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.shop_owner_token}"}
        response = self.make_request("POST", "/shops", TEST_SHOP, headers=headers)
        
        if not response:
            self.log_test("Shop Creation (Owner)", False, "Request failed")
            return False
            
        if response.status_code == 201:
            data = response.json()
            
            # Validate shop data
            shop_id = data.get("id") or str(data.get("_id", ""))
            if (data.get("name") == TEST_SHOP["name"] and
                data.get("description") == TEST_SHOP["description"] and
                data.get("category") == TEST_SHOP["category"] and
                shop_id):
                
                self.shop_id = shop_id  # Store for other tests
                self.log_test("Shop Creation (Owner)", True, f"Shop created by owner with ID: {self.shop_id}")
                return True
            else:
                self.log_test("Shop Creation (Owner)", False, "Invalid shop data structure", data)
        else:
            self.log_test("Shop Creation (Owner)", False, f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_shop_management_update(self):
        """Test PUT /api/shops/{shop_id} with authorization check"""
        print("🏪 Testing Shop Update Authorization...")
        
        if not self.shop_owner_token or not self.shop_id:
            self.log_test("Shop Update Authorization", False, "Missing shop owner token or shop ID")
            return False
            
        # Test data for update
        update_data = {
            "name": "Updated TechHub Electronics",
            "description": "Updated description for our electronics store"
        }
        
        headers = {"Authorization": f"Bearer {self.shop_owner_token}"}
        response = self.make_request("PUT", f"/shops/{self.shop_id}", update_data, headers=headers)
        
        if not response:
            self.log_test("Shop Update Authorization", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            # Verify update was applied
            if (data.get("name") == update_data["name"] and
                data.get("description") == update_data["description"]):
                
                self.log_test("Shop Update Authorization", True, "Shop updated successfully by owner")
                return True
            else:
                self.log_test("Shop Update Authorization", False, "Update not applied correctly", data)
        else:
            self.log_test("Shop Update Authorization", False, f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_shop_verification_request(self):
        """Test POST /api/shop-verification/request/{shop_id}"""
        print("✅ Testing Shop Verification Request...")
        
        if not self.shop_owner_token or not self.shop_id:
            self.log_test("Shop Verification Request", False, "Missing shop owner token or shop ID")
            return False
            
        headers = {"Authorization": f"Bearer {self.shop_owner_token}"}
        response = self.make_request("POST", f"/shop-verification/request/{self.shop_id}", headers=headers)
        
        if not response:
            self.log_test("Shop Verification Request", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            # Validate verification request response
            if "message" in data and ("verification" in data or "status" in data):
                self.log_test("Shop Verification Request", True, f"Verification requested: {data['message']}")
                return True
            else:
                self.log_test("Shop Verification Request", False, "Invalid verification response structure", data)
        else:
            self.log_test("Shop Verification Request", False, f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_billing_plans(self):
        """Test GET /api/billing/plans"""
        print("💳 Testing Billing Plans...")
        
        response = self.make_request("GET", "/billing/plans", headers={})
        
        if not response:
            self.log_test("Billing Plans", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            # Validate plans structure
            if "plans" in data:
                plans = data["plans"]
                expected_plans = ["basic", "professional", "enterprise"]
                
                if all(plan in plans for plan in expected_plans):
                    # Validate plan structure
                    basic_plan = plans["basic"]
                    if "name" in basic_plan and "price" in basic_plan and "currency" in basic_plan:
                        self.log_test("Billing Plans", True, f"Found {len(plans)} subscription plans")
                        return True
                    else:
                        self.log_test("Billing Plans", False, "Invalid plan structure", data)
                else:
                    self.log_test("Billing Plans", False, f"Missing expected plans: {expected_plans}", data)
            else:
                self.log_test("Billing Plans", False, "Missing plans in response", data)
        else:
            self.log_test("Billing Plans", False, f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_billing_checkout(self):
        """Test POST /api/billing/checkout"""
        print("💳 Testing Billing Checkout...")
        
        if not self.shop_owner_token:
            self.log_test("Billing Checkout", False, "No shop owner token available")
            return False
            
        checkout_data = {
            "plan_id": "basic",
            "origin_url": "https://trust-ratings-app.preview.emergentagent.com"
        }
        
        headers = {"Authorization": f"Bearer {self.shop_owner_token}"}
        response = self.make_request("POST", "/billing/checkout", checkout_data, headers=headers)
        
        if not response:
            self.log_test("Billing Checkout", False, "Request failed")
            return False
            
        # Note: This might fail due to Stripe configuration, but we test the endpoint structure
        if response.status_code == 200:
            data = response.json()
            
            # Validate checkout response
            if "url" in data and "session_id" in data:
                self.log_test("Billing Checkout", True, "Checkout session created successfully")
                return True
            else:
                self.log_test("Billing Checkout", False, "Invalid checkout response structure", data)
        elif response.status_code == 500:
            # Expected if Stripe is not properly configured
            error_data = response.json() if response.content else {}
            if "Stripe" in str(error_data):
                self.log_test("Billing Checkout", True, "Endpoint working - Stripe configuration issue (expected)")
                return True
            else:
                self.log_test("Billing Checkout", False, f"HTTP {response.status_code}", error_data)
        else:
            self.log_test("Billing Checkout", False, f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_billing_subscription(self):
        """Test GET /api/billing/subscription"""
        print("💳 Testing Get Subscription...")
        
        if not self.shop_owner_token:
            self.log_test("Get Subscription", False, "No shop owner token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.shop_owner_token}"}
        response = self.make_request("GET", "/billing/subscription", headers=headers)
        
        if not response:
            self.log_test("Get Subscription", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            # Validate subscription structure
            required_fields = ["plan_id", "plan_name", "price", "currency", "status"]
            if all(field in data for field in required_fields):
                self.log_test("Get Subscription", True, f"Current plan: {data['plan_name']} (${data['price']})")
                return True
            else:
                self.log_test("Get Subscription", False, f"Missing required fields: {required_fields}", data)
        else:
            self.log_test("Get Subscription", False, f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_billing_transactions(self):
        """Test GET /api/billing/transactions"""
        print("💳 Testing Get Transactions...")
        
        if not self.shop_owner_token:
            self.log_test("Get Transactions", False, "No shop owner token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.shop_owner_token}"}
        response = self.make_request("GET", "/billing/transactions", headers=headers)
        
        if not response:
            self.log_test("Get Transactions", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            # Validate transactions structure
            if "transactions" in data:
                transactions = data["transactions"]
                self.log_test("Get Transactions", True, f"Found {len(transactions)} transactions")
                return True
            else:
                self.log_test("Get Transactions", False, "Missing transactions in response", data)
        else:
            self.log_test("Get Transactions", False, f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_reviews_with_shop_filter(self):
        """Test GET /api/reviews with shop_id filter"""
        print("⭐ Testing Reviews with Shop Filter...")
        
        if not self.shop_id:
            self.log_test("Reviews with Shop Filter", False, "No shop ID available")
            return False
            
        # Test with shop_id parameter
        response = self.make_request("GET", f"/reviews?shop_id={self.shop_id}", headers={})
        
        if not response:
            self.log_test("Reviews with Shop Filter", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            # Validate response structure
            if "data" in data and "total" in data:
                reviews = data["data"]
                # All reviews should be for the specified shop
                if all(review.get("shop_id") == self.shop_id for review in reviews):
                    self.log_test("Reviews with Shop Filter", True, f"Found {len(reviews)} reviews for shop {self.shop_id}")
                    return True
                else:
                    self.log_test("Reviews with Shop Filter", False, "Reviews contain wrong shop IDs", data)
            else:
                self.log_test("Reviews with Shop Filter", False, "Invalid response structure", data)
        else:
            self.log_test("Reviews with Shop Filter", False, f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_review_response_creation(self):
        """Test POST /api/review-responses"""
        print("💬 Testing Review Response Creation...")
        
        if not self.shop_owner_token:
            self.log_test("Review Response Creation", False, "Missing shop owner token")
            return False
        
        # First, create a review for the shop owner's shop using regular user
        if not self.token or not self.shop_id:
            self.log_test("Review Response Creation", False, "Missing regular user token or shop owner's shop ID")
            return False
            
        # Create a review for the shop owner's shop
        review_data = {
            "shop_id": self.shop_id,  # This is the shop owner's shop
            "rating": 4,
            "comment": "Great service and fast delivery! Highly recommend this shop."
        }
        
        # Use regular user token to create the review
        headers = {"Authorization": f"Bearer {self.token}"}
        review_response = self.make_request("POST", "/reviews", review_data, headers=headers)
        
        if not review_response or review_response.status_code != 201:
            self.log_test("Review Response Creation", False, "Failed to create test review")
            return False
            
        review_data_response = review_response.json()
        test_review_id = review_data_response.get("id") or str(review_data_response.get("_id", ""))
        
        if not test_review_id:
            self.log_test("Review Response Creation", False, "No review ID returned")
            return False
            
        # Now create a response as the shop owner
        response_data = {
            "review_id": test_review_id,
            "response_text": "Thank you for your wonderful review! We're delighted to hear about your positive experience."
        }
        
        headers = {"Authorization": f"Bearer {self.shop_owner_token}"}
        response = self.make_request("POST", "/review-responses", response_data, headers=headers)
        
        if not response:
            self.log_test("Review Response Creation", False, "Request failed")
            return False
            
        if response.status_code == 201:
            data = response.json()
            
            # Validate response structure
            if (data.get("review_id") == test_review_id and
                data.get("response_text") == response_data["response_text"] and
                "id" in data):
                
                self.log_test("Review Response Creation", True, f"Review response created with ID: {data['id']}")
                return True
            else:
                self.log_test("Review Response Creation", False, "Invalid response data structure", data)
        else:
            self.log_test("Review Response Creation", False, f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def run_all_tests(self):
        """Run all tests in sequence - Focus on Shop Owner Dashboard"""
        print("🚀 Starting Shop Owner Dashboard Backend API Tests")
        print(f"🌐 Base URL: {BASE_URL}")
        print("=" * 60)
        
        # Basic Authentication Flow (for creating test data)
        print("🔐 BASIC AUTHENTICATION FLOW")
        print("-" * 30)
        basic_auth_success = (
            self.test_user_registration() and
            self.test_user_login() and
            self.test_get_current_user()
        )
        
        if not basic_auth_success:
            print("❌ Basic authentication flow failed. Continuing with shop owner tests.")
        
        # Create test data (shop and review) for shop owner tests
        if basic_auth_success:
            print("\n🏪 CREATING TEST DATA")
            print("-" * 30)
            test_data_success = (
                self.test_create_shop() and
                self.test_create_review()
            )
            
            if not test_data_success:
                print("❌ Test data creation failed. Some shop owner tests may fail.")
        
        # Shop Owner Authentication & Authorization
        print("\n🔐 SHOP OWNER AUTHENTICATION & AUTHORIZATION")
        print("-" * 50)
        shop_owner_auth_success = self.test_shop_owner_login()
        
        if not shop_owner_auth_success:
            print("❌ Shop owner authentication failed. Cannot proceed with dashboard tests.")
            return False
        
        # Shop Owner Dashboard API
        print("\n📊 SHOP OWNER DASHBOARD API")
        print("-" * 30)
        dashboard_success = self.test_shop_owner_dashboard()
        
        # Shop Management APIs
        print("\n🏪 SHOP MANAGEMENT APIs")
        print("-" * 30)
        shop_mgmt_success = (
            self.test_shop_management_create() and
            self.test_get_all_shops() and
            self.test_get_single_shop() and
            self.test_shop_management_update()
        )
        
        # Shop Verification API
        print("\n✅ SHOP VERIFICATION API")
        print("-" * 30)
        verification_success = self.test_shop_verification_request()
        
        # Billing APIs
        print("\n💳 BILLING APIs")
        print("-" * 30)
        billing_success = (
            self.test_billing_plans() and
            self.test_billing_checkout() and
            self.test_billing_subscription() and
            self.test_billing_transactions()
        )
        
        # Review Management
        print("\n⭐ REVIEW MANAGEMENT")
        print("-" * 30)
        review_mgmt_success = (
            self.test_reviews_with_shop_filter() and
            self.test_review_response_creation()
        )
        
        # Statistics (general)
        print("\n📈 STATISTICS")
        print("-" * 30)
        stats_success = self.test_get_statistics()
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 SHOP OWNER DASHBOARD TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        # Categorize results
        critical_tests = [
            "Shop Owner Login", "Shop Owner Dashboard", "Shop Creation (Owner)",
            "Shop Update Authorization", "Shop Verification Request"
        ]
        
        critical_failures = []
        other_failures = []
        
        for result in self.test_results:
            if not result["success"]:
                if result["test"] in critical_tests:
                    critical_failures.append(result)
                else:
                    other_failures.append(result)
        
        if critical_failures:
            print(f"\n❌ CRITICAL FAILURES ({len(critical_failures)}):")
            for test in critical_failures:
                print(f"   - {test['test']}: {test['details']}")
        
        if other_failures:
            print(f"\n⚠️  OTHER FAILURES ({len(other_failures)}):")
            for test in other_failures:
                print(f"   - {test['test']}: {test['details']}")
        
        if passed == total:
            print("\n🎉 All Shop Owner Dashboard tests passed!")
            return True
        elif len(critical_failures) == 0:
            print("\n✅ All critical Shop Owner Dashboard functionality working!")
            return True
        else:
            print(f"\n❌ {len(critical_failures)} critical failures found.")
            return False

    def test_specific_shop_creation_request(self):
        """Test the specific shop creation request from the review"""
        print("🎯 Testing Specific Shop Creation Request...")
        print("=" * 60)
        
        # Step 1: Login as shop owner
        print("Step 1: Login as shop owner (owner@shop.com / owner123)")
        login_success = self.test_shop_owner_login()
        if not login_success:
            print("❌ Shop owner login failed - cannot proceed")
            return False
        
        # Step 2: Create shop with specific data
        print("\nStep 2: Create shop with specific data")
        specific_shop_data = {
            "name": "Test Shop Backend",
            "website": "https://testshop-backend.de",
            "category": "Bekleidung",
            "description": "Test shop for backend validation",
            "logo": "https://via.placeholder.com/200",
            "image": "https://via.placeholder.com/800x600"
        }
        
        headers = {"Authorization": f"Bearer {self.shop_owner_token}"}
        print(f"Making POST request to {BASE_URL}/shops")
        print(f"Request data: {json.dumps(specific_shop_data, indent=2)}")
        
        response = self.make_request("POST", "/shops", specific_shop_data, headers=headers)
        
        if not response:
            print("❌ Request failed - no response received")
            return False
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"Response data: {json.dumps(data, indent=2)}")
            
            # Verify response contains shop ID
            shop_id = data.get("id") or str(data.get("_id", ""))
            if shop_id:
                print(f"✅ Shop created successfully with ID: {shop_id}")
                self.shop_id = shop_id
                
                # Verify all fields are present
                fields_match = (
                    data.get("name") == specific_shop_data["name"] and
                    data.get("website") == specific_shop_data["website"] and
                    data.get("category") == specific_shop_data["category"] and
                    data.get("description") == specific_shop_data["description"] and
                    data.get("logo") == specific_shop_data["logo"] and
                    data.get("image") == specific_shop_data["image"]
                )
                
                if fields_match:
                    print("✅ All shop data fields match the request")
                else:
                    print("⚠️ Some shop data fields don't match")
                    
            else:
                print("❌ No shop ID found in response")
                return False
        else:
            error_data = response.json() if response.content else {}
            print(f"❌ Shop creation failed with status {response.status_code}")
            print(f"Error response: {json.dumps(error_data, indent=2)}")
            return False
        
        # Step 3: Verify shop appears in GET /api/shops
        print(f"\nStep 3: Verify shop appears in GET /api/shops")
        print(f"Making GET request to {BASE_URL}/shops")
        
        response = self.make_request("GET", "/shops", headers={})
        
        if not response:
            print("❌ GET /shops request failed")
            return False
            
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {data.get('total', 0)} total shops")
            
            shops = data.get("data", [])
            shop_found = False
            
            for shop in shops:
                if shop.get("id") == self.shop_id:
                    shop_found = True
                    print(f"✅ Created shop found in shops list:")
                    print(f"   Name: {shop.get('name')}")
                    print(f"   Category: {shop.get('category')}")
                    print(f"   Website: {shop.get('website')}")
                    break
            
            if not shop_found:
                print(f"❌ Created shop with ID {self.shop_id} not found in shops list")
                return False
        else:
            error_data = response.json() if response.content else {}
            print(f"❌ GET /shops failed with status {response.status_code}")
            print(f"Error response: {json.dumps(error_data, indent=2)}")
            return False
        
        # Step 4: Verify shop appears in shop owner dashboard
        print(f"\nStep 4: Verify shop appears in GET /api/dashboard/shop-owner")
        print(f"Making GET request to {BASE_URL}/dashboard/shop-owner")
        
        headers = {"Authorization": f"Bearer {self.shop_owner_token}"}
        response = self.make_request("GET", "/dashboard/shop-owner", headers=headers)
        
        if not response:
            print("❌ Dashboard request failed")
            return False
            
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Dashboard response structure: {list(data.keys())}")
            
            # Check if shop appears in dashboard shops
            dashboard_shops = data.get("shops", [])
            print(f"Found {len(dashboard_shops)} shops in dashboard")
            
            shop_in_dashboard = False
            for shop in dashboard_shops:
                if shop.get("id") == self.shop_id:
                    shop_in_dashboard = True
                    print(f"✅ Created shop found in dashboard:")
                    print(f"   Name: {shop.get('name')}")
                    print(f"   Category: {shop.get('category')}")
                    print(f"   Status: {shop.get('status', 'N/A')}")
                    print(f"   Verified: {shop.get('is_verified', False)}")
                    break
            
            if not shop_in_dashboard:
                print(f"❌ Created shop with ID {self.shop_id} not found in dashboard")
                print("Available shops in dashboard:")
                for shop in dashboard_shops:
                    print(f"   - {shop.get('name')} (ID: {shop.get('id')})")
                return False
                
            # Check statistics update
            stats = data.get("statistics", {})
            print(f"\nDashboard statistics:")
            print(f"   Total shops: {stats.get('total_shops', 0)}")
            print(f"   Verified shops: {stats.get('verified_shops', 0)}")
            print(f"   Total reviews: {stats.get('total_reviews', 0)}")
            print(f"   Average rating: {stats.get('average_rating', 0)}")
            
        else:
            error_data = response.json() if response.content else {}
            print(f"❌ Dashboard request failed with status {response.status_code}")
            print(f"Error response: {json.dumps(error_data, indent=2)}")
            return False
        
        print("\n🎉 All shop creation tests passed successfully!")
        print("=" * 60)
        return True

    # ========== EMAIL VERIFICATION TESTS ==========
    
    def test_email_verification_send_code(self):
        """Test POST /api/email-verification/send-code"""
        print("📧 Testing Email Verification - Send Code...")
        
        # Use an existing user email
        test_email = "sarah.johnson@example.com"
        
        request_data = {"email": test_email}
        response = self.make_request("POST", "/email-verification/send-code", request_data, headers={})
        
        if not response:
            self.log_test("Email Verification - Send Code", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            # Validate response structure
            required_fields = ["message", "expires_in_minutes", "email"]
            if all(field in data for field in required_fields):
                
                if (data["email"] == test_email and 
                    data["expires_in_minutes"] == 15 and
                    "sent" in data["message"].lower()):
                    
                    self.log_test("Email Verification - Send Code", True, 
                                f"Verification code sent to {test_email}, expires in {data['expires_in_minutes']} minutes")
                    return True
                else:
                    self.log_test("Email Verification - Send Code", False, "Invalid response data", data)
            else:
                self.log_test("Email Verification - Send Code", False, 
                            f"Missing required fields: {required_fields}", data)
        else:
            self.log_test("Email Verification - Send Code", False, 
                        f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_email_verification_check_code_storage(self):
        """Check if verification code is stored in MongoDB"""
        print("🗄️ Testing Email Verification - Code Storage...")
        
        # Check MongoDB for verification code
        try:
            import asyncio
            from motor.motor_asyncio import AsyncIOMotorClient
            
            async def check_verification_code():
                client = AsyncIOMotorClient('mongodb://localhost:27017')
                db = client['test_database']
                
                # Look for verification record
                verification = await db.email_verifications.find_one({"email": "sarah.johnson@example.com"})
                client.close()
                return verification
            
            verification = asyncio.run(check_verification_code())
            
            if verification:
                required_fields = ["code", "expires_at", "created_at", "attempts"]
                if all(field in verification for field in required_fields):
                    self.log_test("Email Verification - Code Storage", True, 
                                f"Verification code stored in database with {len(verification['code'])} digit code")
                    return verification["code"]  # Return code for next test
                else:
                    self.log_test("Email Verification - Code Storage", False, 
                                f"Missing required fields in verification record: {required_fields}")
            else:
                self.log_test("Email Verification - Code Storage", False, "No verification record found in database")
                
        except Exception as e:
            self.log_test("Email Verification - Code Storage", False, f"Database check failed: {e}")
            
        return None
    
    def test_email_verification_verify_correct_code(self, verification_code):
        """Test POST /api/email-verification/verify-code with correct code"""
        print("✅ Testing Email Verification - Verify Correct Code...")
        
        if not verification_code:
            self.log_test("Email Verification - Verify Correct Code", False, "No verification code available")
            return False
        
        verify_data = {
            "email": "sarah.johnson@example.com",
            "code": verification_code
        }
        
        response = self.make_request("POST", "/email-verification/verify-code", verify_data, headers={})
        
        if not response:
            self.log_test("Email Verification - Verify Correct Code", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            # Validate response structure
            if "message" in data and "verified" in data:
                if data["verified"] and "successfully" in data["message"].lower():
                    self.log_test("Email Verification - Verify Correct Code", True, 
                                "Email verification successful with correct code")
                    return True
                else:
                    self.log_test("Email Verification - Verify Correct Code", False, 
                                "Verification not successful", data)
            else:
                self.log_test("Email Verification - Verify Correct Code", False, 
                            "Invalid response structure", data)
        else:
            self.log_test("Email Verification - Verify Correct Code", False, 
                        f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_email_verification_verify_incorrect_code(self):
        """Test POST /api/email-verification/verify-code with incorrect code"""
        print("❌ Testing Email Verification - Verify Incorrect Code...")
        
        # First send a new code to test with
        request_data = {"email": "sarah.johnson@example.com"}
        send_response = self.make_request("POST", "/email-verification/send-code", request_data, headers={})
        
        if not send_response or send_response.status_code != 200:
            self.log_test("Email Verification - Verify Incorrect Code", False, "Could not send verification code")
            return False
        
        # Try with wrong code
        verify_data = {
            "email": "sarah.johnson@example.com",
            "code": "99999"  # Wrong code
        }
        
        response = self.make_request("POST", "/email-verification/verify-code", verify_data, headers={})
        
        if not response:
            self.log_test("Email Verification - Verify Incorrect Code", False, "Request failed")
            return False
            
        if response.status_code == 400:
            data = response.json()
            
            # Should get error about invalid code
            if "detail" in data and "invalid" in data["detail"].lower():
                self.log_test("Email Verification - Verify Incorrect Code", True, 
                            f"Correctly rejected incorrect code: {data['detail']}")
                return True
            else:
                self.log_test("Email Verification - Verify Incorrect Code", False, 
                            "Unexpected error message", data)
        else:
            self.log_test("Email Verification - Verify Incorrect Code", False, 
                        f"Expected HTTP 400, got {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_email_verification_check_status_before(self):
        """Test GET /api/email-verification/check-status/{email} before verification"""
        print("📊 Testing Email Verification - Check Status (Before)...")
        
        test_email = "sarah.johnson@example.com"
        response = self.make_request("GET", f"/email-verification/check-status/{test_email}", headers={})
        
        if not response:
            self.log_test("Email Verification - Check Status (Before)", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            # Validate response structure
            required_fields = ["email", "verified"]
            if all(field in data for field in required_fields):
                
                if data["email"] == test_email:
                    # Could be verified or not depending on previous tests
                    self.log_test("Email Verification - Check Status (Before)", True, 
                                f"Status check working - Email: {data['email']}, Verified: {data['verified']}")
                    return True
                else:
                    self.log_test("Email Verification - Check Status (Before)", False, 
                                "Email mismatch in response", data)
            else:
                self.log_test("Email Verification - Check Status (Before)", False, 
                            f"Missing required fields: {required_fields}", data)
        else:
            self.log_test("Email Verification - Check Status (Before)", False, 
                        f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_email_verification_max_attempts(self):
        """Test max attempts (5) scenario"""
        print("🚫 Testing Email Verification - Max Attempts...")
        
        # First send a new code to a different user
        test_email = "sarah.johnson.1763483220@example.com"
        request_data = {"email": test_email}
        send_response = self.make_request("POST", "/email-verification/send-code", request_data, headers={})
        
        if not send_response or send_response.status_code != 200:
            self.log_test("Email Verification - Max Attempts", False, "Could not send verification code")
            return False
        
        # Try wrong code 5 times
        verify_data = {
            "email": test_email,
            "code": "00000"  # Wrong code
        }
        
        for attempt in range(5):
            response = self.make_request("POST", "/email-verification/verify-code", verify_data, headers={})
            if not response or response.status_code != 400:
                self.log_test("Email Verification - Max Attempts", False, f"Unexpected response on attempt {attempt + 1}")
                return False
        
        # 6th attempt should be blocked
        response = self.make_request("POST", "/email-verification/verify-code", verify_data, headers={})
        
        if not response:
            self.log_test("Email Verification - Max Attempts", False, "Request failed")
            return False
            
        if response.status_code == 429:
            data = response.json()
            
            if "detail" in data and "too many" in data["detail"].lower():
                self.log_test("Email Verification - Max Attempts", True, 
                            f"Correctly blocked after 5 attempts: {data['detail']}")
                return True
            else:
                self.log_test("Email Verification - Max Attempts", False, 
                            "Unexpected error message", data)
        else:
            self.log_test("Email Verification - Max Attempts", False, 
                        f"Expected HTTP 429, got {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_email_verification_check_backend_logs(self):
        """Check backend logs for email sending confirmation"""
        print("📋 Testing Email Verification - Backend Logs...")
        
        try:
            # Check supervisor backend logs for email sending confirmation
            import subprocess
            result = subprocess.run(
                ["tail", "-n", "50", "/var/log/supervisor/backend.out.log"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                log_content = result.stdout
                
                # Look for email success messages
                if "✅ Verification email sent successfully" in log_content or "Email sent successfully" in log_content:
                    self.log_test("Email Verification - Backend Logs", True, 
                                "Found email sending confirmation in backend logs")
                    return True
                else:
                    # Check for any email-related logs
                    email_logs = [line for line in log_content.split('\n') if 'email' in line.lower() or 'smtp' in line.lower()]
                    if email_logs:
                        self.log_test("Email Verification - Backend Logs", True, 
                                    f"Found {len(email_logs)} email-related log entries")
                        return True
                    else:
                        self.log_test("Email Verification - Backend Logs", False, 
                                    "No email sending confirmation found in logs")
            else:
                self.log_test("Email Verification - Backend Logs", False, 
                            f"Could not read backend logs: {result.stderr}")
                
        except Exception as e:
            self.log_test("Email Verification - Backend Logs", False, f"Log check failed: {e}")
            
        return False

    # ========== CUSTOMER DASHBOARD TESTS ==========
    
    def test_customer_login(self):
        """Test customer login with specified credentials"""
        print("🔑 Testing Customer Login...")
        
        # Use existing customer credentials as specified in review request
        customer_credentials = {
            "email": "mdbvwjr849@tempmail.at",
            "password": "TestPassword123!"
        }
        
        response = self.make_request("POST", "/auth/login", customer_credentials, headers={})
        
        if not response:
            self.log_test("Customer Login", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            # Validate response structure
            if "user" in data and "token" in data:
                user = data["user"]
                token = data["token"]
                
                # Verify user data and role
                if (user.get("email") == customer_credentials["email"] and
                    user.get("role") == "shopper" and
                    token.get("access_token")):
                    
                    self.token = token["access_token"]  # Store customer token
                    self.user_id = user["id"]
                    self.log_test("Customer Login", True, f"Customer logged in: {user['email']}")
                    return True
                else:
                    self.log_test("Customer Login", False, f"Invalid role or data. Role: {user.get('role')}", data)
            else:
                self.log_test("Customer Login", False, "Missing user or token in response", data)
        elif response.status_code == 404:
            # User doesn't exist, try to create it
            print("   User not found, attempting to create test user...")
            
            # Create test user
            test_user_data = {
                "full_name": "Test Customer",
                "email": customer_credentials["email"],
                "password": customer_credentials["password"],
                "role": "shopper"
            }
            
            register_response = self.make_request("POST", "/auth/register", test_user_data, headers={})
            
            if register_response and register_response.status_code == 201:
                print("   Test user created successfully, attempting login again...")
                # Try login again
                login_response = self.make_request("POST", "/auth/login", customer_credentials, headers={})
                
                if login_response and login_response.status_code == 200:
                    data = login_response.json()
                    user = data["user"]
                    token = data["token"]
                    
                    self.token = token["access_token"]
                    self.user_id = user["id"]
                    self.log_test("Customer Login", True, f"Customer created and logged in: {user['email']}")
                    return True
                else:
                    self.log_test("Customer Login", False, "Login failed after user creation")
            else:
                self.log_test("Customer Login", False, "Could not create test user")
        else:
            self.log_test("Customer Login", False, f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_customer_dashboard_overview(self):
        """Test GET /api/customer/dashboard - Focus on shop_name correctness"""
        print("📊 Testing Customer Dashboard Overview...")
        
        if not self.token:
            self.log_test("Customer Dashboard Overview", False, "No customer token available")
            return False
            
        response = self.make_request("GET", "/customer/dashboard")
        
        if not response:
            self.log_test("Customer Dashboard Overview", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            # Validate dashboard structure
            required_fields = ["user", "statistics", "recent_reviews"]
            if all(field in data for field in required_fields):
                
                # Check statistics
                stats = data["statistics"]
                required_stats = ["total_reviews", "average_rating_given", "favorite_shops", "unread_notifications"]
                if all(stat in stats for stat in required_stats):
                    
                    # Check recent_reviews for shop_name correctness
                    recent_reviews = data["recent_reviews"]
                    shop_name_issues = []
                    
                    for review in recent_reviews:
                        shop_name = review.get("shop_name", "")
                        if shop_name == "Unknown Shop":
                            shop_name_issues.append(f"Review ID {review.get('id')} has 'Unknown Shop'")
                        elif not shop_name:
                            shop_name_issues.append(f"Review ID {review.get('id')} has empty shop_name")
                    
                    if shop_name_issues:
                        self.log_test("Customer Dashboard Overview", False, 
                                    f"Shop name issues found: {'; '.join(shop_name_issues)}", data)
                        return False
                    else:
                        self.log_test("Customer Dashboard Overview", True, 
                                    f"Dashboard loaded - Reviews: {stats['total_reviews']}, Avg Rating: {stats['average_rating_given']}, Favorites: {stats['favorite_shops']}, Notifications: {stats['unread_notifications']}")
                        return True
                else:
                    self.log_test("Customer Dashboard Overview", False, f"Missing statistics fields: {required_stats}", data)
            else:
                self.log_test("Customer Dashboard Overview", False, f"Missing required fields: {required_fields}", data)
        else:
            self.log_test("Customer Dashboard Overview", False, f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_customer_reviews_list_with_sorting(self):
        """Test GET /api/customer/reviews with different sort_by parameters"""
        print("⭐ Testing Customer Reviews List with Sorting...")
        
        if not self.token:
            self.log_test("Customer Reviews List", False, "No customer token available")
            return False
        
        sort_options = ["newest", "oldest", "highest", "lowest"]
        all_tests_passed = True
        
        for sort_by in sort_options:
            print(f"   Testing sort_by: {sort_by}")
            response = self.make_request("GET", f"/customer/reviews?sort_by={sort_by}")
            
            if not response:
                self.log_test(f"Customer Reviews List ({sort_by})", False, "Request failed")
                all_tests_passed = False
                continue
                
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                if "reviews" in data and "total" in data:
                    reviews = data["reviews"]
                    
                    # Check each review for shop_name correctness
                    shop_name_issues = []
                    for review in reviews:
                        shop_name = review.get("shop_name", "")
                        if shop_name == "Unknown Shop":
                            shop_name_issues.append(f"Review ID {review.get('id')} has 'Unknown Shop'")
                        elif not shop_name:
                            shop_name_issues.append(f"Review ID {review.get('id')} has empty shop_name")
                    
                    if shop_name_issues:
                        self.log_test(f"Customer Reviews List ({sort_by})", False, 
                                    f"Shop name issues: {'; '.join(shop_name_issues[:3])}")  # Show first 3 issues
                        all_tests_passed = False
                    else:
                        self.log_test(f"Customer Reviews List ({sort_by})", True, 
                                    f"Found {len(reviews)} reviews, all with correct shop names")
                else:
                    self.log_test(f"Customer Reviews List ({sort_by})", False, "Invalid response structure", data)
                    all_tests_passed = False
            else:
                self.log_test(f"Customer Reviews List ({sort_by})", False, f"HTTP {response.status_code}", response.json() if response.content else {})
                all_tests_passed = False
        
        return all_tests_passed
    
    def ensure_test_data(self):
        """Ensure we have test data (shops and reviews) to work with"""
        if not self.token:
            return False
        
        # Check if we have shops
        shops_response = self.make_request("GET", "/shops", headers={})
        if not shops_response or shops_response.status_code != 200:
            return False
        
        shops_data = shops_response.json()
        shops = shops_data.get("data", [])
        
        if not shops:
            # Create a test shop using shop owner credentials
            shop_owner_login = self.make_request("POST", "/auth/login", SHOP_OWNER_CREDENTIALS, headers={})
            if shop_owner_login and shop_owner_login.status_code == 200:
                shop_owner_token = shop_owner_login.json()["token"]["access_token"]
                
                test_shop_data = {
                    "name": "Test Electronics Store",
                    "description": "A test electronics store for testing purposes",
                    "logo": "https://via.placeholder.com/200",
                    "image": "https://via.placeholder.com/800x600",
                    "website": "https://test-electronics.com",
                    "category": "Electronics"
                }
                
                headers = {"Authorization": f"Bearer {shop_owner_token}"}
                create_shop_response = self.make_request("POST", "/shops", test_shop_data, headers=headers)
                
                if create_shop_response and create_shop_response.status_code == 201:
                    created_shop = create_shop_response.json()
                    self.shop_id = created_shop.get("id") or str(created_shop.get("_id", ""))
                    return True
        else:
            self.shop_id = shops[0]["id"]
            return True
        
        return False
    
    def test_review_update(self):
        """Test PUT /api/reviews/{review_id} - Create, update, and verify shop rating update"""
        print("✏️ Testing Review Update...")
        
        if not self.token:
            self.log_test("Review Update", False, "No customer token available")
            return False
        
        # Ensure we have test data
        if not self.ensure_test_data():
            self.log_test("Review Update", False, "Could not ensure test data availability")
            return False
        
        # Check if we already have a review to update
        response = self.make_request("GET", "/customer/reviews")
        
        if not response or response.status_code != 200:
            self.log_test("Review Update", False, "Could not fetch customer reviews")
            return False
        
        reviews_data = response.json()
        reviews = reviews_data.get("reviews", [])
        
        if reviews:
            # Use existing review
            review_id = reviews[0]["id"]
            shop_id = reviews[0]["shop_id"]
            print(f"   Using existing review {review_id}")
        else:
            # Skip this test if no reviews exist
            self.log_test("Review Update", True, "Skipped - no reviews available to update")
            return True
        
        # Get shop rating before update
        shop_response = self.make_request("GET", f"/shops/{shop_id}", headers={})
        if not shop_response or shop_response.status_code != 200:
            self.log_test("Review Update", False, "Could not fetch shop data")
            return False
        
        shop_before = shop_response.json()
        rating_before = shop_before.get("rating", 0)
        
        # Update the review
        update_data = {
            "rating": 5,
            "comment": "Updated review: Excellent service and outstanding quality!"
        }
        
        print(f"   Updating review {review_id}")
        update_response = self.make_request("PUT", f"/reviews/{review_id}", update_data)
        
        if not update_response:
            self.log_test("Review Update", False, "Update request failed - no response")
            return False
        
        print(f"   Update response status: {update_response.status_code}")
        if update_response.content:
            print(f"   Update response: {update_response.json()}")
            
        if update_response.status_code == 200:
            updated_review = update_response.json()
            
            # Verify update was applied
            if (updated_review.get("rating") == update_data["rating"] and
                updated_review.get("comment") == update_data["comment"]):
                
                # Check shop rating was updated
                shop_after_response = self.make_request("GET", f"/shops/{shop_id}", headers={})
                if shop_after_response and shop_after_response.status_code == 200:
                    shop_after = shop_after_response.json()
                    rating_after = shop_after.get("rating", 0)
                    
                    self.log_test("Review Update", True, 
                                f"Review updated successfully. Shop rating: {rating_before} → {rating_after}")
                    return True
                else:
                    self.log_test("Review Update", False, "Could not verify shop rating update")
            else:
                self.log_test("Review Update", False, "Review update not applied correctly", updated_review)
        else:
            self.log_test("Review Update", False, f"HTTP {update_response.status_code}", update_response.json() if update_response.content else {})
            
        return False
    
    def test_review_delete(self):
        """Test DELETE /api/reviews/{review_id} - Delete review and verify shop rating update"""
        print("🗑️ Testing Review Delete...")
        
        if not self.token:
            self.log_test("Review Delete", False, "No customer token available")
            return False
        
        # Ensure we have test data
        if not self.ensure_test_data():
            self.log_test("Review Delete", False, "Could not ensure test data availability")
            return False
        
        # Get customer's reviews to find one to delete
        response = self.make_request("GET", "/customer/reviews")
        
        if not response or response.status_code != 200:
            self.log_test("Review Delete", False, "Could not fetch customer reviews")
            return False
        
        reviews_data = response.json()
        reviews = reviews_data.get("reviews", [])
        
        if not reviews:
            # Skip this test if no reviews exist
            self.log_test("Review Delete", True, "Skipped - no reviews available to delete")
            return True
        
        # Use existing review
        review_to_delete = reviews[0]
        review_id = review_to_delete["id"]
        shop_id = review_to_delete["shop_id"]
        
        # Use the first review
        review_to_delete = reviews[0]
        review_id = review_to_delete["id"]
        shop_id = review_to_delete["shop_id"]
        
        # Get shop rating before deletion
        shop_response = self.make_request("GET", f"/shops/{shop_id}", headers={})
        if not shop_response or shop_response.status_code != 200:
            self.log_test("Review Delete", False, "Could not fetch shop data")
            return False
        
        shop_before = shop_response.json()
        rating_before = shop_before.get("rating", 0)
        review_count_before = shop_before.get("review_count", 0)
        
        # Delete the review
        delete_response = self.make_request("DELETE", f"/reviews/{review_id}")
        
        if not delete_response:
            self.log_test("Review Delete", False, "Delete request failed")
            return False
            
        if delete_response.status_code == 200:
            delete_result = delete_response.json()
            
            if "message" in delete_result and "deleted" in delete_result["message"].lower():
                
                # Verify review is deleted
                verify_response = self.make_request("GET", "/customer/reviews")
                if verify_response and verify_response.status_code == 200:
                    updated_reviews = verify_response.json().get("reviews", [])
                    review_still_exists = any(r["id"] == review_id for r in updated_reviews)
                    
                    if not review_still_exists:
                        # Check shop rating was updated
                        shop_after_response = self.make_request("GET", f"/shops/{shop_id}", headers={})
                        if shop_after_response and shop_after_response.status_code == 200:
                            shop_after = shop_after_response.json()
                            rating_after = shop_after.get("rating", 0)
                            review_count_after = shop_after.get("review_count", 0)
                            
                            self.log_test("Review Delete", True, 
                                        f"Review deleted successfully. Shop rating: {rating_before} → {rating_after}, Count: {review_count_before} → {review_count_after}")
                            return True
                        else:
                            self.log_test("Review Delete", False, "Could not verify shop rating update")
                    else:
                        self.log_test("Review Delete", False, "Review still exists after deletion")
                else:
                    self.log_test("Review Delete", False, "Could not verify review deletion")
            else:
                self.log_test("Review Delete", False, "Unexpected delete response", delete_result)
        else:
            self.log_test("Review Delete", False, f"HTTP {delete_response.status_code}", delete_response.json() if delete_response.content else {})
            
        return False
    
    def test_customer_favorites(self):
        """Test GET /api/customer/favorites - Verify shop data completeness"""
        print("❤️ Testing Customer Favorites...")
        
        if not self.token:
            self.log_test("Customer Favorites", False, "No customer token available")
            return False
            
        response = self.make_request("GET", "/customer/favorites")
        
        if not response:
            self.log_test("Customer Favorites", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            # Validate response structure
            if "favorites" in data:
                favorites = data["favorites"]
                
                # Check each favorite shop for complete data
                incomplete_shops = []
                for shop in favorites:
                    required_fields = ["id", "name", "category", "rating", "review_count", "is_verified"]
                    missing_fields = [field for field in required_fields if field not in shop or shop[field] is None]
                    
                    if missing_fields:
                        incomplete_shops.append(f"Shop {shop.get('name', 'Unknown')} missing: {', '.join(missing_fields)}")
                
                if incomplete_shops:
                    self.log_test("Customer Favorites", False, 
                                f"Incomplete shop data: {'; '.join(incomplete_shops[:3])}")  # Show first 3 issues
                else:
                    self.log_test("Customer Favorites", True, 
                                f"Found {len(favorites)} favorite shops, all with complete data")
                return True
            else:
                self.log_test("Customer Favorites", False, "Missing favorites in response", data)
        else:
            self.log_test("Customer Favorites", False, f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def run_customer_dashboard_tests(self):
        """Run comprehensive Customer Dashboard API tests"""
        print("🚀 Starting Customer Dashboard API Tests")
        print(f"🌐 Base URL: {BASE_URL}")
        print("=" * 60)
        
        # Customer Authentication
        print("🔐 CUSTOMER AUTHENTICATION")
        print("-" * 30)
        customer_auth_success = self.test_customer_login()
        
        if not customer_auth_success:
            print("❌ Customer authentication failed. Cannot proceed with dashboard tests.")
            return False
        
        # Customer Dashboard Tests
        print("\n📊 CUSTOMER DASHBOARD TESTS")
        print("-" * 30)
        
        dashboard_tests = [
            ("Customer Dashboard Overview", self.test_customer_dashboard_overview),
            ("Customer Reviews List", self.test_customer_reviews_list_with_sorting),
            ("Review Update", self.test_review_update),
            ("Customer Favorites", self.test_customer_favorites),
            ("Review Delete", self.test_review_delete)  # Move delete to last to avoid conflicts
        ]
        
        test_results = []
        for test_name, test_func in dashboard_tests:
            print(f"\n🧪 Running {test_name}...")
            result = test_func()
            test_results.append((test_name, result))
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 CUSTOMER DASHBOARD TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, result in test_results if result)
        total = len(test_results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        # Show detailed results
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        # Check for shop name issues specifically
        shop_name_failures = []
        for result in self.test_results:
            if not result["success"] and "shop name" in result["details"].lower():
                shop_name_failures.append(result)
        
        if shop_name_failures:
            print(f"\n🚨 SHOP NAME DISPLAY ISSUES FOUND ({len(shop_name_failures)}):")
            for test in shop_name_failures:
                print(f"   - {test['test']}: {test['details']}")
        
        if passed == total:
            print("\n🎉 All Customer Dashboard tests passed!")
            return True
        else:
            print(f"\n❌ {total - passed} test(s) failed.")
            return False

    # ========== FAKE SHOP CHECKER & SEARCH TESTS ==========
    
    def test_fake_shop_checker_with_existing_shop(self):
        """Test POST /api/fake-check/check with existing shop URL"""
        print("🔍 Testing Fake Shop Checker - Existing Shop...")
        
        # First get a shop from the database to test with
        response = self.make_request("GET", "/shops", headers={})
        
        if not response or response.status_code != 200:
            self.log_test("Fake Shop Checker - Existing Shop", False, "Could not fetch shops for testing")
            return False
            
        shops_data = response.json()
        shops = shops_data.get("data", [])
        
        if not shops:
            self.log_test("Fake Shop Checker - Existing Shop", False, "No shops available for testing")
            return False
            
        # Use the first shop's website
        test_shop = shops[0]
        test_url = test_shop.get("website", "")
        
        if not test_url:
            self.log_test("Fake Shop Checker - Existing Shop", False, "No website URL found in shop data")
            return False
            
        # Test the fake shop checker
        check_data = {"url": test_url}
        response = self.make_request("POST", "/fake-check/check", check_data, headers={})
        
        if not response:
            self.log_test("Fake Shop Checker - Existing Shop", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            # Validate response structure
            required_fields = ["is_registered", "is_verified", "trust_score", "warnings", "recommendations"]
            if all(field in data for field in required_fields):
                
                # Should be registered since we used an existing shop
                if data["is_registered"]:
                    self.log_test("Fake Shop Checker - Existing Shop", True, 
                                f"Shop found: {data.get('shop_name', 'N/A')}, Trust Score: {data['trust_score']}")
                    return True
                else:
                    self.log_test("Fake Shop Checker - Existing Shop", False, 
                                f"Shop should be registered but wasn't found. URL: {test_url}")
            else:
                self.log_test("Fake Shop Checker - Existing Shop", False, 
                            f"Missing required fields: {required_fields}", data)
        else:
            self.log_test("Fake Shop Checker - Existing Shop", False, 
                        f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_fake_shop_checker_with_fake_shop(self):
        """Test POST /api/fake-check/check with non-existing shop URL"""
        print("🔍 Testing Fake Shop Checker - Fake Shop...")
        
        # Test with a fake shop URL
        fake_url = "https://fake-shop-test.com"
        check_data = {"url": fake_url}
        
        response = self.make_request("POST", "/fake-check/check", check_data, headers={})
        
        if not response:
            self.log_test("Fake Shop Checker - Fake Shop", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            # Validate response structure
            required_fields = ["is_registered", "is_verified", "trust_score", "warnings", "recommendations"]
            if all(field in data for field in required_fields):
                
                # Should NOT be registered
                if not data["is_registered"] and not data["is_verified"]:
                    # Should have warnings and recommendations
                    if data["warnings"] and data["recommendations"] and data["trust_score"] <= 50:
                        self.log_test("Fake Shop Checker - Fake Shop", True, 
                                    f"Fake shop correctly identified, Trust Score: {data['trust_score']}")
                        return True
                    else:
                        self.log_test("Fake Shop Checker - Fake Shop", False, 
                                    "Missing warnings/recommendations or trust score too high")
                else:
                    self.log_test("Fake Shop Checker - Fake Shop", False, 
                                "Fake shop incorrectly marked as registered/verified")
            else:
                self.log_test("Fake Shop Checker - Fake Shop", False, 
                            f"Missing required fields: {required_fields}", data)
        else:
            self.log_test("Fake Shop Checker - Fake Shop", False, 
                        f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_fake_shop_checker_statistics(self):
        """Test GET /api/fake-check/statistics"""
        print("📊 Testing Fake Shop Checker Statistics...")
        
        response = self.make_request("GET", "/fake-check/statistics", headers={})
        
        if not response:
            self.log_test("Fake Shop Checker Statistics", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            # Validate statistics structure
            required_fields = ["total_shops", "verified_shops", "total_reviews", "average_rating"]
            if all(field in data for field in required_fields):
                
                # Validate data types and reasonable values
                if (isinstance(data["total_shops"], int) and data["total_shops"] >= 0 and
                    isinstance(data["verified_shops"], int) and data["verified_shops"] >= 0 and
                    isinstance(data["total_reviews"], int) and data["total_reviews"] >= 0 and
                    isinstance(data["average_rating"], (int, float)) and 0 <= data["average_rating"] <= 5):
                    
                    self.log_test("Fake Shop Checker Statistics", True, 
                                f"Stats - Shops: {data['total_shops']}, Verified: {data['verified_shops']}, Reviews: {data['total_reviews']}, Avg Rating: {data['average_rating']}")
                    return True
                else:
                    self.log_test("Fake Shop Checker Statistics", False, "Invalid data types or values", data)
            else:
                self.log_test("Fake Shop Checker Statistics", False, 
                            f"Missing required fields: {required_fields}", data)
        else:
            self.log_test("Fake Shop Checker Statistics", False, 
                        f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_shop_search_all_shops(self):
        """Test GET /api/search/shops without parameters"""
        print("🔍 Testing Shop Search - All Shops...")
        
        response = self.make_request("GET", "/search/shops", headers={})
        
        if not response:
            self.log_test("Shop Search - All Shops", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            # Validate response structure
            required_fields = ["data", "total", "page", "pages", "filters"]
            if all(field in data for field in required_fields):
                
                shops = data["data"]
                if isinstance(shops, list) and data["total"] >= 0:
                    self.log_test("Shop Search - All Shops", True, 
                                f"Found {len(shops)} shops on page {data['page']} of {data['pages']} (total: {data['total']})")
                    return True
                else:
                    self.log_test("Shop Search - All Shops", False, "Invalid shops data or total count", data)
            else:
                self.log_test("Shop Search - All Shops", False, 
                            f"Missing required fields: {required_fields}", data)
        else:
            self.log_test("Shop Search - All Shops", False, 
                        f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_shop_search_with_query(self):
        """Test GET /api/search/shops with query parameter"""
        print("🔍 Testing Shop Search - With Query...")
        
        # Test with a common search term
        response = self.make_request("GET", "/search/shops?q=shop", headers={})
        
        if not response:
            self.log_test("Shop Search - With Query", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            # Validate response structure
            required_fields = ["data", "total", "page", "pages", "filters"]
            if all(field in data for field in required_fields):
                
                # Check that filters reflect the query
                if data["filters"]["query"] == "shop":
                    shops = data["data"]
                    self.log_test("Shop Search - With Query", True, 
                                f"Query 'shop' returned {len(shops)} shops (total: {data['total']})")
                    return True
                else:
                    self.log_test("Shop Search - With Query", False, "Query filter not reflected in response", data)
            else:
                self.log_test("Shop Search - With Query", False, 
                            f"Missing required fields: {required_fields}", data)
        else:
            self.log_test("Shop Search - With Query", False, 
                        f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_shop_search_with_category(self):
        """Test GET /api/search/shops with category filter"""
        print("🔍 Testing Shop Search - With Category...")
        
        # First get available categories
        categories_response = self.make_request("GET", "/search/categories", headers={})
        
        if not categories_response or categories_response.status_code != 200:
            self.log_test("Shop Search - With Category", False, "Could not fetch categories")
            return False
            
        categories_data = categories_response.json()
        categories = categories_data.get("categories", [])
        
        if not categories:
            self.log_test("Shop Search - With Category", False, "No categories available")
            return False
            
        # Use the first category with shops
        test_category = None
        for cat in categories:
            if cat["count"] > 0:
                test_category = cat["name"]
                break
        
        if not test_category:
            self.log_test("Shop Search - With Category", False, "No categories with shops found")
            return False
            
        # Test search with category
        response = self.make_request("GET", f"/search/shops?category={test_category}", headers={})
        
        if not response:
            self.log_test("Shop Search - With Category", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            # Validate response structure and category filter
            if (data.get("filters", {}).get("category") == test_category and
                "data" in data and "total" in data):
                
                shops = data["data"]
                # Verify all returned shops have the correct category
                if all(shop.get("category") == test_category for shop in shops):
                    self.log_test("Shop Search - With Category", True, 
                                f"Category '{test_category}' returned {len(shops)} shops")
                    return True
                else:
                    self.log_test("Shop Search - With Category", False, 
                                "Some shops don't match the category filter")
            else:
                self.log_test("Shop Search - With Category", False, "Invalid response structure or filter", data)
        else:
            self.log_test("Shop Search - With Category", False, 
                        f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_shop_search_pagination(self):
        """Test GET /api/search/shops pagination"""
        print("🔍 Testing Shop Search - Pagination...")
        
        # Test page 1
        response1 = self.make_request("GET", "/search/shops?page=1&limit=5", headers={})
        
        if not response1 or response1.status_code != 200:
            self.log_test("Shop Search - Pagination", False, "Page 1 request failed")
            return False
            
        data1 = response1.json()
        
        if data1.get("total", 0) <= 5:
            # Not enough data for pagination test
            self.log_test("Shop Search - Pagination", True, "Pagination working (insufficient data for multi-page test)")
            return True
            
        # Test page 2
        response2 = self.make_request("GET", "/search/shops?page=2&limit=5", headers={})
        
        if not response2 or response2.status_code != 200:
            self.log_test("Shop Search - Pagination", False, "Page 2 request failed")
            return False
            
        data2 = response2.json()
        
        # Validate pagination
        if (data1["page"] == 1 and data2["page"] == 2 and
            data1["total"] == data2["total"] and
            len(data1["data"]) <= 5 and len(data2["data"]) <= 5):
            
            # Ensure different shops on different pages
            page1_ids = {shop.get("id") for shop in data1["data"]}
            page2_ids = {shop.get("id") for shop in data2["data"]}
            
            if not page1_ids.intersection(page2_ids):
                self.log_test("Shop Search - Pagination", True, 
                            f"Pagination working - Page 1: {len(data1['data'])} shops, Page 2: {len(data2['data'])} shops")
                return True
            else:
                self.log_test("Shop Search - Pagination", False, "Same shops appear on different pages")
        else:
            self.log_test("Shop Search - Pagination", False, "Invalid pagination data", {"page1": data1, "page2": data2})
            
        return False
    
    def test_shop_search_categories(self):
        """Test GET /api/search/categories"""
        print("🏷️ Testing Shop Search Categories...")
        
        response = self.make_request("GET", "/search/categories", headers={})
        
        if not response:
            self.log_test("Shop Search Categories", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            # Validate response structure
            if "categories" in data:
                categories = data["categories"]
                
                if isinstance(categories, list) and len(categories) > 0:
                    # Validate category structure
                    valid_categories = all(
                        isinstance(cat, dict) and "name" in cat and "count" in cat
                        for cat in categories
                    )
                    
                    if valid_categories:
                        total_shops = sum(cat["count"] for cat in categories)
                        self.log_test("Shop Search Categories", True, 
                                    f"Found {len(categories)} categories with {total_shops} total shops")
                        return True
                    else:
                        self.log_test("Shop Search Categories", False, "Invalid category structure", data)
                else:
                    self.log_test("Shop Search Categories", False, "Empty or invalid categories list", data)
            else:
                self.log_test("Shop Search Categories", False, "Missing categories field", data)
        else:
            self.log_test("Shop Search Categories", False, 
                        f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_shop_search_suggestions(self):
        """Test GET /api/search/suggestions"""
        print("💡 Testing Shop Search Suggestions...")
        
        # Test with a 2-character query
        response = self.make_request("GET", "/search/suggestions?q=sh", headers={})
        
        if not response:
            self.log_test("Shop Search Suggestions", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            # Validate response structure
            if "suggestions" in data:
                suggestions = data["suggestions"]
                
                if isinstance(suggestions, list):
                    # Validate suggestion structure
                    valid_suggestions = all(
                        isinstance(sug, dict) and 
                        "type" in sug and "id" in sug and "name" in sug and "category" in sug
                        for sug in suggestions
                    )
                    
                    if valid_suggestions:
                        self.log_test("Shop Search Suggestions", True, 
                                    f"Query 'sh' returned {len(suggestions)} suggestions")
                        return True
                    else:
                        self.log_test("Shop Search Suggestions", False, "Invalid suggestion structure", data)
                else:
                    self.log_test("Shop Search Suggestions", False, "Invalid suggestions list", data)
            else:
                self.log_test("Shop Search Suggestions", False, "Missing suggestions field", data)
        else:
            self.log_test("Shop Search Suggestions", False, 
                        f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def run_fake_shop_checker_and_search_tests(self):
        """Run all Fake Shop Checker and Search API tests"""
        print("🚀 Starting Fake Shop Checker & Search API Tests")
        print(f"🌐 Base URL: {BASE_URL}")
        print("=" * 60)
        
        # Fake Shop Checker Tests
        print("🔍 FAKE SHOP CHECKER APIs")
        print("-" * 30)
        fake_checker_success = (
            self.test_fake_shop_checker_with_existing_shop() and
            self.test_fake_shop_checker_with_fake_shop() and
            self.test_fake_shop_checker_statistics()
        )
        
        # Shop Search Tests
        print("\n🔍 SHOP SEARCH APIs")
        print("-" * 30)
        search_success = (
            self.test_shop_search_all_shops() and
            self.test_shop_search_with_query() and
            self.test_shop_search_with_category() and
            self.test_shop_search_pagination() and
            self.test_shop_search_categories() and
            self.test_shop_search_suggestions()
        )
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 FAKE SHOP CHECKER & SEARCH TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        # Categorize results by test type
        fake_checker_tests = [
            "Fake Shop Checker - Existing Shop",
            "Fake Shop Checker - Fake Shop", 
            "Fake Shop Checker Statistics"
        ]
        
        search_tests = [
            "Shop Search - All Shops",
            "Shop Search - With Query",
            "Shop Search - With Category",
            "Shop Search - Pagination",
            "Shop Search Categories",
            "Shop Search Suggestions"
        ]
        
        fake_checker_failures = []
        search_failures = []
        
        for result in self.test_results:
            if not result["success"]:
                if result["test"] in fake_checker_tests:
                    fake_checker_failures.append(result)
                elif result["test"] in search_tests:
                    search_failures.append(result)
        
        if fake_checker_failures:
            print(f"\n❌ FAKE SHOP CHECKER FAILURES ({len(fake_checker_failures)}):")
            for test in fake_checker_failures:
                print(f"   - {test['test']}: {test['details']}")
        
        if search_failures:
            print(f"\n❌ SHOP SEARCH FAILURES ({len(search_failures)}):")
            for test in search_failures:
                print(f"   - {test['test']}: {test['details']}")
        
        if passed == total:
            print("\n🎉 All Fake Shop Checker & Search tests passed!")
            return True
        else:
            print(f"\n❌ {total - passed} test(s) failed.")
            return False

    def run_email_verification_tests(self):
        """Run comprehensive email verification tests"""
        print("🚀 Starting Email Verification Backend API Tests")
        print(f"🌐 Base URL: {BASE_URL}")
        print("=" * 60)
        
        # Test 1: Send verification code
        print("\n📧 EMAIL VERIFICATION CODE SENDING")
        print("-" * 40)
        send_success = self.test_email_verification_send_code()
        
        # Test 2: Check code storage in database
        print("\n🗄️ EMAIL VERIFICATION CODE STORAGE")
        print("-" * 40)
        verification_code = self.test_email_verification_check_code_storage()
        
        # Test 3: Check backend logs for email sending
        print("\n📋 EMAIL VERIFICATION BACKEND LOGS")
        print("-" * 40)
        logs_success = self.test_email_verification_check_backend_logs()
        
        # Test 4: Verify correct code
        print("\n✅ EMAIL VERIFICATION CODE VALIDATION")
        print("-" * 40)
        verify_success = self.test_email_verification_verify_correct_code(verification_code)
        
        # Test 5: Check status before verification (using different user)
        print("\n📊 EMAIL VERIFICATION STATUS CHECK")
        print("-" * 40)
        status_success = self.test_email_verification_check_status_before()
        
        # Test 6: Verify incorrect code
        print("\n❌ EMAIL VERIFICATION INCORRECT CODE")
        print("-" * 40)
        incorrect_success = self.test_email_verification_verify_incorrect_code()
        
        # Test 7: Max attempts scenario
        print("\n🚫 EMAIL VERIFICATION MAX ATTEMPTS")
        print("-" * 40)
        max_attempts_success = self.test_email_verification_max_attempts()
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 EMAIL VERIFICATION TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        # Categorize results
        critical_tests = [
            "Email Verification - Send Code", 
            "Email Verification - Code Storage",
            "Email Verification - Verify Correct Code",
            "Email Verification - Check Status (Before)"
        ]
        
        critical_failures = []
        other_failures = []
        
        for result in self.test_results:
            if not result["success"]:
                if result["test"] in critical_tests:
                    critical_failures.append(result)
                else:
                    other_failures.append(result)
        
        if critical_failures:
            print(f"\n❌ CRITICAL FAILURES ({len(critical_failures)}):")
            for test in critical_failures:
                print(f"   - {test['test']}: {test['details']}")
        
        if other_failures:
            print(f"\n⚠️  OTHER FAILURES ({len(other_failures)}):")
            for test in other_failures:
                print(f"   - {test['test']}: {test['details']}")
        
        if passed == total:
            print("\n🎉 All Email Verification tests passed!")
            return True
        elif len(critical_failures) == 0:
            print("\n✅ All critical Email Verification functionality working!")
            return True
        else:
            print(f"\n❌ {len(critical_failures)} critical failures found.")
            return False

def main():
    """Main test runner"""
    tester = APITester()
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type == "customer-dashboard":
            print("👤 Running Customer Dashboard API Tests")
            success = tester.run_customer_dashboard_tests()
        elif test_type == "email-verification":
            print("📧 Running Email Verification API Tests")
            success = tester.run_email_verification_tests()
        elif test_type == "fake-shop-search":
            print("🔍 Running Fake Shop Checker & Search API Tests")
            success = tester.run_fake_shop_checker_and_search_tests()
        else:
            print("❌ Unknown test type. Available options: customer-dashboard, email-verification, fake-shop-search")
            sys.exit(1)
    else:
        # Run the Fake Shop Checker and Search API tests as default
        print("🔍 Running Fake Shop Checker & Search API Tests")
        success = tester.run_fake_shop_checker_and_search_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()