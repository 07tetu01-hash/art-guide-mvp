#!/usr/bin/env bash
set -euo pipefail

MSG="${1:-Update data}"

if [ ! -d "scripts" ] || [ ! -d "data" ]; then
  echo "❌ repo直下で実行してね（scripts/ と data/ が見える場所）"
  exit 1
fi

echo "▶ build json..."
python3 scripts/build_json.py

echo "▶ git add..."
git add artists.json works.json exhibitions.json data/*.csv scripts/build_json.py scripts/update_data.sh

echo "▶ git commit..."
git commit -m "$MSG" || {
  echo "ℹ️ コミットする変更がなかった（何も変わってない）"
  exit 0
}

echo "▶ git push..."
git push

echo "✅ done"
