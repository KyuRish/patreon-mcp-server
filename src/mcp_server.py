from mcp.server.fastmcp import FastMCP
from utils.client import PatreonClient

mcp = FastMCP(
    name="patreon",
    instructions=(
        "Patreon API integration. Workflow: "
        "1) Call fetch_campaigns to get campaign IDs. "
        "2) Use campaign_id with fetch_campaign, fetch_members, or fetch_posts. "
        "3) For paginated tools (fetch_members, fetch_posts), pass next_cursor as cursor to get more pages. "
        "Note: patron emails are not fetched for privacy reasons."
    ),
)
client = PatreonClient()
