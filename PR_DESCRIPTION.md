# chore: modernization & reliability (NO change to JSON scraping behavior)

**Important guarantee:** This project continues to use Reddit's public `.json` endpoints only.
No changes to scraping logic or data sources are introduced here without explicit approval.

## What this changes
- Adds packaging (`pyproject.toml`) so users can `pip install .`
- Adds CI (pytest + flake8)
- Adds logging + retry session utilities
- Adds optional async media downloader
- Adds resume/manifest helpers
- Provides CLI with `subreddit|user|link` commands

## What stays the same
- Uses Reddit `.json` endpoints only
- No OAuth/API keys
- Same output concept; posts are written to `out/posts.jsonl` with raw JSON preserved
- Media download is optional and off by default

## Follow-ups (subject to approval)
- Align CLI flags with existing docs if different
- Expand tests with mocked HTTP responses
