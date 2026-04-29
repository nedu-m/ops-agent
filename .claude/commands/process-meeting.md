Process a meeting transcript into ClickUp action items:

1. Ask the user to paste the meeting transcript (or read it from a file path if provided)
2. Run `python -c "from agents.extractor import extract_action_items; import json; print(json.dumps(extract_action_items(open('transcript.txt').read()), indent=2))"`
3. Show the extracted action items to the user and ask for confirmation before creating ClickUp tasks
4. If confirmed, run `python agents/clickup_tasks.py` with the items
5. Report how many tasks were created and provide the ClickUp URLs

If the transcript is provided directly in the command, save it to a temp file first.
