# Kalorien-Tracker + Whoop

Eine React-Native-App (Expo, iOS + Android aus **einer** Codebase) für
Kalorien-Tracking mit **drei Eingabewegen** und einer **modularen
Whoop-Integration**, die das Tagesziel dynamisch anpasst.

Kernprinzip: **Ehrlichkeit über Genauigkeit.**
- 📷 **Foto** → *Schätzung* (Claude Vision, ±20–30 %) — immer als „geschätzt“ markiert.
- 🏷️ **Barcode** → *exakt* (Open Food Facts).
- ⌨️ **Text + Gramm** → *exakt* (manuell).

Und: **Modularität.** Das Kern-Logging (SQLite) und die Zielberechnung laufen
**komplett ohne Whoop**. Fällt die Whoop-API aus oder läuft das Token ab,
funktioniert die App unverändert weiter — Whoop ist eine optionale Ebene obendrauf.

---

## Features (V1)

1. **Drei Eingabewege**, klar nach Genauigkeit gekennzeichnet. Jeder Eintrag
   speichert: Lebensmittel, Menge, kcal, Protein, Fett, Kohlenhydrate,
   Eingabemethode, Genauigkeit, Zeitstempel.
2. **Tagesziel-Berechnung** aus deinem Profil (Mifflin-St-Jeor BMR → TDEE →
   Ziel). Live: „Noch X kcal, Y g Protein übrig heute“.
3. **Whoop-Integration** (OAuth2). Zeigt **alle** Tagesdaten roh an (Recovery,
   Schlaf inkl. Phasen, Strain/Cycle, Workouts, Körperdaten) und passt das
   Kalorien-/Protein-Ziel dynamisch an.
4. **Tagesübersicht** mit Ring/Balken für Kalorien & Makros, Whoop-Rohdaten und
   Klartext: „Basierend auf deiner Recovery (X %) → heutiges Ziel: Y kcal“.

**Nicht in V1** (bewusst): Shopify/Notion/Gmail/Kalender, Sprachsteuerung,
automatische Trainingsplanung.

---

## Projektstruktur

```
App.tsx                     App-Root, verbindet die Provider
src/
  db/
    database.ts             SQLite: Food-Logs (Kern, offline)
    settingsStore.ts        SQLite: Key-Value (Profil)
  models/
    types.ts                Domänentypen + Genauigkeits-Mapping
    whoop.ts                Whoop-Typen
  services/
    goals.ts                Zielberechnung + dynamische Whoop-Anpassung (pure)
    openFoodFacts.ts        Barcode-Lookup (exakt)
    claudeVision.ts         Foto → Schätzung (Claude Vision)
    whoop/
      whoopTokens.ts        OAuth2-Token: Speicherung, Exchange, Refresh
      whoopApi.ts           Whoop-Datenabruf (jeder Endpunkt einzeln abgesichert)
  context/
    ProfileContext.tsx      Profil-State + Basisziel
    DayLogContext.tsx       Heutige Einträge
    WhoopContext.tsx        Whoop-Verbindung + Daten (isoliert, nicht blockierend)
  components/               UI: Ringe, Balken, Whoop-Panel, Badges, UI-Kit
  screens/                  Heute, AddHub, Foto, Barcode, Manuell, Profil
  navigation/               Bottom-Tabs + Add-Stack
  utils/                    config, net (Fetch-Timeout), format
```

---

## Setup

### 1. Voraussetzungen
- Node.js 18+ und npm
- Die **Expo Go** App auf deinem iPhone (App Store) — für schnelles Testen.

### 2. Abhängigkeiten installieren
```bash
npm install
```

### 3. `.env` anlegen
Kopiere `.env.example` nach `.env` und trage deine Werte ein:
```bash
cp .env.example .env
```
```dotenv
WHOOP_CLIENT_ID=999f682c-beaf-4aad-91e4-5371c487d1ce
WHOOP_REDIRECT_URI=http://localhost:8080/callback
WHOOP_CLIENT_SECRET=dein_secret        # nur lokal, siehe Sicherheit
ANTHROPIC_API_KEY=sk-ant-...           # optional, nur für Foto-Schätzung
ANTHROPIC_MODEL=claude-opus-4-8
```
`.env` ist in `.gitignore` — **niemals committen.**

