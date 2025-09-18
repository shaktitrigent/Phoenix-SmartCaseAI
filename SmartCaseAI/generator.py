import os
from datetime import datetime
from typing import List, Dict, Optional

from pydantic import BaseModel, Field, RootModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI


class TestCase(BaseModel):
    """Structured test case model."""
    id: int = Field(description="Unique test case ID")
    title: str = Field(description="Test case title")
    description: str = Field(description="Detailed description")
    preconditions: Optional[str] = Field(default=None, description="Prerequisites or setup")
    steps: List[str] = Field(description="Step-by-step instructions")
    expected: str = Field(description="Expected outcome")
    type: str = Field(description="Type: positive, negative, edge, etc.")
    
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
        api_key: Optional[str] = None,
    ):
        """
        Initialize the generator with chosen LLM.
        
        Args:
            llm_provider: LLM provider to use (currently only "openai" supported)
            api_key: API key for the LLM provider (optional, uses env var if not provided)
        """
        if llm_provider == "openai":
            key = api_key or os.getenv("OPENAI_API_KEY")
            if not key:
                raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
            self.llm = ChatOpenAI(model="gpt-5-nano", api_key=key)
        else:
            raise ValueError("Currently only 'openai' provider is supported.")

    def _generate(self, user_story: str, output_format: str) -> Dict:
        """
        Internal method to generate test cases using LLM.
        """
        if output_format.lower() == "plain":
            parser = PydanticOutputParser(pydantic_object=TestCaseList)
            prompt_template = """
            You are an expert QA engineer. From the user story: "{story}"
            
            Generate 5-10 comprehensive test cases in plain English, covering positive, negative, edge, and boundary scenarios.
            Include prerequisites, instructions, and expected criteria if relevant.
            
            IMPORTANT: Return ONLY a JSON array of test cases, not an object with an "items" key.
            
            {format_instructions}
            """
        elif output_format.lower() == "bdd":
            parser = PydanticOutputParser(pydantic_object=BDDScenarioList)
            prompt_template = """
            You are an expert QA engineer skilled in BDD. From the user story: "{story}"
            
            Generate 5-10 BDD scenarios in Gherkin format, covering positive, negative, edge, and boundary cases.
            Include prerequisites in 'Given', actions in 'When', expectations in 'Then'.
            
            IMPORTANT: Return ONLY a JSON array of scenarios, not an object with an "items" key.
            
            {format_instructions}
            """
        else:
            raise ValueError("Output format must be 'plain' or 'bdd'.")

        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | self.llm

        try:
            # Get raw response from LLM
            raw_response = chain.invoke({
                "story": user_story,
                "format_instructions": parser.get_format_instructions(),
            })
            
            # Parse the response
            response_content = raw_response.content if hasattr(raw_response, 'content') else str(raw_response)
            
            # Try to parse with the parser
            try:
                return parser.parse(response_content)
            except Exception as parse_error:
                # Fallback: Try to handle the case where LLM returns {"items": [...]}
                import json
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
            raise Exception(f"Failed to generate {output_format} test cases: {str(e)}")

    def generate_test_cases(
        self,
        user_story: str,
        output_format: str = "bdd",
        num_cases: Optional[int] = None,
    ) -> List[Dict]:
        """
        Generate test cases from a raw user story string.
        
        Args:
            user_story: The user story to generate tests for
            output_format: "plain" or "bdd"
            num_cases: Optional limit on number of test cases
            
        Returns:
            List of dictionaries containing test case data
            
        Example:
            generator = StoryBDDGenerator(llm_provider="openai")
            cases = generator.generate_test_cases(
                "As a user, I want to log in so I can access my account.", 
                output_format="bdd"
            )
        """
        root_result = self._generate(user_story, output_format)
        
        # Extract the actual list from the RootModel
        result = root_result.root
        
        if num_cases:
            result = result[:num_cases]  # Trim if specified
        return [case.dict() for case in result]  # Convert to dicts for easy serialization

    def _format_plain_tests_to_markdown(self, test_cases: List[Dict], user_story: str) -> str:
        """Format plain English test cases to markdown format."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        md_content = f"""# Test Cases - Plain English Format

**Generated on:** {timestamp}

**User Story:** {user_story}

---

"""
        
        for i, case in enumerate(test_cases, 1):
            md_content += f"""## Test Case {case.get('id', i)}: {case.get('title', 'Untitled')}

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
        
        md_content = f"""# BDD Test Scenarios - Gherkin Format

**Generated on:** {timestamp}

**User Story:** {user_story}

---

"""
        
        for i, scenario in enumerate(bdd_scenarios, 1):
            md_content += f"""## Scenario {i}: {scenario.get('scenario', 'Untitled Scenario')}

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
        num_cases: Optional[int] = None
    ) -> Dict[str, str]:
        """
        Generate test cases and export them to separate markdown files.
        
        Args:
            user_story: The user story to generate tests for
            output_dir: Directory to save the markdown files
            filename_prefix: Prefix for the markdown filenames
            num_cases: Optional limit on number of test cases
            
        Returns:
            Dictionary with file paths of generated markdown files
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate both types of test cases
        plain_tests = self.generate_test_cases(user_story, output_format="plain", num_cases=num_cases)
        bdd_tests = self.generate_test_cases(user_story, output_format="bdd", num_cases=num_cases)
        
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
    gen = StoryBDDGenerator(llm_provider="openai")
    
    # Example user story
    story = "As a user, I want to reset my password so I can regain access if forgotten."
    
    # Generate and export to separate markdown files
    print("Generating test cases and exporting to markdown files...")
    file_paths = gen.export_to_markdown(
        user_story=story,
        output_dir="test_output",
        filename_prefix="password_reset_tests",
        num_cases=5
    )
    
    print(f"✅ Plain English tests saved to: {file_paths['plain_english']}")
    print(f"✅ BDD tests saved to: {file_paths['bdd']}")