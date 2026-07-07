---
name: sa-lead-gen
description: Use when the user wants to process raw lead captures into scored lead files and draft outreach messages for the AI consulting business in South Africa.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [lead-gen, consulting, south-africa, outreach]
    related_skills: [obsidian-capture]
---

# SA Lead Generation System

Processes raw lead notes into scored lead files and draft outreach messages for Thaby's AI consulting offer ladder.

## Offer ladder

1. Free 15-min assessment → one bottleneck, one off-the-shelf AI tool
2. $1,000 paid assessment → full AI-built report
3. $2,000/month AI Concierge → 2x 45-min calls + Voxer support, capped at 6 clients

## Discovery question

"If you could wave a magic wand, what one thing in your business would you fix?"

## How leads enter the system

Drop a note in `00-Inbox/` starting with `lead:` or use the WhatsApp capture format.

Capture format examples:

- `lead: Sipho Nkosi, plumbing business in Durban, drowning in quote emails and late invoices, found via Small Business SA Facebook group, contact: sipho@example.com`
- Or with explicit fields:
  ```
  lead:
  name: Sipho Nkosi
  business: plumbing business in Durban
  bottleneck: drowning in quote emails and late invoices
  source: Small Business SA Facebook group
  contact: sipho@example.com
  ```

## Processing

Script: `/home/chomi/.hermes/scripts/lead-gen-tender.py`
Schedule: daily at 9am SAST

It does:
1. Reads `lead:` notes from `00-Inbox/`
2. Extracts name, business, bottleneck, source, contact
3. Scores fit (Low/Medium/High)
4. Creates a lead file in `05-Leads/`
5. Drafts an outreach message in `06-Resources/Outreach-Drafts/`
6. Moves the raw inbox note to `90-Archive/Inbox-Processed/`

## Scoring signals

- operations/admin pain (+3)
- decision maker language (+2)
- specific bottleneck (+2)
- efficiency / effectiveness / quality pain (+1 each)
- contact info present (+1)

Fit:
- High: 6+
- Medium: 3-5
- Low: 0-2

## Outreach draft

- High/Medium fit: personalized free assessment offer with discovery question
- Low fit: softer intro offer

## Rules

- All outreach is a draft. Thaby must approve before sending.
- Do not scrape Facebook or LinkedIn directly (ToS risk). Use manual captures from groups, job boards, referrals, or saved posts.
- Update `Leads MOC` weekly.
- Cap concierge at 6 clients. Track active count in `04-Clients/Active/`.
