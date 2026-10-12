#!/usr/bin/env python3
"""Reel 003 -- MYTH OR ROCK #01: "Looks dry. Safe to climb?" (Faktenbasis: Post #015, Font nach Regen).

Format MYTH OR ROCK: Behauptung -> Mitmach-Pause -> Beleg in zwei Zuegen -> Urteil TRUE / FALSE / IT DEPENDS.
Dramaturgie (Topo): Hook 0-2,25 s | Pause mit TRUE/FALSE 2,45-4,05 s | Zug 1 im Querschnitt: Regen sickert ein,
die Kruste trocknet, der Sand darunter bleibt nass 4,25-6,75 s | Zug 2: nasser Sandstein bricht, die Kruste
waechst nicht nach 6,95-9,45 s | Urteil 9,6 s (73 %) | Folge fuers Klettern 10,15 s | Endsignet 12,3-13,1 s.
Aufruf:  python3 r003_mythorrock_015.py --out ../../../reels --qc <Ordner>   (--stills 0,4.8 fuer Einzelbilder)
"""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import outcrop as o
import motion as m
import reelkit as rk
from outcrop import C, P
from motion import X0, W, H, seg, seilzug, sturz, griff, lerp, put

DUR = 13.1
META = dict(
    slug="2026-10-16_mythorrock-01", dur_range=[10, 15], payoff_t=9.60, title="GeoCrimps r003 MYTH OR ROCK #01",
    on_screen=["MYTH OR ROCK", "LOOKS DRY. SAFE TO CLIMB?", "TRUE", "FALSE", "Pause. Your guess?",
               "DRY CRUST. WET SAND BELOW.", "WET SANDSTONE BREAKS EASIER.", "IT NEVER GROWS BACK.",
               "VERDICT", "FALSE.", "WAIT A DAY OR TWO."],
    labels=["CRUST", "SAND"],
    qc_times=[0.0, 1.5, 2.65, 3.5, 4.35, 4.85, 5.4, 6.2, 6.85, 7.3, 7.7, 8.1, 8.9, 9.75, 10.9, 12.7],
    marks=[(0, "Hook"), (2.25, "Welle"), (2.85, "Pause"), (4.25, "Zug 1"), (4.8, "Regen"), (5.4, "trocknet"),
           (6.75, "Welle"), (6.95, "Zug 2"), (7.6, "Bruch"), (8.6, "Steigerung"), (9.45, "Stille"), (9.6, "PAYOFF"),
           (10.15, "Wisch"), (12.3, "Klanglogo")])

# ------------------------------------------------------------------ Zeitplan
T_W1, T_S2 = 2.25, 2.45            # Welle -> Mitmach-Pause
T_CHIPS = (2.60, 2.75)
T_PAUSE = 2.85                     # "Pause. Your guess?" bis 4,05 (1,2 s)
T_W2, T_S3 = 4.05, 4.25            # Welle -> Zug 1 (Querschnitt)
T_RAIN = [4.36 + 0.09 * k for k in range(7)]
FALL = 0.45
T_SEEP = 4.62                      # Wasser sickert ein (bis ca. 5,8)
T_LAB = (4.95, 5.10)               # Labels CRUST, SAND
T_DRY = 5.40                       # Kruste trocknet ab (bis 6,15), Text "DRY CRUST." / "WET SAND BELOW."
T_CR, T_S4 = 6.75, 6.95            # Welle -> Zug 2
T_PULL, T_BREAK, T_DROP = 7.15, 7.60, 7.85
T_NEVER = 8.55                     # "IT NEVER GROWS BACK."
T_RISE = 8.60
T_S5 = 9.60                        # Urteil (Payoff)
T_SWIPE, T_OR = 10.15, 10.55
T_END = 12.30

# ------------------------------------------------------------------ Block (Font-Sloper) und Farben
XL, XR, HB = 120, 1030, 520        # Block: linke/rechte Fusskante, Hoehe
CX, HA = (XL + XR) / 2, (XR - XL) / 2
# Profil eines Font-Blocks: breit, oben flach, rechts eine gerundete Schulter (der Sloper); Catmull-Rom-Spline
_CTRL = [(0.00, 0), (0.02, 150), (0.06, 290), (0.13, 400), (0.25, 470), (0.40, 505), (0.55, 512), (0.68, 495),
         (0.79, 455), (0.88, 390), (0.94, 300), (0.98, 190), (0.995, 80), (1.0, 0)]
