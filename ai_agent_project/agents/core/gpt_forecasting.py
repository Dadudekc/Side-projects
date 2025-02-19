"""

A Python class that uses OpenAI's GPT models to generate AI-driven market forecasts.

This class requires an OpenAI API key, which can be set as an environment variable("OPENAI_API_KEY").

Attributes:
    None

Methods:
    generate_forecast(context: str) -> str: 
        Takes a string argument 'context' that represents financial or trading context. 
        This method generates a forecast based on the given context using OpenAI's GPT model and 
        returns the
"""

import openai
import os
from agents.core.AgentBase import AgentBase

class GPTForecaster(AgentBase):
    def __init__(self):
        super().__init__(name="GPTForecaster", project_name="ForecastingAgent")

    def solve_task(self, task, **kwargs):
        return {"status": "success", "forecast": "Predicted value"}

    def describe_capabilities(self) -> str:
        return "Provides AI-powered market forecasting."


    def generate_forecast(self, context: str) -> str:
        """Generates insights based on financial or trading context."""
        prompt = f"Analyze this data and provide a forecast: {context}"
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "system", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"]
