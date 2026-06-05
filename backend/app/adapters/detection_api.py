import base64
import httpx
import json
import logging
from pathlib import Path
from app.core.config import settings
from app.models.detection import DetectionResult

logger = logging.getLogger(__name__)

# Cache for Baidu access token
_baidu_token_cache: dict = {"token": None, "expires_at": 0}


async def get_baidu_access_token() -> str:
    """Get Baidu access token, with caching."""
    import time

    now = time.time()
    if _baidu_token_cache["token"] and now < _baidu_token_cache["expires_at"]:
        return _baidu_token_cache["token"]

    async with httpx.AsyncClient(timeout=settings.BAIDU_API_TIMEOUT_SECONDS) as client:
        resp = await client.post(
            settings.BAIDU_TOKEN_URL,
            params={
                "grant_type": "client_credentials",
                "client_id": settings.BAIDU_API_KEY,
                "client_secret": settings.BAIDU_SECRET_KEY,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    if "access_token" not in data:
        raise RuntimeError(f"Failed to get Baidu access token: {data}")

    token = data["access_token"]
    expires_in = data.get("expires_in", 2592000)  # Default 30 days
    _baidu_token_cache["token"] = token
    _baidu_token_cache["expires_at"] = now + expires_in - 3600  # Refresh 1 hour early

    return token


async def detect_image(file_path: str) -> dict:
    """
    Call Baidu advanced_general API with a local image file.
    Returns the parsed response dict.
    """
    # Read and encode image
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {file_path}")

    with open(path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode("utf-8")

    token = await get_baidu_access_token()

    async with httpx.AsyncClient(timeout=settings.BAIDU_API_TIMEOUT_SECONDS) as client:
        resp = await client.post(
            f"{settings.BAIDU_DETECT_URL}?access_token={token}",
            data={"image": image_base64},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        resp.raise_for_status()
        data = resp.json()

    return data


def parse_detection_result(data: dict) -> dict:
    """
    Parse Baidu API response into internal format.
    Returns dict with result_num, items, raw_log_id.
    Raises ValueError if the API returned an error.
    """
    if "error_code" in data or "error_msg" in data:
        raise ValueError(f"Baidu API error: {data.get('error_msg', 'Unknown error')}")

    items = []
    for item in data.get("result", []):
        items.append({
            "keyword": item.get("keyword", ""),
            "root": item.get("root", ""),
            "score": item.get("score", 0.0),
        })

    return {
        "result_num": data.get("result_num", len(items)),
        "items": items,
        "raw_log_id": str(data.get("log_id", "")),
    }


def build_detection_result(task_id: str, parsed: dict) -> DetectionResult:
    """Build a DetectionResult ORM object from parsed data."""
    return DetectionResult(
        task_id=task_id,
        result_num=parsed["result_num"],
        items_json=json.dumps(parsed["items"], ensure_ascii=False),
        raw_log_id=parsed.get("raw_log_id"),
    )
