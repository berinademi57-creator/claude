# Jarvis einrichten: jede App, jeder Schritt

Arbeite die Stufen der Reihe nach ab. Nach jeder Stufe zeigt dir
`jarvis-plus status`, was noch fehlt (im HUD: Knopf **ZUGRIFFE**).

> **Keys nie in Chats oder Screenshots schicken.** Trag sie direkt in die Dateien
> auf deinem PC ein (`~/.openjarvis/…`). Jarvis sagt dir selbst, was fehlt.

---

## Dein Stand (was ich weiss)

| | Was | Status |
|---|---|---|
| ✅ | Whoop Developer-App (Client ID + Secret) | im privaten Paket, wird automatisch eingetragen |
| 🟡 | Twilio (Trial) | Auth Token im privaten Paket · **fehlt:** Account SID, Twilio-Nummer, deine Handynummer verifizieren |
| ❌ | **Anthropic API-Key** (Jarvis' Gehirn) | **das Wichtigste, ohne geht nichts** |
| ❌ | Telegram-Bot | fehlt |
| ❌ | Tailscale (Handy-Zugang + Telefon) | fehlt |
| ❌ | Chrome-Erweiterung „Playwright MCP Bridge“ | fehlt |
| ❌ | Garmin-Login | nur ein Befehl (Stufe 3) |
| ❌ | Google (Gmail, Kalender, Drive) | nur ein Befehl (Stufe 6) |
| ❌ | Netlify, Instagram-Token, 21st.dev | fehlt (Stufe 6) |
| 🟡 | Higgsfield, Canva, Notion, Figma | Konten hast du, je ein Login-Befehl (Stufe 6) |

> **Weil du 16 bist:** Anthropic und Twilio verlangen volljährige Kontoinhaber. Lass die
> Konten (auch das bestehende Twilio-Konto) auf einen Elternteil laufen. Der zahlt dann
> auch, und ihr könnt ein Ausgabelimit setzen.

---

## Stufe 1: Programme auf dem PC (10 Min)

1. **Google Chrome** installieren (für HUD-Fenster, Browser-Steuerung, Spracheingabe).
2. **Git**: Windows `winget install Git.Git` · Mac: kommt mit `xcode-select --install`.
3. **Node.js 22**: Windows `winget install OpenJS.NodeJS.LTS` · Mac `brew install node`
   (oder Installer von nodejs.org). Nötig für Connectoren und Browser-Steuerung.
4. Python, uv und OpenJarvis installiert der Jarvis-Installer automatisch.

## Stufe 2: Jarvis installieren (10 Min)

1. Terminal öffnen (Windows: PowerShell, Mac: Terminal).
2. Repo holen:
   ```bash
   git clone https://github.com/berinademi57-creator/claude.git
   cd claude
   git checkout claude/bold-mendel-5rrt2t
   ```
3. **jarvis-privat.zip** (aus dem Chat) in den Ordner `claude/jarvis/` entpacken, sodass es
   `claude/jarvis/private/…` gibt. Darin: dein Profil, ademidigital-Wissen, Marken-Skill,
   Whoop- und Twilio-Schlüssel.
4. Installer starten:
   - Mac: `bash jarvis/install.sh`
   - Windows: `powershell -ExecutionPolicy Bypass -File jarvis\install.ps1`
5. Danach **Terminal neu öffnen**, damit `jarvis` und `jarvis-plus` gefunden werden.

## Stufe 3: Gehirn + Gesundheit (15 Min)

### Anthropic (Pflicht)
1. [console.anthropic.com](https://console.anthropic.com) → Konto anlegen (Elternteil).
2. **Billing** → Guthaben aufladen (10–20 CHF reichen für den Start).
   **Limits** → monatliches Ausgabelimit setzen, z.B. 20 CHF.
3. **API Keys → Create Key** → kopieren.
4. In `~/.openjarvis/credentials.toml` bei `ANTHROPIC_API_KEY = "…"` einfügen.

### Whoop (fast fertig)
1. Secret ist schon eingetragen. Im Terminal: `jarvis-plus whoop-login`
2. Browser öffnet sich → bei Whoop einloggen → **Allow**. Fertig.

### Garmin
1. In `~/.openjarvis/jarvis-plus.env`: `GARMIN_EMAIL=` und `GARMIN_PASSWORD=` eintragen.
2. `jarvis-plus garmin-login` → Code aus der Garmin-Mail/App eingeben.
3. Danach `GARMIN_PASSWORD` wieder löschen. Jarvis merkt sich den Login selbst.
   (Einen Garmin-Token aus dem Garmin-Portal brauchst du dafür nicht.)

Test: `jarvis-plus check` → zeigt Recovery, HRV, Schlaf, Stress.

## Stufe 4: Handy (Chat, HUD, Stimme) (15 Min)

### Telegram (chatten von überall)
1. Telegram auf Handy + PC installieren.
2. [@BotFather](https://t.me/BotFather) → `/newbot` → Name `Jarvis` → Username z.B. `berin_jarvis_bot`
   → **Token** kopieren.
3. [@userinfobot](https://t.me/userinfobot) → schreibt dir deine **Chat-ID** (Zahl).
4. Eintragen:
   - `~/.openjarvis/credentials.toml` → `TELEGRAM_BOT_TOKEN = "…"`
   - `~/.openjarvis/jarvis-plus.env` → `TELEGRAM_BOT_TOKEN=…` und `TELEGRAM_CHAT_ID=…`
   - `~/.openjarvis/config.toml` → `[channel.telegram]` `allowed_chat_ids = "DEINE-ID"` und
     `[proactive]` `notification_channel = "telegram:DEINE-ID"`
5. Test: `jarvis-plus test-telegram`

### Tailscale (HUD + Stimme auf dem Handy, auch unterwegs)
1. [tailscale.com](https://tailscale.com) → mit Google anmelden → App auf **PC und iPhone**
   installieren, beide mit demselben Konto.
2. Am PC: `tailscale serve --bg 8765`
3. Es erscheint eine Adresse `https://<pc-name>.<…>.ts.net` → am iPhone in Safari öffnen →
   Teilen → **Zum Home-Bildschirm**. Jetzt hast du Jarvis als App mit Orb, Stimme und
   📞-Anruf-Modus.

## Stufe 5: Telefonieren (20 Min)

Zwei Wege:
- **📞 im HUD (gratis):** Anruf-Modus in der Jarvis-App, freihändig reden über Internet.
- **Echte Telefonleitung (Twilio):** Jarvis ruft dich auf deiner normalen Nummer an
  (Erinnerungen, Weckruf, Stress-Alarm), und ihr redet richtig miteinander.

Twilio-Einrichtung (dein Trial-Konto):
1. Twilio-Konsole → **Account SID** mit dem **Kopier-Knopf** kopieren (im Screenshot war sie
   abgeschnitten) → `jarvis-plus.env` → `TWILIO_ACCOUNT_SID=…`
2. **Phone Numbers → Manage → Verified Caller IDs** → deine Handynummer verifizieren
   (Trial-Konten dürfen nur verifizierte Nummern anrufen).
3. **Phone Numbers → Buy a number** → Trial-Nummer holen (eine US-Nummer geht sofort;
   Schweizer Nummern brauchen Ausweis/Adresse = „Regulatory Bundle“).
4. Eintragen: `TWILIO_FROM_NUMBER=+1…` (Twilio-Nummer), `MY_PHONE_NUMBER=+41…` (dein Handy).
5. Tailscale **Funnel** erlauben: beim ersten Mal zeigt der nächste Befehl einen Link,
   dort „Funnel“ aktivieren.
6. `jarvis-plus telefon-einrichten` → richtet alles ein (geheime Adresse, Twilio-Nummer).
7. Test: `jarvis-plus test-call` (nur Ansage) oder sag Jarvis: „Ruf mich an.“

Gut zu wissen:
- Trial: vor jedem Anruf spielt Twilio eine kurze Ansage („press any key“). Nach Upgrade weg.
- **Lass dich lieber von Jarvis anrufen**, als die US-Nummer anzurufen. Ein Anruf in die
  USA kostet dich Auslandsgebühren, der Anruf von Jarvis nur Twilio-Guthaben.
- Nur deine Nummer kommt durch, alle anderen Anrufer werden abgewiesen.

## Stufe 6: PC-Steuerung + Business (30 Min)

### Browser mit deinen gespeicherten Logins
1. Chrome Web Store → **„Playwright MCP Bridge“** installieren.
2. Erweiterung öffnen → **Token** kopieren → `~/.openjarvis/credentials.toml`:
   ```toml
   [browser]
   PLAYWRIGHT_MCP_EXTENSION_TOKEN = "…"
   ```
3. Jetzt kann Jarvis in deinem echten Chrome klicken und tippen, mit allen Logins
   (Instagram, Gmail, Shopify, Bexio …). Tipp: Wenn du willst, dass er nur Business-Seiten
   sieht, leg in Chrome ein eigenes Profil „Jarvis“ an und installier die Erweiterung nur dort.

### Desktop-Apps steuern
- **Windows:** richtet der Installer ein (Windows-MCP).
- **Mac:** Systemeinstellungen → Datenschutz & Sicherheit → **Bedienungshilfen** und
  **Automation** → Terminal und node erlauben (fragt beim ersten Mal von selbst).
- Apps, Links und Dateien öffnen kann Jarvis immer, auch ohne das.

### Google (Gmail, Kalender, Drive)
`jarvis connect gdrive` → mit Google einloggen → alles erlauben.

### Websites online stellen (Netlify, gratis)
1. [app.netlify.com](https://app.netlify.com) → mit GitHub anmelden.
2. Avatar → **User settings → Applications → Personal access tokens → New token**.
3. `jarvis-plus.env` → `NETLIFY_AUTH_TOKEN=…`

### Instagram (Business/Creator)
1. In der Instagram-App: Einstellungen → Kontotyp → **Professionelles Konto** (Creator/Business).
2. [developers.facebook.com](https://developers.facebook.com) → My Apps → **Create App** →
   Use Case „Instagram API“ (Instagram Login) → dein Instagram-Konto hinzufügen →
   **Access Token generieren**.
3. `jarvis-plus.env` → `INSTAGRAM_ACCESS_TOKEN=…` (gilt 60 Tage, dann neu erzeugen).

### Connectoren (je ein Befehl, Login im Browser)
```bash
jarvis-plus connect higgsfield   # Bilder/Videos (Abo, kostet Credits)
jarvis-plus connect canva
jarvis-plus connect notion
jarvis-plus connect figma
jarvis-plus connect 21st         # vorher Key von 21st.dev/mcp → TWENTYFIRST_API_KEY
```

### Optional
- **OpenAI-Key** (`credentials.toml`) → natürlichere deutsche Stimme in Terminal/Desktop-App.
  Im HUD ist die Stimme gratis über den Browser.

## Stufe 7: Immer im Hintergrund (5 Min)

1. `jarvis-plus autostart`
   - startet **Jarvis-Gehirn** (`jarvis serve`), **HUD + Telefon-Leitung** und den
     **Wächter** bei jedem Hochfahren, startet sie neu, falls sie abstürzen,
   - öffnet beim Anmelden das **HUD-Fenster** (wie im Video).
2. PC darf nicht schlafen, wenn Jarvis erreichbar sein soll:
   - Windows: Einstellungen → System → Energie → Standbymodus bei Netzbetrieb: **Nie**
   - Mac: Systemeinstellungen → Energie → **Ruhezustand verhindern, wenn Display aus**
   - Tipp: Ein alter Laptop oder Mac mini als „Jarvis-Server“ ist ideal.
3. Prüfen, ob alles läuft:
   - HUD: http://localhost:8765 (oben „ONLINE“)
   - Windows: Aufgabenplanung → Aufgaben „Jarvis-…“
   - Mac: `launchctl list | grep ademidigital`
   - Logs: `~/.openjarvis/logs/`
4. Ausschalten: `jarvis-plus autostart aus`

## Stufe 8: Fertig-Check

`jarvis-plus status` → alles ✅? Dann:
- **PC:** HUD-Fenster ist offen → „Jarvis, guten Morgen“ oder Leertaste.
- **Handy:** Jarvis-App vom Home-Bildschirm (Tailscale) oder Telegram.
- **Telefon:** „Jarvis, ruf mich in 10 Minuten an“.
- **Website:** „Bau mir eine Landingpage für einen Coiffeur in Biel, dunkel, mit 3D-Effekt“.

---

## Sicherheit: deine geteilten Schlüssel

Du hast im Chat den **Twilio Auth Token**, das **Whoop Client Secret** und einen
**Garmin-Token** geschickt. Sie stehen damit im Chatverlauf. Am sichersten ist es, sie
**neu zu erzeugen** und nur die neuen in `~/.openjarvis/jarvis-plus.env` einzutragen:
- Twilio: Konsole → Account → **API keys & tokens** → Auth Token → neuen anfordern („Request
  secondary token“) → zum Haupt-Token machen → in `jarvis-plus.env` ersetzen.
- Whoop: developer.whoop.com → deine App → Secret neu erzeugen → `WHOOP_CLIENT_SECRET`
  ersetzen → `jarvis-plus whoop-login`.
- Garmin: Falls der Token ein Login-Token war: Garmin-Passwort ändern. Jarvis braucht ihn nicht.

## Kosten im Überblick

| Dienst | Kosten |
|---|---|
| Anthropic (Claude) | nach Nutzung; Haiku ist Standard (günstig), Sonnet nur für Websites/Code. Limit setzen! |
| Twilio | Trial-Guthaben gratis; danach Nummer ca. 1–2 USD/Monat + Rappen pro Minute |
| Higgsfield | dein Abo-Guthaben (Jarvis fragt vorher) |
| Alles andere (Telegram, Tailscale, Netlify, Whoop, Garmin, Google, Skills) | gratis |

## Was Jarvis nicht kann (ehrlich)

- Apps auf dem **iPhone** fernsteuern (Apple erlaubt das nicht). Auf dem **PC** geht fast alles.
- Instagram-**DMs** über die offizielle API (braucht eine von Meta geprüfte App).
  Über die Browser-Steuerung kann er Instagram Web aber wie du bedienen; mach das sparsam,
  sonst sperrt Instagram den Account.
- Logins, die nicht gespeichert sind, oder 2-Faktor-Codes: da fragt er dich.
- Ohne laufenden PC ist er offline. Telegram-Nachrichten kommen an, sobald er wieder läuft.
