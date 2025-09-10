#!/usr/bin/env python3
"""
Example usage of the enhanced StoryBDDGenerator with markdown export functionality.

This script demonstrates how to generate test cases and export them to separate
markdown files for plain English and BDD formats.
"""

import os
from SmartCaseAI.generator import StoryBDDGenerator

def main():
    """Main example showing how to use the markdown export functionality."""
    
    # Initialize the generator (requires OpenAI API key)
    try:
        gen = StoryBDDGenerator(llm_provider="openai")
        
        # Define your user story
        user_story = """
        As a user, I want to reset my password so that I can regain access 
        to my account if I forget my current password.
        """
        
        print("🔄 Generating test cases and exporting to markdown files...")
        
        # Generate and export to separate markdown files
        file_paths = gen.export_to_markdown(
            user_story=user_story.strip(),
            output_dir="generated_tests",        # Directory to save files
            filename_prefix="password_reset",    # Filename prefix
            num_cases=6                          # Limit number of test cases
        )
        
        print(f"✅ Plain English tests saved to: {file_paths['plain_english']}")
        print(f"✅ BDD tests saved to: {file_paths['bdd']}")
        
        # You can also generate individual formats if needed
        print("\n🔄 Generating individual format (BDD only)...")
        bdd_cases = gen.generate_test_cases(
            user_story=user_story.strip(),
            output_format="bdd",
            num_cases=3
        )
        print(f"Generated {len(bdd_cases)} BDD scenarios")
        
    except ValueError as e:
        if "API key required" in str(e):
            print("❌ Error: OpenAI API key is required.")
            print("Please set your API key using:")
            print("   Windows: $env:OPENAI_API_KEY='your-api-key-here'")
            print("   Linux/Mac: export OPENAI_API_KEY='your-api-key-here'")
        else:
            print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
