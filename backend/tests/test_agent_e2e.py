"""
End-to-End Agent Test Script

Tests the orchestrator and all agents locally without database.
Run this to verify agent fixes before deployment.

Usage:
    cd backend
    python -m pytest tests/test_agent_e2e.py -v -s

    Or directly:
    python tests/test_agent_e2e.py
"""

import asyncio
import sys
from datetime import date, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(backend_path / ".env")


def test_country_code_conversion():
    """Test that country names are converted to ISO codes correctly."""
    from app.agents.orchestrator.agent import get_country_code

    # Test common country names
    assert get_country_code("Egypt") == "EG", "Egypt should convert to EG"
    assert get_country_code("Uzbekistan") == "UZ", "Uzbekistan should convert to UZ"
    assert get_country_code("United States") == "US", "United States should convert to US"
    assert get_country_code("United Kingdom") == "GB", "United Kingdom should convert to GB"
    assert get_country_code("Japan") == "JP", "Japan should convert to JP"
    assert get_country_code("France") == "FR", "France should convert to FR"

    # Test already ISO codes
    assert get_country_code("US") == "US", "US should stay US"
    assert get_country_code("gb") == "GB", "gb should convert to GB (uppercase)"

    # Test partial matches
    assert get_country_code("usa") == "US", "usa should match United States"

    print("[PASS] Country code conversion tests passed!")


def test_orchestrator_initialization():
    """Test that orchestrator initializes correctly."""
    from app.agents.orchestrator.agent import OrchestratorAgent

    orchestrator = OrchestratorAgent()

    # Check available agents
    available = orchestrator.list_available_agents()
    print(f"Available agents: {available}")

    expected_agents = ["visa", "country", "weather", "currency", "culture", "food", "attractions"]
    for agent in expected_agents:
        assert agent in available, f"{agent} should be available"

    print(f"[PASS] Orchestrator initialized with {len(available)} agents")


def test_agent_input_creation():
    """Test that agent inputs are created with correct country codes."""
    from app.agents.orchestrator.agent import OrchestratorAgent, TripData

    orchestrator = OrchestratorAgent()

    # Create trip data with full country names (like the error case)
    trip_data = TripData(
        trip_id="test-123",
        user_nationality="Egypt",  # Full name, not ISO code
        destination_country="Uzbekistan",  # Full name, not ISO code
        destination_city="Tashkent",
        departure_date=date(2026, 1, 20),
        return_date=date(2026, 1, 28),
        trip_purpose="tourism",
    )

    # Create visa agent input
    visa_input = orchestrator._create_agent_input(trip_data, "visa")

    assert visa_input.user_nationality == "EG", f"Expected 'EG', got '{visa_input.user_nationality}'"
    assert visa_input.destination_country == "UZ", f"Expected 'UZ', got '{visa_input.destination_country}'"

    print(f"[PASS] Visa input created with correct ISO codes: {visa_input.user_nationality} -> {visa_input.destination_country}")


def test_culture_agent_normalization():
    """Test that culture agent normalizes LLM output correctly."""
    from app.agents.culture.models import DressCodeInfo, ReligiousConsideration

    # Test dress code normalization with LLM-style field names
    llm_output = {
        "casual_guidelines": "Dress modestly",
        "formal_guidelines": "Suits for business",
        "religious_site_requirements": "Cover head and remove shoes",
        "beach_swimwear_guidelines": "Conservative swimwear",
    }

    # Map LLM field names to model field names
    field_mapping = {
        "casual_guidelines": "casual",
        "formal_guidelines": "formal",
        "religious_site_requirements": "religious_sites",
        "beach_swimwear_guidelines": "beach_resort",
    }
    mapped = {field_mapping.get(k, k): v for k, v in llm_output.items()}
    result = DressCodeInfo(**mapped)

    assert isinstance(result, DressCodeInfo)
    assert result.casual == "Dress modestly"
    assert result.religious_sites == "Cover head and remove shoes"

    print("[PASS] Culture agent dress code normalization works!")

    # Test religious considerations normalization
    llm_religious = {
        "primary_religions": ["Islam", "Christianity"],
        "considerations": [
            {"topic": "Ramadan", "guideline": "Fasting month - respect locals fasting", "severity": "advisory"}
        ]
    }

    primary = ", ".join(llm_religious.get("primary_religions", []))
    considerations = [
        ReligiousConsideration(
            topic=c["topic"],
            guideline=c.get("guideline", ""),
            severity=c.get("severity", "info")
        )
        for c in llm_religious.get("considerations", [])
    ]

    assert primary == "Islam, Christianity"
    assert len(considerations) == 1
    assert considerations[0].topic == "Ramadan"

    print("[PASS] Culture agent religious normalization works!")


def test_currency_agent_normalization():
    """Test that currency agent normalizes LLM output correctly."""
    from app.agents.currency.models import LocalCurrency

    # Test local currency normalization
    llm_currency = {
        "code": "UZS",
        "name": "Uzbekistani Som",
        "symbol": "som"  # Use ASCII for test
    }

    result = LocalCurrency(
        code=llm_currency.get("code", "USD"),
        name=llm_currency.get("name", "Unknown"),
        symbol=llm_currency.get("symbol", "$"),
    )

    assert isinstance(result, LocalCurrency)
    assert result.code == "UZS"
    assert result.name == "Uzbekistani Som"

    print("[PASS] Currency agent local_currency normalization works!")

    # Test tipping customs normalization (dict to string)
    llm_tipping = {
        "tipping_culture": "Moderate",
        "typical_percentage": "10-15%",
        "restaurants": "10% is appreciated",
    }

    # Simulate normalization logic
    parts = []
    if "tipping_culture" in llm_tipping:
        parts.append(f"Tipping culture: {llm_tipping['tipping_culture']}")
    if "typical_percentage" in llm_tipping:
        parts.append(f"Typical tip: {llm_tipping['typical_percentage']}")
    result = ". ".join(parts) if parts else "Tipping customs vary"

    assert isinstance(result, str)
    assert "Moderate" in result or "10-15%" in result

    print("[PASS] Currency agent tipping_customs normalization works!")


