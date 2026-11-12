# Compliance-Check: Website Physiotherapie Central Plaza GmbH

> **Hinweis:** Diese Prüfung unterstützt die Umsetzung, ersetzt aber keine Rechtsberatung.
> Rechtliche Anforderungen ändern sich; im Zweifel eine Fachperson (z. B. Anwalt/Anwältin
> oder den Berufsverband Physioswiss) beiziehen. Stand: November 2026.

## Zusammenfassung
**Freigabe mit Bedingungen.** Technik, Datenschutz und Impressum sind sauber umgesetzt.
Offen sind nur Punkte, die der Kunde bestätigen muss (Titel, Bildrechte, FAQ-Inhalte).

## Anwendbare Vorschriften

| Vorschrift | Bezug zur Website | Wichtigste Anforderungen |
|---|---|---|
| **UWG Art. 3 Abs. 1 lit. s** | Angebot von Dienstleistungen im Internet | Klare Angaben zu Identität und Kontaktadresse inkl. E-Mail |
| **UWG Art. 3 Abs. 1 lit. b/c** | Leistungsbeschreibungen, Titel | Keine unrichtigen/irreführenden Angaben, keine unzutreffenden Titel |
| **OR (Firmenrecht)** | Firmenname | Eingetragene Firma «Physiotherapie Central Plaza GmbH» unverändert verwenden |
| **DSG (revDSG) + DSV** | Kontaktformular, Hosting, Logfiles | Informationspflicht (Art. 19), Datensicherheit (Art. 8), Auftragsbearbeitung (Art. 9), Bekanntgabe ins Ausland (Art. 16) |
| **DSGVO** (nur subsidiär) | Besucher aus der EU | Rechtsgrundlagen nennen, Betroffenenrechte |
| **GesBG Art. 16 lit. e** | Werbung einer Gesundheitsfachperson | Werbung muss objektiv, bedarfsgerecht, nicht irreführend und nicht aufdringlich sein |
| **Kantonales Gesundheitsrecht Luzern** | Berufsausübung | Berufsausübungsbewilligung; sachliche Werbung |
| **StGB Art. 321 / DSG Art. 62** | Berufsgeheimnis | Gesundheitsdaten vertraulich; nicht über die Website erheben |
| **URG (Urheberrecht)** | Fotos, Logo, Schriften | Nutzungsrechte für alle Bilder; Schriftlizenz (OFL) |
| **FMG Art. 45c** | Cookies | Information bei Cookies – hier nicht nötig, da keine Cookies |
| **BehiG Art. 6** | Barrierefreiheit (private Anbieter) | Keine Diskriminierung; freiwillig WCAG 2.1 AA umgesetzt |

## Anforderungen

