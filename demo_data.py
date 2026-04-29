"""Seed demo data for Streamlit Cloud deployment."""
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).parent / "opsagent.db"

TRANSCRIPTS = [
    ("Chukwunedum", "#meeting-notes",
     "Weekly sync May 1. Alex needs to finalize the pitch deck by Thursday. Maria will reach out to the three investors and schedule intro calls before end of week. James is fixing the authentication bug before the demo on Friday. Lisa will update the landing page copy today. Alex will send the contract to the lawyer by Wednesday."),
    ("Chukwunedum", "#meeting-notes",
     "Product review April 30. Daniel owns shipping the mobile push notifications feature by May 5th. Sarah is writing test cases for the new onboarding flow. Kevin will set up the staging environment for client demos. Priya will write the feature changelog before Friday."),
    ("Chukwunedum", "#meeting-notes",
     "Morning standup. John is blocked on the database migration and needs DevOps to unblock him today. Emma will finish the billing integration by end of sprint. Team needs to review the PRs sitting in review."),
]

ACTION_ITEMS = [
    (1, "Finalize the pitch deck", "Alex", "2026-05-08", "task001", "https://app.clickup.com/t/task001", "created"),
    (1, "Reach out to investors and schedule intro calls", "Maria", "2026-05-07", "task002", "https://app.clickup.com/t/task002", "created"),
    (1, "Fix the authentication bug", "James", "2026-05-08", "task003", "https://app.clickup.com/t/task003", "created"),
    (1, "Update the landing page copy", "Lisa", None, "task004", "https://app.clickup.com/t/task004", "created"),
    (1, "Send contract to the lawyer", "Alex", "2026-05-07", "task005", "https://app.clickup.com/t/task005", "created"),
    (2, "Ship mobile push notifications feature", "Daniel", "2026-05-05", "task006", "https://app.clickup.com/t/task006", "created"),
    (2, "Write test cases for new onboarding flow", "Sarah", None, "task007", "https://app.clickup.com/t/task007", "created"),
    (2, "Set up staging environment for client demos", "Kevin", None, "task008", "https://app.clickup.com/t/task008", "created"),
    (2, "Write feature changelog for marketing", "Priya", "2026-05-02", "task009", "https://app.clickup.com/t/task009", "created"),
    (3, "Unblock John on database migration", None, None, "task010", "https://app.clickup.com/t/task010", "created"),
    (3, "Finish billing integration", "Emma", None, "task011", "https://app.clickup.com/t/task011", "created"),
    (3, "Review and clear PR queue", None, None, "task012", "https://app.clickup.com/t/task012", "created"),
]


def seed():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS transcripts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slack_user TEXT NOT NULL,
            slack_channel TEXT NOT NULL,
            slack_ts TEXT NOT NULL,
            raw_text TEXT NOT NULL,
            submitted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS action_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transcript_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            assignee TEXT,
            due_date TEXT,
            clickup_task_id TEXT,
            clickup_task_url TEXT,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    existing = conn.execute("SELECT COUNT(*) FROM transcripts").fetchone()[0]
    if existing > 0:
        conn.close()
        return

    now = datetime.now(timezone.utc).isoformat()
    for i, (user, channel, text) in enumerate(TRANSCRIPTS, 1):
        conn.execute(
            "INSERT INTO transcripts (slack_user, slack_channel, slack_ts, raw_text, submitted_at) VALUES (?,?,?,?,?)",
            (user, channel, f"ts{i}", text, now),
        )

    for item in ACTION_ITEMS:
        conn.execute(
            "INSERT INTO action_items (transcript_id, title, assignee, due_date, clickup_task_id, clickup_task_url, status) VALUES (?,?,?,?,?,?,?)",
            item,
        )

    conn.commit()
    conn.close()
    print("Demo data seeded.")


if __name__ == "__main__":
    seed()
