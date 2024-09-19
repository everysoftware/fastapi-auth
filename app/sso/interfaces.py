import abc
from typing import Any, overload, Literal

from .exceptions import NotSupported, Unauthorized
from .schemas import AnyUrl, SSOBearerToken, OpenID, DiscoveryDocument


class ISSO(abc.ABC):
    """Single sign-on client interface"""

    provider: str = NotImplemented
    client_id: str = NotImplemented
    client_secret: str = NotImplemented
    redirect_uri: AnyUrl | None = NotImplemented
    scope: list[str] = []

    _token: SSOBearerToken | None = None
    _discovery: DiscoveryDocument | None = None

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: AnyUrl | None = None,
        scope: list[str] | None = None,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri or self.redirect_uri
        self.scope = scope or self.scope

    async def discover(self) -> DiscoveryDocument:
        """Retrieves the discovery document containing useful URLs.

        Raises:
            NotSupported: If the provider is not supported.

        Returns:
            A dictionary containing important endpoints like authorization, token and userinfo.
        """
        raise NotSupported

    async def openid_from_response(
        self,
        response: dict[Any, Any],
    ) -> OpenID:
        """Converts a response from the provider's user info endpoint to an OpenID object.

        Args:
            response: The response from the user info endpoint.

        Raises:
            NotImplementedError: If the provider is not supported.

        Returns:
            The user information in a standardized format.
        """
        raise NotSupported

    @abc.abstractmethod
    async def get_login_url(
        self,
        *,
        redirect_uri: AnyUrl | None = None,
        params: dict[str, Any] | None = None,
        state: str | None = None,
    ) -> str: ...

    @abc.abstractmethod
    async def login(
        self,
        callback: Any,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> SSOBearerToken:
        """
        Login to the SSO provider and get the bearer token.

        Args:
            callback: The callback URL with code and other params.
            params: Additional query parameters to add to the token request.
            headers: Additional headers to add to the token request.

        Returns:
            The bearer token with access token and other details.
        """
        ...

    @abc.abstractmethod
    async def get_userinfo_response(
        self, *, headers: dict[str, Any] | None = None
    ) -> dict[str, Any]: ...

    async def get_discovery(self) -> DiscoveryDocument:
        if self._discovery is None:
            self._discovery = await self.discover()
        return self._discovery

    async def get_discovery_value(self, name: str) -> str:
        discovery = await self.get_discovery()
        value = getattr(discovery, name, None)
        if not isinstance(value, str) and value is None:
            raise NotSupported
        return value

    @property
    async def authorization_endpoint(self) -> str:
        return await self.get_discovery_value("authorization_endpoint")

    @property
    async def token_endpoint(self) -> str:
        return await self.get_discovery_value("token_endpoint")

    @property
    async def userinfo_endpoint(self) -> str:
        return await self.get_discovery_value("userinfo_endpoint")

    @property
    def token(self) -> SSOBearerToken:
        if self._token is None:
            raise Unauthorized
        return self._token

    @overload
    async def get_userinfo(
        self,
        *,
        normalize: Literal[True] = True,
        headers: dict[str, str] | None = None,
    ) -> OpenID: ...

    @overload
    async def get_userinfo(
        self,
        *,
        normalize: Literal[False],
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]: ...

    async def get_userinfo(
        self,
        *,
        normalize: bool = True,
        headers: dict[str, str] | None = None,
    ) -> OpenID | dict[str, Any]:
        """
        Get user information from the userinfo endpoint.

        Args:
            normalize: Convert the response to OpenID object.
            headers: Additional headers to add to the request.

        Returns:
            The user information in a standardized format.
        """
        response = await self.get_userinfo_response(headers=headers)
        if normalize:
            return await self.openid_from_response(response)
        return response
