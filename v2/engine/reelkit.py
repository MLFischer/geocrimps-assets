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
import klang
import musik
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


# ------------------------------------------------------------------ Abspann mit Aufruf (seit 16.10.2026)
class Outro(EndSting):
    """Abspann fuer alle neuen Reels (Markus, 16.10.2026: "am ende sollte noch ein aufruf zum like and subscribe oder so
    dabei sein"): Isolinien ziehen sich zusammen, das Logo erscheint, darunter "LIKE & FOLLOW" und die Markenzeile
    "FOR MORE CLIMBING × GEOLOGY", ein Herz schlaegt einmal. Auf Instagram heisst Abonnieren "Follow".
    Dauer DUR s; das Reel endet mit dem Abspann und laeuft als Loop weiter. Im Reel: self.outro = reelkit.Outro(),
    in frame(): ab T_END self.outro.frame(t, T_END); META "abspann_ab" = T_END; Ton: SoundBook.klanglogo + musik."""
    DUR = 3.0
    CTA = "LIKE & FOLLOW"
    CLAIM = "FOR MORE CLIMBING × GEOLOGY"
    Y_LOCK, Y_CTA, Y_CLAIM, Y_HEART = 500, 950, 1120, 1250

    def __init__(self):
        lock = Image.open(LOCKUP).convert("RGBA")
        lw = 520; lh = int(lock.height * lw / lock.width)          # Logo kleiner als im Endsignet: der Aufruf ist die Hauptsache
        self.lockup = m.Sprite(lock.resize((lw, lh), Image.LANCZOS), (W - lw) // 2, self.Y_LOCK)
        self.mark_c = (self.lockup.x + 505 * lw / 1000, self.lockup.y + 280 * lw / 1000)
        self.bg = m.background(lambda im: None)
        self.cta = m.text_sprite(self.CTA, W // 2, self.Y_CTA, "display", 136, C["magnesia"], anchor="ma")
        self.claim = m.text_sprite(self.CLAIM, W // 2, self.Y_CLAIM, "stencil", 40, C["slate"], anchor="ma", tracking=0.12)
        self.claim.text = None                     # Markenzeile wie die Kopfzeile: nicht Teil der 40 Woerter
        hx, hy, r = W // 2, self.Y_HEART + 40, 34

        def heart(im):
            d = ImageDraw.Draw(im)
            pts = [P(hx + r * 1.15 * math.sin(a) ** 3, hy - r * (0.95 * math.cos(a) - 0.38 * math.cos(2 * a)
                                                               - 0.15 * math.cos(3 * a) - 0.05 * math.cos(4 * a)))
                   for a in np.linspace(0, 2 * math.pi, 120)]
            d.polygon(pts, fill=o.rgb(C["heat"]))
        self.heart = m.sprite(heart)

    def frame(self, t, t0):
        f = self.bg.copy()
        u = seilzug(seg(t, t0, 0.5))
        put(f, self.contract(u), op=1 - seg(t, t0 + 0.4, 0.2))
        put(f, self.lockup, op=seg(t, t0 + 0.3, 0.3))
        v = seilzug(seg(t, t0 + 0.6, 0.5))
        put(f, self.cta, dy=lerp(36, 0, v), op=v)
        put(f, self.claim, op=seg(t, t0 + 0.95, 0.4))
        w = seg(t, t0 + 1.3, 0.35)
        if w > 0:                                   # Herz: springt auf und schlaegt danach ruhig
            beat = 1 + 0.05 * max(0.0, math.sin(2 * math.pi * (t - t0 - 1.65) / 0.9)) if w >= 1 else 1.0
            put(f, self.heart, op=min(1.0, w * 3), scale=lerp(1.7, 1.0, griff(w)) if w < 1 else beat)
        return f


class ReelBase:
    """Gemeinsame Grundlage: Korn/Vignette und Frame-Iterator."""
    DUR = 12.0

    def __init__(self):
        self.fin = m.Finish()

    def frame(self, t):
        raise NotImplementedError

    def frames(self, draft=False):
        """Alle Frames; protokolliert dabei je Frame die eingesetzten Text-Sprites (self.textlog, fuer die Lesezeit)."""
        n = int(round(self.DUR * FPS))
        self.textlog = []
        for i in range(n):
            t = i / FPS
            if draft and i % 3:
                continue
            m.TEXTLOG = []
            f, s = self.frame(t)
            self.textlog.append((t, m.TEXTLOG))
            m.TEXTLOG = None
            yield self.fin(f, s)


# ------------------------------------------------------------------ Ton
class SoundBook:
    """Sammelt Klangereignisse und protokolliert die Herkunft jedes Klangs (Lizenzregister)."""
    def __init__(self):
        self.ev, self.used = [], {}
        self.no_duck = set()                     # Ereignisse, unter denen die Flaeche nicht duckt (Hi-Hats des Pulses)

    def kenney(self, pack, name, t, gain, label, ratio=None):
        path = os.path.join(SFX, f"kenney_{pack}", "Audio", name)
        smp = m.load_audio(path)
        if ratio:
            smp = m.pitch(smp, ratio)
        self.ev.append((t, smp, gain)); self.used.setdefault(label, set()).add("CC0 Kenney: " + name)

    def synth(self, kind, t, gain, label, **kw):
        self.ev.append((t, m.synth(kind, **kw), gain)); self.used.setdefault(label, set()).add(f"selbst erzeugt ({kind})")

    def klang(self, kind, t, gain, label, ratio=None, **kw):
        """Kinoklaenge aus dem eigenen Klangset (engine/klang.py): sub_hit, braam, crunch, chalk_slap, reverse, kick, hat,
        tick, thud. Selbst erzeugt, also lizenzfrei per Konstruktion (Kaufbibliotheken verbieten die Weitergabe im Repo)."""
        smp = klang.make(kind, **kw)
        if ratio:
            smp = m.pitch(smp, ratio)
        self.ev.append((max(0.0, t), smp, gain)); self.used.setdefault(label, set()).add(f"selbst erzeugt (klang.{kind})")
        return smp

    def ton(self, kind, t, gain, label, **kw):
        """Musikbaustein aus engine/musik.py (flaeche, zupf, bass, schwelle, akzent), selbst erzeugt."""
        smp = musik.KINDS[kind](**kw)
        self.ev.append((max(0.0, t), smp, gain)); self.used.setdefault(label, set()).add(f"selbst erzeugt (musik.{kind})")
        return smp

    def musik(self, abschnitte, bpm=84.0, gain=-12.0):
        """Musikalische Untermalung (seit 16.10.2026, Markus: "eher musikalische untermalung"). abschnitte: Liste
        (t0, t1, akkord, bassnote, figur) in der Tonart des Reels (MIDI-Noten, Beispiele in musik.py); figur:
          "flaeche"   nur Akkordflaeche und Bass (Haltezeiten, Aufloesung)
          "ruhig"     dazu Zupftoene auf Vierteln (Fragen, Fazit, Abspann)
          "bewegt"    dazu Achtel-Arpeggio auf und ab (Zuege)
          "steigend"  Achtel aufwaerts und lauter werdend (Spannung vor dem Bruch)
          "pause"     Stille (z. B. 0,15 s vor dem Payoff)
        Die Akkorde wechseln mit den Szenen, nicht im festen Takt: Untermalung statt Song. Ersetzt pulse() und pads()."""
        beat = 60.0 / bpm
        for k, (t0, t1, akkord, bassnote, figur) in enumerate(abschnitte):
            d = t1 - t0
            if figur == "pause" or d <= 0.05:
                continue
            self.ton("flaeche", t0, gain, "musik", akkord=akkord, dauer=d, seed=k)
            self.ton("bass", t0, gain - 1.0, "musik", m=bassnote, dauer=min(d + 0.4, 3.2))
            if figur not in ("ruhig", "bewegt", "steigend"):
                continue
            noten = musik.zerlegt(akkord)
            folge = noten if figur != "bewegt" else noten + noten[-2:0:-1]
            step = beat if figur == "ruhig" else beat / 2
            tt, i = t0 + 0.04, 0
            while tt < t1 - 0.1:
                g = gain - 4.0 - (1.5 if i % 2 else 0.0) + (4.0 * (tt - t0) / d if figur == "steigend" else 0.0)
                self.ton("zupf", tt, g, "musik", m=folge[i % len(folge)], dauer=1.0, pan=0.25 * ((i % 3) - 1))
                tt += step; i += 1

    def klanglogo(self, t0, tonika=67, gain=-6.0):
        """Klanglogo zum Abspann (seit 16.10.2026, ohne Kenney-Klicks): Dur-Dreiklang aufwaerts, dann die Oktave."""
        for k, d in enumerate((0, 4, 7)):
            self.ton("zupf", t0 + 0.14 * k, gain - 1.0, "klanglogo", m=tonika + d, dauer=1.2, pan=0.2 * (k - 1))
        self.ton("zupf", t0 + 0.5, gain, "klanglogo", m=tonika + 12, dauer=1.6)

    def hook1(self, h, root=55.0, akkord=None, bassnote=None):
        """Klangsignatur von Hook 1 (h = reelkit.Hook1): Ton ab 0,0 s (Rueckwaerts-Anschwellen bis zum Zugreifen),
        Kreide-Klatsch beim Griff, Einschlag + Braam + Knacken bei "× GEOLOGY", Luftzug beim Uebergang in die Kopfzeile.
        root: Grundton des Braam (55 = A; je Reel variieren, z. B. 49 = G, 58.3 = B-flat).
        akkord (seit 16.10.2026, fuer alle neuen Reels): musikalische Fassung in der Tonart des Reels, anschwellende
        Flaeche statt Rauschen, Akkordschlag statt Braam, Einschlag, Klatsch und Gestein leiser."""
        if akkord:
            self.ton("schwelle", 0.0, -8.0, "hook1-anschwellen", akkord=akkord, dauer=max(0.2, h.t_grab))
            self.klang("chalk_slap", h.t_grab, -9.0, "hook1-griff")
            self.klang("sub_hit", h.t_geo - 0.01, -8.0, "hook1-einschlag")
            self.ton("akzent", h.t_geo, -5.0, "hook1-akkord", akkord=akkord, bassnote=bassnote or min(akkord) - 12)
            self.klang("crunch", h.t_geo + 0.02, -15.0, "hook1-gestein")
            self.synth("whoosh", h.t_out - 0.04, -18.0, "hook1-uebergang", dur=0.5, seed=12)
            return
        self.klang("reverse", 0.0, -9.0, "hook1-anschwellen", dur=max(0.2, h.t_grab))
        self.klang("chalk_slap", h.t_grab, -3.0, "hook1-griff")
        self.klang("sub_hit", h.t_geo - 0.01, -2.0, "hook1-einschlag")
        self.klang("braam", h.t_geo, -7.0, "hook1-braam", root=root)
        self.klang("crunch", h.t_geo + 0.02, -6.0, "hook1-gestein")
        self.synth("whoosh", h.t_out - 0.04, -11.0, "hook1-uebergang", dur=0.42, seed=12)

    def pulse(self, t0, t1, bpm=116, gain=-15.0, hat_gain=-23.0, avoid=(), avoid_s=0.14):
        """Puls (Kick auf dem Schlag, Hi-Hat dazwischen) von t0 bis t1. Vor pads() aufrufen: die Flaeche duckt sich unter
        jedem Schlag (pumpt), das treibt Hook 2 und die Zuege. avoid: Zeiten grosser Treffer, dort faellt der Schlag aus."""
        beat = 60.0 / bpm; t = t0; k = 0
        while t < t1 - 0.05:
            for tt, kind, g in ((t, "kick", gain), (t + beat / 2, "hat", hat_gain)):
                if tt < t1 and all(abs(tt - a) > avoid_s for a in avoid):
                    smp = self.klang(kind, tt, g + (1.5 if kind == "kick" and k % 4 == 0 else 0.0), "puls", seed=k)
                    if kind == "hat":
                        self.no_duck.add(id(smp))
            t += beat; k += 1

    def countdown(self, t0, t1, step=0.33, gain=-12.0, tonleiter=None):
        """Rate-Pause im Quiz: Toene im Abstand step von t0 bis t1, aufsteigend, der letzte eine Oktave ueber dem ersten
        (aktive Pause statt Stille). Seit 16.10.2026 weiche Zupftoene statt Klicks; tonleiter: MIDI-Noten in der Tonart
        des Reels (Standard: G-Dur-Pentatonik ab G4)."""
        ton = tonleiter or [67, 69, 71, 74, 76, 79]
        n = max(1, int((t1 - t0) / step + 1e-6))
        for i in range(n):
            m_ = ton[min(i, len(ton) - 1)] if i < n - 1 else ton[0] + 12
            self.ton("zupf", t0 + i * step, gain + (2.0 if i == n - 1 else 0.0), "countdown", m=m_, dauer=0.6)

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
            rel = [(t - t0, smp, gg) for t, smp, gg in self.ev if t0 <= t < t1 and id(smp) not in self.no_duck]
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


# ------------------------------------------------------------------ Meta-Hook / Kopfzeile (seit 13.10.2026)
# Wo man gelandet ist: Kopfzeile, in jedem Reel gleich. Mittags noch "GEOCRIMPS · GEOLOGY OF CLIMBING" ab Frame 0;
# seit dem Abend (Hook 1, siehe unten) "GEOCRIMPS · CLIMBING × GEOLOGY": die grossen Hook-1-Woerter schrumpfen in diese Zeile.
META_HOOK = ("GEOCRIMPS", "CLIMBING × GEOLOGY")
META_HOOK_Y, FORMAT_Y, HOOK_Y = 300, 352, 404      # Kopfzeile, Formatlabel, Hook-Frage (vorher Label 300, Hook 352)


def tracked_width(s, role, size, tracking):
    f = o.font(role, size)
    return (sum(f.getlength(ch) for ch in s) + tracking * size * o.S * (len(s) - 1)) / o.S


def meta_hook(y=META_HOOK_Y, x=X0, size=40, tracking=0.12, desc_color=C["magnesia"]):
    """GEOCRIMPS (magnesia) . GEOLOGY OF CLIMBING; als Bildmarke dient das Logo oben an der Topo-Linie links daneben.
    Steht ab Frame 0 und geht zusammen mit der Hook-Frage. Markenelement wie das Endsignet: zaehlt nicht zu den 40 Woertern."""
    brand, desc = META_HOOK
    w1 = tracked_width(brand, "stencil", size, tracking)
    gap = size * 0.42
    wd = o.text_width("·", "stencil", size)

    def d(im):
        o.text(im, x, y, brand, "stencil", size, C["magnesia"], tracking=tracking)
        o.text(im, x + w1 + gap, y, "·", "stencil", size, C["slate"])
        o.text(im, x + w1 + 2 * gap + wd, y, desc, "stencil", size, desc_color, tracking=tracking)
    return m.sprite(d)


def sichtbar(img, spr):
    """Anteil der deckenden Pixel eines Sprites, die im fertigen Bild so erscheinen wie gezeichnet.
    Nahe 1 = steht frei im Bild; klein = fehlt oder ist verdeckt."""
    a = np.asarray(spr.img.getchannel("A")) > 200
    ref = np.asarray(spr.img.convert("RGB"), dtype=np.float32)
    reg = np.asarray(img.convert("RGB") if hasattr(img, "convert") else img, dtype=np.float32)
    reg = reg[spr.y:spr.y + spr.h, spr.x:spr.x + spr.w, :3]
    if reg.shape[:2] != a.shape or not a.any():
        return 0.0
    return round(float((np.abs(reg - ref).mean(axis=2)[a] < 40).mean()), 3)


def meta_hook_sichtbar(cover):
    """Kopfzeile (Meta-Hook) im Cover: Anteil wie in sichtbar()."""
    return sichtbar(cover, meta_hook())


# ------------------------------------------------------------------ Hook 1 "CLIMBING × GEOLOGY" (seit 13.10.2026, abends)
# Markus 13.10.: "hook 1 (klettern und geologie) und dann hook 2 (eigentliches reel thema)". Anlass: Reel #1 verlor in
# der ersten Sekunde ein Viertel der Zuschauer, und bei Reel #2 wurde am Anfang nicht klar, worum es geht.
# Hook 1 (1,0-1,6 s): GEOCRIMPS klein und CLIMBING gross ab Frame 0; ein Kletterer (kletter.Climber) greift den Griff
# des Reels (Kreidewolke, Klatschen), dann schlaegt "× GEOLOGY" ein und das Gestein klappt in seine Geologie auf
# (kletter.GeoReveal, Einschlag + Braam). Danach schrumpfen die grossen Woerter in die Kopfzeile und Hook 2 (die
# Themenfrage, mindestens 3,2 s) faehrt ein; der Kletterer bleibt im Bild. Die Hook-1-Woerter sind wie die Kopfzeile
# ein Markenelement und zaehlen nicht zu den 40 Woertern.
HOOK1_WORDS = ("CLIMBING", "× GEOLOGY")
HOOK1_RANGE = (1.0, 1.6)            # Frame 0 bis Beginn des Uebergangs in die Kopfzeile
HOOK1_OUT = 0.34                    # Dauer des Uebergangs


def _offset_in_tracked(s, i, role, size, tracking):
    f = o.font(role, size)
    return (sum(f.getlength(ch) for ch in s[:i]) + tracking * size * o.S * i) / o.S


class Hook1:
    """Text und Zeitplan von Hook 1. draw(f, t) zeichnet je nach t: Marke + CLIMBING (ab Frame 0), Puls beim Zugreifen
    (t_grab), Einschlag "× GEOLOGY" (t_geo), Uebergang in die Kopfzeile (t_out .. t_out + HOOK1_OUT), danach die
    Kopfzeile bis hook_bis (dann blendet sie mit der Themenfrage aus). Bild (Kletterer, Aufklappen) zeichnet das Reel."""

    def __init__(self, t_grab=0.38, t_geo=0.68, t_out=1.40, size=214, y=FORMAT_Y - 6):
        self.t_grab, self.t_geo, self.t_out = t_grab, t_geo, t_out
        self.kicker = meta_hook()
        self.brand = m.text_sprite(META_HOOK[0], X0, META_HOOK_Y, "stencil", 40, C["magnesia"], tracking=0.12)
        sz = min(m.fit(w, "display", size) for w in HOOK1_WORDS)
        self.size = sz
        y2 = y + sz * 0.9
        self.w1 = m.text_sprite(HOOK1_WORDS[0], X0, y, "display", sz, C["magnesia"])
        self.brand.text = self.w1.text = None      # Markenintro mit fester Dauer: nicht Teil der Lesezeit-Pruefung
        wx = o.text_width("× ", "display", sz)

        def geo(im):
            o.text(im, X0, y2, "×", "display", sz, C["slate"])
            o.text(im, X0 + wx, y2, HOOK1_WORDS[1][2:], "display", sz, C["magnesia"])
        self.w2 = m.sprite(geo)
        self.bottom = y2 + sz * 0.95                                   # Unterkante der grossen Woerter
        # Zielpositionen in der Kopfzeile (meta_hook: Marke, Punkt, Beschreibung)
        brand, desc = META_HOOK
        w_brand = tracked_width(brand, "stencil", 40, 0.12)
        gap = 40 * 0.42; wd = o.text_width("·", "stencil", 40)
        xd = X0 + w_brand + 2 * gap + wd
        i2 = desc.index("×")
        self.targets = []
        for spr, sub, x_t in ((self.w1, desc[:i2 - 1], xd), (self.w2, desc[i2:], xd + _offset_in_tracked(desc, i2, "stencil", 40, 0.12))):
            k = tracked_width(sub, "stencil", 40, 0.12) / max(1.0, spr.w)
            self.targets.append((spr, k, x_t, self.kicker.y))

    def draw(self, f, t, hook_bis=None, fade=0.12):
        """Bis t_out + HOOK1_OUT: Hook 1 und Uebergang; danach Kopfzeile (blendet ab hook_bis aus, wenn angegeben)."""
        t1 = self.t_out + HOOK1_OUT
        if t >= t1:
            op = 1.0 if hook_bis is None else 1 - seg(t, hook_bis, fade)
            put(f, self.kicker, op=op)
            return
        v = seg(t, self.t_out, HOOK1_OUT)
        if v > 0:                                                       # Uebergang: der Block schrumpft in die Kopfzeile
            u = 0.5 - 0.5 * math.cos(math.pi * v)                       # weich an beiden Enden
            put(f, self.brand)
            put(f, self.kicker, op=seg(t, self.t_out + 0.5 * HOOK1_OUT, 0.5 * HOOK1_OUT))
            fade_big = 1 - seg(t, self.t_out + 0.45 * HOOK1_OUT, 0.5 * HOOK1_OUT)
            (s1, k1, x_t, y_t), _ = self.targets
            ax, ay = s1.x, s1.y                                         # beide Woerter gemeinsam skalieren: kein Ueberlappen
            for spr in (self.w1, self.w2):
                put(f, spr, dx=(x_t - ax) * u, dy=(y_t - ay) * u, op=fade_big, scale=lerp(1.0, k1, u), anchor=(ax, ay))
            return
        put(f, self.brand)
        bump = math.sin(math.pi * seg(t, self.t_grab, 0.2)) if t >= self.t_grab else 0.0
        put(f, self.w1, scale=1 + 0.06 * bump, anchor=(self.w1.x, self.w1.y + self.w1.h / 2))
        v = seg(t, self.t_geo, 0.22)
        if v > 0:
            put(f, self.w2, op=min(1.0, v * 3), scale=lerp(1.32, 1.0, griff(v)) if v < 1 else 1.0,
                anchor=(self.w2.x, self.w2.y + self.w2.h / 2))

    def frame0_anteil(self, img):
        """Stehen GEOCRIMPS und CLIMBING frei in Frame 0? (kleinerer der beiden Anteile)"""
        return min(sichtbar(img, self.brand), sichtbar(img, self.w1))


# ------------------------------------------------------------------ Ablauf und Lesezeit (seit 13.10.2026)
ABLAEUFE = ("quiz", "offene_frage", "erklaerkette")
HOOK_MIN_S, FRAGE_MIN_S = 3.6, 1.5      # Hook-Frage bzw. jede weitere Frage im Bild, Beginn bis Beginn des Ausblendens
                                         # (16.10.2026: 3,2 -> 3,6 s und 1,2 -> 1,5 s, "alles noch etwas langsamer")

# Lesezeit (seit 15.10.2026, Wunsch Markus: mehr Zeit an Momenten mit neuer Information, ohne Leerlauf; 16.10.2026:
# "alles noch etwas langsamer und bewusster"). Jeder Text im Bild muss je Auftritt voll sichtbar (Deckkraft >= VOLL_OP)
# mindestens LESE_BASIS_S + LESE_JE_WORT_S je Wort stehen; Aufloesung und Fazit (META "verdauen") zusaetzlich VERDAU_S.
# 0,35 s je Wort entspricht gut 170 Woertern pro Minute: im Bereich der BBC-Untertitelrate (160-180 wpm) und langsamer
# als stilles Lesen englischer Sachtexte (Mittel 238 wpm, Brysbaert 2019), weil viele Zuschauer Englisch als Zweitsprache
# lesen und gleichzeitig das Bild verfolgen. 15.10.: 0,6 s + 0,3 s, Verdauen 0,6 s; 16.10.: 0,75 s + 0,35 s, Verdauen 0,8 s.
LESE_BASIS_S, LESE_JE_WORT_S, VERDAU_S, VOLL_OP = 0.75, 0.35, 0.8, 0.95

# Ton (seit 16.10.2026, Markus: "die toene nicht ganz so klirrend metallisch bitte, eher musikalische untermalung"):
# Neue Reels haben Musik (SoundBook.musik), keinen Puls mit Hi-Hats und keine metallischen oder UI-Klicks von Kenney.
KENNEY_VERBOTEN = ("impactMetal", "impactMining", "impactPunch", "impactGeneric", "maximize", "minimize", "question",
                   "tick_", "pluck_", "drop_", "click_", "switch_", "glass_", "bong_")


def hochton_anteil(wav_path, f_grenze=4000.0):
    """Anteil der Energie oberhalb f_grenze Hz in Prozent und spektraler Schwerpunkt in Hz (Mono-Summe der Mischung)."""
    import wave
    with wave.open(wav_path) as w:
        n, ch, sw = w.getnframes(), w.getnchannels(), w.getsampwidth()
        a = np.frombuffer(w.readframes(n), dtype={2: np.int16, 4: np.int32}[sw]).reshape(-1, ch).astype(np.float64)
    x = a.mean(axis=1)
    X = np.abs(np.fft.rfft(x)) ** 2
    f = np.fft.rfftfreq(len(x), 1 / SR)
    tot = X.sum() or 1.0
    return round(100 * X[f > f_grenze].sum() / tot, 3), round(float((X * f).sum() / tot), 0)


def woerter(s):
    return len(s.replace("…", " ").replace("·", " ").replace("×", " ").split())


def lesezeit_noetig(text, verdauen=False):
    return round(LESE_BASIS_S + LESE_JE_WORT_S * woerter(text) + (VERDAU_S if verdauen else 0.0), 2)


def lesezeiten(textlog, verdauen=()):
    """Je Text und Auftritt (zusammenhaengend sichtbar): ab wann, wie lange voll sichtbar, wie lange noetig."""
    dt = 1.0 / FPS
    texte = []
    for _, log in textlog:
        for txt, _ in log:
            if txt not in texte:
                texte.append(txt)
    res = []
    for txt in texte:
        cur = None
        for t, log in list(textlog) + [(None, [])]:               # Waechter-Eintrag schliesst den letzten Auftritt
            op = max([o_ for x, o_ in log if x == txt], default=0.0)
            if op > 0.02:
                if cur is None:
                    cur = {"text": txt, "ab_s": round(t, 2), "voll_s": 0.0}
                if op >= VOLL_OP:
                    cur["voll_s"] += dt
            elif cur is not None:
                cur["voll_s"] = round(cur["voll_s"], 2)
                cur["noetig_s"] = lesezeit_noetig(txt, txt in verdauen)
                cur["verdauen"] = txt in verdauen
                cur["ok"] = cur["voll_s"] >= cur["noetig_s"] - 1e-6
                res.append(cur)
                cur = None
    return sorted(res, key=lambda r_: r_["ab_s"])


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
    ablauf (quiz | offene_frage | erklaerkette, wie der Slot im Themenplan), hook_ab / hook_bis (Hook 2: Beginn des
    Einblendens / des Ausblendens der Themenfrage), weitere_fragen ([[Beginn, Beginn des Ausblendens], ...] je weiterer
    Frage im Bild), hook1_bis (Beginn des Uebergangs von Hook 1 in die Kopfzeile), cover_t (Zeitpunkt des Covers: ein
    Bild aus Hook 2 mit Kopfzeile und Themenfrage), verdauen (Texte der Aufloesung und des Fazits, genau wie die Sprites sie
    tragen; sie brauchen VERDAU_S mehr Lesezeit), abspann_ab (Beginn des Abspanns reelkit.Outro; der Payoff-Anteil
    bezieht sich dann auf die Zeit bis zum Abspann). Das Reel stellt seine reelkit.Hook1-Instanz als self.hook1 und
    seinen Abspann als self.outro bereit.
    Text im Bild nur ueber m.text_sprite / m.lines_sprite oder ein Sprite mit .text: nur so misst die Lesezeit-Pruefung ihn."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "..", "..", "reels"))
    ap.add_argument("--qc", default=None, help="Ordner fuer QC-Dateien")
    ap.add_argument("--stills", default=None, help="Kommagetrennte Zeitpunkte: nur Einzelbilder in --qc schreiben")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    slug = META["slug"]
    stem = META.get("datei", slug)                                # Dateiname (Neufassung eines Reels: z. B. <slug>_v2)
    r = ReelCls()
    if a.stills:
        os.makedirs(a.qc, exist_ok=True)
        for ts in a.stills.split(","):
            f, s = r.frame(float(ts))
            Image.fromarray(r.fin(f, s)).save(os.path.join(a.qc, f"still_{float(ts):05.2f}.png"))
        return
    qc = a.qc or a.out
    os.makedirs(qc, exist_ok=True)
    f0, s0 = r.frame(0.0)                                         # Frame 0: Hook 1 (GEOCRIMPS + CLIMBING)
    frame0 = r.fin(f0, s0)
    h1 = getattr(r, "hook1", None)
    hook1_frame0 = h1.frame0_anteil(frame0) if h1 else 0.0
    cover_t = float(META.get("cover_t", 0.0))                     # Cover: Bild aus Hook 2 (Kopfzeile + Themenfrage)
    fc, sc = r.frame(cover_t)
    cover = r.fin(fc, sc)
    Image.fromarray(cover).save(os.path.join(a.out, stem + ".jpg"), quality=92)
    meta_ok = meta_hook_sichtbar(cover)
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
    sheet.save(os.path.join(qc, stem + "_kontaktbogen.png"))
    book = SoundBook()                                            # Ton
    sound_events(book)
    tmp = os.path.join(qc, stem + "_mix.wav"); norm = os.path.join(qc, stem + "_norm.wav")
    m.write_wav(tmp, m.mix(book.ev, r.DUR))
    ln = m.master(tmp, norm)
    mp4 = os.path.join(a.out, stem + ".mp4")                      # Video
    n = int(round(r.DUR * FPS))
    m.encode(r.frames(), n, mp4, audio_wav=norm, crf=21)
    tonverlauf_png(mp4, os.path.join(qc, stem + "_tonverlauf.png"), META.get("marks", []), META.get("title", slug))
    words = sum(len(s.replace("·", " ").split()) for s in META["on_screen"])
    rep = {"slug": slug, "datei": stem, "dauer_s": r.DUR, "fps": FPS, "frames": n, "mp4_mb": round(os.path.getsize(mp4) / 1e6, 2),
           "woerter_im_bild": words, "labels": len(META.get("labels", [])),
           "woerter_gesamt_mit_labels": words + sum(len(s.split()) for s in META.get("labels", [])),
           "payoff_anteil": round(META["payoff_t"] / (META.get("abspann_ab") or r.DUR), 3), "loudnorm": ln,
           "messung": m.measure(mp4), "toene": book.licenses()}
    quellen = [q for v in book.used.values() for q in v]          # Ton: Musik statt Metall (seit 16.10.2026)
    metall = sorted({q for q in quellen if q.startswith("CC0 Kenney") and any(x in q for x in KENNEY_VERBOTEN)})
    hoch, schwerpunkt = hochton_anteil(norm)
    rep.update({"metallische_klaenge": metall, "puls_mit_hihat": "puls" in book.used,
                "hochton_anteil_ueber_4khz_prozent": hoch, "spektraler_schwerpunkt_hz": schwerpunkt})
    outro = getattr(r, "outro", None)                             # Abspann mit Aufruf (seit 16.10.2026)
    ab, ab_vor = plan_ablauf(slug)
    fragen = META.get("weitere_fragen", [])
    hook_s = round((META.get("hook_bis") or 0) - (META.get("hook_ab") or 0), 2)
    h1_bis = META.get("hook1_bis")
    rep.update({"ablauf": META.get("ablauf"), "ablauf_im_themenplan": ab, "ablauf_slot_davor": ab_vor,
                "hook1": " / ".join(HOOK1_WORDS), "hook1_bis_s": h1_bis, "hook1_in_frame0_anteil": hook1_frame0,
                "hook1_woerter_extra": sum(len(s.replace("×", " ").split()) for s in HOOK1_WORDS),
                "hook_ab_s": META.get("hook_ab"), "hook_bis_s": META.get("hook_bis"), "hook_steht_s": hook_s, "hook_min_s": HOOK_MIN_S,
                "fragen_min_s": FRAGE_MIN_S,
                "weitere_fragen_stehen_s": [round(b - a, 2) for a, b in fragen], "cover_t": cover_t,
                "meta_hook": " · ".join(META_HOOK), "meta_hook_woerter_extra": sum(len(s.replace("×", " ").split()) for s in META_HOOK),
                "meta_hook_im_cover_anteil": meta_ok})
    verd = list(META.get("verdauen", []))                         # Lesezeit je Info (gemessen beim Rendern)
    lz = lesezeiten(getattr(r, "textlog", []), verd)
    gemessen = {x["text"] for x in lz}
    soll_w = sum(woerter(s) for s in META["on_screen"]) + sum(woerter(s) for s in META.get("labels", []))
    rep.update({"lesezeit_regel": f"voll sichtbar >= {LESE_BASIS_S} s + {LESE_JE_WORT_S} s je Wort, "
                                  f"Aufloesung/Fazit +{VERDAU_S} s (Deckkraft >= {VOLL_OP})",
                "lesezeiten": lz, "verdauen": verd,
                "woerter_gemessen": sum(woerter(s) for s in gemessen), "woerter_laut_meta": soll_w})
    for x in lz:
        print(f"  Lesezeit {'ok ' if x['ok'] else 'ZU KURZ'} {x['ab_s']:6.2f} s  {x['voll_s']:4.2f} / {x['noetig_s']:4.2f} s  {x['text']}")
    checks = {"dauer_im_formatrahmen": META.get("dur_range", [0, 99])[0] <= r.DUR <= META.get("dur_range", [0, 99])[1],
              "hook1_klettern_geologie_in_frame_0": hook1_frame0 >= 0.9,
              "hook1_dauer_1_0_bis_1_6_s": h1_bis is not None and HOOK1_RANGE[0] <= h1_bis <= HOOK1_RANGE[1],
              "hook2_nach_hook1": h1_bis is not None and (META.get("hook_ab") or 0) >= h1_bis,
              "meta_hook_im_cover": meta_ok >= 0.9,
              "hook_frage_mindestdauer": hook_s >= HOOK_MIN_S - 1e-6,
              "weitere_fragen_mindestdauer": all(b - a >= FRAGE_MIN_S - 1e-6 for a, b in fragen),
              "lesezeit_je_info": bool(lz) and all(x["ok"] for x in lz),
              "verdauzeit_aufloesung_und_fazit": bool(verd) and all(v in gemessen for v in verd),
              "alle_texte_gemessen": rep["woerter_gemessen"] == soll_w,
              "ablauf_wie_im_themenplan": META.get("ablauf") in ABLAEUFE and META.get("ablauf") == ab,
              "ablauf_anders_als_im_slot_davor": ab is not None and ab != ab_vor,
              "payoff_65_80_prozent": 0.65 <= rep["payoff_anteil"] <= 0.80,
              "hoechstens_40_woerter": rep["woerter_gesamt_mit_labels"] <= 40,
              "lautheit_-14_+-0.5": abs(rep["messung"].get("I_LUFS", 0) + 14) <= 0.5,
              "true_peak_max_-1": rep["messung"].get("TP_dBFS", 0) <= -1.0,
              "mp4_unter_100_mb": rep["mp4_mb"] < 100,
              "abspann_mit_aufruf": bool(outro) and META.get("abspann_ab") is not None
                  and abs(META["abspann_ab"] + Outro.DUR - r.DUR) < 0.05
                  and any(x["text"] == Outro.CTA and x["ok"] for x in lz),
              "musik_statt_metall": "musik" in book.used and not metall and "puls" not in book.used}
    rep["pruefungen"] = checks
    rep["alle_pruefungen_ok"] = all(checks.values())
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    json.dump(rep, open(os.path.join(qc, stem + "_bericht.json"), "w"), ensure_ascii=False, indent=1)
