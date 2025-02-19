"""
This module defines the ProfessorSynapseAgent class which is an extension of the AgentBase class defined in Core. 

This AI Agent, Professor Synapse, evolves through learning, forecasting, and knowledge-based reasoning. 

Notably, the Professor Synapse Agent can perform various tasks related to reasoning, forecasting, and collaboration.

Functions:
    - describe_capabilities() -> str: Returns a description of the agent's responsibilities.
    - respond(user_input: str) -> str: Processes the query and generates a response based on reasoning and real-time data.
"""
import json
import os
import requests
import logging
from bs4 import BeautifulSoup  # Web scraping

from ai_engine.models.apis.api_client import APIClient  # Handles real-time lookups
from ai_engine.reasoning_engine.reasoning_engine import ReasoningEngine  # Dynamic reasoning
from agents.core.memory_engine import MemoryEngine
from agents.core.gpt_forecasting import GPTForecaster
from agents.core.graph_memory import GraphMemory
from agents.core.AgentBase import AgentBase  # Base class


class ProfessorSynapseAgent(AgentBase):
    """
    🧙🏾‍♂️ Professor Synapse - A reasoning AI that evolves through learning, forecasting,
    and knowledge-based reasoning.

    Inherits from AgentBase and extends its functionality with:
      - Memory management via MemoryEngine.
      - Forecasting capabilities using GPTForecaster.
      - A knowledge graph maintained with GraphMemory.
      - Real-time data retrieval through APIClient.
    """

    def __init__(self):
        super().__init__(name="ProfessorSynapseAgent", project_name="AI_Reasoning_Agent")
        self.memory_engine = MemoryEngine()
        self.forecaster = GPTForecaster()
        self.knowledge_graph = GraphMemory()
        self.api_client = APIClient()

    def describe_capabilities(self) -> str:
        """
        Return a description of this agent's responsibilities.

        Returns:
            str: A description of the agent's capabilities.
        """
        return "Handles knowledge reasoning, forecasting, and real-time lookups."

    def respond(self, user_input: str) -> str:
        """
        Generates a response by processing the query through reasoning, logic, and real-time data.

        Args:
            user_input (str): The user's query.

        Returns:
            str: A formatted response from Professor Synapse.
        """
        # Construct a reasoning schema to guide the response generation
        reasoning_schema = {
            "Reasoning": {
                "wm": {"g": "Answer Query", "sg": user_input, "pr": {"completed": [], "current": ["Processing"]}, "ctx": "User Inquiry"},
                "kg": {"tri": []},
                "logic": {"propositions": [], "proofs": [], "critiques": [], "doubts": []},
                "chain": {"steps": [], "reflect": "", "err": [], "note": [], "warn": []},
                "exp": [],
                "se": []
            }
        }

        real_time_data = self.fetch_data(user_input)
        if real_time_data and real_time_data != "No relevant data found.":
            return f"🧙🏾‍♂️ Professor Synapse: {real_time_data}"

        # Use reasoning engine to analyze the query with the constructed schema
        reasoning_response = ReasoningEngine.analyze_query(user_input, reasoning_schema)
        return f"🧙🏾‍♂️ Professor Synapse: {reasoning_response}"

    def fetch_data(self, query: str) -> str:
        """
        Fetches real-time data based on the query type (market data, news, etc.).

        Args:
            query (str): The query string from the user.

        Returns:
            str: Retrieved data or a default message if no data is found.
        """
        # For stock prices
        if "stock price" in query:
            symbol = query.split()[-1]
            data = self.api_client.fetch_stock_price(symbol)
            if data:
                return data
            return self.api_client.fetch_stock_from_alpaca(symbol)

        # For cryptocurrency prices
        if "crypto price" in query:
            symbol = query.split()[-1]
            return self.api_client.fetch_crypto_price(symbol)

        # For forex rates
        if "forex rate" in query:
            currency = query.split()[-1]
            return self.api_client.fetch_forex_rate(currency)

        # For news-related queries
        if "news" in query:
            topic = query.split()[-1]
            data = self.api_client.fetch_news(topic)
            if data:
                return data
            return self.api_client.fetch_news_from_finnhub(topic)

        return "No relevant data found."

    def learn_knowledge(self, subject: str, relation: str, obj: str):
        """
        Teaches Professor Synapse a new piece of knowledge by updating the knowledge graph.

        Args:
            subject (str): The subject of the knowledge.
            relation (str): The relationship type.
            obj (str): The object or related entity.
        """
        self.knowledge_graph.add_knowledge(subject, relation, obj)

    def collaborate_with_agents(self, task: str, data: dict) -> str:
        """
        Engages other agents to solve complex tasks via collaboration.

        Args:
            task (str): The task to be delegated.
            data (dict): Additional task parameters.

        Returns:
            str: The outcome of the collaboration or an error message if no suitable agent is found.
        """
        best_agent = AgentRegistry().find_best_agent(task)
        if best_agent:
            response = best_agent.execute_task(data)
            return f"🤝 Collaboration: {best_agent.name} handled this task → {response}"
        return "No suitable agent found for collaboration."

    def solve_task(self, task: str, **kwargs) -> dict:
        """
        Handles various tasks related to reasoning, forecasting, and collaboration.
        Returns a structured dictionary response for clarity in testing.

        Args:
            task (str): Action to be performed.
            **kwargs: Additional parameters.

        Returns:
            dict: The result of the operation.
        """
        if task == "reason":
            return {"status": "success", "response": self.respond(kwargs.get("query", ""))}
        elif task == "fetch_data":
            return {"status": "success", "data": self.fetch_data(kwargs.get("query", ""))}
        elif task == "collaborate":
            return {"status": "success", "response": self.collaborate_with_agents(kwargs.get("task", ""), kwargs)}
        else:
            return {"status": "error", "message": f"Invalid task '{task}'"}

    def shutdown(self) -> None:
        """
        Logs a shutdown message and performs any necessary cleanup.
        """
        logging.info("ProfessorSynapseAgent is shutting down.")
