#!/usr/bin/env python3
"""
Comprehensive Email Verification Test Suite
Tests all scenarios mentioned in the review request
"""

import requests
import json
import sys
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import time

# Configuration
BASE_URL = "https://trust-ratings-app.preview.emergentagent.com/api"
TIMEOUT = 30

class EmailVerificationTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = TIMEOUT
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
        
        if headers is None:
            headers = {}
            
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            return response
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
    
    async def check_database_verification_code(self, email):
        """Check MongoDB for verification code"""
        try:
            client = AsyncIOMotorClient('mongodb://localhost:27017')
            db = client['test_database']
            
            verification = await db.email_verifications.find_one({"email": email})
            client.close()
            return verification
        except Exception as e:
            print(f"Database check failed: {e}")
            return None
    
    async def get_existing_user(self):
        """Get an existing user from database"""
        try:
            client = AsyncIOMotorClient('mongodb://localhost:27017')
            db = client['test_database']
            
            user = await db.users.find_one({"role": "shopper"})
            client.close()
            return user
        except Exception as e:
            print(f"Database check failed: {e}")
            return None
    
    async def create_test_user(self):
        """Create a new test user for verification"""
        try:
            client = AsyncIOMotorClient('mongodb://localhost:27017')
            db = client['test_database']
            
            # Create unique test user
            timestamp = int(time.time())
            test_user = {
                "full_name": "Test User Email Verification",
                "email": f"test.email.verification.{timestamp}@example.com",
                "password": "hashedpassword123",  # In real app this would be hashed
                "role": "shopper",
                "email_verified": False,
                "created_at": datetime.utcnow()
            }
            
            result = await db.users.insert_one(test_user)
            client.close()
            
            if result.inserted_id:
                return test_user["email"]
            return None
        except Exception as e:
            print(f"User creation failed: {e}")
            return None
    
    def test_scenario_1_send_code_existing_user(self):
        """Test Scenario 1: Send verification code to existing user"""
        print("📧 Test Scenario 1: Email Verification Code Sending (Existing User)")
        
        # Create a new unverified user for this test
        test_email = asyncio.run(self.create_test_user())
        if not test_email:
            self.log_test("Scenario 1 - Send Code (Existing User)", False, "Could not create test user")
            return False
        
        request_data = {"email": test_email}
        
        response = self.make_request("POST", "/email-verification/send-code", request_data)
        
        if not response:
            self.log_test("Scenario 1 - Send Code (Existing User)", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            # Check for already verified case
            if data.get("already_verified"):
                self.log_test("Scenario 1 - Send Code (Existing User)", True, 
                            f"✅ API correctly handles already verified user: {test_email}")
                return test_email
            
            # Validate response structure for new verification
            required_fields = ["message", "expires_in_minutes", "email"]
            if all(field in data for field in required_fields):
                
                if (data["email"] == test_email and 
                    data["expires_in_minutes"] == 15):
                    
                    self.log_test("Scenario 1 - Send Code (Existing User)", True, 
                                f"✅ API returns success response for {test_email}")
                    return test_email
                else:
                    self.log_test("Scenario 1 - Send Code (Existing User)", False, "Invalid response data", data)
            else:
                self.log_test("Scenario 1 - Send Code (Existing User)", False, 
                            f"Missing required fields: {required_fields}", data)
        else:
            self.log_test("Scenario 1 - Send Code (Existing User)", False, 
                        f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_scenario_1_check_email_sent_logs(self):
        """Check backend logs for 'Email sent successfully' message"""
        print("📋 Test Scenario 1: Check Backend Logs for Email Sending")
        
        try:
            import subprocess
            result = subprocess.run(
                ["tail", "-n", "100", "/var/log/supervisor/backend.err.log"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                log_content = result.stdout
                
                # Look for specific email success messages
                if "✅ Verification email sent successfully" in log_content:
                    self.log_test("Scenario 1 - Email Sent Logs", True, 
                                "✅ Found 'Email sent successfully' message in backend logs")
                    return True
                elif "Email sent successfully" in log_content:
                    self.log_test("Scenario 1 - Email Sent Logs", True, 
                                "✅ Found email sending confirmation in backend logs")
                    return True
                else:
                    self.log_test("Scenario 1 - Email Sent Logs", False, 
                                "❌ No 'Email sent successfully' message found in logs")
            else:
                self.log_test("Scenario 1 - Email Sent Logs", False, 
                            f"Could not read backend logs: {result.stderr}")
                
        except Exception as e:
            self.log_test("Scenario 1 - Email Sent Logs", False, f"Log check failed: {e}")
            
        return False
    
    def test_scenario_1_check_database_storage(self, email):
        """Check if verification code is stored in MongoDB email_verifications collection"""
        print("🗄️ Test Scenario 1: Verify Code Storage in MongoDB")
        
        verification = asyncio.run(self.check_database_verification_code(email))
        
        if verification:
            required_fields = ["code", "expires_at", "created_at", "attempts"]
            if all(field in verification for field in required_fields):
                
                # Validate code format (5 digits)
                code = verification["code"]
                if len(code) == 5 and code.isdigit():
                    self.log_test("Scenario 1 - Database Storage", True, 
                                f"✅ Verification code stored in email_verifications collection (5-digit code: {code})")
                    return code
                else:
                    self.log_test("Scenario 1 - Database Storage", False, 
                                f"Invalid code format: {code}")
            else:
                self.log_test("Scenario 1 - Database Storage", False, 
                            f"Missing required fields in verification record: {required_fields}")
        else:
            self.log_test("Scenario 1 - Database Storage", False, 
                        "❌ No verification record found in email_verifications collection")
            
        return None
    
    def test_scenario_2_verify_correct_code(self, email, code):
        """Test Scenario 2: Verify correct code"""
        print("✅ Test Scenario 2: Email Verification Code Validation (Correct Code)")
        
        if not code:
            self.log_test("Scenario 2 - Verify Correct Code", False, "No verification code available")
            return False
        
        verify_data = {
            "email": email,
            "code": code
        }
        
        response = self.make_request("POST", "/email-verification/verify-code", verify_data)
        
        if not response:
            self.log_test("Scenario 2 - Verify Correct Code", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            if "message" in data and "verified" in data:
                if data["verified"] and "successfully" in data["message"].lower():
                    self.log_test("Scenario 2 - Verify Correct Code", True, 
                                "✅ Correct code accepted and email verified successfully")
                    return True
                else:
                    self.log_test("Scenario 2 - Verify Correct Code", False, 
                                "Verification not successful", data)
            else:
                self.log_test("Scenario 2 - Verify Correct Code", False, 
                            "Invalid response structure", data)
        else:
            self.log_test("Scenario 2 - Verify Correct Code", False, 
                        f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_scenario_2_verify_incorrect_code(self):
        """Test Scenario 2: Verify incorrect code"""
        print("❌ Test Scenario 2: Email Verification Code Validation (Incorrect Code)")
        
        # Create a new test user for this test
        test_email = asyncio.run(self.create_test_user())
        if not test_email:
            self.log_test("Scenario 2 - Verify Incorrect Code", False, "Could not create test user")
            return False
        
        # Send verification code first
        request_data = {"email": test_email}
        send_response = self.make_request("POST", "/email-verification/send-code", request_data)
        
        if not send_response or send_response.status_code != 200:
            self.log_test("Scenario 2 - Verify Incorrect Code", False, "Could not send verification code")
            return False
        
        # Try with wrong code
        verify_data = {
            "email": test_email,
            "code": "99999"  # Wrong code
        }
        
        response = self.make_request("POST", "/email-verification/verify-code", verify_data)
        
        if not response:
            self.log_test("Scenario 2 - Verify Incorrect Code", False, "Request failed")
            return False
            
        if response.status_code == 400:
            data = response.json()
            
            if "detail" in data and "invalid" in data["detail"].lower():
                self.log_test("Scenario 2 - Verify Incorrect Code", True, 
                            f"✅ Incorrect code correctly rejected: {data['detail']}")
                return True
            else:
                self.log_test("Scenario 2 - Verify Incorrect Code", False, 
                            "Unexpected error message", data)
        else:
            self.log_test("Scenario 2 - Verify Incorrect Code", False, 
                        f"Expected HTTP 400, got {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_scenario_2_expired_code(self):
        """Test Scenario 2: Expired code scenario"""
        print("⏰ Test Scenario 2: Email Verification Code Validation (Expired Code)")
        
        # For this test, we'll simulate by checking the logic
        # In a real scenario, we'd wait 15+ minutes or manipulate the database
        
        # Create a new test user
        test_email = asyncio.run(self.create_test_user())
        if not test_email:
            self.log_test("Scenario 2 - Expired Code", False, "Could not create test user")
            return False
        
        # Send verification code
        request_data = {"email": test_email}
        send_response = self.make_request("POST", "/email-verification/send-code", request_data)
        
        if not send_response or send_response.status_code != 200:
            self.log_test("Scenario 2 - Expired Code", False, "Could not send verification code")
            return False
        
        # Get the code from database and manually expire it
        try:
            
            async def expire_code():
                client = AsyncIOMotorClient('mongodb://localhost:27017')
                db = client['test_database']
                
                # Set expiry to past time
                past_time = datetime.utcnow() - timedelta(minutes=1)
                await db.email_verifications.update_one(
                    {"email": test_email},
                    {"$set": {"expires_at": past_time}}
                )
                
                # Get the code
                verification = await db.email_verifications.find_one({"email": test_email})
                client.close()
                return verification["code"] if verification else None
            
            code = asyncio.run(expire_code())
            
            if not code:
                self.log_test("Scenario 2 - Expired Code", False, "Could not get verification code")
                return False
            
            # Try to verify with expired code
            verify_data = {
                "email": test_email,
                "code": code
            }
            
            response = self.make_request("POST", "/email-verification/verify-code", verify_data)
            
            if not response:
                self.log_test("Scenario 2 - Expired Code", False, "Request failed")
                return False
                
            if response.status_code == 400:
                data = response.json()
                
                if "detail" in data and "expired" in data["detail"].lower():
                    self.log_test("Scenario 2 - Expired Code", True, 
                                f"✅ Expired code correctly rejected: {data['detail']}")
                    return True
                else:
                    self.log_test("Scenario 2 - Expired Code", False, 
                                "Unexpected error message", data)
            else:
                self.log_test("Scenario 2 - Expired Code", False, 
                            f"Expected HTTP 400, got {response.status_code}", response.json() if response.content else {})
                
        except Exception as e:
            self.log_test("Scenario 2 - Expired Code", False, f"Test setup failed: {e}")
            
        return False
    
    def test_scenario_2_max_attempts(self):
        """Test Scenario 2: Max attempts (5) scenario"""
        print("🚫 Test Scenario 2: Email Verification Code Validation (Max Attempts)")
        
        # Create a new test user
        test_email = asyncio.run(self.create_test_user())
        if not test_email:
            self.log_test("Scenario 2 - Max Attempts", False, "Could not create test user")
            return False
        
        # Send verification code
        request_data = {"email": test_email}
        send_response = self.make_request("POST", "/email-verification/send-code", request_data)
        
        if not send_response or send_response.status_code != 200:
            self.log_test("Scenario 2 - Max Attempts", False, "Could not send verification code")
            return False
        
        # Try wrong code 5 times
        verify_data = {
            "email": test_email,
            "code": "00000"  # Wrong code
        }
        
        for attempt in range(5):
            response = self.make_request("POST", "/email-verification/verify-code", verify_data)
            if not response or response.status_code != 400:
                self.log_test("Scenario 2 - Max Attempts", False, f"Unexpected response on attempt {attempt + 1}")
                return False
        
        # 6th attempt should be blocked
        response = self.make_request("POST", "/email-verification/verify-code", verify_data)
        
        if not response:
            self.log_test("Scenario 2 - Max Attempts", False, "Request failed")
            return False
            
        if response.status_code == 429:
            data = response.json()
            
            if "detail" in data and "too many" in data["detail"].lower():
                self.log_test("Scenario 2 - Max Attempts", True, 
                            f"✅ Max attempts (5) correctly enforced: {data['detail']}")
                return True
            else:
                self.log_test("Scenario 2 - Max Attempts", False, 
                            "Unexpected error message", data)
        else:
            self.log_test("Scenario 2 - Max Attempts", False, 
                        f"Expected HTTP 429, got {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def test_scenario_3_check_status_before(self):
        """Test Scenario 3: Check verification status before verification"""
        print("📊 Test Scenario 3: Verification Status Check (Before Verification)")
        
        # Create a new unverified test user
        test_email = asyncio.run(self.create_test_user())
        if not test_email:
            self.log_test("Scenario 3 - Status Before", False, "Could not create test user")
            return False, None
        
        response = self.make_request("GET", f"/email-verification/check-status/{test_email}")
        
        if not response:
            self.log_test("Scenario 3 - Status Before", False, "Request failed")
            return False, None
            
        if response.status_code == 200:
            data = response.json()
            
            required_fields = ["email", "verified"]
            if all(field in data for field in required_fields):
                
                if data["email"] == test_email and data["verified"] == False:
                    self.log_test("Scenario 3 - Status Before", True, 
                                f"✅ Status check before verification: Email: {data['email']}, Verified: {data['verified']}")
                    return True, test_email
                else:
                    self.log_test("Scenario 3 - Status Before", False, 
                                f"Unexpected status: {data}")
            else:
                self.log_test("Scenario 3 - Status Before", False, 
                            f"Missing required fields: {required_fields}", data)
        else:
            self.log_test("Scenario 3 - Status Before", False, 
                        f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False, None
    
    def test_scenario_3_check_status_after(self, email):
        """Test Scenario 3: Check verification status after successful verification"""
        print("📊 Test Scenario 3: Verification Status Check (After Verification)")
        
        if not email:
            self.log_test("Scenario 3 - Status After", False, "No email provided")
            return False
        
        # First verify the email
        # Send code
        request_data = {"email": email}
        send_response = self.make_request("POST", "/email-verification/send-code", request_data)
        
        if not send_response or send_response.status_code != 200:
            self.log_test("Scenario 3 - Status After", False, "Could not send verification code")
            return False
        
        # Get code from database
        verification = asyncio.run(self.check_database_verification_code(email))
        if not verification:
            self.log_test("Scenario 3 - Status After", False, "Could not get verification code")
            return False
        
        # Verify with correct code
        verify_data = {
            "email": email,
            "code": verification["code"]
        }
        
        verify_response = self.make_request("POST", "/email-verification/verify-code", verify_data)
        
        if not verify_response or verify_response.status_code != 200:
            self.log_test("Scenario 3 - Status After", False, "Could not verify email")
            return False
        
        # Now check status
        response = self.make_request("GET", f"/email-verification/check-status/{email}")
        
        if not response:
            self.log_test("Scenario 3 - Status After", False, "Request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            
            required_fields = ["email", "verified"]
            if all(field in data for field in required_fields):
                
                if data["email"] == email and data["verified"] == True:
                    self.log_test("Scenario 3 - Status After", True, 
                                f"✅ Status check after verification: Email: {data['email']}, Verified: {data['verified']}")
                    return True
                else:
                    self.log_test("Scenario 3 - Status After", False, 
                                f"Unexpected status: {data}")
            else:
                self.log_test("Scenario 3 - Status After", False, 
                            f"Missing required fields: {required_fields}", data)
        else:
            self.log_test("Scenario 3 - Status After", False, 
                        f"HTTP {response.status_code}", response.json() if response.content else {})
            
        return False
    
    def run_comprehensive_tests(self):
        """Run all comprehensive email verification tests"""
        print("🚀 COMPREHENSIVE EMAIL VERIFICATION TEST SUITE")
        print("=" * 60)
        print("Testing SMTP Email Verification System")
        print("SMTP Server: codimasters.com:465 (SSL)")
        print("From: trust@codimasters.com")
        print("=" * 60)
        
        # Scenario 1: Email Verification Code Sending
        print("\n📧 SCENARIO 1: EMAIL VERIFICATION CODE SENDING")
        print("-" * 50)
        
        test_email = self.test_scenario_1_send_code_existing_user()
        if test_email:
            self.test_scenario_1_check_email_sent_logs()
            verification_code = self.test_scenario_1_check_database_storage(test_email)
        else:
            verification_code = None
        
        # Scenario 2: Email Verification Code Validation
        print("\n✅ SCENARIO 2: EMAIL VERIFICATION CODE VALIDATION")
        print("-" * 50)
        
        if test_email and verification_code:
            self.test_scenario_2_verify_correct_code(test_email, verification_code)
        
        self.test_scenario_2_verify_incorrect_code()
        self.test_scenario_2_expired_code()
        self.test_scenario_2_max_attempts()
        
        # Scenario 3: Verification Status Check
        print("\n📊 SCENARIO 3: VERIFICATION STATUS CHECK")
        print("-" * 50)
        
        status_before_success, status_test_email = self.test_scenario_3_check_status_before()
        if status_before_success and status_test_email:
            self.test_scenario_3_check_status_after(status_test_email)
        
        # Final Summary
        print("\n" + "=" * 60)
        print("📋 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        # Success criteria analysis
        critical_tests = [
            "Scenario 1 - Send Code (Existing User)",
            "Scenario 1 - Email Sent Logs", 
            "Scenario 1 - Database Storage",
            "Scenario 2 - Verify Correct Code",
            "Scenario 3 - Status Before",
            "Scenario 3 - Status After"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result["success"] and result["test"] in critical_tests)
        
        print(f"\n🎯 SUCCESS CRITERIA ANALYSIS:")
        print(f"   Critical Tests Passed: {critical_passed}/{len(critical_tests)}")
        
        if critical_passed == len(critical_tests):
            print("\n🎉 ALL SUCCESS CRITERIA MET!")
            print("✅ All API endpoints return correct status codes")
            print("✅ Verification codes are stored correctly in database") 
            print("✅ Email sending is logged in backend")
            print("✅ Verification flow works end-to-end")
            return True
        else:
            print(f"\n❌ {len(critical_tests) - critical_passed} critical test(s) failed")
            
            failed_critical = [result["test"] for result in self.test_results 
                             if not result["success"] and result["test"] in critical_tests]
            
            if failed_critical:
                print("Failed critical tests:")
                for test in failed_critical:
                    print(f"   - {test}")
            
            return False

def main():
    """Main test runner"""
    tester = EmailVerificationTester()
    
    print("🚀 Starting Comprehensive Email Verification Tests")
    print(f"🌐 Backend URL: {BASE_URL}")
    
    success = tester.run_comprehensive_tests()
    
    if success:
        print("\n✅ COMPREHENSIVE EMAIL VERIFICATION TESTS PASSED")
    else:
        print("\n❌ COMPREHENSIVE EMAIL VERIFICATION TESTS FAILED")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()