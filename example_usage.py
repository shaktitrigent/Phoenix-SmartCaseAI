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

        "Allow volunteers to update their hours in the portal" :


        """ Description

We are enhancing the Volunteer Portal so that, when the Allow Volunteer Hour Edits configuration is enabled, volunteers can correct their sign-out time if it was logged by the system via auto sign-out.

Currently, auto sign-outs may record inflated hours if a volunteer forgets to sign out. This leads to inaccurate reporting and requires staff intervention. By allowing volunteers to edit just their sign-out time (not the sign-in time or other details) on auto sign-out entries, we empower them to quickly correct mistakes, reduce coordinator workload, and improve accuracy while maintaining auditability and control.

Acceptance Criteria
Eligibility Rules:

Edit option is only available if:

The district/building has Allow Volunteer Hour Edits enabled.

The hours entry was created via auto sign-out.

The hours entry was previously updated by them and they need to make a change. (this is updating self entered hours for the hours they edited)

UI – Volunteer Portal:

On the volunteer’s My Hours History screen, under Details for a specific day, End Date/Time should be editable if the eligibility rules are met.  

Only the sign-out time can be changed.

image-20250910-170829.png
 

Validation:

New sign-out time must be after the sign-in time.

New sign-out time must be the same date.

The Sign Out Event Method changes  from Auto to Proxy

Once the update it done, Raptor Web should reflect the new time in Sign In/Out history and use the method Proxy

Security:

Volunteers cannot edit entries that were signed out via VisitorSafe.


Description

We are enhancing the Volunteer Portal so that, when the Allow Volunteer Hour Edits configuration is enabled, volunteers can correct their sign-out time if it was logged by the system via auto sign-out.

Currently, auto sign-outs may record inflated hours if a volunteer forgets to sign out. This leads to inaccurate reporting and requires staff intervention. By allowing volunteers to edit just their sign-out time (not the sign-in time or other details) on auto sign-out entries, we empower them to quickly correct mistakes, reduce coordinator workload, and improve accuracy while maintaining auditability and control.

Acceptance Criteria
Eligibility Rules:

Edit option is only available if:

The district/building has Allow Volunteer Hour Edits enabled.

The hours entry was created via auto sign-out.

The hours entry was previously updated by them and they need to make a change. (this is updating self entered hours for the hours they edited)

UI – Volunteer Portal:

On the volunteer’s My Hours History screen, under Details for a specific day, End Date/Time should be editable if the eligibility rules are met.  

Only the sign-out time can be changed.



Validation:

New sign-out time must be after the sign-in time.

New sign-out time must be the same date.

The Sign Out Event Method changes  from Auto to Proxy

Once the update it done, Raptor Web should reflect the new time in Sign In/Out history and use the method Proxy

Security:

Volunteers cannot edit entries that were signed out via VisitorSafe.
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
            
            # Example: Simulate having additional files for analysis
            # In a real scenario, these would be actual files provided by the user
            additional_files = []
            
            # Check if there are any example files in the project
            example_files_dir = Path("example_files")
            if example_files_dir.exists():
                additional_files = list(example_files_dir.glob("*"))
                print(f"📎 Found {len(additional_files)} example files for analysis")
            
            # Generate test cases with file analysis
            output_dir = f"production_tests/{domain}"
            file_paths = generator.export_to_markdown(
                user_story=story,
                output_dir=output_dir,
                filename_prefix=f"{domain}_tests",
                num_cases=config.DEFAULT_NUM_CASES,
                additional_files=additional_files if additional_files else None
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