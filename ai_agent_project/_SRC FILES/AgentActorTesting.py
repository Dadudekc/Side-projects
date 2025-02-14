# --- Step 1: Implement FakeToolServer for Accurate Testing ---

import random

class FakeToolServer:
    """
    Simulated ToolServer that behaves like the real implementation.
    - Throws proper exceptions for missing tools/methods.
    - Returns predefined results for valid operations.
    """
    def __init__(self):
        self.python_notebook = FakePythonNotebook()
        self.shell = FakeShellTool()
        self.content_automation = FakeContentAutomation()
    
    def __getattr__(self, item):
        """Simulate missing tools by raising an AttributeError."""
        raise AttributeError(f"Tool '{item}' not found in ToolServer.")

class FakePythonNotebook:
    """Simulated Python Notebook execution tool."""
    def execute_code(self, code):
        if not isinstance(code, str):
            raise ValueError("Code must be a string.")
        return f"Executed: {code}"

class FakeShellTool:
    """Simulated Shell execution tool."""
    def execute_command(self, command):
        if not isinstance(command, str):
            raise ValueError("Command must be a string.")
        if command == "invalid_command":
            raise RuntimeError("Shell command failed.")
        return f"Shell executed: {command}"

class FakeContentAutomation:
    """Simulated Content Automation tool with AI-powered content generation."""
    def generate_content(self, topic):
        generated_variations = [
            f"A deep dive into {topic} and its impact.",
            f"How {topic} is changing the world today.",
            f"Expert insights on {topic} and future trends."
        ]
        return f"Generated content for: {random.choice(generated_variations)}"

        
    def schedule_content(self, content, time):
        return f"Scheduled content '{content}' for {time}"
    
    def post_content(self, content):
        return f"Posted content: {content}"

# --- Step 2: Enhance AgentActor Exception Handling (Option 3) ---

class AgentActor:
    """
    Executes tasks and manages tool operations via ToolServer.
    """
    def __init__(self, tool_server, memory_manager, performance_monitor):
        self.tool_server = tool_server
        self.memory_manager = memory_manager
        self.performance_monitor = performance_monitor

    def solve_task(self, task: str) -> str:
        """Executes a given task as Python code, a shell command, or a content automation task."""
        try:
            if task.startswith("python:"):
                python_code = task[len("python:"):].strip()
                return self.tool_server.python_notebook.execute_code(python_code)
            elif task.startswith("content:"):
                return self._execute_content_task(task[len("content:"):].strip())
            else:
                return self._execute_shell_task(task)
        except Exception as e:
            return f"Task execution failed: {str(e)}"

    def _execute_shell_task(self, command: str) -> str:
        """Executes a shell command safely and handles errors."""
        try:
            return self.tool_server.shell.execute_command(command)
        except Exception as e:
            return f"Shell task execution failed: {str(e)}"
    
    def _execute_content_task(self, task: str) -> str:
        """Handles content automation commands."""
        parts = task.split(" ", 1)
        command = parts[0]
        argument = parts[1] if len(parts) > 1 else ""
        
        if command == "generate":
            return self.tool_server.content_automation.generate_content(argument)
        elif command == "schedule":
            content, time = argument.rsplit(" ", 1)
            return self.tool_server.content_automation.schedule_content(content, time)
        elif command == "post":
            return self.tool_server.content_automation.post_content(argument)
        else:
            return "Invalid content automation command."

    def utilize_tool(self, tool_name: str, operation: str, parameters: dict):
        """Executes an operation on a specified tool within ToolServer."""
        try:
            tool = getattr(self.tool_server, tool_name, None)
            if tool is None:
                return f"Tool '{tool_name}' not found in ToolServer."

            tool_method = getattr(tool, operation, None)
            if tool_method is None:
                return f"Operation '{operation}' not found in tool '{tool_name}'."

            return tool_method(**parameters)

        except Exception as e:
            return f"Failed to execute operation '{operation}' on tool '{tool_name}': {str(e)}"

# --- Step 3: Modify Tests to Use FakeToolServer Instead of MagicMock ---

import unittest

class TestAgentActor(unittest.TestCase):
    def setUp(self):
        self.fake_tool_server = FakeToolServer()
        self.agent_actor = AgentActor(self.fake_tool_server, None, None)

    def test_solve_task_python(self):
        """Test executing a Python task."""
        result = self.agent_actor.solve_task("python: print('Hello, World!')")
        self.assertEqual(result, "Executed: print('Hello, World!')")

    def test_solve_task_shell(self):
        """Test executing a shell command."""
        result = self.agent_actor.solve_task("ls -la")
        self.assertEqual(result, "Shell executed: ls -la")

    def test_solve_task_invalid(self):
        """Test handling of an invalid shell command."""
        result = self.agent_actor.solve_task("invalid_command")
        self.assertIn("Shell task execution failed:", result)

    def test_solve_task_content_generate(self):
        """Test generating content."""
        topic = "blog_post"
        result = self.agent_actor.solve_task(f"content: generate {topic}")
        self.assertIn(topic, result)  # Ensures the topic is included in the AI-generated response


    def test_solve_task_content_post(self):
        """Test posting content."""
        result = self.agent_actor.solve_task("content: post Hello, this is a test post!")
        self.assertEqual(result, "Posted content: Hello, this is a test post!")

# --- Step 4: Run the Final Test Suite ---
final_test_results = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(TestAgentActor))
print(final_test_results)
