import os
import warnings
from typing import (
    Any,
)
from urllib.parse import urlencode

import httpx
from httpx import Request

from app.obs.logging import get_logger
from .exceptions import SSOLoginError
from .interfaces import ISSO
from .pkce import get_pkce_challenge_pair
from .schemas import (
    SSOCallback,
    SSOBearerToken,
    AnyUrl,
)
from .state import generate_random_state

logger = get_logger(__name__)


class SSOBase(ISSO):
    uses_pkce: bool = False
    requires_state: bool = True
    allow_insecure_http: bool = False

    generated_state: str | None = None
    pkce_code_challenge: str | None = None
    pkce_code_verifier: str | None = None
    pkce_challenge_method = "S256"
    pkce_challenge_length: int = 96
    state: str | None = None

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: AnyUrl | None = None,
        scope: list[str] | None = None,
        *,
        allow_insecure_http: bool = False,
    ):
        super().__init__(client_id, client_secret, redirect_uri, scope)
        if self.requires_state:
            self.generated_state = generate_random_state()
        if self.uses_pkce:
            self.pkce_code_verifier, self.pkce_code_challenge = (
                get_pkce_challenge_pair(self.pkce_challenge_length)
            )
        self.allow_insecure_http = allow_insecure_http
        if self.allow_insecure_http:
            logger.debug(
                "Initializing %s with allow_insecure_http=True",
                self.__class__.__name__,
            )
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    def get_client(self) -> httpx.AsyncClient:  # noqa
        return httpx.AsyncClient()

    async def get_login_url(
        self,
        *,
        scope: list[str] | None = None,
        redirect_uri: AnyUrl | None = None,
        state: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> str:
        params = params or {}
        redirect_uri = redirect_uri or self.redirect_uri
        if redirect_uri is None:
            raise ValueError(
                "redirect_uri must be provided, either at construction or request time"
            )
        if self.uses_pkce:
            params |= {
                "code_challenge": self.pkce_code_challenge,
                "code_challenge_method": self.pkce_challenge_method,
            }
        if self.requires_state:
            params |= {"state": state or self.generated_state}
        request_params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": " ".join(scope or self.scope),
            **params,
        }
        return (
            f"{await self.authorization_endpoint}?{urlencode(request_params)}"
        )

    async def prepare_token_request(
        self,
        callback: SSOCallback,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Request:
        params = params or {}
        headers = headers or {}
        headers |= {"Content-Type": "application/x-www-form-urlencoded"}
        if self.uses_pkce:
            if callback.pkce_code_verifier:
                params |= {"code_verifier": callback.pkce_code_verifier}
            else:
                warnings.warn(
                    "PKCE code verifier was not found in the callback. This will probably lead to a login error."
                )
        if self.requires_state:
            params |= {"state": self.state}
        body = {
            "grant_type": "authorization_code",
            "code": callback.code,
            "redirect_uri": callback.redirect_uri or self.redirect_uri,
            **params,
        }
        return Request(
            "post",
            await self.token_endpoint,
            data=body,
            headers=headers,
        )

    async def login(
        self,
        callback: SSOCallback,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> SSOBearerToken:
        self.state = callback.state
        request = await self.prepare_token_request(
            callback, params=params, headers=headers
        )
        auth = httpx.BasicAuth(self.client_id, self.client_secret)
        async with self.get_client() as client:
            response = await client.send(
                request,
                auth=auth,
            )
            content = response.json()
            if response.status_code < 200 or response.status_code > 299:
                logger.info(
                    f"SSO Login Response ({response.status_code}): {content}"
                )
                raise SSOLoginError()
            self._token = SSOBearerToken(
                access_token=content.get("access_token"),
                refresh_token=content.get("refresh_token"),
                id_token=content.get("id_token"),
                expires_in=content.get("expires_in"),
                token_type=content.get("token_type", "Bearer"),
                scope=content.get(
                    "scope", callback.scope or " ".join(self.scope)
                ),
            )
            return self._token

    async def get_userinfo_response(
        self,
        *,
        headers: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        headers = headers or {}
        headers |= {
            "Authorization": f"{self.token.token_type} {self.token.access_token}",
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(
                await self.userinfo_endpoint, headers=headers
            )
            return response.json()  # type: ignore[no-any-return]