CRUST, CRUST_IN, SCAR = "#D8C6A3", "#9E8A68", "#B89A6E"
YB_MAIN, YB_PAY = 1420, 1560       # Fusslinie in Szene 1-4 bzw. im Urteil (Platz fuer den Text)
F0, F1 = 830, 985                  # Bruchstueck an der rechten Schulter (x-Bereich)

def _catmull(pts, n=24):
    q = [pts[0]] + pts + [pts[-1]]; out = []
    for i in range(1, len(q) - 2):
        p0, p1, p2, p3 = q[i - 1], q[i], q[i + 1], q[i + 2]
        for k in range(n):
            t = k / n; t2 = t * t; t3 = t2 * t
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(pts[-1])
    return out

_D = sorted(_catmull([(XL + u * (XR - XL), h * HB / 512) for u, h in _CTRL]))
_DX = np.array([p[0] for p in _D]); _DH = np.clip(np.array([p[1] for p in _D]), 0, None)

def top_y(x, yb):
    return yb - float(np.interp(x, _DX, _DH))

def surface(yb, x0=XL, x1=XR, step=4):
    xs = list(np.arange(x0, x1 + 0.01, step))
    return [(float(x), top_y(x, yb)) for x in xs]

def normals(pts):
    """Normalen einer von links nach rechts laufenden Oberflaechenlinie, nach innen (ins Gestein) gedreht."""
    out = []
    for i in range(len(pts)):
        a = pts[max(0, i - 1)]; b = pts[min(len(pts) - 1, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]; L = math.hypot(tx, ty) or 1
        out.append((-ty / L, tx / L))
    return out

def offset(pts, d):
    return [(x + nx * d, y + ny * d) for (x, y), (nx, ny) in zip(pts, normals(pts))]

def crack_curve(yb, depth=72):
    """Innere Bruchlinie unter der Schulter: von F0 nach F1, in der Mitte am tiefsten."""
    outer = surface(yb, F0, F1, 3)
    nrm = normals(outer)
    n = len(outer) - 1
    return [(x + nx * (6 + depth * math.sin(math.pi * i / n) ** 0.8), y + ny * (6 + depth * math.sin(math.pi * i / n) ** 0.8))
            for i, ((x, y), (nx, ny)) in enumerate(zip(outer, nrm))], outer

def ground(im, yb):
    d = ImageDraw.Draw(im)
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    dl.rectangle([P(40, yb), P(1060, 1960)], fill=o.rgb(C["graphite"], 150))
    im.alpha_composite(lay)
    rnd = random.Random(3)
    for _ in range(140):
        x, y = rnd.uniform(50, 1050), rnd.uniform(yb + 14, 1900); r = rnd.uniform(1.5, 3.5)
        d.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=o.rgb(C["line"]))
    d.line([P(40, yb), P(1060, yb)], fill=o.rgb(C["slate"]), width=int(3 * o.S))

def puddles(im, yb):
    d = ImageDraw.Draw(im)
    for cx, rx, ry in ((240, 74, 10), (905, 96, 11), (1010, 40, 6)):
        d.ellipse([P(cx - rx, yb + 14 - ry), P(cx + rx, yb + 14 + ry)], fill=o.rgb(C["water"], 150))
        d.arc([P(cx - rx * 0.7, yb + 14 - ry * 0.6), P(cx + rx * 0.5, yb + 14 + ry * 0.4)], 200, 330,
              fill=o.rgb(C["ice"], 200), width=int(2 * o.S))

