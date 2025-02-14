import logging
import asyncio
from typing import List, Optional, Dict, Any
import subprocess
import networkx as nx
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class ChainOfThoughtReasoner:
    """
    Implements advanced chain-of-thought reasoning by decomposing tasks into semantic steps,
    supporting hierarchical reasoning, contextual memory, and dynamic step adjustment.
    """

    def __init__(self, agent_dispatcher, model_name: str = 'mistral:latest',
                 ollama_url: str = "http://localhost:11434"):
        """
        Initializes the ChainOfThoughtReasoner with an agent dispatcher and a semantic model.

        Args:
            agent_dispatcher: An instance responsible for dispatching tasks to agents.
            model_name (str): The name of the Mistral model configured in Ollama.
            ollama_url (str): The URL for the Ollama model API.
        """
        self.agent_dispatcher = agent_dispatcher
        self.memory: Dict[str, Any] = {}  # Contextual memory
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.reasoning_graph = nx.DiGraph()  # To manage hierarchical steps
        self.lock = asyncio.Lock()

        logger.info("ChainOfThoughtReasoner initialized.")

    async def solve_task_with_reasoning(self, task: str, agent_name: str) -> str:
        """
        Decomposes the task into semantic steps, executes each step (possibly in parallel),
        and manages hierarchical reasoning and memory.

        Args:
            task (str): The main task to solve with chain-of-thought reasoning.
            agent_name (str): The name of the agent to handle each reasoning step.

        Returns:
            str: The final result after completing all reasoning steps or an error message.
        """
        try:
            steps = await self.decompose_task(task)
            if not steps:
                error_message = "Failed to decompose the task into steps."
                logger.error(error_message)
                return error_message

            # Build reasoning graph
            self.build_reasoning_graph(steps)

            # Execute steps with respect to dependencies
            await self.execute_steps(agent_name)

            # Retrieve the final result
            final_step_id = f"step_{len(steps)}"
            final_result = self.memory.get(final_step_id, "No result produced.")

            logger.info("All steps completed successfully.")
            return final_result

        except Exception as e:
            logger.exception(
                f"An unexpected error occurred while solving the task: {e}")
            return f"An unexpected error occurred: {str(e)}"

    async def execute_steps(self, agent_name: str):
        """
        Executes the reasoning steps while respecting dependencies.

        Args:
            agent_name (str): The agent responsible for executing the steps.
        """
        tasks = {}
        step_events = {step_id: asyncio.Event()
                       for step_id in self.reasoning_graph.nodes()}

        async def execute_step_wrapper(step_id: str):
            dependencies = list(self.reasoning_graph.predecessors(step_id))
            for dep_id in dependencies:
                await step_events[dep_id].wait()

            await self.execute_step(step_id, agent_name)
            step_events[step_id].set()

        for step_id in self.reasoning_graph.nodes():
            tasks[step_id] = asyncio.create_task(execute_step_wrapper(step_id))

        await asyncio.gather(*tasks.values())

    async def execute_step(self, step_id: str, agent_name: str) -> Any:
        """
        Executes a single reasoning step after ensuring all dependencies are met.

        Args:
            step_id (str): Identifier for the step.
            agent_name (str): The agent responsible for executing the step.

        Returns:
            Any: The result of the step execution.
        """
        try:
            step = self.reasoning_graph.nodes[step_id]['content']
            logger.info(f"Executing Step {step_id}: {step}")

            # Enrich step with memory
            enriched_step = self.enrich_step_with_memory(step)

            # Dispatch the task and get the result
            result = await self.agent_dispatcher.dispatch_task(
                enriched_step, agent_name, use_chain_of_thought=False
            )

            if result is None:
                raise Exception(f"Step {step_id} failed to execute.")

            # Update memory in a thread-safe way
            async with self.lock:
                self.update_memory(step_id, result)

            # Self-evaluate the result
            if not await self.self_evaluate(step, result):
                retry_result = await self.retry_step(step, agent_name)
                if retry_result is None:
                    raise Exception(
                        f"Retry failed at step {step_id}: '{step}'.")
                async with self.lock:
                    self.update_memory(step_id, retry_result)

            logger.debug(
                f"Completed Step {step_id}: {step} with result: {result}")
            return result

        except Exception as e:
            logger.exception(
                f"An error occurred while executing step {step_id}: {e}")
            raise

    async def decompose_task(self, task: str) -> List[str]:
        """
        Breaks down the main task into semantically meaningful steps.

        Args:
            task (str): The main task.

        Returns:
            List[str]: A list of decomposed steps.
        """
        try:
            prompt = (
                "Please decompose the following task into detailed, logical, and semantically meaningful steps. "
                "Provide the output in JSON format as an array of steps.\n\n"
                f"Task: {task}\n\nSteps:"
            )
            response = await self._call_ollama_cli(prompt)
            if response is None:
                logger.error("No response from the decomposition model.")
                return []

            steps = self.parse_decomposition_output(response)
            logger.debug(f"Task decomposed into steps: {steps}")
            return steps

        except Exception as e:
            logger.exception(f"Failed to decompose task: {e}")
            return []

    async def _call_ollama_cli(self, prompt: str) -> Optional[str]:
        """
        Calls the Ollama CLI with the given prompt.

        Args:
            prompt (str): The prompt to send to the model.

        Returns:
            Optional[str]: The model's response, or None if an error occurred.
        """
        try:
            logger.debug(f"Model name in use: {self.model_name}")
            logger.debug(f"Calling Ollama CLI with prompt: {prompt}")

            # Define the command for subprocess execution
            command = ["ollama", "run", self.model_name]
            
            # Run the command asynchronously with prompt as input
            process = await asyncio.create_subprocess_exec(
                *command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                text=False  # We will manually handle encoding
            )

            # Send the encoded prompt and receive output
            stdout, stderr = await process.communicate(input=prompt.encode("utf-8"))
            
            # Check for errors in stderr or non-zero return code
            if process.returncode != 0 or stderr:
                error_msg = stderr.decode("utf-8").strip() if stderr else "Unknown error"
                logger.error(f"Ollama CLI stderr: {error_msg}")
                return None

            # Decode and clean up the standard output
            content = stdout.decode("utf-8").strip()
            logger.debug(f"Received response from Ollama CLI: {content}")
            return content

        except subprocess.CalledProcessError as e:
            logger.error(f"Ollama CLI call failed with CalledProcessError: {e}")
            return None
        except Exception as ex:
            logger.exception(f"An unexpected error occurred while calling Ollama CLI: {str(ex)}")
            return None



    def parse_decomposition_output(self, text: str) -> List[str]:
        """
        Parses the output from the decomposition model into a list of steps.

        Args:
            text (str): The raw text output from the decomposition model.

        Returns:
            List[str]: A list of individual steps.
        """
        try:
            steps = json.loads(text)
            if not isinstance(steps, list):
                raise ValueError("Invalid format: Expected a list of steps.")
            return steps

        except json.JSONDecodeError:
            logger.warning(
                "Failed to parse JSON output. Falling back to line parsing.")
            lines = text.strip().split('\n')
            steps = []
            for line in lines:
                line = line.strip()
                if line:
                    step = line.lstrip('0123456789.)-• ').strip()
                    if step:
                        steps.append(step)
            return steps

        except Exception as e:
            logger.exception(f"Error parsing decomposition output: {e}")
            return []

    def build_reasoning_graph(self, steps: List[str]) -> None:
        """
        Builds a directed graph representing the dependencies between reasoning steps.

        Args:
            steps (List[str]): A list of steps to include in the reasoning graph.
        """
        self.reasoning_graph.clear()
        for idx, step in enumerate(steps, start=1):
            step_id = f"step_{idx}"
            self.reasoning_graph.add_node(step_id, content=step)
            if idx > 1:
                self.reasoning_graph.add_edge(
                    f"step_{idx - 1}", step_id)  # Ensures dependency
        logger.debug(
            f"Reasoning graph constructed with nodes: {list(self.reasoning_graph.nodes(data=True))}")

    def enrich_step_with_memory(self, step: str) -> str:
        """
        Enhances the step with contextual memory for more informed processing.

        Args:
            step (str): The original step content.

        Returns:
            str: The enriched step content.
        """
        if self.memory:
            memory_content = "\n".join(
                [f"{k}: {v}" for k, v in self.memory.items()])
            enriched_step = f"Contextual Memory:\n{memory_content}\n\nTask Step: {step}"
            return enriched_step
        else:
            return step

    def update_memory(self, step_id: str, result: str) -> None:
        """
        Updates the contextual memory with the result of a completed step.

        Args:
            step_id (str): The identifier of the completed step.
            result (str): The result produced by the step.
        """
        self.memory[step_id] = result
        logger.debug(f"Memory updated with {step_id}: {result}")

    async def self_evaluate(self, step: str, result: str) -> bool:
        """
        Evaluates the quality of the step's result.

        Args:
            step (str): The step content.
            result (str): The result produced by the step.

        Returns:
            bool: True if the result is satisfactory, False otherwise.
        """
        try:
            evaluation_prompt = (
                f"Evaluate the following result for the step:\n\n"
                f"Step: {step}\n"
                f"Result: {result}\n\n"
                "Is the result correct and complete? Answer 'yes' or 'no' and provide a brief explanation."
            )
            response = await self._call_ollama_cli(evaluation_prompt)
            if response is None:
                logger.error("No response from the evaluation model.")
                return False

            logger.debug(f"Self-evaluation response: {response}")
            is_valid = 'yes' in response.lower()
            return is_valid

        except Exception as e:
            logger.exception(f"Failed to self-evaluate: {e}")
            return False

    async def retry_step(self, step: str, agent_name: str) -> Optional[str]:
        """
        Retries a failed step with possible refinements.

        Args:
            step (str): The step content.
            agent_name (str): The name of the agent to handle the retry.

        Returns:
            Optional[str]: The result of the retried step, or None if it fails again.
        """
        try:
            retry_prompt = (
                "The previous attempt to complete the step failed. Please try again with more details.\n\n"
                f"Step: {step}"
            )
            logger.info(f"Retrying step: {step}")
            result = await self.agent_dispatcher.dispatch_task(
                retry_prompt, agent_name, use_chain_of_thought=False
            )
            return result

        except Exception as e:
            logger.exception(f"Failed to retry step: {e}")
            return None
