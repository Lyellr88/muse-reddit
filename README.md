# muse-reddit

Personal-use Reddit OAuth shell. A small Python script that authenticates as a
single Reddit user (u/Alone-Biscotti6145) and performs a short list of
explicitly approved actions: submitting text posts and reading the account's
own post performance.

Status: early shell. The OAuth flow and API helpers are in place. Posting
targets and scheduling are still being decided.

## Setup

1. Create a Reddit app at https://www.reddit.com/prefs/apps (type: script).
2. Copy `.env.example` to `.env` and fill in your credentials.
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python reddit_shell.py`

## What it does

- Builds the Reddit OAuth authorize URL (`identity`, `read`, `submit` scopes).
- Exchanges the returned code for access and refresh tokens.
- Refreshes tokens when they expire.
- Provides thin helpers: `api_get`, `api_post`, `get_identity`, `submit_text_post`.

## What it does not do

- No automated commenting, voting, or messaging.
- No bulk or scheduled actions yet. Every post is submitted explicitly.
- Credentials never leave `.env`. The `.env` file is gitignored.

## License

MIT
