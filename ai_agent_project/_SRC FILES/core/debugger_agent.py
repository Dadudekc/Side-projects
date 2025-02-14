# -------------------------------------------------------------------
# File Path: C:\Projects\AI_Debugger_Assistant\src\agents\core\DebuggerAgent.py
#
# Project: AI_Debugger_Assistant
#
# Description:
# This file defines the `DebuggerAgent` class, an agent specializing in 
# detecting and resolving syntax, runtime, and logical errors in code. 
# It leverages AI-driven insights via Ollama and Mistral through the 
# command line to identify and fix common coding issues, particularly 
# useful in development and code review scenarios. 
#
# Classes:
# - DebuggerAgent: Extends `AgentBase` to provide task-specific methods 
#   for error detection and resolution, integrating with diagnostic tools.
#
# Usage:
# This module is instantiated and managed by the core agent dispatcher
# in the AI_Debugger_Assistant project.
# -------------------------------------------------------------------

import subprocess
import logging
import tempfile
import os
import asyncio
import json
# Dynamically set the project root
import sys
import os

# Add the project root directory to the system path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, project_root)

from ai_agent_project.src.agents.core.utilities.agent_base import AgentBase
from ai_agent_project.src.agents.core.utilities.ai_agent_utils import track_performance
from ai_agent_project.src.agents.core.utilities.ai_model import AIModel
from ai_agent_project.src.agents.core.utilities.ollama_model import OllamaModel
from ai_agent_project.src.agents.core.utilities.mistral_model import MistralModel
from ai_agent_project.src.agents.core.utilities.ai_cache import AICache
from typing import Dict, Any

