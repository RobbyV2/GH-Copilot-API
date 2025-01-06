import json
import os
from typing import Dict, Any, List


def load_env_config() -> Dict[str, Any]:
    """Load configuration from environment variables"""
    config = {}
    
    if refresh_token := os.getenv("REFRESH_TOKEN"):
        config["refresh_token"] = refresh_token
    
    if host := os.getenv("HOST"):
        config["host"] = host
    
    if port := os.getenv("PORT"):
        config["port"] = port
        
    if auth_tokens := os.getenv("AUTH_TOKENS"):
        config["auth_tokens"] = [token.strip() for token in auth_tokens.split(",")]
        
    return config


def load_json_config() -> Dict[str, Any]:
    """Load configuration from config.json file"""
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "config.json"
    )

    if not os.path.exists(config_path):
        return {}

    with open(config_path, "r") as f:
        return json.load(f)


def validate_config(config: Dict[str, Any]) -> None:
    """Validate the configuration"""
    required_fields = ["refresh_token", "host", "port", "auth_tokens"]
    missing_fields = [field for field in required_fields if field not in config]

    if missing_fields:
        raise ValueError(
            f"Missing required fields in configuration: {', '.join(missing_fields)}"
        )

    if not isinstance(config["auth_tokens"], list):
        raise ValueError("auth_tokens must be an array")

    if not all(isinstance(token, str) for token in config["auth_tokens"]):
        raise ValueError("All auth_tokens must be strings")

    if len(config["auth_tokens"]) == 0:
        raise ValueError("auth_tokens array cannot be empty")


def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables and config.json file"""
    
    env_config = load_env_config()
    json_config = load_json_config()
    
    config = {**json_config, **env_config}
    
    validate_config(config)
    
    return config
