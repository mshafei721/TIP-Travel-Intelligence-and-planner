"""
Agent Exceptions

Custom exceptions for agent execution errors and failures.
"""


class AgentExecutionError(Exception):
    """
    Raised when an agent fails to execute successfully

    This can be due to:
    - External API failures
    - Invalid input data
    - LLM errors
    - Timeout errors
    - Data validation errors
    """

    def __init__(
        self,
        message: str = "Agent execution failed",
        agent_name: str | None = None,
        original_error: Exception | None = None,
    ):
        """
        Initialize AgentExecutionError.

        Args:
            message: Error message description
            agent_name: Name of the agent that failed
            original_error: The original exception that caused this error
        """
        self.agent_name = agent_name
        self.original_error = original_error
        full_message = f"[{agent_name}] {message}" if agent_name else message
        super().__init__(full_message)


class AgentConfigurationError(Exception):
    """
    Raised when agent configuration is invalid

    This can be due to:
    - Missing required configuration
    - Invalid LLM model name
    - Invalid temperature or max_tokens
    """


class AgentTimeoutError(AgentExecutionError):
    """
    Raised when agent execution exceeds time limit
    """


class AgentValidationError(AgentExecutionError):
    """
    Raised when agent output fails validation
    """
