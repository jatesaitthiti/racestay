#!/usr/bin/env bash
# Publish the RaceStay static prototype to GitHub Pages.
# Requires: git, gh (GitHub CLI) authenticated with `gh auth login` (scopes: repo, workflow).
set -euo pipefail

REPO="${1:-racestay}"   # repo name (default: racestay). Override: bash publish.sh my-repo-name

echo "▶ init git repo…"
git init -b main >/dev/null 2>&1 || git checkout -B main
git add -A
git commit -m "RaceStay ATM 2026 — static prototype" >/dev/null 2>&1 || echo "  (nothing new to commit)"

echo "▶ create GitHub repo '$REPO' and push…"
if gh repo view "$REPO" >/dev/null 2>&1; then
  echo "  repo exists — pushing to it"
  git remote add origin "$(gh repo view "$REPO" --json url -q .url).git" 2>/dev/null || true
  git push -u origin main
else
  gh repo create "$REPO" --public --source=. --remote=origin --push
fi

OWNER="$(gh api user -q .login)"

echo "▶ enable GitHub Pages (branch main / root)…"
gh api --method POST "repos/$OWNER/$REPO/pages" \
  -f "source[branch]=main" -f "source[path]=/" >/dev/null 2>&1 \
  || echo "  (Pages may already be enabled — skipping)"

echo "▶ waiting for the Pages URL…"
URL=""
for i in $(seq 1 10); do
  URL="$(gh api "repos/$OWNER/$REPO/pages" -q .html_url 2>/dev/null || true)"
  [ -n "$URL" ] && break
  sleep 3
done

echo ""
echo "✅ Done. Site will be live shortly at:"
echo "   ${URL:-https://$OWNER.github.io/$REPO/}"
echo "   (first build can take 1–2 minutes)"
