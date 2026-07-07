---
name: obsidian-capture
description: Use when the user wants to save a note, decision, lead, log, or client update to the Obsidian vault at /mnt/c/Users/batha/Documents/Thaby-Systems. Parse the WhatsApp quick-capture prefix, write the file, and confirm the location.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [obsidian, note-taking, capture, productivity]
    related_skills: []
---

# Obsidian Quick Capture

Capture notes from WhatsApp into the `Thaby-Systems` Obsidian vault.

## Vault location

`/mnt/c/Users/batha/Documents/Thaby-Systems`

## Capture prefixes

| Prefix | Filing | Filename pattern |
|--------|--------|------------------|
| `note:` | `00-Inbox/` | `YYYY-MM-DD HHMM - note.md` |
| `decision:` | `02-Decisions/` | `YYYY-MM-DD - decision title.md` |
| `lead:` | `05-Leads/` | `Lead - name - business.md` |
| `log:` | `01-Daily-Logs/` | `YYYY-MM-DD - Daily Log.md` (append) |
| `client:` | `04-Clients/Active/` or `04-Clients/Prospects/` | `Client - name.md` |

## Workflow

1. Parse the prefix and the rest of the message.
2. Determine the target folder and filename.
3. If the note is short, write it as the file body. If detailed, structure it with frontmatter and sections.
4. For `decision:` notes, link them in `02-Decisions/Decisions MOC.md` if a new decision is finalized.
5. Confirm to the user: file path + a one-line summary of what was saved.

## Filename rules

- Use today's date in SAST (Africa/Johannesburg).
- Sanitize names: replace spaces with hyphens, strip special characters, keep ASCII alphanumerics.
- If a file already exists, append rather than overwrite, or create a uniquely numbered variant.

## Body format

For a lead note:
```markdown
---
tags: [lead]
status: New
source: <source>
contact: <contact>
---

# Lead - <Name>

**Business:** <business>
**Contact:** <contact>
**Source:** <source>
**Status:** New
**Bottleneck:** <bottleneck>
**Offer fit:** <free/paid/concierge/ala-carte>

## Notes

- <message>

## Next action

- <next action>

## Conversation history

- YYYY-MM-DD - Initial capture
```

For a decision note:
```markdown
---
tags: [decision]
date: YYYY-MM-DD
status: Decided
---

# YYYY-MM-DD - <Decision title>

**Status:** Decided
**Date:** YYYY-MM-DD
**Stakeholders:** Thaby

## Options

1. <option 1>
2. <option 2>

## Decision

<final decision>

## Reason

<reason>

## Consequences

<consequences>
```

For a daily log entry, append to `01-Daily-Logs/YYYY-MM-DD - Daily Log.md` under the relevant section. If the file does not exist, create it from the template.

## Common pitfalls

- Never overwrite existing files. Append or create a variant.
- Always confirm the saved path to the user.
- Don't guess contact details; use what was provided or leave blank.
- If the prefix is missing, ask the user which category the note belongs to.

## Verification

- [ ] File written successfully.
- [ ] File path confirmed in the reply.
- [ ] MOC updated when a new decision or lead is finalized.
