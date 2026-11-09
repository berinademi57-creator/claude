#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
#  Jarvis-Installer für macOS / Linux / WSL2
#  Aufruf (im Ordner dieses Repos):   bash jarvis/install.sh
#  Erneut ausführen ist sicher: deine Einstellungen bleiben erhalten.
#  --update überschreibt config.toml und SOUL.md mit der neuen Version.
# ═══════════════════════════════════════════════════════════════
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -n "${OPENJARVIS_HOME:-}" ]]; then OJ_HOME="$OPENJARVIS_HOME"
elif [[ -n "${XDG_DATA_HOME:-}" ]]; then OJ_HOME="$XDG_DATA_HOME/openjarvis"
else OJ_HOME="$HOME/.openjarvis"; fi
UPDATE="${1:-}"

say()  { printf '\n\033[1;31m▶ %s\033[0m\n' "$*"; }
warn() { printf '\033[33m  ⚠ %s\033[0m\n' "$*"; }

# 1) OpenJarvis selbst (offizieller Installer: uv, Python, Ollama, jarvis)
if command -v jarvis >/dev/null 2>&1; then
  say "OpenJarvis ist schon installiert ($(command -v jarvis))"
else
  say "Installiere OpenJarvis (ca. 3 Minuten) …"
  curl -fsSL https://open-jarvis.github.io/OpenJarvis/install.sh | bash
fi
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

# 2) jarvis-plus (Whoop, Garmin, Stress, Anrufe, Instagram, Kunden, HUD, Websites)
say "Installiere jarvis-plus …"
if command -v uv >/dev/null 2>&1; then
  uv tool install --force --with garminconnect "$HERE/jarvis_plus"
else
  python3 -m pip install --user --upgrade "$HERE/jarvis_plus[garmin]"
fi
if ! command -v jarvis-plus >/dev/null 2>&1; then
  echo "❌ jarvis-plus wurde nicht gefunden. Prüfe, ob ~/.local/bin im PATH ist." >&2
  exit 1
fi

# 3) Konfiguration nach ~/.openjarvis
say "Richte Konfiguration in $OJ_HOME ein …"
mkdir -p "$OJ_HOME/skills"
stamp="$(date +%Y%m%d-%H%M%S)"
for f in config.toml SOUL.md; do
  # Schon von uns eingerichtet → deine Änderungen behalten (ausser --update)
  if [[ "$UPDATE" != "--update" ]] \
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

# Profil: privates Paket > vorhandene eigene Datei > Vorlage
PRIV="$HERE/private"
is_template() { [[ ! -f "$1" ]] || grep -q "füll das aus" "$1" || ! grep -q "Über mich" "$1"; }
if [[ -f "$PRIV/USER.md" ]] && is_template "$OJ_HOME/USER.md"; then
  cp "$PRIV/USER.md" "$OJ_HOME/USER.md"; echo "  USER.md aus privatem Paket"
elif is_template "$OJ_HOME/USER.md"; then
  cp "$HERE/config/USER.md" "$OJ_HOME/USER.md"
fi
if [[ -f "$PRIV/MEMORY.md" ]]; then
  if [[ -f "$OJ_HOME/MEMORY.md" ]] && ! cmp -s "$PRIV/MEMORY.md" "$OJ_HOME/MEMORY.md"; then
    cp "$OJ_HOME/MEMORY.md" "$OJ_HOME/MEMORY.md.backup-$stamp"
  fi
  cp "$PRIV/MEMORY.md" "$OJ_HOME/MEMORY.md"; echo "  MEMORY.md (Business-Wissen) aus privatem Paket"
fi
[[ -f "$OJ_HOME/credentials.toml" ]] || cp "$HERE/config/credentials.toml.example" "$OJ_HOME/credentials.toml"
[[ -f "$OJ_HOME/jarvis-plus.env" ]] || cp "$HERE/config/jarvis-plus.env.example" "$OJ_HOME/jarvis-plus.env"
chmod 600 "$OJ_HOME/credentials.toml" "$OJ_HOME/jarvis-plus.env"

# jarvis-plus in OpenJarvis eintragen (andere Connectoren bleiben erhalten)
jarvis-plus register

# 4) Skills: eigene + private + die besten Website-Skills von GitHub
say "Installiere Skills …"
for dir in "$HERE"/skills/*/ "$PRIV"/skills/*/; do
  [[ -f "$dir/SKILL.md" ]] || continue
  name="$(basename "$dir")"
  mkdir -p "$OJ_HOME/skills/$name" && cp -R "$dir"/. "$OJ_HOME/skills/$name/"
  echo "  ✓ $name"
done
gh_skill() {  # $1 = Skill-Name, $2 = Repo
  if jarvis skill install "github:$1" --url "$2" --force </dev/null >/dev/null 2>&1; then
    echo "  ✓ $1  ($2)"
  else
    warn "$1 konnte nicht installiert werden (später: jarvis skill install github:$1 --url $2)"
  fi
}
gh_skill frontend-design        https://github.com/anthropics/skills
gh_skill web-artifacts-builder  https://github.com/anthropics/skills
gh_skill theme-factory          https://github.com/anthropics/skills
gh_skill impeccable             https://github.com/pbakaus/impeccable
gh_skill design-taste-frontend  https://github.com/Leonxlnx/taste-skill
gh_skill web-design-guidelines  https://github.com/vercel-labs/agent-skills

# 5) Node.js für Connectoren (Higgsfield, Canva, Notion …)
if ! command -v npx >/dev/null 2>&1; then
  warn "Node.js fehlt (für Connectoren + 'jarvis gui'). Mac: brew install node · Linux: https://nodejs.org"
fi

# 6) Immer im Hintergrund
if grep -Eq '^ANTHROPIC_API_KEY *= *"[^"]+"' "$OJ_HOME/credentials.toml"; then
  say "Starte Jarvis im Hintergrund (Autostart) …"
  jarvis-plus autostart an || warn "Autostart fehlgeschlagen, später: jarvis-plus autostart"
  AUTOSTART_DONE=1
else
  AUTOSTART_DONE=0
fi

cat <<EOF

✅ Installation fertig!

Noch zu tun (einmalig), danach erledigt Jarvis den Rest:
  1. $OJ_HOME/credentials.toml   → ANTHROPIC_API_KEY, TELEGRAM_BOT_TOKEN
  2. $OJ_HOME/jarvis-plus.env    → Whoop-Secret, Garmin, Twilio, Instagram, Netlify, Telegram-Chat-ID
  3. In $OJ_HOME/config.toml bei [channel.telegram] deine Chat-ID eintragen

Verbinden:
  jarvis-plus whoop-login
  jarvis-plus garmin-login
  jarvis connect gdrive          # Gmail + Google Kalender + Tasks
  jarvis-plus connect higgsfield # + canva, notion, figma, 21st
  jarvis-plus status             # zeigt, was noch fehlt
EOF
if [[ "$AUTOSTART_DONE" == "1" ]]; then
  echo "Jarvis läuft im Hintergrund. HUD: http://localhost:8765"
else
  echo ""
  echo "Danach einmal:   jarvis-plus autostart     (läuft dann immer im Hintergrund)"
  echo "HUD öffnen:      http://localhost:8765"
fi
