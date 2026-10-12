#!/usr/bin/env python3
"""Reel 001 -- WHODUNIT #01: "Nobody drilled these holes." (Faktenbasis: Post #008).

Dramaturgie (Topo): Hook 0-2,2 s | Verdaechtige + Pause 2,45-6,1 s | Zug 1 Regen + CO2 6,3-9,6 s |
Zug 2 (Crux) Schwachstellen 9,95-13,0 s | Payoff 13,05 s (78 %) | Endsignet 16,0-16,8 s.
Aufruf:  python3 r001_whodunit_008.py --out ../../../reels  [--sfx <Ordner mit CC0-Klaengen>] [--draft]
"""
import argparse, json, math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import outcrop as o
import motion as m
from outcrop import C, P
from motion import X0, W, H, FPS, seg, seilzug, sturz, griff, lerp, put

DUR = 16.8
SLUG = "2026-10-12_whodunit-01"
ON_SCREEN = ["WHODUNIT", "NOBODY DRILLED THESE HOLES.", "3 SUSPECTS", "CLIMBERS WITH A DRILL", "WIND AND SAND",
             "RAIN", "Pause. Your guess?", "RAIN GRABS CO₂ FROM AIR AND SOIL.", "IT EATS THE WEAK SPOTS FIRST.",
             "VERDICT", "RAIN.", "DISSOLVED, NOT CARVED."]
LABELS = ["CO₂", "CO₂", "FOSSIL", "CRACK"]

# ------------------------------------------------------------------ Zeitplan
T_W1, T_S2 = 2.20, 2.45          # Isolinien-Welle -> Verdaechtige
T_ROWS = (2.75, 3.05, 3.35)
T_PAUSE = 4.60
T_W2, T_S3 = 6.10, 6.32          # Welle -> Regen
T_DROPS = (6.60, 6.85, 7.10, 7.35, 7.60, 7.85)
FALL = 0.55
T_CR, T_S4 = 9.60, 9.95          # Riss -> Crux
T_GROW = (10.30, 10.60)
T_TICKS = 11.70
T_S5 = 13.05                     # Payoff
T_SWIPE = 13.95
T_NOT = 14.45
T_END = 16.00

RAIL_Y = [1300 - 227.5 * (i + 0.5) for i in range(4)]   # Bohrhaken-Positionen (outcrop.route_rail)


# ------------------------------------------------------------------ Bausteine (aus dem Storyboard)
def wall(im, top=930, dim=0, seed=1):
    poly = o.ragged(110, top, 1090, 1960, seed=seed, amp=16, n=18, top_only=True)
    o.rock_body(im, poly, fill=C["graphite"], pattern="limestone", pat_color=C["line"], sketch=False, seed=seed)
    ImageDraw.Draw(im).line([P(x, y) for x, y in poly[:19]], fill=o.rgb(C["magnesia"]), width=int(4 * o.S), joint="curve")
    for cx, cy, rx, ry in [(300, top + 150, 46, 34), (525, top + 80, 30, 24), (720, top + 220, 60, 42),
                           (430, top + 330, 36, 28), (875, top + 120, 40, 30), (980, top + 330, 34, 26)]:
        o.pocket(im, cx, cy, rx, ry)
    if dim:
        im.alpha_composite(Image.new("RGBA", im.size, o.rgb(C["obsidian"], dim)))
    return poly

def wall_top_y(poly, x):
    pts = poly[:19]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return pts[-1][1]

def bolt_sprite(i):
    y = RAIL_Y[i]; s = 10
    def d(im):
        dr = ImageDraw.Draw(im); col = o.rgb(C["magnesia"])
        dr.line([P(56 - s, y - s), P(56 + s, y + s)], fill=col, width=int(4 * o.S))
        dr.line([P(56 - s, y + s), P(56 + s, y - s)], fill=col, width=int(4 * o.S))
    return m.sprite(d)


