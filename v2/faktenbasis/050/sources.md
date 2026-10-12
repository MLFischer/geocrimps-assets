# GeoCrimp #050 — Quellen & Faktencheck

Neues Thema (Warteschlange W7 war mit #043–#049 aufgebraucht; gezogen aus dem Backlog „Ryolith-Tuff vs. Ignimbrit"). Alle Claims am 17.08.2026 geprüft.

Hauptquellen:
[USGS — **Bishop Tuff in Long Valley Caldera, California**](https://www.usgs.gov/volcanoes/long-valley-caldera/science/bishop-tuff-long-valley-caldera-california) ·
[Wilson & Hildreth (1997), **The Bishop Tuff: New Insights from Eruptive Stratigraphy**, J. Geology 105:407–440](https://www.journals.uchicago.edu/doi/10.1086/515937) ·
[Wikipedia — Bishop Tuff (als Aggregator der Datierungen)](https://en.wikipedia.org/wiki/Bishop_Tuff)

| Claim (im Post) | Belegsatz aus der Quelle | Status |
|---|---|---|
| Die Tablelands bestehen aus dem Bishop Tuff, einem geschweißten Tuff | „The Bishop Tuff is a welded tuff which formed … as a rhyolitic pyroclastic flow during the approximately six-day eruption that formed the Long Valley Caldera." | ✅ wörtlich bestätigt |
| Eruptionsdauer „etwa sechs Tage" | s. o. („approximately six-day eruption"); USGS-Übersicht spricht von „5- to 6-day-long" | ✅ bestätigt, Post sagt „about six days" |
| **Alter „roughly 765,000 years ago"** | „formed 764,800 ± 600 years ago" (nach Andersen et al. 2017 PNAS / Crowley et al. 2007 Geology) | ✅ bestätigt — **s. Kalibrierung unten** |
| ~200 km³ flossen außerhalb der Caldera aus | „as much as about 200 km3 (48 mi3) erupted as pyroclastic flows/ignimbrite that flowed outside the caldera" (USGS) | ✅ wörtlich bestätigt |
| ~350 km³ stauten sich in der Caldera und verschweißten dort | „Approximately 350 km3 (85 mi3) ponded and welded together within the caldera." (USGS) | ✅ wörtlich bestätigt |
| Fläche „more than 2,200 square kilometres" | „these pyroclastic flows swept over an area of more than 2,200 km2" (USGS) | ✅ wörtlich bestätigt |
| Mächtigkeit bis ~200 m | „buried the pre-existing ground to depths of nearly 200 m (660 f) just south of the caldera" (USGS) | ✅ wörtlich bestätigt |
| **Fun Fact: der Schweißgrad ist nicht einheitlich** | „These pyroclastic flow deposits show various degrees of welding." (USGS) | ✅ wörtlich bestätigt — trägt den Fun Fact |
| Der Owens River hat die Owens River Gorge in die Platte geschnitten | „Erosion of the plateau by the Owens River has carved the Owens River Gorge." | ✅ wörtlich bestätigt |
| Gesteinsart: hoch-silikatischer rhyolithischer Schweißtuff aus Asche und Bimsklasten | „The Bishop Tuff is a high-silicate rhyolitic welded tuff, made up of ash and pumice clasts." | ✅ wörtlich bestätigt |
| **Ortsnennung Bishop / Long Valley** ist ein Claim | „The Bishop Tuff caps a volcanic plateau in the northern Owens Valley in eastern California … sitting northwest of Bishop" | ✅ Gesteinsart, Alter und Genese der genannten Lokalität stimmen mit dem Posttext überein |

**Formulierungs-Kalibrierung:**

- **Alter: „roughly 765,000 years ago".** Die publizierten Werte streuen: 764,8 ± 0,6 ka (Ar/Ar-Sanidin, Andersen et al. 2017), 758,9 ± 1,8 ka in Teilen der Fernerkundungs-/Strukturliteratur, und die USGS-Übersichtsseite rundet auf „about 760,000 years ago". Der Post nennt **eine** Zahl mit „roughly" statt einer Scheinpräzision; jede der publizierten Fassungen liegt innerhalb dessen, was „roughly 765,000" abdeckt oder knapp daneben — deshalb der Weichmacher.
- **„About 200 … another 350 or so" statt einer Gesamtzahl.** Kursierende Zusammenfassungen nennen „~650 km³ Magma". Diese Summe steht **nicht** auf der zitierten USGS-Seite; dort stehen die drei Teilmengen (>100 km³ Ashfall, ~200 km³ außerhalb, ~350 km³ innerhalb). Der Post nennt deshalb die belegten Teilmengen und addiert sie nicht.
- **„welded" ist der tragende Begriff, nicht „compressed".** Verschweißung durch Eigenlast bei noch hoher Temperatur ist der Grund, warum das Zeug kletterbar ist — und die Formulierung deckt sich mit dem Quellenwort.

**Bewusst NICHT behauptet:**

- **Dass die Taschen und Huecos der Tablelands ausgewitterte Gasblasen sind.** Das war die naheliegende Arbeitshypothese und hat den Faktencheck **nicht** überstanden. In der Literatur werden für Hohlformen in Tuff Tafoni-/Salzverwitterung und differentielle Verwitterung angeführt; für den Bishop Tuff speziell fand sich dazu keine zitierfähige, begutachtete Arbeit — nur Bildunterschriften und Sekundärtexte. Regel 3e („Mechanismen nicht raten") greift: Der Post erzählt deshalb die **Verschweißung** (voll belegt) und erwähnt Taschen gar nicht als Mechanismus.
- **Reibungs- oder Klettereigenschaften des Tuffs.** Keine Messung, keine Aussage — dieselbe Linie wie bei #032 (Flechten) und #046 (Serpentinit).
- Eine Aussage darüber, ob Long Valley „überfällig" oder gefährlich ist. Vulkanische Risikoaussagen gehören nicht in dieses Format.

## Bildherkunft — **offen, Foto-Hero vorbereitet und nicht aktiv**

Einer der zwei für diese Woche vorgesehenen Foto-Heroes: Die Textur eines Schweißtuffs — flachgedrückte Bimsfetzen in feiner Aschematrix — ist genau das, was eine Flachgrafik prinzipiell nicht zeigen kann. Der Post ist über `photo_zone("050", fallback=…)` verdrahtet und **rendert derzeit die Vektor-Illustration**.

Grund: In diesem Lauf war die Wikimedia-Commons-API nicht erreichbar (`web_fetch` liefert für `commons.wikimedia.org` leere Antworten, der verbundene Chrome-Browser war über den ganzen Lauf nicht ansprechbar). Ohne Lizenzlesung pro Datei aus `extmetadata` darf nach der Projektregel **kein** Bild in `PHOTOS` — und ohne Browser ließ sich auch keine Binärdatei nach `Assets/Photos/` legen.

Kandidatenkategorie für den nächsten Versuch: Commons `Category:Bishop Tuff`. Gesichtet wurden u. a.
`File:Bishop Tuff over Sherwin Till (Pleistocene; Sherwin Summit, Owens Valley, California, USA) 3.jpg` und
`File:Clastic dikes in the Bishop Tuff (Pleistocene, 760 ka; Sherwin Summit, Owens Valley, California, USA) 2.jpg`.
Das Titelmuster deutet auf James St. John (bisher durchgängig CC BY 2.0) — **Vermutung, kein Befund; Lizenz vor Aktivierung pro Datei lesen.**
**Motivvorbehalt:** Beide gesichteten Kandidaten sind Aufschluss-Übersichten (Straßenanschnitt, Kontakt zum Sherwin Till). Für den Hero wäre ein **Nahbereichsfoto der Schweißtextur** deutlich stärker; eine Übersicht liest im Hero als „helle Böschung" und wäre gegenüber der Illustration ein Rückschritt (Regel aus dem Skill). Lieber weiter suchen als das Erstbeste nehmen.