class DebuggerAgent(AgentBase):
    """
    An agent specialized in debugging code by detecting syntax, runtime, 
    and logical errors. Uses both internal methods and external tools to 
    identify issues in code snippets.
    
    Attributes:
        name (str): The name of the agent.
        description (str): A brief description of the agent's purpose.
    """

    def __init__(self, name="DebuggerAgent", description="Agent for code debugging and error resolution", config_path: str = "ai_agent_project/config/config.yaml"):
        """
        Initializes the DebuggerAgent with default parameters and sets up AI models.

        Args:
            name (str): The agent's name.
            description (str): A short description of the agent's role.
            config_path (str): Path to the configuration YAML file.
        """
        super().__init__(name, description)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.setup_logging(config_path)
        self.logger.info(f"{self.name} initialized with debugging capabilities.")
        self.config = self.load_config(config_path)
        self.ai_models = self.initialize_ai_models()
        self.ai_cache = AICache(self.config.get('cache', {}).get('cache_file', 'ai_cache.json'))

    def setup_logging(self, config_path: str):
        """
        Sets up logging based on the configuration file.

        Args:
            config_path (str): Path to the configuration YAML file.
        """
        import yaml

        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            raise Exception(f"Failed to load configuration: {str(e)}")

        logging_config = config.get('logging', {})
        log_level = getattr(logging, logging_config.get('level', 'INFO').upper(), logging.INFO)
        log_format = logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handlers = logging_config.get('handlers', ['console'])

        logging.basicConfig(level=log_level, format=log_format)

        if 'file' in handlers:
            log_file = os.path.join('logs', 'debugger_agent.log')
            os.makedirs('logs', exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(logging.Formatter(log_format))
            logging.getLogger().addHandler(file_handler)

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Loads the configuration from a YAML file.

        Args:
            config_path (str): Path to the configuration YAML file.

        Returns:
            dict: Configuration dictionary.
        """
        import yaml

        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            self.logger.info("Configuration loaded successfully.")
            return config
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            return {}

    def initialize_ai_models(self) -> Dict[str, AIModel]:
        """
        Initializes AI models based on the configuration.

        Returns:
            dict: Dictionary of AI model instances.
        """
        ai_models_config = self.config.get('ai_models', [])
        ai_models = {}
        for model_conf in ai_models_config:
            if model_conf.get('enabled', False):
                name = model_conf.get('name')
                command = model_conf.get('command')
                if name == "Ollama":
                    ai_models[name] = OllamaModel(command)
                elif name == "Mistral":
                    ai_models[name] = MistralModel(command)
                # Add more AI models here as needed
        self.logger.info(f"Initialized AI models: {list(ai_models.keys())}")
        return ai_models

    @track_performance
    async def perform_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform debugging based on the provided code and detect errors asynchronously.
        
        Args:
            task_data (dict): Contains code and other parameters for debugging.

        Returns:
            dict: Summary of detected issues and suggested fixes.
        """
        code = task_data.get("code", "")
        syntax_errors = await self.detect_syntax_errors(code)
        runtime_errors = await self.detect_runtime_errors(code)
        logic_errors = await self.detect_logic_errors(code)

        error_summary = {
            "syntax_errors": syntax_errors,
            "runtime_errors": runtime_errors,
            "logic_errors": logic_errors
        }

        self.logger.info(f"Task completed with error summary: {error_summary}")

        suggested_fixes = await self.suggest_fixes(error_summary)
        report = {
            "error_summary": error_summary,
            "suggested_fixes": suggested_fixes
        }

        return report

    async def detect_syntax_errors(self, code: str) -> str:
        """
        Checks the provided code for syntax errors.

        Args:
            code (str): The code snippet to check.

        Returns:
            str: Syntax error details or "No syntax errors detected."
        """
        try:
            compile(code, "<string>", "exec")
            self.logger.info("No syntax errors detected.")
            return "No syntax errors detected."
        except SyntaxError as e:
            error_message = f"Syntax Error: {e.text.strip()} (Line {e.lineno})"
            self.logger.error(error_message)
            return error_message

    async def detect_runtime_errors(self, code: str) -> str:
        """
        Executes the code in a restricted environment to detect runtime errors.

        Args:
            code (str): The code snippet to execute.

        Returns:
            str: Runtime error details or "No runtime errors detected."
        """
        try:
            # Define a restricted execution environment
            exec_globals = {"__builtins__": {}}
            exec_locals = {}
            exec(code, exec_globals, exec_locals)
            self.logger.info("No runtime errors detected.")
            return "No runtime errors detected."
        except Exception as e:
            error_message = f"Runtime Error: {str(e)}"
            self.logger.error(error_message)
            return error_message

    async def detect_logic_errors(self, code: str) -> str:
        """
        Uses an external static analysis tool (e.g., pylint) to detect logical errors.

        Args:
            code (str): The code snippet to analyze.

        Returns:
            str: Logic error details or "No logic errors detected."
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
            temp_file.write(code.encode("utf-8"))
            temp_file_path = temp_file.name

        try:
            process = await asyncio.create_subprocess_exec(
                "pylint", temp_file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                self.logger.info("Logic errors detected using pylint.")
                return stdout.decode()
            else:
                self.logger.info("No logic errors detected.")
                return "No logic errors detected."
        except FileNotFoundError:
            error_message = "Pylint is not installed or not accessible in the PATH."
            self.logger.error(error_message)
            return error_message
        except Exception as e:
            error_message = f"Error during logic error detection: {str(e)}"
            self.logger.error(error_message)
            return error_message
        finally:
            os.remove(temp_file_path)

    async def suggest_fixes(self, error_summary: Dict[str, str]) -> Dict[str, str]:
        """
        Suggests potential fixes based on detected errors.

        Args:
            error_summary (dict): A dictionary containing detected errors.

        Returns:
            dict: Suggested fixes for each detected error type.
        """
        fixes = {}
        for error_type, error_message in error_summary.items():
            if "syntax" in error_type.lower():
                fixes[error_type] = "Check the syntax, especially missing colons or parentheses."
            elif "runtime" in error_type.lower():
                fixes[error_type] = "Verify variable definitions and ensure proper data handling."
            elif "logic" in error_type.lower():
                fixes[error_type] = "Review code logic or try running pylint for detailed feedback."
            else:
                fixes[error_type] = "No suggestions available."

        # AI-Driven Fix Suggestions via Ollama and Mistral
        ai_fixes = await self.ai_generate_fixes(error_summary)
        fixes.update(ai_fixes)

        self.logger.info("Generated fix suggestions for detected errors.")
        return fixes

    async def ai_generate_fixes(self, error_summary: Dict[str, str]) -> Dict[str, str]:
        """
        Generates AI-driven fix suggestions using configured AI models.

        Args:
            error_summary (dict): A dictionary containing detected errors.

        Returns:
            dict: AI-generated fix suggestions.
        """
        ai_fixes = {}
        tasks = []
        for error_type, error_message in error_summary.items():
            for model_name, model in self.ai_models.items():
                task = asyncio.create_task(self.get_ai_fix(model_name, model, error_type, error_message))
                tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        for result in results:
            if result:
                model_name, error_type, fix = result
                ai_fixes[f"{model_name}_{error_type}"] = fix

        # Save fixes to cache
        for key, fix in ai_fixes.items():
            model_name, error_type = key.split("_", 1)
            self.ai_cache.set_fix(model_name, error_type, error_summary[error_type], fix)
        
        # Save cache asynchronously
        asyncio.create_task(self.save_cache())

        return ai_fixes

    async def get_ai_fix(self, model_name: str, model: AIModel, error_type: str, error_message: str):
        """
        Fetches AI-generated fix suggestions from a specific AI model, utilizing caching.

        Args:
            model_name (str): Name of the AI model.
            model (AIModel): Instance of the AI model.
            error_type (str): Type of error detected.
            error_message (str): Details of the error.

        Returns:
            tuple: (model_name, error_type, fix) or None if failed.
        """
        if self.config.get('cache', {}).get('enabled', False):
            cached_fix = await self.ai_cache.get_fix(model_name, error_type, error_message)
            if cached_fix:
                self.logger.info(f"Retrieved cached fix for {model_name} - {error_type}: {cached_fix}")
                return (model_name, error_type, cached_fix)

        fix = await model.generate_fix(error_type, error_message)
        if fix:
            return (model_name, error_type, fix)
        return None

    async def save_cache(self):
        """
        Saves the AI cache asynchronously.
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.ai_cache.save_cache)

    def export_report(self, report: Dict[str, Any], format: str = "json") -> str:
        """
        Exports the error summary and suggested fixes in the specified format.

        Args:
            report (dict): The report containing error summaries and suggested fixes.
            format (str): The format to export the report ('json' or 'html').

        Returns:
            str: Path to the exported report or error message.
        """
        if format.lower() == "json":
            report_path = os.path.join(os.getcwd(), "debug_report.json")
            try:
                with open(report_path, "w") as report_file:
                    json.dump(report, report_file, indent=4)
                self.logger.info(f"Error report exported in JSON format at {report_path}")
                return f"Report saved to {report_path}"
            except Exception as e:
                error_message = f"Failed to export JSON report: {str(e)}"
                self.logger.error(error_message)
                return error_message

        elif format.lower() == "html":
            report_path = os.path.join(os.getcwd(), "debug_report.html")
            try:
                with open(report_path, "w") as report_file:
                    report_file.write("<html><body><h2>Error Report</h2><h3>Summary</h3><ul>")
                    for error_type, error_message in report["error_summary"].items():
                        report_file.write(f"<li><strong>{error_type}:</strong> {error_message}</li>")
                    report_file.write("</ul><h3>Suggested Fixes</h3><ul>")
                    for fix_type, fix_message in report["suggested_fixes"].items():
                        report_file.write(f"<li><strong>{fix_type}:</strong> {fix_message}</li>")
                    report_file.write("</ul></body></html>")
                self.logger.info(f"Error report exported in HTML format at {report_path}")
                return f"Report saved to {report_path}"
            except Exception as e:
                error_message = f"Failed to export HTML report: {str(e)}"
                self.logger.error(error_message)
                return error_message

        else:
            error_message = "Unsupported format. Please choose 'json' or 'html'."
            self.logger.error(error_message)
            return error_message

    async def apply_fixes(self, code: str, suggested_fixes: Dict[str, str]) -> str:
        """
        Applies suggested fixes to the provided code.

        Args:
            code (str): Original code snippet.
            suggested_fixes (dict): Dictionary of suggested fixes.

        Returns:
            str: Code with applied fixes or a message indicating no fixes applied.
        """
        for fix_type, fix_message in suggested_fixes.items():
            if fix_type.startswith("Ollama_") or fix_type.startswith("Mistral_"):
                # Example: Automatically apply simple fixes based on AI suggestions
                # This requires natural language processing to parse and apply fixes
                # For demonstration, we'll assume fix_message contains a simple replacement instruction
                # In reality, this would be more complex and require sophisticated parsing
                self.logger.info(f"Applying fix from {fix_type}: {fix_message}")
                # Placeholder for fix application logic
                # e.g., code = code.replace("error_pattern", "fixed_pattern")
        self.logger.info("Applied suggested fixes to the code.")
        return code

