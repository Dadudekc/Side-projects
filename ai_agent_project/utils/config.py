# utils/config.py

import json
import os

def load_config(config_path="config.json"):
    """
    Loads configuration settings from a JSON file. 
    If the file does not exist, it returns a default configuration.
    """
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)
    else:
        # Default configuration
        config = {
            "ai_models": {
                "local": {
                    "mistral": {"enabled": True, "model_path": "models/mistral_model.py"},
                    "deepseek": {"enabled": True, "model_path": "models/deepseek_model.py"}
                },
                "openai": {"enabled": True, "api_key": "YOUR_OPENAI_API_KEY"}
            },
            "test_runner": {"timeout": 30},
            "logging": {"level": "INFO"}
        }
    return config
