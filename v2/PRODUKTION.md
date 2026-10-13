# GeoCrimps V2 – Reel-Produktion

Anleitung für jede Produktion eines neuen Reels, auch für die geplante Claude-Aufgabe. Stand 13.10.2026. Vorbilder im Repo: r001 (WHODUNIT, Ablauf Quiz), r002 (HOLD ID, Ablauf Erklärkette), r003 (MYTH OR ROCK, Ablauf Offene Frage, nutzt `reelkit`).

## 1. Auftrag je Lauf

- Genau **ein** Reel: der früheste Slot in `v2/themenplan.json` mit `"reel": null`, dessen Termin mindestens 20 Stunden in der Zukunft liegt.
- Gibt es für diesen Termin schon einen Eintrag in `v2/reels.json`, ist nichts zu tun; das wird gemeldet.
- Ist kein Slot mehr frei, wird ein neuer im Rhythmus angelegt (Dienstag 18:07 Geschichte, Freitag 17:07 Kurzformat, Berliner Zeit, Rotation aus `themenplan.json`), mit einem `"ablauf"`, der sich vom Slot davor unterscheidet (Abschnitt 5). Das Thema kommt dann aus `v2/faktenbasis/Themenbibliothek.md`.
- Ziel: Das Reel liegt spätestens 20 Stunden vor dem Termin mit bestandenem Probelauf als `"ready"` in der Warteschlange.

## 2. Ablauf

1. **Stand holen:** `git pull`. Werkzeuge prüfen: python3 mit Pillow und numpy, ffmpeg mit libx264.
2. **Fakten:** `v2/faktenbasis/<post>/caption.md` und `sources.md` lesen. Jede Aussage im Bild und in der Caption muss dort belegt sein. Für eine neue Aussage wird die Quelle im Web geprüft (Seite öffnen, nicht nur das Suchergebnis) und als neue Zeile in `sources.md` nachgetragen: Aussage, Quelle mit Link, „✅ web-verifiziert <Datum>“. Was sich nicht belegen lässt, fällt weg. Kalibrierungen und Korrekturläufe in `sources.md` gelten weiter.
3. **Skript:** Ablauf aus dem Slot übernehmen (`"ablauf"` in `themenplan.json`: `quiz`, `offene_frage` oder `erklaerkette`, Abschnitt 5). Hook mit Hook-Score, Züge, Payoff, Folge fürs Klettern, Wortzahl. Bildmittel so wählen, dass sich das Reel vom vorigen unterscheidet (Abschnitt 6).
4. **Engine-Skript** `v2/engine/reels/r<NNN>_<format>_<post>.py` auf Basis von `v2/engine/reelkit.py`, Vorlage `r003_mythorrock_015.py`. Slug: `<Termin YYYY-MM-DD>_<formatkurz>-<NN>` mit formatkurz `whodunit`, `holdid`, `rewind`, `scalejump`, `mythorrock`; NN zählt pro Format. In `META` stehen außerdem `ablauf`, `hook_bis` (Sekunde, ab der die Hook-Frage ausgeblendet wird) und `weitere_fragen` (`[[Beginn, Beginn des Ausblendens], …]` je weiterer Frage im Bild, sonst `[]`); `reelkit.run` prüft sie. Der Kopfkommentar nennt Ablauf und Bildmittel (Übergang, Enthüllung, Payoff, Tonart), damit das nächste Reel davon abweichen kann.
5. **Einzelbilder ansehen:** `--stills <Zeitpunkte> --qc <Ordner>` rendern und die PNGs wirklich betrachten: Frame 0, jeder Zug, Payoff, Endsignet. Prüfen: nichts abgeschnitten, kein Text über Text, Text außerhalb der Instagram-Zonen, gut lesbar, das Bild sagt nichts Falsches. Fehler beheben, erneut ansehen.
6. **Komplett rendern:** `python3 <skript> --qc <Ordner>`. Im Bericht muss `"alle_pruefungen_ok": true` stehen (Dauer im Formatrahmen, Meta-Hook frei im Cover, Hook-Frage mindestens 3,2 s, jede weitere Frage mindestens 1,2 s, Ablauf wie im Slot und anders als im Slot davor, Payoff bei 65–80 %, höchstens 40 Wörter inklusive Labels, −14 LUFS ± 0,5, True Peak ≤ −1 dBTP). Kontaktbogen und Tonverlauf ansehen.
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
| WHODUNIT | Wer oder was hat das gemacht? | Spur → drei Verdächtige → (Quiz: Rate-Pause) → zwei Züge → Urteil | 16–21 s | r001 |
| REWIND | Was war dieser Fels früher? | Fels heute → Zähler läuft zurück, Altersfarbe wechselt (`outcrop.AGE`, `age_of`) → Ursprung → zurück ins Heute | 19–26 s | – |
| SCALE JUMP | Was steckt im Gestein? | Wand → Griff → Korn → Kristall oder Fossil, mit Maßstabsbalken | 13–19 s | – |
| MYTH OR ROCK | Stimmt, was Kletterer sagen? | Behauptung → (Quiz: TRUE/FALSE und Rate-Pause) → Beleg in zwei Zügen → Urteil TRUE, FALSE, IT DEPENDS oder Stempel MYTH/ROCK | 11–16 s | r003 |
| HOLD ID | Woher kommt dieser Griff? | Griffform → Querschnitt → Entstehung in zwei Zügen → Stempel „HOLD ID #NN“ | 9–13 s | r002 |

