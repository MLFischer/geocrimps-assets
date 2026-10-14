# GeoCrimps V2 – Reel-Produktion

Anleitung für jede Produktion eines neuen Reels, auch für die geplante Claude-Aufgabe. Stand 14.10.2026. Vorbilder im Repo, beide mit Hook 1 + Hook 2 (Abschnitt 5): **r002** (HOLD ID, Ablauf Erklärkette, Fassung 4) und **r003** (MYTH OR ROCK, Ablauf Offene Frage, Fassung 4). r001 (WHODUNIT, Ablauf Quiz) zeigt nur noch die Quiz-Chips; sein Einstieg ist veraltet.

## 1. Auftrag je Lauf

- Genau **ein** Reel: der früheste Slot in `v2/themenplan.json` mit `"reel": null`, dessen Termin mindestens 20 Stunden in der Zukunft liegt.
- Gibt es für diesen Termin schon einen Eintrag in `v2/reels.json`, ist nichts zu tun; das wird gemeldet.
- Ist kein Slot mehr frei, wird ein neuer im Rhythmus angelegt (Dienstag 18:07 Geschichte, Freitag 17:07 Kurzformat, Berliner Zeit, Rotation aus `themenplan.json`), mit einem `"ablauf"`, der sich vom Slot davor unterscheidet (Abschnitt 5). Das Thema kommt dann aus `v2/faktenbasis/Themenbibliothek.md`.
- Ziel: Das Reel liegt spätestens 20 Stunden vor dem Termin mit bestandenem Probelauf als `"ready"` in der Warteschlange.

## 2. Ablauf

