"""ClickUp MCP Server — full feature parity with @nazruden/clickup-server + task body reading."""

import os
import json
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("clickup")

BASE = "https://api.clickup.com/api/v2"
BASE_V3 = "https://api.clickup.com/api/v3"
TOKEN = os.environ.get("CLICKUP_API_TOKEN", "")


def _h():
    return {"Authorization": TOKEN, "Content-Type": "application/json"}


async def _get(url, params=None):
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(url, headers=_h(), params=params)
        r.raise_for_status()
        return r.json()


async def _post(url, body=None):
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(url, headers=_h(), json=body or {})
        r.raise_for_status()
        return r.json()


async def _put(url, body=None):
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.put(url, headers=_h(), json=body or {})
        r.raise_for_status()
        return r.json()


async def _delete(url):
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.delete(url, headers=_h())
        r.raise_for_status()
        return r.text or "{}"


def _json(data):
    return json.dumps(data, ensure_ascii=False, indent=2)


# ─── Teams/Workspaces ─────────────────────────────────────────────────────────

@mcp.tool()
async def get_teams() -> str:
    """Get all teams (workspaces) accessible to the authenticated user."""
    data = await _get(f"{BASE}/team")
    teams = [{"id": t["id"], "name": t["name"]} for t in data.get("teams", [])]
    return _json(teams)


# ─── Spaces ───────────────────────────────────────────────────────────────────

@mcp.tool()
async def get_spaces(team_id: str, archived: bool = False) -> str:
    """Get all spaces in a workspace."""
    data = await _get(f"{BASE}/team/{team_id}/space", {"archived": str(archived).lower()})
    spaces = [{"id": s["id"], "name": s["name"]} for s in data.get("spaces", [])]
    return _json(spaces)


@mcp.tool()
async def get_space(space_id: str) -> str:
    """Get details of a specific space."""
    return _json(await _get(f"{BASE}/space/{space_id}"))


@mcp.tool()
async def create_space(team_id: str, name: str) -> str:
    """Create a new space in a workspace."""
    return _json(await _post(f"{BASE}/team/{team_id}/space", {"name": name}))


@mcp.tool()
async def update_space(space_id: str, name: str) -> str:
    """Update a space name."""
    return _json(await _put(f"{BASE}/space/{space_id}", {"name": name}))


@mcp.tool()
async def delete_space(space_id: str) -> str:
    """Delete a space."""
    await _delete(f"{BASE}/space/{space_id}")
    return "Space deleted."


# ─── Folders ──────────────────────────────────────────────────────────────────

@mcp.tool()
async def get_folders(space_id: str, archived: bool = False) -> str:
    """Get all folders in a space."""
    data = await _get(f"{BASE}/space/{space_id}/folder", {"archived": str(archived).lower()})
    folders = [{"id": f["id"], "name": f["name"]} for f in data.get("folders", [])]
    return _json(folders)


@mcp.tool()
async def get_folder(folder_id: str) -> str:
    """Get details of a specific folder."""
    return _json(await _get(f"{BASE}/folder/{folder_id}"))


@mcp.tool()
async def create_folder(space_id: str, name: str) -> str:
    """Create a new folder in a space."""
    return _json(await _post(f"{BASE}/space/{space_id}/folder", {"name": name}))


@mcp.tool()
async def update_folder(folder_id: str, name: str) -> str:
    """Update a folder name."""
    return _json(await _put(f"{BASE}/folder/{folder_id}", {"name": name}))


@mcp.tool()
async def delete_folder(folder_id: str) -> str:
    """Delete a folder."""
    await _delete(f"{BASE}/folder/{folder_id}")
    return "Folder deleted."


# ─── Lists ────────────────────────────────────────────────────────────────────

@mcp.tool()
async def get_lists(folder_id: str) -> str:
    """Get all lists in a folder."""
    data = await _get(f"{BASE}/folder/{folder_id}/list")
    lists = [{"id": l["id"], "name": l["name"]} for l in data.get("lists", [])]
    return _json(lists)


@mcp.tool()
async def get_folderless_lists(space_id: str) -> str:
    """Get lists not inside any folder (directly under space)."""
    data = await _get(f"{BASE}/space/{space_id}/list")
    lists = [{"id": l["id"], "name": l["name"]} for l in data.get("lists", [])]
    return _json(lists)


@mcp.tool()
async def create_list(parent_id: str, parent_type: str, name: str, content: str = "", status: str = "") -> str:
    """Create a new list in a folder or space. parent_type: 'folder' or 'space'."""
    url = f"{BASE}/folder/{parent_id}/list" if parent_type == "folder" else f"{BASE}/space/{parent_id}/list"
    body = {"name": name}
    if content:
        body["content"] = content
    if status:
        body["status"] = status
    return _json(await _post(url, body))


# ─── Tasks ────────────────────────────────────────────────────────────────────