Dienstags läuft eine Geschichte (WHODUNIT, REWIND, SCALE JUMP), freitags ein Kurzformat (HOLD ID, MYTH OR ROCK).

## 5. Dramaturgie und Text

- **Topo:** Einstieg, höchstens drei Züge, Top. Die Frage öffnet sich in Frame 0, der Payoff kommt bei 65–80 % der Laufzeit, danach höchstens 2 s Folge fürs Klettern, dann das Endsignet (`reelkit.EndSting`, 0,8 s). Das Video endet hart und läuft als Loop weiter.
- **Frame 0 ist das Cover:** Motiv, Meta-Hook und Hook vollständig sichtbar, nichts blendet aus dem Leeren ein. Oben links der Meta-Hook (`reelkit.meta_hook()`, y 300, das Logo der Topo-Linie steht links davor), darunter das Formatlabel (stencil 40, slate, `reelkit.FORMAT_Y` = 352), die Hook-Frage ab `reelkit.HOOK_Y` = 404. Meta-Hook und Formatlabel gehen zusammen mit der Hook-Frage. Zwischen Hook und Motiv bleiben mindestens 40 px Luft; bei drei Hook-Zeilen deshalb `display` 164 statt 176 (r002).
- **Meta-Hook** (Markus, 13.10.2026: man soll sofort sehen, wo man gelandet ist): „GEOCRIMPS · GEOLOGY OF CLIMBING“ wie der Profilname, in jedem Reel gleich. Er sagt Neuen in Frame 0, dass es um Klettern und Gestein geht; der Hook bleibt die eigentliche Frage. Markenelement wie das Endsignet: zählt nicht zu den 40 Wörtern, wohl aber zur Lesezeit. `reelkit.run` prüft, dass er im Cover frei steht.
- **Lesezeit:** Die Hook-Frage steht mindestens 3,2 s bis zum ersten Übergang (Markus, 13.10.2026: „die Frage braucht eine Sekunde länger zum Lesen“). Jede weitere Frage im Bild (Callback, Rate-Pause) steht mindestens 1,2 s.
- **Hook:** höchstens 7 Wörter, verrät die Antwort nicht, zeigt auf etwas, das Kletterer kennen, setzt kein Orts- oder Fachwissen voraus; der Payoff löst genau das ein, was der Hook verspricht.
- **Hook-Score:** fünf Varianten, je 0–2 Punkte für Lücke, Kletterbezug, Bildbarkeit in Frame 0, Kürze, Deckung durch den Payoff. Genommen wird die beste mit mindestens 8 von 10. Die Tabelle kommt in den QC-Bericht.
- **Reduktion:** Logline in höchstens 15 Wörtern; höchstens drei Züge mit je höchstens 8 Wörtern; höchstens 40 Wörter im Bild inklusive Labels (ohne Meta-Hook und Endsignet); höchstens zwei Zahlen, eine davon mit Vergleich. Text sitzt am Detail. Kein Text ohne Bildänderung, keine Dauer-Elemente wie Handle oder Postnummer.
- **Präzision:** Das Bild sagt nichts, was die Caption zurücknehmen muss. „most soluble“ statt „softest“, Umstrittenes vorsichtig formulieren, CO₂ mit Tiefzeichen.
- **Spannung:** offene Frage in Frame 0; die Auflösung bleibt verborgen, bis sie dran ist; vor dem Payoff ein steigender Ton, etwa 0,15 s Stille, dann ein Treffer.

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
- Raster: Textspalte x 96–930, rechts davon liegen die Instagram-Buttons; Text ab y 300 (Meta-Hook und Formatlabel nur im Hook, Zug-Texte ab y 352). Darüber liegt die obere Instagram-Zone und im Profilraster der 3:4-Beschnitt (y 240). Unterhalb von etwa y 1450 liegt die Caption von Instagram: dort nichts Wichtiges. Topo-Linie links bei x 56 mit einem Bohrhaken pro Zug (`reelkit.Rail(n)` und `outcrop.route_rail`), das Logo leuchtet beim Payoff.
- Bewegung: Eintritte `seilzug` (0,25–0,4 s), Brüche und Fallen `sturz`, Chips `griff`.
- **Abwechslung:** Gegenüber dem vorigen Reel ändert sich mindestens eines dieser Bildmittel: Übergang (`reelkit.wave` Isolinien-Welle, `reelkit.light_sweep` Lichtstreifen, Zoom mit `motion.zoomed`, `reelkit.crackline`), Enthüllung (Querschnitt, Zeitraffer, Bruch, Scan, Maßstabssprung), Payoff (Kreide-Wisch, Stempel, Urteil mit Chip) und die Tonart der Klangfläche (`SoundBook.pads(..., ratio=1.335)` = Quarte höher, `ratio=0.749` = Quarte tiefer). Welche Mittel die bisherigen Reels nutzten, steht in Abschnitt 10; jedes neue Reel trägt dort seine Zeile nach.
- Gesteinssignaturen aus `outcrop` (limestone, dolomite, sandstone, shale, granite, basalt, conglomerate, gneiss) nur, wenn die Lithologie stimmt, sonst neutrale Körnung.

