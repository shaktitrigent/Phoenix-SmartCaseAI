import os
from datetime import datetime
from typing import List, Dict, Optional, Union
from pathlib import Path
import json
import asyncio

from pydantic import BaseModel, Field, RootModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic

from .unified_file_analyzer import UnifiedFileAnalyzer


class TestCase(BaseModel):
    """Structured test case model."""
    id: int = Field(description="Unique test case ID")
    title: str = Field(description="Test case title")
    description: str = Field(description="Detailed description")
    preconditions: Optional[str] = Field(default=None, description="Prerequisites or setup")
    steps: List[str] = Field(description="Step-by-step instructions")
    expected: str = Field(description="Expected outcome")
    type: str = Field(description="Type: positive, negative, edge, etc.")
    provider: Optional[str] = Field(default=None, description="LLM provider that generated this test case")
    
    @classmethod
    def model_json_schema(cls, by_alias=True, ref_template='#/$defs/{model}'):
        """Override to match exact required format."""
        schema = super().model_json_schema(by_alias=by_alias, ref_template=ref_template)
        # Fix preconditions field to match required format
        if 'properties' in schema and 'preconditions' in schema['properties']:
            schema['properties']['preconditions'] = {
                "title": "Preconditions",
                "description": "Prerequisites or setup",
                "default": None,
                "type": "string"
            }
        return schema


class BDDScenario(BaseModel):
    """BDD/Gherkin-style scenario model."""
    feature: str = Field(description="Feature name")
    scenario: str = Field(description="Scenario title")
    given: List[str] = Field(description="Given steps (preconditions)")
    when: List[str] = Field(description="When steps (actions)")
    then: List[str] = Field(description="Then steps (expectations)")
    provider: Optional[str] = Field(default=None, description="LLM provider that generated this scenario")


class TestCaseList(RootModel[List[TestCase]]):
    """Root model for List[TestCase] to work with PydanticOutputParser."""
    
    @classmethod
    def model_json_schema(cls, by_alias=True, ref_template='#/$defs/{model}'):
        """Generate schema matching the exact required format."""
        testcase_schema = TestCase.model_json_schema(by_alias=by_alias, ref_template=ref_template)
        return {
            "title": "List[TestCase]",
            "description": "A list of TestCase objects.",
            "type": "array",
            "items": testcase_schema
        }


class BDDScenarioList(RootModel[List[BDDScenario]]):
    """Root model for List[BDDScenario] to work with PydanticOutputParser."""
    
    @classmethod
    def model_json_schema(cls, by_alias=True, ref_template='#/$defs/{model}'):
        """Generate schema matching the exact required format."""
        bdd_schema = BDDScenario.model_json_schema(by_alias=by_alias, ref_template=ref_template)
        return {
            "title": "List[BDDScenario]",
            "description": "A list of BDDScenario objects.",
            "type": "array",
            "items": bdd_schema
        }