class Reel:
    def __init__(self):
        self.fin = m.Finish()
        self.stamp = m.text_sprite("WHODUNIT", X0, 300, "stencil", 40, C["slate"], tracking=0.12)
        # Szene 1: Hook (Frame 0 = Cover)
        def bg1(im):
            o.contour_field(im, 760, 1500, n=10, r0=120, step=60, alpha=110)
            wall(im)
            o.chalk_ticks(im, 820, 1100, angle_deg=-38, seed=2)
            o.chalk_ticks(im, 400, 1040, angle_deg=-142, seed=5)
            o.route_rail(im, 0, 4)
        self.bg1 = m.background(bg1)
        self.hook, _ = m.lines_sprite(["NOBODY", "DRILLED", "THESE HOLES."], 352)
        # Szene 2: Verdaechtige
        def bg2(im):
            wall(im, dim=170); o.route_rail(im, 1, 4)
        self.bg2 = m.background(bg2)
        self.title2, _ = m.lines_sprite(["3 SUSPECTS"], 352, size=150)
        self.rows = []
        y = 560
        for letter, word in [("A", "CLIMBERS WITH A DRILL"), ("B", "WIND AND SAND"), ("C", "RAIN")]:
            def d(im, y=y, letter=letter, word=word):
                o.hold_label(im, X0, y, letter, C["magnesia"], size=58, role="stencil", pad=(26, 12))
                o.text(im, X0 + 100, y + 4, word, "display_xb", 78, C["magnesia"])
            self.rows.append(m.sprite(d)); y += 128
        self.pause = m.text_sprite("Pause. Your guess?", X0, y + 30, "text_b", 54, C["magnesia"])
        # Szene 3: Regen nimmt CO2 auf
        self.poly3 = None
        def bg3(im):
            self.poly3 = wall(im, top=1060, seed=1); o.route_rail(im, 2, 4)
        self.bg3 = m.background(bg3)
        self.text3, _ = m.lines_sprite(["RAIN GRABS CO₂", "FROM AIR AND SOIL."], 352, role="display_xb", size=118)
        self.drop = m.sprite(lambda im: o.droplet(im, 540, 960, size=40))
        self.co2 = m.text_sprite("CO₂", 540, 960, "mono", 40, C["water"], anchor="lm")
        self.drop_x = [300, 470, 640, 810, 380, 720]
        self.drop_y0 = [600, 640, 590, 660, 700, 620]
        # Szene 4: Crux -- Schwachstellen
        def bg4(im):
            poly = o.ragged(110, 820, 1090, 1960, seed=7, amp=12, n=18, top_only=True)
            o.rock_body(im, poly, fill=C["graphite"], pattern="limestone", pat_color=C["line"], seed=7)
            ImageDraw.Draw(im).line([P(x, y) for x, y in poly[:19]], fill=o.rgb(C["magnesia"]), width=int(4 * o.S))
            o.spiral(im, 380, 1080, r=70, color=C["magnesia"], width=5, dashed=True)
            o.crack(im, [(720, 840), (705, 930), (742, 1010), (716, 1120), (760, 1220)], color=C["slate"], width=5)
            o.route_rail(im, 3, 4)
        self.bg4 = m.background(bg4)
        self.text4, _ = m.lines_sprite(["IT EATS THE", "WEAK SPOTS", "FIRST."], 352, role="display_xb", size=150)
        self.tick_a = m.sprite(lambda im: o.chalk_ticks(im, 520, 1010, angle_deg=-30, seed=3))
        self.tick_b = m.sprite(lambda im: o.chalk_ticks(im, 850, 960, angle_deg=-150, seed=4))
        self.lab_a = m.text_sprite("FOSSIL", 470, 1180, "mono", 30, C["magnesia"], tracking=0.1)
        self.lab_b = m.text_sprite("CRACK", 800, 1120, "mono", 30, C["magnesia"], tracking=0.1)
        # Szene 5: Payoff
        def bg5(im):
            wall(im, top=1120, seed=1); o.route_rail(im, 4, 4, logo_on=True)
        self.bg5 = m.background(bg5)
        self.verdict = m.text_sprite("VERDICT", X0, 330, "stencil", 64, C["slate"], tracking=0.1)
        self.rain, y5 = m.lines_sprite(["RAIN."], 400, size=300)
        sw = o.text_width("DISSOLVED,", "display", 150)
        y5 += 46
        self.swipe = m.sprite(lambda im: o.chalk_swipe(im, X0 - 8, y5 + 18, X0 + sw + 14, y5 + 168, seed=9))
        self.dissolved = m.text_sprite("DISSOLVED,", X0, y5 + 8, "display", 150, C["obsidian"])
        self.notcarved = m.text_sprite("NOT CARVED.", X0, y5 + 184, "display", 150, C["magnesia"])
        self.chipc = m.sprite(lambda im: o.hold_label(im, 640, 352, "C", C["magnesia"], size=58, role="stencil", pad=(26, 12)))
        self.swipe_box = (X0 - 8, y5 + 18, X0 + sw + 14, y5 + 168)
        # Szene 6: Endsignet
        self.bg6 = m.background(lambda im: None)
        lock = Image.open(os.path.join(os.path.dirname(HERE), "assets", "lockup_stacked_dark.png")).convert("RGBA")
        lw = 760; lh = int(lock.height * lw / lock.width)
        self.lockup = m.Sprite(lock.resize((lw, lh), Image.LANCZOS), (W - lw) // 2, 640)
        self.mark_c = (self.lockup.x + 505 * lw / 1000, self.lockup.y + 280 * lw / 1000)
        self.bolts = [bolt_sprite(i) for i in range(4)]

    # -------------------------------------------------------------- Uebergaenge (2x gezeichnet)
    def wave(self, u, cx=540, cy=1100):
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

    def crackline(self, u, alpha=255):
        rnd = random.Random(12); pts = []; x = 560
        for k in range(17):                                   # unterhalb des Textblocks: kreuzt keine Woerter
            pts.append((x + rnd.uniform(-38, 38), 620 + k * 84))
        n = max(2, int(len(pts) * u))
        return m.sprite(lambda im: ImageDraw.Draw(im).line([P(px, py) for px, py in pts[:n]],
                                                           fill=o.rgb(C["magnesia"], alpha), width=int(6 * o.S), joint="curve"))

    def contract(self, u):
        cx, cy = self.mark_c
        def d(im):
            o.contour_field(im, cx, cy, n=9, r0=lerp(420, 60, u), step=lerp(70, 12, u), color=C["slate"],
                            alpha=int(lerp(230, 110, u)), width=2.6, seed=4, squash=0.86)
        return m.sprite(d)

    # -------------------------------------------------------------- Frames
    def bolt_pop(self, f, t, i, t0):
        u = seg(t, t0, 0.3)
        if 0 < u < 1:
            put(f, self.bolts[i], scale=lerp(1.9, 1.0, griff(u)))

    def frame(self, t):
        if t < T_W1 + 0.25:                                        # Szene 1
            f = m.zoomed(self.bg1, 1 + 0.03 * seilzug(seg(t, 0, T_W1)), 600, 1250)
            put(f, self.stamp); put(f, self.hook)
            if t >= T_W1:
                put(f, self.wave(seg(t, T_W1, 0.5)))
            return f, 11
        if t < T_W2 + 0.22:                                        # Szene 2
            f = self.bg2.copy()
            put(f, self.stamp)
            u = seilzug(seg(t, T_S2, 0.3)); put(f, self.title2, dx=lerp(-40, 0, u), op=u)
            for spr, t0 in zip(self.rows, T_ROWS):
                u = seg(t, t0, 0.3)
                put(f, spr, dx=lerp(-50, 0, griff(u)), op=min(1, u * 1.6))
            u = seilzug(seg(t, T_PAUSE, 0.35)); put(f, self.pause, dx=lerp(-30, 0, u), op=u)
            self.bolt_pop(f, t, 0, T_S2)
            if t < T_W1 + 0.5:
                put(f, self.wave(seg(t, T_W1, 0.5)))
            if t >= T_W2:
                put(f, self.wave(seg(t, T_W2, 0.45), cy=500))
            return f, 12
        if t < T_CR + 0.35:                                        # Szene 3
            f = self.bg3.copy()
            u = seilzug(seg(t, T_S3 + 0.03, 0.35)); put(f, self.text3, dx=lerp(-40, 0, u), op=u)
            dr = ImageDraw.Draw(f)
            for k, (x, y0, t0) in enumerate(zip(self.drop_x, self.drop_y0, T_DROPS)):
                yl = wall_top_y(self.poly3, x)
                if t < t0:
                    continue
                u = seg(t, t0, FALL)
                if u < 1:
                    y = lerp(y0, yl - 18, sturz(u))
                    put(f, self.drop, dx=x - 540, dy=y - 960, op=min(1, u * 5))
                    if k in (1, 3):
                        put(f, self.co2, dx=x - 540 + 32, dy=y - 960 - 26, op=min(1, u * 5))
                else:
                    v = seg(t, t0 + FALL, 0.6)
                    r = 10 + 34 * seilzug(v)
                    a = int(220 * (1 - v))
                    if a > 0:
                        dr.ellipse([x - r, yl - r * 0.32, x + r, yl + r * 0.32], outline=o.rgb(C["water"], a), width=3)
                    ln = 140 * seilzug(v)
                    dr.line([(x, yl + 6), (x + 6, yl + 6 + ln)], fill=o.rgb(C["water"], int(200 * (1 - 0.6 * v))), width=4)
            self.bolt_pop(f, t, 1, T_S3)
            if t < T_W2 + 0.45:
                put(f, self.wave(seg(t, T_W2, 0.45), cy=500))
            if t >= T_CR:
                put(f, self.crackline(sturz(seg(t, T_CR, 0.35))))
            return f, 13
        if t < T_S5:                                               # Szene 4
            f = self.bg4.copy()
            u = seilzug(seg(t, T_S4 + 0.03, 0.35)); put(f, self.text4, dx=lerp(-40, 0, u), op=u)
            dr = ImageDraw.Draw(f)
            g1 = seilzug(seg(t, T_GROW[0], 1.2)); g2 = seilzug(seg(t, T_GROW[1], 1.2))
            if g1 > 0:
                s = lerp(0.15, 1.0, g1); cx, cy, rx, ry = 395, 1085, 65, 55
                dr.pieslice([cx - rx * s, cy - ry * s, cx + rx * s, cy + ry * s], 190, 350, fill=o.rgb(C["obsidian"]))
            if g2 > 0:
                s = lerp(0.1, 1.0, g2); cx, cy, rx, ry = 735, 1025, 35, 25
                dr.ellipse([cx - rx * s, cy - ry * s, cx + rx * s, cy + ry * s], fill=o.rgb(C["obsidian"]))
            rnd = random.Random(31)
            for b in range(18):                                    # feines Aufloesen: Blaeschen
                t0 = T_GROW[b % 2] + rnd.uniform(0, 1.2); bx = (395 if b % 2 == 0 else 735) + rnd.uniform(-40, 40)
                v = seg(t, t0, 0.8)
                if 0 < v < 1:
                    by = (1060 if b % 2 == 0 else 1010) - 90 * v; r = rnd.uniform(3, 6)
                    dr.ellipse([bx - r, by - r, bx + r, by + r], outline=o.rgb(C["water"], int(230 * (1 - v))), width=2)
            u = seg(t, T_TICKS, 0.3)
            for spr in (self.tick_a, self.tick_b, self.lab_a, self.lab_b):
                put(f, spr, op=min(1, u * 1.8), scale=lerp(0.7, 1.0, griff(u)) if u < 1 else 1.0)
            self.bolt_pop(f, t, 2, T_S4)
            if t < T_S4 + 0.2:
                v = seg(t, T_S4, 0.2); put(f, self.crackline(1.0, alpha=int(255 * (1 - v))))
            return f, 14
        if t < T_END:                                              # Szene 5: Payoff
            f = self.bg5.copy()
            put(f, self.verdict, op=seg(t, T_S5, 0.15))
            u = seg(t, T_S5, 0.22); put(f, self.rain, op=min(1, u * 2), scale=lerp(1.18, 1.0, seilzug(u)),
                                         anchor=(X0, 400))
            u = seg(t, T_S5 + 0.3, 0.3); put(f, self.chipc, op=min(1, u * 2), scale=lerp(0.6, 1.0, griff(u)) if u < 1 else 1.0)
            put(f, m.reveal(self.swipe, seilzug(seg(t, T_SWIPE, 0.2))))
            put(f, self.dissolved, op=seg(t, T_SWIPE + 0.08, 0.12))
            u = seilzug(seg(t, T_NOT, 0.3)); put(f, self.notcarved, dx=lerp(-40, 0, u), op=u)
            v = seg(t, T_SWIPE + 0.1, 0.6)                         # Kreidestaub beim Treffer
            if 0 < v < 1:
                dr = ImageDraw.Draw(f); rnd = random.Random(77); x0, y0, x1, y1 = self.swipe_box
                for _ in range(40):
                    px = rnd.uniform(x0, x1); py = rnd.uniform(y0, y1); ang = rnd.uniform(0, 6.28); sp = rnd.uniform(30, 120)
                    qx = px + math.cos(ang) * sp * seilzug(v); qy = py + math.sin(ang) * sp * seilzug(v) + 40 * v * v
                    r = rnd.uniform(1.5, 3.5)
                    dr.ellipse([qx - r, qy - r, qx + r, qy + r], fill=o.rgb(C["magnesia"], int(200 * (1 - v))))
            self.bolt_pop(f, t, 3, T_S5)
            return f, 15
        f = self.bg6.copy()                                        # Szene 6: Endsignet
        u = seilzug(seg(t, T_END, 0.45))
        put(f, self.contract(u), op=1 - seg(t, T_END + 0.35, 0.15))
        put(f, self.lockup, op=seg(t, T_END + 0.3, 0.2))
        return f, 16

    def frames(self, draft=False):
        n = int(round(DUR * FPS))
        for i in range(n):
            t = i / FPS
            if draft and i % 3:
                continue
            f, seed = self.frame(t)
            yield self.fin(f, seed)


# ------------------------------------------------------------------ Ton
SFX = os.path.join(os.path.dirname(HERE), "sfx", "kenney")

def K(pack, name):
    return os.path.join(SFX, f"kenney_{pack}", "Audio", name)

def sound_events():
    """CC0-Klaenge (Kenney) plus selbst erzeugte Flaeche, Grollen, Aufloesen und Steigerung."""
    ev, used = [], {}
    def f(path, t, gain, label):
        ev.append((t, m.load_audio(path), gain)); used.setdefault(label, "CC0 Kenney: " + os.path.basename(path))
    def s(kind, t, gain, label, **kw):
        ev.append((t, m.synth(kind, **kw), gain)); used.setdefault(label, f"selbst erzeugt ({kind})")
    ticks = [K("interface-sounds", n) for n in ("tick_001.ogg", "tick_002.ogg", "tick_004.ogg")]
    clacks = [K("impact-sounds", f"impactMetal_light_00{i}.ogg") for i in range(3)]
    drops = [K("interface-sounds", "drop_001.ogg"), K("interface-sounds", "drop_004.ogg")]
    whoosh = K("interface-sounds", "maximize_001.ogg")
    f(ticks[0], 0.35, -8.0, "kreide-tick")
    f(whoosh, T_W1, -7.0, "uebergang")
    f(clacks[0], T_S2, -7.0, "bohrhaken")
    for k, t0 in enumerate(T_ROWS):
        f(ticks[k % 3], t0, -6.0, "kreide-tick")
    f(K("interface-sounds", "question_001.ogg"), T_PAUSE, -7.0, "frage")
    f(whoosh, T_W2, -7.0, "uebergang")
    f(clacks[1], T_S3, -7.0, "bohrhaken")
    for k, t0 in enumerate(T_DROPS):
        f(drops[k % 2], t0 + FALL, -4.0 - (k % 3), "tropfen")
    f(K("impact-sounds", "impactMining_000.ogg"), T_CR, -3.0, "riss")
    f(clacks[2], T_S4, -7.0, "bohrhaken")
    s("fizz", T_GROW[0], -15.0, "aufloesen", dur=1.6, seed=8)
    f(ticks[1], T_TICKS, -6.0, "kreide-tick"); f(ticks[0], T_TICKS + 0.07, -7.0, "kreide-tick")
    s("riser", 11.95, -9.0, "steigerung", dur=0.85)
    f(K("impact-sounds", "impactPunch_heavy_000.ogg"), T_S5, -2.0, "treffer")
    f(clacks[0], T_S5 + 0.02, -9.0, "bohrhaken")
    f(ticks[2], T_S5 + 0.3, -6.0, "kreide-tick")
    f(K("interface-sounds", "scratch_001.ogg"), T_SWIPE, -5.0, "kreide-wisch")
    f(K("interface-sounds", "scratch_002.ogg"), T_SWIPE + 0.08, -7.0, "kreide-wisch")
    pl = m.load_audio(K("interface-sounds", "pluck_001.ogg"))
    for k, r in enumerate((1.0, 1.26, 1.5)):                    # Klanglogo: drei steigende Toene
        ev.append((T_END + 0.12 * k, m.pitch(pl, r), -3.0))
    used["klanglogo"] = "CC0 Kenney: pluck_001.ogg (drei Tonhoehen)"
    f(K("impact-sounds", "impactGeneric_light_000.ogg"), T_END + 0.45, -5.0, "klatsch")
    s("rumble", 0.0, -11.0, "zeit-grollen", dur=2.3, seed=1)
    for t0, t1, g in ((0.0, 12.8, -9.0), (13.35, 16.0, -11.0)):  # Flaeche, vor dem Payoff kurz Stille
        pad = m.synth("pad", dur=t1 - t0, seed=int(t0))
        rel = [(t - t0, smp, gg) for t, smp, gg in ev if t0 <= t < t1]
        ev.append((t0, m.duck(pad, rel, depth_db=-6.0), g))
    used["flaeche"] = "selbst erzeugt (pad)"
    return ev, used


# ------------------------------------------------------------------ Hauptprogramm
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "..", "..", "..", "reels"))
    ap.add_argument("--qc", default=None, help="Ordner fuer QC-Bilder")
    ap.add_argument("--draft", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    r = Reel()
    # Cover = Frame 0
    f0, s0 = r.frame(0.0)
    Image.fromarray(r.fin(f0, s0)).save(os.path.join(a.out, SLUG + ".jpg"), quality=92)
    # QC-Kontaktbogen
    if a.qc:
        os.makedirs(a.qc, exist_ok=True)
        ts = [0.0, 1.5, 2.45, 3.6, 5.2, 6.4, 7.5, 8.6, 9.75, 10.8, 12.2, 13.2, 14.2, 15.2, 16.25, 16.75]
        thumbs = []
        for t in ts:
            f, s = r.frame(t)
            im = Image.fromarray(r.fin(f, s)).resize((270, 480), Image.LANCZOS)
            ImageDraw.Draw(im).text((8, 8), f"{t:.2f}s", fill=(255, 120, 60))
            thumbs.append(im)
        sheet = Image.new("RGB", (270 * 8, 480 * 2), (0, 0, 0))
        for k, im in enumerate(thumbs):
            sheet.paste(im, ((k % 8) * 270, (k // 8) * 480))
        sheet.save(os.path.join(a.qc, SLUG + "_kontaktbogen.png"))
    # Ton
    ev, used = sound_events()
    tmp = os.path.join(a.qc or a.out, SLUG + "_mix.wav"); norm = os.path.join(a.qc or a.out, SLUG + "_norm.wav")
    m.write_wav(tmp, m.mix(ev, DUR))
    ln = m.master(tmp, norm)              # -14 LUFS / <= -1 dBTP im fertigen AAC (mit Probe-Encodes)
    # Video
    mp4 = os.path.join(a.out, SLUG + ".mp4")
    n = int(round(DUR * FPS))
    m.encode(r.frames(), n, mp4, audio_wav=norm, crf=21)
    rep = {"slug": SLUG, "dauer_s": DUR, "fps": FPS, "frames": n, "mp4_mb": round(os.path.getsize(mp4) / 1e6, 2),
           "woerter_im_bild": sum(len(s.replace("·", " ").split()) for s in ON_SCREEN), "labels": len(LABELS),
           "payoff_anteil": round(T_S5 / DUR, 3), "loudnorm": ln, "messung": m.measure(mp4), "toene": used}
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    json.dump(rep, open(os.path.join(a.qc or a.out, SLUG + "_bericht.json"), "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
