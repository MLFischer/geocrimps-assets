# GeoCrimp #057 — Quellen & Faktencheck

Thema aus der W9-Warteschlange (entstand als offener Punkt in `Posts/056/sources.md`, Anschluss an Superposition). Alle Claims am 24.08.2026 geprüft.

Hauptquelle: [Way-up structures, in **Historical Geology** (Callan Bentley u. a., OpenGeology)](https://opengeology.org/historicalgeology/tools-of-historical-geology/way-up-structures/)

| Claim (im Post) | Belegsatz aus der Quelle | Status |
|---|---|---|
| Es gibt Strukturen, die oben anders aussehen als unten — „way-up" / „geopetal" | „We call these patterns that look different right-side-up compared to up-side-down by the general term **way-up structures**. Some geologists also call them **geopetal structures**." | ✅ wörtlich bestätigt |
| Sie dienen der Bestimmung der Younging Direction | „Way-up indicators are critical for figuring out the correct sequence of geologic units. They help us determine ‚younging direction,' the direction in which strata get younger." | ✅ wörtlich bestätigt |
| Definierendes Merkmal: Unterschied zwischen Ober- und Unterseite | „The key thing is that a way-up structure must be display some difference between its top and its bottom. **They always look different up-side-down compared to right-side-up.**" | ✅ wörtlich bestätigt |
| **Gradierte Schichtung: grob unten, fein oben — „in most cases"** | „In **normal** graded bedding, we see coarse at the bottom and fine at the top, with a gradational transition in between. Therefore, **in most cases**, we can find graded bedding in an outcrop … and find the coarsest bit and head in the direction of the finest bit, and be confident the strata get younger in that direction." | ✅ wörtlich bestätigt — inkl. der Einschränkung |
| **Es gibt inverse Gradierung** | „However, *caveat emptor*: nature is vast and varied, and she has a few more tricks up her sleeve." + Abschnitt „Reverse grading" mit Beispielen aus der Purisima Formation und aus **Lahar-Ablagerungen** (Absaroka Volcanic Field) | ✅ bestätigt |
| Schrägschichtung: unten tangential, oben gekappt | Bildunterschrift: „Crossbeds are tangential at bottom and truncated at top." | ✅ wörtlich bestätigt |
| **Ein Indikator reicht nicht — Vorsicht und Mehrfachbeleg** | „Be cautious about leaping to big, important conclusions from a single way-up structure. … Examples seen in the field can frequently be ambiguous. The careful historical geologist will search for as many examples as possible; to see if they agree with one another. Careful geologists seek a preponderance of evidence before settling on an interpretation." | ✅ wörtlich bestätigt — **tragender Satz von Slide 3** |
| **Fun Fact: höhergradige Metamorphose zerstört die Strukturen** | „Metamorphic rocks develop no way-up structures as a consequence of metamorphism, but sometimes primary structures in a sedimentary or volcanic protolith can potentially survive as discernible patterns in **lower-grade** metamorphic rocks. **Higher-grade metamorphic rocks are so thoroughly recrystallized that any original geopetal structures would be destroyed.**" | ✅ wörtlich bestätigt |
| Gradierte Schichtung typisch für Turbidite | „Graded bedding is most commonly found in submarine turbidity current deposits (e.g., on an abyssal fan), but it can occur in other settings too, such as lakes, floodplains, and tidal flats." | ✅ wörtlich bestätigt (im Post nur als „settles out of a slowing current" angedeutet) |

**Formulierungs-Kalibrierung:**

- **„in most cases", nicht „always".** Regel 3f. Die Quelle sagt ausdrücklich „in most cases" und führt danach die Ausnahmen auf. Der Post übernimmt genau diese Abstufung — und macht die Ausnahme zum eigenen dritten Schritt, statt sie in eine Fußnote zu schieben.
- **Slide 3 ist die Pointe, nicht der Kleingedruckte.** Ein Post, der nur „grob unten, fein oben" sagt, wäre ein Merksatz. Der Punkt der Quelle ist der methodische: mehrere Indikatoren, und sie müssen übereinstimmen. Caption und Slide 3 sagen beide dasselbe.
- **Keine Zahl.** Es gibt in dieser Quelle keine quantitative Aussage, die der Post tragen könnte — also steht keine im Post.
- **Quellen-Einordnung:** OpenGeology „Historical Geology" ist ein offenes Lehrbuch (OER) von Callan Bentley u. a., kein begutachteter Artikel. Für kanonischen Lehrbuchstoff (Way-up-Kriterien sind seit Jahrzehnten Standard) ist das tragfähig; für eine Zahl oder eine strittige Genese wäre es zu dünn. Der Post enthält keine Zahl.

