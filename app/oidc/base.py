"""SSO login base dependency."""

import json
import logging
import os
import warnings
from types import TracebackType
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Optional,
    Type,
    TypedDict,
    Union,
    Mapping,
    cast,
    overload,
    Literal,
)

import httpx
import pydantic
from oauthlib.oauth2 import WebApplicationClient
from starlette import status
from starlette.responses import RedirectResponse

from .exceptions import UnsetStateWarning
from .pkce import get_pkce_challenge_pair
from .schemas import SSOCallback, OpenID, SSOBearerToken
from .state import generate_random_state

logger = logging.getLogger(__name__)


class DiscoveryDocument(TypedDict):
    authorization_endpoint: str
    token_endpoint: str
    userinfo_endpoint: str


class SSOProvider:
    """Base class for all SSO providers."""

    provider: str = NotImplemented
    client_id: str = NotImplemented
    client_secret: str = NotImplemented
    redirect_uri: Optional[Union[pydantic.AnyHttpUrl, str]] = NotImplemented
    scope: ClassVar[List[str]] = []
    headers: ClassVar[Optional[Dict[str, Any]]] = None
    uses_pkce: bool = False
    requires_state: bool = False

    _pkce_challenge_length: int = 96

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: Optional[Union[pydantic.AnyHttpUrl, str]] = None,
        allow_insecure_http: bool = False,
        scope: Optional[List[str]] = None,
    ):
        """Base class (mixin) for all SSO providers."""
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.redirect_uri: Optional[Union[pydantic.AnyHttpUrl, str]] = (
            redirect_uri
        )
        self.allow_insecure_http: bool = allow_insecure_http
        self._oauth_client: Optional[WebApplicationClient] = None
        self._generated_state: Optional[str] = None

        if self.allow_insecure_http:
            logger.debug(
                "Initializing %s with allow_insecure_http=True",
                self.__class__.__name__,
            )
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        self._scopes = scope or self.scope
        self._refresh_token: Optional[str] = None
        self._id_token: Optional[str] = None
        self._state: Optional[str] = None
        self._pkce_code_challenge: Optional[str] = None
        self._pkce_code_verifier: Optional[str] = None
        self._pkce_challenge_method = "S256"

    @property
    def state(self) -> Optional[str]:
        """Retrieves the state as it was returned from the server.

        Warning:
            This will emit a warning if the state is unset, implying either that
            the server didn't return a state or `verify_and_process` hasn't been
            called yet.

        Returns:
            Optional[str]: The state parameter returned from the server.
        """
        if self._state is None:
            warnings.warn(
                "'state' parameter is unset. This means the server either "
                "didn't return state (was this expected?) or 'verify_and_process' hasn't been called yet.",
                UnsetStateWarning,
            )
        return self._state

    @property
    def oauth_client(self) -> WebApplicationClient:
        """Retrieves the OAuth Client to aid in generating requests and parsing responses.

        Raises:
            NotImplementedError: If the provider is not supported or `client_id` is not set.

        Returns:
            WebApplicationClient: OAuth client instance.
        """
        if self.client_id == NotImplemented:
            raise NotImplementedError(
                f"Provider {self.provider} not supported"
            )  # pragma: no cover
        if self._oauth_client is None:
            self._oauth_client = WebApplicationClient(self.client_id)
        return self._oauth_client

    @property
    def access_token(self) -> Optional[str]:
        """Retrieves the access token from token endpoint.

        Returns:
            Optional[str]: The access token if available.
        """
        return self.oauth_client.access_token  # type: ignore[no-any-return]

    @property
    def refresh_token(self) -> Optional[str]:
        """Retrieves the refresh token if returned from provider.

        Returns:
            Optional[str]: The refresh token if available.
        """
        return self._refresh_token or self.oauth_client.refresh_token

    @property
    def id_token(self) -> Optional[str]:
        """Retrieves the id token if returned from provider.

        Returns:
            Optional[str]: The id token if available.
        """
        return self._id_token

    @property
    def is_authorized(self) -> bool:
        """Check if the user is authorized.

        Returns:
            Optional[str]: The access token if available.
        """
        return self.access_token is not None

    async def openid_from_response(
        self,
        response: dict[Any, Any],
        session: Optional[httpx.AsyncClient] = None,
    ) -> OpenID:
        """Converts a response from the provider's user info endpoint to an OpenID object.

        Args:
            response (dict): The response from the user info endpoint.
            session (Optional[httpx.AsyncClient]): The HTTPX AsyncClient session.

        Raises:
            NotImplementedError: If the provider is not supported.

        Returns:
            OpenID: The user information in a standardized format.
        """
        raise NotImplementedError(f"Provider {self.provider} not supported")

    async def get_discovery_document(self) -> DiscoveryDocument:
        """Retrieves the discovery document containing useful URLs.

        Raises:
            NotImplementedError: If the provider is not supported.

        Returns:
            DiscoveryDocument: A dictionary containing important endpoints like authorization, token and userinfo.
        """
        raise NotImplementedError(f"Provider {self.provider} not supported")

    @property
    async def authorization_endpoint(self) -> Optional[str]:
        """Return `authorization_endpoint` from discovery document."""
        discovery = await self.get_discovery_document()
        return discovery.get("authorization_endpoint")

    @property
    async def token_endpoint(self) -> Optional[str]:
        """Return `token_endpoint` from discovery document."""
        discovery = await self.get_discovery_document()
        return discovery.get("token_endpoint")

    @property
    async def userinfo_endpoint(self) -> Optional[str]:
        """Return `userinfo_endpoint` from discovery document."""
        discovery = await self.get_discovery_document()
        return discovery.get("userinfo_endpoint")

    @property
    def _extra_query_params(self) -> Dict[Any, Any]:
        return {}

    def __enter__(self) -> "SSOProvider":
        self._oauth_client = None
        self._refresh_token = None
        self._id_token = None
        self._state = None
        if self.requires_state:
            self._generated_state = generate_random_state()
        if self.uses_pkce:
            self._pkce_code_verifier, self._pkce_code_challenge = (
                get_pkce_challenge_pair(self._pkce_challenge_length)
            )
        return self

    def __exit__(
        self,
        _exc_type: Optional[Type[BaseException]],
        _exc_val: Optional[BaseException],
        _exc_tb: Optional[TracebackType],
    ) -> None:
        return None

    async def get_login_url(
        self,
        *,
        redirect_uri: Optional[Union[pydantic.AnyHttpUrl, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        state: Optional[str] = None,
    ) -> str:
        """Generates and returns the prepared login URL.

        Args:
            redirect_uri (Optional[str]): Overrides the `redirect_uri` specified on this instance.
            params (Optional[Dict[str, Any]]): Additional query parameters to add to the login request.
            state (Optional[str]): The state parameter for the OAuth 2.0 authorization request.

        Raises:
            ValueError: If `redirect_uri` is not provided either at construction or request time.

        Returns:
            str: The prepared login URL.
        """
        if self.requires_state and not state:
            state = self._generated_state
        params = params or {}
        redirect_uri = redirect_uri or self.redirect_uri
        if redirect_uri is None:
            raise ValueError(
                "redirect_uri must be provided, either at construction or request time"
            )
        if self.uses_pkce and not all(
            (self._pkce_code_verifier, self._pkce_code_challenge)
        ):
            warnings.warn(
                f"{self.__class__.__name__!r} uses PKCE and no code was generated yet. "
                "Use SSO class as a context manager to get rid of this warning and possible errors."
            )
        if self.requires_state and not state:
            if self._generated_state is None:
                warnings.warn(
                    f"{self.__class__.__name__!r} requires state in the request but none was provided nor "
                    "generated automatically. Use SSO as a context manager. The login process will most probably fail."
                )
            state = self._generated_state
        request_uri = self.oauth_client.prepare_request_uri(  # noqa
            await self.authorization_endpoint,
            redirect_uri=redirect_uri,
            state=state,
            scope=self._scopes,
            code_challenge=self._pkce_code_challenge,
            code_challenge_method=self._pkce_challenge_method,
            **params,
        )
        return cast(str, request_uri)

    def get_login_redirect(self, login_url: str) -> RedirectResponse:
        """Redirects to the login URL.

        Args:
            login_url (str): The login URL to redirect to.

        Returns:
            RedirectResponse: The redirect response.
        """
        response = RedirectResponse(login_url, status.HTTP_303_SEE_OTHER)
        if self.uses_pkce:
            response.set_cookie(
                "pkce_code_verifier", str(self._pkce_code_verifier)
            )
        return response

    async def get_token_request(
        self,
        callback: SSOCallback,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Prepare token request to get the access token.

        Args:
            callback (SSOCallback): The callback URL with code and other params.
            params (Mapping[str, Any]): Additional query parameters to add to the token request.
            headers (Mapping[str, str]): Additional headers to add to the token request.

        Returns:
            dict[str, Any]: The token request with URL, content and headers.
        """
        params = (params or {}) | self._extra_query_params
        additional_headers = headers or {}
        if self.headers:
            additional_headers |= self.headers
        if self.uses_pkce:
            if callback.pkce_code_verifier:
                params |= {"code_verifier": callback.pkce_code_verifier}
            else:
                warnings.warn(
                    "PKCE code verifier was not found in the callback. This will probably lead to a login error."
                )
        redirect_uri = callback.redirect_uri or self.redirect_uri
        token_url, headers, body = self.oauth_client.prepare_token_request(
            await self.token_endpoint,
            redirect_url=redirect_uri,
            code=callback.code,
            **params,
        )
        return {
            "url": token_url,
            "content": body,
            "headers": headers | additional_headers,
        }

    async def login(
        self,
        callback: SSOCallback,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> SSOBearerToken:
        """
        Login to the SSO provider and get the access token.

        Args:
            callback (SSOCallback): The callback URL with code and other params.
            params (Mapping[str, Any]): Additional query parameters to add to the token request.
            headers (Mapping[str, str]): Additional headers to add to the token request.

        Returns:
            SSOBearerToken: The bearer token with access token and other details.
        """
        self._state = callback.state
        request = await self.get_token_request(
            callback, params=params, headers=headers
        )
        auth = httpx.BasicAuth(self.client_id, self.client_secret)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                **request,
                auth=auth,
            )
        content = response.json()
        self.oauth_client.parse_request_body_response(json.dumps(content))
        self._refresh_token = content.get("refresh_token")
        self._id_token = content.get("id_token")
        return SSOBearerToken(
            access_token=self.oauth_client.access_token,
            refresh_token=content.get("refresh_token"),
            id_token=content.get("id_token"),
            expires_in=self.oauth_client.expires_in,
            token_type=self.oauth_client.token_type,
            scope=callback.scope or " ".join(self.scope),
        )

    @overload
    async def get_userinfo(
        self,
        convert_response: Literal[True] = True,
        headers: Optional[Mapping[str, Any]] = None,
    ) -> OpenID: ...

    @overload
    async def get_userinfo(
        self,
        convert_response: Literal[False],
        headers: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]: ...

    async def get_userinfo(
        self,
        convert_response: bool = True,
        headers: Optional[Mapping[str, Any]] = None,
    ) -> OpenID | dict[str, Any]:
        """
        Get user information from the userinfo endpoint.

        Args:
            convert_response (bool): Convert the response to OpenID object.
            headers (Optional[Mapping[str, Any]]): Additional headers to add to the request.

        Returns:
            OpenID | dict[str, Any]: The user information in a standardized format.
        """
        headers = headers or {}
        if self.headers:
            headers.update(self.headers)
        url, headers, _ = self.oauth_client.add_token(
            await self.userinfo_endpoint, headers=headers
        )
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
        content = response.json()
        if convert_response:
            return await self.openid_from_response(content, client)
        return content
