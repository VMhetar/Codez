import os
import re
import json
import requests
import datetime
import difflib
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)


# ===============================
# MODIFY CODE (Structured JSON)
# ===============================
def modify_code(code, instruction):
    response = client.chat.completions.create(
        model="anthropic/claude-3-haiku",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a senior engineer.\n"
                    "Respond ONLY with valid JSON.\n"
                    "Ensure all strings are properly escaped.\n"
                    "Do not include markdown.\n"
                )
            },
            {
                "role": "user",
                "content": f"""
Return JSON in this exact format:

{{
  "code": "<FULL MODIFIED PYTHON FILE AS STRING>"
}}

Important:
- Escape all newlines as \\n
- Escape all quotes properly
- Return ONLY JSON

Instruction:
{instruction}

Code:
{code}
"""
            }
        ]
    )

    content = response.choices[0].message.content.strip()

    # Clean markdown if model still adds it
    if "```" in content:
        content = content.split("```")[1]

    try:
        parsed = json.loads(content)
        return parsed["code"]
    except Exception:
        print("⚠ JSON parsing failed. Raw output:\n")
        print(content)
        raise


# ===============================
# GENERATE PR SUMMARY
# ===============================
def generate_pr_summary(instruction, original, modified):
    response = client.chat.completions.create(
        model="anthropic/claude-3-haiku",
        messages=[
            {
                "role": "system",
                "content": "You are a senior code reviewer. Provide structured markdown."
            },
            {
                "role": "user",
                "content": f"""
Instruction:
{instruction}

Original Code:
{original}

Modified Code:
{modified}

Generate:
- Summary
- Key Changes
- Risk Level (Low/Medium/High)
- Testing Recommendations
"""
            }
        ]
    )

    return response.choices[0].message.content


# ===============================
# MAIN
# ===============================
def main():
    instruction = input("Enter instruction: ")
    file_path = "app.py"

    with open(file_path, "r") as f:
        original_code = f.read()

    modified_code = modify_code(original_code, instruction)

    print("\n---- ORIGINAL ----\n", original_code)
    print("\n---- MODIFIED ----\n", modified_code)

    # Clean branch name
    short = re.sub(r'[^a-zA-Z0-9 ]', '', instruction)
    short = short.split('.')[0][:30]
    short = short.replace(" ", "-").lower()
    branch_name = f"ai/{short}-{datetime.datetime.now().strftime('%H%M%S')}"

    # Generate PR summary
    pr_summary = generate_pr_summary(instruction, original_code, modified_code)

    # Generate diff
    diff = "\n".join(
        difflib.unified_diff(
            original_code.splitlines(),
            modified_code.splitlines(),
            lineterm=""
        )
    )

    # Create PR
    pr_response = requests.post(
        "http://localhost:8000/create_pr",
        json={
            "branch_name": branch_name,
            "file_path": file_path,
            "content": modified_code,
            "commit_message": instruction
        }
    )

    pr_url = pr_response.json()["pr_url"]

    # Send Slack notification with diff preview
    requests.post(
        "http://localhost:8000/notify_slack",
        json={
            "text": f"""
🚀 AI Agent Update

Task: {instruction}
Branch: {branch_name}
PR: {pr_url}

📌 Diff Preview:

Awaiting review.
"""
        }
    )

    print("PR Created:", pr_url)


if __name__ == "__main__":
    main()