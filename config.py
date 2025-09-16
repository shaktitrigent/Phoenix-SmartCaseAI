"""
Production configuration for Phoenix-SmartCaseAI

This module contains configuration settings for production deployment.
"""

import os
from typing import Optional, Dict, Any

class Config:
    """Production configuration class."""
    
    # API Configuration
    DEFAULT_LLM_PROVIDER = "openai"
    DEFAULT_MODEL = "gpt-4o-mini"
    API_TIMEOUT = 30  # seconds
    MAX_RETRIES = 3
    
    # Generation Defaults
    DEFAULT_NUM_CASES = 5
    MAX_NUM_CASES = 20
    DEFAULT_OUTPUT_DIR = "./test_cases"
    DEFAULT_FILENAME_PREFIX = "generated_tests"
    
    # File Configuration
    MAX_FILE_SIZE_MB = 10
    SUPPORTED_FORMATS = ["plain", "bdd", "both"]
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE = 60
    RATE_LIMIT_TOKENS_PER_MINUTE = 10000
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Environment Variables
    @staticmethod
    def get_api_key(provider: str = "openai") -> Optional[str]:
        """Get API key from environment variables."""
        env_vars = {
            "openai": "OPENAI_API_KEY",
            "google": "GOOGLE_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY"
        }
        return os.getenv(env_vars.get(provider.lower()))
    
    @staticmethod
    def validate_environment() -> Dict[str, Any]:
        """Validate production environment setup."""
        issues = []
        
        # Check for API key
        if not Config.get_api_key("openai"):
            issues.append("OPENAI_API_KEY environment variable not set")
        
        # Check Python version
        import sys
        if sys.version_info < (3, 8):
            issues.append(f"Python 3.8+ required, found {sys.version}")
        
        # Check available disk space
        import shutil
        free_space_gb = shutil.disk_usage(".").free / (1024**3)
        if free_space_gb < 1:
            issues.append(f"Low disk space: {free_space_gb:.1f}GB available")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "python_version": sys.version,
            "free_space_gb": round(free_space_gb, 1)
        }


class DevelopmentConfig(Config):
    """Development-specific configuration."""
    
    LOG_LEVEL = "DEBUG"
    MAX_RETRIES = 1
    DEFAULT_NUM_CASES = 3


class ProductionConfig(Config):
    """Production-specific configuration."""
    
    LOG_LEVEL = "WARNING"
    MAX_RETRIES = 5
    API_TIMEOUT = 60


# Configuration factory
def get_config(environment: str = None) -> Config:
    """Get configuration based on environment."""
    env = environment or os.getenv("ENVIRONMENT", "production").lower()
    
    if env == "development":
        return DevelopmentConfig()
    elif env == "production":
        return ProductionConfig()
    else:
        return Config()


if __name__ == "__main__":
    # Validate production environment
    config = get_config()
    validation = config.validate_environment()
    
    print("🔍 Environment Validation:")
    print(f"✅ Valid: {validation['valid']}")
    print(f"🐍 Python: {validation['python_version']}")
    print(f"💾 Free Space: {validation['free_space_gb']}GB")
    
    if validation['issues']:
        print("\n⚠️ Issues Found:")
        for issue in validation['issues']:
            print(f"  - {issue}")
    else:
        print("\n🎉 Environment ready for production!")