1. **Stand holen:** `git pull`. Werkzeuge prüfen: python3 mit Pillow und numpy, ffmpeg mit libx264.
2. **Fakten:** `v2/faktenbasis/<post>/caption.md` und `sources.md` lesen. Jede Aussage im Bild und in der Caption muss dort belegt sein. Für eine neue Aussage wird die Quelle im Web geprüft (Seite öffnen, nicht nur das Suchergebnis) und als neue Zeile in `sources.md` nachgetragen: Aussage, Quelle mit Link, „✅ web-verifiziert <Datum>“. Was sich nicht belegen lässt, fällt weg. Kalibrierungen und Korrekturläufe in `sources.md` gelten weiter.
3. **Skript:** Ablauf aus dem Slot übernehmen (`"ablauf"` in `themenplan.json`: `quiz`, `offene_frage` oder `erklaerkette`, Abschnitt 5). Hook mit Hook-Score, Züge, Payoff, Folge fürs Klettern, Wortzahl. Bildmittel so wählen, dass sich das Reel vom vorigen unterscheidet (Abschnitt 6).
4. **Engine-Skript** `v2/engine/reels/r<NNN>_<format>_<post>.py` auf Basis von `v2/engine/reelkit.py`, `v2/engine/kletter.py` und `v2/engine/klang.py`, Vorlage `r003_mythorrock_015.py` (oder `r002_holdid_029.py`), beide Fassung 4. Slug: `<Termin YYYY-MM-DD>_<formatkurz>-<NN>` mit formatkurz `whodunit`, `holdid`, `rewind`, `scalejump`, `mythorrock`; NN zählt pro Format. In `META` stehen außerdem `ablauf`, `hook1_bis` (Beginn des Übergangs von Hook 1 in die Kopfzeile), `hook_ab` und `hook_bis` (Hook-2-Frage: Beginn des Einblendens und des Ausblendens), `cover_t` (Zeitpunkt des Covers in Hook 2) und `weitere_fragen` (`[[Beginn, Beginn des Ausblendens], …]` je weiterer Frage im Bild, sonst `[]`); das Reel stellt `self.hook1 = reelkit.Hook1(...)` bereit. `reelkit.run` prüft das alles. Der Kopfkommentar nennt Ablauf und Bildmittel (Übergang, Enthüllung, Payoff, Tonart), damit das nächste Reel davon abweichen kann.
5. **Einzelbilder ansehen:** `--stills <Zeitpunkte> --qc <Ordner>` rendern und die PNGs wirklich betrachten: Frame 0, jeder Zug, Payoff, Endsignet. Mindestens: Frame 0, Griff (`t_grab`), „× GEOLOGY“ (`t_geo`), Cover (`cover_t`), jeder Zug, Payoff, Endsignet. Prüfen: nichts abgeschnitten, kein Text über Text, Text außerhalb der Instagram-Zonen, gut lesbar, die Hand des Kletterers sitzt am Griff, das Bild sagt nichts Falsches. Fehler beheben, erneut ansehen.
6. **Komplett rendern:** `python3 <skript> --qc <Ordner>`. Im Bericht muss `"alle_pruefungen_ok": true` stehen (Dauer im Formatrahmen, Hook 1 frei in Frame 0, Kopfzeile frei im Cover, Hook-2-Frage mindestens 3,2 s, jede weitere Frage mindestens 1,2 s, Ablauf wie im Slot und anders als im Slot davor, Payoff bei 65–80 %, höchstens 40 Wörter inklusive Labels, −14 LUFS ± 0,5, True Peak ≤ −1 dBTP). Kontaktbogen und Tonverlauf ansehen.
7. **Caption und erster Kommentar** nach Abschnitt 8.
8. **Eintragen:** Eintrag in `v2/reels.json` mit denselben Feldern wie r003 (auch `"ablauf"`), `"status": "ready"`, `"scheduled"` = Termin des Slots mit Offset. Im Slot in `themenplan.json` die Reel-ID eintragen. QC unter `v2/qc/<slug>/` ablegen (Bericht mit Hook-Score und Faktencheck als JSON, Kontaktbogen als JPG, Tonverlauf als PNG). Zeile in Abschnitt 10 nachtragen. Neue Kenney-Klänge in `v2/engine/sfx/LIZENZEN.md` nachtragen.
9. **Probelauf:** Commit und Push auf `main`. Warten, bis der Lauf „pages build and deployment“ für diesen Commit fertig ist (`gh api repos/MLFischer/geocrimps-assets/actions/runs?head_sha=<sha>`). Dann `v2/probe.trigger` ändern und pushen; der Workflow „Reel-Probelauf“ prüft das nächste Reel ohne bestandenen Probelauf. Ergebnis mit `git pull` holen: `"probe": {"result": "FINISHED"}`.
10. **Fehlschlag:** Probelauf nicht FINISHED oder eine Prüfung nicht ok → `"status": "review"`, `"last_error"` mit Grund, pushen. In der Abschlussmeldung klar sagen, dass dieses Reel **nicht** automatisch erscheint.
11. **Abschlussmeldung an Markus** (Deutsch, kurz): Format, Thema und Hook; wann es erscheint; Link zum Video `https://mlfischer.github.io/geocrimps-assets/reels/<slug>.mp4`; wie man es anhält (`"hold": true` in `v2/reels.json` oder Claude Bescheid geben); Abweichungen oder offene Punkte in einem Satz.

## 3. Nie

- Selbst veröffentlichen. Das macht nur der Workflow `reel-publish.yml` zum Termin; `v2/publish.trigger` bleibt unberührt.
- Secrets lesen oder ändern, Workflows ändern, veröffentlichte Reels oder ihre Einträge ändern oder löschen, etwas in `v1/` ändern.
- Fremdmaterial verwenden: nur die Schriften (OFL) und Klänge (Kenney CC0, selbst erzeugt) aus dem Repo, keine Fotos, keine Musik, keine Logos Dritter, keine echten Personen.

## 4. Formate

