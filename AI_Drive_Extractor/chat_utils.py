import os
from typing import List, Dict

import openai


def chat_completion(messages: List[Dict[str, str]], model: str = "gpt-4") -> str:
    """Send messages to OpenAI ChatCompletion and return response text."""
    openai.api_key = os.getenv("OPENAI_API_KEY", "")
    response = openai.ChatCompletion.create(model=model, messages=messages)
    return response["choices"][0]["message"]["content"].strip()