def boulder_front(im, yb, broken=False, ticks=True):
    """Block von der Seite: neutrale Oberflaeche, duenne helle Kruste als Rand, Kreide-Ticks auf dem Sloper."""
    outer = surface(yb)
    poly = outer + [(CX + HA, yb), (CX - HA, yb)]
    mask = Image.new("L", im.size, 0); ImageDraw.Draw(mask).polygon([P(x, y) for x, y in poly], fill=255)
    body = Image.new("RGBA", im.size, o.rgb(C["graphite"])); body.putalpha(mask); im.alpha_composite(body)
    yy, xx = np.mgrid[0:im.size[1], 0:im.size[0]].astype(np.float32) / o.S          # Licht von oben links
    shade = np.clip((xx - (CX - HA)) / (2 * HA), 0, 1) * 0.35 + np.clip((yy - (yb - HB)) / HB, 0, 1) * 0.35
    sh = Image.new("RGBA", im.size, o.rgb(C["obsidian"]))
    sh.putalpha(Image.fromarray((np.asarray(mask, np.float32) * shade).astype(np.uint8))); im.alpha_composite(sh)
    rnd = random.Random(5); d = ImageDraw.Draw(im)
    for _ in range(900):
        x = rnd.uniform(XL + 10, XR - 10); y = rnd.uniform(yb - HB, yb - 4)
        if y < top_y(x, yb) + 18:
            continue
        r = rnd.uniform(1.2, 2.8); d.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=o.rgb(rnd.choice([C["line"], "#353E46"])))
    rim = offset(outer, 9)
    d.polygon([P(*p) for p in outer + rim[::-1]], fill=o.rgb(CRUST, 215))
    d.line([P(*p) for p in rim], fill=o.rgb(CRUST_IN, 160), width=int(1.6 * o.S))
    d.line([P(*p) for p in outer], fill=o.rgb(C["magnesia"]), width=int(3 * o.S), joint="curve")
    if broken:
        _scar(im, yb, front=True)
    if ticks:
        o.chalk_ticks(im, 640, top_y(640, yb) + 52, angle_deg=-30, seed=2)

def _scar(im, yb, front):
    """Bruchstelle: Schulter fehlt, frische Bruchflaeche ohne Kruste."""
    inner, outer = crack_curve(yb)
    d = ImageDraw.Draw(im)
    cut = outer + inner[::-1]
    cut_out = [(x + 2.5 * (x - CX) / HA, y - 3) for x, y in outer] + inner[::-1]
    d.polygon([P(*p) for p in cut_out], fill=o.rgb(C["obsidian"]))
    face = offset(inner, 13 if front else 8)
    d.polygon([P(*p) for p in inner + face[::-1]], fill=o.rgb(SCAR, 230 if front else 190))
    d.line([P(*p) for p in inner], fill=o.rgb(SCAR), width=int(4 * o.S), joint="curve")
    return cut

def boulder_section(im, yb, broken=False):
    """Querschnitt: Sand (Sandstein-Signatur), dicke Kruste, Fusslinie."""
    outer = surface(yb)
    poly = outer + [(CX + HA, yb), (CX - HA, yb)]
    o.rock_body(im, poly, fill=C["graphite"], pattern="sandstone", pat_color="#39424A", seed=4)
    rim = offset(outer, 16)
    d = ImageDraw.Draw(im)
    d.polygon([P(*p) for p in outer + rim[::-1]], fill=o.rgb(CRUST))
    rnd = random.Random(6)
    for (x, y), (x2, y2) in zip(outer[::3], rim[::3]):               # feine Kornstruktur in der Kruste
        if rnd.random() < 0.6:
            d.line([P(x, y), P(x2, y2)], fill=o.rgb(CRUST_IN, 120), width=int(1.2 * o.S))
    d.line([P(*p) for p in rim], fill=o.rgb(CRUST_IN), width=int(2 * o.S))
    d.line([P(*p) for p in outer], fill=o.rgb(C["magnesia"]), width=int(3 * o.S), joint="curve")
    if broken:
        _scar(im, yb, front=False)


