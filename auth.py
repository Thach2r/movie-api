import os
from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# Set the environment variable API_KEY before starting the server, e.g.:
#   export API_KEY="your-secret-key-here"
# If the variable is not set, a default development key is used so the app
# still starts during local testing without extra setup.
# ---------------------------------------------------------------------------

API_KEY = os.getenv("API_KEY", "dev-secret-123")

api_key_header = APIKeyHeader(
    name="X-API-Key",
    description="API key required for write operations (POST / PUT / DELETE).",
    auto_error=False,   # We raise our own error for a cleaner response body
)


async def require_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    FastAPI dependency that validates the X-API-Key request header.

    Usage
    -----
    Add  ``api_key: str = Depends(require_api_key)``  to any endpoint that
    should be protected (POST, PUT, DELETE).  Read-only endpoints (GET) do
    **not** need this dependency and remain publicly accessible.

    Raises
    ------
    HTTP 401  – header is missing entirely.
    HTTP 403  – header is present but the key is wrong.
    """
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Supply the X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key.",
        )
    return api_key