| Format | Frage | Ablauf | Länge | Vorlage |
| --- | --- | --- | --- | --- |
| WHODUNIT | Wer oder was hat das gemacht? | Spur → drei Verdächtige → (Quiz: Rate-Pause) → zwei Züge → Urteil | 17,5–22,5 s | r001 (nur Chips) |
| REWIND | Was war dieser Fels früher? | Fels heute → Zähler läuft zurück, Altersfarbe wechselt (`outcrop.AGE`, `age_of`) → Ursprung → zurück ins Heute | 20,5–27,5 s | – |
| SCALE JUMP | Was steckt im Gestein? | Wand → Griff → Korn → Kristall oder Fossil, mit Maßstabsbalken | 14,5–20,5 s | – |
| MYTH OR ROCK | Stimmt, was Kletterer sagen? | Behauptung → (Quiz: TRUE/FALSE und Rate-Pause) → Beleg in zwei Zügen → Urteil TRUE, FALSE, IT DEPENDS oder Stempel MYTH/ROCK | 12,5–17,5 s | r003 |
| HOLD ID | Woher kommt dieser Griff? | Griffform → Querschnitt → Entstehung in zwei Zügen → Stempel „HOLD ID #NN“ | 10,5–14,5 s | r002 |

Dienstags läuft eine Geschichte (WHODUNIT, REWIND, SCALE JUMP), freitags ein Kurzformat (HOLD ID, MYTH OR ROCK). Die Längen enthalten Hook 1 (seit 14.10.2026 je 1,5 s mehr).

## 5. Dramaturgie und Text

- **Topo:** Einstieg (Hook 1 + Hook 2), höchstens drei Züge, Top. Der Payoff kommt bei 65–80 % der Laufzeit, danach höchstens 2 s Folge fürs Klettern, dann das Endsignet (`reelkit.EndSting`, 0,8 s). Das Video endet hart und läuft als Loop weiter.
- **Warum zwei Hooks** (Markus, 13.10.2026: „hook 1 (klettern und geologie) und dann hook 2 (eigentliches reel thema)“): Reel #1 verlor in der ersten Sekunde ein Viertel der Zuschauer (Skip-Rate 52 %), und bei Reel #2 war am Anfang nicht klar, worum es geht. Hook 1 sagt deshalb sofort, wo man gelandet ist; Hook 2 stellt die Frage.
- **Hook 1 (Frame 0 bis ~1,2 s):** `reelkit.Hook1(t_grab≈0,32, t_geo≈0,58, t_out≈1,22)`. GEOCRIMPS klein und CLIMBING groß ab Frame 0; ein Kletterer (`kletter.Climber`, Rückenansicht) ist ab Frame 0 in Bewegung und greift bei `t_grab` den Griff dieses Reels (Kreidewolke `kletter.chalk_puff`, Kreide-Klatsch). Bei `t_geo` schlägt „× GEOLOGY“ ein und das Gestein klappt in seine Geologie auf (`kletter.GeoReveal`: Signatur und Schichten im Felsumriss, radial vom Griff; nur die Signatur, die zur Lithologie passt). Ab `t_out` schrumpfen die großen Wörter in die Kopfzeile „GEOCRIMPS · CLIMBING × GEOLOGY“. Jedes Reel zeigt seinen eigenen Fels und Griff, also nie denselben Vorspann. Das Aufklappen verrät die Antwort nicht (r003 zeigt Sandstein, nicht das nasse Innere).
- **Hook 2 (ab ~1,5 s):** Formatlabel (stencil 40, slate, `reelkit.FORMAT_Y` = 352) und Themenfrage (ab `reelkit.HOOK_Y` = 404) fahren ein und stehen mindestens 3,2 s (`hook_ab` bis `hook_bis`). Die Frage nennt den Gegenstand und den Kletterbezug („WHY DOES THIS EDGE STICK OUT?“, „IT LOOKS DRY. WHY NOT CLIMB?“). Der Kletterer bleibt im Bild. Zwischen Frage und Motiv mindestens 40 px Luft; bei drei Zeilen `display` 164.
- **Cover:** ein Bild aus Hook 2 (`cover_t` ≈ `hook_ab` + 0,85 s) mit Kopfzeile, Formatlabel, Frage und Kletterer am Griff. Hook-1-Wörter und Kopfzeile sind Markenelemente wie das Endsignet: Sie zählen nicht zu den 40 Wörtern, wohl aber zur Lesezeit.
- **Der Kletterer erzählt mit:** Er kommt in mindestens einem Zug oder im Payoff wieder vor (r002: hängt am Gang und klopft ihn ab; r003: wartet auf dem Pad, zieht, der Griff bricht, er fällt aufs Pad). Das macht aus der Erklärung eine Kletterszene.
- **Lesezeit:** Die Hook-Frage steht mindestens 3,2 s bis zum ersten Übergang (Markus, 13.10.2026: „die Frage braucht eine Sekunde länger zum Lesen“). Jede weitere Frage im Bild (Callback, Rate-Pause) steht mindestens 1,2 s.
- **Hook:** höchstens 7 Wörter, verrät die Antwort nicht, zeigt auf etwas, das Kletterer kennen, setzt kein Orts- oder Fachwissen voraus; der Payoff löst genau das ein, was der Hook verspricht.
- **Hook-Score** (für die Hook-2-Frage): fünf Varianten, je 0–2 Punkte für Lücke, Kletterbezug, Bildbarkeit im Hook-2-Bild, Kürze, Deckung durch den Payoff. Genommen wird die beste mit mindestens 8 von 10. Die Tabelle kommt in den QC-Bericht.
- **Reduktion:** Logline in höchstens 15 Wörtern; höchstens drei Züge mit je höchstens 8 Wörtern; höchstens 40 Wörter im Bild inklusive Labels (ohne Hook-1-Wörter, Kopfzeile und Endsignet); höchstens zwei Zahlen, eine davon mit Vergleich. Text sitzt am Detail. Kein Text ohne Bildänderung, keine Dauer-Elemente wie Handle oder Postnummer.
- **Präzision:** Das Bild sagt nichts, was die Caption zurücknehmen muss. „most soluble“ statt „softest“, Umstrittenes vorsichtig formulieren, CO₂ mit Tiefzeichen.
- **Spannung:** Bewegung und Ton ab Frame 0 (`reelkit.run` prüft beides), offene Frage ab Hook 2; ein Puls trägt Hook 2 und die Züge; die Auflösung bleibt verborgen, bis sie dran ist; vor dem Payoff ein steigender Ton, etwa 0,15 s Stille, dann ein Treffer.
- **Rate-Pause (Quiz) ist aktiv, nie still:** Reel #1 verlor in der stillen Rate-Pause fast so schnell Zuschauer wie in der ersten Sekunde. Deshalb Countdown-Ticks (`SoundBook.countdown`), sichtbare Bewegung (Chips pulsen, Zeiger läuft), höchstens 1,5 s.

