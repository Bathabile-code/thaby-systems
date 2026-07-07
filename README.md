# Thaby-Systems Backup

Backup of custom Hermes agent infrastructure for Thaby's businesses.

## Contents

- `hermes-scripts/` — Custom Python/shell scripts for automation
- `hermes-skills/` — Custom Hermes skills
- `systemd/` — Systemd user service/timer for solar catch-up
- `vault/` — Obsidian vault structure and templates (manual snapshot)

## Scripts

| Script | Purpose |
|--------|---------|
| `obsidian-tender.py` | Tends Obsidian vault: daily notes, inbox review, MOC updates |
| `lead-gen-tender.py` | Processes lead notes, scores them, drafts outreach |
| `obsidian-catch-up.py` | Runs at boot if machine was off, catches up missed crons |

## Systemd

Timer runs 30 seconds after WSL boot for solar-powered catch-up.

## How to restore

1. Copy scripts to `~/.hermes/scripts/`
2. Copy skills to `~/.hermes/skills/productivity/`
3. Copy systemd files to `~/.config/systemd/user/`
4. Run: `systemctl --user daemon-reload && systemctl --user enable obsidian-catch-up.timer`
