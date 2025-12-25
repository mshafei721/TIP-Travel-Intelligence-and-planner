"""
Tests for BaseAgent abstract class

Following TDD RED-GREEN-REFACTOR:
1. RED: Write tests that MUST fail (because BaseAgent doesn't exist yet)
2. GREEN: Implement minimal BaseAgent to make tests pass
3. REFACTOR: Improve code while keeping tests green
"""

from datetime import datetime
from typing import Any

import pytest

# These imports will fail initially (RED phase)
from app.agents.base import BaseAgent
from app.agents.config import AgentConfig
from app.agents.exceptions import AgentExecutionError
from app.agents.interfaces import AgentResult, SourceReference


class MockAgent(BaseAgent):
    """
    Mock implementation of BaseAgent for testing

    This concrete class implements all abstract methods
    so we can test BaseAgent functionality.
    """

    def configure_tools(self) -> list[Any]:
        """Return empty tools list for testing"""
        return []

    def create_task(self, input_data: dict[str, Any]) -> Any:
        """Create mock task for testing"""
        return {"description": "mock task", "input": input_data}

    def run(self, input_data: dict[str, Any]) -> AgentResult:
        """Execute mock agent logic"""
        return AgentResult(
            agent_type="mock",
            trip_id=input_data.get("trip_id", "test-123"),
            generated_at=datetime.utcnow(),
            confidence_score=0.95,
            data={"result": "success"},
            sources=[
                SourceReference(
                    url="https://example.com",
                    title="Test Source",
                    verified_at=datetime.utcnow(),
                )
            ],
            error=None,
        )


class TestBaseAgent:
    """Test suite for BaseAgent abstract class"""

    def test_base_agent_is_abstract(self):
        """BaseAgent should be abstract and cannot be instantiated directly"""
        with pytest.raises(TypeError):
            # This should fail because BaseAgent has abstract methods
            BaseAgent(config=AgentConfig())

    def test_mock_agent_instantiation(self):
        """MockAgent should instantiate successfully with default config"""
        config = AgentConfig()
        agent = MockAgent(config=config)

        assert agent is not None
        assert isinstance(agent, BaseAgent)
        assert agent.config == config

    def test_mock_agent_instantiation_with_custom_config(self):
        """MockAgent should accept custom configuration"""
        config = AgentConfig(
            llm_model="claude-3-opus-20240229",
            temperature=0.5,
            max_tokens=2000,
            verbose=False,
        )
        agent = MockAgent(config=config)

        assert agent.config.llm_model == "claude-3-opus-20240229"
        assert agent.config.temperature == 0.5
        assert agent.config.max_tokens == 2000
        assert agent.config.verbose is False

    def test_configure_tools_is_abstract(self):
        """configure_tools must be implemented by subclasses"""
        # MockAgent implements this, so it should work
        agent = MockAgent(config=AgentConfig())
        tools = agent.configure_tools()

        assert isinstance(tools, list)

    def test_create_task_is_abstract(self):
        """create_task must be implemented by subclasses"""
        agent = MockAgent(config=AgentConfig())
        task = agent.create_task({"trip_id": "test-123"})

        assert task is not None
        assert "description" in task

    def test_run_is_abstract(self):
        """run must be implemented by subclasses"""
        agent = MockAgent(config=AgentConfig())
        result = agent.run({"trip_id": "test-456"})

        assert isinstance(result, AgentResult)
        assert result.agent_type == "mock"
        assert result.trip_id == "test-456"
        assert result.confidence_score > 0.0

    def test_agent_result_structure(self):
        """AgentResult should have all required fields"""
        agent = MockAgent(config=AgentConfig())
        result = agent.run({"trip_id": "test-789"})

        # Required fields
        assert hasattr(result, "agent_type")
        assert hasattr(result, "trip_id")
        assert hasattr(result, "generated_at")
        assert hasattr(result, "confidence_score")
        assert hasattr(result, "data")
        assert hasattr(result, "sources")
        assert hasattr(result, "error")

        # Types
        assert isinstance(result.agent_type, str)
        assert isinstance(result.trip_id, str)
        assert isinstance(result.generated_at, datetime)
        assert isinstance(result.confidence_score, float)
        assert isinstance(result.data, dict)
        assert isinstance(result.sources, list)

        # Constraints
        assert 0.0 <= result.confidence_score <= 1.0

    def test_source_reference_structure(self):
        """SourceReference should have all required fields"""
        agent = MockAgent(config=AgentConfig())
        result = agent.run({"trip_id": "test-101"})

        assert len(result.sources) > 0
        source = result.sources[0]

        assert hasattr(source, "url")
        assert hasattr(source, "title")
        assert hasattr(source, "verified_at")

        assert isinstance(source.url, str)
        assert isinstance(source.title, str)
        assert isinstance(source.verified_at, datetime)

    def test_agent_config_defaults(self):
        """AgentConfig should have sensible defaults"""
        config = AgentConfig()

        assert config.llm_model == "claude-3-5-sonnet-20241022"
        assert config.temperature == 0.1
        assert config.max_tokens == 4000
        assert config.verbose is True

    def test_agent_execution_error(self):
        """AgentExecutionError should be raisable"""
        with pytest.raises(AgentExecutionError):
            raise AgentExecutionError("Test error message")


class TestAgentResultValidation:
    """Test Pydantic validation for AgentResult"""

    def test_agent_result_requires_all_fields(self):
        """AgentResult should require all mandatory fields"""
        with pytest.raises(Exception):  # Pydantic ValidationError
            AgentResult(
                agent_type="test",
                # Missing trip_id
                generated_at=datetime.utcnow(),
                confidence_score=0.9,
                data={},
                sources=[],
            )

    def test_confidence_score_validation(self):
        """Confidence score should be between 0.0 and 1.0"""
        # Valid confidence scores
        result = AgentResult(
            agent_type="test",
            trip_id="test-123",
            generated_at=datetime.utcnow(),
            confidence_score=0.95,
            data={},
            sources=[],
            error=None,
        )
        assert result.confidence_score == 0.95

        # Test boundary values
        result_min = AgentResult(
            agent_type="test",
            trip_id="test-124",
            generated_at=datetime.utcnow(),
            confidence_score=0.0,
            data={},
            sources=[],
        )
        assert result_min.confidence_score == 0.0

        result_max = AgentResult(
            agent_type="test",
            trip_id="test-125",
            generated_at=datetime.utcnow(),
            confidence_score=1.0,
            data={},
            sources=[],
        )
        assert result_max.confidence_score == 1.0