### Abläufe: nicht jedes Reel gleich

Jeder Slot in `themenplan.json` hat einen Ablauf. Zwei aufeinanderfolgende Reels haben nie denselben. Das Format bestimmt den Inhalt, der Ablauf, wie die Frage gestellt und aufgelöst wird.

| Ablauf | Hook | Mitmachen | Mitte | Auflösung | Vorbild |
| --- | --- | --- | --- | --- | --- |
| `quiz` | Frage oder Behauptung mit Auswahl (A/B/C oder TRUE/FALSE als Chips) | Rate-Pause „Pause. Your guess?“, 1,2–2 s | zwei Züge belegen | Urteil, die richtige Auswahl leuchtet auf. Caption: „Did you guess …?“ | r001 |
| `offene_frage` | offene W-Frage (why, how, what) ohne Auswahl, mindestens 3,2 s | keine Pause. Die Hook-Frage kehrt vor dem Payoff klein zurück (Callback, mindestens 1,2 s, slate) | Zug 1 wirkt harmlos, Zug 2 bringt die Wendung („But …“) | Antwort in höchstens vier Wörtern, groß. Caption fragt nach eigener Erfahrung, nicht nach einem Tipp | r003 |
| `erklaerkette` | Frage an ein sichtbares Detail | keine | Entstehung Schritt für Schritt (Querschnitt, Zeitraffer) | Antwort, dann Stempel oder Folge fürs Klettern | r002 |