## 7. Ton

- Jedes Reel bringt seinen Ton mit: Fläche (`pad`) und Geräusche auf den Bildwechseln. Vokabular: tick (Kreide), crack (Bruch), drip (Wasser), rumble (Zeitraffer), whoosh (Übergang), clack (Bohrhaken), Klanglogo (`SoundBook.sound_logo`).
- Nur Kenney CC0 aus `v2/engine/sfx/kenney` und selbst erzeugte Klänge (`motion.synth`).
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

Video und Cover liegen unter `reels/<slug>.mp4` und `.jpg`, die QC unter `v2/qc/<slug>/`. Der Projektordner auf Markus’ Mac wird nicht automatisch befüllt; die nächste Sitzung mit Zugriff auf den Mac legt neue Reels unter `V2 Outcrop/04 Reels/` ab.

## 10. Bildmittel bisher (für die Abwechslung)

Das neue Reel weicht in mindestens einer Spalte vom vorigen ab und hat einen anderen Ablauf. Eine Zeile je Reel, in Terminfolge.

| Reel | Termin | Format | Ablauf | Übergang | Enthüllung | Payoff | Tonart |
| --- | --- | --- | --- | --- | --- | --- | --- |
| r001 | 12.10.2026 | WHODUNIT #01 | quiz | Isolinien-Welle, Riss-Linie | drei Verdächtige als Chips, Regen mit CO₂, Schwachstellen | Urteil, Chip C leuchtet, Kreide-Wisch | Grundton |
| r002 | 13.10.2026 | HOLD ID #01 | erklaerkette | Schnittlinie, Isolinien-Welle | Querschnitt: Quarz wächst, Zeitraffer der Verwitterung | Antwort groß, Kreide-Wisch, Stempel HOLD ID | Grundton |
| r003 | 16.10.2026 | MYTH OR ROCK #01 | offene_frage | Lichtstreifen, Zoom auf den Griff | Zeitraffer Regen und Abtrocknen, Bruch zeigt das Innere | Antwort groß, Stempel MYTH, Kreide-Wisch | Quarte höher (`ratio=1.335`) |