@mcp.tool()
async def get_tasks(list_id: str, include_closed: bool = False, page: int = 0) -> str:
    """Get tasks in a list. Returns name, status, assignees, and truncated description."""
    params = {"include_closed": str(include_closed).lower(), "page": str(page)}
    data = await _get(f"{BASE}/list/{list_id}/task", params)
    tasks = []
    for t in data.get("tasks", []):
        tasks.append({
            "id": t.get("id"),
            "name": t.get("name"),
            "status": t.get("status", {}).get("status"),
            "assignees": [a.get("username") for a in t.get("assignees", [])],
            "due_date": t.get("due_date"),
            "priority": t.get("priority", {}).get("priority") if t.get("priority") else None,
            "url": t.get("url"),
        })
    return _json(tasks)


@mcp.tool()
async def get_task(task_id: str) -> str:
    """Get full task details including description/body content (text_content and description)."""
    data = await _get(f"{BASE}/task/{task_id}")
    return _json({
        "id": data.get("id"),
        "name": data.get("name"),
        "description": data.get("description", ""),
        "text_content": data.get("text_content", ""),
        "markdown_description": data.get("markdown_description", ""),
        "status": data.get("status", {}).get("status"),
        "assignees": [a.get("username") for a in data.get("assignees", [])],
        "due_date": data.get("due_date"),
        "date_created": data.get("date_created"),
        "date_updated": data.get("date_updated"),
        "url": data.get("url"),
        "tags": [t.get("name") for t in data.get("tags", [])],
        "priority": data.get("priority", {}).get("priority") if data.get("priority") else None,
        "list": {"id": data.get("list", {}).get("id"), "name": data.get("list", {}).get("name")},
        "folder": {"id": data.get("folder", {}).get("id"), "name": data.get("folder", {}).get("name")},
        "space": {"id": data.get("space", {}).get("id")},
        "custom_fields": data.get("custom_fields", []),
    })


@mcp.tool()
async def create_task(list_id: str, name: str, description: str = "", status: str = "",
                      priority: Optional[int] = None, assignees: list[int] = [],
                      due_date: Optional[int] = None, tags: list[str] = []) -> str:
    """Create a new task in a list."""
    body: dict = {"name": name}
    if description:
        body["markdown_content"] = description
    if status:
        body["status"] = status
    if priority:
        body["priority"] = priority
    if assignees:
        body["assignees"] = assignees
    if due_date:
        body["due_date"] = due_date
    if tags:
        body["tags"] = tags
    data = await _post(f"{BASE}/list/{list_id}/task", body)
    return _json({"id": data.get("id"), "name": data.get("name"), "url": data.get("url")})


@mcp.tool()
async def update_task(task_id: str, name: str = "", description: str = "", status: str = "",
                      priority: Optional[int] = None, due_date: Optional[int] = None,
                      assignees: list[int] = []) -> str:
    """Update an existing task."""
    body: dict = {}
    if name:
        body["name"] = name
    if description:
        body["markdown_content"] = description
    if status:
        body["status"] = status
    if priority is not None:
        body["priority"] = priority
    if due_date is not None:
        body["due_date"] = due_date
    if assignees:
        body["assignees"] = assignees
    if not body:
        return "No fields to update."
    data = await _put(f"{BASE}/task/{task_id}", body)
    return _json({"id": data.get("id"), "name": data.get("name"), "status": data.get("status", {}).get("status")})


# ─── Comments ─────────────────────────────────────────────────────────────────

@mcp.tool()
async def get_comments(task_id: str) -> str:
    """Get all comments on a task."""
    data = await _get(f"{BASE}/task/{task_id}/comment")
    comments = [{"id": c.get("id"), "user": c.get("user", {}).get("username"),
                 "text": c.get("comment_text", ""), "date": c.get("date")}
                for c in data.get("comments", [])]
    return _json(comments)


@mcp.tool()
async def add_comment(task_id: str, text: str) -> str:
    """Add a comment to a task."""
    await _post(f"{BASE}/task/{task_id}/comment", {"comment_text": text})
    return "Comment added."


# ─── Views ────────────────────────────────────────────────────────────────────

@mcp.tool()
async def get_views(parent_id: str, parent_type: str) -> str:
    """Get views for a team/space/folder/list. parent_type: team|space|folder|list."""
    data = await _get(f"{BASE}/{parent_type}/{parent_id}/view")
    views = [{"id": v["id"], "name": v["name"], "type": v.get("type")} for v in data.get("views", [])]
    return _json(views)


@mcp.tool()
async def get_view(view_id: str) -> str:
    """Get details of a specific view."""
    data = await _get(f"{BASE}/view/{view_id}")
    return _json(data.get("view", data))


@mcp.tool()
async def get_view_tasks(view_id: str, page: int = 0) -> str:
    """Get tasks in a view."""
    data = await _get(f"{BASE}/view/{view_id}/task", {"page": str(page)})
    tasks = [{"id": t.get("id"), "name": t.get("name"), "status": t.get("status", {}).get("status")}
             for t in data.get("tasks", [])]
    return _json(tasks)