### 4. Starten
```bash
npm start
```
Dann in Expo Go den QR-Code scannen.

---

## Auf dem iPhone (iOS) installieren

**Schnell testen (empfohlen zum Start):**
1. „Expo Go“ aus dem App Store laden.
2. `npm start` am Rechner ausführen (Rechner und iPhone im selben WLAN).
3. Mit der iPhone-Kamera den QR-Code scannen → App öffnet sich in Expo Go.

**Als „echte“ App aufs Handy (eigenes Icon, ohne Expo Go):**
Dafür baust du einen Standalone-Build mit **EAS Build** (Apple-Developer-Konto
nötig, 99 $/Jahr für den App Store; alternativ interner Build):
```bash
npm install -g eas-cli
eas login
eas build --platform ios --profile preview
```
Danach kannst du den Build über TestFlight installieren. Die eine Codebase
baut ebenso Android: `eas build --platform android`.

---

## Whoop-Konfiguration

- Scopes: `read:recovery read:cycles read:sleep read:workout read:profile
  read:body_measurement` plus `offline` (für den Refresh-Token).
- Redirect-URI: `http://localhost:8080/callback` (aus deiner Whoop-App-Config).

**Wichtiger Hinweis zur Redirect-URI:** `localhost:8080/callback` funktioniert
für den Web-/Desktop-Flow. Für einen echten On-Device-Test solltest du in deinem
[Whoop-Developer-Dashboard](https://developer.whoop.com) zusätzlich eine
App-Scheme-Redirect-URI registrieren (z. B. `caltracker://callback`) und in
`.env` `WHOOP_REDIRECT_URI` entsprechend setzen — sonst kann die App den
OAuth-Callback auf dem Gerät nicht empfangen.

---

## Dynamische Zielanpassung (Logik)

In `src/services/goals.ts`, rein funktional und testbar:

- **Basis:** BMR (Mifflin-St-Jeor) × Aktivitätsfaktor = TDEE, dann Ziel-Delta
  (Muskelaufbau +12 %, Cutting −18 %, Recomp 0 %). Protein = g/kg × Gewicht.
- **Whoop-Anpassung:**
  - Niedrige Recovery (< 34 %) **oder** mittlere Recovery + hoher Strain gestern
    (≥ 14) → Kalorien +8 %, Protein +5 % („regenerieren“).
  - Hohe Recovery (≥ 67 %) → Protein-Ziel +10 % hervorgehoben („guter Tag für
    intensives Training“).
  - Sonst: Basisziel unverändert.
- Ohne Whoop-Daten wird **immer** das Basisziel verwendet.

---

## Sicherheit

- **Secrets nur in `.env`**, nie im Code. `.env` ist gitignored.
- **Client-Secret & API-Key im App-Bundle:** Alles unter `extra` in
  `app.config.js` landet im Bundle und ist auslesbar. Für **lokale/persönliche**
  Nutzung ist das ok. Für einen geteilten/produktiven Build:
  - **Whoop:** Setze `WHOOP_TOKEN_PROXY_URL` auf ein eigenes Backend, das den
    Token-Exchange durchführt (Client-Secret bleibt serverseitig). Dann
    `WHOOP_CLIENT_SECRET` im Client leer lassen.
  - **Claude Vision:** Route den Vision-Aufruf über dasselbe Backend und lass
    `ANTHROPIC_API_KEY` im Client leer.
- Tokens werden in `expo-secure-store` (Keychain/Keystore) gespeichert, nicht im
  Klartext.

---

## Hinweis (Alter/Gesundheit)

Die Zielformeln sind für Erwachsene gedacht. Mit 16 bist du noch im Wachstum —
nimm die Zahlen als grobe Orientierung, iss genug für Training **und** Wachstum,
und bespreche Kaloriendefizite/Cutting am besten mit Eltern, Arzt oder Trainer.
Die App zeigt diesen Hinweis auch im Profil-Screen.
