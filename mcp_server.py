import os
import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from github import Github

load_dotenv()

mcp = FastMCP("agent-server")

# ==============================
# GitHub Setup
# ==============================

g = Github(os.getenv("GITHUB_TOKEN"))
repo = g.get_repo(os.getenv("REPO_NAME"))

DEFAULT_BRANCH = "main"
BRANCH_PREFIX = "ai/"


# ==============================
# TOOL: Read Repository File
# ==============================
"""
This MCP tool allows the AI agent to read files from the GitHub repository. The agent can use this to understand the codebase and company documentation before making changes.
"""
@mcp.tool()
def read_repository_file(file_path: str) -> str:
    try:
        contents = repo.get_contents(file_path, ref=DEFAULT_BRANCH)
        return contents.decoded_content.decode()
    except Exception as e:
        return f"ERROR: File '{file_path}' not found in repository."

# ==============================
# TOOL: List Repository Files
# ==============================
"""
This MCP tool allows the AI agent to list files in a directory of the GitHub repository. This can help the agent navigate the codebase and find relevant files for making changes."""
@mcp.tool()
def list_repository_files(path: str = "") -> str:
    """List files in a directory of the repository."""
    contents = repo.get_contents(path, ref=DEFAULT_BRANCH)
    file_list = [item.path for item in contents]
    return "\n".join(file_list)


# ==============================
# TOOL: Create Pull Request
# ==============================
"""
This MCP tool allows the AI agent to create a new branch, update a file, and open a pull request on GitHub. The agent will NEVER push directly to the main branch, ensuring a safe development workflow. The agent can use this tool to implement changes based on the change request and company goals
"""
@mcp.tool()
def create_pull_request(
    branch_name: str,
    file_path: str,
    content: str,
    message: str
) -> str:

    # Ensure branch prefix
    if not branch_name.startswith(BRANCH_PREFIX):
        branch_name = BRANCH_PREFIX + branch_name

    source = repo.get_branch(DEFAULT_BRANCH)

    # Avoid branch collision
    try:
        repo.get_branch(branch_name)
        branch_name = branch_name + "-1"
    except Exception:
        pass

    # Create branch
    repo.create_git_ref(
        ref=f"refs/heads/{branch_name}",
        sha=source.commit.sha
    )

    try:
        # Try updating existing file
        contents = repo.get_contents(file_path, ref=DEFAULT_BRANCH)

        repo.update_file(
            path=file_path,
            message=message,
            content=content,
            sha=contents.sha,
            branch=branch_name
        )

    except Exception:
        # If file does not exist → create new file
        repo.create_file(
            path=file_path,
            message=message,
            content=content,
            branch=branch_name
        )

    # Create PR
    pr = repo.create_pull(
        title=message[:60],  
        body=f"""
### 🤖 AI Generated Pull Request

Branch: `{branch_name}`
Target: `{DEFAULT_BRANCH}`

This change was generated automatically by the MCP AI Agent.
Please review before merging.
""",
        head=branch_name,
        base=DEFAULT_BRANCH
    )

    return pr.html_url

# ==============================
# TOOL: Notify Slack
# ==============================
"""
This MCP tool allows the AI agent to send messages to a Slack channel via an incoming webhook. The agent can use this to notify the maintainers of the repository about the changes.
"""
@mcp.tool()
def notify_slack(message: str) -> str:
    """Send a message to Slack channel."""

    webhook = os.getenv("SLACK_WEBHOOK_URL")

    response = requests.post(
        webhook,
        json={"text": message}
    )

    if response.status_code == 200:
        return "Slack notification sent successfully."
    else:
        return f"Slack error: {response.text}"

if __name__ == "__main__":
    mcp.run()