@mcp.tool()
async def create_view(parent_id: str, parent_type: str, name: str, view_type: str = "list") -> str:
    """Create a view. parent_type: team|space|folder|list. view_type: list|board|calendar|gantt."""
    data = await _post(f"{BASE}/{parent_type}/{parent_id}/view", {"name": name, "type": view_type})
    return _json(data.get("view", data))


@mcp.tool()
async def delete_view(view_id: str) -> str:
    """Delete a view."""
    await _delete(f"{BASE}/view/{view_id}")
    return "View deleted."


# ─── Custom Fields ────────────────────────────────────────────────────────────

@mcp.tool()
async def get_custom_fields(list_id: str) -> str:
    """Get all custom fields for a list."""
    data = await _get(f"{BASE}/list/{list_id}/field")
    fields = [{"id": f["id"], "name": f["name"], "type": f["type"]} for f in data.get("fields", [])]
    return _json(fields)


@mcp.tool()
async def set_custom_field(task_id: str, field_id: str, value: str) -> str:
    """Set a custom field value on a task. Value is passed as string (JSON-encode arrays/objects)."""
    # Try to parse as JSON for structured values
    try:
        parsed = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        parsed = value
    await _post(f"{BASE}/task/{task_id}/field/{field_id}", {"value": parsed})
    return "Custom field set."


@mcp.tool()
async def remove_custom_field(task_id: str, field_id: str) -> str:
    """Remove a custom field value from a task."""
    await _delete(f"{BASE}/task/{task_id}/field/{field_id}")
    return "Custom field removed."


# ─── Docs ─────────────────────────────────────────────────────────────────────

@mcp.tool()
async def search_docs(team_id: str, query: str = "") -> str:
    """Search docs in a workspace."""
    params = {}
    if query:
        params["query"] = query
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(f"{BASE_V3}/workspaces/{team_id}/docs", headers=_h(), params=params)
        r.raise_for_status()
        data = r.json()
    docs = [{"id": d.get("id"), "name": d.get("name")} for d in data.get("docs", [])]
    return _json(docs)


@mcp.tool()
async def get_doc_pages(workspace_id: str, doc_id: str) -> str:
    """Get pages in a doc."""
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(f"{BASE_V3}/workspaces/{workspace_id}/docs/{doc_id}/pages", headers=_h())
        r.raise_for_status()
        data = r.json()
    pages = [{"id": p.get("id"), "name": p.get("name")} for p in data.get("pages", [])]
    return _json(pages)


@mcp.tool()
async def get_doc_page_content(workspace_id: str, doc_id: str, page_id: str) -> str:
    """Get content of a specific doc page (markdown)."""
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(f"{BASE_V3}/workspaces/{workspace_id}/docs/{doc_id}/pages/{page_id}",
                        headers={**_h(), "Accept": "text/md"})
        r.raise_for_status()
        data = r.json()
    return _json({"id": data.get("id"), "name": data.get("name"), "content": data.get("content", "")})


@mcp.tool()
async def create_doc(workspace_id: str, name: str, parent_id: str = "", parent_type: int = 7) -> str:
    """Create a new doc. parent_type: 4=space, 5=folder, 6=list, 7=workspace."""
    body: dict = {"name": name}
    if parent_id:
        body["parent"] = {"id": parent_id, "type": parent_type}
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(f"{BASE_V3}/workspaces/{workspace_id}/docs", headers=_h(), json=body)
        r.raise_for_status()
        data = r.json()
    return _json({"id": data.get("id"), "name": data.get("name")})


@mcp.tool()
async def create_doc_page(workspace_id: str, doc_id: str, name: str, content: str = "") -> str:
    """Create a new page in a doc."""
    body: dict = {"name": name}
    if content:
        body["content"] = content
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(f"{BASE_V3}/workspaces/{workspace_id}/docs/{doc_id}/pages",
                         headers={**_h(), "Content-Type": "text/md"}, json=body)
        r.raise_for_status()
        data = r.json()
    return _json({"id": data.get("id"), "name": data.get("name")})


@mcp.tool()
async def edit_doc_page(workspace_id: str, doc_id: str, page_id: str, content: str, title: str = "") -> str:
    """Edit a doc page content (replace)."""
    body: dict = {"content": content}
    if title:
        body["name"] = title
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.put(f"{BASE_V3}/workspaces/{workspace_id}/docs/{doc_id}/pages/{page_id}",
                        headers={**_h(), "Content-Type": "text/md"}, json=body)
        r.raise_for_status()
        data = r.json()
    return _json({"id": data.get("id"), "name": data.get("name")})


# ─── Board (view shortcut) ───────────────────────────────────────────────────

@mcp.tool()
async def create_board(space_id: str, name: str) -> str:
    """Create a board view in a space (shortcut for create_view with type=board)."""
    data = await _post(f"{BASE}/space/{space_id}/view", {"name": name, "type": "board"})
    return _json(data.get("view", data))


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
