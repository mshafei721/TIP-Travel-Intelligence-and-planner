"""
BaseAgent - Abstract base class for all AI agents

This module defines the common interface that all agents must implement.
It provides the foundation for the multi-agent system architecture.

Key Design Principles:
1. Abstract class enforces consistent interface across all agents
2. Each agent specializes in one domain (single responsibility)
3. All agents return standardized AgentResult format
4. Configuration is validated via Pydantic
5. Error handling is consistent across agents

Usage:
    class VisaAgent(BaseAgent):
        def configure_tools(self) -> List[Any]:
            return [sherpa_api_tool, iata_tool]

        def create_task(self, input_data: Dict[str, Any]) -> Any:
            return Task(description="...", agent=self.agent)

        def run(self, input_data: Dict[str, Any]) -> AgentResult:
            # Execute agent logic
            return AgentResult(...)
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from app.agents.config import AgentConfig
from app.agents.interfaces import AgentResult


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents

    All agents must inherit from this class and implement:
    - configure_tools(): Setup agent-specific tools (APIs, scrapers, etc.)
    - create_task(): Define the task for the agent to execute
    - run(): Execute the agent and return results

    Attributes:
        config: Agent configuration (LLM model, temperature, etc.)

    Note:
        Subclasses can either:
        1. Pass config to __init__ (traditional approach for testing)
        2. Define a @property config that returns AgentConfig (for CrewAI agents)
    """

    _config: Optional[AgentConfig] = None

    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Initialize base agent with optional configuration

        Args:
            config: Agent configuration object (optional - can use property instead)

        Raises:
            TypeError: If instantiated directly (must use subclass)
        """
        if type(self) is BaseAgent:
            raise TypeError("BaseAgent cannot be instantiated directly. Use a subclass.")

        if config is not None:
            self._config = config

    @property
    def config(self) -> AgentConfig:
        """
        Get agent configuration.

        Can be overridden by subclasses to provide dynamic config.
        """
        if self._config is not None:
            return self._config
        # Subclasses should override this property if not using __init__ config
        raise NotImplementedError(
            f"{self.__class__.__name__} must either pass config to __init__ "
            "or override the config property"
        )

    @config.setter
    def config(self, value: AgentConfig) -> None:
        """Set agent configuration."""
        self._config = value

    def configure_tools(self) -> list[Any]:
        """
        Configure agent-specific tools (optional - can be overridden by subclasses)

        Tools can include:
        - External API clients (Sherpa, IATA, weather APIs, etc.)
        - Web scrapers (Playwright for embassy websites)
        - Database queries
        - File processors

        Returns:
            List of tool objects for the agent to use

        Note:
            This method is optional. Current CrewAI agents create tools
            directly in their initialization methods instead.

        Example:
            def configure_tools(self):
                return [
                    SherpaAPITool(api_key=settings.SHERPA_API_KEY),
                    IATATool(credentials=settings.IATA_CREDS),
                    EmbassyScraperTool()
                ]
        """
        return []

    def create_task(self, input_data: dict[str, Any]) -> Any:
        """
        Create task definition for agent execution (optional - can be overridden by subclasses)

        The task defines:
        - What the agent should do
        - Expected input format
        - Expected output format
        - Success criteria

        Args:
            input_data: Input parameters for the task (trip details, preferences, etc.)

        Returns:
            Task object (implementation varies by agent framework)

        Note:
            This method is optional. Current CrewAI agents create tasks
            directly in their run() methods using helper functions.

        Example:
            def create_task(self, input_data):
                return Task(
                    description=f"Find visa requirements for {input_data['destination']}",
                    agent=self.agent,
                    expected_output="JSON with visa requirements"
                )
        """
        return None

    @abstractmethod
    def run(self, input_data: dict[str, Any]) -> AgentResult:
        """
        Execute the agent and return results

        This is the main entry point for agent execution.
        It should:
        1. Validate input data
        2. Execute agent logic (call APIs, run LLM, etc.)
        3. Format results into AgentResult
        4. Handle errors gracefully

        Args:
            input_data: Agent input parameters

        Returns:
            AgentResult with execution results, confidence score, and sources

        Raises:
            AgentExecutionError: If agent fails to execute
            AgentValidationError: If input/output validation fails
            AgentTimeoutError: If execution exceeds timeout

        Example:
            def run(self, input_data):
                try:
                    # 1. Validate input
                    self._validate_input(input_data)

                    # 2. Execute agent
                    result = self.agent.execute(input_data)

                    # 3. Return formatted result
                    return AgentResult(
                        agent_type="visa",
                        trip_id=input_data["trip_id"],
                        generated_at=datetime.utcnow(),
                        confidence_score=0.95,
                        data=result,
                        sources=[...]
                    )
                except Exception as e:
                    raise AgentExecutionError(f"Visa agent failed: {e}")
        """

    async def run_async(self, input_data: dict[str, Any]) -> AgentResult:
        """
        Execute the agent asynchronously

        This is a default implementation that wraps the synchronous run() method.
        Subclasses can override this for true async execution if needed.

        Args:
            input_data: Agent input parameters

        Returns:
            AgentResult with execution results

        Raises:
            AgentExecutionError: If agent fails to execute
        """
        import asyncio

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.run, input_data)

    def __repr__(self) -> str:
        """String representation of agent"""
        return f"{self.__class__.__name__}(config={self.config})"
