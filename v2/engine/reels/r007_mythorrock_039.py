#!/usr/bin/env python3
"""Reel 007 -- MYTH OR ROCK #02: "Climbers say: Frankenjura is limestone." (Faktenbasis: Post #039, Frankenjura ist
Dolomit), Ablauf "quiz".

Fassung 1 vom 25.10.2026 nach PRODUKTION.md (Stand 16.10.2026), Vorlage r003 Fassung 6 (Musik, Tempo, Abspann, Lesezeit),
Quiz-Chips wie r004. Format MYTH OR ROCK: Behauptung -> Chips und Rate-Pause -> Beleg in zwei Zuegen -> Urteil IT DEPENDS.
Hook 1 0-1,45 s: GEOCRIMPS + CLIMBING ab Frame 0, ein Kletterer greift ein Loch in einem Felsturm (Kreidewolke),
"x GEOLOGY" schlaegt ein und nur die gebankte Wand links klappt in ihre Kalk-Signatur auf; der loechrige Turm bleibt
ohne Signatur (verraet den Dolomit nicht).
Hook 2 ab 1,8 s: Formatlabel MYTH OR ROCK, Kontextzeile "CLIMBERS SAY:" (Kalkfarbe) ueber "FRANKENJURA IS LIMESTONE.";
ab 3,8 s drei Griff-Chips TRUE / FALSE / IT DEPENDS, ab 4,8 s "YOUR GUESS?" mit Countdown aus Toenen, Chips pulsen.
Zug 1 (Scan): eine senkrechte Scanlinie faehrt von links nach rechts; die Wand bekommt die Kalk-Signatur (Label
LIMESTONE), der Turm die Dolomit-Signatur in warmer Farbe: "THIS TOWER: DOLOMITE." Der Kletterer greift hoeher.
Zug 2 (Kristallgitter): Zoom ins Loch, schematisches Gitter (nicht massstaeblich): alle Plaetze Ca, dann wird jede
zweite Lage Mg: "MAGNESIUM REPLACES HALF THE CALCIUM."
Payoff: Zoom zurueck, Chip IT DEPENDS leuchtet, "LIMESTONE AND DOLOMITE." gross; der Kletterer zieht ans naechste Loch.
Fazit: beide Gesteine leuchten kurz auf: "YOU'RE CLIMBING BOTH." Abspann mit LIKE & FOLLOW.
Fakten (v2/faktenbasis/039/sources.md, Nachtrag 25.10.2026): Die Fraenkische Alb praegen Felsbildungen aus Riffdolomiten
und Massenkalken (LfU 2010, Malm); Felsstotzen aus Frankendolomit, Magnesium ersetzte teilweise das Calcium (LfU,
Geotop Felsburg Tuechersfeld); Dolomit CaMg(CO3)2 (geology.com), also halb so viel Ca wie Calcit CaCO3; Kalkfelsen
gebankt und geklueftet, loechrige Dolomittuerme (Hofbauer et al. 2005); Kletterer nennen den Frankenjura Kalk (UKC).
Bewusst NICHT: "obere Lagen Dolomit" und "im Osten Dolomit" (die zitierte UKC-Seite traegt das am 25.10.2026 nicht
mehr), Loeslichkeit von Dolomit (Quellen widersprechen sich), Dolomit als Grund der Tuerme.
Bildmittel (Abwechslungsregel): Uebergang Scanlinie und Zoom (r006: Lupenkreis-Sprung, Kamerafahrt) | Enthuellung Scan
und Gitter-Tausch (r006: Massstabssprung, Zeitraffer) | Payoff Chip leuchtet, Antwort gross, Kletterer zieht (r006: kein
Chip) | Musik B-Dur (B flat), 82 BPM (r006: F-Dur, 86 BPM).
Aufruf:  python3 r007_mythorrock_039.py --out ../../../reels --qc <Ordner>   (--stills 0,4.8 fuer Einzelbilder, --reach)
"""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import outcrop as o
import motion as m
import reelkit as rk
import kletter as kl
from outcrop import C, P
from motion import X0, W, H, seg, seilzug, sturz, griff, lerp, put