| # | Anforderung | Status | Massnahme |
|---|---|---|---|
| 1 | Impressum mit Firma, Adresse, E-Mail, vertretungsberechtigter Person, UID | ✅ erfüllt | UID CHE-149.883.560 in Zefix geprüft |
| 2 | Datenschutzerklärung (Verantwortlicher, Zwecke, Empfänger, Ausland, Rechte, EDÖB) | ✅ erfüllt | – |
| 3 | Bekanntgabe in die USA (Netlify) | ✅ erfüllt | Netlify ist unter dem Swiss-U.S. DPF zertifiziert (Angemessenheit durch Bundesrat) |
| 4 | Auftragsbearbeitungsvertrag mit Netlify | ⚠️ offen | DPA im Netlify-Konto herunterladen und ablegen |
| 5 | Datensicherheit (TLS, Härtung) | ✅ erfüllt | HTTPS/HSTS, CSP, keine Drittanbieter-Skripte |
| 6 | Keine Gesundheitsdaten über das Formular erheben | ✅ erfüllt | Hinweis im Formular; keine Gesundheitsfelder |
| 7 | Löschkonzept Formularanfragen | ⚠️ organisatorisch | Anfragen spätestens nach 12 Monaten in Netlify löschen (so in der DSE versprochen) |
| 8 | Sachliche Gesundheitswerbung, keine Heilversprechen | ✅ erfüllt | Formulierungen mit «kann …», keine Superlative, keine Patientenbewertungen |
| 9 | Titel/Abschlüsse korrekt | ❓ unbekannt | Kunde bestätigt B.Sc., M.Sc. Neurorehabilitation, Master Ultraschalldiagnostik, Anerkennung in der Schweiz |
| 9a | Dry Needling nur mit Ausbildung | ❓ unbekannt | Physioswiss-Positionspapier: Dry Needling nur mit SRK-Anerkennung und standardisierter Dry-Needling-Ausbildung → Kunde bestätigt Zertifikat, sonst Leistung entfernen |
| 10 | Bildrechte Gerätefotos & Dry-Needling-Foto | ❓ unbekannt | Erlaubnis der Hersteller/Quelle prüfen oder durch eigene Fotos ersetzen |
| 11 | Bildrechte Unsplash-Bild (Ultraschall) | ✅ erfüllt | Unsplash-Lizenz erlaubt kommerzielle Nutzung |
| 12 | Cookies / Tracking | ✅ nicht vorhanden | Kein Banner nötig |
| 13 | Google Fonts / Maps-Einbettung | ✅ nicht vorhanden | Schriften lokal, Karten nur als Link |
| 14 | Barrierefreiheit | ✅ erfüllt | axe-core 0 Verstösse, Kontrast ≥ 4.5:1 |

## Risiken

| Risiko | Schwere | Massnahme |
|---|---|---|
| Fremde Gerätefotos ohne Erlaubnis | Mittel | Hersteller anfragen (meist problemlos) oder eigene Fotos der Geräte in der Praxis machen |
| Unbestätigte Angaben zu Titeln/Erfahrung | Mittel | Vor Livegang vom Kunden schriftlich bestätigen lassen (E-Mail genügt) |
| FAQ zur Kostenübernahme passt nicht zur Praxis | Niedrig | Kunde prüft; Text ist bewusst vorsichtig formuliert |
| Formularanfragen werden nicht gelöscht | Niedrig | Jährliche Erinnerung im Kalender |
| Spätere Ergänzung von Tracking/Buchungstool ohne DSE-Anpassung | Mittel | Bei jeder neuen Einbindung: Datenschutzerklärung und `_headers` (CSP) anpassen |

## Empfohlene Massnahmen (Priorität)
1. **Kunde bestätigt** Titel, Abschlüsse, Dry-Needling-Ausbildung, Neurorehabilitations-Text und FAQ (schriftlich).
2. **Bildrechte klären** für Gerätefotos und Dry-Needling-Bild – sonst ersetzen.
3. **Netlify-DPA ablegen** und Löschroutine für Formularanfragen einplanen.

## Freigaben

| Wer | Warum | Status |
|---|---|---|
| Hasan Zećiri (Geschäftsführer) | Richtigkeit aller Inhalte, Titel, Bildrechte | ausstehend |
| optional: Physioswiss / Rechtsberatung | Gesundheitswerbung im Zweifelsfall | optional |

## Weitere Prüfung empfohlen
- Falls später eine **Online-Terminbuchung** (z. B. externes Buchungstool) eingebunden wird:
  Datenschutzerklärung, CSP und ggf. Auftragsbearbeitung neu prüfen.
- Falls **Preise** auf der Website genannt werden: Preisbekanntgabeverordnung (PBV) beachten
  (tatsächlich zu bezahlende Preise in CHF).
- Allgemein für die Praxis (nicht Website): Verzeichnis der Bearbeitungstätigkeiten für
  Patientendaten (DSG Art. 12 / DSV Art. 24) prüfen, da regelmässig Gesundheitsdaten bearbeitet werden.