## 6. Bild (Corporate Design „Outcrop“)

- 1080 × 1920, 30 fps, gezeichnet mit `outcrop`, `motion` und `reelkit`. Farben aus `outcrop.C` (obsidian, graphite, line, slate, magnesia, water, heat, ice, bio) und `outcrop.AGE`; eigene Zusatzfarben nur sparsam und begründet (Quarz `#DAD5CA` in r002, Kruste `#D8C6A3` in r003).
- Schriften: `display` (Big Shoulders 900) für Hook und Payoff, `display_xb` etwa 118 für Zug-Texte, `stencil` für Formatlabel und Stempel, `text_b` 50–54 für Satzzeilen, `mono` 30 für Labels am Detail.
- Raster: Textspalte x 96–930, rechts davon liegen die Instagram-Buttons; Text ab y 300 (Kopfzeile y 300, Formatlabel 352 und Frage ab 404 nur in Hook 2, Hook-1-Wörter ab y 346, Zug-Texte ab y 352). Darüber liegt die obere Instagram-Zone und im Profilraster der 3:4-Beschnitt (y 240). Unterhalb von etwa y 1450 liegt die Caption von Instagram: dort nichts Wichtiges. Topo-Linie links bei x 56 mit einem Bohrhaken pro Zug (`reelkit.Rail(n)` und `outcrop.route_rail`), das Logo leuchtet beim Payoff.
- Bewegung: Eintritte `seilzug` (0,25–0,4 s), Brüche und Fallen `sturz`, Chips `griff`.
- Kletterer: `kletter.Climber(scale=1.0, width=18.0, torso_w=36.0)`, Posen als Zielpunkte (Becken `hip`, Neigung `lean`, Hände `lh`/`rh`, Füße `lf`/`rf`; Rückenansicht mit `sw=22, hw=13, eb=(-1, 1), kb=(1, -1)`), Arme und Beine per Zwei-Gelenk-IK. Vor dem Rendern nachrechnen, dass jede Hand ihren Griff erreicht (`Climber.joints`, Abstand < 1 px); sonst Becken verschieben. Bouldern: `kletter.crash_pad` unter dem Block. Höhe der Figur etwa 330 px.
- **Abwechslung:** Gegenüber dem vorigen Reel ändert sich mindestens eines dieser Bildmittel: Übergang (`reelkit.wave` Isolinien-Welle, `reelkit.light_sweep` Lichtstreifen, Zoom mit `motion.zoomed`, `reelkit.crackline`), Enthüllung (Querschnitt, Zeitraffer, Bruch, Scan, Maßstabssprung), Payoff (Kreide-Wisch, Stempel, Urteil mit Chip) und die Tonart der Klangfläche (`SoundBook.pads(..., ratio=1.335)` = Quarte höher, `ratio=0.749` = Quarte tiefer). Welche Mittel die bisherigen Reels nutzten, steht in Abschnitt 10; jedes neue Reel trägt dort seine Zeile nach.
- Gesteinssignaturen aus `outcrop` (limestone, dolomite, sandstone, shale, granite, basalt, conglomerate, gneiss) nur, wenn die Lithologie stimmt, sonst neutrale Körnung.

## 7. Ton

