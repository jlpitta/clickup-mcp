"""ClickUp MCP Server — expõe get_task (com description) e operações básicas."""

import os
import json
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("clickup")

BASE_URL = "https://api.clickup.com/api/v2"
TOKEN = os.environ.get("CLICKUP_API_TOKEN", "")
TEAM_ID = os.environ.get("CLICKUP_TEAM_ID", "")


def _headers():
    return {"Authorization": TOKEN, "Content-Type": "application/json"}


@mcp.tool()
async def get_task(task_id: str) -> str:
    """Get full task details including description/body content."""
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/task/{task_id}", headers=_headers())
        r.raise_for_status()
        data = r.json()
    return json.dumps({
        "id": data.get("id"),
        "name": data.get("name"),
        "description": data.get("description", ""),
        "text_content": data.get("text_content", ""),
        "status": data.get("status", {}).get("status"),
        "assignees": [a.get("username") for a in data.get("assignees", [])],
        "due_date": data.get("due_date"),
        "date_created": data.get("date_created"),
        "date_updated": data.get("date_updated"),
        "url": data.get("url"),
        "tags": [t.get("name") for t in data.get("tags", [])],
        "priority": data.get("priority", {}).get("priority") if data.get("priority") else None,
        "list": data.get("list", {}).get("name"),
    }, ensure_ascii=False, indent=2)


@mcp.tool()
async def get_tasks_in_list(list_id: str, include_closed: bool = False) -> str:
    """Get all tasks in a list with their descriptions."""
    params = {"include_closed": str(include_closed).lower()}
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/list/{list_id}/task", headers=_headers(), params=params)
        r.raise_for_status()
        data = r.json()
    tasks = []
    for t in data.get("tasks", []):
        tasks.append({
            "id": t.get("id"),
            "name": t.get("name"),
            "status": t.get("status", {}).get("status"),
            "assignees": [a.get("username") for a in t.get("assignees", [])],
            "due_date": t.get("due_date"),
            "text_content": t.get("text_content", "")[:500],
        })
    return json.dumps(tasks, ensure_ascii=False, indent=2)


@mcp.tool()
async def create_task(list_id: str, name: str, description: str = "", status: str = "", priority: int = 0, assignees: list[int] = []) -> str:
    """Create a new task in a list."""
    body = {"name": name}
    if description:
        body["description"] = description
    if status:
        body["status"] = status
    if priority:
        body["priority"] = priority
    if assignees:
        body["assignees"] = assignees
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE_URL}/list/{list_id}/task", headers=_headers(), json=body)
        r.raise_for_status()
        data = r.json()
    return json.dumps({"id": data.get("id"), "name": data.get("name"), "url": data.get("url")}, ensure_ascii=False)


@mcp.tool()
async def update_task(task_id: str, name: str = "", description: str = "", status: str = "", priority: int = 0) -> str:
    """Update an existing task's properties."""
    body = {}
    if name:
        body["name"] = name
    if description:
        body["description"] = description
    if status:
        body["status"] = status
    if priority:
        body["priority"] = priority
    if not body:
        return "No fields to update."
    async with httpx.AsyncClient() as client:
        r = await client.put(f"{BASE_URL}/task/{task_id}", headers=_headers(), json=body)
        r.raise_for_status()
        data = r.json()
    return json.dumps({"id": data.get("id"), "name": data.get("name"), "status": data.get("status", {}).get("status")}, ensure_ascii=False)


@mcp.tool()
async def get_comments(task_id: str) -> str:
    """Get all comments on a task."""
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE_URL}/task/{task_id}/comment", headers=_headers())
        r.raise_for_status()
        data = r.json()
    comments = []
    for c in data.get("comments", []):
        comments.append({
            "id": c.get("id"),
            "user": c.get("user", {}).get("username"),
            "text": c.get("comment_text", ""),
            "date": c.get("date"),
        })
    return json.dumps(comments, ensure_ascii=False, indent=2)


@mcp.tool()
async def add_comment(task_id: str, text: str) -> str:
    """Add a comment to a task."""
    body = {"comment_text": text}
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE_URL}/task/{task_id}/comment", headers=_headers(), json=body)
        r.raise_for_status()
    return "Comment added."


if __name__ == "__main__":
    mcp.run()
