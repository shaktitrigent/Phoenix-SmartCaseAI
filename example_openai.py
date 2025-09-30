#!/usr/bin/env python3
"""
OpenAI Payment Portal Test Generation

This script generates test cases for the Payment Portal user story using OpenAI GPT models.
All supporting files from input_files/ are automatically included for enhanced context.
"""

import os
from SmartCaseAI.generator import StoryBDDGenerator

# Payment Portal User Story
PAYMENT_PORTAL_STORY = """As a customer of an e-commerce platform,
I want to securely process my payment through a comprehensive payment portal,
So that I can complete my purchase quickly and safely with multiple payment options."""

def check_openai_api():
    """Check if OpenAI API key is configured."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[ERROR] OpenAI API key not configured")
        print("Please set OPENAI_API_KEY environment variable")
        print("Get your key from: https://platform.openai.com/api-keys")
        return False
    
    if not api_key.startswith("sk-"):
        print("[ERROR] Invalid OpenAI API key format")
        print("OpenAI API keys should start with 'sk-'")
        return False
    
    print("[OK] OpenAI API key configured")
    return True

def generate_openai_tests():
    """Generate Payment Portal test cases using OpenAI."""
    print("\nPayment Portal Test Generation - OpenAI Provider")
    print("=" * 60)
    
    if not check_openai_api():
        return
    
    try:
        # Initialize OpenAI generator
        generator = StoryBDDGenerator(llm_provider="openai")
        print("[OK] OpenAI generator initialized")
        
        # Discover additional files from input_files/
        from pathlib import Path
        input_files_dir = Path("input_files")
        additional_files = []
        
        if input_files_dir.exists():
            supported_extensions = {'.txt', '.md', '.json', '.csv', '.xml', '.pdf', '.docx', '.png', '.jpg', '.jpeg', '.webp'}
            for file_path in input_files_dir.iterdir():
                if (file_path.is_file() and 
                    file_path.suffix.lower() in supported_extensions and
                    file_path.name.lower() != 'readme.md'):
                    additional_files.append(str(file_path))
        
        print(f"\nDiscovered {len(additional_files)} supporting files:")
        for file in sorted(additional_files):
            file_name = Path(file).name
            file_ext = Path(file).suffix.lower()
            if file_ext in {'.png', '.jpg', '.jpeg', '.webp'}:
                print(f"  - {file_name} [IMAGE - will be analyzed for UI insights]")
            else:
                print(f"  - {file_name} [{file_ext[1:].upper()}]")
        
        # Generate test cases with explicit additional files
        print("\nGenerating comprehensive test cases...")
        print("Using Payment Portal user story + all supporting files")
        
        # Export both formats to organized directory
        file_paths = generator.export_to_markdown(
            user_story=PAYMENT_PORTAL_STORY,
            output_dir="examples/payment_portal/openai",
            filename_prefix="payment_portal_openai",
            num_cases=10,
            additional_files=additional_files
        )
        
        print(f"\n[SUCCESS] OpenAI test cases generated:")
        print(f"  Plain English: {file_paths['plain_english']}")
        print(f"  BDD Format: {file_paths['bdd']}")
        
        # Also generate individual formats for comparison
        plain_cases = generator.generate_test_cases(
            PAYMENT_PORTAL_STORY,
            output_format="plain",
            num_cases=5,
            additional_files=additional_files
        )
        
        bdd_cases = generator.generate_test_cases(
            PAYMENT_PORTAL_STORY,
            output_format="bdd", 
            num_cases=5,
            additional_files=additional_files
        )
        
        print(f"\n[SUMMARY] OpenAI Results:")
        print(f"  Generated {len(plain_cases)} plain English test cases")
        print(f"  Generated {len(bdd_cases)} BDD scenarios")
        print(f"  Supporting files used: {len(additional_files)} files from input_files/")
        
        print(f"\nSample Test Case Titles (OpenAI):")
        for i, case in enumerate(plain_cases[:3], 1):
            print(f"  {i}. {case.get('title', 'N/A')}")
        
        print(f"\nSample BDD Scenarios (OpenAI):")
        for i, scenario in enumerate(bdd_cases[:3], 1):
            print(f"  {i}. {scenario.get('scenario', 'N/A')}")
            
    except Exception as e:
        print(f"[ERROR] OpenAI test generation failed: {e}")
        if "API key" in str(e):
            print("Please verify your OpenAI API key and account status")
        elif "rate limit" in str(e).lower():
            print("Rate limit reached. Please wait and try again")
        else:
            print("Check your internet connection and try again")

def main():
    print("Phoenix-SmartCaseAI: Payment Portal Testing")
    print("Provider: OpenAI GPT Models")
    print("=" * 50)
    
    # Create output directory
    os.makedirs("examples/payment_portal/openai", exist_ok=True)
    
    # Generate tests
    generate_openai_tests()
    
    print(f"\n{'='*50}")
    print("OpenAI Payment Portal Test Generation Complete")
    print("=" * 50)
    print("Compare with other providers:")
    print("  python example_gemini.py")
    print("  python example_claude.py")
    print("  python example_all.py")

if __name__ == "__main__":
    main()