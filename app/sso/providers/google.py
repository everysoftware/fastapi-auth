"""Google SSO Login Helper."""

from typing import ClassVar, Optional, Any

import httpx

from app.sso.providers.base import (
    DiscoveryDocument,
    SSOProvider,
)
from app.sso.providers.exceptions import SSOLoginError
from app.sso.providers.schemas import OpenID


class GoogleSSO(SSOProvider):
    """Class providing login via Google OAuth."""

    discovery_url = (
        "https://accounts.google.com/.well-known/openid-configuration"
    )
    provider = "google"
    scope: ClassVar = ["openid", "email", "profile"]

    async def openid_from_response(
        self,
        response: dict[Any, Any],
        session: Optional["httpx.AsyncClient"] = None,
    ) -> OpenID:
        """Return OpenID from user information provided by Google."""
        if response.get("email_verified"):
            return OpenID(
                email=response.get("email"),
                provider=self.provider,
                id=response.get("sub"),
                first_name=response.get("given_name"),
                last_name=response.get("family_name"),
                display_name=response.get("name"),
                picture=response.get("picture"),
            )
        raise SSOLoginError(
            message=f"User {response.get('email')} is not verified with Google"
        )

    async def get_discovery_document(self) -> DiscoveryDocument:
        """Get document containing handy urls."""
        async with httpx.AsyncClient() as session:
            response = await session.get(self.discovery_url)
            content = response.json()
            return content  # type: ignore[no-any-return]
