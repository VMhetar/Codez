import os
import requests
from github import Github
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

g = Github(os.getenv("GITHUB_TOKEN"))
repo = g.get_repo(os.getenv("Codez"))

class PRRequest(BaseModel):
    branch_name: str
    file_path: str
    content: str
    commit_message: str

@app.post("/create_pr")
def create_pr(data: PRRequest):
    source = repo.get_branch("main")
    repo.create_git_ref(ref=f"refs/heads/{data.branch_name}", sha=source.commit.sha)

    contents = repo.get_contents(data.file_path, ref="main")

    repo.update_file(
        path=data.file_path,
        message=data.commit_message,
        content=data.content,
        sha=contents.sha,
        branch=data.branch_name
    )

    pr = repo.create_pull(
        title=f"AI Update: {data.commit_message}",
        body="Generated via MCP AI Agent",
        head=data.branch_name,
        base="main"
    )

    return {"pr_url": pr.html_url}


@app.post("/notify_slack")
def notify_slack(message: dict):
    requests.post(os.getenv("SLACK_WEBHOOK_URL"), json=message)
    return {"status": "sent"}