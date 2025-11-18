"""
Phoenix-SmartCaseAI: AI-Powered Test Case Generation

A Python package for generating comprehensive test cases from user stories
using Large Language Models (LLMs). Supports both Plain English and BDD/Gherkin
formats with export to markdown files.

Example usage:
    from phoenix_smartcaseai import generate_bdd_from_story, StoryBDDGenerator
    
    # Simple function call
    scenarios = generate_bdd_from_story("As a user, I want to log in so I can access my dashboard.")
    
    # Or use the class directly
    generator = StoryBDDGenerator(llm_provider="openai")
    test_cases = generator.generate_test_cases(user_story, output_format="bdd")
    
    # Or export directly to markdown files
    file_paths = generator.export_to_markdown(
        user_story=user_story,
        output_dir="test_cases",
        filename_prefix="login_tests"
    )

Classes:
    StoryBDDGenerator: Main class for generating test cases
    TestCase: Pydantic model for plain English test cases
    BDDScenario: Pydantic model for BDD scenarios
    UnifiedFileAnalyzer: File analysis for additional context

For more information, visit: https://github.com/shaktitrigent/Phoenix-SmartCaseAI
"""

from ._version import __version__, __version_info__, __status__, __author__, __email__, __license__
from .generator import (
    StoryBDDGenerator,
    TestCase,
    BDDScenario,
    TestCaseList,
    BDDScenarioList
)
from .unified_file_analyzer import UnifiedFileAnalyzer, FileAnalysisResult

# Provide backward compatibility alias
FileAnalyzer = UnifiedFileAnalyzer


def generate_bdd_from_story(
    user_story: str,
    llm_provider: str = "openai",
    num_cases: int = 5,
    api_keys: dict = None
) -> list:
    """
    Convenience function to generate BDD scenarios from a user story.
    
    Args:
        user_story: The user story to generate tests for
        llm_provider: LLM provider to use ("openai", "gemini", "claude", or "all")
        num_cases: Number of test cases to generate (default: 5)
        api_keys: Optional dictionary of API keys for different providers
        
    Returns:
        List of dictionaries containing BDD scenario data
        
    Example:
        >>> scenarios = generate_bdd_from_story("As a user, I want to log in so I can access my dashboard.")
        >>> print(scenarios[0]['scenario'])
    """
    generator = StoryBDDGenerator(llm_provider=llm_provider, api_keys=api_keys)
    return generator.generate_test_cases(
        user_story=user_story,
        output_format="bdd",
        num_cases=num_cases
    )


def generate_plain_from_story(
    user_story: str,
    llm_provider: str = "openai",
    num_cases: int = 5,
    api_keys: dict = None
) -> list:
    """
    Convenience function to generate plain English test cases from a user story.
    
    Args:
        user_story: The user story to generate tests for
        llm_provider: LLM provider to use ("openai", "gemini", "claude", or "all")
        num_cases: Number of test cases to generate (default: 5)
        api_keys: Optional dictionary of API keys for different providers
        
    Returns:
        List of dictionaries containing test case data
        
    Example:
        >>> cases = generate_plain_from_story("As a user, I want to log in so I can access my dashboard.")
        >>> print(cases[0]['title'])
    """
    generator = StoryBDDGenerator(llm_provider=llm_provider, api_keys=api_keys)
    return generator.generate_test_cases(
        user_story=user_story,
        output_format="plain",
        num_cases=num_cases
    )


# Public API - only expose what users need
__all__ = [
    "StoryBDDGenerator",
    "TestCase", 
    "BDDScenario",
    "UnifiedFileAnalyzer",
    "FileAnalysisResult",
    "FileAnalyzer",  # Legacy support
    "generate_bdd_from_story",
    "generate_plain_from_story",
    "__version__",
    "__author__",
    "__email__"
]


