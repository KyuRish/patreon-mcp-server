import os
import re
import httpx


class PatreonAPIError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"Patreon API error {status_code}: {message}")


_ID_PATTERN = re.compile(r"^[0-9]{1,20}$")


def _validate_id(value: str, name: str = "ID") -> str:
    if not _ID_PATTERN.match(value):
        raise ValueError(f"Invalid {name}: must be 1-20 ASCII digits")
    return value


def _validate_cursor(value: str) -> str:
    if len(value) > 512 or not value.isprintable():
        raise ValueError("Invalid pagination cursor")
    return value


class PatreonClient:
    BASE_URL = "https://www.patreon.com/api/oauth2/v2"

    def __init__(self, access_token: str = None):
        token = access_token or os.getenv("PATREON_ACCESS_TOKEN")
        if not token:
            raise ValueError("PATREON_ACCESS_TOKEN is required")

        self.client = httpx.Client(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {token}",
                "User-Agent": "PatreonMCP/1.0",
            },
            timeout=30.0,
            follow_redirects=False,
        )

    def _get(self, path: str, params: dict = None) -> dict:
        try:
            response = self.client.get(path, params=params)
            if not response.is_success:
                code = response.status_code
                if code == 429:
                    retry = response.headers.get("Retry-After", "60")
                    raise PatreonAPIError(429, f"Rate limited. Retry after {retry}s")
                if code == 401:
                    raise PatreonAPIError(401, "Unauthorized  - check your access token")
                if code == 403:
                    raise PatreonAPIError(403, "Forbidden  - insufficient permissions")
                if code == 404:
                    raise PatreonAPIError(404, "Resource not found")
                if 300 <= code < 400:
                    raise PatreonAPIError(code, "Unexpected redirect")
                raise PatreonAPIError(code, "Request failed")
        except PatreonAPIError:
            raise
        except httpx.RequestError:
            raise PatreonAPIError(0, "Connection error  - could not reach Patreon API")
        return response.json()

    def _build_fields(self, fields: dict[str, list[str]]) -> dict:
        return {f"fields[{k}]": ",".join(v) for k, v in fields.items()}

    def get_identity(self) -> dict:
        params = self._build_fields({
            "user": [
                "email", "full_name", "image_url", "about", "created",
                "url", "social_connections",
            ],
        })
        params["include"] = "campaign,memberships"
        return self._get("/identity", params)

    def get_campaigns(self) -> dict:
        params = self._build_fields({
            "campaign": [
                "creation_name", "patron_count", "pledge_url",
                "published_at", "url", "vanity", "is_monthly",
                "one_liner", "pay_per_name",
            ],
        })
        return self._get("/campaigns", params)

    def get_campaign(self, campaign_id: str) -> dict:
        _validate_id(campaign_id, "campaign_id")
        params = self._build_fields({
            "campaign": [
                "creation_name", "patron_count", "pledge_url",
                "published_at", "url", "vanity", "is_monthly",
                "created_at", "image_url", "summary",
                "one_liner", "pay_per_name",
            ],
            "tier": [
                "title", "amount_cents", "description",
                "published", "patron_count",
            ],
        })
        params["include"] = "tiers,creator"
        return self._get(f"/campaigns/{campaign_id}", params)

    def get_members(self, campaign_id: str, cursor: str = None) -> dict:
        _validate_id(campaign_id, "campaign_id")
        params = self._build_fields({
            "member": [
                "full_name", "patron_status",
                "pledge_cadence", "lifetime_support_cents",
                "currently_entitled_amount_cents", "last_charge_date",
                "last_charge_status", "will_pay_amount_cents",
                "is_follower",
            ],
            "tier": ["title", "amount_cents", "description"],
            "user": ["full_name", "image_url", "url"],
        })
        params["include"] = "currently_entitled_tiers,user"
        params["page[count]"] = "100"
        if cursor:
            _validate_cursor(cursor)
            params["page[cursor]"] = cursor
        return self._get(f"/campaigns/{campaign_id}/members", params)

    def get_posts(self, campaign_id: str, cursor: str = None) -> dict:
        _validate_id(campaign_id, "campaign_id")
        params = self._build_fields({
            "post": [
                "title", "content", "is_paid", "is_public",
                "published_at", "url", "embed_data", "embed_url",
                "app_id", "app_status",
            ],
        })
        params["page[count]"] = "20"
        if cursor:
            _validate_cursor(cursor)
            params["page[cursor]"] = cursor
        return self._get(f"/campaigns/{campaign_id}/posts", params)

    def get_post(self, post_id: str) -> dict:
        _validate_id(post_id, "post_id")
        params = self._build_fields({
            "post": [
                "title", "content", "is_paid", "is_public",
                "published_at", "url", "embed_data", "embed_url",
                "app_id", "app_status",
            ],
        })
        return self._get(f"/posts/{post_id}", params)
