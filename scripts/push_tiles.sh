set -euo pipefail
: "${DWTS_OUT:=$HOME/dwts-out}"
cd "$(dirname "$0")/.."
repo=$PWD
url=$(git remote get-url github)
force=""
[ "${1:-}" = "--force" ] && force="-f"
work=$(mktemp -d "$DWTS_OUT/tiles_branch.XXXX")
mkdir -p "$work/tiles" "$work/listen"
cp "$DWTS_OUT"/tiles/*.pmtiles "$work/tiles/"
cp -r "$DWTS_OUT"/listen/. "$work/listen/"
cd "$work"
git init -q -b tiles
git config user.name "$(git -C "$repo" config user.name)"
git config user.email "$(git -C "$repo" config user.email)"
cat > README.md <<'EOF'
# tiles (orphan branch)

Raster tiles (PMTiles) and the listening grid for the app, written by `python -m dwts.run tiles` and
`python -m dwts.run listen` on `main`. The Pages workflow on `main` copies them into the site.
EOF
git add -A
big=$(find tiles listen -type f -size +50M)
if [ -n "$big" ]; then echo "files over 50 MB: $big"; exit 1; fi
if grep -rIl -E "machine urs|password|token=" . --exclude-dir=.git; then echo "secret pattern found"; exit 1; fi
git commit -q -m "Tiles and listening grid $(date -u +%Y-%m-%dT%H:%MZ)"
du -sh tiles listen
git push $force -q "$url" tiles:tiles
echo "pushed tiles branch from $work"
