"""Per-IP fixed-window rate limits (in-process). Stricter bucket for auth routes.

Counters live in memory per process; they are not shared across workers or replicas.
For strict global limits in production, use an external store or edge rate limiting.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from threading import Lock

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import Settings

# (window_id, count) per logical key; resets when the window rolls.
_window_state: dict[str, tuple[int, int]] = {}
_state_lock = Lock()


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def _enforce_fixed_window(
    key: str,
    limit: int,
    window_seconds: int,
) -> tuple[bool, int]:
    """Return (allowed, retry_after_seconds)."""
    if limit <= 0:
        return True, 0
    now = int(time.time())
    window_id = now // window_seconds
    state_key = f"rl:{key}"
    with _state_lock:
        stored = _window_state.get(state_key)
        if stored is None or stored[0] != window_id:
            count = 1
            _window_state[state_key] = (window_id, count)
        else:
            count = stored[1] + 1
            _window_state[state_key] = (window_id, count)
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
