#!/usr/bin/env python3
"""Watchdog: stays SILENT until alwayzon.co.za resolves to GitHub Pages, then reports ONCE.
Used as a no_agent cron (empty stdout = no delivery)."""
import json, os, urllib.request

MARKER = os.path.expanduser("~/.hermes/cache/alwayzon_live_reported")
GH = {"185.199.108.153", "185.199.109.153", "185.199.110.153", "185.199.111.153"}

def dns_a(host):
    try:
        with urllib.request.urlopen(f"https://dns.google/resolve?name={host}&type=A", timeout=15) as r:
            d = json.load(r)
        return [a.get("data") for a in d.get("Answer", [])]
    except Exception:
        return []

def main():
    if os.path.exists(MARKER):
        print()  # already reported once — stay silent
        return
    ips = set(dns_a("alwayzon.co.za"))
    if ips & GH:
        open(MARKER, "w").write("1")
        print("✅ alwayzon.co.za is LIVE! The site is now serving.\nhttps://alwayzon.co.za")
    else:
        print()  # not live yet — silent

if __name__ == "__main__":
    main()
