"""
A single shared `Limiter` instance, imported by main.py (to register the
exception handler + middleware) and by every router that needs a stricter or
looser limit on a specific route via the `@limiter.limit(...)` decorator.

In-memory storage (slowapi's default) is used deliberately: it requires no
Redis dependency, which keeps the whole stack deployable on Cloud Run's free
tier with a single container and no extra managed service. The tradeoff —
limits reset if the container restarts, and aren't shared across multiple
instances — is acceptable for a hackathon-scale deployment with
`min-instances` near zero. Swap `storage_uri` to a Redis URL later if this
needs to survive horizontal scaling.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
