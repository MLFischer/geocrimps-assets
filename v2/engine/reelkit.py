#!/usr/bin/env python3
"""GeoCrimps V2 "Outcrop" -- gemeinsame Bausteine fuer Reel-Skripte (ab r003).

r001 und r002 sind vor diesem Modul entstanden und bleiben unveraendert lauffaehig.
Neue Reels importieren von hier: Uebergaenge (Isolinien-Welle, Riss), Topo-Linie mit
Bohrhaken, Endsignet, Kreidestaub, kleine 2x-Zeichenflaechen, Ton-Buch mit Lizenz-
Protokoll und das gemeinsame Hauptprogramm (Cover, QC-Kontaktbogen, Tonverlauf,
Lautheit -14 LUFS / <= -1 dBTP, H.264-Export, Messbericht).

Ein Reel-Skript definiert:  class Reel(reelkit.ReelBase) mit frame(t) -> (PIL.Image RGBA 1x, grain_seed)
und eine Funktion sound_events(book) -> None. Dann:  reelkit.run(Reel, sound_events, META)
"""
import argparse, json, math, os, random, subprocess
import numpy as np
from PIL import Image, ImageDraw

import outcrop as o
import motion as m
from outcrop import C, P
from motion import W, H, FPS, SR, X0, seg, seilzug, sturz, griff, lerp, put

HERE = os.path.dirname(os.path.abspath(__file__))
SFX = os.path.join(HERE, "sfx", "kenney")
LOCKUP = os.path.join(HERE, "assets", "lockup_stacked_dark.png")