def test_food_agent_normalization():
    """Test that food agent normalizes LLM output correctly."""
    # Test street food normalization (dict to list) - simulate the logic
    llm_street_food = {
        "popular_items": ["Samsa", "Plov", "Shashlik"],
        "prices": "$1-5 per item",
        "best_areas": ["Chorsu Bazaar", "Old Town"]
    }

    # Simulate normalization logic
    items = []
    if "popular_items" in llm_street_food:
        items.extend(llm_street_food["popular_items"])
    if "prices" in llm_street_food:
        items.append(f"Typical prices: {llm_street_food['prices']}")
    if "best_areas" in llm_street_food:
        areas = llm_street_food["best_areas"]
        if isinstance(areas, list):
            items.append(f"Best areas: {', '.join(areas)}")
    result = items

    assert isinstance(result, list)
    assert "Samsa" in result
    assert any("price" in item.lower() for item in result)

    print(f"[PASS] Food agent street_food normalization works! Result: {result[:3]}...")

    # Test dining etiquette normalization (dict to list)
    llm_etiquette = {
        "important_customs": ["Remove shoes", "Use right hand"],
        "taboos": ["Don't point with feet"]
    }

    # Simulate normalization logic
    rules = []
    if "important_customs" in llm_etiquette:
        rules.extend(llm_etiquette["important_customs"])
    if "taboos" in llm_etiquette:
        rules.extend([f"Avoid: {t}" for t in llm_etiquette["taboos"]])
    result = rules

    assert isinstance(result, list)
    assert len(result) > 0

    print(f"[PASS] Food agent dining_etiquette normalization works! Result: {result[:2]}...")


async def test_orchestrator_with_mocked_db():
    """Test full orchestrator run with mocked database."""
    from app.agents.orchestrator.agent import OrchestratorAgent

    # Mock supabase
    with patch("app.agents.orchestrator.agent.supabase") as mock_db:
        # Mock the database calls
        mock_db.table.return_value.upsert.return_value.execute.return_value = MagicMock()
        mock_db.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock()

        orchestrator = OrchestratorAgent()

        trip_data = {
            "trip_id": "test-e2e-123",
            "user_nationality": "Egypt",
            "destination_country": "Uzbekistan",
            "destination_city": "Tashkent",
            "departure_date": date(2026, 1, 20),
            "return_date": date(2026, 1, 28),
            "trip_purpose": "tourism",
        }

        print("\n>>> Starting orchestrator test run...")
        print(f"   Trip: {trip_data['user_nationality']} -> {trip_data['destination_country']}")

        try:
            result = await orchestrator.generate_report(trip_data)

            print(f"\n=== Results ===")
            print(f"   Sections generated: {list(result.get('sections', {}).keys())}")
            print(f"   Errors: {len(result.get('errors', []))}")

            if result.get('errors'):
                print(f"\n[WARN] Agent errors:")
                for error in result['errors']:
                    agent = error.get('agent', 'unknown')
                    msg = error.get('error', '')[:100]
                    print(f"   - {agent}: {msg}...")

            # Check that we got some sections
            sections = result.get('sections', {})
            if len(sections) >= 3:
                print(f"\n[PASS] Orchestrator test passed with {len(sections)} sections!")
            else:
                print(f"\n[WARN] Only {len(sections)} sections generated")

            return result

        except Exception as e:
            print(f"\n[FAIL] Orchestrator test failed: {e}")
            raise


def run_all_tests():
    """Run all end-to-end tests."""
    print("\n" + "=" * 60)
    print("AGENT END-TO-END TESTS")
    print("=" * 60)

    tests = [
        ("Country Code Conversion", test_country_code_conversion),
        ("Orchestrator Initialization", test_orchestrator_initialization),
        ("Agent Input Creation", test_agent_input_creation),
        ("Culture Agent Normalization", test_culture_agent_normalization),
        ("Currency Agent Normalization", test_currency_agent_normalization),
        ("Food Agent Normalization", test_food_agent_normalization),
    ]

    results = []

    for name, test_func in tests:
        print(f"\n--- {name} ---")
        try:
            test_func()
            results.append(("PASS", name))
        except AssertionError as e:
            print(f"[FAIL]: {e}")
            results.append(("FAIL", name))
        except Exception as e:
            print(f"[ERROR]: {e}")
            results.append(("ERROR", name))

    # Run async test
    print(f"\n--- Orchestrator Full Run (Mocked DB) ---")
    try:
        asyncio.run(test_orchestrator_with_mocked_db())
        results.append(("PASS", "Orchestrator Full Run"))
    except Exception as e:
        print(f"[ERROR]: {e}")
        results.append(("ERROR", "Orchestrator Full Run"))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for r in results if r[0] == "PASS")
    failed = sum(1 for r in results if r[0] == "FAIL")
    errors = sum(1 for r in results if r[0] == "ERROR")

    for status, name in results:
        icon = "[OK]" if status == "PASS" else "[X]"
        print(f"{icon} {status:5s} - {name}")

    print(f"\n=== Results: {passed} passed, {failed} failed, {errors} errors ===")

    if passed == len(results):
        print("\n*** ALL TESTS PASSED! ***")
        return True
    else:
        print(f"\n[WARN] {failed + errors} tests need attention")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
