#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
#  Jarvis-Installer für macOS / Linux / WSL2
#  Aufruf (im Ordner dieses Repos):   bash jarvis/install.sh
# ═══════════════════════════════════════════════════════════════
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -n "${OPENJARVIS_HOME:-}" ]]; then OJ_HOME="$OPENJARVIS_HOME"
elif [[ -n "${XDG_DATA_HOME:-}" ]]; then OJ_HOME="$XDG_DATA_HOME/openjarvis"
else OJ_HOME="$HOME/.openjarvis"; fi

say() { printf '\n\033[1;36m▶ %s\033[0m\n' "$*"; }

# 1) OpenJarvis selbst (offizieller Installer: uv, Python, Ollama, jarvis)
if command -v jarvis >/dev/null 2>&1; then
  say "OpenJarvis ist schon installiert ($(command -v jarvis))"
else
  say "Installiere OpenJarvis (ca. 3 Minuten) …"
  curl -fsSL https://open-jarvis.github.io/OpenJarvis/install.sh | bash
fi
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

# 2) jarvis-plus (Whoop, Garmin, Stress, Anrufe, Instagram, Kunden)
say "Installiere jarvis-plus …"
if command -v uv >/dev/null 2>&1; then
  uv tool install --force --with garminconnect "$HERE/jarvis_plus"
else
  python3 -m pip install --user --upgrade "$HERE/jarvis_plus[garmin]"
fi
JP_BIN="$(command -v jarvis-plus || true)"
if [[ -z "$JP_BIN" ]]; then
  echo "❌ jarvis-plus wurde nicht gefunden. Prüfe, ob ~/.local/bin im PATH ist." >&2
  exit 1
fi

# 3) Konfiguration nach ~/.openjarvis kopieren
say "Richte Konfiguration in $OJ_HOME ein …"
mkdir -p "$OJ_HOME"
stamp="$(date +%Y%m%d-%H%M%S)"
for f in config.toml SOUL.md; do
  # Schon von uns eingerichtet → deine Änderungen behalten (Update: --update)
  if [[ "${1:-}" != "--update" ]] \
     && grep -q -e "Dein persönlicher Jarvis" -e "Du bist \*\*Jarvis\*\*" "$OJ_HOME/$f" 2>/dev/null; then
    echo "  $f behalten (schon eingerichtet)"
    continue
  fi
  if [[ -f "$OJ_HOME/$f" ]] && ! cmp -s "$HERE/config/$f" "$OJ_HOME/$f"; then
    cp "$OJ_HOME/$f" "$OJ_HOME/$f.backup-$stamp"
    echo "  Backup: $f.backup-$stamp"
  fi
  cp "$HERE/config/$f" "$OJ_HOME/$f"
done
# Persönliche Dateien nie überschreiben
[[ -f "$OJ_HOME/USER.md" ]] && grep -q "Über mich" "$OJ_HOME/USER.md" || cp "$HERE/config/USER.md" "$OJ_HOME/USER.md"
[[ -f "$OJ_HOME/credentials.toml" ]] || cp "$HERE/config/credentials.toml.example" "$OJ_HOME/credentials.toml"
[[ -f "$OJ_HOME/jarvis-plus.env" ]] || cp "$HERE/config/jarvis-plus.env.example" "$OJ_HOME/jarvis-plus.env"
chmod 600 "$OJ_HOME/credentials.toml" "$OJ_HOME/jarvis-plus.env"

# MCP-Server mit absolutem Pfad eintragen (Jarvis startet ihn selbst)
cat > "$OJ_HOME/mcp-servers.json" <<JSON
[
  {"name": "jarvis-plus", "command": "$JP_BIN", "args": ["serve"]}
]
JSON

cat <<EOF

✅ Installation fertig!

Jetzt noch deine Zugänge eintragen (einmalig):
  1. $OJ_HOME/credentials.toml   → ANTHROPIC_API_KEY, TELEGRAM_BOT_TOKEN
  2. $OJ_HOME/jarvis-plus.env    → Whoop-Secret, Garmin, Twilio, Instagram, Telegram-Chat-ID
  3. $OJ_HOME/USER.md            → alles über dich
  4. In $OJ_HOME/config.toml bei [channel.telegram] deine Chat-ID eintragen

Dann verbinden:
  jarvis-plus whoop-login
  jarvis-plus garmin-login
  jarvis connect gdrive          # Gmail + Google Kalender + Tasks
  jarvis-plus test-telegram
  jarvis-plus test-call

Starten:
  jarvis start                   # Jarvis im Hintergrund (Telegram + App)
  jarvis gui                     # Oberfläche im Browser
  jarvis-plus watch              # Stress-/Kunden-Wächter
EOF
