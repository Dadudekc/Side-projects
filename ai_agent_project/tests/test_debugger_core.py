"""

This code includes a set of unit tests for the DebugAgent class in the ai_engine.models.debugger.debugger_core module.

Functions:

- test_analyze_error: Tests that the analyze_error method correctly includes the provided error and detail in its return.
- test_run_diagnostics: Tests that the run_diagnostics method includes the expected outputs.
- test_describe_capabilities: Tests that the describe_capabilities method includes "can run tests" in its capabilities.
- test_learning_db: Tests that the _
"""

import os
import tempfile
import json
import pytest
from ai_engine.models.debugger.debugger_core import DebugAgent

def test_analyze_error():
    agent = DebugAgent()
    result = agent.analyze_error("TestError", context={"detail": "unit test"})
    assert "TestError" in result
    assert "unit test" in result

def test_run_diagnostics():
    agent = DebugAgent()
    result = agent.run_diagnostics(system_check=True, detailed=True)
    assert "Basic diagnostics" in result
    assert "System check passed" in result

def test_describe_capabilities():
    agent = DebugAgent()
    capabilities = agent.describe_capabilities()
    assert "can run tests" in capabilities

def test_learning_db(tmp_path):
    # Create a temporary learning DB file
    temp_db = tmp_path / "learning_db.json"
    agent = DebugAgent()
    # Override the learning DB path to use the temp file
    agent.LEARNING_DB_PATH = str(temp_db)
    agent.learning_db = {}
    # Store a fix in the DB
    agent._store_learned_fix("SampleError", "SampleFix")
    
    # Create a new instance to load from the temporary DB file
    new_agent = DebugAgent()
    new_agent.LEARNING_DB_PATH = str(temp_db)
    loaded_db = new_agent._load_learning_db()
    assert "SampleError" in loaded_db
    assert loaded_db["SampleError"] == "SampleFix"