class Reel(rk.ReelBase):
    DUR = DUR

    def __init__(self):
        super().__init__()
        self.rail = rk.Rail(3)
        self.end = rk.EndSting()
        self.stamp = m.text_sprite("MYTH OR ROCK", X0, 300, "stencil", 40, C["slate"], tracking=0.12)
        # Szene 1: Hook (Frame 0 = Cover)
        def bg1(im):
            o.contour_field(im, 820, 1700, n=9, r0=140, step=64, alpha=90)
            ground(im, YB_MAIN); puddles(im, YB_MAIN); boulder_front(im, YB_MAIN); o.route_rail(im, 0, 3)
        self.bg1 = m.background(bg1)
        self.hook, _ = m.lines_sprite(["LOOKS DRY.", "SAFE TO", "CLIMB?"], 352)
        # Szene 2: Mitmach-Pause
        def bg2(im):
            ground(im, YB_MAIN); puddles(im, YB_MAIN); boulder_front(im, YB_MAIN)
            im.alpha_composite(Image.new("RGBA", im.size, o.rgb(C["obsidian"], 170))); o.route_rail(im, 1, 3)
        self.bg2 = m.background(bg2)
        self.claim, yc = m.lines_sprite(["LOOKS DRY.", "SAFE TO CLIMB?"], 352, role="display_xb", size=104)
        self.chip_t = m.sprite(lambda im: o.hold_label(im, X0, yc + 50, "TRUE", C["magnesia"], size=58, role="stencil", pad=(26, 12)))
        wt = o.text_width("TRUE", "stencil", 58) + 2 * 26
        self.chip_f = m.sprite(lambda im: o.hold_label(im, X0 + wt + 40, yc + 50, "FALSE", C["magnesia"], size=58, role="stencil", pad=(26, 12)))
        self.pause = m.text_sprite("Pause. Your guess?", X0, yc + 180, "text_b", 54, C["magnesia"])
        # Szene 3: Querschnitt -- Regen, Einsickern, Abtrocknen
        def bg3(im):
            ground(im, YB_MAIN); boulder_section(im, YB_MAIN); o.route_rail(im, 2, 3)
        self.bg3 = m.background(bg3)
        outer = surface(YB_MAIN); rim = offset(outer, 16)
        self.crust_wet = m.sprite(lambda im: ImageDraw.Draw(im).polygon([P(*p) for p in outer + rim[::-1]], fill=o.rgb(C["water"])))
        self.text3a, ya = m.lines_sprite(["DRY CRUST."], 352, role="display_xb", size=118)
        self.text3b, _ = m.lines_sprite(["WET SAND BELOW."], ya, role="display_xb", size=118)
        self.lab_crust = m.text_sprite("CRUST", 740, 830, "mono", 30, C["magnesia"], tracking=0.1)
        self.lab_sand = m.text_sprite("SAND", 330, 1060, "mono", 30, C["magnesia"], tracking=0.1)
        rnd = random.Random(11); self.water = []
        while len(self.water) < 420:
            x = rnd.uniform(XL + 26, XR - 26); ty = top_y(x, YB_MAIN)
            dep = rnd.uniform(22, 260); y = ty + dep
            if y > YB_MAIN - 14 or not XL + 26 < x < XR - 26:
                continue
            self.water.append((x, y, rnd.uniform(2.4, 4.6), T_SEEP + dep / 260 * 1.05 + rnd.uniform(0, 0.25)))
        self.drop = m.sprite(lambda im: o.droplet(im, 540, 960, size=34))
        self.rain_x = [250, 370, 480, 600, 710, 820, 925]
        # Szene 4: Bruch
        def bg4(im):
            ground(im, YB_MAIN); boulder_section(im, YB_MAIN); o.route_rail(im, 3, 3)
        def bg4b(im):
            ground(im, YB_MAIN); boulder_section(im, YB_MAIN, broken=True); o.route_rail(im, 3, 3)
        base4 = m.background(bg4); broken4 = m.background(bg4b)
        dr = ImageDraw.Draw(base4); dr2 = ImageDraw.Draw(broken4)       # nasser Sand bleibt sichtbar
        inner, outer_f = crack_curve(YB_MAIN)
        self.flake_poly = outer_f + inner[::-1]
        mk = rk.mask_from(self.flake_poly)
        for x, y, r, _ in self.water:
            for d_ in (dr, dr2):
                d_.ellipse([x - r, y - r, x + r, y + r], fill=o.rgb(C["water"], 200))
        broken4.paste(m.background(bg4b).crop((0, 0, W, H)), (0, 0), mk)  # Bruchstelle ohne Wasserpunkte
        self.bg4, self.bg4b = base4, broken4
        bb = mk.getbbox()
        fl = base4.copy(); fl.putalpha(mk); fl = fl.crop(bb)
        self.flake = (fl, bb)
        self.text4, y4 = m.lines_sprite(["WET SANDSTONE", "BREAKS EASIER."], 352, role="display_xb", size=118)
        self.text4b, _ = m.lines_sprite(["IT NEVER GROWS BACK."], y4 + 28, role="display_xb", size=84, fill=C["slate"])
        sx = (F0 + F1) / 2; sy = top_y(sx, YB_MAIN)
        self.pull = (sx - 20, sy - 70, sx + 70, sy + 30)
        # Szene 5: Urteil
        self.verdict = m.text_sprite("VERDICT", X0, 330, "stencil", 64, C["slate"], tracking=0.1)
        self.false_, y5 = m.lines_sprite(["FALSE."], 400, size=260)
        sw = o.text_width("WAIT A DAY", "display", 150)
        y5 += 30
        self.swipe = m.sprite(lambda im: o.chalk_swipe(im, X0 - 8, y5 + 18, X0 + sw + 14, y5 + 168, seed=9))
        self.wait = m.text_sprite("WAIT A DAY", X0, y5 + 8, "display", 150, C["obsidian"])
        self.ortwo = m.text_sprite("OR TWO.", X0, y5 + 184, "display", 150, C["magnesia"])
        self.swipe_box = (X0 - 8, y5 + 18, X0 + sw + 14, y5 + 168)
        def bg5(im):
            ground(im, YB_PAY); puddles(im, YB_PAY); boulder_front(im, YB_PAY, broken=True); o.route_rail(im, 3, 3, logo_on=True)
        self.bg5 = m.background(bg5)

    # -------------------------------------------------------------- Frames
    def frame(self, t):
        if t < T_S2:                                               # Szene 1: Hook
            f = m.zoomed(self.bg1, 1 + 0.03 * seilzug(seg(t, 0, T_W1)), 640, 1000)
            put(f, self.stamp); put(f, self.hook)
            if t >= T_W1:
                put(f, rk.wave(seg(t, T_W1, 0.5), cx=640, cy=1000))
            return f, 31
        if t < T_S3:                                               # Szene 2: Pause
            f = self.bg2.copy()
            put(f, self.stamp)
            u = seilzug(seg(t, T_S2 + 0.03, 0.3)); put(f, self.claim, dx=lerp(-40, 0, u), op=u)
            for spr, t0 in ((self.chip_t, T_CHIPS[0]), (self.chip_f, T_CHIPS[1])):
                u = seg(t, t0, 0.3); put(f, spr, op=min(1, u * 1.8), scale=lerp(0.6, 1.0, griff(u)) if u < 1 else 1.0)
            u = seilzug(seg(t, T_PAUSE, 0.35)); put(f, self.pause, dx=lerp(-30, 0, u), op=u)
            self.rail.pop(f, t, 0, T_S2)
            if t < T_W1 + 0.5:
                put(f, rk.wave(seg(t, T_W1, 0.5), cx=640, cy=1000))
            if t >= T_W2:
                put(f, rk.wave(seg(t, T_W2, 0.45), cy=500))
            return f, 32
        if t < T_S4:                                               # Szene 3: Regen, Einsickern, Abtrocknen
            f = self.bg3.copy()
            wet = seg(t, T_RAIN[0] + FALL - 0.05, 0.4) * (1 - seg(t, T_DRY, 0.75))
            put(f, self.crust_wet, op=0.62 * wet)
            dr = ImageDraw.Draw(f)
            for x, y, r, ta in self.water:
                v = seg(t, ta, 0.25)
                if v > 0:
                    rr = r * (0.4 + 0.6 * seilzug(v)); dr.ellipse([x - rr, y - rr, x + rr, y + rr], fill=o.rgb(C["water"], int(200 * v)))
            for k, (x, t0) in enumerate(zip(self.rain_x, T_RAIN)):
                yl = top_y(x, YB_MAIN)
                u = seg(t, t0, FALL)
                if 0 < u < 1:
                    y = lerp(760 + 30 * (k % 3), yl - 16, sturz(u)); put(f, self.drop, dx=x - 540, dy=y - 960, op=min(1, u * 5))
                elif u >= 1:
                    v = seg(t, t0 + FALL, 0.5)
                    if v < 1:
                        rr = 10 + 30 * seilzug(v); a = int(220 * (1 - v))
                        dr.ellipse([x - rr, yl - rr * 0.3, x + rr, yl + rr * 0.3], outline=o.rgb(C["water"], a), width=3)
            v = seg(t, T_DRY, 0.8)                                 # Verdunstung an der Oberflaeche
            if 0 < v < 1:
                for k, x in enumerate(range(240, 960, 90)):
                    yl = top_y(x, YB_MAIN) - 10 - 70 * seilzug(v) - (k % 2) * 14
                    pts = [(x + 6 * math.sin(yy / 9 + k), yy) for yy in range(int(yl), int(yl) - 34, -3)]
                    dr.line(pts, fill=o.rgb(C["slate"], int(170 * math.sin(math.pi * v))), width=3)
            u = seilzug(seg(t, T_DRY + 0.03, 0.35)); put(f, self.text3a, dx=lerp(-40, 0, u), op=u)
            u = seilzug(seg(t, T_DRY + 0.33, 0.35)); put(f, self.text3b, dx=lerp(-40, 0, u), op=u)
            for spr, t0 in ((self.lab_crust, T_LAB[0]), (self.lab_sand, T_LAB[1])):
                u = seg(t, t0, 0.3); put(f, spr, op=min(1, u * 1.8), scale=lerp(0.7, 1.0, griff(u)) if u < 1 else 1.0)
            self.rail.pop(f, t, 1, T_S3)
            if t < T_W2 + 0.45:
                put(f, rk.wave(seg(t, T_W2, 0.45), cy=500))
            if t >= T_CR:
                put(f, rk.wave(seg(t, T_CR, 0.45), cy=500))
            return f, 33
        if t < T_S5:                                               # Szene 4: Bruch
            fl, bb = self.flake
            if t < T_DROP:
                f = self.bg4.copy()
                jig = 2.0 * math.sin(t * 70) * seg(t, T_PULL + 0.3, 0.1) if t >= T_PULL + 0.3 else 0
                if jig:
                    f.paste(self.bg4b.crop(bb), (bb[0], bb[1]))
                    f.alpha_composite(fl, (int(bb[0] + jig), bb[1]))
                if t >= T_BREAK:                                    # Riss laeuft durch den nassen Sand
                    inner, _ = crack_curve(YB_MAIN); n = max(2, int(len(inner) * sturz(seg(t, T_BREAK, 0.22))))
                    ImageDraw.Draw(f).line(inner[:n], fill=o.rgb(C["magnesia"]), width=4)
            else:
                f = self.bg4b.copy()
                u = seg(t, T_DROP, 0.75)
                if u < 1:
                    rot = fl.rotate(-38 * sturz(u), resample=Image.BICUBIC, expand=True)
                    cx = (bb[0] + bb[2]) / 2 + 110 * u; cy = (bb[1] + bb[3]) / 2 + 900 * u * u
                    rot.putalpha(rot.getchannel("A").point(lambda a, k=1 - 0.3 * u: int(a * k)))
                    m.composite(f, rot, int(cx - rot.width / 2), int(cy - rot.height / 2))
            u = seilzug(seg(t, T_PULL, 0.3))                       # Zug am Sloper
            if 0 < u and t < T_DROP + 0.3:
                x0, y0, x1, y1 = self.pull
                xe, ye = lerp(x0, x1, u), lerp(y0, y1, u)
                a = 1 - seg(t, T_DROP, 0.3)
                def draw(d, X, Y, xe=xe, ye=ye, a=a):
                    d.line([(X(x0), Y(y0)), (X(xe), Y(ye))], fill=o.rgb(C["magnesia"], int(255 * a)), width=int(6 * o.S))
                    ang = math.atan2(ye - y0, xe - x0)
                    for s in (-1, 1):
                        d.line([(X(xe), Y(ye)), (X(xe - 26 * math.cos(ang + s * 0.5)), Y(ye - 26 * math.sin(ang + s * 0.5)))],
                               fill=o.rgb(C["magnesia"], int(255 * a)), width=int(6 * o.S))
                put(f, rk.region(x0 - 40, y0 - 40, x1 + 40, y1 + 40, draw))
            u = seilzug(seg(t, T_S4 + 0.03, 0.35)); put(f, self.text4, dx=lerp(-40, 0, u), op=u)
            u = seilzug(seg(t, T_NEVER, 0.35)); put(f, self.text4b, dx=lerp(-30, 0, u), op=u)
            self.rail.pop(f, t, 2, T_S4)
            if t < T_CR + 0.45:
                put(f, rk.wave(seg(t, T_CR, 0.45), cy=500))
            return f, 34
        if t < T_END:                                              # Szene 5: Urteil
            f = self.bg5.copy()
            put(f, self.verdict, op=seg(t, T_S5, 0.15))
            u = seg(t, T_S5, 0.22); put(f, self.false_, op=min(1, u * 2), scale=lerp(1.18, 1.0, seilzug(u)), anchor=(X0, 400))
            self.rail.logo_pop(f, t, T_S5)
            put(f, m.reveal(self.swipe, seilzug(seg(t, T_SWIPE, 0.2))))
            put(f, self.wait, op=seg(t, T_SWIPE + 0.08, 0.12))
            u = seilzug(seg(t, T_OR, 0.3)); put(f, self.ortwo, dx=lerp(-40, 0, u), op=u)
            rk.dust(f, t, T_SWIPE + 0.1, self.swipe_box)
            return f, 35
        return self.end.frame(t, T_END), 36