- Jedes Reel bringt seinen Ton mit: Fläche (`pad`), Puls und Geräusche auf den Bildwechseln. Vokabular: tick (Kreide), crack (Bruch), drip (Wasser), rumble (Zeitraffer), whoosh (Übergang), clack (Bohrhaken), Klanglogo (`SoundBook.sound_logo`).
- Kino-Klangset (`v2/engine/klang.py`, über `SoundBook.klang`): sub_hit (Einschlag), braam, crunch (Gestein), chalk_slap, reverse (Anschwellen), kick, hat, tick, thud (Aufprall). Alles selbst erzeugt; Kaufbibliotheken (Sonniss, Pixabay u. a.) gehören nicht ins öffentliche Repo, weil ihre Lizenzen die Weitergabe der Rohdateien verbieten.
- Hook 1 hat eine feste Klangsignatur (`SoundBook.hook1(h1, root=...)`): Anschwellen ab 0,0 s, Kreide-Klatsch beim Griff, Einschlag + Braam + Knacken bei „× GEOLOGY“. Den Grundton je Reel wechseln (55 = A in r002, 49 = G in r003, z. B. 58,3 = B), damit nicht jedes Reel gleich klingt.
- Puls (`SoundBook.pulse(t0, t1, bpm, gain=-16, hat_gain=-25, avoid=[große Treffer])`) von Hook 2 bis zur Steigerung, vor `pads()` aufrufen; Tempo je Reel wechseln (r002 116, r003 108 BPM).
- Handy-Lautsprecher geben unter etwa 200 Hz kaum etwas wieder. Die Klänge in `klang.py` haben deshalb einen hörbaren Anschlag; reiner Tiefbass als einziger Treffer reicht nicht.
- Nur Kenney CC0 aus `v2/engine/sfx/kenney` und selbst erzeugte Klänge (`motion.synth`, `klang`).
- Lautheit −14 LUFS, True Peak höchstens −1 dBTP; `reelkit.run` stellt das ein und prüft es.

## 8. Caption und erster Kommentar (Englisch)

1. Erster Satz: „<FORMAT> #NN · <was das Reel zeigt>“. Er ersetzt den Alt-Text. Die Serienmarke steht am Anfang, der Publisher erkennt daran Doppelposts.
2. Zwei bis drei Sätze Erklärung mit den Vorbehalten aus `sources.md`.
3. Eine konkrete Bitte zum Weiterschicken an eine echte Person aus dem Kletteralltag („Send this to the friend who …“).
4. Eine Frage für die Kommentare.
5. „Source: <Autor> (<Jahr>), <Journal>. Full sources in the first comment.“
6. Höchstens fünf Hashtags: zwei Kletter-, zwei Geo-, ein Gebiets-Tag, wenn es passt.

Erster Kommentar: „Sources: “ und die vollständigen Quellen (Autor, Jahr, Titel, Journal oder Herausgeber), getrennt durch „ · “. Titel und Jahr vorher an der Quelle prüfen. `audio_name`: „GeoCrimps – <FORMAT>“.

## 9. Ablage

Video und Cover liegen unter `reels/<slug>.mp4` und `.jpg`, die QC unter `v2/qc/<slug>/`. Die Produktion legt nichts auf Markus’ Mac ab. Das übernimmt die geplante Aufgabe „GeoCrimps – Mac-Ordner abgleichen“ (täglich 12:43, nur wenn der Mac erreichbar ist): Sie kopiert jedes Reel aus `v2/reels.json` nach `V2 Outcrop/04 Reels/<id> <FORMAT> #<NN> (<Tag> <Datum>)/` und schreibt dort den aktuellen Status in `Caption_und_Kommentar.txt`.

## 10. Bildmittel bisher (für die Abwechslung)

Das neue Reel weicht in mindestens einer Spalte vom vorigen ab und hat einen anderen Ablauf. Eine Zeile je Reel, in Terminfolge.

| Reel | Termin | Format | Ablauf | Übergang | Enthüllung | Payoff | Tonart |
| --- | --- | --- | --- | --- | --- | --- | --- |
| r001 | 12.10.2026 | WHODUNIT #01 | quiz | Isolinien-Welle, Riss-Linie | drei Verdächtige als Chips, Regen mit CO₂, Schwachstellen | Urteil, Chip C leuchtet, Kreide-Wisch | Grundton |
| r002 | 14.10.2026 (Neu-Post, Fassung 4) | HOLD ID #01 | erklaerkette | Hook 1: Aufklappen Sandstein am Quarzgang; Schnittlinie, Isolinien-Welle | Querschnitt: Quarz wächst, Zeitraffer der Verwitterung | Antwort groß, Kreide-Wisch, Stempel HOLD ID, Kletterer klopft den Gang ab | Braam A, Puls 116 BPM, Fläche Grundton |
| r003 | 16.10.2026 (Fassung 4) | MYTH OR ROCK #01 | offene_frage | Hook 1: Aufklappen Sandstein am Sloper; Lichtstreifen, Zoom auf den Griff | Zeitraffer Regen und Abtrocknen, Kletterer zieht, der Griff bricht, Sturz aufs Pad | Antwort groß, Stempel MYTH, Kreide-Wisch | Braam G, Puls 108 BPM, Fläche Quarte höher (`ratio=1.335`) |

