#!/usr/bin/env python3
"""
Review Submission with Mandatory Evidence Testing
Tests the review creation API endpoint POST /api/reviews with focus on mandatory evidence for low-star reviews (1-3 stars).
"""

import requests
import json
import base64
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://trust-ratings-app.preview.emergentagent.com/api"
TIMEOUT = 30

# Test credentials - will register new user for testing
import time
timestamp = int(time.time())
TEST_USER = {
    "full_name": "Review Tester",
    "email": f"review.tester.{timestamp}@example.com",
    "password": "TestPassword123!",
    "role": "shopper"
}

class ReviewEvidenceAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = TIMEOUT
        self.token = None
        self.user_id = None
        self.shop_id = None
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
            print(f"   Request Exception: {e}")
            print(f"   URL: {url}, Method: {method}")
            return None
    
    def create_test_image_base64(self, size="small"):
        """Create a test image in base64 format"""
        # Create a simple 1x1 pixel PNG image
        if size == "small":
            # 1x1 pixel red PNG
            png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x07\n\xdb\xa8\x00\x00\x00\x00IEND\xaeB`\x82'
        else:
            # Larger test image (still small but bigger than 1x1)
            png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x02\x00\x00\x00\x90\x91h6\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x19IDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x07\n\xdb\xa8\x00\x00\x00\x00IEND\xaeB`\x82'
        
        base64_data = base64.b64encode(png_data).decode('utf-8')
        return f"data:image/png;base64,{base64_data}"
    
    def register_and_login_shopper(self):
        """Register a new shopper user and login"""
        print(f"📝 Registering new shopper: {TEST_USER['email']}")
        
        # Register user
        response = self.make_request("POST", "/auth/register", TEST_USER, headers={})
        
        if not response:
            self.log_test("Shopper Registration", False, "Request failed")
            return False
            
        if response.status_code == 201:
            data = response.json()
            
            if "user" in data and "token" in data:
                user = data["user"]
                token = data["token"]
                
                if (user.get("email") == TEST_USER["email"] and
                    user.get("role") == "shopper" and
                    token.get("access_token")):
                    
                    self.token = token["access_token"]
                    self.user_id = user["id"]
                    self.log_test("Shopper Registration & Login", True, f"User registered and logged in successfully")
                    return True
                else:
                    self.log_test("Shopper Registration", False, "Invalid user data or role", data)
            else:
                self.log_test("Shopper Registration", False, "Missing user or token in response", data)
        else:
            self.log_test("Shopper Registration", False, f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def get_existing_shop_id(self):
        """Get an existing shop ID from the database"""
        print("🏪 Getting existing shop ID...")
        
        response = self.make_request("GET", "/shops", headers={})
        
        if not response:
            self.log_test("Get Shop ID", False, "Request failed")
            return None
            
        if response.status_code == 200:
            data = response.json()
            
            if "data" in data and len(data["data"]) > 0:
                shop = data["data"][0]  # Get first shop
                shop_id = shop.get("id")
                if shop_id:
                    self.shop_id = shop_id
                    self.log_test("Get Shop ID", True, f"Using shop: {shop.get('name')} (ID: {shop_id})")
                    return shop_id
                else:
                    self.log_test("Get Shop ID", False, "No shop ID found in response")
            else:
                self.log_test("Get Shop ID", False, "No shops found in database")
        else:
            self.log_test("Get Shop ID", False, f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return None
    
    def test_high_star_review_no_evidence(self):
        """Test 1: High-star review (4-5 stars) - No evidence required"""
        print("⭐ Testing High-Star Review (5 stars) - No Evidence Required...")
        
        if not self.token or not self.shop_id:
            self.log_test("High-Star Review (No Evidence)", False, "Missing auth token or shop ID")
            return False
        
        review_data = {
            "shop_id": self.shop_id,
            "rating": 5,
            "comment": "Excellent service and product quality! Fast shipping, great customer support, and authentic products. Highly recommended for everyone!"
        }
        
        response = self.make_request("POST", "/reviews", review_data)
        
        if not response:
            self.log_test("High-Star Review (No Evidence)", False, "Request failed")
            return False
            
        if response.status_code == 201:
            data = response.json()
            
            # Validate response structure and status
            if (data.get("shop_id") == self.shop_id and
                data.get("rating") == 5 and
                data.get("status") == "published"):  # Should be published immediately
                
                self.log_test("High-Star Review (No Evidence)", True, 
                            f"Review created with status: {data.get('status')} (ID: {data.get('id', 'N/A')})")
                return True
            else:
                self.log_test("High-Star Review (No Evidence)", False, 
                            f"Invalid response data. Status: {data.get('status')}, Expected: published", data)
        else:
            self.log_test("High-Star Review (No Evidence)", False, 
                        f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_low_star_review_with_evidence(self):
        """Test 2: Low-star review (1-3 stars) WITH evidence"""
        print("⭐ Testing Low-Star Review (2 stars) WITH Evidence...")
        
        if not self.token or not self.shop_id:
            self.log_test("Low-Star Review (With Evidence)", False, "Missing auth token or shop ID")
            return False
        
        # Create test images
        test_image1 = self.create_test_image_base64("small")
        test_image2 = self.create_test_image_base64("large")
        
        review_data = {
            "shop_id": self.shop_id,
            "rating": 2,
            "comment": "Poor quality product and terrible customer service. The item arrived damaged and the support team was unhelpful. Very disappointed with this purchase.",
            "proof_photos": [test_image1, test_image2],
            "proof_order_number": "ORD-2024-12345"
        }
        
        response = self.make_request("POST", "/reviews", review_data)
        
        if not response:
            self.log_test("Low-Star Review (With Evidence)", False, "Request failed")
            return False
        
        # Debug: Print response details
        print(f"   Response Status: {response.status_code}")
        if response.content:
            try:
                error_data = response.json()
                print(f"   Response Data: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Response Text: {response.text}")
            
        if response.status_code == 201:
            data = response.json()
            
            # Validate response structure and status
            if (data.get("shop_id") == self.shop_id and
                data.get("rating") == 2 and
                data.get("status") == "pending" and  # Should be pending for admin approval
                data.get("proof_order_number") == "ORD-2024-12345" and
                len(data.get("proof_photos", [])) == 2 and
                "id" in data):
                
                self.log_test("Low-Star Review (With Evidence)", True, 
                            f"Review created with status: {data.get('status')}, proof included (ID: {data.get('id')})")
                return True
            else:
                self.log_test("Low-Star Review (With Evidence)", False, 
                            f"Invalid response data. Status: {data.get('status')}, Proof photos: {len(data.get('proof_photos', []))}", data)
        else:
            self.log_test("Low-Star Review (With Evidence)", False, 
                        f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_low_star_review_without_photos(self):
        """Test 3: Low-star review (1-3 stars) WITHOUT photos (Should Fail)"""
        print("❌ Testing Low-Star Review (2 stars) WITHOUT Photos (Should Fail)...")
        
        if not self.token or not self.shop_id:
            self.log_test("Low-Star Review (No Photos)", False, "Missing auth token or shop ID")
            return False
        
        review_data = {
            "shop_id": self.shop_id,
            "rating": 2,
            "comment": "Poor quality product and terrible customer service. The item arrived damaged and the support team was unhelpful.",
            "proof_order_number": "ORD-2024-67890"
            # Missing proof_photos
        }
        
        response = self.make_request("POST", "/reviews", review_data)
        
        if not response:
            self.log_test("Low-Star Review (No Photos)", False, "Request failed")
            return False
            
        if response.status_code == 400:
            data = response.json()
            
            # Should get error about missing proof photos
            if "detail" in data and ("foto" in data["detail"].lower() or "photo" in data["detail"].lower()):
                self.log_test("Low-Star Review (No Photos)", True, 
                            f"Correctly rejected review without photos: {data['detail']}")
                return True
            else:
                self.log_test("Low-Star Review (No Photos)", False, 
                            f"Unexpected error message: {data.get('detail')}", data)
        else:
            self.log_test("Low-Star Review (No Photos)", False, 
                        f"Expected HTTP 400, got {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_low_star_review_without_order_number(self):
        """Test 4: Low-star review (1-3 stars) WITHOUT order number (Should Fail)"""
        print("❌ Testing Low-Star Review (2 stars) WITHOUT Order Number (Should Fail)...")
        
        if not self.token or not self.shop_id:
            self.log_test("Low-Star Review (No Order Number)", False, "Missing auth token or shop ID")
            return False
        
        test_image = self.create_test_image_base64("small")
        
        review_data = {
            "shop_id": self.shop_id,
            "rating": 2,
            "comment": "Poor quality product and terrible customer service. The item arrived damaged and the support team was unhelpful.",
            "proof_photos": [test_image]
            # Missing proof_order_number
        }
        
        response = self.make_request("POST", "/reviews", review_data)
        
        if not response:
            self.log_test("Low-Star Review (No Order Number)", False, "Request failed")
            return False
            
        if response.status_code == 400:
            data = response.json()
            
            # Should get error about missing order number
            if "detail" in data and ("bestellnummer" in data["detail"].lower() or "order" in data["detail"].lower()):
                self.log_test("Low-Star Review (No Order Number)", True, 
                            f"Correctly rejected review without order number: {data['detail']}")
                return True
            else:
                self.log_test("Low-Star Review (No Order Number)", False, 
                            f"Unexpected error message: {data.get('detail')}", data)
        else:
            self.log_test("Low-Star Review (No Order Number)", False, 
                        f"Expected HTTP 400, got {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_invalid_base64_image(self):
        """Test 5: Try to submit review with invalid base64 image data"""
        print("❌ Testing Low-Star Review with Invalid Base64 Image (Should Fail)...")
        
        if not self.token or not self.shop_id:
            self.log_test("Invalid Base64 Image", False, "Missing auth token or shop ID")
            return False
        
        review_data = {
            "shop_id": self.shop_id,
            "rating": 1,
            "comment": "Terrible product quality and awful customer service. Would not recommend to anyone at all.",
            "proof_photos": ["invalid_base64_data_not_an_image"],
            "proof_order_number": "ORD-2024-99999"
        }
        
        response = self.make_request("POST", "/reviews", review_data)
        
        if not response:
            self.log_test("Invalid Base64 Image", False, "Request failed")
            return False
            
        if response.status_code == 400:
            data = response.json()
            
            # Should get error about invalid image
            if "detail" in data and ("bild" in data["detail"].lower() or "image" in data["detail"].lower() or "datei" in data["detail"].lower()):
                self.log_test("Invalid Base64 Image", True, 
                            f"Correctly rejected invalid image: {data['detail']}")
                return True
            else:
                self.log_test("Invalid Base64 Image", False, 
                            f"Unexpected error message: {data.get('detail')}", data)
        else:
            self.log_test("Invalid Base64 Image", False, 
                        f"Expected HTTP 400, got {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_too_many_photos(self):
        """Test 6: Try to submit more than 5 photos (should fail)"""
        print("❌ Testing Low-Star Review with Too Many Photos (Should Fail)...")
        
        if not self.token or not self.shop_id:
            self.log_test("Too Many Photos", False, "Missing auth token or shop ID")
            return False
        
        # Create 6 test images (more than allowed limit of 5)
        test_images = [self.create_test_image_base64("small") for _ in range(6)]
        
        review_data = {
            "shop_id": self.shop_id,
            "rating": 1,
            "comment": "Terrible product quality and awful customer service. Would not recommend to anyone at all.",
            "proof_photos": test_images,
            "proof_order_number": "ORD-2024-88888"
        }
        
        response = self.make_request("POST", "/reviews", review_data)
        
        if not response:
            self.log_test("Too Many Photos", False, "Request failed")
            return False
            
        if response.status_code == 400:
            data = response.json()
            
            # Should get error about too many photos
            if "detail" in data and ("5" in data["detail"] or "maximal" in data["detail"].lower()):
                self.log_test("Too Many Photos", True, 
                            f"Correctly rejected too many photos: {data['detail']}")
                return True
            else:
                self.log_test("Too Many Photos", False, 
                            f"Unexpected error message: {data.get('detail')}", data)
        else:
            self.log_test("Too Many Photos", False, 
                        f"Expected HTTP 400, got {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_3_star_review_boundary(self):
        """Test 7: Test 3-star review (boundary case) - should require evidence"""
        print("⭐ Testing 3-Star Review (Boundary Case) - Should Require Evidence...")
        
        if not self.token or not self.shop_id:
            self.log_test("3-Star Review Boundary", False, "Missing auth token or shop ID")
            return False
        
        # First try without evidence (should fail)
        review_data_no_evidence = {
            "shop_id": self.shop_id,
            "rating": 3,
            "comment": "Average product quality and service. Could be better but not terrible either."
        }
        
        response = self.make_request("POST", "/reviews", review_data_no_evidence)
        
        if response and response.status_code == 400:
            # Good, it should require evidence
            test_image = self.create_test_image_base64("small")
            
            # Now try with evidence (should succeed)
            review_data_with_evidence = {
                "shop_id": self.shop_id,
                "rating": 3,
                "comment": "Average product quality and service. Could be better but not terrible either.",
                "proof_photos": [test_image],
                "proof_order_number": "ORD-2024-33333"
            }
            
            response = self.make_request("POST", "/reviews", review_data_with_evidence)
            
            if response and response.status_code == 201:
                data = response.json()
                if data.get("status") == "pending":
                    self.log_test("3-Star Review Boundary", True, 
                                f"3-star review correctly requires evidence and goes to pending status")
                    return True
                else:
                    self.log_test("3-Star Review Boundary", False, 
                                f"3-star review with evidence has wrong status: {data.get('status')}")
            else:
                self.log_test("3-Star Review Boundary", False, 
                            f"3-star review with evidence failed: HTTP {response.status_code if response else 'No response'}")
        else:
            self.log_test("3-Star Review Boundary", False, 
                        f"3-star review without evidence should fail but got: HTTP {response.status_code if response else 'No response'}")
            
        return False
    
    def test_4_star_review_boundary(self):
        """Test 8: Test 4-star review (boundary case) - should NOT require evidence"""
        print("⭐ Testing 4-Star Review (Boundary Case) - Should NOT Require Evidence...")
        
        if not self.token or not self.shop_id:
            self.log_test("4-Star Review Boundary", False, "Missing auth token or shop ID")
            return False
        
        review_data = {
            "shop_id": self.shop_id,
            "rating": 4,
            "comment": "Good product quality and service. Minor issues but overall satisfied with the purchase."
        }
        
        response = self.make_request("POST", "/reviews", review_data)
        
        if not response:
            self.log_test("4-Star Review Boundary", False, "Request failed")
            return False
            
        if response.status_code == 201:
            data = response.json()
            
            if (data.get("rating") == 4 and
                data.get("status") == "published"):  # Should be published immediately
                
                self.log_test("4-Star Review Boundary", True, 
                            f"4-star review correctly published without evidence requirement")
                return True
            else:
                self.log_test("4-Star Review Boundary", False, 
                            f"4-star review has wrong status: {data.get('status')}")
        else:
            self.log_test("4-Star Review Boundary", False, 
                        f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def run_all_tests(self):
        """Run all review evidence tests"""
        print("🚀 Starting Review Submission with Mandatory Evidence Tests")
        print(f"🌐 Base URL: {BASE_URL}")
        print("=" * 80)
        
        # Register and login with new shopper user
        if not self.register_and_login_shopper():
            print("❌ Could not register and login shopper user. Cannot proceed with tests.")
            return False
        
        # Get existing shop ID
        if not self.get_existing_shop_id():
            print("❌ Could not get existing shop ID. Cannot proceed with tests.")
            return False
        
        print("\n🧪 RUNNING EVIDENCE REQUIREMENT TESTS")
        print("-" * 50)
        
        # Run all test scenarios
        test_methods = [
            self.test_high_star_review_no_evidence,
            self.test_low_star_review_with_evidence,
            self.test_low_star_review_without_photos,
            self.test_low_star_review_without_order_number,
            self.test_invalid_base64_image,
            self.test_too_many_photos,
            self.test_3_star_review_boundary,
            self.test_4_star_review_boundary
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"❌ Test {test_method.__name__} failed with exception: {e}")
                self.log_test(test_method.__name__, False, f"Exception: {e}")
        
        # Summary
        print("\n" + "=" * 80)
        print("📋 REVIEW EVIDENCE TESTING SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        # Categorize results
        critical_tests = [
            "High-Star Review (No Evidence)",
            "Low-Star Review (With Evidence)", 
            "Low-Star Review (No Photos)",
            "Low-Star Review (No Order Number)"
        ]
        
        critical_failures = []
        other_failures = []
        
        for result in self.test_results:
            if not result["success"]:
                if any(critical in result["test"] for critical in critical_tests):
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
            print("\n🎉 All review evidence tests passed!")
            return True
        elif len(critical_failures) == 0:
            print("\n✅ All critical review evidence functionality working!")
            return True
        else:
            print(f"\n❌ {len(critical_failures)} critical failures found.")
            return False

if __name__ == "__main__":
    tester = ReviewEvidenceAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)