# ------------------------------------------------------------------ Ton
def sound_events(b):
    b.kenney("interface-sounds", "tick_001.ogg", 0.35, -8.0, "kreide-tick")
    b.kenney("interface-sounds", "maximize_001.ogg", T_W1, -7.0, "uebergang")
    b.kenney("impact-sounds", "impactMetal_light_000.ogg", T_S2, -7.0, "bohrhaken")
    b.kenney("interface-sounds", "tick_002.ogg", T_CHIPS[0], -6.0, "kreide-tick")
    b.kenney("interface-sounds", "tick_004.ogg", T_CHIPS[1], -6.0, "kreide-tick")
    b.kenney("interface-sounds", "question_001.ogg", T_PAUSE, -7.0, "frage")
    b.kenney("interface-sounds", "maximize_001.ogg", T_W2, -7.0, "uebergang")
    b.kenney("impact-sounds", "impactMetal_light_001.ogg", T_S3, -7.0, "bohrhaken")
    for k, t0 in enumerate(T_RAIN):
        b.kenney("interface-sounds", ("drop_001.ogg", "drop_004.ogg")[k % 2], t0 + FALL, -5.0 - (k % 3), "tropfen")
    b.synth("fizz", T_SEEP, -18.0, "einsickern", dur=1.2, seed=5)
    b.kenney("interface-sounds", "tick_001.ogg", T_LAB[0], -8.0, "kreide-tick")
    b.kenney("interface-sounds", "tick_002.ogg", T_LAB[1], -8.0, "kreide-tick")
    b.synth("whoosh", T_DRY, -15.0, "abtrocknen", dur=0.8, seed=7)
    b.kenney("interface-sounds", "maximize_001.ogg", T_CR, -7.0, "uebergang")
    b.kenney("impact-sounds", "impactMetal_light_002.ogg", T_S4, -7.0, "bohrhaken")
    b.kenney("interface-sounds", "scratch_001.ogg", T_PULL, -12.0, "zug")
    b.kenney("impact-sounds", "impactMining_001.ogg", T_BREAK, -4.0, "bruch")
    b.synth("whoosh", T_DROP, -14.0, "fallen", dur=0.5, seed=9)
    b.kenney("impact-sounds", "impactMining_002.ogg", T_DROP + 0.55, -9.0, "aufschlag")
    b.synth("riser", T_RISE, -9.0, "steigerung", dur=0.85)
    b.kenney("impact-sounds", "impactPunch_heavy_000.ogg", T_S5, -2.0, "treffer")
    b.kenney("impact-sounds", "impactMetal_light_000.ogg", T_S5 + 0.02, -9.0, "bohrhaken")
    b.kenney("interface-sounds", "scratch_001.ogg", T_SWIPE, -5.0, "kreide-wisch")
    b.kenney("interface-sounds", "scratch_002.ogg", T_SWIPE + 0.08, -7.0, "kreide-wisch")
    b.kenney("interface-sounds", "tick_004.ogg", T_OR, -8.0, "kreide-tick")
    b.sound_logo(T_END)
    b.pads([(0.0, 9.45, -9.0), (9.60, T_END, -11.0)])


if __name__ == "__main__":
    rk.run(Reel, sound_events, META)
