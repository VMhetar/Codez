import os
import requests
import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def modify_code(code, instruction):
    response = client.chat.completions.create(
        model="anthropic/claude-3-haiku",
        messages=[
            {
                "role": "system",
                "content": "You are a senior software engineer. Return only full modified code."
            },
            {
                "role": "user",
                "content": f"Instruction:\n{instruction}\n\nCode:\n{code}"
            }
        ]
    )

    return response.choices[0].message.content.strip()


def main():
    instruction = input("Enter instruction: ")

    file_path = "app.py"

    with open(file_path, "r") as f:
        original_code = f.read()

    modified_code = modify_code(original_code, instruction)

    branch_name = f"ai/{instruction.replace(' ','-')}-{datetime.datetime.now().strftime('%H%M%S')}"

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

    requests.post(
        "http://localhost:8000/notify_slack",
        json={
            "text": f"""
🚀 AI Agent Update

Task: {instruction}
Branch: {branch_name}
PR: {pr_url}

Awaiting review.
"""
        }
    )

    print("PR Created:", pr_url)


if __name__ == "__main__":
    main()