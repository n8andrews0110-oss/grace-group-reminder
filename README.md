# Grace Group Daily Reading Reminder

Texts your group every morning with that day's reading from
`reading_schedule.csv` and a link to it on Bible Gateway (ESV). Runs
automatically on GitHub Actions — no server, no laptop that has to stay on.

**Important note on "group text":** there's no public API for posting into
a real iMessage/SMS group thread (that's closed off by Apple/carriers).
This sends the same text individually to each person's number, so everyone
gets it as a text from the same number at the same moment — it just won't
show replies to each other the way a native group thread does. If that
matters to you, say the word and this can be swapped to a platform with a
real group API (GroupMe, Discord, etc.) instead.

## One-time setup

### 1. Create a Twilio account and phone number
1. Sign up at [twilio.com](https://www.twilio.com) (free trial available).
2. Buy an SMS-capable phone number (Console → Phone Numbers → Buy a number).
3. From the Console dashboard, copy your **Account SID** and **Auth Token**.
4. **Trial accounts** can only text numbers you've manually verified in the
   Twilio console (Console → Verified Caller IDs) — fine for testing with a
   few people. To text anyone without pre-verifying them, you'll need to
   upgrade to a paid account (a few dollars covers a small group for months
   at typical SMS rates).
5. For a US number sending regularly, Twilio will prompt you to register for
   **A2P 10DLC** (a carrier requirement for app-to-person texting) — it's a
   quick self-serve form in the Console and avoids messages getting filtered
   as spam.

### 2. Put this code in a GitHub repo
Create a new repo and push everything in this folder to it, keeping the
`.github/workflows/` folder path exactly as-is (that's what GitHub reads to
find the schedule).

### 3. Add your secrets
In the repo: **Settings → Secrets and variables → Actions → New repository
secret**. Add these four:

| Secret name | Value |
|---|---|
| `TWILIO_ACCOUNT_SID` | from the Twilio Console |
| `TWILIO_AUTH_TOKEN` | from the Twilio Console |
| `TWILIO_FROM_NUMBER` | your Twilio number, e.g. `+19045551234` |
| `GROUP_PHONE_NUMBERS` | comma-separated numbers, e.g. `+19045551111,+19045552222,+19045553333` |

Phone numbers must be in E.164 format (`+1` + area code + number, no
dashes/spaces).

### 4. Test it
Go to the **Actions** tab → **Daily Bible Reading Reminder** → **Run
workflow** → check the **force** box → **Run workflow**. This sends
immediately regardless of the time of day, so you can confirm everyone
receives it before trusting the schedule.

### 5. Let it run
That's it. The workflow is scheduled to check in every hour and only
actually sends once a day, around **6:00 AM Eastern** by default.

## Adjusting things later

- **Change the send time:** edit `SEND_HOUR` in
  `.github/workflows/daily-reminder.yml` (24-hour clock, e.g. `7` for
  7:00 AM). No need to touch anything else — daylight saving is handled
  automatically since the check is done in local time, not UTC.
- **Add/remove people:** edit the `GROUP_PHONE_NUMBERS` secret. No code
  changes.
- **New season's reading plan:** once the current plan ends (Dec 22, 2026),
  replace `reading_schedule.csv` with the new one — same four columns
  (`date,day,reading,meditation`, plus `special` for any non-passage days
  like your preaching-passage Sundays). The script itself never needs to
  change.
- **Different timezone:** edit `TIMEZONE` in the workflow file (any
  [IANA timezone name](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones),
  e.g. `America/Chicago`).

## Running/testing locally (optional)

```bash
pip install -r requirements.txt
export TWILIO_ACCOUNT_SID=xxxx
export TWILIO_AUTH_TOKEN=xxxx
export TWILIO_FROM_NUMBER=+19045551234
export GROUP_PHONE_NUMBERS=+19045550000
export FORCE_SEND=true
python send_reminder.py
```
