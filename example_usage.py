#!/usr/bin/env python3
"""
Production Example: Phoenix-SmartCaseAI Usage

This script demonstrates how to use Phoenix-SmartCaseAI in production environments.
"""

import os
import sys
from pathlib import Path

# Add package to path if running from source
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))

from SmartCaseAI import StoryBDDGenerator, __version__
from config import get_config


def main():
    """Main example function."""
    print(f"🚀 Phoenix-SmartCaseAI v{__version__}")
    print("=" * 50)
    
    # Load configuration
    config = get_config()
    
    # Validate environment
    validation = config.validate_environment()
    if not validation['valid']:
        print("❌ Environment validation failed:")
        for issue in validation['issues']:
            print(f"  - {issue}")
        return 1
    
    print("✅ Environment validated successfully")
    
    # Example user stories for different domains
    user_stories = {
        "e-commerce": """
        As an online customer, I want to add items to my shopping cart
        so that I can purchase multiple products in a single transaction.
        
        Acceptance Criteria:
        - Users can add products by clicking "Add to Cart" button
        - Cart icon shows the number of items
        - Users can view cart contents before checkout
        - Cart persists across browser sessions for logged-in users
        """,
        
        "banking": """
        As a bank customer, I want to transfer money between my accounts
        so that I can manage my finances efficiently.
        
        Acceptance Criteria:
        - Users can select source and destination accounts
        - Transfer amount must not exceed available balance
        - Users receive confirmation before executing transfer
        - Transaction history is updated immediately
        - Users receive email notification of successful transfer
        """,
        
        "healthcare": """
        As a patient, I want to book appointments online
        so that I can schedule my visits conveniently.
        
        Acceptance Criteria:
        - Patients can view available time slots
        - System prevents double-booking
        - Patients receive appointment confirmation
        - Patients can reschedule or cancel appointments
        - Doctor's schedule is updated in real-time
        """
    }
    
    try:
        # Initialize generator
        print("\n🔧 Initializing AI generator...")
        generator = StoryBDDGenerator(llm_provider="openai")
        print("✅ Generator ready")
        
        # Process each user story
        for domain, story in user_stories.items():
            print(f"\n🎯 Processing {domain.title()} Use Case")
            print("-" * 40)
            
            # Generate test cases
            output_dir = f"production_tests/{domain}"
            file_paths = generator.export_to_markdown(
                user_story=story,
                output_dir=output_dir,
                filename_prefix=f"{domain}_tests",
                num_cases=config.DEFAULT_NUM_CASES
            )
            
            print(f"📄 Plain English: {file_paths['plain_english']}")
            print(f"🥒 BDD: {file_paths['bdd']}")
        
        print(f"\n🎉 Successfully generated test cases for {len(user_stories)} domains!")
        print(f"📁 Check the 'production_tests/' directory for all generated files.")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if "API key" in str(e):
            print("💡 Make sure to set your OpenAI API key:")
            print("   export OPENAI_API_KEY='your-key-here'")
        return 1


def quick_test():
    """Quick functionality test."""
    print("🧪 Running quick functionality test...")
    
    try:
        from SmartCaseAI import StoryBDDGenerator
        
        # Simple test story
        test_story = "As a user, I want to login with username and password."
        
        generator = StoryBDDGenerator(llm_provider="openai")
        test_cases = generator.generate_test_cases(
            user_story=test_story,
            output_format="plain",
            num_cases=2
        )
        
        print(f"✅ Generated {len(test_cases)} test cases")
        print("🎉 Package is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    # Run quick test first
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        success = quick_test()
        sys.exit(0 if success else 1)
    
    # Run full example
    exit_code = main()
    sys.exit(exit_code)