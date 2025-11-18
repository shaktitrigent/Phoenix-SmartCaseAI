"""
FastAPI Web Application for Phoenix-SmartCaseAI

Provides a web interface and API for generating BDD test cases from user stories.
"""

import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import tempfile
import shutil

from .generator import StoryBDDGenerator

# Initialize FastAPI app
app = FastAPI(
    title="Phoenix-SmartCaseAI API",
    description="AI-powered test case generation from user stories",
    version="1.0.0"
)

# Create outputs directory
outputs_dir = Path(__file__).parent.parent.parent / "outputs"
outputs_dir.mkdir(exist_ok=True)


class GenerateRequest(BaseModel):
    """Request model for BDD generation."""
    user_story: str
    llm_provider: str = "openai"
    output_format: str = "bdd"  # "plain", "bdd", or "both"
    num_cases: int = 5


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface."""
    # Read the HTML template from the web-interface-two-panel folder
    # Try multiple possible paths
    possible_paths = [
        Path(__file__).parent.parent.parent / "web-interface-two-panel" / "index.html",
        Path.cwd() / "web-interface-two-panel" / "index.html",
        Path("web-interface-two-panel") / "index.html",
    ]
    
    html_file = None
    for path in possible_paths:
        if path.exists():
            html_file = path
            break
    
    if html_file and html_file.exists():
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Update the API endpoint to use the FastAPI endpoint
        html_content = html_content.replace(
            "const API_BASE_URL = 'http://localhost:5000';",
            "const API_BASE_URL = '';  // Use relative URLs for same-origin requests"
        )
        html_content = html_content.replace(
            "await fetch(`${API_BASE_URL}/api/generate`, {",
            "await fetch(`${API_BASE_URL}/generate-bdd`, {"
        )
        html_content = html_content.replace(
            "const response = await fetch(`${API_BASE_URL}/`);",
            "const response = await fetch(`${API_BASE_URL}/health`);"
        )
        html_content = html_content.replace(
            "document.getElementById('email').value = '';",
            "// Email field removed"
        )
        
        return HTMLResponse(content=html_content)
    
    # Fallback to embedded HTML if file not found
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Phoenix-SmartCaseAI - BDD Test Case Generator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header p {
            opacity: 0.9;
            font-size: 1.1em;
        }
        .content {
            padding: 40px;
        }
        .form-group {
            margin-bottom: 25px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        textarea, select, input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            font-family: inherit;
            transition: border-color 0.3s;
        }
        textarea {
            min-height: 150px;
            resize: vertical;
        }
        textarea:focus, select:focus, input:focus {
            outline: none;
            border-color: #667eea;
        }
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 18px;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            width: 100%;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }
        button:active {
            transform: translateY(0);
        }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .output-section {
            margin-top: 40px;
            padding: 25px;
            background: #f8f9fa;
            border-radius: 8px;
            display: none;
        }
        .output-section.show {
            display: block;
        }
        .output-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .output-header h2 {
            color: #333;
        }
        .output-content {
            background: white;
            padding: 20px;
            border-radius: 8px;
            max-height: 600px;
            overflow-y: auto;
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.6;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #667eea;
        }
        .error {
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }
        .success {
            background: #efe;
            color: #3c3;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }
        .file-upload {
            margin-top: 10px;
        }
        .file-upload input[type="file"] {
            padding: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Phoenix-SmartCaseAI</h1>
            <p>AI-Powered BDD Test Case Generator</p>
        </div>
        <div class="content">
            <form id="generateForm">
                <div class="form-group">
                    <label for="user_story">User Story</label>
                    <textarea 
                        id="user_story" 
                        name="user_story" 
                        placeholder="As a user, I want to log in so I can access my dashboard..."
                        required></textarea>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="output_format">Output Format</label>
                        <select id="output_format" name="output_format">
                            <option value="bdd">BDD (Gherkin)</option>
                            <option value="plain">Plain English</option>
                            <option value="both">Both Formats</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="llm_provider">LLM Provider</label>
                        <select id="llm_provider" name="llm_provider">
                            <option value="openai">OpenAI</option>
                            <option value="gemini">Google Gemini</option>
                            <option value="claude">Claude (Anthropic)</option>
                        </select>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="num_cases">Number of Test Cases</label>
                    <input 
                        type="number" 
                        id="num_cases" 
                        name="num_cases" 
                        value="5" 
                        min="1" 
                        max="20"
                        required>
                </div>
                
                <div class="form-group">
                    <label>Additional Files (Optional)</label>
                    <div class="file-upload">
                        <input type="file" id="files" name="files" multiple accept=".txt,.md,.pdf,.docx,.json,.xml,.png,.jpg,.jpeg">
                        <small>Supports: txt, md, pdf, docx, json, xml, images</small>
                    </div>
                </div>
                
                <button type="submit" id="generateBtn">Generate Test Cases</button>
            </form>
            
            <div id="loading" class="loading" style="display: none;">
                <p>🔄 Generating test cases... This may take a moment.</p>
            </div>
            
            <div id="error" class="error" style="display: none;"></div>
            <div id="success" class="success" style="display: none;"></div>
            
            <div id="output" class="output-section">
                <div class="output-header">
                    <h2>Generated Test Cases</h2>
                </div>
                <div id="outputContent" class="output-content"></div>
            </div>
        </div>
    </div>
    
    <script>
        document.getElementById('generateForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const form = e.target;
            const loading = document.getElementById('loading');
            const error = document.getElementById('error');
            const success = document.getElementById('success');
            const output = document.getElementById('output');
            const outputContent = document.getElementById('outputContent');
            const generateBtn = document.getElementById('generateBtn');
            
            // Reset UI
            loading.style.display = 'block';
            error.style.display = 'none';
            success.style.display = 'none';
            output.classList.remove('show');
            generateBtn.disabled = true;
            
            // Prepare form data
            const formData = new FormData();
            formData.append('user_story', document.getElementById('user_story').value);
            formData.append('output_format', document.getElementById('output_format').value);
            formData.append('llm_provider', document.getElementById('llm_provider').value);
            formData.append('num_cases', document.getElementById('num_cases').value);
            
            // Add files if any
            const filesInput = document.getElementById('files');
            for (let file of filesInput.files) {
                formData.append('files', file);
            }
            
            try {
                const response = await fetch('/generate-bdd', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Generation failed');
                }
                
                // Display results
                if (data.output_format === 'both' || data.output_format === 'bdd') {
                    outputContent.textContent = data.bdd_content || data.test_cases_markdown || 'No content generated';
                } else {
                    outputContent.textContent = data.test_cases_markdown || 'No content generated';
                }
                
                output.classList.add('show');
                success.textContent = `✅ Successfully generated ${data.num_generated_cases || 0} test cases!`;
                success.style.display = 'block';
                
            } catch (err) {
                error.textContent = '❌ Error: ' + err.message;
                error.style.display = 'block';
            } finally {
                loading.style.display = 'none';
                generateBtn.disabled = false;
            }
        });
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "Phoenix-SmartCaseAI API", "version": "1.0.0"}


@app.post("/generate-bdd")
async def generate_bdd(
    user_story: str = Form(...),
    llm_provider: str = Form("openai"),
    output_format: str = Form("bdd"),
    num_cases: int = Form(5),
    files: Optional[List[UploadFile]] = File(None)
):
    """
    Generate BDD test cases from a user story.
    
    Accepts form data with:
    - user_story: The user story text
    - llm_provider: LLM provider to use (openai, gemini, claude)
    - output_format: Output format (plain, bdd, both)
    - num_cases: Number of test cases to generate
    - files: Optional uploaded files for additional context
    """
    try:
        if not user_story.strip():
            raise HTTPException(status_code=400, detail="User story is required")
        
        # Get API keys from environment
        api_keys = {
            "openai": os.getenv("OPENAI_API_KEY"),
            "gemini": os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"),
            "claude": os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY"),
        }
        
        # Initialize generator
        generator = StoryBDDGenerator(llm_provider=llm_provider, api_keys=api_keys)
        
        # Handle uploaded files
        additional_files = []
        temp_dir = None
        temp_files = []
        
        if files:
            # Create temporary directory for uploaded files
            # Use a more reliable temp directory location
            try:
                temp_dir = tempfile.mkdtemp(prefix="phoenix_smartcaseai_")
            except Exception as e:
                # Fallback to current directory temp folder
                temp_dir = Path.cwd() / "temp_uploads"
                temp_dir.mkdir(exist_ok=True)
            
            try:
                for uploaded_file in files:
                    if not uploaded_file.filename:
                        continue
                    
                    # Create a safe filename
                    safe_filename = "".join(c for c in uploaded_file.filename if c.isalnum() or c in "._- ")
                    if not safe_filename:
                        safe_filename = f"file_{len(temp_files)}"
                    
                    # Save file to temp directory
                    file_path = Path(temp_dir) / safe_filename
                    
                    # Ensure the file is read completely before saving
                    file_content = await uploaded_file.read()
                    
                    # Write file content
                    with open(file_path, "wb") as f:
                        f.write(file_content)
                    
                    # Ensure file is closed and accessible
                    file_path_str = str(file_path.resolve())
                    additional_files.append(file_path_str)
                    temp_files.append(file_path)
                    
            except Exception as e:
                # Clean up on error
                for temp_file in temp_files:
                    try:
                        if temp_file.exists():
                            temp_file.unlink()
                    except:
                        pass
                if temp_dir and Path(temp_dir).exists():
                    try:
                        shutil.rmtree(temp_dir, ignore_errors=True)
                    except:
                        pass
                raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")
        
        # Generate test cases
        start_time = datetime.now()
        
        if output_format == "both":
            # Generate both formats
            plain_cases = generator.generate_test_cases(
                user_story=user_story,
                output_format="plain",
                num_cases=num_cases,
                additional_files=additional_files if additional_files else None
            )
            bdd_cases = generator.generate_test_cases(
                user_story=user_story,
                output_format="bdd",
                num_cases=num_cases,
                additional_files=additional_files if additional_files else None
            )
            
            # Format output
            plain_md = generator._format_plain_tests_to_markdown(plain_cases, user_story)
            bdd_md = generator._format_bdd_tests_to_markdown(bdd_cases, user_story)
            
            result = {
                "success": True,
                "message": "Test cases generated successfully",
                "provider": llm_provider,
                "output_format": "both",
                "num_generated_cases": len(plain_cases) + len(bdd_cases),
                "test_cases_markdown": plain_md,
                "bdd_content": bdd_md,
                "generation_time": (datetime.now() - start_time).total_seconds()
            }
        else:
            # Generate single format
            cases = generator.generate_test_cases(
                user_story=user_story,
                output_format=output_format,
                num_cases=num_cases,
                additional_files=additional_files if additional_files else None
            )
            
            # Format output
            if output_format == "plain":
                content = generator._format_plain_tests_to_markdown(cases, user_story)
                result = {
                    "success": True,
                    "message": "Test cases generated successfully",
                    "provider": llm_provider,
                    "output_format": "plain",
                    "num_generated_cases": len(cases),
                    "test_cases_markdown": content,
                    "bdd_content": "",
                    "generation_time": (datetime.now() - start_time).total_seconds()
                }
            else:  # bdd
                content = generator._format_bdd_tests_to_markdown(cases, user_story)
                result = {
                    "success": True,
                    "message": "Test cases generated successfully",
                    "provider": llm_provider,
                    "output_format": "bdd",
                    "num_generated_cases": len(cases),
                    "test_cases_markdown": "",
                    "bdd_content": content,
                    "generation_time": (datetime.now() - start_time).total_seconds()
                }
        
        return result
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        # Log the full error for debugging
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in generate_bdd: {error_trace}")
        raise HTTPException(
            status_code=500, 
            detail=f"Generation failed: {str(e)}. Please check your API keys and try again."
        )
    finally:
        # Clean up temporary files after generation is complete
        # Add a small delay to ensure files are released
        time.sleep(0.1)
        
        # Clean up individual files
        for temp_file in temp_files:
            try:
                if temp_file.exists():
                    # Try to close any open handles
                    try:
                        temp_file.unlink()
                    except PermissionError:
                        # File might still be in use, try again after a delay
                        time.sleep(0.5)
                        try:
                            temp_file.unlink()
                        except:
                            pass
            except Exception:
                pass
        
        # Clean up temp directory
        if temp_dir and Path(temp_dir).exists():
            try:
                # Try to remove directory
                shutil.rmtree(temp_dir, ignore_errors=True)
            except PermissionError:
                # Directory might have locked files, try again
                time.sleep(0.5)
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except:
                    pass
            except Exception:
                pass

