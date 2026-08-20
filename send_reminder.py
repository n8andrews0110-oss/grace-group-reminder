#!/usr/bin/env python3
"""
Grace Group daily Bible reading reminder.

Looks up today's date in reading_schedule.csv and texts each group member
a reminder with a link to that day's passage (Bible Gateway, ESV).

Meant to run on a schedule -- see .github/workflows/daily-reminder.yml.
It's safe (and intended) to run this every hour: it only actually sends
a text during the configured SEND_HOUR in the configured TIMEZONE, so it
keeps sending at the right local time through daylight saving changes
without anyone needing to touch the code or the workflow.

When the current reading plan ends (Dec 22, 2026), just replace
reading_schedule.csv with next season's schedule -- nothing else changes.
"""

import csv
import os
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo

from twilio.rest import Client

SCHEDULE_FILE = Path(__file__).parent / "reading_schedule.csv"
LIVESTREAM_URL = "https://faith-pca.org/livestream/"


def load_schedule() -> dict:
    with open(SCHEDULE_FILE, newline="", encoding="utf-8") as f:
        return {row["date"]: row for row in csv.DictReader(f)}


def bible_gateway_link(passage: str) -> str:
    """Build a link to the passage on Bible Gateway (ESV). We only ever
    link to the verse -- we never copy the verse text itself, so there's
    no copyright concern with the translation being licensed."""
    return f"https://www.biblegateway.com/passage/?search={quote(passage)}&version=ESV"


def build_message(row: dict) -> str:
    day_label = f"{row['day']} {row['date'][5:].replace('-', '/')}"

    if row.get("special") == "preaching_sunday":
        return (
            f"\U0001F4D6 Grace Group -- {day_label}\n"
            f"Today: read the preaching passage ahead of the service.\n"
            f"{LIVESTREAM_URL}"
        )

    reading = row["reading"]
    meditation = row["meditation"]
    link = bible_gateway_link(reading)

    lines = [
        f"\U0001F4D6 Grace Group -- {day_label}",
        f"Today's reading: {reading}",
    ]
    if meditation and meditation != reading:
        lines.append(f"Meditate on: {meditation}")
    lines.append(link)
    if row["day"] == "Wed":
        lines.append("\U0001F55B Grace Group meets today!")

    return "\n".join(lines)


def should_send_now(timezone: str, send_hour: int) -> bool:
    if os.environ.get("FORCE_SEND", "").lower() in ("1", "true", "yes"):
        print("FORCE_SEND set -- bypassing hour check.")
        return True
    now_local = datetime.now(ZoneInfo(timezone))
    return now_local.hour == send_hour


def get_recipients() -> list:
    raw = os.environ.get("GROUP_PHONE_NUMBERS", "")
    numbers = [n.strip() for n in raw.split(",") if n.strip()]
    if not numbers:
        print("No recipients configured in GROUP_PHONE_NUMBERS -- nothing to send.")
    return numbers


def send_text(client: Client, from_number: str, to_number: str, body: str) -> None:
    try:
        client.messages.create(to=to_number, from_=from_number, body=body)
        print(f"Sent to {to_number}")
    except Exception as exc:
        print(f"FAILED to send to {to_number}: {exc}", file=sys.stderr)


def main() -> None:
    timezone = os.environ.get("TIMEZONE", "America/New_York")
    send_hour = int(os.environ.get("SEND_HOUR", "6"))

    if not should_send_now(timezone, send_hour):
        print(f"Not send hour ({send_hour}:00 {timezone} local) -- exiting without sending.")
        return

    today = datetime.now(ZoneInfo(timezone)).strftime("%Y-%m-%d")
    schedule = load_schedule()
    row = schedule.get(today)

    if row is None:
        print(f"No reading scheduled for {today}. "
              f"The plan may have ended -- drop in a new reading_schedule.csv when the next one starts.")
        return

    message = build_message(row)
    print("Message to send:\n" + message)

    recipients = get_recipients()
    if not recipients:
        return

    client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
    from_number = os.environ["TWILIO_FROM_NUMBER"]

    for number in recipients:
        send_text(client, from_number, number, message)


if __name__ == "__main__":
    main()
