#!/usr/bin/env python3
"""Simple Gmail automation CLI for sending emails and summarizing unread inbox items."""

from __future__ import annotations

import argparse
import base64
import os
import sys
from email.message import EmailMessage
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import List, Sequence

import requests
from dotenv import load_dotenv

try:  # shared humanizer module
    from humanizer import humanize_email
except ImportError:  # package-style invocation
    from .humanizer import humanize_email  # type: ignore
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]

PROJECT_DIR = Path(__file__).resolve().parent
ROOT_DIR = PROJECT_DIR.parent
load_dotenv(ROOT_DIR / ".env", override=False)

_env_credentials = os.getenv("GOOGLE_CLIENT_SECRET_PATH")
if _env_credentials:
    candidate = Path(_env_credentials)
    if not candidate.is_absolute():
        candidate = ROOT_DIR / candidate
else:
    candidate = PROJECT_DIR / "credentials" / "client_secret.json"
DEFAULT_CREDENTIALS_PATH = candidate
TOKEN_PATH = PROJECT_DIR / "credentials" / "token.json"


def get_credentials(credentials_path: Path = DEFAULT_CREDENTIALS_PATH) -> Credentials:
    if not credentials_path.exists():
        raise FileNotFoundError(
            f"Missing Google client secret at {credentials_path}. Update GOOGLE_CLIENT_SECRET_PATH or place the file there."
        )

    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            print("Follow the Google OAuth prompt to authorize access…", file=sys.stderr)
            auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
            print(f"\nOpen this URL in your browser to authorize Gmail access:\n{auth_url}\n")
            code = input("Paste the authorization code here: ").strip()
            flow.fetch_token(code=code)
            creds = flow.credentials
        TOKEN_PATH.write_text(creds.to_json())

    return creds


def build_service(creds: Credentials):
    return build("gmail", "v1", credentials=creds)


def capture_multiline(prompt: str) -> str:
    print(prompt)
    print("Enter a blank line when you are done.\n")
    lines: List[str] = []
    try:
        while True:
            line = input()
            if not line.strip():
                break
            lines.append(line)
    except EOFError:
        pass
    return "\n".join(lines).strip()


def prompt_recipients(initial: Sequence[str] | None = None) -> List[str]:
    if initial:
        return list(initial)
    raw = input("Recipients (comma-separated): ")
    return [addr.strip() for addr in raw.split(",") if addr.strip()]


def send_email(service, recipients: Sequence[str], subject: str, body: str):
    if not recipients:
        raise ValueError("At least one recipient is required.")

    message = EmailMessage()
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject
    message.set_content(body)

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": encoded_message}).execute()


def extract_header(headers, name: str) -> str:
    name = name.lower()
    for header in headers:
        if header.get("name", "").lower() == name:
            return header.get("value", "")
    return ""


def fetch_unread_messages(service, limit: int):
    response = (
        service.users()
        .messages()
        .list(userId="me", labelIds=["UNREAD"], maxResults=limit)
        .execute()
    )
    message_ids = [m["id"] for m in response.get("messages", [])]
    messages = []
    for message_id in message_ids:
        msg = service.users().messages().get(userId="me", id=message_id, format="metadata").execute()
        messages.append(msg)
    return messages


def summarize_message(msg):
    headers = msg.get("payload", {}).get("headers", [])
    subject = extract_header(headers, "Subject") or "(no subject)"
    sender = extract_header(headers, "From") or "(unknown sender)"
    date_header = extract_header(headers, "Date")
    if date_header:
        try:
            dt = parsedate_to_datetime(date_header)
            timestamp = dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            timestamp = date_header
    else:
        timestamp = "(no date)"
    snippet = (msg.get("snippet") or "").strip().replace("\n", " ")
    if len(snippet) > 220:
        snippet = snippet[:217].rstrip() + "…"
    return {
        "id": msg.get("id"),
        "subject": subject,
        "sender": sender,
        "timestamp": timestamp,
        "snippet": snippet or "(no preview available)",
    }


def format_summary(messages):
    if not messages:
        return "No unread emails right now."
    lines = [f"Inbox digest – {len(messages)} unread", ""]
    for idx, msg in enumerate(messages, start=1):
        lines.append(f"{idx}. {msg['subject']} — {msg['sender']} ({msg['timestamp']})")
        lines.append(f"    {msg['snippet']}")
    return "\n".join(lines)


def post_to_discord(summary_text: str):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("DISCORD_WEBHOOK_URL is not set; printing summary locally instead.")
        print(summary_text)
        return
    response = requests.post(webhook_url, json={"content": summary_text}, timeout=10)
    response.raise_for_status()


def mark_messages_read(service, message_ids):
    for message_id in message_ids:
        service.users().messages().modify(
            userId="me",
            id=message_id,
            body={"removeLabelIds": ["UNREAD"]},
        ).execute()


def handle_send(args):
    creds = get_credentials()
    service = build_service(creds)
    recipients = prompt_recipients(args.to)
    subject = args.subject or input("Subject: ")
    body = args.body or capture_multiline("Message body:")

    default_detail = os.getenv("EMAIL_DEFAULT_DETAIL", "Dallas")
    metadata = {"detail": args.detail or default_detail}
    if not args.raw:
        body = humanize_email(body, level=args.humanize_level, metadata=metadata)

    send_email(service, recipients, subject, body)
    print("Email sent.")


def handle_summarize(args):
    creds = get_credentials()
    service = build_service(creds)
    raw_messages = fetch_unread_messages(service, args.max)
    summaries = [summarize_message(msg) for msg in raw_messages]
    summary_text = format_summary(summaries)
    print(summary_text)
    try:
        post_to_discord(summary_text)
        print("Posted summary to Discord webhook.")
    except requests.HTTPError as exc:
        print(f"Failed to post summary: {exc}")
    if args.mark_read and summaries:
        mark_messages_read(service, [m["id"] for m in raw_messages])
        print("Marked messages as read.")


def build_parser():
    parser = argparse.ArgumentParser(description="Gmail automation CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    send_parser = subparsers.add_parser("send", help="Send an email via Gmail")
    send_parser.add_argument("--to", nargs="+", help="Recipients (space-separated). Skip to get prompted.")
    send_parser.add_argument("--subject", help="Optional subject (prompted if omitted).")
    send_parser.add_argument("--body", help="Optional one-line body (prompted for multiline if omitted).")
    send_parser.add_argument(
        "--detail",
        help="Location or context detail to weave into the email (defaults to Dallas unless EMAIL_DEFAULT_DETAIL is set).",
    )
    send_parser.add_argument(
        "--humanize-level",
        type=int,
        default=2,
        help="0-3, how loose/conversational the humanizer should go (default 2).",
    )
    send_parser.add_argument(
        "--raw",
        action="store_true",
        help="Skip the automatic humanizer pass and send the text exactly as typed.",
    )
    send_parser.set_defaults(func=handle_send)

    summary_parser = subparsers.add_parser("summarize", help="Summarize unread Gmail messages")
    summary_parser.add_argument("--max", type=int, default=10, help="Maximum unread messages to scan (default 10).")
    summary_parser.add_argument(
        "--mark-read",
        action="store_true",
        help="Mark the summarized messages as read after posting.",
    )
    summary_parser.set_defaults(func=handle_summarize)

    return parser


def main(argv: List[str] | None = None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
