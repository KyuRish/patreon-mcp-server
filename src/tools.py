from typing import Optional
from mcp_server import mcp, client
from utils.client import PatreonAPIError
from models import (
    User, Campaign, Tier, Member, Post,
    CampaignDetail, MemberPage, PostPage,
    parse_list, parse_single,
)


def _handle_error(e: Exception) -> str:
    if isinstance(e, PatreonAPIError):
        return str(e)
    if isinstance(e, ValueError):
        return str(e)
    return "Unexpected error communicating with Patreon API"


@mcp.tool()
def fetch_identity() -> User:
    """Fetch the authenticated Patreon user's profile."""
    try:
        response = client.get_identity()
        return parse_single(response, User)
    except Exception as e:
        raise RuntimeError(_handle_error(e))


@mcp.tool()
def fetch_campaigns() -> list[Campaign]:
    """Fetch all campaigns for the authenticated creator."""
    try:
        response = client.get_campaigns()
        campaigns, _ = parse_list(response, Campaign)
        return campaigns
    except Exception as e:
        raise RuntimeError(_handle_error(e))


@mcp.tool()
def fetch_campaign(campaign_id: str) -> CampaignDetail:
    """
    Fetch details for a specific campaign including tiers.

    Args:
        campaign_id: The campaign ID to fetch (numeric)
    """
    try:
        response = client.get_campaign(campaign_id)
        campaign = parse_single(response, Campaign)
        included = response.get("included", [])
        tiers = [
            Tier(id=t["id"], **t.get("attributes", {}))
            for t in included if t.get("type") == "tier"
        ]
        return CampaignDetail(campaign=campaign, tiers=tiers)
    except Exception as e:
        raise RuntimeError(_handle_error(e))


@mcp.tool()
def fetch_members(campaign_id: str, cursor: Optional[str] = None) -> MemberPage:
    """
    Fetch members/patrons of a campaign with pagination. Returns up to 100 members per page.
    Pass next_cursor from the response as cursor to get the next page.

    Args:
        campaign_id: The campaign ID (numeric)
        cursor: Pagination cursor for next page (from previous response)
    """
    try:
        response = client.get_members(campaign_id, cursor)
        members, next_cursor = parse_list(response, Member)
        return MemberPage(members=members, next_cursor=next_cursor)
    except Exception as e:
        raise RuntimeError(_handle_error(e))


@mcp.tool()
def fetch_posts(campaign_id: str, cursor: Optional[str] = None) -> PostPage:
    """
    Fetch posts from a campaign with pagination. Returns up to 20 posts per page.
    Pass next_cursor from the response as cursor to get the next page.

    Args:
        campaign_id: The campaign ID (numeric)
        cursor: Pagination cursor for next page (from previous response)
    """
    try:
        response = client.get_posts(campaign_id, cursor)
        posts, next_cursor = parse_list(response, Post)
        return PostPage(posts=posts, next_cursor=next_cursor)
    except Exception as e:
        raise RuntimeError(_handle_error(e))


@mcp.tool()
def fetch_post(post_id: str) -> Post:
    """
    Fetch a specific post by ID.

    Args:
        post_id: The post ID to fetch (numeric)
    """
    try:
        response = client.get_post(post_id)
        return parse_single(response, Post)
    except Exception as e:
        raise RuntimeError(_handle_error(e))
