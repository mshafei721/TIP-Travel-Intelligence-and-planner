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