# -------------------------------------------------------------------
# Value-Adding Improvements
# -------------------------------------------------------------------
# 1. **Automated Fixes**: Implement AI-driven or rule-based methods to 
#    automatically correct minor syntax or runtime issues, streamlining 
#    debugging by making preliminary adjustments before alerting the user.
#
# 2. **Enhanced Error Reporting**: Add functionality to generate and export 
#    error logs and reports in user-friendly formats (e.g., JSON or HTML) 
#    for in-depth analysis and tracking over time.
#
# 3. **Learning-Based Debugging**: Integrate a learning mechanism where 
#    the agent remembers frequent errors and past fixes, enhancing its 
#    suggestion quality for recurring issues.
#
# 4. **Multi-Model Integration**: Support multiple AI models (e.g., Ollama, 
#    Mistral) to provide diverse perspectives on fix suggestions.
#
# 5. **Interactive Debugging Interface**: Develop an interactive interface 
#    (CLI or GUI) where users can review and apply suggested fixes selectively.
#
# 6. **Security Enhancements**: Further restrict the execution environment to 
#    prevent malicious code execution beyond what is already implemented.
#
# 7. **Asynchronous Processing**: Ensure that the agent can handle multiple 
#    debugging tasks concurrently without blocking, improving responsiveness.
#
# 8. **Comprehensive Logging**: Implement detailed logging for each step, 
#    including timestamps, actions taken, and any issues encountered.
#
# 9. **Unit and Integration Tests**: Develop comprehensive tests to ensure 
#    each component functions as expected, facilitating maintenance and scalability.
#
# 10. **Caching AI Responses**: Implement caching for AI-generated fixes to optimize performance.
#
# 11. **Rate Limiting and Retries**: Implement rate limiting and retry mechanisms for AI calls to handle rate limits and transient failures.
#
# 12. **Configuration Validation**: Add validation for configuration files to ensure required fields are present and correctly formatted.
#
# 13. **Error Categorization**: Enhance error categorization to handle more specific error types and provide more tailored fix suggestions.
#
# 14. **Extensible Fix Application**: Develop a more robust mechanism to apply fixes, potentially integrating with code transformation libraries.
#
# 15. **Documentation**: Improve inline documentation and provide comprehensive external documentation for users and developers.
# -------------------------------------------------------------------
