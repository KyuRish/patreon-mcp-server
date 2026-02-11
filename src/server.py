import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from mcp_server import mcp
import tools  # noqa: F401  - registers tools on mcp

if __name__ == "__main__":
    mcp.run(transport=os.getenv("TRANSPORT", "stdio"))
