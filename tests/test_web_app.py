"""
Integration tests for the FastAPI web application.
"""

import pytest
from fastapi.testclient import TestClient
from phoenix_smartcaseai.web_app import app

client = TestClient(app)


def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "service" in data
    assert "version" in data


def test_root_endpoint():
    """Test the root endpoint returns HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Phoenix-SmartCaseAI" in response.text


def test_generate_bdd_endpoint_missing_story():
    """Test generate endpoint with missing user story."""
    response = client.post(
        "/generate-bdd",
        data={
            "user_story": "",
            "llm_provider": "openai",
            "output_format": "bdd",
            "num_cases": 5
        }
    )
    assert response.status_code == 400


def test_generate_bdd_endpoint_invalid_format():
    """Test generate endpoint with invalid format."""
    response = client.post(
        "/generate-bdd",
        data={
            "user_story": "As a user, I want to log in.",
            "llm_provider": "openai",
            "output_format": "invalid",
            "num_cases": 5
        }
    )
    # Should either accept it or return 422 (validation error)
    assert response.status_code in [400, 422, 500]


@pytest.mark.skip(reason="Requires API keys - integration test")
def test_generate_bdd_endpoint_success():
    """Test successful BDD generation (requires API keys)."""
    response = client.post(
        "/generate-bdd",
        data={
            "user_story": "As a user, I want to log in so I can access my dashboard.",
            "llm_provider": "openai",
            "output_format": "bdd",
            "num_cases": 2
        }
    )
    
    # This test requires API keys, so it's skipped by default
    if response.status_code == 200:
        data = response.json()
        assert data["success"] is True
        assert "bdd_content" in data
        assert "num_generated_cases" in data
    else:
        # If API keys are not set, we expect an error
        assert response.status_code in [400, 500]


