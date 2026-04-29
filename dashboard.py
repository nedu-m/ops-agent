"""OpsAgent — demo dashboard."""
import sqlite3
from pathlib import Path
from datetime import datetime

import streamlit as st
from demo_data import seed as seed_demo

DB_PATH = Path(__file__).parent / "opsagent.db"

if not DB_PATH.exists():
    seed_demo()

st.set_page_config(page_title="OpsAgent", page_icon="⚡", layout="wide")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def load_transcripts():
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, slack_user, slack_channel, raw_text, submitted_at FROM transcripts ORDER BY submitted_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def load_action_items(transcript_id=None):
    conn = get_conn()
    if transcript_id:
        rows = conn.execute(
            "SELECT * FROM action_items WHERE transcript_id = ? ORDER BY id", (transcript_id,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM action_items ORDER BY created_at DESC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── header ────────────────────────────────────────────────────────────────────

st.markdown("# ⚡ OpsAgent")
st.markdown(
    "An internal operations automation agent. Paste a meeting transcript into Slack via "
    "`/meetingnotes` and the agent extracts action items using **Claude** and creates "
    "**ClickUp tasks** automatically — with assignee and due date when mentioned."
)

st.divider()

# ── how it works ──────────────────────────────────────────────────────────────

st.markdown("## How it works")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("**1. Slack command**\n\n💬 `/meetingnotes <transcript>`\n\nPaste any meeting transcript directly in Slack")
with col2:
    st.markdown("**2. Claude extracts**\n\n🤖 Claude API\n\nIdentifies action items, assignees, and due dates")
with col3:
    st.markdown("**3. Tasks created**\n\n🗂️ ClickUp API\n\nOne task per action item, created automatically")
with col4:
    st.markdown("**4. Thread reply**\n\n✅ Slack\n\nSummary with task titles and ClickUp links posted in thread")

st.divider()

# ── stats ─────────────────────────────────────────────────────────────────────

transcripts = load_transcripts()
all_items = load_action_items()
created = [i for i in all_items if i["status"] == "created"]
failed = [i for i in all_items if i["status"] == "failed"]

st.markdown("## Pipeline stats")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Transcripts processed", len(transcripts))
m2.metric("Action items extracted", len(all_items))
m3.metric("ClickUp tasks created", len(created))
m4.metric("Success rate", f"{len(created)/len(all_items)*100:.0f}%" if all_items else "—")

st.divider()

# ── transcripts + action items ────────────────────────────────────────────────

st.markdown("## Processed transcripts")

if not transcripts:
    st.info("No transcripts yet. Use `/meetingnotes` in Slack to process your first meeting.")
else:
    for t in transcripts:
        items = load_action_items(t["id"])
        created_count = sum(1 for i in items if i["status"] == "created")
        submitted = t["submitted_at"][:16].replace("T", " ")

        with st.expander(
            f"**{t['slack_channel']}** — {submitted} — {created_count}/{len(items)} tasks created",
            expanded=False,
        ):
            st.markdown("**Transcript:**")
            st.caption(t["raw_text"])

            if items:
                st.markdown(f"**Extracted {len(items)} action items:**")
                for item in items:
                    icon = "✅" if item["status"] == "created" else "❌"
                    assignee = f" → **{item['assignee']}**" if item.get("assignee") else ""
                    due = f" _(due {item['due_date']})_" if item.get("due_date") else ""
                    url = item.get("clickup_task_url")
                    link = f" [{' View in ClickUp'}]({url})" if url else ""
                    st.markdown(f"{icon} {item['title']}{assignee}{due}{link}")

st.divider()

# ── all tasks table ───────────────────────────────────────────────────────────

st.markdown("## All extracted tasks")

tab_all, tab_created, tab_failed = st.tabs([
    f"All ({len(all_items)})",
    f"✅ Created ({len(created)})",
    f"❌ Failed ({len(failed)})",
])


def render_items(items):
    if not items:
        st.info("No tasks in this category.")
        return
    for item in items:
        icon = "✅" if item["status"] == "created" else "❌"
        with st.expander(f"{icon} {item['title']}", expanded=False):
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"**Assignee:** {item['assignee'] or '—'}")
            c2.markdown(f"**Due date:** {item['due_date'] or '—'}")
            c3.markdown(f"**Status:** `{item['status']}`")
            if item.get("clickup_task_url"):
                st.markdown(f"[Open in ClickUp]({item['clickup_task_url']})")


with tab_all:
    render_items(all_items)
with tab_created:
    render_items(created)
with tab_failed:
    render_items(failed)

st.divider()

# ── usage ─────────────────────────────────────────────────────────────────────

st.markdown("## Try it yourself")
st.markdown("In any Slack channel the bot has access to, run:")
st.code(
    "/meetingnotes Team sync. Sarah will send the updated proposal to the client by Friday. "
    "Mike needs to book the venue for the May 10th event. "
    "John will update the onboarding docs before the new hire starts Monday.",
    language="bash",
)
st.caption("The bot replies in thread with extracted tasks and ClickUp links within seconds.")

st.divider()

st.markdown(
    "<div style='text-align:center; color: gray; font-size: 0.85em;'>"
    "Built with Claude Code · "
    "<a href='https://github.com/nedu-m/ops-agent' target='_blank'>View on GitHub</a>"
    "</div>",
    unsafe_allow_html=True,
)