# ------------------------------------------------------------------ Zeitplan (ruhiges Tempo, Lesezeit)
EIN = 0.5
T_GRAB, T_GEO, T_OUT = 0.40, 0.72, 1.45                       # Hook 1
T_Q = 1.80                                                    # Hook 2: Label, Kontextzeile, Behauptung
T_CHIPS = T_Q + 2.0                                           # Chips je 0,3 s versetzt
T_GUESS = T_CHIPS + 1.0                                       # YOUR GUESS? + Countdown
T_HOOK = T_GUESS + 2.0                                        # Ende der Rate-Pause
T_S2 = T_HOOK + 0.5                                           # Zug 1: Scan
T_SCAN = (T_S2 + 0.1, 2.0)                                    # Scanlinie (senkrecht, faehrt nach rechts): Beginn, Dauer
T_LAB = T_S2 + 0.75                                           # Label LIMESTONE an der Wand (Scan hat sie ueberstrichen)
T_TXT1 = T_S2 + 1.8                                           # THIS TOWER: DOLOMITE.
T_MOVE1 = T_TXT1 + 1.2                                        # Kletterer greift hoeher (Bewegung, keine Info)
T_Z0 = T_TXT1 + 2.6                                           # Zoom ins Loch (0,9 s)
T_Z1 = T_Z0 + 0.9
T_S3 = T_Z0 + 0.35                                            # Zug 2 (Bohrhaken)
T_CA = T_Z1 + 0.3                                             # Legende Ca
T_SWAP = T_Z1 + 0.8                                           # jede zweite Lage wird Mg (1,0 s)
T_MG = T_SWAP + 0.5                                           # Legende Mg
T_TXT2 = T_SWAP + 1.3                                         # MAGNESIUM REPLACES HALF THE CALCIUM.
T_S4 = T_TXT2 + 3.2                                           # Payoff
T_RISE = T_S4 - 1.0                                           # Akkord schwillt an
T_ZB = T_S4 - 0.95                                            # Zoom zurueck (0,8 s)
T_MOVE2 = T_S4 + 1.3                                          # Kletterer zieht ans naechste Loch
T_S5 = T_S4 + 3.1                                             # Fazit
T_END = T_S5 + 3.7                                            # Abspann
DUR = T_END + rk.Outro.DUR

# ------------------------------------------------------------------ Szene: Felsturm, unten gebankter Kalk, oben Dolomit
LIME, LIME_IN = "#D9D3C4", "#8F897C"                          # Kalk wie r004
DOLO = "#CDB48A"                                              # Dolomit: warm (verwittert gelblich-grau), nur hier
TOWER_FILL = "#191D22"
Y_G = 1580                                                    # Boden
_TW = [(330, Y_G), (338, 1470), (352, 1380), (366, 1270), (384, 1170), (410, 1100), (452, 1052), (520, 1022),
       (610, 1008), (700, 1012), (780, 1034), (836, 1076), (866, 1140), (884, 1240), (900, 1360), (914, 1470), (926, Y_G)]
TOWER = [(round(660 + (x - 628) * 0.74), y) for x, y in _TW]   # schlank: ein Turm, kein Block
TOP_Y = 1008
WALL = [(-10, 1172), (60, 1150), (140, 1178), (220, 1146), (300, 1168), (360, 1160), (404, 1196), (410, Y_G), (-10, Y_G)]
WALL_BEDS = list(range(1222, Y_G, 48))                          # Kalkwand: gebankt und geklueftet (Hofbauer et al. 2005)


def tower_x(y):
    """Linke und rechte Turmkante in Hoehe y."""
    half = len(TOWER) // 2
    left = TOWER[:half + 1][::-1]; right = TOWER[half:]
    xl = float(np.interp(y, [p[1] for p in left], [p[0] for p in left]))
    xr = float(np.interp(y, [p[1] for p in right], [p[0] for p in right]))
    return xl, xr


P_L, P_R = (598, 1236), (700, 1218)                           # Haende: zwei Loecher (rechts = Griff des Reels)
P_R2, P_L2 = (738, 1150), (612, 1124)                         # hoehere Loecher (Zug 1, Payoff)
F_L, F_R = (588, 1468), (690, 1452)                           # Tritte
F_L2 = (600, 1404)
POCKETS = [P_L, P_R, P_R2, P_L2, (552, 1100), (790, 1268), (520, 1300), (680, 1060), (566, 1176), (500, 1440),
           (800, 1350), (760, 1520), (540, 1530), (830, 1180)]
LEDGES = [F_L, F_R, F_L2, (500, 1520), (790, 1410), (512, 1390)]
ZC, ZOOM = (720, 1150), 1.32

BACK = dict(sw=22, hw=13, eb=(-1, 1), kb=(1, -1))
POSE_START = dict(BACK, hip=(650, 1412), lean=-2, lh=P_L, rh=(690, 1306), lf=F_L, rf=(700, 1500))
POSE_HANG = dict(BACK, hip=(648, 1386), lean=3, lh=P_L, rh=P_R, lf=F_L, rf=F_R)
POSE_SWING = dict(POSE_HANG, hip=(654, 1378), lean=6)
POSE_HIGH = dict(BACK, hip=(662, 1352), lean=5, lh=P_L, rh=P_R2, lf=F_L, rf=F_R)
POSE_TOP = dict(BACK, hip=(664, 1318), lean=0, lh=P_L2, rh=P_R2, lf=F_L2, rf=F_R)

