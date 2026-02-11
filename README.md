# Patreon MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io)

Give AI assistants access to your Patreon creator data. The first authenticated Patreon MCP server  - works with Claude Desktop, Cursor, Windsurf, VS Code Copilot, and any MCP-compatible client.

## Quick Start

### 1. Get your Creator Access Token

Go to [Patreon Developer Portal](https://www.patreon.com/portal/registration/register-clients) and copy your **Creator Access Token**. This token gives access to your own campaign data only.

### 2. Configure your MCP client

**Claude Desktop**  - add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "patreon": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/patreon-mcp-server", "src/server.py"],
      "env": {
        "PATREON_ACCESS_TOKEN": "your_token_here"
      }
    }
  }
}
```

**Claude Code**  - add to `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "patreon": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/patreon-mcp-server", "src/server.py"],
      "env": {
        "PATREON_ACCESS_TOKEN": "your_token_here"
      }
    }
  }
}
```

### 3. Start using it

Ask your AI assistant things like:
- "Show me my Patreon campaigns"
- "Who are my top patrons by lifetime support?"
- "How many patrons are on each tier?"
- "Which patrons have declining payments?"
- "List my recent posts"

## Available Tools

| Tool | Description | Returns |
|------|-------------|---------|
| `fetch_identity` | Your authenticated profile | `User` |
| `fetch_campaigns` | List all your campaigns | `Campaign[]` |
| `fetch_campaign` | Campaign details with tier breakdown | `CampaignDetail` |
| `fetch_members` | Paginated patron list (100/page) | `MemberPage` |
| `fetch_posts` | Paginated post list (20/page) | `PostPage` |
| `fetch_post` | Single post by ID | `Post` |

**Pagination**: `fetch_members` and `fetch_posts` return a `next_cursor` field. Pass it as the `cursor` parameter to fetch the next page.

## Data Fields

### Member
`full_name`, `patron_status`, `pledge_cadence`, `lifetime_support_cents`, `currently_entitled_amount_cents`, `last_charge_date`, `last_charge_status`, `will_pay_amount_cents`, `is_follower`, `tiers`, `user_name`

### Campaign
`creation_name`, `patron_count`, `pledge_url`, `published_at`, `url`, `vanity`, `is_monthly`, `created_at`, `image_url`, `summary`, `one_liner`, `pay_per_name`

### Tier
`title`, `amount_cents`, `description`, `published`, `patron_count`

### Post
`title`, `content`, `is_paid`, `is_public`, `published_at`, `url`, `embed_data`, `embed_url`

## Privacy & Data

This server is designed with patron privacy in mind:

- **No patron emails**  - email addresses are never requested from the API
- **No private notes**  - creator notes about patrons are excluded
- **Read-only**  - no write operations, the server only reads your data
- **No data storage**  - the MCP server itself does not cache or persist any data

**Important**: When using this server with an AI assistant, patron data (names, pledge amounts, charge status) is sent to your AI provider (e.g., Anthropic, OpenAI) and may be temporarily retained per their data processing policies. You are responsible for ensuring your use complies with [Patreon's Creator Privacy Promise](https://support.patreon.com/hc/en-us/articles/360026912432) and applicable data protection laws.

This project is not affiliated with or endorsed by Patreon.

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager

```bash
# Clone the repo
git clone https://github.com/kyurish/patreon-mcp-server.git
cd patreon-mcp-server

# Install dependencies
uv sync

# Test it runs
PATREON_ACCESS_TOKEN=your_token uv run src/server.py
```

## Project Structure

```
src/
  server.py        # Entry point
  mcp_server.py    # FastMCP init + client instance
  tools.py         # @mcp.tool() definitions
  models.py        # Pydantic models + JSON:API parsers
  utils/
    client.py      # PatreonClient (HTTP layer)
```

## Roadmap

This server is currently read-only. Write operations (create posts, manage tiers, send messages to patrons) will be added if there's enough demand - [open an issue](https://github.com/kyurish/patreon-mcp-server/issues) or star the repo to show interest.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

If you find this useful, consider supporting development on [Patreon](https://www.patreon.com/kyurish).
