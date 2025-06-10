from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from fastapi.testclient import TestClient

# Initialize the FastAPI app
app = FastAPI()

# Pydantic model for request body validation
class CodeGenerationRequest(BaseModel):
    name: str
    given: str
    when: str
    then: str

# Function to generate Python code based on input request
def generate_code(request: CodeGenerationRequest):
    # Generate Python function code based on feature description
    code = f"""
def {request.name}():
    # Given: {request.given}
    # When: {request.when}
    # Then: {request.then}
    pass
    """
    
    # Save the generated code to a new file
    file_path = f"./generated_code/{request.name}.py"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, "w") as f:
        f.write(code)

    return {"message": f"Code for '{request.name}' generated successfully!", "file_path": file_path}

# POST endpoint for code generation
@app.post("/api/v1/generate_code")
def generate_code_endpoint(request: CodeGenerationRequest):
    try:
        result = generate_code(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Test Client setup
client = TestClient(app)

# Function to test the code generation functionality
def test_generate_code():
    feature_request = {
        "name": "calculate_sum",
        "given": "two numbers",
        "when": "added together",
        "then": "return their sum"
    }
    response = client.post("/api/v1/generate_code", json=feature_request)
    
    # Verify the generated file exists
    generated_file_path = response.json()["file_path"]
    file_exists = os.path.exists(generated_file_path)

    # Check the content of the generated file
    if file_exists:
        with open(generated_file_path, "r") as file:
            generated_code = file.read()
        assert "def calculate_sum()" in generated_code
        assert "return their sum" in generated_code
    
    # Print the test results
    print(response.status_code, response.json(), file_exists)

# Run the test
test_generate_code()
import ast
import os
import subprocess

class SelfEvolver:
    
    @staticmethod
    def analyze_code(file_path: str):
        """
        Analyzes a Python file to suggest improvements, including missing docstrings,
        long functions, unused variables, and inefficient logic.
        """
        suggestions = []
        
        # Basic Static Analysis (AST)
        with open(file_path, 'r') as file:
            file_content = file.read()
        
        tree = ast.parse(file_content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if ast.get_docstring(node) is None:
                    suggestions.append(f"Function '{node.name}' is missing a docstring.")
                if len(node.body) > 20:
                    suggestions.append(f"Function '{node.name}' is too long. Consider splitting it.")
        
        # AI-Powered Analysis using Mistral
        ai_suggestions = SelfEvolver.get_ai_suggestions(file_content)
        suggestions.extend(ai_suggestions)
        
        return suggestions

    @staticmethod
    def get_ai_suggestions(code: str):
        """
        Sends code to Mistral via ollama for AI-driven code analysis.
        """
        prompt = f"Analyze this Python code and suggest improvements. Focus on detecting unused variables, inefficient logic, and possible optimizations:\n\n{code}"
        
        try:
            # Run Mistral via Ollama
            result = subprocess.run(
                ["ollama", "run", "mistral", prompt],
                capture_output=True,
                text=True
            )
            
            # Process the AI suggestions
            ai_response = result.stdout.strip()
            return ai_response.split('\n')  # Assuming suggestions are separated by newlines
        
        except Exception as e:
            return [f"Error running Mistral analysis: {e}"]

    @staticmethod
    def apply_improvements(file_path: str, suggestions: list):
        """
        Applies basic improvements like adding docstrings based on suggestions.
        """
        with open(file_path, 'r') as file:
            file_content = file.readlines()

        for i, line in enumerate(file_content):
            if "def " in line:
                function_name = line.split('(')[0].replace("def ", "").strip()
                if f"Function '{function_name}' is missing a docstring." in suggestions:
                    file_content.insert(i + 1, f'    """TODO: Add docstring for {function_name}."""\n')

        with open(file_path, 'w') as file:
            file.writelines(file_content)

        return {"message": "Improvements applied successfully!"}