# ------------------------------------------------------------------ kleine 2x-Flaechen und Masken
def region(x0, y0, x1, y1, draw):
    """Bewegte Details in 2x zeichnen, nur im Rechteck: draw(d, X, Y), X/Y rechnen Bildkoordinaten um."""
    x0, y0, x1, y1 = int(x0), int(y0), int(math.ceil(x1)), int(math.ceil(y1))
    w, h = max(1, x1 - x0), max(1, y1 - y0)
    im = Image.new("RGBA", (w * o.S, h * o.S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    draw(d, lambda x: (x - x0) * o.S, lambda y: (y - y0) * o.S)
    return m.Sprite(im.resize((w, h), Image.LANCZOS), x0, y0)

def mask_from(poly):
    """Polygon (Bildkoordinaten) -> weiche 1x-Maske (L), in 2x gezeichnet."""
    mk = Image.new("L", (W * o.S, H * o.S), 0)
    ImageDraw.Draw(mk).polygon([P(x, y) for x, y in poly], fill=255)
    return mk.resize((W, H), Image.BOX)


# ------------------------------------------------------------------ Topo-Linie: Bohrhaken
class Rail:
    """Bohrhaken auf der Topo-Linie (outcrop.route_rail mit total=n) und ihr Einhaenge-Pop."""
    def __init__(self, n):
        self.n = n
        self.y = [1300 - (1300 - 330 - 60) / n * (i + 0.5) for i in range(n)]
        self.bolts = [self._bolt(i) for i in range(n)]
        self.logo = m.sprite(lambda im: o.logo_mark(im, o.RAIL_X, 330, 0.26, C["magnesia"], width=7))

    def _bolt(self, i):
        y, s = self.y[i], 10
        def d(im):
            dr = ImageDraw.Draw(im); col = o.rgb(C["magnesia"])
            dr.line([P(56 - s, y - s), P(56 + s, y + s)], fill=col, width=int(4 * o.S))
            dr.line([P(56 - s, y + s), P(56 + s, y - s)], fill=col, width=int(4 * o.S))
        return m.sprite(d)

    def pop(self, f, t, i, t0):
        u = seg(t, t0, 0.3)
        if 0 < u < 1:
            put(f, self.bolts[i], scale=lerp(1.9, 1.0, griff(u)))

    def logo_pop(self, f, t, t0):
        u = seg(t, t0, 0.3)
        if 0 < u < 1:
            put(f, self.logo, scale=lerp(1.9, 1.0, griff(u)))


# ------------------------------------------------------------------ Uebergaenge
def wave(u, cx=540, cy=1100):
    """Isolinien-Welle (Uebergang zwischen Szenen, 0,45-0,5 s)."""
    rnd = random.Random(4)
    harm = [(k, rnd.uniform(0.02, 0.06), rnd.uniform(0, 6.28)) for k in (2, 3, 5)]
    def d(im):
        dr = ImageDraw.Draw(im)
        for i in range(7):
            r = u * 1750 - i * 95
            if r <= 4:
                continue
            a = int(210 * (1 - u) * (1 - i / 8))
            pts = []
            for j in range(121):
                th = 2 * math.pi * j / 120
                rr = r * (1 + sum(am * math.cos(k * th + ph + i * 0.13) for k, am, ph in harm))
                pts.append(P(cx + rr * math.cos(th), cy + rr * 0.8 * math.sin(th)))
            dr.line(pts, fill=o.rgb(C["magnesia"], a), width=int(3 * o.S))
    return m.sprite(d)

def light_sweep(u, color=C["magnesia"], alpha=95, width=260):
    """Lichtstreifen-Uebergang: ein weicher, schraeger Streifen wischt von links nach rechts (Zeitraffer, Abwechslung zur Welle)."""
    if not 0 < u < 1:
        return None
    x = lerp(-width * 2, W + width, seilzug(u))
    def d(im):
        lay = Image.new("L", (W * o.S, H * o.S), 0); dl = ImageDraw.Draw(lay)
        for k in range(12):
            a = int(alpha * math.sin(math.pi * (k + 0.5) / 12) * math.sin(math.pi * u))
            xx = x + k * width / 12
            dl.polygon([P(xx, 0), P(xx + width / 12 + 1, 0), P(xx + width / 12 + 1 - 420, H), P(xx - 420, H)], fill=a)
        layer = Image.new("RGBA", lay.size, o.rgb(color)); layer.putalpha(lay); im.alpha_composite(layer)
    return m.sprite(d)

def rail_sprite(clipped, total, logo_on=False):
    """Topo-Linie als eigenes Sprite (fuer Szenen, deren Hintergrund gezoomt wird)."""
    return m.sprite(lambda im: o.route_rail(im, clipped, total, logo_on=logo_on))

def crackline(u, alpha=255, x=560, y0=620, seed=12):
    """Riss-Uebergang: zackige Linie von oben nach unten (unterhalb des Textblocks beginnen)."""
    rnd = random.Random(seed); pts = []
    for k in range(17):
        pts.append((x + rnd.uniform(-38, 38), y0 + k * 84))
    n = max(2, int(len(pts) * u))
    return m.sprite(lambda im: ImageDraw.Draw(im).line([P(px, py) for px, py in pts[:n]],
                                                        fill=o.rgb(C["magnesia"], alpha), width=int(6 * o.S), joint="curve"))

def dust(f, t, t0, box, seed=77, n=40, color=C["magnesia"]):
    """Kreidestaub beim Treffer: Partikel fliegen aus box (x0, y0, x1, y1) und fallen."""
    v = seg(t, t0, 0.6)
    if not 0 < v < 1:
        return
    dr = ImageDraw.Draw(f); rnd = random.Random(seed); x0, y0, x1, y1 = box
    for _ in range(n):
        px = rnd.uniform(x0, x1); py = rnd.uniform(y0, y1); ang = rnd.uniform(0, 6.28); sp = rnd.uniform(30, 120)
        qx = px + math.cos(ang) * sp * seilzug(v); qy = py + math.sin(ang) * sp * seilzug(v) + 40 * v * v
        r = rnd.uniform(1.5, 3.5)
        dr.ellipse([qx - r, qy - r, qx + r, qy + r], fill=o.rgb(color, int(200 * (1 - v))))


# ------------------------------------------------------------------ Endsignet (0,8 s)
class EndSting:
    def __init__(self):
        lock = Image.open(LOCKUP).convert("RGBA")
        lw = 760; lh = int(lock.height * lw / lock.width)
        self.lockup = m.Sprite(lock.resize((lw, lh), Image.LANCZOS), (W - lw) // 2, 640)
        self.mark_c = (self.lockup.x + 505 * lw / 1000, self.lockup.y + 280 * lw / 1000)
        self.bg = m.background(lambda im: None)

    def contract(self, u):
        cx, cy = self.mark_c
        def d(im):
            o.contour_field(im, cx, cy, n=9, r0=lerp(420, 60, u), step=lerp(70, 12, u), color=C["slate"],
                            alpha=int(lerp(230, 110, u)), width=2.6, seed=4, squash=0.86)
        return m.sprite(d)

    def frame(self, t, t_end):
        f = self.bg.copy()
        u = seilzug(seg(t, t_end, 0.45))
        put(f, self.contract(u), op=1 - seg(t, t_end + 0.35, 0.15))
        put(f, self.lockup, op=seg(t, t_end + 0.3, 0.2))
        return f


class ReelBase:
    """Gemeinsame Grundlage: Korn/Vignette und Frame-Iterator."""
    DUR = 12.0

    def __init__(self):
        self.fin = m.Finish()

    def frame(self, t):
        raise NotImplementedError

    def frames(self, draft=False):
        n = int(round(self.DUR * FPS))
        for i in range(n):
            t = i / FPS
            if draft and i % 3:
                continue
            f, s = self.frame(t)
            yield self.fin(f, s)


# ------------------------------------------------------------------ Ton
class SoundBook:
    """Sammelt Klangereignisse und protokolliert die Herkunft jedes Klangs (Lizenzregister)."""
    def __init__(self):
        self.ev, self.used = [], {}

    def kenney(self, pack, name, t, gain, label, ratio=None):
        path = os.path.join(SFX, f"kenney_{pack}", "Audio", name)
        smp = m.load_audio(path)
        if ratio:
            smp = m.pitch(smp, ratio)
        self.ev.append((t, smp, gain)); self.used.setdefault(label, set()).add("CC0 Kenney: " + name)

    def synth(self, kind, t, gain, label, **kw):
        self.ev.append((t, m.synth(kind, **kw), gain)); self.used.setdefault(label, set()).add(f"selbst erzeugt ({kind})")

    def sound_logo(self, t_end):
        """Klanglogo zum Endsignet: drei steigende Toene (pluck) + Kreide-Klatsch."""
        for k, r in enumerate((1.0, 1.26, 1.5)):
            self.kenney("interface-sounds", "pluck_001.ogg", t_end + 0.12 * k, -3.0, "klanglogo", ratio=r)
        self.kenney("impact-sounds", "impactGeneric_light_000.ogg", t_end + 0.45, -5.0, "klatsch")

    def pads(self, spans, depth_db=-6.0, ratio=1.0):
        """Flaeche je Abschnitt (t0, t1, gain_db), unter den Ereignissen geduckt. Luecken = Stille.
        ratio != 1 verschiebt die Tonart (z. B. 1.335 = Quarte hoeher), damit nicht jedes Reel gleich klingt."""
        for t0, t1, g in spans:
            pad = m.synth("pad", dur=(t1 - t0) * ratio + 0.05, seed=int(t0 * 10) + 2)
            if abs(ratio - 1.0) > 1e-3:
                pad = m.pitch(pad, ratio)[: int((t1 - t0) * SR)]
            rel = [(t - t0, smp, gg) for t, smp, gg in self.ev if t0 <= t < t1]
            self.ev.append((t0, m.duck(pad, rel, depth_db=depth_db), g))
        self.used.setdefault("flaeche", set()).add("selbst erzeugt (pad)")

    def licenses(self):
        return {k: sorted(v) for k, v in self.used.items()}


# ------------------------------------------------------------------ QC: Tonverlauf als Bild
def tonverlauf_png(mp4, out_png, marks, title):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", mp4, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.float32); dur = len(a) / SR
    Wd, Hd = 2000, 520; im = Image.new("RGB", (Wd, Hd), (14, 17, 19)); d = ImageDraw.Draw(im)
    win = int(SR * 0.02); n = len(a) // win
    blk = a[:n * win].reshape(n, win)
    rms = np.sqrt(np.mean(blk ** 2, axis=1) + 1e-12); pk = np.max(np.abs(blk), axis=1)
    y = lambda db: int(40 + (0 - max(-60, db)) / 60 * (Hd - 90))
    for db in (0, -12, -24, -36, -48, -60):
        d.line([(60, y(db)), (Wd - 10, y(db))], fill=(44, 52, 59)); d.text((8, y(db) - 6), f"{db} dB", fill=(140, 150, 159))
    for i in range(n):
        x = 60 + int(i / n * (Wd - 70))
        d.line([(x, y(20 * np.log10(pk[i] + 1e-9))), (x, y(-60))], fill=(60, 70, 80))
        d.line([(x, y(20 * np.log10(rms[i] + 1e-9))), (x, y(-60))], fill=(140, 150, 159))
    for k, (t, label) in enumerate(marks):
        x = 60 + int(t / dur * (Wd - 70))
        d.line([(x, 30), (x, Hd - 45)], fill=(255, 138, 61) if label.upper() == "PAYOFF" else (90, 169, 255))
        d.text((x + 3, Hd - 40 if k % 2 else Hd - 26), label, fill=(241, 239, 233))
    d.text((60, 8), title + " - Tonverlauf (grau: RMS 20 ms, dunkel: Spitze), gemessen am fertigen MP4", fill=(241, 239, 233))
    im.save(out_png)


# ------------------------------------------------------------------ Ablauf und Lesezeit (seit 13.10.2026)
ABLAEUFE = ("quiz", "offene_frage", "erklaerkette")
HOOK_MIN_S, FRAGE_MIN_S = 3.2, 1.2      # Hook-Frage bzw. jede weitere Frage im Bild, Beginn bis Beginn des Ausblendens


def plan_ablauf(slug):
    """(Ablauf des Slots zum Datum im Slug, Ablauf des Slots davor) aus v2/themenplan.json; (None, None), wenn nicht gefunden."""
    try:
        with open(os.path.join(HERE, "..", "themenplan.json"), encoding="utf-8") as fh:
            slots = sorted(json.load(fh).get("slots", []), key=lambda s: s.get("termin", ""))
    except (OSError, ValueError):
        return None, None
    for k, s in enumerate(slots):
        if s.get("termin", "").startswith(slug[:10]):
            return s.get("ablauf"), (slots[k - 1].get("ablauf") if k else None)
    return None, None


# ------------------------------------------------------------------ Hauptprogramm
def run(ReelCls, sound_events, META):
    """META: slug, dur_range, payoff_t, on_screen (Liste), labels (Liste), qc_times (16 Zeitpunkte), marks [(t, Name)], title,
    ablauf (quiz | offene_frage | erklaerkette, wie der Slot im Themenplan), hook_bis (Sekunde, ab der die Hook-Frage
    ausgeblendet wird; sie steht ab Frame 0), weitere_fragen ([[Beginn, Beginn des Ausblendens], ...] je weiterer Frage im Bild)."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "..", "..", "reels"))
    ap.add_argument("--qc", default=None, help="Ordner fuer QC-Dateien")
    ap.add_argument("--stills", default=None, help="Kommagetrennte Zeitpunkte: nur Einzelbilder in --qc schreiben")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    slug = META["slug"]
    r = ReelCls()
    if a.stills:
        os.makedirs(a.qc, exist_ok=True)
        for ts in a.stills.split(","):
            f, s = r.frame(float(ts))
            Image.fromarray(r.fin(f, s)).save(os.path.join(a.qc, f"still_{float(ts):05.2f}.png"))
        return
    qc = a.qc or a.out
    os.makedirs(qc, exist_ok=True)
    f0, s0 = r.frame(0.0)                                         # Cover = Frame 0
    Image.fromarray(r.fin(f0, s0)).save(os.path.join(a.out, slug + ".jpg"), quality=92)
    thumbs = []                                                   # QC-Kontaktbogen
    for t in META["qc_times"]:
        f, s = r.frame(t)
        im = Image.fromarray(r.fin(f, s)).resize((270, 480), Image.LANCZOS)
        ImageDraw.Draw(im).text((8, 8), f"{t:.2f}s", fill=(255, 120, 60))
        thumbs.append(im)
    rows = (len(thumbs) + 7) // 8
    sheet = Image.new("RGB", (270 * 8, 480 * rows), (0, 0, 0))
    for k, im in enumerate(thumbs):
        sheet.paste(im, ((k % 8) * 270, (k // 8) * 480))
    sheet.save(os.path.join(qc, slug + "_kontaktbogen.png"))
    book = SoundBook()                                            # Ton
    sound_events(book)
    tmp = os.path.join(qc, slug + "_mix.wav"); norm = os.path.join(qc, slug + "_norm.wav")
    m.write_wav(tmp, m.mix(book.ev, r.DUR))
    ln = m.master(tmp, norm)
    mp4 = os.path.join(a.out, slug + ".mp4")                      # Video
    n = int(round(r.DUR * FPS))
    m.encode(r.frames(), n, mp4, audio_wav=norm, crf=21)
    tonverlauf_png(mp4, os.path.join(qc, slug + "_tonverlauf.png"), META.get("marks", []), META.get("title", slug))
    words = sum(len(s.replace("·", " ").split()) for s in META["on_screen"])
    rep = {"slug": slug, "dauer_s": r.DUR, "fps": FPS, "frames": n, "mp4_mb": round(os.path.getsize(mp4) / 1e6, 2),
           "woerter_im_bild": words, "labels": len(META.get("labels", [])),
           "woerter_gesamt_mit_labels": words + sum(len(s.split()) for s in META.get("labels", [])),
           "payoff_anteil": round(META["payoff_t"] / r.DUR, 3), "loudnorm": ln, "messung": m.measure(mp4),
           "toene": book.licenses()}
    ab, ab_vor = plan_ablauf(slug)
    fragen = META.get("weitere_fragen", [])
    rep.update({"ablauf": META.get("ablauf"), "ablauf_im_themenplan": ab, "ablauf_slot_davor": ab_vor,
                "hook_steht_s": META.get("hook_bis"), "weitere_fragen_stehen_s": [round(b - a, 2) for a, b in fragen]})
    checks = {"dauer_im_formatrahmen": META.get("dur_range", [0, 99])[0] <= r.DUR <= META.get("dur_range", [0, 99])[1],
              "hook_frage_mind_3_2_s": (META.get("hook_bis") or 0) >= HOOK_MIN_S - 1e-6,
              "weitere_fragen_mind_1_2_s": all(b - a >= FRAGE_MIN_S - 1e-6 for a, b in fragen),
              "ablauf_wie_im_themenplan": META.get("ablauf") in ABLAEUFE and META.get("ablauf") == ab,
              "ablauf_anders_als_im_slot_davor": ab is not None and ab != ab_vor,
              "payoff_65_80_prozent": 0.65 <= rep["payoff_anteil"] <= 0.80,
              "hoechstens_40_woerter": rep["woerter_gesamt_mit_labels"] <= 40,
              "lautheit_-14_+-0.5": abs(rep["messung"].get("I_LUFS", 0) + 14) <= 0.5,
              "true_peak_max_-1": rep["messung"].get("TP_dBFS", 0) <= -1.0,
              "mp4_unter_100_mb": rep["mp4_mb"] < 100}
    rep["pruefungen"] = checks
    rep["alle_pruefungen_ok"] = all(checks.values())
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    json.dump(rep, open(os.path.join(qc, slug + "_bericht.json"), "w"), ensure_ascii=False, indent=1)
