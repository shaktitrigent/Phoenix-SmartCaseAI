#!/usr/bin/env python3
"""
Command Line Interface for Phoenix-SmartCaseAI

This module provides a CLI for generating test cases from user stories.
"""

import argparse
import sys
import os
from typing import Optional, List
from ._version import __version__
from .generator import StoryBDDGenerator


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Phoenix-SmartCaseAI: Generate test cases from user stories using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  phoenix-smartcase --story "As a user, I want to login..." --output-dir ./tests
  
  # With additional files for context
  phoenix-smartcase --story "As a user, I want to login..." \\
                    --files requirements.pdf ui_mockup.png api_spec.json
  
  # Using a directory of files
  phoenix-smartcase --story "As a user, I want to login..." \\
                    --file-dir ./project_docs
  
  # Interactive mode with files
  phoenix-smartcase --interactive --files wireframe.png user_manual.pdf
  
  # Generate only BDD format with files
  phoenix-smartcase --story "As a user, I want to login..." \\
                    --format bdd --files test_data.csv

Supported file types: txt, md, pdf, docx, xlsx, csv, json, xml, png, jpg, mp4, etc.

For more information, visit: https://github.com/yourusername/Phoenix-SmartCaseAI
        """
    )
    
    # Story input options
    story_group = parser.add_mutually_exclusive_group(required=True)
    story_group.add_argument(
        "--story", "-s",
        type=str,
        help="User story text directly as argument"
    )
    story_group.add_argument(
        "--story-file", "-f",
        type=str,
        help="Path to file containing user story"
    )
    story_group.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Interactive mode - enter story via prompt"
    )
    
    # Generation options
    parser.add_argument(
        "--format",
        choices=["plain", "bdd", "both"],
        default="both",
        help="Output format for test cases (default: both)"
    )
    parser.add_argument(
        "--num-cases", "-n",
        type=int,
        default=5,
        help="Number of test cases to generate (default: 5)"
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="./test_cases",
        help="Directory to save generated files (default: ./test_cases)"
    )
    parser.add_argument(
        "--prefix", "-p",
        type=str,
        default="generated_tests",
        help="Filename prefix for generated files (default: generated_tests)"
    )
    
    # File analysis options
    parser.add_argument(
        "--files", "-F",
        nargs="*",
        help="Additional files to analyze for context (supports: txt, md, pdf, docx, xlsx, csv, json, xml, png, jpg, mp4, etc.)"
    )
    parser.add_argument(
        "--file-dir",
        type=str,
        help="Directory containing files to analyze (all supported files in directory will be analyzed)"
    )
    
    # LLM options
    parser.add_argument(
        "--api-key",
        type=str,
        help="OpenAI API key (or set OPENAI_API_KEY env var)"
    )
    
    # Output options
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress output except errors"
    )
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"Phoenix-SmartCaseAI {__version__}"
    )
    
    args = parser.parse_args()
    
    try:
        # Get user story
        user_story = get_user_story(args)
        
        # Collect additional files
        additional_files = get_additional_files(args)
        
        if not args.quiet:
            print("🚀 Phoenix-SmartCaseAI: AI-Powered Test Case Generation")
            print("=" * 60)
            print(f"📖 User Story Preview:")
            print(f"   {user_story[:100]}{'...' if len(user_story) > 100 else ''}")
            print(f"📁 Output Directory: {args.output_dir}")
            print(f"🎯 Format: {args.format}")
            print(f"🔢 Number of Cases: {args.num_cases}")
            if additional_files:
                print(f"📎 Additional Files: {len(additional_files)} files")
                for file_path in additional_files[:3]:  # Show first 3 files
                    print(f"   - {os.path.basename(file_path)}")
                if len(additional_files) > 3:
                    print(f"   ... and {len(additional_files) - 3} more")
        
        # Initialize generator
        generator = StoryBDDGenerator(
            llm_provider="openai",
            api_key=args.api_key
        )
        
        if not args.quiet:
            print(f"\n✅ Generator initialized with OpenAI")
            if additional_files:
                print(f"🔍 Analyzing {len(additional_files)} additional files for context...")
        
        # Generate based on format
        if args.format == "both":
            # Generate and export both formats
            file_paths = generator.export_to_markdown(
                user_story=user_story,
                output_dir=args.output_dir,
                filename_prefix=args.prefix,
                num_cases=args.num_cases,
                additional_files=additional_files
            )
            
            if not args.quiet:
                print(f"\n🎉 Generated both formats:")
                print(f"📄 Plain English: {file_paths['plain_english']}")
                print(f"🥒 BDD: {file_paths['bdd']}")
            else:
                print(f"{file_paths['plain_english']}")
                print(f"{file_paths['bdd']}")
                
        else:
            # Generate single format
            test_cases = generator.generate_test_cases(
                user_story=user_story,
                output_format=args.format,
                num_cases=args.num_cases,
                additional_files=additional_files
            )
            
            if not args.quiet:
                print(f"\n🎉 Generated {len(test_cases)} {args.format} test cases")
                print("📋 Test cases generated in memory (use --format both for file export)")
            else:
                for i, case in enumerate(test_cases, 1):
                    if args.format == "plain":
                        print(f"{i}. {case.get('title', 'Test Case')}")
                    else:
                        print(f"{i}. {case.get('scenario', 'Scenario')}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        if "API key" in str(e):
            print("💡 Tip: Set your API key with --api-key or environment variable")
            print(f"   export OPENAI_API_KEY='your-key-here'")
        return 1


def get_user_story(args) -> str:
    """Get user story from various input sources."""
    
    if args.story:
        return args.story.strip()
    
    elif args.story_file:
        if not os.path.exists(args.story_file):
            raise FileNotFoundError(f"Story file not found: {args.story_file}")
        
        with open(args.story_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        if not content:
            raise ValueError(f"Story file is empty: {args.story_file}")
        
        return content
    
    elif args.interactive:
        print("📝 Interactive Mode: Enter your user story")
        print("   (Press Ctrl+D when finished, or Ctrl+C to cancel)")
        print("-" * 50)
        
        try:
            lines = []
            while True:
                try:
                    line = input()
                    lines.append(line)
                except EOFError:
                    break
            
            story = '\n'.join(lines).strip()
            if not story:
                raise ValueError("No user story provided")
            
            return story
            
        except KeyboardInterrupt:
            raise KeyboardInterrupt("Interactive input cancelled")
    
    else:
        raise ValueError("No user story source provided")


def get_additional_files(args) -> List[str]:
    """Get additional files for analysis from various sources."""
    files = []
    
    # Add individual files
    if args.files:
        for file_path in args.files:
            if os.path.exists(file_path):
                files.append(file_path)
            else:
                print(f"⚠️  Warning: File not found: {file_path}")
    
    # Add files from directory
    if args.file_dir:
        if not os.path.exists(args.file_dir):
            print(f"⚠️  Warning: Directory not found: {args.file_dir}")
        else:
            # Supported file extensions
            supported_extensions = {
                '.txt', '.md', '.markdown',  # Text files
                '.pdf',  # PDF files
                '.docx', '.doc',  # Word documents
                '.xlsx', '.xls', '.csv',  # Spreadsheets
                '.json',  # JSON files
                '.xml',  # XML files
                '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff',  # Images
                '.mp4', '.avi', '.mov', '.wmv'  # Videos
            }
            
            for root, dirs, filenames in os.walk(args.file_dir):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    file_ext = os.path.splitext(filename)[1].lower()
                    if file_ext in supported_extensions:
                        files.append(file_path)
    
    return files


if __name__ == "__main__":
    sys.exit(main())