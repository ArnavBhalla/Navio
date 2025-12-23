"""
Simple in-memory rate limiting utilities (per-process, best-effort).

This is suitable for demo/dev environments. For production, consider a
distributed rate limiter (Redis, API gateway, etc.).
"""
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Deque, Dict

from fastapi import HTTPException, Request, status


@dataclass
class RateLimitRule:
    requests: int
    window: timedelta


class InMemoryRateLimiter:
    """
    Tracks request timestamps per key (e.g., per user or IP) and enforces a
    simple fixed-window rate limit.
    """

    def __init__(self, rule: RateLimitRule):
        self.rule = rule
        self._buckets: Dict[str, Deque[datetime]] = defaultdict(deque)

    def _get_bucket(self, key: str) -> Deque[datetime]:
        return self._buckets[key]

    def check(self, key: str) -> None:
        """
        Raise HTTPException if the key has exceeded its allowed rate.
        """
        now = datetime.now(timezone.utc)
        bucket = self._get_bucket(key)

        # Drop timestamps outside the window
        window_start = now - self.rule.window
        while bucket and bucket[0] < window_start:
            bucket.popleft()

        if len(bucket) >= self.rule.requests:
            # Too many requests in the current window
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
            )

        # Record this request
        bucket.append(now)


def rate_limit_key_from_request(request: Request) -> str:
    """
    Default key function: combines client host and path.

    If a user is authenticated with a Bearer token, you could extract the
    subject from the token and use that instead of IP.
    """
    client_host = request.client.host if request.client else "unknown"
    return f"{client_host}:{request.url.path}"


