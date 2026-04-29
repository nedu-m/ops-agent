"""Extract action items from a meeting transcript using Claude."""
import os
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are an operations assistant. Your job is to extract action items from meeting transcripts.

For each action item, extract:
- title: a short, clear task description (imperative verb, e.g. "Send proposal to client")
- assignee: the person responsible (first name or @handle if mentioned, null if unclear)
- due_date: deadline if mentioned (ISO format YYYY-MM-DD, null if not mentioned)

Return ONLY a JSON array. No explanation, no markdown, no extra text.

Example output:
[
  {"title": "Send proposal to client", "assignee": "Sarah", "due_date": "2026-05-02"},
  {"title": "Schedule follow-up call", "assignee": null, "due_date": null}
]

If there are no action items, return an empty array: []"""


def extract_action_items(transcript: str) -> list[dict]:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"Extract action items from this meeting transcript:\n\n{transcript}"}
        ],
    )

    raw = message.content[0].text.strip()

    try:
        items = json.loads(raw)
        if not isinstance(items, list):
            return []
        return items
    except json.JSONDecodeError:
        print(f"Failed to parse Claude response as JSON:\n{raw}")
        return []


if __name__ == "__main__":
    sample = """
    Team sync - April 29
    John: We need to send the updated proposal to the client by Friday.
    Sarah: I'll handle that. Also, someone needs to book the venue for the May event.
    John: Can you take that too Sarah, or should Mike do it?
    Sarah: Mike can book the venue. I'll focus on the proposal.
    John: Great. Also we need to update the onboarding docs before the new hire starts Monday.
    Mike: I'll update the docs today.
    """
    items = extract_action_items(sample)
    print(json.dumps(items, indent=2))
