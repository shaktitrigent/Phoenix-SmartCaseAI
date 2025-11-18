"""
Unit tests for the BDD generator.
"""

import pytest
from phoenix_smartcaseai import StoryBDDGenerator, generate_bdd_from_story
from phoenix_smartcaseai.generator import TestCase, BDDScenario


def test_testcase_model():
    """Test TestCase Pydantic model."""
    test_case = TestCase(
        id=1,
        title="Test Login",
        description="Test user login functionality",
        steps=["Navigate to login page", "Enter credentials", "Click login"],
        expected="User is logged in successfully",
        type="positive"
    )
    
    assert test_case.id == 1
    assert test_case.title == "Test Login"
    assert len(test_case.steps) == 3


def test_bdd_scenario_model():
    """Test BDDScenario Pydantic model."""
    scenario = BDDScenario(
        feature="User Authentication",
        scenario="User logs in with valid credentials",
        given=["the user is on the login page", "the user has valid credentials"],
        when=["the user enters their username", "the user enters their password", "the user clicks login"],
        then=["the system authenticates the user", "the user is redirected to dashboard"]
    )
    
    assert scenario.feature == "User Authentication"
    assert len(scenario.given) == 2
    assert len(scenario.when) == 3
    assert len(scenario.then) == 2

@pytest.mark.skip(reason="Requires wrong API keys - integration test")
def test_generator_initialization_without_api_key():
    """Test generator initialization without API key (should raise error)."""
    # This should raise an error if no API key is set
    with pytest.raises((ValueError, Exception)):
        generator = StoryBDDGenerator(llm_provider="openaii")

@pytest.mark.skip(reason="Requires API keys - integration test")
def test_generator_initialization_with_invalid_provider():
    """Test generator initialization with an invalid llm_provider name (should raise error)."""
    with pytest.raises((ValueError, Exception)) as excinfo:
        # Pass an intentionally bad provider name
        generator = StoryBDDGenerator(llm_provider="nonexistent_llm")
    assert "nonexistent_llm" in str(excinfo.value), "The exception message should mention the invalid provider name."


@pytest.mark.skip(reason="Requires API keys - integration test")
def test_generate_bdd_from_story():
    """Test the convenience function for generating BDD scenarios."""
    user_story = "As a user, I want to log in so I can access my dashboard."
    
    # This test requires API keys, so it's skipped by default
    scenarios = generate_bdd_from_story(
        user_story=user_story,
        llm_provider="openai",
        num_cases=2
    )
    
    assert isinstance(scenarios, list)
    assert len(scenarios) > 0
    assert "scenario" in scenarios[0]
    assert "feature" in scenarios[0]


@pytest.mark.skip(reason="Requires API keys - integration test")
def test_generator_generate_test_cases():
    """Test generating test cases with the generator."""
    generator = StoryBDDGenerator(llm_provider="openai")
    
    user_story = "As a user, I want to reset my password."
    cases = generator.generate_test_cases(
        user_story=user_story,
        output_format="bdd",
        num_cases=3
    )
    
    assert isinstance(cases, list)
    assert len(cases) <= 3
    for case in cases:
        assert "scenario" in case
        assert "feature" in case
        assert "given" in case
        assert "when" in case
        assert "then" in case


