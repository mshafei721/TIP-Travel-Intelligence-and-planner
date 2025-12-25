"""
I2 Backend Integration Test - Manual Testing Script

This script tests the live backend API endpoints
Run this after getting a valid JWT token from the frontend

Usage:
1. Log in to frontend: http://localhost:3000/login
2. Get your token from browser console:
   JSON.parse(localStorage.getItem('sb-bsfmmxjoxwbcsbpjkmcn-auth-token')).access_token
3. Set TOKEN variable below
4. Run: python tests/integration_test_manual.py
"""

import json

import requests

# ============================================
# Configuration
# ============================================

BASE_URL = "http://localhost:8000"
TOKEN: str | None = None  # Set this to your JWT token from frontend

# ============================================
# Test Configuration
# ============================================

ENABLE_DESTRUCTIVE_TESTS = False  # Set to True to test account deletion

# ============================================
# Helper Functions
# ============================================


def get_headers():
    """Get headers with authorization"""
    if not TOKEN:
        raise ValueError("TOKEN not set! Get it from frontend localStorage")
    return {"Content-Type": "application/json", "Authorization": f"Bearer {TOKEN}"}


def print_response(response: requests.Response, test_name: str):
    """Pretty print response"""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    print(f"URL: {response.url}")

    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
    except:
        print(f"Response: {response.text}")

    return response


def assert_status(response: requests.Response, expected: int, test_name: str):
    """Assert response status code"""
    if response.status_code == expected:
        print(f"✅ PASS: {test_name}")
        return True
    else:
        print(f"❌ FAIL: {test_name} (Expected {expected}, got {response.status_code})")
        return False


# ============================================
# Test Cases
# ============================================


def test_health_check():
    """Test 1: Health check (no auth required)"""
    response = requests.get(f"{BASE_URL}/api/health")
    print_response(response, "Health Check")
    return assert_status(response, 200, "Health check should return 200")


def test_get_profile():
    """Test 2: GET /api/profile (authenticated)"""
    response = requests.get(f"{BASE_URL}/api/profile", headers=get_headers())
    print_response(response, "Get Profile")
    success = assert_status(response, 200, "Get profile should return 200")

    if success:
        data = response.json()
        assert "user" in data, "Response should contain 'user'"
        print(f"✅ Profile loaded: {data['user'].get('display_name', 'No name set')}")

    return success


def test_update_profile_name():
    """Test 3: PUT /api/profile - Update display name"""
    payload = {"display_name": "Integration Test User"}
    response = requests.put(f"{BASE_URL}/api/profile", headers=get_headers(), json=payload)
    print_response(response, "Update Profile Name")
    success = assert_status(response, 200, "Update profile should return 200")

    if success:
        data = response.json()
        assert data.get("display_name") == "Integration Test User"
        print(f"✅ Name updated to: {data['display_name']}")

    return success


def test_create_traveler_profile():
    """Test 4: PUT /api/profile/traveler - Create traveler profile"""
    payload = {
        "nationality": "US",
        "residency_country": "US",
        "residency_status": "citizen",
        "travel_style": "balanced",
    }
    response = requests.put(f"{BASE_URL}/api/profile/traveler", headers=get_headers(), json=payload)
    print_response(response, "Create Traveler Profile")
    success = assert_status(response, 200, "Create traveler profile should return 200")

    if success:
        data = response.json()
        assert data.get("nationality") == "US"
        print(f"✅ Traveler profile created: {data.get('nationality')}")

    return success


def test_update_traveler_profile():
    """Test 5: PUT /api/profile/traveler - Update existing"""
    payload = {"nationality": "GB", "travel_style": "luxury"}  # Change to UK
    response = requests.put(f"{BASE_URL}/api/profile/traveler", headers=get_headers(), json=payload)
    print_response(response, "Update Traveler Profile")
    success = assert_status(response, 200, "Update traveler profile should return 200")

    if success:
        data = response.json()
        assert data.get("nationality") == "GB"
        print(f"✅ Nationality updated to: {data.get('nationality')}")

    return success


def test_invalid_country_code():
    """Test 6: PUT /api/profile/traveler - Invalid country code (validation)"""
    payload = {"nationality": "USA"}  # Invalid: must be 2 letters
    response = requests.put(f"{BASE_URL}/api/profile/traveler", headers=get_headers(), json=payload)
    print_response(response, "Invalid Country Code")
    return assert_status(response, 422, "Invalid country code should return 422")


