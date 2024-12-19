import json
import os
from typing import Dict, Any


def load_config() -> Dict[str, Any]:
    """Load configuration from config.json file"""
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "config.json"
    )

    if not os.path.exists(config_path):
        raise ValueError(
            "config.json not found. Please create one using config.json.example as a template."
        )

    with open(config_path, "r") as f:
        config = json.load(f)

    required_fields = ["refresh_token", "host", "port", "auth_tokens"]
    missing_fields = [field for field in required_fields if field not in config]

    if missing_fields:
        raise ValueError(
            f"Missing required fields in config.json: {', '.join(missing_fields)}"
        )

    if not isinstance(config["auth_tokens"], list):
        raise ValueError("auth_tokens must be an array in config.json")

    if not all(isinstance(token, str) for token in config["auth_tokens"]):
        raise ValueError("All auth_tokens must be strings in config.json")

    if len(config["auth_tokens"]) == 0:
        raise ValueError("auth_tokens array cannot be empty in config.json")

    return config
