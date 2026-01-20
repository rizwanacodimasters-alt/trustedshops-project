#!/usr/bin/env python3
"""
Focused Review Evidence Testing
Tests the mandatory evidence feature for low-star reviews (1-3 stars) vs high-star reviews (4-5 stars).
"""

import requests
import json
import base64
import time

# Configuration
BASE_URL = "https://trust-ratings-app.preview.emergentagent.com/api"

def create_test_image():
    """Create a simple test image in base64 format"""
    # 1x1 pixel red PNG
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x07\n\xdb\xa8\x00\x00\x00\x00IEND\xaeB`\x82'
    base64_data = base64.b64encode(png_data).decode('utf-8')
    return f"data:image/png;base64,{base64_data}"

def register_user(email_suffix):
    """Register a new user and return token"""
    user_data = {
        "full_name": f"Test User {email_suffix}",
        "email": f"test.user.{email_suffix}@example.com",
        "password": "TestPassword123!",
        "role": "shopper"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    if response.status_code == 201:
        return response.json()["token"]["access_token"]
    else:
        print(f"Registration failed: {response.status_code} - {response.text}")
        return None

def get_shop_id():
    """Get an existing shop ID"""
    response = requests.get(f"{BASE_URL}/shops")
    if response.status_code == 200:
        shops = response.json()["data"]
        if shops:
            return shops[0]["id"]
    return None

def test_scenario(scenario_name, rating, include_evidence=False, expect_success=True, expect_status="published"):
    """Test a specific review scenario"""
    print(f"\n🧪 Testing: {scenario_name}")
    print(f"   Rating: {rating} stars, Evidence: {include_evidence}, Expect: {expect_status}")
    
    # Register new user for this test
    timestamp = int(time.time() * 1000)  # More unique timestamp
    token = register_user(timestamp)
    if not token:
        print("   ❌ FAIL: Could not register user")
        return False
    
    # Get shop ID
    shop_id = get_shop_id()
    if not shop_id:
        print("   ❌ FAIL: Could not get shop ID")
        return False
    
    # Prepare review data
    review_data = {
        "shop_id": shop_id,
        "rating": rating,
        "comment": f"This is a {rating}-star review for testing purposes. The service and product quality reflects this rating appropriately."
    }
    
    # Add evidence if required
    if include_evidence:
        review_data["proof_photos"] = [create_test_image()]
        review_data["proof_order_number"] = f"ORD-2024-{timestamp}"
    
    # Make request
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/reviews", json=review_data, headers=headers)
    
    print(f"   Response Status: {response.status_code}")
    
    if expect_success:
        if response.status_code == 201:
            data = response.json()
            actual_status = data.get("status")
            if actual_status == expect_status:
                print(f"   ✅ PASS: Review created with status '{actual_status}'")
                return True
            else:
                print(f"   ❌ FAIL: Expected status '{expect_status}', got '{actual_status}'")
                return False
        else:
            print(f"   ❌ FAIL: Expected success (201), got {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    else:
        if response.status_code == 400:
            error_data = response.json()
            print(f"   ✅ PASS: Correctly rejected with error: {error_data.get('detail', 'Unknown error')}")
            return True
        else:
            print(f"   ❌ FAIL: Expected 400 error, got {response.status_code}")
            return False

def main():
    print("🚀 Review Evidence Feature Testing")
    print("=" * 60)
    
    test_results = []
    
    # Test 1: High-star review (5 stars) - No evidence required
    result1 = test_scenario(
        "High-Star Review (5 stars) - No Evidence Required",
        rating=5,
        include_evidence=False,
        expect_success=True,
        expect_status="published"
    )
    test_results.append(("High-Star Review (No Evidence)", result1))
    
    # Test 2: Low-star review (2 stars) WITH evidence
    result2 = test_scenario(
        "Low-Star Review (2 stars) WITH Evidence",
        rating=2,
        include_evidence=True,
        expect_success=True,
        expect_status="pending"
    )
    test_results.append(("Low-Star Review (With Evidence)", result2))
    
    # Test 3: Low-star review (2 stars) WITHOUT evidence (should fail)
    result3 = test_scenario(
        "Low-Star Review (2 stars) WITHOUT Evidence (Should Fail)",
        rating=2,
        include_evidence=False,
        expect_success=False
    )
    test_results.append(("Low-Star Review (No Evidence - Should Fail)", result3))
    
    # Test 4: Boundary test - 3 stars WITH evidence
    result4 = test_scenario(
        "Boundary Test - 3-Star Review WITH Evidence",
        rating=3,
        include_evidence=True,
        expect_success=True,
        expect_status="pending"
    )
    test_results.append(("3-Star Review (With Evidence)", result4))
    
    # Test 5: Boundary test - 4 stars WITHOUT evidence
    result5 = test_scenario(
        "Boundary Test - 4-Star Review WITHOUT Evidence",
        rating=4,
        include_evidence=False,
        expect_success=True,
        expect_status="published"
    )
    test_results.append(("4-Star Review (No Evidence)", result5))
    
    # Test 6: Edge case - 1 star WITH evidence
    result6 = test_scenario(
        "Edge Case - 1-Star Review WITH Evidence",
        rating=1,
        include_evidence=True,
        expect_success=True,
        expect_status="pending"
    )
    test_results.append(("1-Star Review (With Evidence)", result6))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    print("\nDetailed Results:")
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    if passed == total:
        print("\n🎉 All tests passed! Review evidence feature is working correctly.")
        print("\nKey Findings:")
        print("• High-star reviews (4-5 stars): No evidence required, status = 'published'")
        print("• Low-star reviews (1-3 stars): Evidence required, status = 'pending'")
        print("• Reviews without required evidence are properly rejected with 400 error")
        return True
    else:
        print(f"\n❌ {total - passed} test(s) failed. Review evidence feature needs attention.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)