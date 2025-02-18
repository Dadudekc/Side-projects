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

class GPTForecaster:
    """
    📊 Uses GPT models to generate AI-driven market forecasts.
    """

    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def generate_forecast(self, context: str) -> str:
        """Generates insights based on financial or trading context."""
        prompt = f"Analyze this data and provide a forecast: {context}"
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "system", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"]
