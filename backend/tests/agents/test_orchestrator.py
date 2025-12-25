"""
Tests for Orchestrator Agent

Testing the orchestrator that coordinates all specialist agents
and generates complete travel reports.

TDD Approach:
1. Write tests (RED)
2. Implement minimal code (GREEN)
3. Refactor while keeping tests passing
"""

from datetime import date, datetime
from unittest.mock import Mock, patch

import pytest

from app.agents.interfaces import AgentResult
from app.agents.orchestrator.agent import OrchestratorAgent


class TestOrchestratorAgent:
    """Test suite for OrchestratorAgent"""

    def test_orchestrator_initialization(self):
        """Test that orchestrator initializes with agent registry"""
        orchestrator = OrchestratorAgent()

        # Should have a registry of available agents
        assert hasattr(orchestrator, "available_agents")
        assert isinstance(orchestrator.available_agents, dict)

        # At minimum should recognize visa agent
        assert "visa" in orchestrator.available_agents

    @pytest.mark.asyncio()
    async def test_orchestrator_generates_report_for_trip(self):
        """Test that orchestrator can generate a complete report"""
        orchestrator = OrchestratorAgent()

        trip_data = {
            "trip_id": "test-trip-123",
            "user_nationality": "US",
            "destination_country": "FR",
            "destination_city": "Paris",
            "departure_date": date(2025, 6, 1),
            "return_date": date(2025, 6, 15),
            "trip_purpose": "tourism",
        }

        # Should return a complete report
        result = await orchestrator.generate_report(trip_data)

        assert isinstance(result, dict)
        assert "trip_id" in result
        assert "sections" in result
        assert "generated_at" in result

    @pytest.mark.asyncio()
    async def test_orchestrator_runs_visa_agent(self):
        """Test that orchestrator runs visa agent"""
        orchestrator = OrchestratorAgent()

        trip_data = {
            "trip_id": "test-trip-456",
            "user_nationality": "US",
            "destination_country": "JP",
            "destination_city": "Tokyo",
            "departure_date": date(2025, 7, 1),
            "return_date": date(2025, 7, 14),
            "trip_purpose": "tourism",
        }

        result = await orchestrator.generate_report(trip_data)

        # Should have visa section
        assert "sections" in result
        assert "visa" in result["sections"]
        assert result["sections"]["visa"] is not None

    @pytest.mark.asyncio()
    async def test_orchestrator_handles_agent_failure_gracefully(self):
        """Test that orchestrator continues if one agent fails"""
        orchestrator = OrchestratorAgent()

        # Mock visa agent to fail
        with patch("app.agents.orchestrator.agent.VisaAgent") as mock_visa:
            mock_visa.return_value.run_async.side_effect = Exception("API failure")

            trip_data = {
                "trip_id": "test-trip-789",
                "user_nationality": "US",
                "destination_country": "GB",
                "destination_city": "London",
                "departure_date": date(2025, 8, 1),
                "return_date": date(2025, 8, 10),
                "trip_purpose": "tourism",
            }

            # Should not raise exception
            result = await orchestrator.generate_report(trip_data)

            # Should have error recorded
            assert "sections" in result
            assert "errors" in result
            assert len(result["errors"]) > 0

    @pytest.mark.asyncio()
    async def test_orchestrator_runs_agents_in_phases(self):
        """Test that orchestrator runs agents in correct phases"""
        orchestrator = OrchestratorAgent()

        # Track execution order
        execution_order = []

        async def track_execution(agent_name):
            execution_order.append(agent_name)
            return AgentResult(
                agent_type=agent_name,
                trip_id="test",
                generated_at=datetime.utcnow(),
                confidence_score=0.9,
                data={},
                sources=[],
                warnings=[],
            )

        # Mock agents
        with patch.object(orchestrator, "_run_agent", side_effect=track_execution):
            trip_data = {
                "trip_id": "test-phases",
                "user_nationality": "US",
                "destination_country": "IT",
                "destination_city": "Rome",
                "departure_date": date(2025, 9, 1),
                "return_date": date(2025, 9, 14),
                "trip_purpose": "tourism",
            }

            await orchestrator.generate_report(trip_data)

            # Visa should run in Phase 1 (independent agents)
            assert "visa" in execution_order

    @pytest.mark.asyncio()
    async def test_orchestrator_saves_results_to_database(self):
        """Test that orchestrator saves results to database"""
        orchestrator = OrchestratorAgent()

        trip_data = {
            "trip_id": "test-save-db",
            "user_nationality": "US",
            "destination_country": "ES",
            "destination_city": "Barcelona",
            "departure_date": date(2025, 10, 1),
            "return_date": date(2025, 10, 14),
            "trip_purpose": "tourism",
        }

        # Mock database save
        with patch("app.agents.orchestrator.agent.supabase") as mock_db:
            mock_db.table.return_value.insert.return_value.execute.return_value = None

            await orchestrator.generate_report(trip_data)

            # Should have called database save
            assert mock_db.table.called

    @pytest.mark.asyncio()
    async def test_orchestrator_updates_agent_job_status(self):
        """Test that orchestrator updates agent job status"""
        orchestrator = OrchestratorAgent()

        trip_data = {
            "trip_id": "test-job-status",
            "user_nationality": "US",
            "destination_country": "DE",
            "destination_city": "Berlin",
            "departure_date": date(2025, 11, 1),
            "return_date": date(2025, 11, 14),
            "trip_purpose": "tourism",
        }

        # Mock database
        with patch("app.agents.orchestrator.agent.supabase") as mock_db:
            mock_update = Mock()
            mock_db.table.return_value.update.return_value.eq.return_value.execute.return_value = (
                None
            )

            await orchestrator.generate_report(trip_data)

            # Should have updated job status
            assert mock_db.table.return_value.update.called

    def test_orchestrator_validates_trip_data(self):
        """Test that orchestrator validates trip data"""
        orchestrator = OrchestratorAgent()

        # Missing required fields
        invalid_data = {
            "trip_id": "test-invalid"
            # Missing nationality, destination, etc.
        }

        with pytest.raises(ValueError):
            orchestrator._validate_trip_data(invalid_data)

    def test_orchestrator_creates_agent_input(self):
        """Test that orchestrator creates proper agent input"""
        orchestrator = OrchestratorAgent()

        trip_data_dict = {
            "trip_id": "test-input",
            "user_nationality": "US",
            "destination_country": "AU",
            "destination_city": "Sydney",
            "departure_date": date(2025, 12, 1),
            "return_date": date(2025, 12, 14),
            "trip_purpose": "tourism",
        }

        # Validate trip data first
        trip_data = orchestrator._validate_trip_data(trip_data_dict)

        agent_input = orchestrator._create_agent_input(trip_data, "visa")

        assert agent_input.trip_id == "test-input"
        assert agent_input.user_nationality == "US"
        assert agent_input.destination_country == "AU"

    @pytest.mark.asyncio()
    async def test_orchestrator_aggregates_results(self):
        """Test that orchestrator aggregates results from all agents"""
        orchestrator = OrchestratorAgent()

        # Mock results from multiple agents (as dicts, not AgentResult objects)
        visa_result_dict = {
            "agent_type": "visa",
            "trip_id": "test-agg",
            "generated_at": datetime.utcnow().isoformat(),
            "confidence_score": 0.95,
            "data": {"visa_required": False},
            "sources": [],
            "warnings": [],
        }

        results = {"visa": visa_result_dict}

        aggregated = orchestrator._aggregate_results(results)

        assert "sections" in aggregated
        assert "visa" in aggregated["sections"]
        assert aggregated["sections"]["visa"]["confidence_score"] == 0.95

    def test_orchestrator_lists_available_agents(self):
        """Test that orchestrator can list available agents"""
        orchestrator = OrchestratorAgent()

        agents = orchestrator.list_available_agents()

        assert isinstance(agents, list)
        assert "visa" in agents

    def test_orchestrator_can_check_agent_availability(self):
        """Test that orchestrator can check if agent is available"""
        orchestrator = OrchestratorAgent()

        assert orchestrator.is_agent_available("visa") == True
        assert orchestrator.is_agent_available("nonexistent") == False
