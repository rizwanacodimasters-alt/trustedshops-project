#!/usr/bin/env python3
"""
Shop Creation Test - Specific test for the review request
Tests shop creation with updated model including all fields and minimal fields
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

class ShopCreationTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = TIMEOUT
        self.shop_owner_token = None
        self.shop_owner_id = None
        self.created_shops = []
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
            return None
    
    def test_shop_owner_login(self):
        """Test 1: Login as shop owner: owner@shop.com / owner123"""
        print("🔑 Test 1: Login as shop owner (owner@shop.com / owner123)")
        
        response = self.make_request("POST", "/auth/login", SHOP_OWNER_CREDENTIALS, headers={})
        
        if not response:
            self.log_test("Shop Owner Login", False, "Request failed")
            return False
            
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
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
            error_data = response.json() if response.content else {}
            self.log_test("Shop Owner Login", False, f"HTTP {response.status_code}", error_data)
            
        return False
    
    def test_create_complete_shop(self):
        """Test 2: Create shop with all fields"""
        print("🏪 Test 2: Create shop with all fields")
        
        if not self.shop_owner_token:
            self.log_test("Create Complete Shop", False, "No shop owner token available")
            return False
        
        # Shop data as specified in review request
        complete_shop_data = {
            "name": "Complete Test Shop",
            "website": "https://complete-test.de",
            "category": "Bekleidung",
            "description": "A test shop with description",
            "email": "shop@test.de",
            "phone": "+49123456789",
            "address": "Test Street 123",
            "logo": "",
            "image": ""
        }
        
        headers = {"Authorization": f"Bearer {self.shop_owner_token}"}
        print(f"Making POST request to {BASE_URL}/shops")
        print(f"Request data: {json.dumps(complete_shop_data, indent=2)}")
        
        response = self.make_request("POST", "/shops", complete_shop_data, headers=headers)
        
        if not response:
            self.log_test("Create Complete Shop", False, "Request failed")
            return False
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Verify response contains shop ID
            shop_id = data.get("id") or str(data.get("_id", ""))
            if shop_id:
                self.created_shops.append({
                    "id": shop_id,
                    "name": complete_shop_data["name"],
                    "type": "complete"
                })
                
                # Verify all fields are present
                fields_match = (
                    data.get("name") == complete_shop_data["name"] and
                    data.get("website") == complete_shop_data["website"] and
                    data.get("category") == complete_shop_data["category"] and
                    data.get("description") == complete_shop_data["description"] and
                    data.get("email") == complete_shop_data["email"] and
                    data.get("phone") == complete_shop_data["phone"] and
                    data.get("address") == complete_shop_data["address"]
                )
                
                if fields_match:
                    self.log_test("Create Complete Shop", True, f"Shop created with ID: {shop_id}, all fields match")
                    return True
                else:
                    self.log_test("Create Complete Shop", False, "Some shop data fields don't match", data)
            else:
                self.log_test("Create Complete Shop", False, "No shop ID found in response", data)
        else:
            error_data = response.json() if response.content else {}
            self.log_test("Create Complete Shop", False, f"HTTP {response.status_code}", error_data)
            
        return False
    
    def test_create_minimal_shop(self):
        """Test 3: Create minimal shop with required fields only"""
        print("🏪 Test 3: Create minimal shop with required fields")
        
        if not self.shop_owner_token:
            self.log_test("Create Minimal Shop", False, "No shop owner token available")
            return False
        
        # Minimal shop data as specified in review request
        minimal_shop_data = {
            "name": "Minimal Shop",
            "website": "https://minimal.de",
            "category": "Baumarkt"
        }
        
        headers = {"Authorization": f"Bearer {self.shop_owner_token}"}
        print(f"Making POST request to {BASE_URL}/shops")
        print(f"Request data: {json.dumps(minimal_shop_data, indent=2)}")
        
        response = self.make_request("POST", "/shops", minimal_shop_data, headers=headers)
        
        if not response:
            self.log_test("Create Minimal Shop", False, "Request failed")
            return False
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Verify response contains shop ID
            shop_id = data.get("id") or str(data.get("_id", ""))
            if shop_id:
                self.created_shops.append({
                    "id": shop_id,
                    "name": minimal_shop_data["name"],
                    "type": "minimal"
                })
                
                # Verify required fields are present
                fields_match = (
                    data.get("name") == minimal_shop_data["name"] and
                    data.get("website") == minimal_shop_data["website"] and
                    data.get("category") == minimal_shop_data["category"]
                )
                
                # Verify optional fields have default values
                optional_fields_ok = (
                    data.get("description") == "" and
                    data.get("email") == "" and
                    data.get("phone") == "" and
                    data.get("address") == "" and
                    data.get("logo") == "" and
                    data.get("image") == ""
                )
                
                if fields_match and optional_fields_ok:
                    self.log_test("Create Minimal Shop", True, f"Minimal shop created with ID: {shop_id}, required fields match, optional fields have defaults")
                    return True
                else:
                    self.log_test("Create Minimal Shop", False, "Required fields don't match or optional fields not defaulted correctly", data)
            else:
                self.log_test("Create Minimal Shop", False, "No shop ID found in response", data)
        else:
            error_data = response.json() if response.content else {}
            self.log_test("Create Minimal Shop", False, f"HTTP {response.status_code}", error_data)
            
        return False
    
    def test_verify_shops_in_dashboard(self):
        """Test 4: Verify shops created via GET /api/dashboard/shop-owner"""
        print("📊 Test 4: Verify shops in dashboard")
        
        if not self.shop_owner_token:
            self.log_test("Verify Shops in Dashboard", False, "No shop owner token available")
            return False
        
        if len(self.created_shops) == 0:
            self.log_test("Verify Shops in Dashboard", False, "No shops were created to verify")
            return False
        
        headers = {"Authorization": f"Bearer {self.shop_owner_token}"}
        print(f"Making GET request to {BASE_URL}/dashboard/shop-owner")
        
        response = self.make_request("GET", "/dashboard/shop-owner", headers=headers)
        
        if not response:
            self.log_test("Verify Shops in Dashboard", False, "Request failed")
            return False
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Dashboard response structure: {list(data.keys())}")
            
            # Check if shops appear in dashboard
            dashboard_shops = data.get("shops", [])
            print(f"Found {len(dashboard_shops)} shops in dashboard")
            
            # Count how many of our created shops are found
            found_shops = 0
            for created_shop in self.created_shops:
                for dashboard_shop in dashboard_shops:
                    if dashboard_shop.get("id") == created_shop["id"]:
                        found_shops += 1
                        print(f"✅ Found {created_shop['type']} shop: {created_shop['name']} (ID: {created_shop['id']})")
                        break
            
            # Check statistics
            stats = data.get("statistics", {})
            total_shops = stats.get("total_shops", 0)
            
            print(f"\nDashboard statistics:")
            print(f"   Total shops: {total_shops}")
            print(f"   Verified shops: {stats.get('verified_shops', 0)}")
            print(f"   Total reviews: {stats.get('total_reviews', 0)}")
            print(f"   Average rating: {stats.get('average_rating', 0)}")
            
            if found_shops == len(self.created_shops):
                self.log_test("Verify Shops in Dashboard", True, f"All {found_shops} created shops found in dashboard. Total shops: {total_shops}")
                return True
            else:
                self.log_test("Verify Shops in Dashboard", False, f"Only {found_shops}/{len(self.created_shops)} created shops found in dashboard")
        else:
            error_data = response.json() if response.content else {}
            self.log_test("Verify Shops in Dashboard", False, f"HTTP {response.status_code}", error_data)
            
        return False
    
    def run_shop_creation_tests(self):
        """Run all shop creation tests as specified in review request"""
        print("🚀 Starting Shop Creation Tests with Updated Model")
        print(f"🌐 Base URL: {BASE_URL}")
        print("=" * 60)
        
        # Test 1: Login as shop owner
        login_success = self.test_shop_owner_login()
        if not login_success:
            print("❌ Shop owner login failed - cannot proceed with shop creation tests")
            return False
        
        print("\n" + "-" * 60)
        
        # Test 2: Create shop with all fields
        complete_shop_success = self.test_create_complete_shop()
        
        print("\n" + "-" * 60)
        
        # Test 3: Create minimal shop
        minimal_shop_success = self.test_create_minimal_shop()
        
        print("\n" + "-" * 60)
        
        # Test 4: Verify shops created
        dashboard_success = self.test_verify_shops_in_dashboard()
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 SHOP CREATION TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        # Show created shops
        if self.created_shops:
            print(f"\n🏪 CREATED SHOPS ({len(self.created_shops)}):")
            for shop in self.created_shops:
                print(f"   - {shop['name']} ({shop['type']}) - ID: {shop['id']}")
        
        # Show failures
        failures = [result for result in self.test_results if not result["success"]]
        if failures:
            print(f"\n❌ FAILURES ({len(failures)}):")
            for test in failures:
                print(f"   - {test['test']}: {test['details']}")
        
        overall_success = passed == total
        if overall_success:
            print("\n🎉 All shop creation tests passed!")
        else:
            print(f"\n❌ {total - passed} test(s) failed.")
        
        return overall_success

def main():
    """Main test runner"""
    tester = ShopCreationTester()
    
    success = tester.run_shop_creation_tests()
    
    if success:
        print("\n✅ Shop Creation Tests PASSED")
    else:
        print("\n❌ Shop Creation Tests FAILED")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()