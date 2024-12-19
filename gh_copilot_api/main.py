import uvicorn
from gh_copilot_api.config import load_config


def main():
    """Main entry point for the application"""
    config = load_config()
    uvicorn.run(
        "gh_copilot_api.server:app",
        host=config["host"],
        port=config["port"],
        reload=True,
    )


if __name__ == "__main__":
    main()
