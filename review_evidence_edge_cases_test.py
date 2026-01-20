#!/usr/bin/env python3
"""
Review Evidence Edge Cases Testing
Tests edge cases for the mandatory evidence feature.
"""

import requests
import json
import base64
import time

# Configuration
BASE_URL = "https://trust-ratings-app.preview.emergentagent.com/api"

def create_test_image():
    """Create a simple test image in base64 format"""
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x07\n\xdb\xa8\x00\x00\x00\x00IEND\xaeB`\x82'
    base64_data = base64.b64encode(png_data).decode('utf-8')
    return f"data:image/png;base64,{base64_data}"

def register_user(email_suffix):
    """Register a new user and return token"""
    user_data = {
        "full_name": f"Edge Test User {email_suffix}",
        "email": f"edge.test.{email_suffix}@example.com",
        "password": "TestPassword123!",
        "role": "shopper"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    if response.status_code == 201:
        return response.json()["token"]["access_token"]
    return None

def get_shop_id():
    """Get an existing shop ID"""
    response = requests.get(f"{BASE_URL}/shops")
    if response.status_code == 200:
        shops = response.json()["data"]
        if shops:
            return shops[0]["id"]
    return None

def test_edge_case(test_name, review_data, expect_success=False, expected_error_keywords=None):
    """Test an edge case scenario"""
    print(f"\n🧪 Testing: {test_name}")
    
    # Register new user
    timestamp = int(time.time() * 1000)
    token = register_user(timestamp)
    if not token:
        print("   ❌ FAIL: Could not register user")
        return False
    
    # Get shop ID
    shop_id = get_shop_id()
    if not shop_id:
        print("   ❌ FAIL: Could not get shop ID")
        return False
    
    # Add shop_id to review data
    review_data["shop_id"] = shop_id
    
    # Make request
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/reviews", json=review_data, headers=headers)
    
    print(f"   Response Status: {response.status_code}")
    
    if expect_success:
        if response.status_code == 201:
            data = response.json()
            print(f"   ✅ PASS: Review created successfully")
            return True
        else:
            print(f"   ❌ FAIL: Expected success, got {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    else:
        if response.status_code == 400:
            error_data = response.json()
            error_detail = error_data.get('detail', '').lower()
            print(f"   Error Detail: {error_data.get('detail', 'Unknown error')}")
            
            if expected_error_keywords:
                for keyword in expected_error_keywords:
                    if keyword.lower() in error_detail:
                        print(f"   ✅ PASS: Correctly rejected with expected error")
                        return True
                print(f"   ❌ FAIL: Error doesn't contain expected keywords: {expected_error_keywords}")
                return False
            else:
                print(f"   ✅ PASS: Correctly rejected with 400 error")
                return True
        else:
            print(f"   ❌ FAIL: Expected 400 error, got {response.status_code}")
            return False

def main():
    print("🚀 Review Evidence Edge Cases Testing")
    print("=" * 60)
    
    test_results = []
    
    # Test 1: Low-star review with photos but no order number
    result1 = test_edge_case(
        "Low-Star Review with Photos but No Order Number",
        {
            "rating": 2,
            "comment": "Poor service and quality issues with the product delivery.",
            "proof_photos": [create_test_image()]
            # Missing proof_order_number
        },
        expect_success=False,
        expected_error_keywords=["bestellnummer", "order"]
    )
    test_results.append(("Photos but No Order Number", result1))
    
    # Test 2: Low-star review with order number but no photos
    result2 = test_edge_case(
        "Low-Star Review with Order Number but No Photos",
        {
            "rating": 2,
            "comment": "Poor service and quality issues with the product delivery.",
            "proof_order_number": "ORD-2024-TEST123"
            # Missing proof_photos
        },
        expect_success=False,
        expected_error_keywords=["foto", "photo"]
    )
    test_results.append(("Order Number but No Photos", result2))
    
    # Test 3: Invalid base64 image data
    result3 = test_edge_case(
        "Low-Star Review with Invalid Base64 Image",
        {
            "rating": 1,
            "comment": "Terrible product quality and customer service experience.",
            "proof_photos": ["invalid_base64_data_not_an_image"],
            "proof_order_number": "ORD-2024-INVALID"
        },
        expect_success=False,
        expected_error_keywords=["bild", "image", "datei"]
    )
    test_results.append(("Invalid Base64 Image", result3))
    
    # Test 4: Too many photos (more than 5)
    result4 = test_edge_case(
        "Low-Star Review with Too Many Photos",
        {
            "rating": 1,
            "comment": "Terrible product quality and customer service experience.",
            "proof_photos": [create_test_image() for _ in range(6)],  # 6 photos (limit is 5)
            "proof_order_number": "ORD-2024-TOOMANY"
        },
        expect_success=False,
        expected_error_keywords=["5", "maximal"]
    )
    test_results.append(("Too Many Photos", result4))
    
    # Test 5: Empty proof_photos array
    result5 = test_edge_case(
        "Low-Star Review with Empty Photos Array",
        {
            "rating": 2,
            "comment": "Poor service and quality issues with the product delivery.",
            "proof_photos": [],  # Empty array
            "proof_order_number": "ORD-2024-EMPTY"
        },
        expect_success=False,
        expected_error_keywords=["foto", "photo"]
    )
    test_results.append(("Empty Photos Array", result5))
    
    # Test 6: Very short order number
    result6 = test_edge_case(
        "Low-Star Review with Very Short Order Number",
        {
            "rating": 2,
            "comment": "Poor service and quality issues with the product delivery.",
            "proof_photos": [create_test_image()],
            "proof_order_number": "AB"  # Too short (minimum is 3 characters)
        },
        expect_success=False,
        expected_error_keywords=["bestellnummer", "order", "gültige"]
    )
    test_results.append(("Very Short Order Number", result6))
    
    # Test 7: Valid low-star review with minimum requirements
    result7 = test_edge_case(
        "Valid Low-Star Review with Minimum Requirements",
        {
            "rating": 2,
            "comment": "Poor service and quality issues with the product delivery.",
            "proof_photos": [create_test_image()],
            "proof_order_number": "ABC"  # Minimum 3 characters
        },
        expect_success=True
    )
    test_results.append(("Minimum Valid Requirements", result7))
    
    # Test 8: Valid low-star review with maximum photos (5)
    result8 = test_edge_case(
        "Valid Low-Star Review with Maximum Photos",
        {
            "rating": 1,
            "comment": "Terrible product quality and customer service experience.",
            "proof_photos": [create_test_image() for _ in range(5)],  # Exactly 5 photos
            "proof_order_number": "ORD-2024-MAX5"
        },
        expect_success=True
    )
    test_results.append(("Maximum Valid Photos", result8))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 EDGE CASES TEST SUMMARY")
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
        print("\n🎉 All edge case tests passed! Review evidence validation is robust.")
        return True
    else:
        print(f"\n❌ {total - passed} edge case test(s) failed.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)