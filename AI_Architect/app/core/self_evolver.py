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
