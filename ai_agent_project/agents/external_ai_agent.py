import json
import requests
from agents.core.AgentBase import AgentBase

class ExternalAIAdapter(AgentBase):
    """
    Adapter for a third-party AI model.
    
    Wraps API calls to the external AI model and conforms to the AgentBase interface.
    """

    def __init__(self, api_key: str, endpoint: str):
        self.api_key = api_key
        self.endpoint = endpoint

    def solve_task(self, action: str, **kwargs) -> dict:
        payload = {
            "action": action,
            "parameters": kwargs
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            response = requests.post(self.endpoint, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            return {"status": "success", "result": result.get("result")}
        except Exception as e:
            return {"error": f"External AI model call failed: {str(e)}"}
