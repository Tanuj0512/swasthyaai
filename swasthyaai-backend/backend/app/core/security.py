# """
# Verifies Supabase Auth JWTs.

# Design decision (see docs/ARCHITECTURE.md section 0): we use Supabase Auth
# exclusively — no Firebase — so this is the ONLY identity-verification code
# path in the backend. Supabase issues HS256-signed JWTs using the project's
# JWT secret; we verify the signature, expiry, and audience claim here. This
# module does not touch the database — it only proves "this token was issued
# by our Supabase project and hasn't expired." Turning a verified token into an
# application user (with a role and PHC/district scope) is the job of
# `app.api.v1.deps.get_current_staff`, which looks up `staff_profiles`.
# """

# from typing import Any, Dict

# from jose import JWTError, jwt

# from app.core.config import settings
# from app.core.exceptions import AuthenticationError


# def decode_supabase_jwt(token: str) -> Dict[str, Any]:
#     try:
#         payload = jwt.decode(
#             token,
#             settings.SUPABASE_JWT_SECRET,
#             algorithms=["ES256"],
#             audience=settings.SUPABASE_JWT_AUDIENCE,
#         )
#     except JWTError as exc:
#         raise AuthenticationError("Invalid or expired authentication token.") from exc

#     subject = payload.get("sub")
#     if not subject:
#         raise AuthenticationError("Authentication token is missing a subject claim.")

#     return payload


"""
Verifies Supabase Auth JWTs.

Design decision (see docs/ARCHITECTURE.md section 0): we use Supabase Auth
exclusively — no Firebase — so this is the ONLY identity-verification code
path in the backend. Supabase issues HS256-signed JWTs using the project's
JWT secret; we verify the signature, expiry, and audience claim here. This
module does not touch the database — it only proves "this token was issued
by our Supabase project and hasn't expired." Turning a verified token into an
application user (with a role and PHC/district scope) is the job of
`app.api.v1.deps.get_current_staff`, which looks up `staff_profiles`.
"""

"""
Verifies Supabase Auth JWTs.
...
"""

import logging
from typing import Any, Dict

from jose import JWTError, jwt

from app.core.config import settings
from app.core.exceptions import AuthenticationError

if settings.DEMO_DISABLE_JWT_VERIFY:
    logging.getLogger(__name__).warning(
        "JWT VERIFICATION DISABLED (DEMO_DISABLE_JWT_VERIFY=1) — "
        "tokens are NOT being cryptographically verified. Do not use outside a local demo."
    )


def decode_supabase_jwt(token: str) -> Dict[str, Any]:
    try:
        if settings.DEMO_DISABLE_JWT_VERIFY:
            payload = jwt.decode(
                token,
                key="",
                algorithms=["HS256", "ES256"],
                options={
                    "verify_signature": False,
                    "verify_aud": False,
                    "verify_exp": False,
                },
            )
        else:
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience=settings.SUPABASE_JWT_AUDIENCE,
            )
    except JWTError as exc:
        raise AuthenticationError("Invalid or expired authentication token.") from exc

    subject = payload.get("sub")
    if not subject:
        raise AuthenticationError("Authentication token is missing a subject claim.")

    return payload