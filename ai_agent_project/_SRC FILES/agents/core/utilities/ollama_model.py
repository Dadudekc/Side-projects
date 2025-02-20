# Path: ai_agent_project/src/agents/core/utilities/ollama_model.py

import subprocess
import asyncio
import logging
from .ai_model import AIModel



class OllamaModel(AIModel):
    """
    AI model integration for Ollama.
    """

    def __init__(self, command: str):
        self.command = command
        self.logger = logging.getLogger(self.__class__.__name__)

    async def generate_fix(self, error_type: str, error_message: str) -> str:
        prompt = f"Provide a fix suggestion for the following error:\nError Type: {error_type}\nError Message: {error_message}\nFix:"
        try:
            process = await asyncio.create_subprocess_exec(
                *self.command.split(),
                prompt,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                fix = stdout.decode().strip()
                self.logger.info(f"Ollama-generated fix for {error_type}: {fix}")
                return fix
            else:
                self.logger.error(f"Ollama failed: {stderr.decode().strip()}")
                return ""
        except FileNotFoundError:
            self.logger.error("Ollama is not installed or not accessible in the PATH.")
            return ""
        except Exception as e:
            self.logger.error(f"Error using Ollama for {error_type}: {str(e)}")
            return ""
