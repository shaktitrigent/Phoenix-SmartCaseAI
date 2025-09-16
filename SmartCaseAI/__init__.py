"""
Phoenix-SmartCaseAI: AI-Powered Test Case Generation

A Python package for generating comprehensive test cases from user stories
using Large Language Models (LLMs). Supports both Plain English and BDD/Gherkin
formats with export to markdown files.

Example usage:
    from SmartCaseAI import StoryBDDGenerator
    
    generator = StoryBDDGenerator(llm_provider="openai")
    
    user_story = "As a user, I want to login..."
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

For more information, visit: https://github.com/yourusername/Phoenix-SmartCaseAI
"""

from ._version import __version__, __version_info__, __status__, __author__, __email__, __license__
from .generator import (
    StoryBDDGenerator,
    TestCase,
    BDDScenario,
    TestCaseList,
    BDDScenarioList
)

# Public API - only expose what users need
__all__ = [
    "StoryBDDGenerator",
    "TestCase", 
    "BDDScenario",
    "__version__",
    "__author__",
    "__email__"
]
