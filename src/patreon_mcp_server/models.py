from pydantic import BaseModel, ConfigDict
from typing import Optional


class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    image_url: Optional[str] = None
    about: Optional[str] = None
    url: Optional[str] = None
    created: Optional[str] = None


class Campaign(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    creation_name: Optional[str] = None
    patron_count: Optional[int] = None
    pledge_url: Optional[str] = None
    published_at: Optional[str] = None
    url: Optional[str] = None
    vanity: Optional[str] = None
    is_monthly: Optional[bool] = None
    created_at: Optional[str] = None
    image_url: Optional[str] = None
    summary: Optional[str] = None
    one_liner: Optional[str] = None
    pay_per_name: Optional[str] = None


class Tier(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    title: Optional[str] = None
    amount_cents: Optional[int] = None
    description: Optional[str] = None
    published: Optional[bool] = None
    patron_count: Optional[int] = None


class Member(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    full_name: Optional[str] = None
    patron_status: Optional[str] = None
    pledge_cadence: Optional[int] = None
    lifetime_support_cents: Optional[int] = None
    currently_entitled_amount_cents: Optional[int] = None
    last_charge_date: Optional[str] = None
    last_charge_status: Optional[str] = None
    will_pay_amount_cents: Optional[int] = None
    is_follower: Optional[bool] = None
    tiers: list[str] = []
    user_name: Optional[str] = None


class Post(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    title: Optional[str] = None
    content: Optional[str] = None
    is_paid: Optional[bool] = None
    is_public: Optional[bool] = None
    published_at: Optional[str] = None
    url: Optional[str] = None
    embed_data: Optional[dict] = None
    embed_url: Optional[str] = None
    app_id: Optional[str] = None
    app_status: Optional[str] = None


class CampaignDetail(BaseModel):
    model_config = ConfigDict(extra="ignore")
    campaign: Campaign
    tiers: list[Tier] = []


class MemberPage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    members: list[Member] = []
    next_cursor: Optional[str] = None


class PostPage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    posts: list[Post] = []
    next_cursor: Optional[str] = None


def _build_included_index(included: list[dict]) -> dict:
    return {(item["type"], item["id"]): item for item in included}


def parse_resource(item: dict, included: list[dict] = None) -> dict:
    result = {"id": item["id"], **item.get("attributes", {})}

    if included and "relationships" in item:
        rels = item["relationships"]
        index = _build_included_index(included)

        if "currently_entitled_tiers" in rels:
            tier_ids = [t["id"] for t in rels["currently_entitled_tiers"].get("data", [])]
            tier_names = []
            for tid in tier_ids:
                inc = index.get(("tier", tid))
                if inc:
                    tier_names.append(inc.get("attributes", {}).get("title", tid))
            result["tiers"] = tier_names

        if "user" in rels:
            user_data = rels["user"].get("data")
            if user_data:
                inc = index.get(("user", user_data["id"]))
                if inc:
                    result["user_name"] = inc.get("attributes", {}).get("full_name")

    return result


def parse_list(response: dict, model_class):
    included = response.get("included", [])
    items = []
    for item in response.get("data", []):
        parsed = parse_resource(item, included)
        items.append(model_class(**parsed))

    pagination = response.get("meta", {}).get("pagination", {})
    cursor = pagination.get("cursors", {}).get("next")

    return items, cursor


def parse_single(response: dict, model_class):
    data = response.get("data")
    if not data:
        raise ValueError("Invalid API response: missing 'data' key")
    included = response.get("included", [])
    parsed = parse_resource(data, included)
    return model_class(**parsed)
