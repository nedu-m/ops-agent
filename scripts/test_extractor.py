"""Spike: verify Claude extracts action items correctly."""
import json
import sys
sys.path.insert(0, ".")
from agents.extractor import extract_action_items

transcript = """
Team sync - April 29
John: We need to send the updated proposal to the client by Friday.
Sarah: I'll handle that. Also, someone needs to book the venue for the May 10th event.
John: Can you take that too Sarah, or should Mike do it?
Sarah: Mike can book the venue. I'll focus on the proposal.
John: Great. Also we need to update the onboarding docs before the new hire starts Monday.
Mike: I'll update the docs today.
"""

items = extract_action_items(transcript)
print(f"Extracted {len(items)} action items:\n")
print(json.dumps(items, indent=2))
