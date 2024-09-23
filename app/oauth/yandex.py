from typing import Any

from app.oauth.base import SSOBase
from app.oauth.schemas import OpenID, DiscoveryDocument


class YandexSSO(SSOBase):
    provider = "yandex"
    scope = ["login:email", "login:info", "login:avatar"]
    avatar_url = "https://avatars.yandex.net/get-yapic"

    async def discover(self) -> DiscoveryDocument:
        return DiscoveryDocument(
            authorization_endpoint="https://oauth.yandex.ru/authorize",
            token_endpoint="https://oauth.yandex.ru/token",
            userinfo_endpoint="https://login.yandex.ru/info",
        )

    async def openid_from_response(
        self,
        response: dict[Any, Any],
    ) -> OpenID:
        picture = None
        if (avatar_id := response.get("default_avatar_id")) is not None:
            picture = f"{self.avatar_url}/{avatar_id}/islands-200"
        return OpenID(
            email=response.get("default_email"),
            display_name=response.get("display_name"),
            provider=self.provider,
            id=response.get("id"),
            first_name=response.get("first_name"),
            last_name=response.get("last_name"),
            picture=picture,
        )
