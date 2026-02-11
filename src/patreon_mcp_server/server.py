import os

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from patreon_mcp_server.mcp_server import mcp
import patreon_mcp_server.tools  # noqa: F401  - registers tools on mcp

def main():
    mcp.run(transport=os.getenv("TRANSPORT", "stdio"))

if __name__ == "__main__":
    main()