# Tonart B-Dur (B flat), 82 BPM; MIDI, Bass eine Oktave tiefer
GM9, EBMAJ7, CM7, F_, BB, FSUS4 = ([55, 58, 62, 65, 69], [51, 55, 58, 62], [55, 58, 60, 63], [53, 57, 60, 65],
                                   [58, 62, 65, 70], [53, 58, 60, 65])
PENTA = [70, 72, 74, 77, 79, 82, 84]                          # B-Dur-Pentatonik ab B4


def check_reach():
    cl = kl.Climber(scale=1.0, width=18.0, torso_w=36.0); out = {}
    for name, p in (("start", POSE_START), ("hang", POSE_HANG), ("swing", POSE_SWING), ("high", POSE_HIGH), ("top", POSE_TOP)):
        j = cl.joints(p)
        out[name] = round(max(math.dist(j[k], p[k]) for k in ("lh", "rh", "lf", "rf")), 2)
    return out


def climber_pose(t):
    if t < T_GRAB:
        return kl.lerp_pose(POSE_START, POSE_SWING, seilzug(seg(t, 0.0, T_GRAB)))
    if t < T_MOVE1:
        u = seg(t, T_GRAB, 0.3)
        p = kl.lerp_pose(POSE_SWING, POSE_HANG, 0.5 - 0.5 * math.cos(math.pi * u))
    elif t < T_MOVE2:
        u = seg(t, T_MOVE1, 0.8)
        p = kl.lerp_pose(POSE_HANG, POSE_HIGH, 0.5 - 0.5 * math.cos(math.pi * u))
    else:
        u = seg(t, T_MOVE2, 0.9)
        p = kl.lerp_pose(POSE_HIGH, POSE_TOP, 0.5 - 0.5 * math.cos(math.pi * u))
    if t > T_GRAB + 0.3:                                       # atmet, pendelt leicht
        w = math.sin(2 * math.pi * (t - T_GRAB - 0.3) / 2.6)
        p = dict(p, hip=(p["hip"][0] + 3 * w, p["hip"][1] + 1.5 * abs(w)), lean=p["lean"] + 1.2 * w)
    return p


def _mask(poly, cond=None):
    """2x-Maske des Polygons; cond(X, Y) (Bildkoordinaten, numpy) schneidet zusaetzlich."""
    mk = Image.new("L", (W * o.S, H * o.S), 0)
    ImageDraw.Draw(mk).polygon([P(x, y) for x, y in poly], fill=255)
    a = np.asarray(mk, np.float32)
    if cond is not None:
        yy, xx = np.mgrid[0:H * o.S, 0:W * o.S].astype(np.float32) / o.S
        a = a * cond(xx, yy)
    return a




def _pattern_sprite(a_mask, kind, color, alpha, tint=0, seed=6):
    pat = o._pattern_layer((W * o.S, H * o.S), kind, color, seed=seed)
    a = np.maximum(np.asarray(pat.getchannel("A"), np.float32) * (alpha / 255), tint) * (a_mask / 255)
    lay = Image.new("RGBA", (W * o.S, H * o.S), o.rgb(color))
    lay.putalpha(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)))
    small = lay.resize((W, H), Image.LANCZOS)
    bb = small.getbbox()
    return m.Sprite(small.crop(bb), bb[0], bb[1])


def crop_left(spr, x):
    """Teil des Sprites links der Bildspalte x (Scan deckt von links auf)."""
    w = int(min(spr.w, x - spr.x))
    if w <= 0:
        return None
    return m.Sprite(spr.img.crop((0, 0, w, spr.h)), spr.x, spr.y)


def scan_x(t):
    u = seg(t, *T_SCAN)
    return lerp(-30, 940, 0.5 - 0.5 * math.cos(math.pi * u))


