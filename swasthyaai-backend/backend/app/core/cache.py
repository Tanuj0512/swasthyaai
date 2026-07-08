"""
Lightweight in-process caching for read-heavy, computation-heavy endpoints —
specifically inventory forecasts and district aggregations, both of which
scan multiple tables and do non-trivial arithmetic on every call.

Why an in-process TTLCache instead of Redis: this app runs as a small number
of Cloud Run instances (often exactly one, given `min-instances: 0`), and the
data being cached (PHC operational snapshots) tolerates a few seconds of
staleness by nature — it's refreshed by periodic staff data entry, not
real-time streams. Introducing Redis here would add an extra managed service,
extra cost, and an extra failure mode for a caching need that a 30-second TTL
comfortably satisfies. Revisit if this ever runs as many replicas needing a
shared cache.
"""

import functools
import hashlib
import json
from typing import Callable

from cachetools import TTLCache

from app.core.config import settings

_cache: TTLCache = TTLCache(maxsize=512, ttl=settings.CACHE_DEFAULT_TTL_SECONDS)


def _make_key(func_name: str, args: tuple, kwargs: dict) -> str:
    # Skip the first positional arg when it's `self`/a repository/db session
    # object (unhashable, and irrelevant to cache identity) — only primitive
    # args/kwargs form the key.
    safe_args = [a for a in args if isinstance(a, (str, int, float, bool, type(None)))]
    safe_kwargs = {k: v for k, v in kwargs.items() if isinstance(v, (str, int, float, bool, type(None)))}
    raw = json.dumps({"f": func_name, "a": safe_args, "k": safe_kwargs}, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


def cache_response(ttl: int | None = None) -> Callable:
    """Decorator for service-layer methods returning JSON-serializable data.

    Usage:
        @cache_response(ttl=30)
        def get_forecast(self, phc_id: int) -> ForecastResult: ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = _make_key(func.__qualname__, args, kwargs)
            if key in _cache:
                return _cache[key]
            result = func(*args, **kwargs)
            _cache[key] = result
            return result

        return wrapper

    return decorator


def clear_cache() -> None:
    """Used by write-path services after mutating data, and by tests."""
    _cache.clear()
