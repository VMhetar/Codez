import json
import httpx
import asyncio
import os
from mcp.server.fastmcp import FastMCP
from mcp_server import read_repository_file, create_pull_request, notify_slack
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_repository_file",
            "description": "Read a file from the repository",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"}
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_pull_request",
            "description": "Create a pull request in a new branch",
            "parameters": {
                "type": "object",
                "properties": {
                    "branch_name": {"type": "string"},
                    "file_path": {"type": "string"},
                    "content": {"type": "string"},
                    "message": {"type": "string"}
                },
                "required": ["branch_name", "file_path", "content", "message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "notify_slack",
            "description": "Send a message to Slack",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"}
                },
                "required": ["message"]
            }
        }
    }
]


async def run_llm(change_request: str):

    system_prompt = """
You are an autonomous AI engineering agent.

You MUST use tools for any action involving:
- Reading repository files
- Creating pull requests
- Sending Slack notifications

You are NOT allowed to output final code directly.

Workflow:
1. Read repository file.
2. Modify code.
3. Create a pull request using the tool.
4. Notify Slack.

Always call tools. Never just respond with code.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": change_request}
    ]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f'Bearer {os.getenv("OPENROUTER_API_KEY")}',
    }

    async with httpx.AsyncClient() as client:

        while True:

            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json={
                    "model": "anthropic/claude-3-haiku",
                    "messages": messages,
                    "tools": TOOLS,
                    "tool_choice":"auto"
                },
            )

            response.raise_for_status()
            result = response.json()

            message = result["choices"][0]["message"]

            # If no tool call → done
            if "tool_calls" not in message:
                return message["content"]

            tool_call = message["tool_calls"][0]
            tool_name = tool_call["function"]["name"]
            tool_args = json.loads(tool_call["function"]["arguments"])

            # Execute MCP tool locally
            if tool_name == "read_repository_file":
                tool_result = read_repository_file(**tool_args)

            elif tool_name == "create_pull_request":
                tool_result = create_pull_request(**tool_args)

            elif tool_name == "notify_slack":
                tool_result = notify_slack(**tool_args)

            else:
                tool_result = "Unknown tool"

            # Append tool result back to conversation
            messages.append(message)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": tool_result
            })
if __name__ == "__main__":
    user_input = input("Enter change request: ")
    result = asyncio.run(run_llm(user_input))
    print("\nFinal Response:\n", result)