# 🤖 Dein Jarvis – OpenJarvis + persönliche Erweiterungen

Basis ist [OpenJarvis](https://github.com/open-jarvis/OpenJarvis) (Stanford, Open Source).
Dazu kommt **jarvis-plus**, eine eigene Erweiterung mit Whoop, Garmin,
Stress-Check, Anrufen, Instagram, Kunden-CRM und deinem Profil „über mich“.

```
 Handy (Telegram) ─┐                    ┌─ Whoop API (Recovery, HRV, Schlaf, Strain)
 PC (Desktop-App)  ├──►  OpenJarvis  ◄──┼─ Garmin (Stress, Body Battery, Schlaf)
 Browser (gui)    ─┘    (Claude als     ├─ Twilio (ruft dich an, SMS)
                         Gehirn,        ├─ Instagram (Posts, Kommentare, Stats)
                         Gedächtnis,    ├─ Kunden-CRM (lokal)
                         Erinnerungen)  ├─ Gmail / Google Kalender / Drive
                                        └─ Profil „über mich“ (lokal)
         ▲
         └── jarvis-plus watch: prüft alle 30 Min deine Werte und meldet sich selbst
```

---

## Was Jarvis kann

| Wunsch | Status | Wie |
|---|---|---|
| Mit ihm reden, überall (Handy + PC) | ✅ | Telegram-Bot (Text) · Desktop-App / `jarvis gui` · `jarvis` im Terminal |
| Er ruft dich an | ✅ | Twilio: `mich_anrufen` („Ruf mich um 7 Uhr an und weck mich“) |
| Erinnerungen | ✅ | `schedule_task` → Telegram, SMS oder Anruf zur Uhrzeit |
| Whoop | ✅ | Offizielle API v2: Recovery, HRV, Ruhepuls, Schlaf, Strain, Workouts |
| Garmin | ✅ | Stress, Body Battery, Schlaf, Schritte (inoffizielle Bibliothek, siehe unten) |
| Merkt, wann du gestresst bist | ✅ | `stress_check` + Wächter schickt dir automatisch Tipps (optional Anruf) |
| Coach | ✅ | Persönlichkeit in `SOUL.md`: Training, Ernährung, Schlaf, Mindset, Business |
| Alles über dich wissen | ✅ | `USER.md` + `ueber-mich.md` + automatisches Langzeitgedächtnis |
| Business / Kunden | ✅ | Kunden-CRM mit Status, Notizen, Fälligkeiten; tägliche Erinnerung |
| Gmail, Kalender, Drive | ✅ | Eingebaut in OpenJarvis: `jarvis connect gdrive` |
| Instagram | ⚠️ teilweise | Posts + Kommentare lesen, antworten, Foto posten, Statistiken |
| Instagram-DMs | ❌ | Braucht eine von Meta geprüfte App |
| „Jede App“ steuern | ❌ | Geht nur bei Apps mit Schnittstelle (API/MCP); siehe „Mehr Apps“ |
| Echtes Telefongespräch mit Jarvis | ❌ (noch) | Er ruft an und spricht; Gespräch läuft per Telegram/Desktop |

Ehrlich gesagt: Kein Assistent kann **jede** App auf deinem Handy bedienen.
iPhone und Android erlauben das nicht. Alles mit einer Schnittstelle lässt sich
aber nachrüsten.

---

## Installation

### Was du brauchst (einmalig anlegen)

| Konto | Wofür | Kosten |
|---|---|---|
| [Anthropic API](https://console.anthropic.com) | Jarvis' Gehirn (Claude) | pro Nutzung, ca. ein paar € im Monat bei normaler Nutzung |
| Telegram + [@BotFather](https://t.me/BotFather) | Mit Jarvis überall schreiben | kostenlos |
| [Whoop Developer](https://developer.whoop.com) | Hast du schon (Client-ID steht drin), du brauchst das **Client Secret** | kostenlos |
| Garmin Connect | Dein normales Login | kostenlos |
| [Twilio](https://www.twilio.com) | Anrufe + SMS | ca. 1 €/Monat Nummer + Cent-Beträge pro Anruf |
| Instagram **Business- oder Creator-Account** + [Meta-Developer-App](https://developers.facebook.com) | Instagram-Funktionen | kostenlos |

> **Wichtig, weil du 16 bist:** Anthropic (API) und Twilio verlangen, dass
> der Kontoinhaber volljährig ist. Lass diese Konten von einem Elternteil
> anlegen. Das bezahlt dann auch die API-Kosten.
> **Kostenlose Alternative ohne Konto:** Jarvis komplett lokal mit Ollama
> laufen lassen (siehe `config.toml`, Variante B). Das braucht einen starken PC
> und ist etwas weniger schlau.

### Schritt 1: Installieren

**Mac / Linux:**
```bash
git clone https://github.com/berinademi57-creator/claude.git
cd claude
git checkout claude/bold-mendel-5rrt2t
bash jarvis/install.sh
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/berinademi57-creator/claude.git
cd claude
git checkout claude/bold-mendel-5rrt2t
powershell -ExecutionPolicy Bypass -File jarvis\install.ps1
```

Der Installer:
1. installiert OpenJarvis mit dem offiziellen Installer (uv, Python, Ollama, `jarvis`),
2. installiert `jarvis-plus`,
3. kopiert Konfiguration, Persönlichkeit und Vorlagen nach `~/.openjarvis/`
   (vorhandene Dateien werden gesichert, deine eigenen Einträge bleiben erhalten).

### Schritt 2: Zugänge eintragen

1. **`~/.openjarvis/credentials.toml`**: `ANTHROPIC_API_KEY`, `TELEGRAM_BOT_TOKEN`
2. **`~/.openjarvis/jarvis-plus.env`**: Whoop-Secret, Garmin-Login, Twilio, Instagram, Telegram
3. **`~/.openjarvis/USER.md`**: alles Wichtige über dich (Ziele, Business, Alltag)
4. **Telegram-Chat-ID** herausfinden: in Telegram [@userinfobot](https://t.me/userinfobot)
   anschreiben, die Zahl in `jarvis-plus.env` (`TELEGRAM_CHAT_ID`) **und** in
   `~/.openjarvis/config.toml` bei `[channel.telegram] allowed_chat_ids` eintragen.
   Dann kann **nur du** deinen Jarvis benutzen.

### Schritt 3: Verbinden und testen

```bash
jarvis-plus whoop-login      # Browser öffnet sich → Whoop erlauben
jarvis-plus garmin-login     # danach GARMIN_PASSWORD aus der .env löschen
jarvis connect gdrive        # Gmail + Google Kalender + Tasks
jarvis-plus check            # zeigt Whoop + Garmin + Stress-Einschätzung
jarvis-plus test-telegram    # Nachricht aufs Handy
jarvis-plus test-call        # dein Handy klingelt
```

### Schritt 4: Starten

```bash
jarvis start                 # Jarvis im Hintergrund (Telegram + App)
jarvis gui                   # schöne Chat-Oberfläche im Browser
jarvis-plus watch            # Wächter: Stress- und Kunden-Erinnerungen
```

Am PC kannst du auch die **Desktop-App** nehmen (`.exe` / `.dmg` unter
[OpenJarvis Releases](https://github.com/open-jarvis/OpenJarvis/releases)).
Sie nutzt dieselbe Konfiguration.

**Damit Jarvis immer läuft**, muss ein Rechner an sein (PC, Laptop, Mac mini,
Raspberry Pi 5 oder ein kleiner Cloud-Server). Für den Autostart gibt es bei
OpenJarvis fertige Vorlagen (`deploy/systemd`, `deploy/launchd`, `deploy/windows`).

---

## So redest du mit ihm (Beispiele)

- „Guten Morgen“ → Recovery, Schlaf, Stress, Termine, fällige Kunden, Fokus des Tages
- „Wie gestresst bin ich gerade?“
- „Ruf mich morgen um 6:30 an und sag: Aufstehen, Training!“
- „Erinnere mich jeden Sonntag um 18 Uhr an die Wochenplanung“
- „Neuer Kunde: Lisa Schmidt, Insta-Shop, will ein Angebot bis Freitag“
- „Was ist bei meinen Kunden diese Woche fällig?“
- „Schreib mir 3 Caption-Ideen für meinen nächsten Post und zeig mir die Kommentare vom letzten“
- „Merk dir: Ich will bis Juni 5 kg Muskeln aufbauen“
- „Sollte ich heute hart trainieren?“ (nutzt deine Whoop- und Garmin-Daten)

---

## Die Erweiterung `jarvis-plus`

MCP-Server in `jarvis_plus/`, OpenJarvis startet ihn automatisch. Er läuft auch
in Claude Desktop oder anderen MCP-Apps.

| Tool | Was es macht |
|---|---|
| `whoop_daten`, `garmin_daten` | Gesundheitsdaten |
| `stress_check` | Kombiniert beides → Level (niedrig/mittel/hoch), Gründe, Tipps |
| `mich_anrufen`, `mir_sms_schicken`, `mir_telegram_schicken` | Nur an **deine eigene** Nummer bzw. deinen Chat |
| `ueber_mich_lesen`, `ueber_mich_merken` | Dein Profil (`~/.openjarvis/ueber-mich.md`) |
| `kunde_speichern`, `kunde_notiz`, `kunde_anzeigen`, `kunden_liste`, `kunden_faellig` | Kunden-CRM (lokale SQLite) |
| `instagram_konto`, `instagram_posts`, `instagram_kommentare`, `instagram_kommentar_antworten`, `instagram_foto_posten`, `instagram_statistiken` | Instagram. Posten und Antworten **nur nach deinem „ja“** |

**Stress-Logik** (`stress.py`, einfache Regeln, keine Diagnose):
Whoop-Recovery rot/gelb, HRV unter deinem 7-Tage-Schnitt, Ruhepuls erhöht,
< 6 h Schlaf, Garmin-Stress ≥ 35/50, Body Battery < 25 → Punkte → Level.

Tests: `cd jarvis/jarvis_plus && pip install -e '.[dev]' && pytest`

### Hinweis zu Garmin
Garmin hat keine offizielle API für Privatpersonen. `garminconnect` ist eine
weit verbreitete inoffizielle Bibliothek, die sich wie die Garmin-Connect-App
anmeldet. Sie funktioniert meistens gut, kann aber bei Garmin-Änderungen
zeitweise kaputtgehen. Dann hilft meist `pip install -U garminconnect`.

---

## Mehr Apps anbinden

Jede App mit **MCP-Server** lässt sich in `~/.openjarvis/mcp-servers.json`
eintragen (z.B. Notion, Shopify, Spotify, Home Assistant, Todoist). Beispiel:

```json
[
  {"name": "jarvis-plus", "command": "/pfad/zu/jarvis-plus", "args": ["serve"]},
  {"name": "notion", "command": "npx", "args": ["-y", "@notionhq/notion-mcp-server"]}
]
```

OpenJarvis bringt außerdem selbst mit: Gmail, Google Kalender/Drive/Tasks,
Outlook, Notion, Obsidian, Slack, Spotify, Strava, Oura, Apple Health/Notizen/
Kalender (Mac), WhatsApp, iMessage, Wetter, News. Siehe `jarvis connect --help`.

---

## Sicherheit

- Alle Keys liegen nur auf deinem Rechner (`~/.openjarvis/`, Dateirechte 600),
  **nie in Git**.
- Telegram ist auf deine Chat-ID beschränkt.
- Jarvis ruft/schreibt nur **dich** an, nie fremde Nummern.
- Veröffentlichen (Instagram) nur nach deiner Bestätigung.
- Gesundheitsdaten bleiben lokal. An Claude geht nur, was für die Antwort nötig ist.
