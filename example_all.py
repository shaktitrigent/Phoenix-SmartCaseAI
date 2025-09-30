#!/usr/bin/env python3
"""
All Providers Payment Portal Test Generation

This script generates test cases for the Payment Portal user story using ALL available LLM providers
(OpenAI, Gemini, Claude) and combines their outputs for comprehensive test coverage.
All supporting files from input_files/ are automatically included for enhanced context.
"""

import os
from SmartCaseAI.generator import StoryBDDGenerator

# Payment Portal User Story
PAYMENT_PORTAL_STORY = """As a customer of an e-commerce platform,
I want to securely process my payment through a comprehensive payment portal,
So that I can complete my purchase quickly and safely with multiple payment options."""

def check_api_keys():
    """Check which API keys are configured."""
    providers = {
        "OpenAI": os.getenv("OPENAI_API_KEY"),
        "Google": os.getenv("GOOGLE_API_KEY"), 
        "Claude": os.getenv("ANTHROPIC_API_KEY")
    }
    
    available = []
    missing = []
    
    for provider, key in providers.items():
        if key:
            # Basic format validation
            if provider == "OpenAI" and key.startswith("sk-"):
                available.append(provider)
            elif provider == "Google" and len(key) > 20:
                available.append(provider) 
            elif provider == "Claude" and key.startswith("sk-ant-"):
                available.append(provider)
            else:
                missing.append(f"{provider} (invalid format)")
        else:
            missing.append(provider)
    
    print(f"[STATUS] Available providers: {', '.join(available) if available else 'None'}")
    if missing:
        print(f"[WARNING] Missing/Invalid providers: {', '.join(missing)}")
    
    return len(available) > 0, available

def generate_multi_provider_tests():
    """Generate Payment Portal test cases using all available providers."""
    print("\nPayment Portal Test Generation - All Providers")
    print("=" * 60)
    
    has_providers, available_providers = check_api_keys()
    if not has_providers:
        print("[ERROR] No valid API keys configured")
        print("\nPlease configure at least one API key:")
        print("  OPENAI_API_KEY=sk-...")
        print("  GOOGLE_API_KEY=...")
        print("  ANTHROPIC_API_KEY=sk-ant-...")
        return
    
    try:
        # Initialize multi-provider generator
        generator = StoryBDDGenerator(llm_provider="all")
        print(f"[OK] Multi-provider generator initialized")
        print(f"[INFO] Using providers: {', '.join(available_providers)}")
        
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
                print(f"  - {file_name} [IMAGE - will be routed to best provider for analysis]")
            else:
                print(f"  - {file_name} [{file_ext[1:].upper()}]")
        
        # Generate test cases with explicit additional files
        print("\nGenerating comprehensive test cases...")
        print("Using Payment Portal user story + all supporting files")
        print("Combining outputs from all available LLM providers...")
        
        # Export both formats to organized directory
        file_paths = generator.export_to_markdown(
            user_story=PAYMENT_PORTAL_STORY,
            output_dir="examples/payment_portal/all_providers",
            filename_prefix="payment_portal_combined",
            num_cases=15,  # More cases since we're combining multiple providers
            additional_files=additional_files
        )
        
        print(f"\n[SUCCESS] Multi-provider test cases generated:")
        print(f"  Plain English: {file_paths['plain_english']}")
        print(f"  BDD Format: {file_paths['bdd']}")
        
        # Also generate individual formats for detailed analysis
        plain_cases = generator.generate_test_cases(
            PAYMENT_PORTAL_STORY,
            output_format="plain",
            num_cases=10,
            additional_files=additional_files
        )
        
        bdd_cases = generator.generate_test_cases(
            PAYMENT_PORTAL_STORY,
            output_format="bdd", 
            num_cases=10,
            additional_files=additional_files
        )
        
        print(f"\n[SUMMARY] Multi-Provider Results:")
        print(f"  Generated {len(plain_cases)} plain English test cases")
        print(f"  Generated {len(bdd_cases)} BDD scenarios")
        print(f"  Combined insights from: {', '.join(available_providers)}")
        print(f"  Supporting files used: {len(additional_files)} files from input_files/")
        
        # Show diversity of test cases
        print(f"\nSample Combined Test Cases:")
        for i, case in enumerate(plain_cases[:5], 1):
            provider = case.get('provider', 'Multi-Provider')
            print(f"  {i}. {case.get('title', 'N/A')} [{provider}]")
        
        print(f"\nSample Combined BDD Scenarios:")
        for i, scenario in enumerate(bdd_cases[:5], 1):
            provider = scenario.get('provider', 'Multi-Provider')
            print(f"  {i}. {scenario.get('scenario', 'N/A')} [{provider}]")
        
        print(f"\nMulti-Provider Benefits Demonstrated:")
        print(f"  - Comprehensive coverage from multiple AI perspectives")
        print(f"  - Diverse testing approaches and methodologies")
        print(f"  - Enhanced edge case detection")
        print(f"  - Combined expertise in security, usability, and compliance")
        print(f"  - More robust test scenario generation")
            
    except Exception as e:
        print(f"[ERROR] Multi-provider test generation failed: {e}")
        if "API key" in str(e):
            print("Please verify your API keys and account status")
        elif "rate limit" in str(e).lower():
            print("Rate limit reached on one or more providers. Please wait and try again")
        else:
            print("Check your internet connection and API statuses")

def generate_comparison_report():
    """Generate a comparison report of the different providers."""
    print(f"\n{'='*60}")
    print("PROVIDER COMPARISON GUIDE")
    print("=" * 60)
    
    print("\nRun individual provider examples to compare:")
    print("  python example_openai.py  # GPT models - great for detailed instructions")
    print("  python example_gemini.py  # Google AI - excellent edge case detection") 
    print("  python example_claude.py  # Anthropic - thorough compliance coverage")
    print("  python example_all.py     # Combined - comprehensive test suite")
    
    print(f"\nCompare outputs in examples/payment_portal/:")
    print("  openai/          - OpenAI-generated tests")
    print("  gemini/          - Gemini-generated tests")
    print("  claude/          - Claude-generated tests") 
    print("  all_providers/   - Combined multi-provider tests")
    
    print(f"\nEvaluation Criteria:")
    print("  - Test case coverage and completeness")
    print("  - Edge case identification")
    print("  - Security scenario depth")
    print("  - Regulatory compliance considerations")
    print("  - User experience focus")
    print("  - Technical accuracy")

def main():
    print("Phoenix-SmartCaseAI: Payment Portal Testing")
    print("Provider: ALL Available LLM Providers")
    print("=" * 50)
    
    # Create output directory
    os.makedirs("examples/payment_portal/all_providers", exist_ok=True)
    
    # Generate tests using all providers
    generate_multi_provider_tests()
    
    # Show comparison guide
    generate_comparison_report()
    
    print(f"\n{'='*50}")
    print("Multi-Provider Payment Portal Test Generation Complete")
    print("=" * 50)

if __name__ == "__main__":
    main()
