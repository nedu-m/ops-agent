# OpsAgent — Architecture

OpsAgent is an internal operations automation agent. It listens for a `/meetingnotes`
Slack command, extracts action items from the transcript using Claude, and automatically
creates ClickUp tasks — with assignee and due date when mentioned.

## Agent Loop

```
Slack /meetingnotes <transcript>
        │
        ▼
   extractor.py (Claude)
        │
        ▼
   action_items[]
        │
        ▼
   clickup_tasks.py → ClickUp tasks created
        │
        ▼
   Slack thread reply (summary + task URLs)
        │
        ▼
   SQLite (transcripts + action_items tables)
```

## Agents

| File | What it does | Inputs | Outputs |
|---|---|---|---|
| `agents/extractor.py` | Extracts action items from transcript | Raw transcript text | JSON array of action items |
| `agents/clickup_tasks.py` | Creates ClickUp tasks | Action items array | ClickUp task IDs + URLs |
| `agents/slack_bot.py` | Slack bot entry point | `/meetingnotes` command | Slack thread reply, SQLite rows |

## Database

SQLite at `opsagent.db`. Initialize with: `python db/init_db.py`

Tables: `transcripts`, `action_items`

## Slash Commands

| Command | What it does |
|---|---|
| `/process-meeting` | Claude Code processes a transcript file into ClickUp tasks |

## Slack Setup

The `/meetingnotes` command must be registered in your Slack app:
1. Slack app → Slash Commands → Create New Command
2. Command: `/meetingnotes`
3. With Socket Mode enabled, no Request URL needed

## Environment Variables

```
ANTHROPIC_API_KEY     Anthropic API key
CLICKUP_API_TOKEN     ClickUp personal API token
CLICKUP_LIST_ID       ID of the list where action item tasks are created
SLACK_BOT_TOKEN       Slack bot OAuth token (xoxb-...)
SLACK_APP_TOKEN       Slack app-level token for Socket Mode (xapp-...)
SLACK_CHANNEL_ID      Default channel (optional)
```

## Common Failure Modes

- **No action items extracted**: Claude found nothing actionable. Transcript may be too short or conversational without clear tasks.
- **ClickUp 400 error**: Check `CLICKUP_LIST_ID` — tasks are created in whichever list this points to.
- **Slack command not appearing**: Register `/meetingnotes` under Slash Commands in your Slack app settings.
