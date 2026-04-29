"""Slack bot: listen for /meetingnotes command, extract action items, create ClickUp tasks."""
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from extractor import extract_action_items
from clickup_tasks import create_tasks

load_dotenv()

DB_PATH = Path(__file__).parent.parent / "opsagent.db"

app = App(token=os.environ["SLACK_BOT_TOKEN"])


def save_to_db(slack_user: str, slack_channel: str, slack_ts: str,
               raw_text: str, action_items: list[dict]) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute(
        """INSERT INTO transcripts (slack_user, slack_channel, slack_ts, raw_text, submitted_at)
           VALUES (?, ?, ?, ?, ?)""",
        (slack_user, slack_channel, slack_ts, raw_text, datetime.now(timezone.utc).isoformat()),
    )
    transcript_id = cur.lastrowid

    for item in action_items:
        conn.execute(
            """INSERT INTO action_items
               (transcript_id, title, assignee, due_date, clickup_task_id, clickup_task_url, status)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                transcript_id,
                item["title"],
                item.get("assignee"),
                item.get("due_date"),
                item.get("clickup_task_id"),
                item.get("clickup_task_url"),
                "created" if item.get("clickup_task_id") else "failed",
            ),
        )

    conn.commit()
    conn.close()
    return transcript_id


@app.command("/meetingnotes")
def handle_meeting_notes(ack, body, client):
    ack()

    transcript = body.get("text", "").strip()
    user = body["user_id"]
    channel = body["channel_id"]

    if not transcript:
        client.chat_postEphemeral(
            channel=channel,
            user=user,
            text="Please paste your meeting transcript after the command.\nUsage: `/meetingnotes <transcript>`",
        )
        return

    # Acknowledge immediately — extraction takes a few seconds
    result = client.chat_postMessage(
        channel=channel,
        text=f"<@{user}> Processing your meeting notes... I'll extract action items and create ClickUp tasks.",
    )
    ts = result["ts"]

    action_items = extract_action_items(transcript)

    if not action_items:
        client.chat_postMessage(
            channel=channel,
            thread_ts=ts,
            text="No action items found in that transcript. Try pasting a longer excerpt with clear tasks or assignments.",
        )
        return

    created = create_tasks(action_items)
    save_to_db(user, channel, ts, transcript, created)

    # Build summary message
    lines = [f"Found *{len(created)} action items* — ClickUp tasks created:\n"]
    for item in created:
        assignee = f" → {item['assignee']}" if item.get("assignee") else ""
        due = f" (due {item['due_date']})" if item.get("due_date") else ""
        url = item.get("clickup_task_url")
        link = f" <{url}|View task>" if url else " _(failed to create)_"
        lines.append(f"• {item['title']}{assignee}{due}{link}")

    client.chat_postMessage(
        channel=channel,
        thread_ts=ts,
        text="\n".join(lines),
    )


if __name__ == "__main__":
    print("Ops Agent listening for /meetingnotes commands...")
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
