from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from aiohttp import ClientSession, ClientTimeout
import json

from gh_copilot_api.token import get_cached_copilot_token
from gh_copilot_api.logger import logger
from gh_copilot_api.config import load_config

config = load_config()


async def validate_auth_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return JSONResponse(
            status_code=401,
            content={
                "error": {
                    "code": "unauthorized",
                    "message": "No authorization header or api key found in request.",
                    "details": "No authorization header or api key found in request.",
                }
            },
        )

    try:
        token_type, token = auth_header.split()
        if token_type.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization type")

        if token not in config["auth_tokens"]:
            raise HTTPException(status_code=401, detail="Invalid authorization token")

        return token
    except ValueError:
        raise HTTPException(
            status_code=401, detail="Invalid authorization header format"
        )


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


API_URL = "https://api.individual.githubcopilot.com/chat/completions"
TIMEOUT = ClientTimeout(total=300)


def preprocess_request_body(request_body: dict) -> dict:
    """
    Preprocess the request body to handle array content in messages.
    """
    if not request_body.get("messages"):
        return request_body

    processed_messages = []

    for message in request_body["messages"]:
        if not isinstance(message.get("content"), list):
            processed_messages.append(message)
            continue

        for content_item in message["content"]:
            if content_item.get("type") != "text":
                raise HTTPException(400, "Only text type is supported in content array")

            processed_messages.append(
                {"role": message["role"], "content": content_item["text"]}
            )

    return {**request_body, "messages": processed_messages}


@app.get("/models")
async def list_models(auth_token: str = Depends(validate_auth_token)):
    """
    Returns a list of available models.
    """
    return {
        "object": "list",
        "data": [
            {
                "id": "o1",
                "object": "model",
                "created": 1687882411,
                "owned_by": "github-copilot",
                "permission": [],
            },
            {
                "id": "o1-preview",
                "object": "model",
                "created": 1687882411,
                "owned_by": "github-copilot",
                "permission": [],
            },
            {
                "id": "o1-mini",
                "object": "model",
                "created": 1687882411,
                "owned_by": "github-copilot",
                "permission": [],
            },
            {
                "id": "gpt-4o",
                "object": "model",
                "created": 1687882411,
                "owned_by": "github-copilot",
                "permission": [],
            },
            {
                "id": "claude-3.5-sonnet",
                "object": "model",
                "created": 1687882411,
                "owned_by": "github-copilot",
                "permission": [],
            },
        ],
    }


@app.post("/chat/completions")
async def proxy_chat_completions(
    request: Request, auth_token: str = Depends(validate_auth_token)
):
    """
    Proxies chat completion requests with SSE support.
    """
    request_body = await request.json()

    logger.info(f"Received request: {json.dumps(request_body, indent=2)}")

    try:
        request_body = preprocess_request_body(request_body)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(400, f"Error preprocessing request: {str(e)}")

    async def stream_response():
        try:
            token = await get_cached_copilot_token()
            async with ClientSession(timeout=TIMEOUT) as session:
                async with session.post(
                    API_URL,
                    json=request_body,
                    headers={
                        "Authorization": f"Bearer {token['token']}",
                        "Content-Type": "application/json",
                        "Accept": "text/event-stream",
                        "editor-version": "vscode/1.95.3",
                    },
                ) as response:
                    if response.status != 200:
                        error_message = await response.text()
                        logger.error(f"API error: {error_message}")
                        error_response = {
                            "error": {
                                "message": error_message,
                                "type": (
                                    "rate_limit_exceeded"
                                    if response.status == 429
                                    else "api_error"
                                ),
                                "code": (
                                    "rate_limit_exceeded"
                                    if response.status == 429
                                    else "api_error"
                                ),
                                "param": None,
                            }
                        }
                        yield json.dumps(error_response).encode("utf-8")
                        return

                    async for chunk in response.content.iter_chunks():
                        if chunk:
                            yield chunk[0]

        except Exception as e:
            logger.error(f"Error in stream_response: {str(e)}")
            error_response = {
                "error": {
                    "message": str(e),
                    "type": "internal_error",
                    "code": "internal_error",
                    "param": None,
                }
            }
            yield json.dumps(error_response).encode("utf-8")

    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream",
    )