## 11. Betrieb: was automatisch läuft und was bei einer Meldung zu tun ist

| Was | Wann (Berliner Zeit) | Wo |
| --- | --- | --- |
| Reel produzieren und einplanen | So und Mi 07:41 | geplante Claude-Aufgabe, dieses Dokument |
| Probelauf bei Instagram | nach jeder Produktion | `.github/workflows/reel-probe.yml`, Auslöser `v2/probe.trigger` |
| Veröffentlichen und Quellen-Kommentar | Di 18:07, Fr 17:07 (Versuche alle 15 min, höchstens 6 h verspätet) | `.github/workflows/reel-publish.yml` |
| Instagram-Token erneuern | 1. und 15. des Monats, 06:17 bzw. 05:17 | `.github/workflows/token-refresh.yml`, Status `v2/status/token.json` |
| Wächter (Gesundheitscheck) | täglich 07:23 bzw. 06:23, Di/Fr zusätzlich 20:23 bzw. 19:23 | `.github/workflows/waechter.yml`, Stand `v2/status/waechter.json` |
| Kurzbericht Kennzahlen | Mo 08:47 bzw. 07:47 | `.github/workflows/kennzahlen.yml`, Dateien `v2/kennzahlen/` |
| Mac-Ordner abgleichen | täglich 12:43, wenn der Mac erreichbar ist | geplante Claude-Aufgabe |

Die erste Zeit gilt für die Sommerzeit, die zweite ab 25.10.2026 (die Workflows laufen in UTC).

**Meldungen:** Der Wächter öffnet bei Handlungsbedarf ein Issue „Wächter: …“ im Repo und erwähnt Markus (Mail). Er schließt es selbst, sobald alles passt. Der Kurzbericht erscheint jeden Montag als Kommentar im Issue „Kennzahlen: Kurzbericht“. Typische Meldungen und was hilft:

- **Termin verpasst:** Bis 6 h nach dem Termin `v2/publish.trigger` ändern und pushen (oder Claude Bescheid geben); danach `scheduled` in `v2/reels.json` auf einen neuen Termin setzen.
- **Termin ohne Reel / Reel im Status review:** Die geplante Produktion ist ausgefallen oder hat ein Problem gemeldet. Claude Bescheid geben; Claude produziert das Reel nach diesem Dokument oder behebt den gemeldeten Fehler.
- **Probelauf fehlt oder Video nicht erreichbar:** `v2/probe.trigger` ändern und pushen; hilft das nicht, GitHub Pages prüfen.
- **Instagram-Token ungültig oder läuft ab:** Workflow „Instagram-Token erneuern“ von Hand starten (`v2/token.trigger` ändern). Ist das Token schon abgelaufen, muss Markus im Meta-Entwicklerportal ein neues erzeugen und als Secret `IG_ACCESS_TOKEN` speichern; Tokens gehören nie in Chat, Dateien oder Commits.
- **GH_ADMIN_TOKEN läuft ab** (zuerst am 10.01.2027): Markus legt auf GitHub einen neuen fine-grained Token nur für `geocrimps-assets` mit Schreibrecht auf Secrets an und speichert ihn als Secret `GH_ADMIN_TOKEN`.
- **Workflow fehlgeschlagen:** Link im Issue öffnen; der Lauf zeigt, welcher Schritt scheiterte.

Testen: Eine Zeile, die nur `TESTALARM` enthält, in `v2/waechter.trigger` erzeugt einen Testfehler; der nächste normale Lauf schließt das Issue wieder.
