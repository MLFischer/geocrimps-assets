# GeoCrimps – Assets und Veröffentlichung

**Aktive Version: V2 „Outcrop“** – Reels über Klettergeologie, zweimal pro Woche (Di 18:07, Fr 17:07, Berliner Zeit), vollautomatisch produziert und über die Instagram-API veröffentlicht. Seit 12.10.2026 (Reel #1), danach Di/Fr.

| Ordner / Datei | Inhalt |
|---|---|
| `reels/` | Fertige Reels (MP4 1080×1920) und Cover (JPG). Öffentlich über GitHub Pages: `https://mlfischer.github.io/geocrimps-assets/reels/…` – Instagram lädt die Videos von dort. |
| `v2/reels.json` | Warteschlange: Termin, Caption, Quellen-Kommentar, Status `review` → `ready` → `published`. `"hold": true` hält ein Reel an. |
| `v2/reel_publish.py` | Veröffentlicht fällige Reels (Container → Status FINISHED → Publish → Quellen-Kommentar); `--probe` testet ohne Veröffentlichung. |
| `v2/engine/` | Reel-Engine: Corporate Design V2 (`outcrop.py`), Bewegung, Ton und Export (`motion.py`), ein Skript pro Reel unter `reels/`, Schriften (OFL) und CC0-Klänge mit Lizenzregister. |
| `.github/workflows/reel-publish.yml` | Zeitplan Di/Fr, mehrere Versuche pro Termin, schreibt die Queue zurück. |
| `.github/workflows/reel-probe.yml` | Probelauf auf Knopfdruck oder bei Änderung von `v2/probe.trigger`. |
| `v1/` | Archiv V1 „Bedrock“ (Bilder #001–#063, alte Queue, `publish.py`, Workflows). Wird nicht mehr ausgeführt. |

Secrets: `IG_USER_ID`, `IG_ACCESS_TOKEN` (Instagram Login, 60 Tage gültig), `GH_ADMIN_TOKEN` (darf nur Secrets dieses Repos schreiben; für die automatische Token-Erneuerung), `BLUESKY_*` (V1).

Konzept und Fahrplan: Claude-Dokument „GeoCrimps V2 Outcrop – Reel-Konzept & Fahrplan Runde 2“ (Markdown-Kopie im Projektordner unter `V2 Outcrop/01 Konzept/`).
