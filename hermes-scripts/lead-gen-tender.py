#!/usr/bin/env python3
"""
lead-gen-tender.py

Reads raw lead intake notes from Obsidian vault, scores them, drafts outreach,
and writes ready-for-review messages back to the vault.
"""

import os
import re
import json
import datetime
from pathlib import Path

VAULT = Path("/mnt/c/Users/batha/Documents/Thaby-Systems")
LEADS_DIR = VAULT / "05-Leads"
INBOX_DIR = VAULT / "00-Inbox"
OUTREACH_DIR = VAULT / "06-Resources" / "Outreach-Drafts"

SAST = datetime.timezone(datetime.timedelta(hours=2))


def today() -> str:
    return datetime.datetime.now(SAST).strftime("%Y-%m-%d")


def parse_inbox_leads():
    """Find raw lead: notes in inbox and convert them to lead files."""
    raw = []
    if not INBOX_DIR.exists():
        return raw

    for f in INBOX_DIR.iterdir():
        if not f.is_file() or not f.name.endswith(".md"):
            continue
        content = f.read_text(errors="ignore")
        if content.lower().startswith("lead:") or "lead:" in content.lower()[:100]:
            raw.append((f, content))
    return raw


def extract_lead_info(content: str) -> dict:
    """Extract structured info from a lead note."""
    lines = content.splitlines()
    text = "\n".join(lines[1:]) if lines else content

    name = "Unknown"
    business = ""
    bottleneck = ""
    source = ""
    contact = ""

    # First, try explicit field labels anywhere in the text
    labeled = {
        "name": "",
        "business": "",
        "bottleneck": "",
        "source": "",
        "contact": "",
    }
    for line in lines:
        lower = line.lower()
        for key in labeled.keys():
            if lower.startswith(f"{key}:"):
                labeled[key] = line.split(":", 1)[-1].strip()

    # If explicit labels are present, use them
    if any(labeled.values()):
        name = labeled["name"] or name
        business = labeled["business"]
        bottleneck = labeled["bottleneck"]
        source = labeled["source"]
        contact = labeled["contact"]
    else:
        # Parse comma-separated natural language capture: lead: Name, business, bottleneck, found via source, contact: email
        first = lines[0] if lines else ""
        if first.lower().startswith("lead:"):
            rest = first[5:].strip()

            # Extract contact: ... at the end
            contact_match = re.search(r"contact[:\s]+([^,]+(?:\s+[^,]+)?)(?:\s*$|,\s*$)", rest, re.IGNORECASE)
            if contact_match:
                contact = contact_match.group(1).strip()
                rest = rest[:contact_match.start()].strip()

            # Extract source: found via / from / source
            source_match = re.search(r"(?:found\s+via|source|from)[:\s]+(.+?)(?:\s*,\s*contact|$)", rest, re.IGNORECASE)
            if source_match:
                source = source_match.group(1).strip().rstrip(",")
                rest = rest[:source_match.start()].strip()

            # Now split the remainder by commas
            parts = [p.strip() for p in rest.split(",")]
            if len(parts) >= 3:
                name = parts[0]
                business = parts[1]
                bottleneck = ", ".join(parts[2:])
            elif len(parts) == 2:
                name = parts[0]
                business = parts[1]
            elif len(parts) == 1:
                name = parts[0]

    # If name is a long phrase, try to shorten it to first 2-3 words
    name_parts = name.split()
    if len(name_parts) > 3 and not any(title in name.lower() for title in ["mr", "mrs", "ms", "dr"]):
        # Heuristic: if it looks like "name + business" without comma, split on business keywords
        if " business" in name.lower() or " company" in name.lower() or " in " in name.lower():
            # leave as is, it's likely a business
            pass
        else:
            name = " ".join(name_parts[:2])

    return {
        "name": name,
        "business": business,
        "bottleneck": bottleneck,
        "source": source,
        "contact": contact,
        "raw": content,
    }


