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
    transcript_id INTEGER NOT NULL REFERENCES transcripts(id),
    title TEXT NOT NULL,
    assignee TEXT,
    due_date TEXT,
    clickup_task_id TEXT,
    clickup_task_url TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
