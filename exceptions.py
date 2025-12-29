"""
CompeteGrok Custom Exceptions Module.

This module defines custom exception classes for better error categorization
and handling in the CompeteGrok project.
"""

class CompeteGrokError(Exception):
    """Base exception class for CompeteGrok errors."""
    pass

class WorkflowError(CompeteGrokError):
    """Exception raised for workflow-related errors in LangGraph."""
    pass

class AgentError(CompeteGrokError):
    """Exception raised for agent invocation or processing errors."""
    pass

class DebateError(CompeteGrokError):
    """Exception raised for debate subgraph errors."""
    pass

class ConfigurationError(CompeteGrokError):
    """Exception raised for configuration or setup errors."""
    pass

class ToolError(CompeteGrokError):
    """Exception raised for tool execution errors."""
    pass

class FileProcessingError(CompeteGrokError):
    """Exception raised for file processing errors."""
    pass