def score_lead(lead: dict) -> dict:
    """Score the lead for fit."""
    score = 0
    signals = []

    raw = lead["raw"].lower()
    bottleneck = lead["bottleneck"].lower()

    # Hiring / admin / ops signals
    if any(k in raw for k in ["hiring", "assistant", "admin", "operations", "ops", "team", "staff"]):
        score += 3
        signals.append("operations/admin pain")

    # Business owner / decision maker
    if any(k in raw for k in ["owner", "founder", "director", "ceo", "manager"]):
        score += 2
        signals.append("decision maker language")

    # Specific bottleneck mentioned
    if bottleneck and len(bottleneck) > 10:
        score += 2
        signals.append("specific bottleneck")

    # Time / money / quality language
    if any(k in raw for k in ["time", "hours", "wasting", "slow", "manual", "too much"]):
        score += 1
        signals.append("efficiency pain")
    if any(k in raw for k in ["money", "revenue", "sales", "leads", "customers", "growth"]):
        score += 1
        signals.append("effectiveness pain")
    if any(k in raw for k in ["quality", "mistakes", "errors", "rework", "complaints"]):
        score += 1
        signals.append("quality pain")

    # Contact info present
    if lead["contact"]:
        score += 1
        signals.append("contact info present")

    if score >= 6:
        fit = "High"
    elif score >= 3:
        fit = "Medium"
    else:
        fit = "Low"

    return {"score": score, "fit": fit, "signals": signals}


def draft_outreach(lead: dict, score: dict) -> str:
    """Draft a free assessment outreach message."""
    name = lead["name"].split()[0] if lead["name"] != "Unknown" else "there"
    business = lead["business"] or "your business"
    bottleneck = lead["bottleneck"] or "bottleneck"

    body = f"""Hi {name},

I saw your post about {bottleneck} at {business}. 

I help South African business owners fix one bottleneck with AI in a free 15-minute assessment. No pitch, just a practical tool you can use the same day.

If you could wave a magic wand, what one thing in {business} would you fix?

Happy to jump on a quick call if you want a second pair of eyes.

Thaby
"""

    if score["fit"] == "Low":
        body = f"""Hi {name},

I came across {business} and thought I'd reach out. I help small businesses in SA save time with AI tools.

Would you be open to a free 15-minute assessment where I find one quick win in your ops?

Thaby
"""

    return body


def process_leads():
    raw_leads = parse_inbox_leads()
    if not raw_leads:
        return "No new lead: notes found in Inbox."

    OUTREACH_DIR.mkdir(parents=True, exist_ok=True)

    results = []
    for f, content in raw_leads:
        lead = extract_lead_info(content)
        score = score_lead(lead)
        outreach = draft_outreach(lead, score)

        # Create lead file
        safe_name = re.sub(r"[^\w\-]", "-", lead["name"].lower()).strip("-")
        lead_file = LEADS_DIR / f"Lead - {safe_name}.md"

        # If exists, append number
        counter = 1
        original_lead_file = lead_file
        while lead_file.exists():
            lead_file = LEADS_DIR / f"Lead - {safe_name}-{counter}.md"
            counter += 1

        lead_body = f"""---
tags: [lead]
status: New
fit: {score["fit"]}
score: {score["score"]}
source: {lead["source"] or "Inbox"}
contact: {lead["contact"]}
---

# Lead - {lead["name"]}

**Business:** {lead["business"] or "Unknown"}
**Contact:** {lead["contact"] or "Unknown"}
**Source:** {lead["source"] or "Inbox"}
**Status:** New
**Fit:** {score["fit"]} ({score["score"]}/10)
**Signals:** {", ".join(score["signals"]) or "None"}

## Bottleneck

{lead["bottleneck"] or "Not specified"}

## Raw capture

{lead["raw"]}

## Next action

- Draft outreach message below
- Get Thaby approval before sending
- Book free assessment if interested

## Conversation history

- {today()} - Initial capture
"""
        lead_file.write_text(lead_body)

        # Draft outreach file
        draft_file = OUTREACH_DIR / f"{today()} - {safe_name} - outreach.md"
        draft_counter = 1
        original_draft_file = draft_file
        while draft_file.exists():
            draft_file = OUTREACH_DIR / f"{today()} - {safe_name}-{draft_counter} - outreach.md"
            draft_counter += 1

        draft_body = f"""# Outreach Draft - {lead["name"]}

**Lead file:** [[{lead_file.name.replace(".md", "")}]]
**Fit:** {score["fit"]} ({score["score"]}/10)
**Status:** Draft — awaiting Thaby approval

---

{outreach}

---

## Notes for Thaby

- This is a draft. Do not send until approved.
- If fit is Low, consider a softer intro or no outreach.
- If High, prioritize booking the free assessment.
"""
        draft_file.write_text(draft_body)

        # Optionally move the raw inbox file to archive
        archive_dir = VAULT / "90-Archive" / "Inbox-Processed"
        archive_dir.mkdir(parents=True, exist_ok=True)
        archive_file = archive_dir / f"{today()} - {f.name}"
        f.rename(archive_file)

        results.append(f"Processed: {lead['name']} ({score['fit']}) → {lead_file.name} + {draft_file.name}")

    return "\n".join(results)


def main():
    print(process_leads())


if __name__ == "__main__":
    main()