**Bewusst NICHT behauptet:**

- **Keine Lokalität.** Nach v1.2 ist eine Ortsnennung ein Claim über Gesteinsart, Alter und Genese. Für ein Methodenthema braucht es keine, also steht keine drin. Location-Tag bleibt leer.
- **Keine Reibungs- oder Griffigkeitsaussage.** Konsequent wie #032, #046, #051, #052.
- **Nicht behauptet, man könne jede überkippte Wand erkennen.** Die Quelle sagt das Gegenteil („frequently be ambiguous").
- **Sohlmarken und Belastungsmarken** stehen in der Quelle, kommen im Post aber nur als Aufzählung in der Caption vor — ohne sie zu erklären, weil v1.2 pro Slide einen Gedanken verlangt.

## Bildherkunft — **offen, Foto-Hero vorbereitet und nicht aktiv**

Erster für diese Woche vorgesehener Foto-Hero. Ein Aufschlussfoto mit gekappten Schrägschichtungs-Laminae oder einer sichtbar gradierten Bank zeigt genau das, was eine Flachgrafik nur behaupten kann: Korngrößenverlauf und die Kappungsfläche als **Textur**. Der Post ist über `photo_zone("057", fallback=…)` verdrahtet und **rendert derzeit die Vektor-Illustration**.

Grund: Die Wikimedia-Commons-API war in diesem Lauf über `web_fetch` nicht erreichbar (Provenance-Sperre), und `list_connected_browsers` meldete über den gesamten Lauf kein Gerät. Damit war weder die **Lizenzlesung pro Datei aus `extmetadata`** möglich noch das Ablegen einer Binärdatei in `Assets/Photos/`. Ohne geprüfte Lizenz kein `PHOTOS`-Eintrag — Projektregel eingehalten.

Für den nächsten Versuch: Commons `Category:Graded bedding` oder `Category:Cross-bedding`, gesucht wird ein **Aufschluss im Nahbereich mit Maßstab**, bei dem die Kappung oben tatsächlich zu sehen ist. Lizenz pro Datei lesen; CC BY-SA bleibt ausgeschlossen. **Motivprüfung gegen den Posttext:** Das Bild muss aufrecht stehende Schichten zeigen, sonst widerspricht es dem eigenen Slide.

## Nachtrag 28.10.2026 (Reel r008 WHODUNIT #02)

| Aussage (im Reel / in der Caption) | Quelle | Status |
|---|---|---|
| Kompression (konvergente Plattengrenzen) kann Bänke **auf den Kopf falten**; dann liest man die Erdgeschichte rückwärts → im Reel: „UP WAS DOWN.“, „HERE, UP MEANS OLDER.“ (in einer überkippten Folge zeigt die Younging Direction nach unten) | [Bentley, Layou, Kohrs, Jaye, Affolter & Ricketts: Historical Geology, Kap. 61.1 „(Tools of the Trade) Way-up structures – Introduction“, Geosciences LibreTexts (veröffentlicht 27.07.2023, CC BY-NC 4.0)](https://geo.libretexts.org/Bookshelves/Geology/Historical_Geology_(Bentley_et_al.)/61%3A_(Tools_of_the_Trade)_Way-up_structures/61.01%3A_Introduction) — „compressive stresses … fold beds into up-side-down positions“, „would be reading Earth history backward!“ | ✅ web-verifiziert 28.10.2026 |
| Definition, Younging Direction und „A note of caution“ (viele Beispiele suchen, Übereinstimmung prüfen) stehen in derselben LibreTexts-Fassung wie auf opengeology.org → im Reel „EVERY BED AGREES.“ (mehrere Bänke als mehrere Indikatoren) | wie oben | ✅ web-verifiziert 28.10.2026 (opengeology.org war in diesem Lauf nicht abrufbar; die Zeilen vom 24.08.2026 gelten weiter) |

**Reel-Kalibrierung:** Die Wand ist schematisch (kein Ort), sie zeigt überall dasselbe Kriterium (gradierte Bänke); das Reel sagt nicht, dass ein einzelnes Kriterium beweist, und die Caption nennt die inverse Gradierung. Das Zwischenbild „Bank setzt sich ab, unten zuerst“ zeigt nur die Reihenfolge der Ablagerung (unten älter), keine Sinkgeschwindigkeit.
