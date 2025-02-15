import unittest
from unittest.mock import patch, MagicMock
from agents.AgentDispatcher import AgentDispatcher
from agents.AgentRegistry import AgentRegistry
from agents.core.AgentBase import AgentBase,
from agents.core.utilities.AIModelManager import AIModelManager
from agents.core.utilities.AIPatchUtils import AIPatchUtils
, CustomAgent, DeepSeekModel, MistralModel, OpenAIModel

class TestAgentDispatcher(unittest.TestCase):
    
    @patch("agents.AgentRegistry.AgentRegistry.list_agents", return_value=["TestAgent"])
    def test_initialization_with_agents(self, mock_list_agents):
        dispatcher = AgentDispatcher()
        self.assertEqual(dispatcher.agents, ["TestAgent"])
    
    @patch("agents.AgentRegistry.AgentRegistry.list_agents", return_value=[])
    @patch("logging.warning")
    def test_initialization_without_agents(self, mock_warning, mock_list_agents):
        dispatcher = AgentDispatcher()
        mock_warning.assert_called_with("No agents were loaded into the registry!")
    
    @patch("agents.AgentRegistry.AgentRegistry.get_agent")
    def test_dispatch_task_with_valid_agent(self, mock_get_agent):
        mock_agent = MagicMock(spec=AgentBase)
        mock_agent.solve_task.return_value = {"result": "success"}
        mock_get_agent.return_value = mock_agent
        
        dispatcher = AgentDispatcher()
        task_data = {"action": "test_action"}
        result = dispatcher.dispatch_task("TestAgent", task_data)
        self.assertEqual(result, '{"result": "success"}')''
    
    @patch("agents.AgentRegistry.AgentRegistry.get_agent", return_value=None)
    @patch("logging.error")
    def test_dispatch_task_with_invalid_agent(self, mock_error, mock_get_agent):
        dispatcher = AgentDispatcher()
        task_data = {"action": "test_action"}
        result = dispatcher.dispatch_task("InvalidAgent", task_data)
        
        mock_error.assert_called_with("Agent 'InvalidAgent' not found in registry.")''        self.assertEqual(result, '{"error": "Agent \'InvalidAgent\' not found."}')''    
    @patch("agents.AgentRegistry.AgentRegistry.get_agent")
    @patch("logging.error")
    def test_dispatch_task_with_non_agentbase_instance(self, mock_error, mock_get_agent):
        mock_get_agent.return_value = "NotAnAgentBaseInstance"
        
        dispatcher = AgentDispatcher()
        task_data = {"action": "test_action"}
        result = dispatcher.dispatch_task("TestAgent", task_data)
        
        mock_error.assert_called_with("Agent 'TestAgent' does not inherit from AgentBase.")''        self.assertEqual(result, '{"error": "Agent \'TestAgent\' is invalid."}')''
    
    @patch("agents.AgentRegistry.AgentRegistry.get_agent")
    @patch("logging.error")
    def test_dispatch_task_with_exception(self, mock_error, mock_get_agent):
        mock_agent = MagicMock(spec=AgentBase)
        mock_agent.solve_task.side_effect = Exception("Task error")
        mock_get_agent.return_value = mock_agent
        
        dispatcher = AgentDispatcher()
        task_data = {"action": "test_action"}
        result = dispatcher.dispatch_task("TestAgent", task_data)
        
        mock_error.assert_called_with("Error executing task for 'TestAgent': Task error")''        self.assertEqual(result, '{"error": "Task execution failed: Task error"}')''
if __name__ == "__main__":
    unittest.main()
