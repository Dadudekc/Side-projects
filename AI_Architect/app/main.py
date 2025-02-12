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
