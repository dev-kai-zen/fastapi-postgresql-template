"""Per-IP fixed-window rate limits (Redis). Stricter bucket for auth routes."""

from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable

import redis
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import Settings


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def _enforce_fixed_window(
    redis_url: str,
    key: str,
    limit: int,
    window_seconds: int,
) -> tuple[bool, int]:
    """Return (allowed, retry_after_seconds)."""
    if limit <= 0:
        return True, 0
    now = int(time.time())
    window_id = now // window_seconds
    redis_key = f"rl:{key}:{window_id}"
    with redis.from_url(redis_url, decode_responses=True) as r:
        pipe = r.pipeline()
        pipe.incr(redis_key)
        pipe.expire(redis_key, window_seconds)
        count_s, _ = pipe.execute()
        count = int(count_s)
        if count > limit:
            retry_after = window_seconds - (now % window_seconds)
            if retry_after <= 0:
                retry_after = window_seconds
            return False, retry_after
        return True, 0


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, settings: Settings):
        super().__init__(app)
        self._settings = settings

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        s = self._settings
        if not s.rate_limit_enabled:
            return await call_next(request)

        path = request.url.path
        prefix = s.api_v1_prefix.rstrip("/")
        if not path.startswith(prefix):
            return await call_next(request)

        rel = path.removeprefix(prefix)
        if not rel.startswith("/"):
            rel = f"/{rel}"

        if rel.startswith("/auth"):
            limit = s.rate_limit_auth_per_minute
            bucket = "auth"
        else:
            limit = s.rate_limit_api_per_minute
            bucket = "api"

        ip = client_ip(request)
        key = f"{bucket}:{ip}"

        allowed, retry_after = await asyncio.to_thread(
            _enforce_fixed_window,
            s.redis_url,
            key,
            limit,
            s.rate_limit_window_seconds,
        )

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"},
                headers={"Retry-After": str(retry_after)},
            )

        return await call_next(request)