def test_update_preferences():
    """Test 7: PUT /api/profile/preferences - Update preferences"""
    payload = {
        "email_notifications": True,
        "push_notifications": False,
        "language": "en",
        "currency": "USD",
        "units": "metric",
    }
    response = requests.put(
        f"{BASE_URL}/api/profile/preferences", headers=get_headers(), json=payload
    )
    print_response(response, "Update Preferences")
    success = assert_status(response, 200, "Update preferences should return 200")

    if success:
        data = response.json()
        prefs = data.get("preferences", {})
        print(f"✅ Preferences updated: currency={prefs.get('currency')}")

    return success


def test_invalid_currency():
    """Test 8: PUT /api/profile/preferences - Invalid currency code"""
    payload = {"currency": "US"}  # Invalid: must be 3 letters
    response = requests.put(
        f"{BASE_URL}/api/profile/preferences", headers=get_headers(), json=payload
    )
    print_response(response, "Invalid Currency Code")
    return assert_status(response, 422, "Invalid currency should return 422")


def test_get_statistics():
    """Test 9: GET /api/profile/statistics"""
    response = requests.get(f"{BASE_URL}/api/profile/statistics", headers=get_headers())
    print_response(response, "Get Statistics")
    success = assert_status(response, 200, "Get statistics should return 200")

    if success:
        data = response.json()
        stats = data.get("statistics", {})
        print(
            f"✅ Stats: {stats.get('totalTrips')} trips, {stats.get('countriesVisited')} countries"
        )

    return success


def test_unauthenticated_access():
    """Test 10: Access without token (should fail)"""
    response = requests.get(f"{BASE_URL}/api/profile")  # No headers
    print_response(response, "Unauthenticated Access")
    return assert_status(response, 401, "Unauthenticated request should return 401")


def test_delete_account_wrong_confirmation():
    """Test 11: DELETE /api/profile - Wrong confirmation"""
    if not ENABLE_DESTRUCTIVE_TESTS:
        print("\n⚠️ SKIP: Destructive test disabled (ENABLE_DESTRUCTIVE_TESTS=False)")
        return True

    payload = {"confirmation": "DELETE MY ACCOUN"}  # Wrong text
    response = requests.delete(f"{BASE_URL}/api/profile", headers=get_headers(), json=payload)
    print_response(response, "Delete Account - Wrong Confirmation")
    return assert_status(response, 400, "Wrong confirmation should return 400")


# ============================================
# Main Test Runner
# ============================================


def run_all_tests():
    """Run all integration tests"""
    print("\n" + "=" * 60)
    print("I2 BACKEND INTEGRATION TESTS")
    print("=" * 60)

    if not TOKEN:
        print("\n❌ ERROR: TOKEN not set!")
        print("\nTo get your token:")
        print("1. Log in to http://localhost:3000/login")
        print("2. Open browser DevTools (F12) → Console")
        print(
            "3. Run: JSON.parse(localStorage.getItem('sb-bsfmmxjoxwbcsbpjkmcn-auth-token')).access_token"
        )
        print("4. Copy the token and set TOKEN variable in this script")
        return

    print(f"\n📍 Backend URL: {BASE_URL}")
    print(f"🔑 Token: {TOKEN[:20]}...{TOKEN[-20:]}")

    tests = [
        test_health_check,
        test_get_profile,
        test_update_profile_name,
        test_create_traveler_profile,
        test_update_traveler_profile,
        test_invalid_country_code,
        test_update_preferences,
        test_invalid_currency,
        test_get_statistics,
        test_unauthenticated_access,
        test_delete_account_wrong_confirmation,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(("PASS" if result else "FAIL", test.__name__))
        except Exception as e:
            print(f"\n❌ ERROR in {test.__name__}: {e}")
            results.append(("ERROR", test.__name__))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for r in results if r[0] == "PASS")
    failed = sum(1 for r in results if r[0] == "FAIL")
    errors = sum(1 for r in results if r[0] == "ERROR")

    for status, name in results:
        icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{icon} {status:5s} - {name}")

    print(
        f"\n📊 Results: {passed} passed, {failed} failed, {errors} errors out of {len(results)} tests"
    )

    if passed == len(results):
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️ {failed + errors} tests failed or errored")


if __name__ == "__main__":
    run_all_tests()
