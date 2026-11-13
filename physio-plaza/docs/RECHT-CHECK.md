# Compliance-Check: Website Physiotherapie Central Plaza GmbH

> **Hinweis:** Diese Prüfung unterstützt die Umsetzung, ersetzt aber keine Rechtsberatung.
> Rechtliche Anforderungen ändern sich; im Zweifel eine Fachperson (z. B. Anwalt/Anwältin
> oder den Berufsverband Physioswiss) beiziehen. Stand: November 2026.

## Zusammenfassung
**Freigabe mit Bedingungen.** Technik, Datenschutz und Impressum sind sauber umgesetzt.
Offen sind Punkte, die nur der Kunde bestätigen kann (medizinische Texte der Leistungsseiten, Titel,
Dry-Needling-Zertifikat, Bildrechte, FAQ-Inhalte), sowie eine kurze Vereinbarung zur Auftragsbearbeitung,
falls die Website im Netlify-Konto der Agentur läuft.

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
| 2 | Datenschutzerklärung (Verantwortlicher, Zwecke, Empfänger, Ausland, Rechte, EDÖB) | ✅ erfüllt | Empfänger-Kategorien genannt: Hosting-Anbieter und beauftragte Dienstleister (Web-Agentur) |
| 3 | Bekanntgabe in die USA (Netlify) | ✅ erfüllt | Netlify ist unter dem Swiss-U.S. DPF zertifiziert (Angemessenheit durch Bundesrat) |
| 4 | Auftragsbearbeitungsvertrag mit Netlify | ⚠️ offen | DPA im Netlify-Konto herunterladen und ablegen |
| 4a | Auftragsbearbeitung Praxis ↔ ADEMI DIGITAL (DSG Art. 9) | ⚠️ offen, falls die Website im Konto der Agentur läuft | Wer das Netlify-Konto verwaltet, kann die Formular-Anfragen lesen. Entweder das Konto gehört der Praxis (empfohlen), oder Praxis und Agentur halten schriftlich fest: Bearbeitung nur nach Weisung, Vertraulichkeit, Datensicherheit, Löschung, Netlify als Unterauftragsbearbeiter |
| 5 | Datensicherheit (TLS, Härtung) | ✅ erfüllt | HTTPS/HSTS, CSP, keine Drittanbieter-Skripte |
| 6 | Keine Gesundheitsdaten über das Formular erheben | ✅ erfüllt | Hinweis im Formular; keine Gesundheitsfelder |
| 7 | Löschkonzept Formularanfragen | ⚠️ organisatorisch | Anfragen spätestens nach 12 Monaten in Netlify löschen (so in der DSE versprochen) |
| 8 | Sachliche Gesundheitswerbung, keine Heilversprechen | ✅ erfüllt | Formulierungen mit «kann …» bzw. «mit dem Ziel …», keine Superlative, keine Patientenbewertungen |
| 8a | Medizinische Aussagen der vier Leistungsseiten fachlich richtig | ❓ vom Kunden zu prüfen | Texte zu Anwendungsgebieten, Ablauf und Hinweisen vor der Behandlung stammen nicht vom Therapeuten. Jede Seite trägt den Hinweis «ersetzt keine individuelle ärztliche oder physiotherapeutische Abklärung». Hasan liest gegen und gibt schriftlich frei |
| 8b | Angaben zu Parkplätzen und Anfahrt richtig | ❓ teilweise offen | Bus/Bahn aus offiziellen Fahrplandaten (Stand Nov. 2026). Der Parkplan nennt Daten für zwei Felder (ab 01.12.26 / 01.02.27) – Bedeutung vom Kunden bestätigen lassen |
| 9 | Titel/Abschlüsse korrekt | ✅ weitgehend erfüllt | Gemäss Praxis-Broschüre: B.Sc., M.Sc. Neurorehabilitation; Ultraschalldiagnostik (MSc) ist **in Ausbildung** und so gekennzeichnet (vorher fälschlich als Abschluss). Anerkennung in der Schweiz vom Kunden bestätigen lassen |
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
| Fachlich ungenaue Aussage auf einer Leistungsseite | Mittel | Freigabe durch Hasan vor dem Livegang; Texte sind bewusst zurückhaltend formuliert |
| Leistung beworben, für die die Ausbildung fehlt (Dry Needling) | Mittel–Hoch | Zertifikat bestätigen lassen, sonst Karte und Seite entfernen |
| Agentur hat Zugriff auf Patientenanfragen ohne Vereinbarung | Mittel | Konto auf die Praxis oder kurze schriftliche Vereinbarung (siehe 4a) |
| Netlify-Kontingent aufgebraucht → Website und Formular vorübergehend offline (Betriebsrisiko) | Niedrig–Mittel | Eigenes Konto für die Praxis, Warn-Mails beachten, bei Bedarf bezahlter Plan |
| FAQ zur Kostenübernahme passt nicht zur Praxis | Niedrig | Kunde prüft; Text ist bewusst vorsichtig formuliert |
| Formularanfragen werden nicht gelöscht | Niedrig | Jährliche Erinnerung im Kalender |
| Spätere Ergänzung von Tracking/Buchungstool ohne DSE-Anpassung | Mittel | Bei jeder neuen Einbindung: Datenschutzerklärung und `_headers` (CSP) anpassen |

## Empfohlene Massnahmen (Priorität)
1. **Kunde bestätigt** Titel, Abschlüsse, Dry-Needling-Ausbildung, die Texte der vier Leistungsseiten und die FAQ (schriftlich).
2. **Bildrechte klären** für Gerätefotos und Dry-Needling-Bild – sonst ersetzen.
3. **Konto-Frage klären:** Netlify-Konto der Praxis – oder Vereinbarung zur Auftragsbearbeitung zwischen Praxis und ADEMI DIGITAL.
4. **Netlify-DPA ablegen** und Löschroutine für Formularanfragen einplanen.

## Freigaben

| Wer | Warum | Status |
|---|---|---|
| Hasan Zećiri (Geschäftsführer) | Richtigkeit aller Inhalte (inkl. Leistungsseiten), Titel, Zertifikate, Bildrechte, Parkplan | ausstehend |
| optional: Physioswiss / Rechtsberatung | Gesundheitswerbung im Zweifelsfall | optional |

## Weitere Prüfung empfohlen
- Falls später eine **Online-Terminbuchung** (z. B. externes Buchungstool) eingebunden wird:
  Datenschutzerklärung, CSP und ggf. Auftragsbearbeitung neu prüfen.
- Falls **Preise** auf der Website genannt werden: Preisbekanntgabeverordnung (PBV) beachten
  (tatsächlich zu bezahlende Preise in CHF).
- Allgemein für die Praxis (nicht Website): Verzeichnis der Bearbeitungstätigkeiten für
  Patientendaten (DSG Art. 12 / DSV Art. 24) prüfen, da regelmässig Gesundheitsdaten bearbeitet werden.
