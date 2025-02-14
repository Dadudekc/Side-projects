# -------------------------------------------------------------------
# File Path: C:\Projects\AI_Debugger_Assistant\src\error_detection\error_detection.py
#
# Project: AI_Debugger_Assistant
#
# Description:
# This file is part of the AI_Debugger_Assistant project.
# It provides tools to detect syntax, runtime, and logic errors within 
# Python code using various methods, including Python's built-in `exec`, 
# subprocess calls for static analysis tools, and custom error handling.
# The results provide detailed feedback on code issues for debugging 
# assistance and error correction.
#
# Classes:
# - ErrorDetector: Handles detection of syntax, runtime, and logic errors 
#   within provided code.
#
# Usage:
# The `ErrorDetector` class is designed to be instantiated with a code 
# snippet, providing methods to identify and classify different error types.
# -------------------------------------------------------------------

import ast
import subprocess
import tempfile
import traceback
import os

class ErrorDetector:
    """
    Class for detecting and classifying errors in Python code.
    Supports syntax error detection, runtime error handling, 
    and logic error identification through static analysis.
    """

    def __init__(self, code: str):
        """
        Initializes the ErrorDetector with code for analysis.
        
        Args:
            code (str): Python code to be analyzed.
        """
        self.code = code

    def detect_syntax_errors(self) -> str:
        """
        Detects syntax errors in the provided code using AST parsing.

        Returns:
            str: Description of syntax errors if found, or an empty string.
        """
        try:
            ast.parse(self.code)
            return ""
        except SyntaxError as e:
            return f"Syntax Error: {e.msg} (line {e.lineno})"

    def detect_runtime_errors(self, globals_=None, locals_=None) -> str:
        """
        Detects runtime errors by executing the code in a controlled environment.
        
        Args:
            globals_ (dict): Optional globals for code execution.
            locals_ (dict): Optional locals for code execution.

        Returns:
            str: Description of runtime errors if found, or an empty string.
        """
        try:
            exec(self.code, globals_ or {}, locals_ or {})
            return ""
        except Exception as e:
            return f"Runtime Error: {str(e)}\n" + traceback.format_exc()

    def detect_logic_errors(self) -> str:
        """
        Detects potential logic errors using static analysis with pylint.

        Returns:
            str: Output of pylint analysis indicating logic issues.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp_file:
            tmp_file.write(self.code.encode("utf-8"))
            tmp_file_path = tmp_file.name

        try:
            result = subprocess.run(
                ["pylint", tmp_file_path, "--disable=C,R,W"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Logic Error: {e.output.strip()}"
        finally:
            os.remove(tmp_file_path)

    def detect_all_errors(self) -> dict:
        """
        Detects all error types: syntax, runtime, and logic.

        Returns:
            dict: Dictionary of error types and their descriptions.
        """
        errors = {
            "syntax_errors": self.detect_syntax_errors(),
            "runtime_errors": self.detect_runtime_errors(),
            "logic_errors": self.detect_logic_errors()
        }
        return errors


# Example Usage:
if __name__ == "__main__":
    code_snippet = """
for i in range(10)
    print(i)
"""
    detector = ErrorDetector(code_snippet)
    all_errors = detector.detect_all_errors()
    print("Syntax Errors:", all_errors["syntax_errors"])
    print("Runtime Errors:", all_errors["runtime_errors"])
    print("Logic Errors:", all_errors["logic_errors"])


# -------------------------------------------------------------------
# Value-Adding Improvements
# -------------------------------------------------------------------
# 1. **Automated Error Correction Suggestions**: Implement a method 
#    to offer possible fixes for syntax errors, using NLP or AI to 
#    analyze common patterns and provide context-aware corrections.
#
# 2. **Logic Error Categorization**: Classify logic errors by severity 
#    (e.g., minor, major) based on the pylint output, aiding in 
#    prioritizing fixes.
#
# 3. **Error Logging and Reporting**: Integrate with an external logging 
#    system or dashboard for tracking error frequencies, locations, 
#    and potential patterns over time.
# -------------------------------------------------------------------
