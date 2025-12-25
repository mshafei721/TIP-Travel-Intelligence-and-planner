#!/usr/bin/env python3
"""
TIP - Credential Validation Script
Validates all environment variables and tests service connectivity
WITHOUT exposing actual secret values
"""

import os
import sys
from pathlib import Path
from typing import Tuple

# Try to import optional dependencies
try:
    from dotenv import load_dotenv

    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️  requests not installed. Install with: pip install requests")

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️  redis not installed. Install with: pip install redis")

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_header():
    """Print validation header"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}TIP - Credential Validation{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")


def mask_secret(value: str, show_chars: int = 4) -> str:
    """Mask a secret value, showing only first/last few characters"""
    if not value or len(value) < show_chars * 2:
        return "***"
    return f"{value[:show_chars]}...{value[-show_chars:]}"


def check_env_var(var_name: str, required: bool = True) -> Tuple[bool, str]:
    """Check if environment variable exists and has a value"""
    value = os.getenv(var_name)

    if not value or value.strip() == "":
        if required:
            return False, f"{RED}✗{RESET} Missing"
        else:
            return True, f"{YELLOW}⚠{RESET} Optional (empty)"

    # Check if it's still a placeholder
    placeholders = [
        "your_",
        "change_me",
        "xxxxx",
        "CHANGE_ME",
        "fill_in",
        "add_your",
        "get_from",
    ]
    if any(placeholder.lower() in value.lower() for placeholder in placeholders):
        return False, f"{RED}✗{RESET} Placeholder value detected"

    masked = mask_secret(value)
    return True, f"{GREEN}✓{RESET} Set ({masked})"


def test_supabase_connection() -> Tuple[bool, str]:
    """Test Supabase connectivity"""
    if not REQUESTS_AVAILABLE:
        return False, "requests library not available"

    url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")

    if not url or not anon_key:
        return False, "Missing credentials"

    try:
        # Test REST API health endpoint
        headers = {"apikey": anon_key, "Authorization": f"Bearer {anon_key}"}
        response = requests.get(f"{url}/rest/v1/", headers=headers, timeout=10)

        if response.status_code in [200, 401, 404]:  # 401/404 means API is reachable
            return True, f"{GREEN}✓{RESET} Connected"
        else:
            return False, f"HTTP {response.status_code}"
    except requests.exceptions.Timeout:
        return False, "Connection timeout"
    except requests.exceptions.ConnectionError:
        return False, "Connection failed"
    except Exception as e:
        return False, f"Error: {str(e)[:30]}"


def test_redis_connection() -> Tuple[bool, str]:
    """Test Redis connectivity"""
    if not REDIS_AVAILABLE:
        return False, "redis library not available"

    redis_url = os.getenv("REDIS_URL")

    if not redis_url:
        return False, "Missing REDIS_URL"

    try:
        r = redis.from_url(redis_url, socket_connect_timeout=5)
        r.ping()
        return True, f"{GREEN}✓{RESET} Connected"
    except redis.ConnectionError:
        return False, "Connection failed (is Redis running?)"
    except Exception as e:
        return False, f"Error: {str(e)[:30]}"


def validate_database_url() -> Tuple[bool, str]:
    """Validate DATABASE_URL format"""
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        return False, "Missing"

    # Check if it's a valid PostgreSQL URL
    if not db_url.startswith("postgresql://"):
        return False, "Invalid format (must start with postgresql://)"

    # Check if password placeholder is still there
    if "[YOUR-PASSWORD]" in db_url or "your_password" in db_url:
        return False, "Password placeholder not replaced"

    masked = mask_secret(db_url, 10)
    return True, f"{GREEN}✓{RESET} Valid format ({masked})"


def main():
    """Main validation function"""
    # Load .env file
    env_path = Path(__file__).parent / ".env"

    if not env_path.exists():
        print(f"{RED}✗ .env file not found!{RESET}")
        print(f"Expected location: {env_path}")
        sys.exit(1)

    if DOTENV_AVAILABLE:
        load_dotenv(env_path)
        print(f"{GREEN}✓{RESET} Loaded .env file from: {env_path}\n")
    else:
        print(f"{YELLOW}⚠{RESET} dotenv not available, reading from environment\n")

    print_header()

    # Track results
    results = {
        "required_missing": [],
        "optional_missing": [],
        "connectivity_failed": [],
    }

    # ==============================================
    # PHASE 1 REQUIREMENTS (CRITICAL)
    # ==============================================
    print(f"{BOLD}Phase 1 Requirements (Critical):{RESET}\n")

    print(f"{BOLD}Supabase (Database & Auth):{RESET}")
    required_supabase = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_JWT_SECRET",
        "DATABASE_URL",
    ]

    for var in required_supabase[:-1]:  # All except DATABASE_URL
        is_ok, status = check_env_var(var, required=True)
        print(f"  {var:30s} {status}")
        if not is_ok:
            results["required_missing"].append(var)

    # Special handling for DATABASE_URL
    is_ok, status = validate_database_url()
    print(f"  {'DATABASE_URL':30s} {status}")
    if not is_ok:
        results["required_missing"].append("DATABASE_URL")

    # Test Supabase connectivity
    print(f"\n  {BOLD}Testing Supabase connection...{RESET}")
    is_connected, status = test_supabase_connection()
    print(f"  {'Connectivity':30s} {status}")
    if not is_connected:
        results["connectivity_failed"].append(("Supabase", status))

    print(f"\n{BOLD}Redis & Celery:{RESET}")
    redis_vars = ["REDIS_URL", "CELERY_BROKER_URL", "CELERY_RESULT_BACKEND"]

    for var in redis_vars:
        is_ok, status = check_env_var(var, required=True)
        print(f"  {var:30s} {status}")
        if not is_ok:
            results["required_missing"].append(var)

    # Test Redis connectivity
    print(f"\n  {BOLD}Testing Redis connection...{RESET}")
    is_connected, status = test_redis_connection()
    print(f"  {'Connectivity':30s} {status}")
    if not is_connected:
        results["connectivity_failed"].append(("Redis", status))

    print(f"\n{BOLD}Application Settings:{RESET}")
    app_vars = ["SECRET_KEY", "FRONTEND_URL", "BACKEND_URL", "ENVIRONMENT"]

    for var in app_vars:
        is_ok, status = check_env_var(var, required=True)
        print(f"  {var:30s} {status}")
        if not is_ok:
            results["required_missing"].append(var)

    # ==============================================
    # PHASE 2+ REQUIREMENTS (OPTIONAL FOR NOW)
    # ==============================================
    print(f"\n{BOLD}Phase 2+ Requirements (Optional for now):{RESET}\n")

    optional_groups = {
        "LLM APIs (Phase 2+)": ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"],
        "Weather API (Phase 5)": ["WEATHER_API_KEY"],
        "Currency API (Phase 6)": ["CURRENCY_API_KEY"],
        "Visa API (Phase 3)": ["VISA_API_KEY"],
        "Flight API (Phase 11)": ["FLIGHT_API_KEY"],
        "Mapbox (Phase 9+)": ["MAPBOX_ACCESS_TOKEN"],
        "Scraping (Phase 4+)": ["FIRECRAWL_API_KEY", "APIFY_API_KEY"],
    }

    for group_name, vars_list in optional_groups.items():
        print(f"{BOLD}{group_name}:{RESET}")
        for var in vars_list:
            is_ok, status = check_env_var(var, required=False)
            print(f"  {var:30s} {status}")
        print()

    # ==============================================
    # SUMMARY
    # ==============================================
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}Validation Summary:{RESET}\n")

    if results["required_missing"]:
        print(f"{RED}✗ FAILED{RESET} - Missing required credentials:")
        for var in results["required_missing"]:
            print(f"  - {var}")
        print()

    if results["connectivity_failed"]:
        print(f"{YELLOW}⚠ WARNING{RESET} - Connectivity issues:")
        for service, reason in results["connectivity_failed"]:
            print(f"  - {service}: {reason}")
        print()

    if not results["required_missing"] and not results["connectivity_failed"]:
        print(f"{GREEN}✓ ALL PHASE 1 REQUIREMENTS MET!{RESET}")
        print(f"\n{GREEN}🚀 Ready to begin Phase 1 implementation{RESET}")
        print(f"{BLUE}{'='*60}{RESET}\n")
        return 0
    elif not results["required_missing"]:
        print(
            f"{YELLOW}⚠ Credentials configured but connectivity issues detected{RESET}"
        )
        print("   Fix connectivity issues before proceeding")
        print(f"{BLUE}{'='*60}{RESET}\n")
        return 1
    else:
        print(f"{RED}✗ Configuration incomplete{RESET}")
        print("   Please add missing credentials to .env file")
        print(f"{BLUE}{'='*60}{RESET}\n")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Validation cancelled{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Unexpected error: {e}{RESET}")
        sys.exit(1)
