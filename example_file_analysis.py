#!/usr/bin/env python3
"""
Example: Phoenix-SmartCaseAI with File Analysis

This script demonstrates how to use Phoenix-SmartCaseAI with additional file analysis
for enhanced test case generation.
"""

import os
import sys
from pathlib import Path

# Add package to path if running from source
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))

from SmartCaseAI import StoryBDDGenerator, __version__
from SmartCaseAI.file_analyzer import FileAnalyzer


def create_sample_files():
    """Create sample files for demonstration."""
    sample_dir = Path("sample_files")
    sample_dir.mkdir(exist_ok=True)
    
    # Create sample text file
    with open(sample_dir / "requirements.txt", "w") as f:
        f.write("""
User Authentication Requirements:
- Users must be able to login with email and password
- Password must be at least 8 characters
- Account lockout after 3 failed attempts
- Password reset via email
- Session timeout after 30 minutes of inactivity
        """)
    
    # Create sample JSON file
    with open(sample_dir / "api_spec.json", "w") as f:
        f.write("""
{
  "endpoints": {
    "login": {
      "method": "POST",
      "url": "/api/auth/login",
      "parameters": {
        "email": "string",
        "password": "string"
      },
      "responses": {
        "200": "Login successful",
        "401": "Invalid credentials",
        "429": "Too many attempts"
      }
    },
    "logout": {
      "method": "POST",
      "url": "/api/auth/logout",
      "responses": {
        "200": "Logout successful"
      }
    }
  }
}
        """)
    
    # Create sample CSV file
    with open(sample_dir / "test_data.csv", "w") as f:
        f.write("""
email,password,expected_result
user1@example.com,password123,success
user2@example.com,wrongpass,failure
admin@example.com,admin123,success
invalid-email,password123,failure
user3@example.com,short,failure
        """)
    
    print(f"✅ Created sample files in {sample_dir}")
    return sample_dir


def demonstrate_file_analysis():
    """Demonstrate file analysis capabilities."""
    print("🔍 File Analysis Demonstration")
    print("=" * 50)
    
    # Create sample files
    sample_dir = create_sample_files()
    
    # Initialize file analyzer
    analyzer = FileAnalyzer()
    
    # Analyze all files in the sample directory
    files_to_analyze = list(sample_dir.glob("*"))
    print(f"\n📁 Analyzing {len(files_to_analyze)} files...")
    
    results = analyzer.analyze_multiple_files(files_to_analyze)
    
    # Display results
    for result in results:
        print(f"\n📄 File: {Path(result.file_path).name}")
        print(f"   Type: {result.file_type}")
        print(f"   Content preview: {result.content[:100]}...")
        if result.metadata:
            print(f"   Metadata: {result.metadata}")
    
    # Generate combined analysis
    combined_analysis = analyzer.generate_combined_analysis(results)
    print(f"\n📋 Combined Analysis:")
    print(combined_analysis)
    
    return results


def demonstrate_enhanced_test_generation():
    """Demonstrate enhanced test case generation with file analysis."""
    print("\n🚀 Enhanced Test Case Generation")
    print("=" * 50)
    
    # User story
    user_story = """
    As a user, I want to be able to log into the system using my email and password
    so that I can access my personal dashboard and manage my account.
    """
    
    # Additional files for context
    sample_dir = Path("sample_files")
    additional_files = list(sample_dir.glob("*")) if sample_dir.exists() else []
    
    try:
        # Initialize generator
        generator = StoryBDDGenerator(llm_provider="openai")
        
        print(f"📖 User Story: {user_story.strip()}")
        print(f"📎 Additional Files: {len(additional_files)} files")
        
        # Generate test cases with file analysis
        print("\n🔧 Generating test cases with file analysis...")
        
        # Generate BDD scenarios
        bdd_cases = generator.generate_test_cases(
            user_story=user_story,
            output_format="bdd",
            num_cases=5,
            additional_files=additional_files
        )
        
        print(f"\n🥒 Generated {len(bdd_cases)} BDD scenarios:")
        for i, case in enumerate(bdd_cases, 1):
            print(f"\n{i}. {case.get('scenario', 'Untitled')}")
            print(f"   Feature: {case.get('feature', 'Not specified')}")
            print(f"   Given: {', '.join(case.get('given', []))}")
            print(f"   When: {', '.join(case.get('when', []))}")
            print(f"   Then: {', '.join(case.get('then', []))}")
        
        # Generate plain English test cases
        plain_cases = generator.generate_test_cases(
            user_story=user_story,
            output_format="plain",
            num_cases=3,
            additional_files=additional_files
        )
        
        print(f"\n📝 Generated {len(plain_cases)} plain English test cases:")
        for i, case in enumerate(plain_cases, 1):
            print(f"\n{i}. {case.get('title', 'Untitled')}")
            print(f"   Description: {case.get('description', 'No description')}")
            print(f"   Type: {case.get('type', 'Not specified')}")
            print(f"   Steps: {len(case.get('steps', []))} steps")
        
        # Export to markdown files
        print(f"\n💾 Exporting to markdown files...")
        file_paths = generator.export_to_markdown(
            user_story=user_story,
            output_dir="enhanced_test_output",
            filename_prefix="login_tests_with_files",
            num_cases=5,
            additional_files=additional_files
        )
        
        print(f"✅ Files exported:")
        print(f"   📄 Plain English: {file_paths['plain_english']}")
        print(f"   🥒 BDD: {file_paths['bdd']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if "API key" in str(e):
            print("💡 Make sure to set your OpenAI API key:")
            print("   export OPENAI_API_KEY='your-key-here'")


def demonstrate_cli_usage():
    """Demonstrate CLI usage with file analysis."""
    print("\n🖥️  CLI Usage Examples")
    print("=" * 50)
    
    print("""
Example CLI commands with file analysis:

1. Basic usage with individual files:
   phoenix-smartcase --story "As a user, I want to login..." \\
                     --files requirements.pdf ui_mockup.png api_spec.json

2. Using a directory of files:
   phoenix-smartcase --story "As a user, I want to login..." \\
                     --file-dir ./project_docs

3. Interactive mode with files:
   phoenix-smartcase --interactive \\
                     --files wireframe.png user_manual.pdf

4. Generate only BDD format with files:
   phoenix-smartcase --story "As a user, I want to login..." \\
                     --format bdd \\
                     --files test_data.csv

5. Custom output directory and prefix:
   phoenix-smartcase --story "As a user, I want to login..." \\
                     --output-dir ./my_tests \\
                     --prefix login_feature \\
                     --files requirements.pdf

Supported file types:
- Text: .txt, .md, .markdown
- Documents: .pdf, .docx, .doc
- Spreadsheets: .xlsx, .xls, .csv
- Data: .json, .xml
- Images: .png, .jpg, .jpeg, .gif, .bmp, .tiff
- Videos: .mp4, .avi, .mov, .wmv
    """)


def main():
    """Main demonstration function."""
    print(f"🚀 Phoenix-SmartCaseAI v{__version__} - File Analysis Demo")
    print("=" * 60)
    
    try:
        # Demonstrate file analysis
        demonstrate_file_analysis()
        
        # Demonstrate enhanced test generation
        demonstrate_enhanced_test_generation()
        
        # Show CLI usage examples
        demonstrate_cli_usage()
        
        print(f"\n🎉 Demonstration completed successfully!")
        print(f"📁 Check the 'enhanced_test_output/' directory for generated files.")
        print(f"📁 Check the 'sample_files/' directory for example files.")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
