#!/usr/bin/env python3
"""
obsidian-catch-up.py

Runs at WSL boot. Checks missed cron jobs and executes them.
Designed for solar/nighttime shutdown setups where the machine is off overnight.
"""

import os
import json
import datetime
import subprocess
from pathlib import Path

SAST = datetime.timezone(datetime.timedelta(hours=2))
STATE_FILE = Path("/home/chomi/.hermes/scripts/obsidian-catch-up-state.json")

# Job definitions: name, cron schedule, script to run if missed
JOBS = [
    {
        "name": "Obsidian Daily Note",
        "schedule": "0 6 * * *",
        "script": "/home/chomi/.hermes/scripts/obsidian-daily.sh",
    },
    {
        "name": "Lead Gen Processor",
        "schedule": "0 9 * * *",
        "script": "/home/chomi/.hermes/scripts/lead-gen.sh",
    },
    {
        "name": "Obsidian Inbox Review",
        "schedule": "0 20 * * *",
        "script": "/home/chomi/.hermes/scripts/obsidian-inbox.sh",
    },
    {
        "name": "Obsidian Weekly MOC Update",
        "schedule": "0 19 * * 0",
        "script": "/home/chomi/.hermes/scripts/obsidian-mocs.sh",
    },
]


def parse_cron(schedule: str, after: datetime.datetime, before: datetime.datetime):
    """Return datetimes a cron schedule would have fired between after and before."""
    minute, hour, dom, month, dow = schedule.split()
    # Simplify: only supports exact minute and hour, wildcard or specific for dom/month/dow
    if minute != "*":
        minute = int(minute)
    if hour != "*":
        hour = int(hour)

    matches = []
    current = after.replace(second=0, microsecond=0)
    # Walk hour by hour from after to before
    while current <= before:
        if hour == "*" or current.hour == hour:
            if minute == "*" or current.minute == minute:
                # Check dom, month, dow if specific
                if dom != "*" and current.day != int(dom):
                    pass
                elif month != "*" and current.month != int(month):
                    pass
                elif dow != "*" and current.weekday() != int(dow):
                    pass
                else:
                    matches.append(current)
        current += datetime.timedelta(minutes=1)
    return matches


def now_sast() -> datetime.datetime:
    return datetime.datetime.now(SAST)


def load_last_run() -> datetime.datetime:
    if not STATE_FILE.exists():
        # First run ever: assume yesterday 6am so we don't flood
        return now_sast() - datetime.timedelta(days=1, hours=6)
    data = json.loads(STATE_FILE.read_text())
    return datetime.datetime.fromisoformat(data["last_run"])


def save_last_run(dt: datetime.datetime):
    STATE_FILE.write_text(json.dumps({"last_run": dt.isoformat()}))


def run_script(script: str) -> str:
    try:
        result = subprocess.run([script], capture_output=True, text=True, timeout=120)
        output = result.stdout.strip() or "(no output)"
        if result.returncode != 0:
            output += f"\n[ERROR {result.returncode}] {result.stderr.strip()}"
        return output
    except Exception as e:
        return f"[EXCEPTION] {e}"


def main():
    now = now_sast()
    last_run = load_last_run()

    if now - last_run < datetime.timedelta(minutes=5):
        # Prevent rapid restarts from flooding
        print("Catch-up ran recently. Skipping.")
        return

    print(f"Catch-up: last run {last_run}, now {now}")

    results = []
    for job in JOBS:
        matches = parse_cron(job["schedule"], last_run, now)
        if matches:
            # Run once if any matches in window
            output = run_script(job["script"])
            results.append(f"✅ {job['name']} (missed {len(matches)} time(s))\n{output}")
        else:
            results.append(f"⏭️ {job['name']} — nothing missed")

    save_last_run(now)

    summary = f"# Obsidian Catch-Up Summary\n\nLast run: {last_run.strftime('%Y-%m-%d %H:%M')}\nNow: {now.strftime('%Y-%m-%d %H:%M')}\n\n## Jobs run\n\n"
    summary += "\n\n".join(results)

    # Write a summary note to the vault
    vault_dir = Path("/mnt/c/Users/batha/Documents/Thaby-Systems/01-Daily-Logs")
    vault_dir.mkdir(parents=True, exist_ok=True)
    summary_file = vault_dir / f"{now.strftime('%Y-%m-%d')} - Catch-Up.md"
    summary_file.write_text(summary)

    print(summary)


if __name__ == "__main__":
    main()
