#!/usr/bin/env bash
set -euo pipefail
# Deploy an AutoSite generated site to GitHub Pages (own repo per site).
# Usage: deploy-autosite-site.sh <repo-name> <site-dir>
REPO_NAME="${1:?usage: deploy-autosite-site.sh <repo-name> <site-dir>}"
SITE_DIR="${2:?usage: deploy-autosite-site.sh <repo-name> <site-dir>}"
OWNER="Bathabile-code"

if [ -z "${GITHUB_TOKEN:-}" ] && [ -f "$HOME/.hermes/github_token.env" ]; then
  set -a; . "$HOME/.hermes/github_token.env"; set +a
fi
TOKEN="${GITHUB_TOKEN:-}"
if [ -z "$TOKEN" ]; then echo "ERROR: GITHUB_TOKEN not set" >&2; exit 1; fi
AUTH="Authorization: token $TOKEN"

echo "1/4 Creating repo ${OWNER}/${REPO_NAME}..."
CODE="$(curl -s -o /tmp/as-repo.json -w '%{http_code}' -X POST -H "$AUTH" -H "Accept: application/vnd.github+json" \
  "https://api.github.com/user/repos" \
  -d "{\"name\":\"$REPO_NAME\",\"description\":\"AutoSite SA personalized preview\",\"private\":false,\"auto_init\":false}")"
echo "   (create status: $CODE)"

echo "2/4 Pushing site to main..."
cd "$SITE_DIR"
git init -q 2>/dev/null || true
git config user.email "autosite-sa@users.noreply.github.com" >/dev/null 2>&1 || true
git config user.name "AutoSite SA" >/dev/null 2>&1 || true
git add -A
git -c commit.gpgsign=false commit -q -m "AutoSite SA personalized site" 2>/dev/null || true
git branch -M main
git remote remove origin 2>/dev/null || true
git remote add origin "https://${OWNER}:${TOKEN}@github.com/${OWNER}/${REPO_NAME}.git"
PUSH="$(git push -q -u origin main 2>&1)" && echo "   pushed." || { echo "   PUSH FAILED: $PUSH" >&2; exit 1; }

echo "3/4 Enabling GitHub Pages..."
PAGE_CODE="$(curl -s -o /tmp/as-pages.json -w '%{http_code}' -X POST -H "$AUTH" -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/${OWNER}/${REPO_NAME}/pages" -d '{"source":{"branch":"main","path":"/"}}')"
echo "   (pages status: $PAGE_CODE)"

echo "4/4 Live URL (may take ~30-60s to build):"
echo "   https://${OWNER}.github.io/${REPO_NAME}/"
