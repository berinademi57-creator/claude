# 🤖 Dein Jarvis: OpenJarvis + persönliche Erweiterungen

Basis ist [OpenJarvis](https://github.com/open-jarvis/OpenJarvis) (Stanford, Open Source).
Dazu kommt **jarvis-plus**: HUD mit Stimme, Whoop, Garmin, Stress-Check, Anrufe,
Instagram, Kunden-CRM, Website-Bau mit Veröffentlichung, Connectoren und Autostart.

```
 PC / Handy: HUD (Orb, Stimme) ─┐                  ┌─ Whoop · Garmin (Gesundheit, Stress)
 Handy: Telegram ───────────────┼─►  OpenJarvis  ◄─┼─ Twilio (ruft dich an, SMS)
 Desktop-App / jarvis gui ──────┘    Claude Haiku  ├─ Instagram · Kunden-CRM
                                     ↕ Sonnet bei  ├─ Websites bauen → Netlify
                                     Websites/Code ├─ Higgsfield · Canva · Notion · Figma · 21st.dev
                                                   └─ Gmail · Kalender · Drive (eingebaut)
 Autostart: jarvis serve + HUD + Wächter laufen immer im Hintergrund
```

---

## Was Jarvis kann

| Wunsch | Status | Wie |
|---|---|---|
| Krasses Design als App | ✅ | **HUD**: schwarzer Command-Center-Look, glühender Faden-Orb, Vitals, Live-Aktivität. Am Handy als App auf den Homescreen |
| Mit ihm reden | ✅ | Stimme im HUD (Mikrofon, Leertaste oder Wake-Word „Jarvis …“), Antworten werden vorgelesen. Plus Telegram |
| Zeigt immer, was er tut | ✅ | Jeder Schritt erscheint live im HUD („⟳ Whoop-Daten holen …“), mit Dauer und Ergebnis |
| Läuft immer im Hintergrund | ✅ | `jarvis-plus autostart`: startet bei jedem Hochfahren (Mac, Windows, Linux) |
| Wenig Kosten, trotzdem schnell | ✅ | Alltag mit **Claude Haiku** (schnell und günstig), Websites/Code/Strategie automatisch mit **Sonnet**. Kurzer Verlauf, Prompt-Caching. Stimme kostenlos über den Browser |
| Krasse Websites | ✅ | Skill `krasse-websites` + die besten Design-Skills von GitHub. Website erscheint live im HUD, Veröffentlichen mit einem „ja“ (Netlify) |
| Sagt dir, wenn er Zugriff braucht | ✅ | Panel „Zugriffe“ im HUD + `jarvis-plus status` + Jarvis meldet es von selbst |
| Kennt dich + ademidigital | ✅ | Privates Paket: Profil, Business-Wissen, Marken-Skill (nicht im öffentlichen Repo) |
| Connectoren wie Higgsfield | ✅ | `jarvis-plus connect higgsfield` (auch canva, notion, figma, 21st) |
| Ruft dich an, Erinnerungen | ✅ | Twilio + geplante Aufgaben |
| Whoop, Garmin, Stress | ✅ | Wächter meldet sich bei hohem Stress selbst |
| Coach, Kunden, Gmail/Kalender | ✅ | wie vorher |
| Instagram | ⚠️ teilweise | Posts, Kommentare, Antworten, Foto posten, Statistiken. Keine DMs (braucht geprüfte Meta-App) |
| Jede App auf dem Handy steuern | ❌ | iPhone/Android erlauben das keinem Assistenten. Alles mit Schnittstelle lässt sich anbinden |

---

## Installation

### Was du brauchst

| Konto | Wofür | Kosten |
|---|---|---|
| [Anthropic API](https://console.anthropic.com) | Jarvis' Gehirn (Claude) | pro Nutzung; mit Haiku als Standard meist wenige Franken im Monat |
| Telegram + [@BotFather](https://t.me/BotFather) | Jarvis überall anschreiben | kostenlos |
| [Whoop Developer](https://developer.whoop.com) | Client-ID steht schon drin, du brauchst das **Client Secret** | kostenlos |
| Garmin Connect | dein normales Login | kostenlos |
| [Twilio](https://www.twilio.com) | Anrufe + SMS | Nummer + Rappen pro Anruf |
| [Netlify](https://app.netlify.com) | Websites online stellen | kostenlos |
| Instagram Business/Creator + [Meta-App](https://developers.facebook.com) | Instagram-Funktionen | kostenlos |
| Higgsfield, Canva, Notion, Figma | Connectoren | deine bestehenden Konten |
| [Tailscale](https://tailscale.com) | HUD sicher am Handy, auch unterwegs | kostenlos |

> **Wichtig, weil du 16 bist:** Anthropic (API) und Twilio verlangen volljährige
> Kontoinhaber. Lass diese Konten von einem Elternteil anlegen.
> Kostenlose Alternative: Jarvis lokal mit Ollama (`config.toml`, Variante B).

### 1. Installieren

**Mac / Linux:**
```bash
git clone https://github.com/berinademi57-creator/claude.git
cd claude && git checkout claude/bold-mendel-5rrt2t
# privates Paket (jarvis-privat.zip) nach jarvis/private/ entpacken
bash jarvis/install.sh
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/berinademi57-creator/claude.git
cd claude; git checkout claude/bold-mendel-5rrt2t
# privates Paket (jarvis-privat.zip) nach jarvis\private\ entpacken
powershell -ExecutionPolicy Bypass -File jarvis\install.ps1
```

Der Installer installiert OpenJarvis und jarvis-plus, richtet Konfiguration,
Persönlichkeit, dein Profil und dein Business-Wissen ein, installiert alle Skills und
startet Jarvis im Hintergrund, sobald der Claude-Key eingetragen ist.
Erneut ausführen ist sicher; `--update` holt neue Versionen von `config.toml`/`SOUL.md`.

### 2. Zugänge eintragen
1. `~/.openjarvis/credentials.toml`: `ANTHROPIC_API_KEY`, `TELEGRAM_BOT_TOKEN`
2. `~/.openjarvis/jarvis-plus.env`: Whoop-Secret, Garmin, Twilio, Instagram, Netlify, Telegram-Chat-ID
3. Telegram-Chat-ID (über [@userinfobot](https://t.me/userinfobot)) auch in
   `~/.openjarvis/config.toml` bei `[channel.telegram] allowed_chat_ids` eintragen

`jarvis-plus status` zeigt jederzeit, was noch fehlt und wie du es bekommst.

### 3. Verbinden
```bash
jarvis-plus whoop-login
jarvis-plus garmin-login
jarvis connect gdrive              # Gmail + Kalender + Tasks
jarvis-plus connect higgsfield     # Browser-Login, Higgsfield-Abo nötig
jarvis-plus connect canva
jarvis-plus connect notion
jarvis-plus connect 21st           # vorher TWENTYFIRST_API_KEY eintragen
jarvis-plus autostart              # ab jetzt immer im Hintergrund
```

### 4. Benutzen
- **PC:** http://localhost:8765 öffnen → Mikrofon antippen oder Leertaste → reden.
  Mit **WAKE-WORD** hört Jarvis dauerhaft zu, sobald du „Jarvis …“ sagst.
- **Handy:** [Tailscale](https://tailscale.com) auf PC + Handy installieren, am PC
  `tailscale serve --bg 8765` ausführen und die angezeigte `https://…ts.net`-Adresse am Handy
  öffnen → „Zum Home-Bildschirm“. Das Mikrofon braucht HTTPS, Tailscale liefert das.
- **Telegram:** dem Bot schreiben, überall.
- `/smart` vor eine Nachricht → stärkeres Modell erzwingen, `/schnell` → günstiges.

---

## Websites bauen

Sag z.B. *„Bau mir eine Landingpage für einen Coiffeur in Biel, dunkel, edel, mit
Terminbuchungs-Button“*. Jarvis
1. nimmt automatisch das stärkere Modell,
2. folgt dem Skill `krasse-websites` + den Design-Skills,
3. speichert die Seite (`~/Jarvis-Websites/<name>/`) → sie **springt im HUD auf**,
4. ändert, was du willst,
5. stellt sie nach deinem „ja“ auf Netlify online und nennt den Link.

Installierte Website-Skills (Open Source):

| Skill | Quelle | Wofür |
|---|---|---|
| `krasse-websites` | dieses Repo | Ablauf, Stil-Rezepte, Wow-Momente, Checkliste |
| `frontend-design` | [anthropics/skills](https://github.com/anthropics/skills) | weg vom generischen KI-Look |
| `web-artifacts-builder`, `theme-factory` | anthropics/skills | komplexere Web-Apps, Farbthemen |
| `impeccable` | [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | Design-Sprache und Feinschliff |
| `design-taste-frontend` | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | Firmen-Websites auf Top-Niveau |
| `web-design-guidelines` | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | Qualitäts- und UX-Regeln |
| `ademi-digital` | privates Paket | Marke und Content von ADEMI DIGITAL |

Ein Beispiel liegt in `examples/demo-website/` (fiktives Fitnessstudio).

---

## Connectoren

| Name | Was | Hinweis |
|---|---|---|
| `higgsfield` | Bilder/Videos, Generierungen ansehen | Abo nötig, kostet Credits |
| `canva` | Designs suchen, erstellen, exportieren | |
| `notion` | Seiten, Datenbanken | |
| `figma` | Designs lesen | |
| `21st` | fertige UI-Komponenten für Websites | API-Key von 21st.dev |
| Gmail, Kalender, Drive, Strava, Outlook, Slack … | eingebaut in OpenJarvis | `jarvis connect --help` |

Weitere MCP-Server kannst du in `~/.openjarvis/mcp-servers.json` eintragen.
Die Connectoren aus deinem claude.ai-Konto lassen sich nicht direkt übertragen;
jeder braucht einmal den Login über `jarvis-plus connect`.

---

## jarvis-plus Befehle

```
jarvis-plus hud            Oberfläche (http://localhost:8765), --demo = Beispieldaten
jarvis-plus autostart      immer im Hintergrund (an|aus)
jarvis-plus status         welche Zugänge fehlen
jarvis-plus connect NAME   Connector verbinden · connectors = Liste
jarvis-plus check          Stress-Check jetzt
jarvis-plus watch          Wächter (läuft mit Autostart automatisch)
jarvis-plus test-call / test-telegram
```

MCP-Tools für Jarvis: Gesundheit (`whoop_daten`, `garmin_daten`, `stress_check`),
Kontakt (`mich_anrufen`, `mir_sms_schicken`, `mir_telegram_schicken`), Profil
(`ueber_mich_lesen`, `ueber_mich_merken`), Kunden (`kunde_*`, `kunden_*`), Instagram
(`instagram_*`), Websites (`website_speichern`, `websites_liste`,
`website_veroeffentlichen`), `zugriffe_status`.

Tests: `cd jarvis/jarvis_plus && pip install -e '.[dev]' && pytest`

### Hinweis zu Garmin
Garmin hat keine offizielle API für Privatpersonen. `garminconnect` ist eine verbreitete
inoffizielle Bibliothek; bei Garmin-Änderungen hilft meist `pip install -U garminconnect`.

---

## Sicherheit & Privatsphäre
- **Dieses Repo ist öffentlich.** Profil und Business-Wissen liegen deshalb im privaten
  Paket (`jarvis/private/`, von Git ignoriert), nie im Repo. Am besten stellst du das Repo
  auf GitHub auf privat (Settings → Danger Zone → Change visibility).
- Alle Keys liegen nur auf deinem Rechner (`~/.openjarvis/`, Dateirechte 600).
- HUD nur lokal oder über Tailscale; im WLAN nur mit `HUD_TOKEN`.
- Telegram ist auf deine Chat-ID beschränkt; Jarvis ruft/schreibt nur **dich** an.
- Veröffentlichen (Instagram, Websites) und Mails an andere nur nach deinem „ja“.
