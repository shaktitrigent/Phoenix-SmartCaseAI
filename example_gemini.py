#!/usr/bin/env python3
"""
Gemini Payment Portal Test Generation

This script generates test cases for the Payment Portal user story using Google Gemini models.
All supporting files from input_files/ are automatically included for enhanced context.
"""

import os
from SmartCaseAI.generator import StoryBDDGenerator

# Payment Portal User Story
PAYMENT_PORTAL_STORY = """As a customer of an e-commerce platform,
I want to securely process my payment through a comprehensive payment portal,
So that I can complete my purchase quickly and safely with multiple payment options."""

def check_gemini_api():
    """Check if Google API key is configured."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("[ERROR] Google API key not configured")
        print("Please set GOOGLE_API_KEY environment variable")
        print("Get your key from: https://aistudio.google.com/app/apikey")
        return False
    
    if len(api_key) < 20:
        print("[ERROR] Invalid Google API key format")
        print("Google API keys should be longer than 20 characters")
        return False
    
    print("[OK] Google API key configured")
    return True

def generate_gemini_tests():
    """Generate Payment Portal test cases using Gemini."""
    print("\nPayment Portal Test Generation - Gemini Provider")
    print("=" * 60)
    
    if not check_gemini_api():
        return
    
    try:
        # Initialize Gemini generator
        generator = StoryBDDGenerator(llm_provider="gemini")
        print("[OK] Gemini generator initialized")
        
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
                print(f"  - {file_name} [IMAGE - will be analyzed by Gemini for UI insights]")
            else:
                print(f"  - {file_name} [{file_ext[1:].upper()}]")
        
        # Generate test cases with explicit additional files
        print("\nGenerating comprehensive test cases...")
        print("Using Payment Portal user story + all supporting files")
        
        # Export to .feature and .json formats
        file_paths = generator.export_to_feature_and_json(
            user_story=PAYMENT_PORTAL_STORY,
            output_dir="examples/payment_portal/gemini",
            filename_prefix="payment_portal_gemini",
            num_cases=10,
            additional_files=additional_files
        )
        
        print(f"\n[SUCCESS] Gemini test cases generated:")
        print(f"  Feature File (.feature): {file_paths['feature']}")
        print(f"  JSON File (.json): {file_paths['json']}")
        
        # Also export markdown for comparison
        md_paths = generator.export_to_markdown(
            user_story=PAYMENT_PORTAL_STORY,
            output_dir="examples/payment_portal/gemini",
            filename_prefix="payment_portal_gemini",
            num_cases=10,
            additional_files=additional_files
        )
        
        print(f"  Plain English (Markdown): {md_paths['plain_english']}")
        print(f"  BDD Format (Markdown): {md_paths['bdd']}")
        
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
        
        print(f"\n[SUMMARY] Gemini Results:")
        print(f"  Generated {len(plain_cases)} plain English test cases")
        print(f"  Generated {len(bdd_cases)} BDD scenarios")
        print(f"  Supporting files used: {len(additional_files)} files from input_files/")
        
        print(f"\nSample Test Case Titles (Gemini):")
        for i, case in enumerate(plain_cases[:3], 1):
            print(f"  {i}. {case.get('title', 'N/A')}")
        
        print(f"\nSample BDD Scenarios (Gemini):")
        for i, scenario in enumerate(bdd_cases[:3], 1):
            print(f"  {i}. {scenario.get('scenario', 'N/A')}")
        
        print(f"\nGemini Strengths Demonstrated:")
        print(f"  - Excellent edge case detection")
        print(f"  - Strong security scenario coverage")
        print(f"  - Comprehensive boundary testing")
            
    except Exception as e:
        print(f"[ERROR] Gemini test generation failed: {e}")
        if "API key" in str(e) or "authentication" in str(e).lower():
            print("Please verify your Google API key and enable Gemini API")
        elif "model" in str(e).lower() and "not found" in str(e).lower():
            print("Gemini model may be unavailable. Check API quotas and regions")
        elif "rate limit" in str(e).lower():
            print("Rate limit reached. Please wait and try again")
        else:
            print("Check your internet connection and API status")

def main():
    print("Phoenix-SmartCaseAI: Payment Portal Testing")
    print("Provider: Google Gemini Models")
    print("=" * 50)
    
    # Create output directory
    os.makedirs("examples/payment_portal/gemini", exist_ok=True)
    
    # Generate tests
    generate_gemini_tests()
    
    print(f"\n{'='*50}")
    print("Gemini Payment Portal Test Generation Complete")
    print("=" * 50)
    print("Compare with other providers:")
    print("  python example_openai.py")
    print("  python example_claude.py")
    print("  python example_all.py")

if __name__ == "__main__":
    main()