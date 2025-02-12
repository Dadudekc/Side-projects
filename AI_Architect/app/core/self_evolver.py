import ast
import os

class SelfEvolver:
    
    @staticmethod
    def analyze_code(file_path: str):
        """
        Analyzes a Python file to suggest improvements.
        Returns a list of suggestions for improvement.
        """
        suggestions = []
        
        # Parse the Python file
        with open(file_path, 'r') as file:
            file_content = file.read()
        
        tree = ast.parse(file_content)
        
        # Check for missing docstrings in functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if ast.get_docstring(node) is None:
                    suggestions.append(f"Function '{node.name}' is missing a docstring.")
                
                # Check for long functions (arbitrary threshold of 20 lines)
                if len(node.body) > 20:
                    suggestions.append(f"Function '{node.name}' is too long. Consider splitting it.")
        
        return suggestions
    
    @staticmethod
    def apply_improvements(file_path: str, suggestions: list):
        """
        Applies basic improvements based on the suggestions.
        In this basic version, we add docstrings to functions missing them.
        """
        with open(file_path, 'r') as file:
            file_content = file.readlines()

        for i, line in enumerate(file_content):
            if "def " in line:
                function_name = line.split('(')[0].replace("def ", "").strip()
                # Add a basic docstring for each function without one
                if f"Function '{function_name}' is missing a docstring." in suggestions:
                    file_content.insert(i + 1, f'    """TODO: Add docstring for {function_name}."""\n')

        # Save the modified file with improvements
        with open(file_path, 'w') as file:
            file.writelines(file_content)

        return {"message": "Improvements applied successfully!"}
