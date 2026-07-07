#!/usr/bin/env python3
"""
obsidian-tender.py

Tends to the Thaby-Systems Obsidian vault on schedule:
1. Creates daily note from template
2. Reviews Inbox and suggests moves
3. Updates MOCs
"""

import os
import re
import datetime
from pathlib import Path

VAULT = Path("/mnt/c/Users/batha/Documents/Thaby-Systems")
SAST = datetime.timezone(datetime.timedelta(hours=2))


def today() -> str:
    return datetime.datetime.now(SAST).strftime("%Y-%m-%d")


def now_short() -> str:
    return datetime.datetime.now(SAST).strftime("%Y-%m-%d %H%M")


def create_daily_note():
    template = VAULT / "01-Daily-Logs/YYYY-MM-DD - Daily Log Template.md"
    target = VAULT / f"01-Daily-Logs/{today()} - Daily Log.md"

    if target.exists():
        return f"Daily note already exists: {target}"

    body = template.read_text() if template.exists() else "# Daily Log\n\n"
    body = body.replace("{{date:YYYY-MM-DD}}", today())
    target.write_text(body)
    return f"Created daily note: {target}"


def review_inbox():
    inbox = VAULT / "00-Inbox"
    files = [f for f in inbox.iterdir() if f.is_file() and f.name not in ("README.md", "Quick Capture Workflow.md")]

    if not files:
        return "Inbox is empty. Nothing to review."

    lines = [f"## Inbox Review — {today()}\n\n"]
    for f in sorted(files):
        content = f.read_text(errors="ignore")
        first_line = content.splitlines()[0] if content else "(empty)"
        lines.append(f"- [[{f.name.replace('.md', '')}]] — {first_line[:80]}\n")

    lines.append("\n---\n\n**Suggested next actions:**\n")
    lines.append("- Move `decision:` notes to `02-Decisions/`\n")
    lines.append("- Move `lead:` notes to `05-Leads/`\n")
    lines.append("- Move `client:` notes to `04-Clients/`\n")
    lines.append("- Move anything else to the right project folder or archive\n")

    review_file = VAULT / f"01-Daily-Logs/{today()} - Inbox Review.md"
    review_file.write_text("".join(lines))
    return f"Inbox has {len(files)} item(s). Review saved to: {review_file}"


def update_mocs():
    # Update Decisions MOC with any new decision notes
    decisions_dir = VAULT / "02-Decisions"
    decisions = sorted([f for f in decisions_dir.iterdir() if f.is_file() and f.name.endswith(".md") and f.name != "Decisions MOC.md" and f.name != "Decision Note Template.md"])

    lines = ["# Decisions MOC\n\nPermanent decisions. Format: `YYYY-MM-DD - Decision name`.\n\n"]
    for f in decisions:
        name = f.name.replace(".md", "")
        lines.append(f"- [[{name}]]\n")

    moc = VAULT / "02-Decisions/Decisions MOC.md"
    moc.write_text("".join(lines))

    # Update Leads MOC with any new lead notes
    leads_dir = VAULT / "05-Leads"
    leads = sorted([f for f in leads_dir.iterdir() if f.is_file() and f.name.endswith(".md") and f.name != "Leads MOC.md" and f.name != "Lead Note Template.md"])

    lead_lines = ["# Leads MOC\n\nTrack prospects for AI consulting offers.\n\n## Status stages\n\n- New\n- Qualified\n- Free assessment booked\n- Free assessment done\n- Paid assessment offered\n- Paid assessment closed\n- Concierge enrolled\n- Lost / nurture\n\n## Source list\n\n- Facebook groups\n- LinkedIn\n- Referrals\n- Warm outreach\n\n## Leads\n\n"]
    for f in leads:
        name = f.name.replace(".md", "")
        lead_lines.append(f"- [[{name}]]\n")

    leads_moc = VAULT / "05-Leads/Leads MOC.md"
    leads_moc.write_text("".join(lead_lines))

    return f"Updated MOCs: {len(decisions)} decision(s), {len(leads)} lead(s)"


def main():
    import sys
    # Cron passes args from prompt as positional; support both argv styles
    task = "all"
    if len(sys.argv) > 1:
        task = sys.argv[1]

    results = []
    if task in ("daily", "all"):
        results.append(create_daily_note())
    if task in ("inbox", "all"):
        results.append(review_inbox())
    if task in ("mocs", "all"):
        results.append(update_mocs())

    print("\n".join(results))


if __name__ == "__main__":
    main()
