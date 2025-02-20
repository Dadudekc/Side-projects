# Path: ai_agent_project/src/tests/test_agent_dispatcher.py

import pytest
import asyncio
from core.agent_dispatcher import AgentDispatcher
from agents.plugins.example_plugin import ExampleAgent

@pytest.fixture
def dispatcher():
    return AgentDispatcher(agents_directory="agents/plugins")

@pytest.mark.asyncio
async def test_load_agents(dispatcher):
    agents = dispatcher.agents
    assert "exampleagent" in agents
    assert isinstance(agents["exampleagent"], ExampleAgent)

@pytest.mark.asyncio
async def test_dispatch_task(dispatcher):
    result = await dispatcher.dispatch_task(task="echo Hello", agent_name="exampleagent", priority=1)
    assert result is None  # Task is enqueued

    # Execute tasks
    await dispatcher.execute_tasks()

    # Since ExampleAgent returns a string, verify the result
    agent = dispatcher.agents["exampleagent"]
    assert hasattr(agent, 'solve_task')

@pytest.mark.asyncio
async def test_execute_standard_task(dispatcher):
    task = "echo Test"
    agent_name = "exampleagent"
    result = await dispatcher._execute_standard_task(priority=1, task=task, agent_name=agent_name, kwargs={})
    assert isinstance(result, str)
    assert "executed task" in result

def test_list_agents(dispatcher):
    agents = dispatcher.list_agents()
    assert isinstance(agents, list)
    assert "exampleagent" in agents
# Path: ai_agent_project/src/agents/core/tests/test_agent_dispatcher.py

import pytest
import asyncio
from agent_dispatcher import AgentDispatcher

@pytest.mark.asyncio
async def test_dispatch_nonexistent_agent():
    dispatcher = AgentDispatcher(agents_directory="nonexistent_dir")
    result = await dispatcher.dispatch_task(
        task="Test Task", agent_name="nonexistent_agent"
    )
    assert result == "Error: Specified agent does not exist."

# Add more test cases as needed
