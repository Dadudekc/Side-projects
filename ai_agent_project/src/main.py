import logging
import asyncio
from ai_agent_utils import PerformanceMonitor, MemoryManager, ToolServer, Shell, PythonNotebook
from agent_actor import AgentActor
from AgentDispatcher import AgentDispatcher

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Starting the AI Agent System...")

    try:
        # Initialize PerformanceMonitor and MemoryManager
        performance_monitor = PerformanceMonitor()
        memory_manager = MemoryManager()

        # Initialize ToolServer with Shell and PythonNotebook tools
        tool_server = ToolServer(shell=Shell(), python_notebook=PythonNotebook())
        logger.debug("ToolServer initialized with Shell and PythonNotebook tools.")

        # Initialize AgentActor with ToolServer, MemoryManager, and PerformanceMonitor
        agent_actor = AgentActor(
            tool_server=tool_server,
            memory_manager=memory_manager,
            performance_monitor=performance_monitor
        )
        logger.debug(f"Initialized AgentActor with ToolServer={tool_server}, MemoryManager={memory_manager}, PerformanceMonitor={performance_monitor}")

        # Initialize AgentDispatcher and add the AgentActor agent
        dispatcher = AgentDispatcher(agents_directory="path_to_agents_directory")  # Adjust path as needed
        dispatcher.add_agent('actor', agent_actor)

        # Dispatch and await results for different types of tasks

        # Dispatch a shell task to the 'actor' agent
        shell_task = "echo Hello, Jarvis!"
        shell_result = await dispatcher.dispatch_task(shell_task, 'actor', priority=1)
        print(f"Result of shell task '{shell_task}': {shell_result}")

        # Dispatch a Python code task to the 'actor' agent
        python_task = "python: print('Hello from Python code!')"
        python_result = await dispatcher.dispatch_task(python_task, 'actor', priority=2)
        print(f"Result of Python task '{python_task}': {python_result}")

        # Dispatch a trading functionality task to the 'actor' agent
        trading_task = """
from trading_robot import TradingRobot  # Adjust import based on your module structure
robot = TradingRobot()
robot.load_data('path_to_data.csv')  # Replace with actual data path
analysis_result = robot.run_analysis()
print('Trading Analysis Result:', analysis_result)
"""
        trading_result = await dispatcher.dispatch_task(f"python: {trading_task}", 'actor', priority=3)
        print(f"Result of trading task: {trading_result}")

        # Start executing tasks if the dispatcher has a queue-processing loop
        await dispatcher.execute_tasks()

    except Exception as e:
        logger.error(f"An error occurred in the main process: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
