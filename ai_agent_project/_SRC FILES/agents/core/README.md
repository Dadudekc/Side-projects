# Utilities Module Documentation

The `utilities` module provides essential classes and functions that support various aspects of the AI agent project, including memory management, model interaction, reasoning, performance monitoring, and error detection.

## Contents

### agent_base.py
Defines the `AgentBase` class, a foundational class for building agent functionality. This base class can be extended by specific agents like `DebuggerAgent` and `JournalAgent`.

### ai_cache.py
Implements caching mechanisms to optimize memory usage and reduce redundant computations. This utility is critical for efficient agent operations where repetitive tasks are common.

### ai_model.py
Provides the `AIModel` class, an abstract interface for interacting with AI models. Subclasses such as `MistralModel` and `OllamaModel` extend this for specific model integrations.

### ai_agent_utils.py
Contains general-purpose utility functions for configuration loading, performance tracking, and memory management. Key functions include:
- `track_performance()`: Tracks performance of function executions.
- `load_config()`: Loads and validates configuration files.
- `log_memory_usage()`: Logs memory usage for monitoring resource consumption.

### ChainOfThoughtReasoner.py
Handles advanced reasoning processes, leveraging Chain-of-Thought (CoT) methodology for tasks requiring complex reasoning and step-by-step solutions.

### error_detection.py
Contains functions and classes to detect and handle errors within agent processes, enhancing stability and providing insights for debugging.

### memory_manager.py
Manages memory operations and data persistence across sessions, leveraging an SQLite database (`ai_agent_memory.db`) for storing and retrieving memory states.

### mistral_model.py
Integrates with the Mistral AI model for advanced text generation, providing the `MistralModel` class to handle model-specific interactions and responses.

### ollama_model.py
Integrates with the Ollama AI model, similar to `MistralModel`, providing model-specific functionalities through the `OllamaModel` class.

### performance_monitor.py
Tracks and records the performance of various agents and tasks, helping to identify bottlenecks and optimize resource usage.

## Example Usage

```python
from utilities import MemoryManager, ChainOfThoughtReasoner, track_performance

# Initialize memory manager
memory_manager = MemoryManager()

# Load Chain of Thought Reasoner
cot_reasoner = ChainOfThoughtReasoner(agent_dispatcher=dispatcher)

# Use track_performance to log function execution times
@track_performance
def example_task():
    # Your task code here
    pass
