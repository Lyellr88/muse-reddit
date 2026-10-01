"""muse-reddit: personal-use Reddit OAuth shell.

Authenticates as one Reddit user via OAuth2 (authorization code flow) and
exposes thin helpers for explicitly approved actions: submitting text posts
and reading the account's own data.

No automated commenting, voting, or messaging. Every write action is
submitted explicitly by the operator.
"""

import os
import sys
import urllib.parse
import webbrowser

import requests

AUTH_URL = "https://www.reddit.com/api/v1/authorize"
TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
API_BASE = "https://oauth.reddit.com"

CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET", "")
REDIRECT_URI = os.environ.get("REDDIT_REDIRECT_URI", "http://localhost:8080")
USER_AGENT = os.environ.get(
    "REDDIT_USER_AGENT", "muse-reddit:0.1 (by /u/Alone-Biscotti6145)"
)
SCOPES = "identity read submit"


def build_authorize_url(state="muse-reddit"):
    """Return the Reddit approval URL the operator opens in a browser."""
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "state": state,
        "redirect_uri": REDIRECT_URI,
        "duration": "permanent",
        "scope": SCOPES,
    }
    return AUTH_URL + "?" + urllib.parse.urlencode(params)


def exchange_code(code):
    """Exchange an authorize code for access + refresh tokens."""
    resp = requests.post(
        TOKEN_URL,
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
        },
        headers={"User-Agent": USER_AGENT},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def refresh_tokens(refresh_token):
    """Get a fresh access token from a stored refresh token."""
    resp = requests.post(
        TOKEN_URL,
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
        headers={"User-Agent": USER_AGENT},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def api_get(access_token, path, params=None):
    """Authenticated GET against the Reddit API."""
    resp = requests.get(
        API_BASE + path,
        headers={
            "Authorization": "bearer " + access_token,
            "User-Agent": USER_AGENT,
        },
        params=params or {},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def api_post(access_token, path, data=None):
    """Authenticated POST against the Reddit API."""
    resp = requests.post(
        API_BASE + path,
        headers={
            "Authorization": "bearer " + access_token,
            "User-Agent": USER_AGENT,
        },
        data=data or {},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def get_identity(access_token):
    """Return the authenticated user's identity."""
    return api_get(access_token, "/api/v1/me")


def submit_text_post(access_token, subreddit, title, text):
    """Submit a text post. Called explicitly, never on a schedule (yet)."""
    return api_post(
        access_token,
        "/api/submit",
        {
            "sr": subreddit,
            "kind": "self",
            "title": title,
            "text": text,
            "resubmit": False,
        },
    )


def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env first.")
        sys.exit(1)

    url = build_authorize_url()
    print("Open this URL, approve, then paste the code from the redirect:")
    print(url)
    print()
    try:
        webbrowser.open(url)
    except Exception:
        pass

    code = input("code: ").strip()
    tokens = exchange_code(code)
    print("Access token acquired. Refresh token:")
    print(tokens.get("refresh_token", "(none returned)"))

    me = get_identity(tokens["access_token"])
    print("Authenticated as:", me.get("name"))


if __name__ == "__main__":
    main()