class StoryBDDGenerator:
    def __init__(
        self,
        llm_provider: str = "openai",
        api_keys: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize the generator with chosen LLM provider(s).
        
        Args:
            llm_provider: LLM provider to use ("openai", "gemini", "claude", or "all")
            api_keys: Dictionary of API keys for different providers (optional, uses env vars if not provided)
        """
        self.llm_provider = llm_provider
        self.llms = {}
        self.file_analyzer = None
        
        # Initialize API keys
        if api_keys is None:
            api_keys = {}
        
        # Setup providers based on selection
        if llm_provider in ["openai", "all"]:
            openai_key = api_keys.get("openai") or os.getenv("OPENAI_API_KEY")
            if not openai_key:
                raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable or pass in api_keys parameter.")
            self.llms["openai"] = ChatOpenAI(model="gpt-4o-mini", api_key=openai_key)
        
        if llm_provider in ["gemini", "all"]:
            gemini_key = api_keys.get("gemini") or os.getenv("GOOGLE_API_KEY")
            if not gemini_key:
                raise ValueError("Google API key required for Gemini. Set GOOGLE_API_KEY environment variable or pass in api_keys parameter.")
            try:
                self.llms["gemini"] = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash",
                    google_api_key=gemini_key,
                    temperature=0.3
                )
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini model: {e}")
                # Don't add gemini to available LLMs if it fails to initialize
            # File analysis will be handled by SmartFileAnalyzer after LLM setup
        
        if llm_provider in ["claude", "all"]:
            claude_key = api_keys.get("claude") or os.getenv("ANTHROPIC_API_KEY")
            if not claude_key:
                raise ValueError("Anthropic API key required for Claude. Set ANTHROPIC_API_KEY environment variable or pass in api_keys parameter.")
            self.llms["claude"] = ChatAnthropic(
                model="claude-3-5-haiku-20241022",
                api_key=claude_key,
                temperature=0.3
            )
            # File analysis will be handled by SmartFileAnalyzer after LLM setup
        
        if not self.llms:
            raise ValueError(f"Unsupported LLM provider: {llm_provider}. Supported providers: openai, gemini, claude, all")
        
        # Initialize UnifiedFileAnalyzer with all available API keys for intelligent routing
        self.file_analyzer = UnifiedFileAnalyzer(
            openai_api_key=api_keys.get("openai") or os.getenv("OPENAI_API_KEY"),
            google_api_key=api_keys.get("gemini") or os.getenv("GOOGLE_API_KEY"),
            anthropic_api_key=api_keys.get("claude") or os.getenv("ANTHROPIC_API_KEY")
        )

    def _generate_with_single_provider(self, provider_name: str, llm, user_story: str, output_format: str, additional_context: str = "") -> Dict:
        """
        Generate test cases using a single LLM provider.
        
        Args:
            provider_name: Name of the provider (for logging/error handling)
            llm: The LLM instance to use
            user_story: The user story to generate tests for
            output_format: Output format ("plain" or "bdd")
            additional_context: Additional context from file analysis
        """
        # Combine user story with additional context
        full_context = user_story
        if additional_context:
            full_context += f"\n\nAdditional Context from Files:\n{additional_context}"
        
        if output_format.lower() == "plain":
            parser = PydanticOutputParser(pydantic_object=TestCaseList)
            prompt_template = """
            You are an expert QA engineer. From the user story and additional context: "{story}"
            
            Generate 5-10 comprehensive test cases in plain English, covering positive, negative, edge, and boundary scenarios.
            Include prerequisites, instructions, and expected criteria if relevant.
            
            Use the additional context from files (if provided) to understand requirements better and create more accurate test cases.
            
            IMPORTANT: Return ONLY a JSON array of test cases, not an object with an "items" key.
            
            {format_instructions}
            """
        elif output_format.lower() == "bdd":
            parser = PydanticOutputParser(pydantic_object=BDDScenarioList)
            prompt_template = """
            You are an expert QA engineer skilled in BDD. From the user story and additional context: "{story}"
            
            Generate 5-10 BDD scenarios in Gherkin format, covering positive, negative, edge, and boundary cases.
            Include prerequisites in 'Given', actions in 'When', expectations in 'Then'.
            
            Use the additional context from files (if provided) to understand requirements better and create more accurate scenarios.
            
            IMPORTANT: Return ONLY a JSON array of scenarios, not an object with an "items" key.
            
            {format_instructions}
            """
        else:
            raise ValueError("Output format must be 'plain' or 'bdd'.")

        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | llm

        try:
            # Get raw response from LLM
            raw_response = chain.invoke({
                "story": full_context,
                "format_instructions": parser.get_format_instructions(),
            })
            
            # Parse the response
            response_content = raw_response.content if hasattr(raw_response, 'content') else str(raw_response)
            
            # Try to parse with the parser
            try:
                return parser.parse(response_content)
            except Exception as parse_error:
                # Fallback: Try to handle the case where LLM returns {"items": [...]}
                try:
                    parsed_json = json.loads(response_content)
                    if isinstance(parsed_json, dict) and "items" in parsed_json:
                        # Extract the items array and re-parse
                        items_json = json.dumps(parsed_json["items"])
                        return parser.parse(items_json)
                    else:
                        # Re-raise the original parsing error
                        raise parse_error
                except json.JSONDecodeError:
                    # Re-raise the original parsing error
                    raise parse_error
                    
        except Exception as e:
            raise Exception(f"Failed to generate {output_format} test cases with {provider_name}: {str(e)}")


    def _generate_with_multiple_providers(self, user_story: str, output_format: str, additional_context: str = "") -> Dict:
        """
        Generate test cases using multiple LLM providers and combine results.
        
        Args:
            user_story: The user story to generate tests for
            output_format: Output format ("plain" or "bdd")
            additional_context: Additional context from file analysis
        """
        all_results = {}
        
        # Generate with each available provider
        for provider_name, llm in self.llms.items():
            try:
                result = self._generate_with_single_provider(
                    provider_name, llm, user_story, output_format, additional_context
                )
                all_results[provider_name] = result
            except Exception as e:
                print(f"Warning: Failed to generate with {provider_name}: {str(e)}")
                continue
        
        if not all_results:
            raise Exception("All LLM providers failed to generate test cases")
        
        # If only one provider succeeded, return its result
        if len(all_results) == 1:
            return list(all_results.values())[0]
        
        # Combine results from all providers
        combined_cases = []
        case_id_counter = 1
        
        for provider_name, result in all_results.items():
            provider_cases = result.root if hasattr(result, 'root') else result
            
            # Add provider information and renumber IDs
            for case in provider_cases:
                case_dict = case.dict() if hasattr(case, 'dict') else case
                case_dict['id'] = case_id_counter
                case_dict['provider'] = provider_name  # Track which provider generated this
                combined_cases.append(case_dict)
                case_id_counter += 1
        
        # Create a new root model with combined results
        if output_format.lower() == "plain":
            # Convert back to TestCase objects
            test_cases = [TestCase(**case) for case in combined_cases]
            return TestCaseList(test_cases)
        else:
            # Convert back to BDDScenario objects
            bdd_scenarios = [BDDScenario(**case) for case in combined_cases]
            return BDDScenarioList(bdd_scenarios)

    def _generate(self, user_story: str, output_format: str, additional_context: str = "") -> Dict:
        """
        Internal method to generate test cases using configured LLM provider(s).
        
        Args:
            user_story: The user story to generate tests for
            output_format: Output format ("plain" or "bdd")
            additional_context: Additional context from file analysis
        """
        # Use multiple providers if "all" is selected or if multiple providers are configured
        if self.llm_provider == "all" or len(self.llms) > 1:
            return self._generate_with_multiple_providers(user_story, output_format, additional_context)
        else:
            # Use single provider
            provider_name = list(self.llms.keys())[0]
            llm = list(self.llms.values())[0]
            return self._generate_with_single_provider(provider_name, llm, user_story, output_format, additional_context)

    def generate_test_cases(
        self,
        user_story: str,
        output_format: str = "bdd",
        num_cases: Optional[int] = None,
        additional_files: Optional[List[Union[str, Path]]] = None,
    ) -> List[Dict]:
        """
        Generate test cases from a raw user story string with optional file analysis.
        
        Args:
            user_story: The user story to generate tests for
            output_format: "plain" or "bdd"
            num_cases: Optional limit on number of test cases
            additional_files: Optional list of file paths to analyze for additional context
            
        Returns:
            List of dictionaries containing test case data
            
        Example:
            generator = StoryBDDGenerator(llm_provider="openai")
            cases = generator.generate_test_cases(
                "As a user, I want to log in so I can access my account.", 
                output_format="bdd",
                additional_files=["requirements.pdf", "ui_mockup.png"]
            )
        """
        additional_context = ""
        
        # Auto-discover input_files if no additional_files provided
        if additional_files is None:
            input_files_dir = Path("input_files")
            if input_files_dir.exists():
                # Find all supported files in input_files directory
                supported_extensions = {'.txt', '.md', '.json', '.csv', '.xml', '.pdf', '.docx', '.png', '.jpg', '.jpeg', '.webp'}
                auto_files = []
                for file_path in input_files_dir.iterdir():
                    if (file_path.is_file() and 
                        file_path.suffix.lower() in supported_extensions and
                        file_path.name.lower() != 'readme.md'):
                        auto_files.append(str(file_path))
                
                if auto_files:
                    additional_files = auto_files
                    print(f"Auto-discovered {len(auto_files)} supporting files from input_files/")
        
        # Analyze additional files if available
        if additional_files:
            try:
                file_results = self.file_analyzer.analyze_multiple_files(additional_files)
                additional_context = self.file_analyzer.generate_combined_analysis(file_results)
            except Exception as e:
                # Continue without file analysis if it fails
                additional_context = f"Note: File analysis failed: {str(e)}"
        
        root_result = self._generate(user_story, output_format, additional_context)
        
        # Extract the actual list from the RootModel
        result = root_result.root
        
        if num_cases:
            result = result[:num_cases]  # Trim if specified
        return [case.dict() for case in result]  # Convert to dicts for easy serialization

    def _format_plain_tests_to_markdown(self, test_cases: List[Dict], user_story: str) -> str:
        """Format plain English test cases to markdown format."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Check if any test case has provider info (indicating multi-provider mode)
        has_provider_info = any('provider' in case for case in test_cases)
        
        if has_provider_info:
            provider_text = " (Multi-Provider)"
        else:
            provider_text = ""
        
        md_content = f"""# Test Cases - Plain English Format{provider_text}

**Generated on:** {timestamp}

**User Story:** {user_story}

**LLM Provider(s):** {self.llm_provider}

---

"""
        
        for i, case in enumerate(test_cases, 1):
            provider_info = f" (Generated by: {case.get('provider', 'Unknown')})" if has_provider_info else ""
            md_content += f"""## Test Case {case.get('id', i)}: {case.get('title', 'Untitled')}{provider_info}

**Description:** {case.get('description', 'No description provided')}

**Type:** {case.get('type', 'Not specified')}

**Preconditions:** {case.get('preconditions') or 'None'}

**Steps:**
"""
            
            for step_num, step in enumerate(case.get('steps', []), 1):
                md_content += f"{step_num}. {step}\n"
            
            md_content += f"""
**Expected Result:** {case.get('expected', 'Not specified')}

---

"""
        
        return md_content

    def _format_bdd_tests_to_markdown(self, bdd_scenarios: List[Dict], user_story: str) -> str:
        """Format BDD scenarios to markdown format."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Check if any scenario has provider info (indicating multi-provider mode)
        has_provider_info = any('provider' in scenario for scenario in bdd_scenarios)
        
        if has_provider_info:
            provider_text = " (Multi-Provider)"
        else:
            provider_text = ""
        
        md_content = f"""# BDD Test Scenarios - Gherkin Format{provider_text}

**Generated on:** {timestamp}

**User Story:** {user_story}

**LLM Provider(s):** {self.llm_provider}

---

"""
        
        for i, scenario in enumerate(bdd_scenarios, 1):
            provider_info = f" (Generated by: {scenario.get('provider', 'Unknown')})" if has_provider_info else ""
            md_content += f"""## Scenario {i}: {scenario.get('scenario', 'Untitled Scenario')}{provider_info}

**Feature:** {scenario.get('feature', 'Not specified')}

```gherkin
Feature: {scenario.get('feature', 'Not specified')}

Scenario: {scenario.get('scenario', 'Untitled Scenario')}
"""
            
            # Add Given steps
            for given in scenario.get('given', []):
                md_content += f"  Given {given}\n"
            
            # Add When steps
            for when in scenario.get('when', []):
                md_content += f"  When {when}\n"
            
            # Add Then steps
            for then in scenario.get('then', []):
                md_content += f"  Then {then}\n"
            
            md_content += "```\n\n---\n\n"
        
        return md_content

    def export_to_markdown(
        self,
        user_story: str,
        output_dir: str = ".",
        filename_prefix: str = "test_cases",
        num_cases: Optional[int] = None,
        additional_files: Optional[List[Union[str, Path]]] = None
    ) -> Dict[str, str]:
        """
        Generate test cases and export them to separate markdown files.
        
        Args:
            user_story: The user story to generate tests for
            output_dir: Directory to save the markdown files
            filename_prefix: Prefix for the markdown filenames
            num_cases: Optional limit on number of test cases
            additional_files: Optional list of file paths to analyze for additional context
            
        Returns:
            Dictionary with file paths of generated markdown files
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate both types of test cases with file analysis
        plain_tests = self.generate_test_cases(
            user_story, 
            output_format="plain", 
            num_cases=num_cases,
            additional_files=additional_files
        )
        bdd_tests = self.generate_test_cases(
            user_story, 
            output_format="bdd", 
            num_cases=num_cases,
            additional_files=additional_files
        )
        
        # Format to markdown
        plain_md = self._format_plain_tests_to_markdown(plain_tests, user_story)
        bdd_md = self._format_bdd_tests_to_markdown(bdd_tests, user_story)
        
        # Create filenames
        plain_filename = f"{filename_prefix}_plain_{timestamp}.md"
        bdd_filename = f"{filename_prefix}_bdd_{timestamp}.md"
        
        plain_filepath = os.path.join(output_dir, plain_filename)
        bdd_filepath = os.path.join(output_dir, bdd_filename)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Write files
        with open(plain_filepath, 'w', encoding='utf-8') as f:
            f.write(plain_md)
        
        with open(bdd_filepath, 'w', encoding='utf-8') as f:
            f.write(bdd_md)
        
        return {
            "plain_english": plain_filepath,
            "bdd": bdd_filepath
        }


# Example usage
if __name__ == "__main__":
    # Example user story
    story = "As a user, I want to reset my password so I can regain access if forgotten."
    
    print("Phoenix-SmartCaseAI Multi-Provider Test Case Generator")
    print("=" * 60)
    
    # Example 1: OpenAI only
    print("\n1. Generating with OpenAI only...")
    try:
        gen_openai = StoryBDDGenerator(llm_provider="openai")
        file_paths_openai = gen_openai.export_to_markdown(
            user_story=story,
            output_dir="test_output",
            filename_prefix="password_reset_openai",
            num_cases=3
        )
        print(f"[OK] OpenAI Plain English tests: {file_paths_openai['plain_english']}")
        print(f"[OK] OpenAI BDD tests: {file_paths_openai['bdd']}")
    except Exception as e:
        print(f"[ERROR] OpenAI generation failed: {e}")
    
    # Example 2: Gemini only
    print("\n2. Generating with Gemini only...")
    try:
        gen_gemini = StoryBDDGenerator(llm_provider="gemini")
        file_paths_gemini = gen_gemini.export_to_markdown(
            user_story=story,
            output_dir="test_output",
            filename_prefix="password_reset_gemini",
            num_cases=3
        )
        print(f"[OK] Gemini Plain English tests: {file_paths_gemini['plain_english']}")
        print(f"[OK] Gemini BDD tests: {file_paths_gemini['bdd']}")
    except Exception as e:
        print(f"[ERROR] Gemini generation failed: {e}")
    
    # Example 3: Claude only
    print("\n3. Generating with Claude only...")
    try:
        gen_claude = StoryBDDGenerator(llm_provider="claude")
        file_paths_claude = gen_claude.export_to_markdown(
            user_story=story,
            output_dir="test_output",
            filename_prefix="password_reset_claude",
            num_cases=3
        )
        print(f"[OK] Claude Plain English tests: {file_paths_claude['plain_english']}")
        print(f"[OK] Claude BDD tests: {file_paths_claude['bdd']}")
    except Exception as e:
        print(f"[ERROR] Claude generation failed: {e}")
    
    # Example 4: Multi-provider (OpenAI + Gemini + Claude)
    print("\n4. Generating with ALL providers (OpenAI + Gemini + Claude)...")
    try:
        gen_all = StoryBDDGenerator(llm_provider="all")
        file_paths_all = gen_all.export_to_markdown(
            user_story=story,
            output_dir="test_output",
            filename_prefix="password_reset_all_providers",
            num_cases=15  # Will get more test cases from combined providers
        )
        print(f"[OK] All-Providers Plain English tests: {file_paths_all['plain_english']}")
        print(f"[OK] All-Providers BDD tests: {file_paths_all['bdd']}")
        print("All-providers generation combines results from OpenAI, Gemini, and Claude!")
    except Exception as e:
        print(f"[ERROR] All-providers generation failed: {e}")
    
    # Example 5: Custom API keys
    print("\n5. Example with custom API keys...")
    print("# You can also pass custom API keys:")
    print("""
    custom_keys = {
        "openai": "your-openai-key-here",
        "gemini": "your-google-api-key-here",
        "claude": "your-anthropic-api-key-here"
    }
    gen_custom = StoryBDDGenerator(
        llm_provider="all", 
        api_keys=custom_keys
    )
    """)
    
    print("\nBenefits of Multi-Provider Generation:")
    print("   • More diverse test case perspectives")
    print("   • Better coverage of edge cases")
    print("   • Fallback if one provider fails")
    print("   • Compare different LLM approaches")
    print("   • Each test case is labeled with its source provider")
    
    print("\nAvailable LLM Providers:")
    print("   • 'openai' - Use OpenAI GPT models only")
    print("   • 'gemini' - Use Google Gemini models only") 
    print("   • 'claude' - Use Claude (Anthropic) models only")
    print("   • 'all' - Use all providers and combine results")
    
    print("\nRequired Environment Variables:")
    print("   • OPENAI_API_KEY - for OpenAI provider")
    print("   • GOOGLE_API_KEY - for Gemini provider")
    print("   • ANTHROPIC_API_KEY - for Claude provider")
    print("   • Set all three for 'all' provider mode")