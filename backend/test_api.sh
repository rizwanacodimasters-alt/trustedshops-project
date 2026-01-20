#!/bin/bash

# TrustedShops API Testing Script
# This script helps you test the API endpoints

API_URL="http://localhost:8001/api"

echo "=========================================="
echo "TrustedShops API Testing"
echo "=========================================="
echo ""

# Function to test login
test_login() {
    local email=$1
    local password=$2
    local role=$3
    
    echo "Testing login for: $role ($email)"
    
    response=$(curl -s -X POST "$API_URL/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$email\",\"password\":\"$password\"}")
    
    echo "Response: $response" | python3 -m json.tool
    
    # Extract token
    token=$(echo $response | python3 -c "import sys, json; print(json.load(sys.stdin)['token']['access_token'])" 2>/dev/null)
    
    if [ ! -z "$token" ]; then
        echo "✓ Login successful!"
        echo "Token: $token"
        echo ""
        return 0
    else
        echo "✗ Login failed"
        echo ""
        return 1
    fi
}

# Function to test authenticated endpoint
test_authenticated() {
    local token=$1
    local endpoint=$2
    
    echo "Testing: GET $endpoint"
    curl -s -X GET "$API_URL$endpoint" \
        -H "Authorization: Bearer $token" | python3 -m json.tool
    echo ""
}

echo "1. ADMIN LOGIN TEST"
echo "==================="
admin_response=$(curl -s -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@trustedshops.com","password":"admin123"}')

echo "$admin_response" | python3 -m json.tool
admin_token=$(echo $admin_response | python3 -c "import sys, json; print(json.load(sys.stdin)['token']['access_token'])" 2>/dev/null)

if [ ! -z "$admin_token" ]; then
    echo ""
    echo "✓ Admin login successful!"
    echo "Admin Token: $admin_token"
    echo ""
    
    echo "2. TESTING ADMIN ENDPOINTS"
    echo "=========================="
    
    echo "a) Admin Dashboard:"
    curl -s -X GET "$API_URL/admin/dashboard/overview" \
        -H "Authorization: Bearer $admin_token" | python3 -m json.tool
    echo ""
    
    echo "b) All Users:"
    curl -s -X GET "$API_URL/admin/users?limit=5" \
        -H "Authorization: Bearer $admin_token" | python3 -m json.tool
    echo ""
fi

echo ""
echo "3. SHOP OWNER LOGIN TEST"
echo "========================"
owner_response=$(curl -s -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"owner@shop.com","password":"owner123"}')

echo "$owner_response" | python3 -m json.tool
owner_token=$(echo $owner_response | python3 -c "import sys, json; print(json.load(sys.stdin)['token']['access_token'])" 2>/dev/null)

if [ ! -z "$owner_token" ]; then
    echo ""
    echo "✓ Shop Owner login successful!"
    echo "Owner Token: $owner_token"
fi

echo ""
echo "4. CUSTOMER LOGIN TEST"
echo "======================"
customer_response=$(curl -s -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"customer@test.com","password":"customer123"}')

echo "$customer_response" | python3 -m json.tool
customer_token=$(echo $customer_response | python3 -c "import sys, json; print(json.load(sys.stdin)['token']['access_token'])" 2>/dev/null)

if [ ! -z "$customer_token" ]; then
    echo ""
    echo "✓ Customer login successful!"
    echo "Customer Token: $customer_token"
fi

echo ""
echo "=========================================="
echo "QUICK TEST COMMANDS"
echo "=========================================="
echo ""
echo "# Login as Admin:"
echo "curl -X POST $API_URL/auth/login -H 'Content-Type: application/json' -d '{\"email\":\"admin@trustedshops.com\",\"password\":\"admin123\"}'"
echo ""
echo "# Get Admin Dashboard (replace TOKEN):"
echo "curl -X GET $API_URL/admin/dashboard/overview -H 'Authorization: Bearer TOKEN'"
echo ""
echo "# Get All Users (replace TOKEN):"
echo "curl -X GET $API_URL/admin/users -H 'Authorization: Bearer TOKEN'"
echo ""
echo "# Get All Shops:"
echo "curl -X GET $API_URL/shops"
echo ""
echo "# Get Statistics:"
echo "curl -X GET $API_URL/statistics"
echo ""
