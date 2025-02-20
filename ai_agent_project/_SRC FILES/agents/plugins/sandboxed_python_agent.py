# Path: ai_agent_project/src/agents/plugins/sandboxed_python_agent.py

from .plugin_interface import AgentPlugin
import logging
import asyncio
import docker

logger = logging.getLogger(__name__)

class SandboxedPythonAgent(AgentPlugin):
    """
    Python agent that executes code within a Docker container for sandboxing.
    """

    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        self.client = docker.from_env()
        logger.info(f"SandboxedPythonAgent '{self.name}' initialized.")

    async def solve_task(self, task: str, **kwargs) -> str:
        """
        Executes Python code within a Docker container.

        Args:
            task (str): Task description prefixed with 'python:'.

        Returns:
            str: Result or error message.
        """
        python_code = task[len("python:"):].strip()
        logger.info(f"SandboxedPythonAgent '{self.name}' executing Python code.")

        try:
            # Create a Docker container with limited resources
            container = self.client.containers.run(
                image="python:3.9-slim",
                command=["python", "-c", python_code],
                detach=True,
                mem_limit="50m",
                network_disabled=True,
                stdout=True,
                stderr=True,
            )

            # Wait for the container to finish with a timeout
            try:
                result = container.wait(timeout=5)
                logs = container.logs().decode()
                container.remove()
                logger.info(f"SandboxedPythonAgent '{self.name}' execution result: {logs}")
                return logs
            except docker.errors.APIError as e:
                container.remove(force=True)
                error_msg = f"Execution failed: {str(e)}"
                logger.error(error_msg)
                return error_msg
            except docker.errors.ContainerError as e:
                container.remove(force=True)
                error_msg = f"Container error: {str(e)}"
                logger.error(error_msg)
                return error_msg
            except Exception as e:
                container.remove(force=True)
                error_msg = f"Unexpected error: {str(e)}"
                logger.error(error_msg)
                return error_msg

        except Exception as e:
            error_msg = f"Failed to execute task in Docker: {str(e)}"
            logger.exception(error_msg)
            return error_msg

    def describe_capabilities(self) -> str:
        return "SandboxedPythonAgent executes Python code within Docker containers for secure execution."
