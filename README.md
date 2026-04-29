# OpsAgent

An internal operations automation agent. Paste a meeting transcript into Slack via
`/meetingnotes`, and the agent extracts action items using Claude and creates ClickUp
tasks automatically — with assignee and due date when mentioned.

## What it does

```
/meetingnotes <transcript>  →  Claude extracts action items  →  ClickUp tasks created
                                                                        │
                                                              Slack thread reply with task URLs
```

## Why this exists

Meeting action items get lost. Someone has to manually pull them from notes and create
tasks — that's friction, and it gets skipped. This agent removes that step entirely.
Paste the transcript, get tasks. The human stays in the loop via the Slack confirmation
thread but doesn't do the extraction work.

## Setup

```bash
git clone https://github.com/nedu-m/ops-agent
cd ops-agent
python -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env  # fill in credentials
python db/init_db.py
```

Register the `/meetingnotes` slash command in your Slack app (Slash Commands → Create New Command).
With Socket Mode enabled, no public URL is needed.

Then run the bot:
```bash
python agents/slack_bot.py
```

## Usage

In any Slack channel the bot has access to:
```
/meetingnotes Team sync April 29. John will send the proposal by Friday. Sarah will book the venue for May 10th. Mike is updating the onboarding docs today.
```

The bot replies in thread with extracted tasks and ClickUp links.

## Stack

Python · Anthropic SDK · Slack Bolt · ClickUp REST API · SQLite

## Design decisions

- **No confirmation step** — tasks are created immediately. The Slack thread reply is the audit trail. If a task is wrong, delete it in ClickUp.
- **SQLite log** — every transcript and extracted item is stored locally for review and future eval purposes.
- **Assignee as description** — ClickUp's API requires member IDs for assignees, not names. Names are stored in the task description until a member ID mapping is built.
