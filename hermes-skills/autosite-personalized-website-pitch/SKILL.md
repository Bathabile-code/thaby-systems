---
name: autosite-personalized-website-pitch
description: AutoSite lead branding → personalized site + WhatsApp pitch.
version: 1.0.0
author: anish
---

# AutoSite SA — Personalized Website + WhatsApp Pitch

The AutoSite play: take a WhatsApp-ready lead (a local SA service business that publishes a
mobile/WhatsApp number), pull its branding and voice so the website we build **sounds like
them**, then pitch it on WhatsApp. Personalisation is the whole hook — a generic site doesn't
convert, a site that mirrors their own language and identity does.

## When to use

A WhatsApp-ready AutoSite lead (from `autosite-sa/leads/whatsapp-leads.json` or a new
candidate) needs a personalized website built from its real branding, plus a WhatsApp pitch
offering it. See also `sa-lead-gen` (discovery) and `whatsapp-verify` (mobile verification).

## ⚠️ GATE — only for businesses WITHOUT a website (check FIRST, non-negotiable)

The "we built you a free website" pitch ONLY works for a business that has **no website at
all, or a clearly outdated/broken one**. This is the whole point of AutoSite — build a site
for businesses who aren't online yet.

**Before anything else, check whether the lead already has a website:**
1. Search the business name + city for an existing site.
2. If they have a **good, professional, working website** (e.g. a real company site like
   volted.co.za) → **STOP. This pitch does not apply.** Do NOT build a free site, do NOT
   pitch it. Flag the lead as "already has a website — not an AutoSite free-site target."
   (There may be a *different* offer — e.g. an AI-agent/service upgrade — but that is NOT
   this skill's free-website pitch and must be run past Thaby first.)
3. Only proceed to build when the business genuinely has **no website**, or the only thing
   they have is a weak/dated single-purpose page that a modern mobile-first site would
   clearly improve.

The finder must also filter this in: a WhatsApp-ready lead is only send-ready for the
free-website pitch if `has_website` is false. Leads like Volted (professional site) are
**not** AutoSite free-site targets regardless of their WhatsApp number.

## Input

A lead with: `business`, `category`, `city`, `number` (verified WhatsApp mobile), `website` (if any).

## Step 1 — Brand research (what makes them them)

Gather the business's real identity from EVERY accessible public source. Do NOT invent any of it.

- **Facebook page (if they have one):** attempt to pull it with `web_extract` on the page
  URL (find it via `web_search "<business> <city> facebook"`). **⚠️ Known limitation:**
  Firecrawl often refuses Facebook ("Website Not Supported") and FB login-walls pages.
  If it's blocked, record that FB was unreachable and move on — do NOT fabricate FB
  followers, reviews, or content. If it IS reachable, extract: about/bio, services, posts
  (tone + what they talk about), cover/profile imagery (branding), follower count, contact.
- **Their website** (if any): services, exact phrasing they use, USP, contact, tone.
- **Google / Yellosa / ProCompare / Snupit reviews:** rating, number of reviews, what
  customers praise (recurring phrases = their real strengths).
- **LinkedIn** (if a page/profile exists): owner name, years in business, background.
- **Directory listings:** phone, address, hours, established year.

## Step 2 — Brand voice & identity profile

From the research, write a short **brand profile** per lead capturing:
- **What they do** (exact service wording, specialty vs generalist)
- **How they talk** (tone: professional / friendly / casual; phrases they actually use)
- **USP / differentiator** (years experience, 24/7, specialist niche, certified, insured)
- **Social proof** (rating, reviews, followers — only what's real)
- **Branding signals** (colours/logo if visible; else pick from the AutoSite design system)
- **Contact** (phone, WhatsApp, address, hours)
- **Voice sample** — 2–3 lines of copy IN THE OWNER'S OWN WORDS if found (from their site
  or posts), so the site "sounds like them."

## Step 3 — Generate the personalized website

Use the AutoSite design system and template:
- Design system: `/home/chomi/.openclaw/workspace/autosite-sa/DESIGN_SYSTEM.md`
  (dark premium theme, glass morphism, amber accent — **customize the accent to the
  client's brand**).
- Template: `/home/chomi/.openclaw/workspace/autosite-sa/templates/landing-page-v1.html`
- Also see `landing-page-generator` skill for structure/SEO best practices.

Build a single-file `index.html` per lead that:
- Leads with their **specialty**, not a generic label (e.g. "Drain Cleaning Specialists",
  not "Plumbing").
- Uses their real services, their USP (years/24h/insured), their real rating.
- Mirrors their **voice** — borrow their phrasing/tone from the brand profile.
- Uses their real contact + click-to-call/WhatsApp links.
- Uses the AutoSite design system, accent customised to their brand.
Save to `autosite-sa/generated-sites/<safe-name>/index.html`. Include a `DESIGN_REPORT.md`
explaining the choices (mirrors the existing reddys example) and a `README.md`.

## Step 4 — Draft the WhatsApp pitch

The pitch message (this is a WhatsApp lead, so the pitch goes via WhatsApp). Personalized,
short, warm, mobile-friendly. Structure (based on the proven reddys template in
`autosite-sa/outreach/`):
- Greet by owner/first name if known.
- One line of genuine recognition (their real strength — reviews, years, followers if real).
- "We built you a FREE personalized website" — built to sound like them.
- The link (hosted/github pages URL for the generated site).
- What's on it (services, click-to-call, WhatsApp, mobile-friendly).
- ONE clear ask ("want any changes? happy to customise").
Save the draft to `autosite-sa/outreach/<date> - <safe-name> - whatsapp.md`.

## Brand: Alwayzon (renamed 2026-08-19; old internal names "AutoSite SA" / "AlwaysOn SA" are dead)
Alwayzon = a local business's online + automation layer. The name is a play on "always on"
and sells the promise: **24/7 always-on availability** — website + WhatsApp sales pipeline +
domain management. Client-facing materials MUST say "Alwayzon", never "AutoSite"/"AlwaysOn".

**domains.co.za DNS (LEARNED 2026-08-19):** the Host field AUTO-APPENDS `.alwayzon.co.za`.
To add an apex A record leave the **Host field EMPTY** (blank). `@` and the full domain are both
rejected as "invalid hostname" (`@` → `@.alwayzon.co.za`, full domain → doubled). Add 4 A records
→ GitHub Pages IPs `185.199.108.153 / .109 / .110 / .111` to point a site at GitHub Pages free
hosting (no registrar hosting needed). Nameservers stay with domains.co.za.

**Own domain:** `alwayzon.co.za` — REGISTERED via domains.co.za (DiaMatrix) 2026-08-19,
R99/yr, expires 2027-08-18, registrant Bathabile Amirchand. This registrar account is where
all client `.co.za` domains get registered/managed too. Logos (Alwayzon brand) at
`~/.openclaw/workspace/autosite-sa/branding/` (alwayzon-sa-logo.png + alwayzon-sa-avatar.png =
our WhatsApp profile pic).

## Pricing & the value package (LOCKED 2026-08-19 — single source of truth)

**The site build is a paid VALUE PACKAGE (R3,500); the sales pipeline is the upsell.** No free sites.

**The "AlwaysOn Business Starter" package — R3,500 once-off (excl VAT; +15%):**
1. Professional website — responsive, mobile-first, WhatsApp + call buttons, client's own `.co.za` domain, hosting + SSL included
2. Logo design (primary + colour variations)
3. Letterhead (print-ready)
4. Business cards (print-ready)
5. T-shirt design (staff/team)
6. Social media kit (WhatsApp Business profile pic, FB/TikTok cover)
7. Launch + 1 round of revisions

| Item | Price |
|---|---|
| Business Starter package (once-off) | **R3,500** |
| Annual domain + hosting + admin (recurring) | **R300/yr** — WE register & MANAGE the client's `.co.za` |
| Print service (when they want items printed) | **charge per item** (each print job is an upsell) |
| Upsell: sales pipeline setup | **R9,500** once-off |
| Upsell: pipeline monthly | **R1,500 (Starter) / R3,000 (Growth)** per month |

**Domain management (we do it, not the client):** AlwaysOn SA registers and manages each
client's `.co.za` domain (real cost ~R99/yr wholesale→retail) in our own registrar account.
The R300/yr covers the domain + hosting (R0 on GitHub Pages/Cloudflare free tier) + a
management margin. Recurring revenue every client, every year.

**Print upsell:** the package includes print-READY files (logo/letterhead/cards/tee). When a
client wants them physically printed, charge per item — an easy recurring add-on.

**Hosting:** GitHub Pages / Cloudflare Pages **free tier** — R0. SSL free. Deploy via
`~/.hermes/scripts/deploy-autosite-site.sh <repo> <site-dir>` (client site on its own repo).

**SITE-BUILDER (USE THIS, not hand-written HTML):** generate any client site from a config
JSON in ~2 min — `python3 ~/.hermes/scripts/site-builder/generate-site.py <config.json>
--deploy <repo>`. Config schema + template live in that script. NEVER hand-write a client
site; write a config instead. Example config:
`~/.openclaw/workspace/autosite-sa/generated-sites/_demo/moyo-config.json`.

**Outreach & POPIA (Thaby's stance, locked):** contacting a business on its OWN public listing
number (e.g. Google Maps) is NOT a POPIA violation — the number is publicly available info the
business published for business contact (POPIA s6(1)(b) public-info carve-out; also a juristic
business contact, not a private individual). Do NOT flag POPIA as a blocker for this channel.
The real risk is WhatsApp's anti-spam/ban rules, NOT the law — so outreach stays human,
one-at-a-time, personal, with a gentle opt-out line. Never mass-blast a number.

**ROI line for the pitch:** one missed job = R2,500–R15,000. Even Growth at R3,000/mo pays
for itself with one saved job a month, and it's a fraction of a receptionist's R8k–15k/mo.

**Own branding:** AlwaysOn SA needs its own `.co.za` domain (e.g. alwayson.co.za / alwaysonsa.co.za)
in the same registrar account used for clients — register before pitching. Logo at
`~/.openclaw/workspace/autosite-sa/branding/alwayson-sa-logo.png` (used as our WhatsApp profile pic).

## Handoff (approval gate)

- Deliver the generated site path + the WhatsApp draft + the brand profile to Thaby.
- **Nothing is sent until Thaby approves the copy** (her standing AutoSite rule). Once
  approved, the send runs via the WhatsApp pipeline (`pipeline-send.py`) and her reply-notify
  fires when the client responds.
- Log the lead/site in the AutoSite leads file (mark `site_built`, `site_url`, `pitched`).

## Rules

- **Never fabricate** business facts, reviews, followers, years, or voice. Use only what the
  research actually surfaced. If FB is blocked, say so — don't invent FB content.
- **Personalisation is non-negotiable** — never send a generic site to a real business.
- Only pitch leads with a **verified WhatsApp mobile** (landlines are useless).
- Sending stays gated on Thaby's approval of the copy.
- One site + one pitch per lead; dedupe against `generated-sites/`.

## Pitfalls

- **Firecrawl blocks Facebook.** Plan for it: FB is best-effort; pull branding from their
  site/reviews/directories instead. Never invent FB data.
- **Mobile numbers only.** Verify with `whatsapp-verify.py`; a landline can't receive WhatsApp.
- **Don't over-fabricate social proof.** A believable site with real (even modest) proof
  beats a flashy one with invented numbers.
- **Keep it single-file & deployable** (Cloudflare Pages / GitHub Pages compatible) so the
  pitch link actually works.
