#!/usr/bin/env python3
"""
whatsapp-verify.py — verify SA mobile/WhatsApp numbers and file WhatsApp-ready leads.

Takes candidate leads on stdin (JSON array) and keeps only those whose contact
is a valid South African MOBILE number (WhatsApp-capable). Landlines, VoIP (087),
toll-free (0800/086x), and missing numbers are rejected with a reason.

A WhatsApp-able SA number is 10 digits starting with 0 where the prefix is a
mobile range:
  06x, 07x, or 08 with second digit 1-6 or 8-9
  (rejects 087 non-geo VoIP, 0800/0860/0861/0862 toll-free/call-centre)

Output: writes send-ready leads to the file path given via --out (JSON), and
prints a human digest to stdout.

Input candidate shape:
  {"business","category","city","number","source","website","context"}
  (number may include spaces/+27/()- — we normalise)
"""

import sys
import json
import re
import datetime
from pathlib import Path

SAST = datetime.timezone(datetime.timedelta(hours=2))

# Default output: next to the autosite leads.
DEFAULT_OUT = Path("/home/chomi/.openclaw/workspace/autosite-sa/leads/whatsapp-leads.json")

MOBILE_RE = re.compile(r"^0(?:[67]\d{8}|8[1-689]\d{7})$")


def normalise_number(raw: str) -> str:
    """Strip spaces/dashes/+27/() -> E.164-ish local digits."""
    if not raw:
        return ""
    d = re.sub(r"[^\d]", "", raw)
    # +27821234567 -> 0821234567
    if d.startswith("27") and len(d) == 11:
        d = "0" + d[2:]
    return d


def is_mobile(number: str) -> bool:
    return MOBILE_RE.match(number) is not None


def verify(candidate: dict) -> dict:
    """Return {ok, number, reason}."""
    raw = str(candidate.get("number") or "").strip()
    if not raw:
        return {"ok": False, "number": "", "reason": "no number"}
    n = normalise_number(raw)
    if len(n) != 10 or not n.startswith("0"):
        return {"ok": False, "number": n, "reason": f"not a valid SA number ({raw})"}
    if n.startswith("087") or n.startswith("0800") or n[:3] in ("086",):
        return {"ok": False, "number": n, "reason": f"not a mobile (VoIP/toll-free) ({raw})"}
    if is_mobile(n):
        return {"ok": True, "number": n, "reason": "mobile/WhatsApp"}
    return {"ok": False, "number": n, "reason": f"not a mobile prefix ({raw})"}


def main(argv):
    out_path = DEFAULT_OUT
    if "--out" in argv:
        out_path = Path(argv[argv.index("--out") + 1])

    try:
        candidates = json.load(sys.stdin)
    except Exception as e:
        print(f"ERROR reading candidates: {e}", file=sys.stderr)
        return 2
    if not isinstance(candidates, list):
        print("ERROR: expected a JSON array", file=sys.stderr)
        return 2

    keep, reject = [], []
    for c in candidates:
        r = verify(c)
        rec = {**c, "number": r["number"]}
        if r["ok"]:
            rec["whatsapp_verified"] = True
            rec["verified_date"] = datetime.datetime.now(SAST).strftime("%Y-%m-%d")
            keep.append(rec)
        else:
            rec["reject_reason"] = r["reason"]
            reject.append(rec)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"send_ready": keep, "rejected": reject,
                                    "verified": datetime.datetime.now(SAST).strftime("%Y-%m-%d")},
                                   indent=2))

    print(f"VERIFIED {len(keep)} WhatsApp-ready, rejected {len(reject)}")
    for c in keep:
        print(f"  + {c.get('business')} | {c.get('city')} | WhatsApp {c['number']}")
    for c in reject:
        print(f"  - {c.get('business')} | {c.get('city')} | {c.get('reject_reason')}")
    print(f"\nSend-ready saved to: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
