# Path: ai_agent_project/src/tests/test_api.py

import pytest
from fastapi.testclient import TestClient
from api.main import app
from agents.plugins.example_plugin import ExampleAgent
from core.agent_dispatcher import AgentDispatcher

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_agents():
    dispatcher = AgentDispatcher(agents_directory="agents/plugins")
    dispatcher.agents["exampleagent"] = ExampleAgent(name="exampleagent")
    return dispatcher

def test_submit_task():
    response = client.post(
        "/tasks/",
        json={
            "task": "python:print('Hello World')",
            "agent_name": "exampleagent",
            "priority": 1,
            "use_chain_of_thought": False
        },
        headers={"access_token": "default_api_key"}
    )
    assert response.status_code == 200
    assert response.json() == {"status": "Task enqueued successfully."}

def test_list_agents():
    response = client.get(
        "/agents/",
        headers={"access_token": "default_api_key"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "exampleagent" in data
    assert data["exampleagent"]["capabilities"] == "ExampleAgent can execute basic tasks and provide example responses."

def test_add_remove_agent():
    # Assuming there's a valid agent module at 'agents/plugins/new_agent.py'
    module_path = "agents/plugins/new_agent.py"
    response = client.post(
        "/agents/add/",
        params={"agent_name": "newagent", "module_path": module_path},
        headers={"access_token": "default_api_key"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Agent 'newagent' added successfully."

    # Remove the agent
    response = client.post(
        "/agents/remove/",
        params={"agent_name": "newagent"},
        headers={"access_token": "default_api_key"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Agent 'newagent' removed successfully."
