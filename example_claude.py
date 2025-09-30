#!/usr/bin/env python3
"""
Claude Payment Portal Test Generation

This script generates test cases for the Payment Portal user story using Anthropic Claude models.
All supporting files from input_files/ are automatically included for enhanced context.
"""

import os
from SmartCaseAI.generator import StoryBDDGenerator

# Payment Portal User Story
PAYMENT_PORTAL_STORY = """As a customer of an e-commerce platform,
I want to securely process my payment through a comprehensive payment portal,
So that I can complete my purchase quickly and safely with multiple payment options."""

def check_claude_api():
    """Check if Claude API key is configured."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("[ERROR] Claude API key not configured")
        print("Please set ANTHROPIC_API_KEY environment variable")
        print("Get your key from: https://console.anthropic.com/")
        return False
    
    if not api_key.startswith("sk-ant-"):
        print("[ERROR] Invalid Claude API key format")
        print("Claude API keys should start with 'sk-ant-'")
        return False
    
    print("[OK] Claude API key configured")
    return True

def generate_claude_tests():
    """Generate Payment Portal test cases using Claude."""
    print("\nPayment Portal Test Generation - Claude Provider")
    print("=" * 60)
    
    if not check_claude_api():
        return
    
    try:
        # Initialize Claude generator
        generator = StoryBDDGenerator(llm_provider="claude")
        print("[OK] Claude generator initialized")
        
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
                print(f"  - {file_name} [IMAGE - will be routed to Gemini for analysis]")
            else:
                print(f"  - {file_name} [{file_ext[1:].upper()}]")
        
        # Generate test cases with explicit additional files
        print("\nGenerating comprehensive test cases...")
        print("Using Payment Portal user story + all supporting files")
        
        # Export both formats to organized directory
        file_paths = generator.export_to_markdown(
            user_story=PAYMENT_PORTAL_STORY,
            output_dir="examples/payment_portal/claude",
            filename_prefix="payment_portal_claude",
            num_cases=10,
            additional_files=additional_files
        )
        
        print(f"\n[SUCCESS] Claude test cases generated:")
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
        
        print(f"\n[SUMMARY] Claude Results:")
        print(f"  Generated {len(plain_cases)} plain English test cases")
        print(f"  Generated {len(bdd_cases)} BDD scenarios")
        print(f"  Supporting files used: {len(additional_files)} files from input_files/")
        
        print(f"\nSample Test Case Titles (Claude):")
        for i, case in enumerate(plain_cases[:3], 1):
            print(f"  {i}. {case.get('title', 'N/A')}")
        
        print(f"\nSample BDD Scenarios (Claude):")
        for i, scenario in enumerate(bdd_cases[:3], 1):
            print(f"  {i}. {scenario.get('scenario', 'N/A')}")
        
        print(f"\nClaude Strengths Demonstrated:")
        print(f"  - Detailed step-by-step test instructions")
        print(f"  - Excellent context understanding")
        print(f"  - Thorough error handling scenarios")
        print(f"  - Strong regulatory compliance coverage")
            
    except Exception as e:
        print(f"[ERROR] Claude test generation failed: {e}")
        if "API key" in str(e) or "authentication" in str(e).lower():
            print("Please verify your Anthropic API key and account access")
        elif "rate limit" in str(e).lower():
            print("Rate limit reached. Please wait and try again")
        elif "quota" in str(e).lower():
            print("API quota exceeded. Check your Anthropic account limits")
        else:
            print("Check your internet connection and Claude API status")

def main():
    print("Phoenix-SmartCaseAI: Payment Portal Testing")
    print("Provider: Anthropic Claude Models")
    print("=" * 50)
    
    # Create output directory
    os.makedirs("examples/payment_portal/claude", exist_ok=True)
    
    # Generate tests
    generate_claude_tests()
    
    print(f"\n{'='*50}")
    print("Claude Payment Portal Test Generation Complete")
    print("=" * 50)
    print("Compare with other providers:")
    print("  python example_openai.py")
    print("  python example_gemini.py")
    print("  python example_all.py")

if __name__ == "__main__":
    main()