class Reel(rk.ReelBase):
    DUR = DUR

    def __init__(self):
        super().__init__()
        self.rail = rk.Rail(2)
        self.outro = rk.Outro()
        self.rails = [rk.rail_sprite(0, 2), rk.rail_sprite(1, 2), rk.rail_sprite(2, 2), rk.rail_sprite(2, 2, logo_on=True)]
        self.hook1 = rk.Hook1(t_grab=T_GRAB, t_geo=T_GEO, t_out=T_OUT)
        self.climber = kl.Climber(scale=1.0, width=18.0, torso_w=36.0)
        # ---- Texte
        self.label = m.text_sprite("MYTH OR ROCK", X0, rk.FORMAT_Y, "stencil", 40, C["slate"], tracking=0.12)
        self.hook_kick = m.text_sprite("CLIMBERS SAY:", X0, rk.HOOK_Y, "display", 96, LIME)
        self.hook, y_q = m.lines_sprite(["FRANKENJURA", "IS LIMESTONE."], rk.HOOK_Y + 112, size=136)
        self.y_chips = int(y_q) + 26
        self.chips, self.chips_hell, x = [], [], X0
        for lab in ("TRUE", "FALSE", "IT DEPENDS"):
            wch = o.text_width(lab, "stencil", 52) + 52
            self.chips.append(self._chip(x, self.y_chips, lab, C["magnesia"]))
            self.chips_hell.append(self._chip(x, self.y_chips, lab, C["bio"]))
            x += wch + 24
        self.chips_matt = [m.Sprite(c.img, c.x, c.y) for c in self.chips]
        self.guess = m.text_sprite("YOUR GUESS?", X0, self.y_chips + 104, "text_b", 54, C["magnesia"])
        self.text1, _ = m.lines_sprite(["THIS TOWER:", "DOLOMITE."], 352, role="display_xb", size=118)
        self.lab = m.text_sprite("LIMESTONE", 96, 1250, "mono", 30, C["magnesia"], tracking=0.1)
        self.text2, _ = m.lines_sprite(["MAGNESIUM REPLACES", "HALF THE CALCIUM."], 352, role="display_xb", size=118)
        self.answer, _ = m.lines_sprite(["LIMESTONE AND", "DOLOMITE."], 352, size=170)
        self.fazit, _ = m.lines_sprite(["YOU'RE CLIMBING", "BOTH."], 352, size=150)
        # ---- Hintergrund und Turm
        self.bg = m.background(self._draw_bg)
        self.tower = m.sprite(self._draw_tower)
        self.lime_pat = _pattern_sprite(_mask(WALL), "limestone", LIME, 85, tint=22, seed=6)
        self.dolo_pat = _pattern_sprite(_mask(TOWER), "dolomite", DOLO, 95, tint=38, seed=7)
        beds = [[(x, y0 + 4 * math.sin(x / 90 + k)) for x in range(-10, 420, 20)] for k, y0 in enumerate(WALL_BEDS)]
        self.geo = kl.GeoReveal(WALL, "limestone", P_R[0], P_R[1], pat_alpha=90, beds=beds, seed=6)   # nur die Kalkwand
        self.scanline = m.sprite(self._draw_scanline)
        # ---- Zug 2: Kristallgitter (schematisch)
        self.panel = m.sprite(self._draw_panel)
        self.lat_rows, self.lat_cols = 6, 7
        self.ca = m.sprite(lambda im: self._ion(im, 100, 100, 24, LIME))
        self.mg = m.sprite(lambda im: self._ion(im, 100, 100, 17, C["bio"]))
        self.dim = m.Sprite(Image.new("RGBA", (W, H), o.rgb(C["obsidian"], 205)), 0, 0)
        self.lat_x0, self.lat_y0, self.lat_dx, self.lat_dy = 236, 760, 101, 92
        self.co3 = m.sprite(self._draw_co3)
        ly = self.lat_y0 + self.lat_dy * self.lat_rows - 8
        self.leg_ca_dot = m.sprite(lambda im: self._ion(im, 250, ly + 24, 18, LIME))
        self.leg_ca = m.text_sprite("Ca", 284, ly + 6, "mono", 34, C["magnesia"])
        self.leg_mg_dot = m.sprite(lambda im: self._ion(im, 440, ly + 24, 13, C["bio"]))
        self.leg_mg = m.text_sprite("Mg", 470, ly + 6, "mono", 34, C["magnesia"])

    # -------------------------------------------------------------- Hilfsbilder
    @staticmethod
    def _chip(x, y, label, fill):
        spr = m.sprite(lambda im: o.hold_label(im, x, y, label, fill, size=52, role="stencil", pad=(26, 13)))
        spr.text = label
        return spr

    @staticmethod
    def _ion(im, x, y, r, col):
        d = ImageDraw.Draw(im)
        d.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=o.rgb(col))
        d.ellipse([P(x - r * 0.55, y - r * 0.6), P(x - r * 0.1, y - r * 0.2)], fill=o.rgb(C["magnesia"], 90))

    def _draw_bg(self, im):
        o.contour_field(im, 840, 1760, n=9, r0=150, step=66, alpha=80)
        d = ImageDraw.Draw(im)
        lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(lay).rectangle([P(0, Y_G), P(W, H)], fill=o.rgb(C["graphite"], 170))
        im.alpha_composite(lay)
        rnd = random.Random(3)
        for _ in range(120):
            x, y = rnd.uniform(10, 1070), rnd.uniform(Y_G + 12, 1900); r = rnd.uniform(1.5, 3.2)
            d.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=o.rgb(C["line"]))
        d.line([P(0, Y_G), P(W, Y_G)], fill=o.rgb(C["slate"]), width=int(3 * o.S))
        for x0, h in ((990, 90),):                     # Baeume am Turmfuss (Frankenjura: Wald)
            d.line([P(x0, Y_G), P(x0, Y_G - h * 0.4)], fill=o.rgb(C["line"]), width=int(6 * o.S))
            d.polygon([P(x0 - 34, Y_G - h * 0.35), P(x0, Y_G - h * 1.6), P(x0 + 34, Y_G - h * 0.35)], fill=o.rgb("#232B30"))

    def _draw_tower(self, im):
        d = ImageDraw.Draw(im)
        d.polygon([P(x, y) for x, y in WALL], fill=o.rgb(TOWER_FILL))     # Kalkwand links: Baenke und Kluefte
        for k, y0 in enumerate(WALL_BEDS):
            d.line([P(x, y0 + 4 * math.sin(x / 90 + k)) for x in range(-10, 408, 12)], fill=o.rgb(LIME_IN, 150),
                   width=int(2 * o.S))
        for xj, k0 in ((95, 0), (250, 1), (340, 0)):
            for k in range(k0, len(WALL_BEDS) - 1, 2):
                d.line([P(xj + 14 * (k % 2), WALL_BEDS[k] + 4), P(xj + 14 * (k % 2), WALL_BEDS[k + 1])],
                       fill=o.rgb(LIME_IN, 150), width=int(2 * o.S))
        d.line([P(x, y) for x, y in WALL[:7]], fill=o.rgb(LIME), width=int(4 * o.S), joint="curve")
        d.line([P(*WALL[6]), P(*WALL[7])], fill=o.rgb(LIME), width=int(4 * o.S))
        d.polygon([P(x, y) for x, y in TOWER], fill=o.rgb(TOWER_FILL))
        for x0, pts in ((540, [(540, 1060), (534, 1130), (542, 1210), (536, 1290)]),
                        (796, [(790, 1070), (798, 1150), (792, 1230)])):  # Kluefte im massigen Teil
            d.line([P(*p) for p in pts], fill=o.rgb(C["line"]), width=int(3 * o.S), joint="curve")
        for (cx, cy) in POCKETS:
            o.pocket(im, cx, cy, 15, 10)
        for (cx, cy) in LEDGES:
            d.rounded_rectangle([P(cx - 18, cy - 5), P(cx + 18, cy + 6)], radius=4 * o.S, fill=o.rgb(C["slate"], 200))
        d.line([P(x, y) for x, y in TOWER], fill=o.rgb(C["magnesia"]), width=int(4 * o.S), joint="curve")

    def _draw_scanline(self, im):
        d = ImageDraw.Draw(im)
        for k, a in ((14, 30), (8, 60), (3, 230)):
            d.line([P(540, 960), P(540, Y_G)], fill=o.rgb(C["ice"], a), width=int(k * o.S))

    def _draw_panel(self, im):
        d = ImageDraw.Draw(im)
        x0, y0 = 160, 700
        x1, y1 = 920, 700 + 92 * 6 + 110
        d.rounded_rectangle([P(x0, y0), P(x1, y1)], radius=24 * o.S, fill=o.rgb(C["obsidian"]),
                            outline=o.rgb(DOLO, 200), width=int(3 * o.S))

    def _draw_co3(self, im):
        d = ImageDraw.Draw(im)
        for r in range(self.lat_rows):
            for c in range(self.lat_cols - 1):
                cx = self.lat_x0 + self.lat_dx * (c + 0.5) + (self.lat_dx / 2 if r % 2 else 0) * 0
                cy = self.lat_y0 + self.lat_dy * r
                s = 10
                d.polygon([P(cx, cy - s), P(cx + s * 0.9, cy + s * 0.6), P(cx - s * 0.9, cy + s * 0.6)],
                          outline=o.rgb(C["slate"], 200), width=int(2 * o.S))

    # -------------------------------------------------------------- Welt
    def world(self, t):
        f = self.bg.copy()
        put(f, self.tower)
        u = seilzug(seg(t, T_GEO, 0.5))                           # Hook 1: nur der Kalk-Sockel klappt auf
        if u > 0 and t < T_OUT + 0.4:
            self.geo.put(f, u, fade=1 - seg(t, T_OUT, 0.4))
        if t >= T_SCAN[0]:                                        # Zug 1: Scan deckt von links auf, bleibt danach stehen
            x = scan_x(t)
            hell = 1 + 0.25 * math.sin(math.pi * seg(t, T_S5 + 0.4, 1.2))   # Fazit: beide Gesteine leuchten kurz auf
            put(f, crop_left(self.lime_pat, x), op=min(1.0, hell))
            put(f, crop_left(self.dolo_pat, x), op=min(1.0, hell))
            if hell > 1:
                put(f, self.lime_pat, op=hell - 1); put(f, self.dolo_pat, op=hell - 1)
            v = seg(t, *T_SCAN)
            if 0 < v < 1:
                put(f, self.scanline, dx=x - 540, op=min(1, v * 6, (1 - v) * 6))
        put(f, self.climber.sprite(climber_pose(t)))
        kl.chalk_puff(f, t, T_GRAB, P_R[0], P_R[1] - 4, seed=11)
        kl.chalk_puff(f, t, T_MOVE1 + 0.75, P_R2[0], P_R2[1] - 4, seed=12, size=0.7)
        kl.chalk_puff(f, t, T_MOVE2 + 0.85, P_L2[0], P_L2[1] - 4, seed=13, size=0.7)
        return f

    def lattice(self, f, t, op):
        if op <= 0:
            return
        put(f, self.dim, op=op)
        put(f, self.panel, op=op)
        put(f, self.co3, op=op * 0.9)
        for r in range(self.lat_rows):
            ts = T_SWAP + 0.17 * (r // 2)                          # jede zweite Lage (r = 1, 3, 5) wird Mg
            v = seg(t, ts, 0.3) if r % 2 else 0.0
            for c in range(self.lat_cols):
                x = self.lat_x0 + self.lat_dx * c
                y = self.lat_y0 + self.lat_dy * r + 2 * math.sin(2 * math.pi * (t * 0.7 + 0.13 * c + 0.29 * r))
                if v < 1:
                    put(f, self.ca, dx=x - 100, dy=y - 100, op=op * (1 - v), scale=1 - 0.3 * v)
                if v > 0:
                    put(f, self.mg, dx=x - 100, dy=y - 100, op=op * v,
                        scale=lerp(1.5, 1.0, griff(v)) if v < 1 else 1.0)
        a = seilzug(seg(t, T_CA, 0.45))
        put(f, self.leg_ca_dot, op=op * a); put(f, self.leg_ca, op=op * a)
        a = seilzug(seg(t, T_MG, 0.45))
        put(f, self.leg_mg_dot, op=op * a); put(f, self.leg_mg, op=op * a)

    # -------------------------------------------------------------- Frames
    def frame(self, t):
        if t >= T_END:
            return self.outro.frame(t, T_END), 45
        if t < T_Z0:
            z = 1 + 0.03 * (0.5 - 0.5 * math.cos(math.pi * seg(t, 0, T_Z0)))          # langsamer Push-in
        elif t < T_ZB:
            z = lerp(1.03, ZOOM, 0.5 - 0.5 * math.cos(math.pi * seg(t, T_Z0, T_Z1 - T_Z0)))
        else:
            z = lerp(ZOOM, 1.0, 0.5 - 0.5 * math.cos(math.pi * seg(t, T_ZB, 0.8)))
            z *= 1 + 0.03 * (0.5 - 0.5 * math.cos(math.pi * seg(t, T_ZB + 0.8, T_END - T_ZB - 0.8)))
        f = m.zoomed(self.world(t), z, *ZC)
        if t < T_HOOK + 0.25:                                     # Szene 1: Hook 1, Hook 2, Quiz
            put(f, self.rails[0])
            self.hook1.draw(f, t, hook_bis=T_HOOK)
            u = seilzug(seg(t, T_Q, EIN))
            fade = 1 - seg(t, T_HOOK, 0.2)
            if u > 0:
                put(f, self.label, dx=lerp(-30, 0, u), op=u * fade)
                put(f, self.hook_kick, dx=lerp(-40, 0, u), op=u * fade)
                put(f, self.hook, dx=lerp(-40, 0, u), op=u * fade)
            for k, spr in enumerate(self.chips):
                v = seg(t, T_CHIPS + 0.3 * k, 0.45)
                if v > 0:
                    sc = lerp(0.7, 1.0, griff(v)) if v < 1 else 1.0
                    if t >= T_GUESS + 0.45:                       # Rate-Pause: Chips pulsen nacheinander
                        sc = 1 + 0.05 * max(0.0, math.sin(2 * math.pi * ((t - T_GUESS - 0.45) / 1.2 - k / 3)))
                    put(f, spr, op=min(1.0, v * 2) * fade, scale=sc)
            v = seilzug(seg(t, T_GUESS, EIN))
            if v > 0:
                pul = 1 + 0.03 * math.sin(2 * math.pi * (t - T_GUESS) / 0.9) if v >= 1 else 1.0
                put(f, self.guess, dx=lerp(-30, 0, v), op=v * fade, scale=pul)
            return f, 41
        if t < T_S3:                                              # Szene 2: Zug 1, Scan
            put(f, self.rails[1]); self.rail.pop(f, t, 0, T_S2)
            put(f, self.lab, op=seilzug(seg(t, T_LAB, 0.45)) * (1 - seg(t, T_Z0, 0.25)))
            u = seilzug(seg(t, T_TXT1, EIN))
            put(f, self.text1, dx=lerp(-40, 0, u), op=u * (1 - seg(t, T_Z0, 0.25)))
            return f, 42
        if t < T_S5:                                              # Szene 3: Zug 2 (Gitter), Payoff
            put(f, self.rails[3] if t >= T_S4 else self.rails[2]); self.rail.pop(f, t, 1, T_S3)
            put(f, self.text1, op=1 - seg(t, T_Z0, 0.25))
            put(f, self.lab, op=1 - seg(t, T_Z0, 0.25))
            lat = seg(t, T_Z1, 0.5) * (1 - seg(t, T_ZB, 0.35))
            self.lattice(f, t, lat)
            u = seilzug(seg(t, T_TXT2, EIN))
            put(f, self.text2, dx=lerp(-40, 0, u), op=u * (1 - seg(t, T_S4 - 0.2, 0.2)))
            v = seg(t, T_S4, 0.3)
            if v > 0:
                self.rail.logo_pop(f, t, T_S4)
                out = 1 - seg(t, T_S5 - 0.2, 0.2)
                put(f, self.answer, op=min(1, v * 2) * out, scale=lerp(1.18, 1.0, seilzug(v)), anchor=(X0, 352))
                for k, hell in enumerate(self.chips_hell):
                    if k == 2:
                        put(f, hell, op=min(1, v * 2) * out, scale=1 + 0.06 * math.sin(math.pi * seg(t, T_S4 + 0.1, 0.4)))
                    else:
                        put(f, self.chips_matt[k], op=0.32 * min(1, v * 2) * out)
            return f, 43
        put(f, self.rails[3])                                     # Szene 4: Fazit, Querschnitt West -> Ost
        u = seilzug(seg(t, T_S5 + 0.4, EIN))
        put(f, self.fazit, dx=lerp(-40, 0, u), op=u)
        return f, 44


# ------------------------------------------------------------------ Ton: Musik in B-Dur (B flat), 82 BPM
def sound_events(b):
    """Musik nach Szenen (SoundBook.musik, 82 BPM): Behauptung und Rate-Pause in G-Moll (Paralleltonart) mit Countdown aus
    Toenen der B-Dur-Pentatonik, Scan als bewegtes B-Dur-Arpeggio, Gitter-Tausch als steigende Toene, Payoff als
    Akkordschlag in G-Moll, Fazit loest nach B-Dur auf, Klanglogo im Abspann."""
    h1 = rk.Hook1(t_grab=T_GRAB, t_geo=T_GEO, t_out=T_OUT)
    b.hook1(h1, akkord=GM9, bassnote=43)
    b.musik([
        (T_Q - 0.1, T_CHIPS, GM9, 43, "ruhig"),                # Behauptung
        (T_CHIPS, T_GUESS, EBMAJ7, 39, "ruhig"),               # Chips
        (T_GUESS, T_HOOK, CM7, 36, "flaeche"),                 # Rate-Pause (Countdown darueber)
        (T_HOOK, T_S2, F_, 41, "flaeche"),                     # Atempause
        (T_S2, T_TXT1, BB, 46, "bewegt"),                      # Scan
        (T_TXT1, T_Z0, GM9, 43, "ruhig"),                      # THIS TOWER: DOLOMITE.
        (T_Z0, T_SWAP, EBMAJ7, 39, "bewegt"),                  # Zoom, Gitter
        (T_SWAP, T_RISE, CM7, 36, "bewegt"),                   # Tausch, Text
        (T_RISE, T_S4 - 0.15, FSUS4, 41, "flaeche"),           # Steigerung, dann 0,15 s Stille
        (T_S4, T_S5, GM9, 43, "flaeche"),                      # Aufloesung: verdauen
        (T_S5, T_S5 + 1.8, EBMAJ7, 39, "ruhig"),               # Fazit ...
        (T_S5 + 1.8, T_END, BB, 46, "ruhig"),                  # ... loest nach B-Dur auf
    ], bpm=82.0, gain=-12.0)
    b.musik([(T_END, DUR, BB, 46, "flaeche")], bpm=82.0, gain=-14.5)   # Abspann leiser: Payoff bleibt der Hoehepunkt
    for k, note in enumerate((70, 74, 77)):                    # Chips
        b.ton("zupf", T_CHIPS + 0.3 * k, -15.0, "chips", m=note, dauer=0.8, pan=0.3 * (k - 1))
    b.ton("zupf", T_GUESS, -13.0, "frage", m=74, dauer=0.9)
    b.countdown(T_GUESS + 0.45, T_HOOK - 0.05, step=0.4, gain=-11.0, tonleiter=PENTA[:4])
    b.ton("zupf", T_S2, -14.0, "bohrhaken", m=82, dauer=0.9)
    b.ton("schwelle", T_SCAN[0], -15.0, "scan", akkord=BB, dauer=T_SCAN[1] * 0.45)
    b.ton("zupf", T_LAB, -13.0, "label", m=74, dauer=1.0)
    b.ton("zupf", T_SCAN[0] + T_SCAN[1] * 0.55, -12.0, "scan-turm", m=79, dauer=1.1)
    b.ton("zupf", T_TXT1, -14.0, "text", m=77, dauer=0.9)
    b.klang("chalk_slap", T_MOVE1 + 0.75, -13.0, "griff", seed=2)
    b.ton("schwelle", T_Z0, -14.0, "zoom", akkord=EBMAJ7, dauer=0.9)
    b.ton("zupf", T_S3, -14.0, "bohrhaken", m=84, dauer=0.9)
    b.ton("zupf", T_CA, -15.0, "legende", m=70, dauer=0.8)
    for r in range(3):                                          # jede zweite Lage wird Mg: steigende Toene
        b.ton("zupf", T_SWAP + 0.17 * r, -13.0, "tausch", m=PENTA[2 + r], dauer=0.9, pan=0.3 * (r - 1))
    b.ton("zupf", T_MG, -15.0, "legende", m=79, dauer=0.8)
    b.synth("whoosh", T_ZB, -20.0, "zoom-zurueck", dur=0.7, seed=9)
    b.ton("schwelle", T_RISE, -8.0, "steigerung", akkord=FSUS4, dauer=T_S4 - 0.15 - T_RISE)
    b.klang("sub_hit", T_S4 - 0.01, -11.0, "payoff-einschlag", f0=78.0, f1=36.0)
    b.ton("akzent", T_S4, -4.0, "payoff", akkord=GM9, bassnote=43)
    b.ton("zupf", T_S4 + 0.12, -10.0, "chip", m=82, dauer=1.0)
    b.klang("chalk_slap", T_MOVE2 + 0.85, -12.0, "griff", seed=3)
    b.ton("zupf", T_S5 + 0.4, -14.0, "fazit", m=77, dauer=0.9)
    b.ton("zupf", T_S5 + 0.55, -15.0, "fazit", m=82, dauer=1.1)
    b.klanglogo(T_END + 0.3, tonika=70, gain=-9.5)               # Abspann: Logo (B-Dur)
    b.ton("zupf", T_END + 1.3, -14.0, "herz", m=82, dauer=1.2)


cover_t = round(T_Q + 0.85, 2)
META = dict(
    slug="2026-10-30_mythorrock-02", dur_range=[20.0, 28.0], payoff_t=T_S4, abspann_ab=T_END,
    title="GeoCrimps r007 MYTH OR ROCK #02 (Quiz), Fassung 1", ablauf="quiz",
    hook1_bis=T_OUT, hook_ab=T_Q, hook_bis=T_HOOK, weitere_fragen=[[T_GUESS, T_HOOK]], cover_t=cover_t,
    on_screen=["MYTH OR ROCK", "CLIMBERS SAY:", "FRANKENJURA IS LIMESTONE.", "TRUE", "FALSE", "IT DEPENDS",
               "YOUR GUESS?", "THIS TOWER: DOLOMITE.", "MAGNESIUM REPLACES HALF THE CALCIUM.",
               "LIMESTONE AND DOLOMITE.", "YOU'RE CLIMBING BOTH.", rk.Outro.CTA],
    labels=["LIMESTONE", "Ca", "Mg"],
    verdauen=["LIMESTONE AND DOLOMITE.", "YOU'RE CLIMBING BOTH."],
    qc_times=[0.0, 0.4, 0.72, 1.1, 1.6, cover_t, round(T_GUESS + 1.2, 2), round(T_S2 + 1.1, 2),
              round(T_TXT1 + 1.5, 2), round(T_Z1 + 0.6, 2), round(T_SWAP + 1.2, 2), round(T_TXT2 + 2.0, 2),
              round(T_S4 + 1.0, 2), round(T_S5 + 1.5, 2), round(T_END - 0.2, 2), round(T_END + 2.0, 2)],
    marks=[(0, "Hook 1"), (T_GRAB, "Griff"), (T_GEO, "x GEOLOGY"), (T_Q, "Hook 2"), (T_CHIPS, "Chips"),
           (T_GUESS, "Rate-Pause"), (T_S2, "Zug 1 Scan"), (T_TXT1, "Turm"), (T_Z0, "Zoom"), (T_SWAP, "Ca->Mg"), (T_S4, "PAYOFF"),
           (T_S5, "Fazit"), (T_END, "Abspann")])

if __name__ == "__main__":
    if "--reach" in sys.argv:
        print(check_reach())
        sys.exit(0)
    rk.run(Reel, sound_events, META)
