"""Create ClickUp tasks from extracted action items."""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ["CLICKUP_API_TOKEN"]
LIST_ID = os.environ["CLICKUP_LIST_ID"]


def create_task(title: str, assignee: str | None = None, due_date: str | None = None) -> dict:
    headers = {"Authorization": TOKEN, "Content-Type": "application/json"}

    payload = {"name": title, "status": "to do"}

    if assignee:
        payload["description"] = f"Assigned to: {assignee}"

    if due_date:
        from datetime import datetime, timezone
        try:
            dt = datetime.strptime(due_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            payload["due_date"] = int(dt.timestamp() * 1000)
        except ValueError:
            pass

    resp = requests.post(
        f"https://api.clickup.com/api/v2/list/{LIST_ID}/task",
        headers=headers,
        json=payload,
    )
    resp.raise_for_status()
    data = resp.json()
    return {"id": data["id"], "url": data["url"]}


def create_tasks(action_items: list[dict]) -> list[dict]:
    results = []
    for item in action_items:
        try:
            result = create_task(
                title=item["title"],
                assignee=item.get("assignee"),
                due_date=item.get("due_date"),
            )
            results.append({**item, "clickup_task_id": result["id"], "clickup_task_url": result["url"]})
            print(f"  Created: {item['title']} → {result['url']}")
        except Exception as e:
            print(f"  Failed to create task '{item['title']}': {e}")
            results.append({**item, "clickup_task_id": None, "clickup_task_url": None})
    return results
