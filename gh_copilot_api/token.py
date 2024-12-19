import threading
from typing import Optional
import queue
import time

from aiohttp import ClientSession
from gh_copilot_api.logger import logger
from gh_copilot_api.config import load_config

CACHED_COPILOT_TOKEN: Optional[dict] = None
TOKEN_LOCK = threading.Lock()
TOKEN_CACHE_QUEUE: queue.Queue = queue.Queue(maxsize=1)


def cache_copilot_token(token_data: dict) -> None:
    logger.info("Caching token")
    global CACHED_COPILOT_TOKEN
    with TOKEN_LOCK:
        logger.debug(
            f"Caching new token that expires at {token_data.get('expires_at')}"
        )
        CACHED_COPILOT_TOKEN = token_data
        try:
            TOKEN_CACHE_QUEUE.get_nowait()
        except queue.Empty:
            pass
        TOKEN_CACHE_QUEUE.put(token_data)
        logger.debug("Token cached successfully")


async def get_cached_copilot_token() -> dict:
    global CACHED_COPILOT_TOKEN
    with TOKEN_LOCK:
        current_time = time.time()
        if CACHED_COPILOT_TOKEN:
            expires_at = CACHED_COPILOT_TOKEN.get("expires_at", 0)
            logger.info(
                f"Current token expires at {expires_at}, current time is {current_time}"
            )

        if (
            CACHED_COPILOT_TOKEN
            and CACHED_COPILOT_TOKEN.get("expires_at", 0) > time.time() + 300
        ):
            logger.info("Using cached token")
            return CACHED_COPILOT_TOKEN

    logger.info("Token expired or not found, refreshing...")
    new_token = await refresh_token()
    cache_copilot_token(new_token)
    return new_token


async def refresh_token() -> dict:
    logger.info("Attempting to refresh token")
    config = load_config()
    if not config["refresh_token"]:
        logger.error("refresh_token not set in config.json")
        raise ValueError("refresh_token not set in config.json")

    async with ClientSession() as session:
        async with session.get(
            url="https://api.github.com/copilot_internal/v2/token",
            headers={
                "Authorization": "token " + config["refresh_token"],
                "editor-version": "vscode/1.96.1",
            },
        ) as response:
            if response.status == 200:
                token_data = await response.json()
                logger.info(
                    f"Token refreshed successfully, expires at {token_data.get('expires_at')}"
                )
                return token_data
            error_msg = (
                f"Failed to refresh token: {response.status} {await response.text()}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
