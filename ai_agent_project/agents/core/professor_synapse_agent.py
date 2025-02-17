import json
import os
import requests
import logging
from ai_engine.models.apis.api_client import APIClient  # Handles real-time lookups
from ai_engine.reasoning_engine.reasoning_engine import ReasoningEngine  # Manages dynamic reasoning
from agents.core.agent_registry import AgentRegistry  # Enables agent collaboration
from bs4 import BeautifulSoup  # Web scraping for Yahoo Finance & Google News
from agents.core.memory_engine import MemoryEngine
from agents.core.gpt_forecasting import GPTForecaster
from agents.core.graph_memory import GraphMemory

class ProfessorSynapseAgent:
    """
    🧙🏾‍♂️ Professor Synapse - A reasoning AI that evolves through learning,
    forecasting, and knowledge-based reasoning.
    """

    def __init__(self):
        self.name = "Professor Synapse"
        self.memory_engine = MemoryEngine()
        self.forecaster = GPTForecaster()
        self.knowledge_graph = GraphMemory()
        self.api_client = APIClient()

    def respond(self, user_input: str) -> str:
        """Handles real-time reasoning, forecasting, and memory-based learning."""
        # Step 1: Check memory for past interactions
        past_response = self.memory_engine.retrieve_similar_query(user_input)
        if past_response:
            return f"🧙🏾‍♂️ (Memory Recall) {past_response}"

        # Step 2: Fetch real-time data
        real_time_data = self.api_client.fetch_data(user_input)
        if real_time_data:
            self.memory_engine.store_interaction(user_input, real_time_data)
            return f"🧙🏾‍♂️ (Live Data) {real_time_data}"

        # Step 3: Use AI forecasting for insights
        forecast = self.forecaster.generate_forecast(user_input)
        self.memory_engine.store_interaction(user_input, forecast)
        return f"🧙🏾‍♂️ (AI Forecast) {forecast}"

    def learn_knowledge(self, subject: str, relation: str, obj: str):
        """Teaches Professor Synapse a new piece of knowledge."""
        self.knowledge_graph.add_knowledge(subject, relation, obj)

class ProfessorSynapseAgent:
    """
    🧙🏾‍♂️ Professor Synapse - A reasoning AI agent that dynamically updates its reasoning schema,
    fetches real-time data, and collaborates with other agents to achieve user goals effectively.
    """

    def __init__(self):
        self.name = "Professor Synapse"
        self.reasoning_schema = self.load_reasoning_schema()
        self.api_client = APIClient()
        self.registry = AgentRegistry()
        self.logger = logging.getLogger(self.name)

    def load_reasoning_schema(self) -> dict:
        """Loads or initializes the reasoning schema."""
        schema_path = "schemas/reasoning_schema.json"
        if os.path.exists(schema_path):
            with open(schema_path, "r") as f:
                return json.load(f)
        else:
            return {
                "Reasoning": {
                    "wm": {"g": "Unknown", "sg": "Unknown", "pr": {"completed": [], "current": []}, "ctx": "N/A"},
                    "kg": {"tri": []},
                    "logic": {"propositions": [], "proofs": [], "critiques": [], "doubts": []},
                    "chain": {"steps": [], "reflect": "", "err": [], "note": [], "warn": []},
                    "exp": [],
                    "se": []
                }
            }

    def update_reasoning(self, key: str, value):
        """Dynamically updates reasoning schema."""
        self.reasoning_schema["Reasoning"][key] = value
        self.logger.info(f"Updated reasoning schema: {key} → {value}")

    def fetch_data(self, query: str) -> str:
        """Fetches real-time data based on query type (market data, news, etc.)."""
        if "stock price" in query:
            symbol = query.split()[-1]
            return self.api_client.fetch_stock_price(symbol) or self.api_client.fetch_stock_from_alpaca(symbol)

        if "crypto price" in query:
            symbol = query.split()[-1]
            return self.api_client.fetch_crypto_price(symbol)

        if "forex rate" in query:
            currency = query.split()[-1]
            return self.api_client.fetch_forex_rate(currency)

        if "news" in query:
            topic = query.split()[-1]
            return self.api_client.fetch_news(topic) or self.api_client.fetch_news_from_finnhub(topic)

        return "No relevant data found."

    def collaborate_with_agents(self, task: str, data: dict) -> str:
        """Engages other agents to solve complex tasks."""
        best_agent = self.registry.find_best_agent(task)
        if best_agent:
            response = best_agent.execute_task(data)
            return f"🤝 Collaboration: {best_agent.name} handled this task → {response}"
        return "No suitable agent found for collaboration."

    def respond(self, user_input: str) -> str:
        """Generates a response by processing the query through reasoning, logic, and real-time data."""
        self.update_reasoning("wm", {"g": "Answer Query", "sg": user_input, "pr": {"completed": [], "current": ["Processing"]}, "ctx": "User Inquiry"})

        real_time_data = self.fetch_data(user_input)
        if real_time_data:
            return f"🧙🏾‍♂️ Professor Synapse: {real_time_data}"

        reasoning_response = ReasoningEngine.analyze_query(user_input, self.reasoning_schema)
        return f"🧙🏾‍♂️ Professor Synapse: {reasoning_response}"

