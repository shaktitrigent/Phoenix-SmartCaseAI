from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
from datetime import datetime
from pathlib import Path
import tempfile
import shutil
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from SmartCaseAI.generator import StoryBDDGenerator

app = Flask(__name__)
CORS(app)

# Ensure outputs directory exists
outputs_dir = Path("api-server/outputs")
outputs_dir.mkdir(exist_ok=True)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Phoenix-SmartCaseAI API'
    })

@app.route('/api/generate', methods=['POST'])
def generate_test_cases():
    """Generate test cases from user story"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'})
        
        user_story = data.get('user_story', '').strip()
        if not user_story:
            return jsonify({'success': False, 'error': 'User story is required'})
        
        llm_provider = data.get('llm_provider', 'openai')
        output_format = data.get('output_format', 'plain')
        num_cases = data.get('num_cases', 5)
        additional_files = data.get('additional_files', [])
        
        # Create session directory
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session_dir = outputs_dir / session_id
        session_dir.mkdir(exist_ok=True)
        
        # Save user story to file
        story_file = session_dir / "user_story.txt"
        with open(story_file, 'w', encoding='utf-8') as f:
            f.write(user_story)
        
        # Initialize generator
        start_time = datetime.now()
        
        try:
            # Get API keys from environment variables
            api_keys = {
                "openai": os.getenv("OPENAI_API_KEY"),
                "gemini": os.getenv("GEMINI_API_KEY"), 
                "claude": os.getenv("CLAUDE_API_KEY")
            }
            generator = StoryBDDGenerator(llm_provider=llm_provider, api_keys=api_keys)
        except Exception as e:
            return jsonify({'success': False, 'error': f'Failed to initialize generator: {str(e)}'})
        
        # Auto-discover additional files
        additional_files = []
        
        # Check for common test files in the project
        test_files = [
            "test_*.py", "tests/*.py", "spec/*.py", "features/*.py",
            "*_test.py", "*_spec.py", "test_*.js", "*.test.js"
        ]
        
        for pattern in test_files:
            for file_path in Path(".").rglob(pattern):
                if file_path.is_file() and file_path.suffix in ['.py', '.js', '.ts', '.java', '.rb']:
                    additional_files.append(str(file_path))
        
        # Limit to 5 additional files to avoid overwhelming the LLM
        additional_files = additional_files[:5]
        
        # Generate test cases based on format
        if output_format == 'both':
            try:
                plain_cases = generator.generate_test_cases(
                    user_story,
                    output_format="plain",
                    num_cases=num_cases,
                    additional_files=additional_files
                )
                plain_file = f"{session_id}_plain.md"
                plain_path = session_dir / plain_file
                with open(plain_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Test Cases - Plain English Format\n\n")
                    f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"**Provider:** {llm_provider}\n")
                    f.write(f"**User Story:** {user_story}\n\n")
                    for i, case in enumerate(plain_cases, 1):
                        f.write(f"## Test Case {i}: {case.get('title', 'Untitled')}\n\n")
                        f.write(f"**Description:** {case.get('description', 'No description')}\n\n")
                        f.write(f"**Steps:**\n")
                        for j, step in enumerate(case.get('steps', []), 1):
                            f.write(f"{j}. {step}\n")
                        f.write(f"\n**Expected Result:** {case.get('expected', 'Not specified')}\n\n")
            except Exception as e:
                print(f"Warning: Plain format generation failed: {e}")
                plain_cases = []

            try:
                bdd_cases = generator.generate_test_cases(
                    user_story,
                    output_format="bdd",
                    num_cases=num_cases,
                    additional_files=additional_files
                )
                bdd_file = f"{session_id}_bdd.md"
                bdd_path = session_dir / bdd_file
                with open(bdd_path, 'w', encoding='utf-8') as f:
                    f.write(f"# BDD Test Scenarios - Gherkin Format\n\n")
                    f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"**Provider:** {llm_provider}\n")
                    f.write(f"**User Story:** {user_story}\n\n")
                    for i, scenario in enumerate(bdd_cases, 1):
                        f.write(f"## Scenario {i}: {scenario.get('scenario', 'Untitled')}\n\n")
                        f.write(f"**Feature:** {scenario.get('feature', 'Test Feature')}\n\n")
                        f.write(f"```gherkin\n")
                        f.write(f"Feature: {scenario.get('feature', 'Test Feature')}\n\n")
                        f.write(f"Scenario: {scenario.get('scenario', 'Untitled')}\n")
                        for given in scenario.get('given', []):
                            f.write(f"  Given {given}\n")
                        for when in scenario.get('when', []):
                            f.write(f"  When {when}\n")
                        for then in scenario.get('then', []):
                            f.write(f"  Then {then}\n")
                        f.write(f"```\n\n")
            except Exception as e:
                print(f"Warning: BDD format generation failed: {e}")
                bdd_cases = []
                
            # Combine results
            all_cases = {
                'plain': plain_cases if 'plain_cases' in locals() else [],
                'bdd': bdd_cases if 'bdd_cases' in locals() else []
            }
            
            # Create combined markdown file
            combined_file = f"{session_id}_combined.md"
            combined_path = session_dir / combined_file
            with open(combined_path, 'w', encoding='utf-8') as f:
                f.write(f"# Test Cases - Combined Format\n\n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Provider:** {llm_provider}\n")
                f.write(f"**User Story:** {user_story}\n\n")
                
                if all_cases['plain']:
                    f.write(f"## Plain English Test Cases\n\n")
                    for i, case in enumerate(all_cases['plain'], 1):
                        f.write(f"### Test Case {i}: {case.get('title', 'Untitled')}\n\n")
                        f.write(f"**Description:** {case.get('description', 'No description')}\n\n")
                        f.write(f"**Steps:**\n")
                        for j, step in enumerate(case.get('steps', []), 1):
                            f.write(f"{j}. {step}\n")
                        f.write(f"\n**Expected Result:** {case.get('expected', 'Not specified')}\n\n")
                
                if all_cases['bdd']:
                    f.write(f"## BDD Test Scenarios\n\n")
                    for i, scenario in enumerate(all_cases['bdd'], 1):
                        f.write(f"### Scenario {i}: {scenario.get('scenario', 'Untitled')}\n\n")
                        f.write(f"**Feature:** {scenario.get('feature', 'Test Feature')}\n\n")
                        f.write(f"```gherkin\n")
                        f.write(f"Feature: {scenario.get('feature', 'Test Feature')}\n\n")
                        f.write(f"Scenario: {scenario.get('scenario', 'Untitled')}\n")
                        for given in scenario.get('given', []):
                            f.write(f"  Given {given}\n")
                        for when in scenario.get('when', []):
                            f.write(f"  When {when}\n")
                        for then in scenario.get('then', []):
                            f.write(f"  Then {then}\n")
                        f.write(f"```\n\n")
            
            # Return file paths for download
            files = []
            if plain_path.exists():
                files.append({'name': plain_file, 'path': str(plain_path), 'type': 'plain'})
            if bdd_path.exists():
                files.append({'name': bdd_file, 'path': str(bdd_path), 'type': 'bdd'})
            if combined_path.exists():
                files.append({'name': combined_file, 'path': str(combined_path), 'type': 'combined'})
            
            return jsonify({
                'success': True,
                'message': 'Test cases generated successfully',
                'cases': all_cases,
                'files': files,
                'session_id': session_id,
                'generation_time': (datetime.now() - start_time).total_seconds()
            })
        
        else:
            # Single format generation
            try:
                cases = generator.generate_test_cases(
                    user_story,
                    output_format=output_format,
                    num_cases=num_cases,
                    additional_files=additional_files
                )
                
                # Create markdown file
                file_name = f"{session_id}_{output_format}.md"
                file_path = session_dir / file_name
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    if output_format == 'plain':
                        f.write(f"# Test Cases - Plain English Format\n\n")
                        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"**Provider:** {llm_provider}\n")
                        f.write(f"**User Story:** {user_story}\n\n")
                        for i, case in enumerate(cases, 1):
                            f.write(f"## Test Case {i}: {case.get('title', 'Untitled')}\n\n")
                            f.write(f"**Description:** {case.get('description', 'No description')}\n\n")
                            f.write(f"**Steps:**\n")
                            for j, step in enumerate(case.get('steps', []), 1):
                                f.write(f"{j}. {step}\n")
                            f.write(f"\n**Expected Result:** {case.get('expected', 'Not specified')}\n\n")
                    else:  # BDD format
                        f.write(f"# BDD Test Scenarios - Gherkin Format\n\n")
                        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"**Provider:** {llm_provider}\n")
                        f.write(f"**User Story:** {user_story}\n\n")
                        for i, scenario in enumerate(cases, 1):
                            f.write(f"## Scenario {i}: {scenario.get('scenario', 'Untitled')}\n\n")
                            f.write(f"**Feature:** {scenario.get('feature', 'Test Feature')}\n\n")
                            f.write(f"```gherkin\n")
                            f.write(f"Feature: {scenario.get('feature', 'Test Feature')}\n\n")
                            f.write(f"Scenario: {scenario.get('scenario', 'Untitled')}\n")
                            for given in scenario.get('given', []):
                                f.write(f"  Given {given}\n")
                            for when in scenario.get('when', []):
                                f.write(f"  When {when}\n")
                            for then in scenario.get('then', []):
                                f.write(f"  Then {then}\n")
                            f.write(f"```\n\n")
                
                return jsonify({
                    'success': True,
                    'message': 'Test cases generated successfully',
                    'cases': cases,
                    'files': [{'name': file_name, 'path': str(file_path), 'type': output_format}],
                    'session_id': session_id,
                    'generation_time': (datetime.now() - start_time).total_seconds()
                })
                
            except Exception as e:
                return jsonify({'success': False, 'error': f'Generation failed: {str(e)}'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'})

@app.route('/api/download/<path:filename>')
def download_file(filename):
    """Download generated files"""
    try:
        # Security: Only allow files from outputs directory
        file_path = outputs_dir / filename
        if not file_path.exists() or not str(file_path).startswith(str(outputs_dir)):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions')
def list_sessions():
    """List all available sessions"""
    try:
        sessions = []
        for session_dir in outputs_dir.iterdir():
            if session_dir.is_dir():
                files = [f.name for f in session_dir.iterdir() if f.is_file()]
                sessions.append({
                    'session_id': session_dir.name,
                    'files': files,
                    'created': datetime.fromtimestamp(session_dir.stat().st_ctime).isoformat()
                })
        return jsonify({'sessions': sessions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
