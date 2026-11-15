#!/usr/bin/env python3
"""Reel 013 -- HOLD ID #04: "Conglomerate: what made this hold so round?" (Faktenbasis: Post #024, Konglomerat),
Ablauf "quiz".

Fassung 1 vom 15.11.2026 nach PRODUKTION.md (Stand 16.10.2026), Vorlage r003 Fassung 6 (Hook 1 + Hook 2, Lesezeit,
ruhiges Tempo, Musik statt Klicks, Abspann mit LIKE & FOLLOW); Quiz-Chips wie r010.
Hook 1 0-1,45 s: GEOCRIMPS + CLIMBING ab Frame 0, ein Kletterer kneift einen runden Kiesel, der aus einer Konglomerat-
wand ragt (Kreidewolke), "x GEOLOGY" schlaegt ein und die Wand klappt in die Konglomerat-Signatur auf (Ellipsen); das
verraet nicht, woher die Rundung kommt.
Hook 2 ab 1,8 s: Formatlabel HOLD ID, Kontextzeile "CONGLOMERATE:" (Kieselfarbe) ueber "WHAT MADE THIS HOLD SO ROUND?";
ab 4,6 s drei Griff-Chips A LAVA / B RIVER / C CLIMBERS, ab 5,85 s "YOUR GUESS?" mit Countdown aus Toenen (1,95 s).
Zug 1 (Zoom auf die Hand am Kiesel, 0,9 s): die Bindemasse zwischen den Kieseln leuchtet: "GLUED GRAVEL."
Zug 2 (Zeitraffer rueckwaerts): die Bindemasse loest sich, die Kiesel werden locker, Ueberblendung in einen Fluss im
Seitenschnitt, Kiesel rollen ueber das Flussbett: "BEFORE: LOOSE GRAVEL."
Payoff: Chip B leuchtet unter "A RIVER ROLLED IT." (Akkordschlag), die rollenden Kiesel leuchten. Folge (zurueck an der
Wand): die Bindemasse wittert zurueck, die Kiesel stehen weiter heraus, der Kletterer greift an den naechsten Kiesel:
"GLUE USUALLY WEARS FIRST." Kein Stempel (HOLD ID-Rahmen 17-24 s laesst neben Quiz und Lesezeit keinen Platz).
Fakten (v2/faktenbasis/024/sources.md): Konglomerat = gerundete Klasten (Kies, Geroelle) in feinerer Matrix, verkittet
durch Calcit, Eisenoxid, Silica oder Ton; die Rundung entsteht beim Transport in Fluessen und Schuttstroemen (das Bild
zeigt den Fluss, die Caption nennt beide); der Zement ist in der Regel schwaecher als die Klasten, die Matrix wittert
zurueck ("usually", Kalibrierung in sources.md). Keine Reibungsaussage, kein Gebiet im Bild.
Bildmittel (Abwechslungsregel): Uebergang Zoom auf die Hand, Zeitraffer rueckwaerts mit Ueberblendung in den Fluss
(r012: Isolinien-Welle, Profilschnitt) | Enthuellung Bindemasse leuchtet, loest sich, Kiesel rollen im Fluss (r012:
Abkuehlung und Risse im Profil) | Payoff Chip B leuchtet, Antwort gross mit Push-in, Kiesel leuchten (r012: kein Chip) |
Musik E-Dur mit Cis-Moll-Flaechen, 83 BPM (r012: As-Dur 79 BPM).
Aufruf:  python3 r013_holdid_024.py --out ../../../reels --qc <Ordner>   (--stills 0,4.8 | --reach)
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
EIN = 0.45
T_GRAB, T_GEO, T_OUT = 0.40, 0.72, 1.45
T_Q = 1.80                         # Hook 2: Formatlabel, Kontextzeile, Frage
T_CHIPS = T_Q + 2.8                # drei Griff-Chips (je 0,3 s versetzt)
T_GUESS = T_CHIPS + 1.25           # "YOUR GUESS?" + Countdown
T_HOOK = T_GUESS + 1.95            # Ende der Rate-Pause
T_S2 = T_HOOK + 0.4                # Zug 1: Zoom auf die Hand, Bindemasse leuchtet
T_ZOOM = 0.9
T_GLOW = T_S2 + 0.55
T_S3 = T_S2 + 2.35                 # Zug 2: Bindemasse loest sich, Ueberblendung in den Fluss
T_X = (T_S3 + 0.35, 0.65)          # Ueberblendung Wand -> Fluss
T_RISE = T_S3 + 2.45               # Akkord schwillt an, 0,15 s Stille, dann Payoff
T_S4 = T_RISE + 0.75               # Payoff: Chip B, "A RIVER ROLLED IT."
T_S5 = T_S4 + 3.35                 # Folge: zurueck an der Wand
T_BACK = 0.5                       # Ueberblendung Fluss -> Wand
T_WEATHER = (T_S5 + 0.2, 1.3)      # Bindemasse wittert zurueck
T_FAZ = T_S5 + 0.25                # Fazit
T_ZUG = (T_FAZ + 0.9, 0.9)         # Kletterer greift den naechsten Kiesel
T_END = T_FAZ + 3.5                # Abspann
DUR = T_END + rk.Outro.DUR

ZC, ZOOM = (772, 1150), 1.7        # Zoom auf die Hand am Kiesel

# ------------------------------------------------------------------ Szene: Konglomeratwand
PEB = "#C9B48E"                    # Kieselfarbe (Kontextzeile, Signatur)
MATRIX, MATRIX_DOT, MATRIX_OLD = "#5A4E3E", "#776852", "#2B251E"
GLUE = "#EADFC2"
HOLD_COL = "#DCCBA6"                # der Griff: heller Kiesel
PEB_COLS = ["#A39A8C", "#B9AA8E", "#8A9096", "#C7B595", "#9C8D78", "#B0A79A"]
RIDGE = [(30, 1012), (120, 996), (210, 1006), (300, 986), (390, 994), (470, 980), (560, 988), (640, 978),
         (720, 984), (800, 994), (880, 1012), (960, 1004), (1050, 1020)]
WALL = RIDGE + [(1050, H + 10), (30, H + 10)]
HOLD = (772, 1158, 58, 46)         # der Griff dieses Reels: grosser runder Kiesel
H_R = (772, 1122)                  # rechte Hand kneift den Kiesel oben
H_L = (640, 1150)
H_LF, H_RF = (652, 1452), (752, 1440)
H_TOP = (698, 1066)                # Fazit: naechster Kiesel
FIXED = [HOLD, (640, 1160, 30, 22), (652, 1462, 32, 20), (752, 1450, 30, 20), (698, 1074, 30, 22)]

BACK = dict(sw=22, hw=13, eb=(-1, 1), kb=(1, -1))
POSE_START = dict(BACK, hip=(694, 1370), lean=0, lh=H_L, rh=(760, 1255), lf=(662, 1530), rf=(744, 1520))
POSE_GRAB = dict(BACK, hip=(702, 1330), lean=3, lh=H_L, rh=H_R, lf=H_LF, rf=H_RF)
POSE_SWING = dict(POSE_GRAB, hip=(708, 1322), lean=6)
POSE_REACH = dict(BACK, hip=(712, 1292), lean=-4, lh=H_TOP, rh=H_R, lf=H_LF, rf=H_RF)

# ------------------------------------------------------------------ Szene: Fluss (Seitenschnitt, schematisch)
WATER_TOP, BED_Y = 900, 1300
Y_PAY_CHIPS = 700

# Tonart E-Dur mit Cis-Moll-Flaechen (MIDI), Bass eine Oktave tiefer
E_, EADD9, CSM7, AMAJ7, FSM7, B_, BSUS4 = ([52, 56, 59, 64], [52, 56, 59, 66], [56, 59, 61, 64], [57, 61, 64, 68],
                                           [54, 57, 61, 64], [54, 59, 63, 66], [54, 59, 64, 66])
PENTA_E = [64, 66, 68, 71, 73, 76, 78]   # E-Dur-Pentatonik


def ease(u):
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, u)))


def climber_pose(t):
    if t < T_GRAB:
        return kl.lerp_pose(POSE_START, POSE_SWING, seilzug(seg(t, 0.0, T_GRAB)))
    if t < T_ZUG[0]:
        u = seg(t, T_GRAB, 0.3)
        p = kl.lerp_pose(POSE_SWING, POSE_GRAB, ease(u))
        if u >= 1:                                               # atmet, Becken pendelt (Bewegung ohne Info)
            w = math.sin(2 * math.pi * (t - T_GRAB - 0.3) / 2.6)
            p = dict(p, hip=(p["hip"][0] + 4 * w, p["hip"][1] + 1.5 * abs(w)), lean=p["lean"] + 1.5 * w)
        return p
    p = kl.lerp_pose(POSE_GRAB, POSE_REACH, seilzug(seg(t, T_ZUG[0], T_ZUG[1])))
    b = math.sin(2 * math.pi * (t - T_ZUG[0]) / 2.8)
    return dict(p, hip=(p["hip"][0], p["hip"][1] + 1.5 * b), lean=p["lean"] + 0.6 * b)


def reach_check():
    """Abstand jeder Hand und jedes Fusses zu ihrem Ziel (px) in allen Posen; muss < 1 sein."""
    c = kl.Climber(scale=1.0, width=18.0, torso_w=36.0)
    out = {}
    for name, p in (("start", POSE_START), ("grab", POSE_GRAB), ("swing", POSE_SWING), ("reach", POSE_REACH)):
        j = c.joints(p)
        out[name] = round(max(math.hypot(j[k][0] - p[k][0], j[k][1] - p[k][1]) for k in ("lh", "rh", "lf", "rf")), 2)
    return out


def ridge_y(x):
    xs = [p[0] for p in RIDGE]; ys = [p[1] for p in RIDGE]
    return float(np.interp(x, xs, ys))


def pack_pebbles():
    """Kiesel dicht gepackt in der Wand: feste Griffe zuerst, dann zufaellig ohne Ueberlappung."""
    rnd = random.Random(24)
    peb = [(x, y, rx, ry, HOLD_COL if (x, y) == HOLD[:2] else rnd.choice(PEB_COLS), rnd.uniform(-25, 25) if (x, y) != HOLD[:2] else -8)
           for x, y, rx, ry in FIXED]
    tries = 0
    while tries < 9000:
        tries += 1
        rx = rnd.uniform(11, 34); ry = rx * rnd.uniform(0.62, 0.86)
        x = rnd.uniform(40, 1040); y = rnd.uniform(990, 1915)
        if y - ry < ridge_y(x) + 6:
            continue
        if any(math.hypot((x - a) / (rx + ra + 7), (y - b) / (ry + rb + 7)) < 1.0 for a, b, ra, rb, _, _ in peb):
            continue
        peb.append((x, y, rx, ry, rnd.choice(PEB_COLS), rnd.uniform(-30, 30)))
    return peb


def ellipse_poly(x, y, rx, ry, rot=0.0, n=36):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return [(x + rx * math.cos(a) * c - ry * math.sin(a) * s, y + rx * math.cos(a) * s + ry * math.sin(a) * c)
            for a in np.linspace(0, 2 * math.pi, n, endpoint=False)]


def draw_pebble(d, x, y, rx, ry, col, rot, shadow=4.0, sh_a=170, glow=None):
    d.polygon([P(px + shadow * 0.8, py + shadow) for px, py in ellipse_poly(x, y, rx, ry, rot)], fill=o.rgb(C["obsidian"], sh_a))
    d.polygon([P(*q) for q in ellipse_poly(x, y, rx, ry, rot)], fill=o.rgb(col),
              outline=o.rgb(glow or "#1E1A15"), width=int((4 if glow else 1.5) * o.S))
    d.polygon([P(*q) for q in ellipse_poly(x - rx * 0.28, y - ry * 0.32, rx * 0.42, ry * 0.3, rot)], fill=o.rgb("#FFFFFF", 46))


class Reel(rk.ReelBase):
    DUR = DUR

    def __init__(self):
        super().__init__()
        self.rail = rk.Rail(2)
        self.outro = rk.Outro()
        self.rails = [rk.rail_sprite(0, 2), rk.rail_sprite(1, 2), rk.rail_sprite(2, 2), rk.rail_sprite(2, 2, logo_on=True)]
        self.hook1 = rk.Hook1(t_grab=T_GRAB, t_geo=T_GEO, t_out=T_OUT)
        self.climber = kl.Climber(scale=1.0, width=18.0, torso_w=36.0)
        self.peb = pack_pebbles()
        # ---- Texte
        self.label = m.text_sprite("HOLD ID", X0, rk.FORMAT_Y, "stencil", 40, C["slate"], tracking=0.12)
        self.hook_kick = m.text_sprite("CONGLOMERATE:", X0, rk.HOOK_Y, "display", 96, PEB)
        self.hook, y_q = m.lines_sprite(["WHAT MADE THIS", "HOLD SO ROUND?"], rk.HOOK_Y + 112, size=136)
        self.y_chips = int(y_q) + 26
        labels = ["A  LAVA", "B  RIVER", "C  CLIMBERS"]
        self.chips, self.chips_hell, self.chips_pay, x = [], [], [], X0
        for lab in labels:
            wch = o.text_width(lab, "stencil", 52) + 52
            self.chips.append(self._chip(x, self.y_chips, lab, C["magnesia"]))
            self.chips_hell.append(self._chip(x, Y_PAY_CHIPS, lab, C["bio"]))
            self.chips_pay.append(self._chip(x, Y_PAY_CHIPS, lab, C["magnesia"]))
            x += wch + 24
        self.chips_right = x
        self.chips_matt = [m.Sprite(c.img, c.x, c.y) for c in self.chips_pay]   # abgeblendet: nicht als Info gemessen
        self.guess = m.text_sprite("YOUR GUESS?", X0, self.y_chips + 104, "text_b", 54, C["magnesia"])
        self.text1, _ = m.lines_sprite(["GLUED GRAVEL."], 352, role="display_xb", size=118)
        self.text2, _ = m.lines_sprite(["BEFORE:", "LOOSE GRAVEL."], 352, role="display_xb", size=118)
        self.answer, _ = m.lines_sprite(["A RIVER", "ROLLED IT."], 352, size=170)
        self.fazit, _ = m.lines_sprite(["GLUE USUALLY", "WEARS FIRST."], 352, size=136)
        # ---- Wand: frisch und verwittert (Matrix tiefer, Kiesel stehen heraus)
        self.bg = m.background(lambda im: self._draw_wall(im, weathered=False))
        self.bg_old = m.background(lambda im: self._draw_wall(im, weathered=True))
        self.geo = kl.GeoReveal(WALL, "conglomerate", HOLD[0], HOLD[1], color=PEB, pat_alpha=150, seed=9)
        self.glue = self._glue_sprite()
        # ---- Fluss
        self.bg_river = m.background(self._draw_river)
        rnd = random.Random(7)
        self.rollers = [(rnd.uniform(0, 1), rnd.uniform(0.07, 0.12), rnd.uniform(28, 46), rnd.choice(PEB_COLS),
                         rnd.uniform(0, 6.28)) for _ in range(7)]

    # -------------------------------------------------------------- Hilfsbilder
    @staticmethod
    def _chip(x, y, label, fill):
        spr = m.sprite(lambda im: o.hold_label(im, x, y, label, fill, size=52, role="stencil", pad=(26, 13)))
        spr.text = " ".join(label.split())
        return spr

    def _wall_mask(self):
        mk = Image.new("L", (W * o.S, H * o.S), 0)
        ImageDraw.Draw(mk).polygon([P(x, y) for x, y in WALL], fill=255)
        return mk

    def _draw_wall(self, im, weathered):
        o.contour_field(im, 820, 640, n=9, r0=140, step=64, alpha=70)
        d = ImageDraw.Draw(im)
        d.polygon([P(x, y) for x, y in WALL], fill=o.rgb(MATRIX_OLD if weathered else MATRIX))
        rnd = random.Random(3)
        for _ in range(2600):                                     # feine Koerner der Matrix
            x = rnd.uniform(35, 1045); y = rnd.uniform(985, 1915)
            if y < ridge_y(x) + 4:
                continue
            r = rnd.uniform(1.2, 2.6)
            d.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=o.rgb(MATRIX_DOT, 110 if weathered else 200))
        for x, y, rx, ry, col, rot in self.peb:
            if y - ry < ridge_y(x) + 2:
                continue
            draw_pebble(d, x, y, rx, ry, col, rot, shadow=9.0 if weathered else 3.5, sh_a=235 if weathered else 150)
        d.line([P(x, y) for x, y in RIDGE], fill=o.rgb(PEB), width=int(7 * o.S), joint="curve")

    def _glue_sprite(self):
        """Bindemasse zwischen den Kieseln (Zug 1): Matrixflaeche ohne Kiesel, mit Kristallfunken."""
        mk = self._wall_mask(); dm = ImageDraw.Draw(mk)
        for x, y, rx, ry, col, rot in self.peb:
            dm.polygon([P(*q) for q in ellipse_poly(x, y, rx + 1, ry + 1, rot)], fill=0)
        lay = Image.new("RGBA", mk.size, o.rgb(GLUE)); lay.putalpha(mk)
        d = ImageDraw.Draw(lay); rnd = random.Random(5)
        for _ in range(900):
            x = rnd.uniform(35, 1045); y = rnd.uniform(990, 1915); r = rnd.uniform(1.5, 3.0)
            if mk.getpixel((int(x * o.S), int(y * o.S))) > 0:
                d.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=o.rgb("#FFFFFF"))
        small = lay.resize((W, H), Image.LANCZOS)
        bb = small.getbbox()
        return m.Sprite(small.crop(bb), bb[0], bb[1])

    def _draw_river(self, im):
        o.contour_field(im, 820, 640, n=9, r0=140, step=64, alpha=70)
        d = ImageDraw.Draw(im)
        d.rectangle([P(0, WATER_TOP), P(W, BED_Y)], fill=o.rgb("#123A55"))
        d.rectangle([P(0, BED_Y), P(W, H)], fill=o.rgb("#2A251F"))
        rnd = random.Random(11)
        for _ in range(520):                                      # Kiesbett
            x = rnd.uniform(0, W); y = rnd.uniform(BED_Y + 10, 1915); rx = rnd.uniform(12, 30)
            draw_pebble(d, x, y, rx, rx * rnd.uniform(0.6, 0.8), rnd.choice(PEB_COLS), rnd.uniform(-20, 20), shadow=3)
        d.line([P(0, BED_Y), P(W, BED_Y)], fill=o.rgb(PEB, 200), width=int(3 * o.S))

    # -------------------------------------------------------------- Welten
    def wall_world(self, t):
        w = ease(seg(t, *T_WEATHER)) if t >= T_S5 else 0.0
        f = self.bg.copy() if w <= 0 else (self.bg_old.copy() if w >= 1 else Image.blend(self.bg, self.bg_old, w))
        u = seilzug(seg(t, T_GEO, 0.5))
        if u > 0 and t < T_OUT + 0.4:
            self.geo.put(f, u, fade=1 - seg(t, T_OUT, 0.4))
        if T_GLOW <= t < T_X[0] + T_X[1]:                        # Zug 1: Bindemasse leuchtet; Zug 2: sie loest sich
            g = ease(seg(t, T_GLOW, 0.6)) * (1 - ease(seg(t, T_S3, 0.6)))
            put(f, self.glue, op=0.55 * g * (0.85 + 0.15 * math.sin(2 * math.pi * (t - T_GLOW) / 1.1)))
        dy = 0.0
        if T_S3 <= t < T_S5:                                     # Kiesel werden locker: der Griff wackelt
            dy = 2.5 * math.sin(t * 40) * seg(t, T_S3 + 0.2, 0.3)
        put(f, self.climber.sprite(climber_pose(t)), dy=dy)
        kl.chalk_puff(f, t, T_GRAB, H_R[0], H_R[1] - 4, seed=11)
        kl.chalk_puff(f, t, T_ZUG[0] + T_ZUG[1] - 0.05, H_TOP[0], H_TOP[1] - 4, seed=12, size=0.7)
        if t >= T_S5:                                            # Verwitterung: Koerner rieseln aus der Matrix
            rnd = random.Random(31); dr = ImageDraw.Draw(f)
            for k in range(18):
                x0 = rnd.uniform(560, 960); y0 = rnd.uniform(1040, 1380); t0 = T_WEATHER[0] + rnd.uniform(0, 2.4)
                v = seg(t, t0, 0.9)
                if 0 < v < 1:
                    y = y0 + 160 * v * v
                    dr.ellipse([x0 - 2.2, y - 2.2, x0 + 2.2, y + 2.2], fill=o.rgb(MATRIX_DOT, int(230 * (1 - v))))
        return f

    def river_world(self, t, glow=0.0):
        f = self.bg_river.copy()
        lay = Image.new("RGBA", (W, BED_Y - WATER_TOP + 80), (0, 0, 0, 0)); dr = ImageDraw.Draw(lay)
        oy = WATER_TOP - 40
        for k in range(9):                                       # Stroemungslinien nach rechts
            y = WATER_TOP + 25 + k * 30
            ph = (t * 0.45 + k * 0.137) % 1.0
            x0 = lerp(-300, W + 50, ph)
            pts = [(x, y + 4 * math.sin(x / 40 + k) - oy) for x in range(int(x0), int(x0 + 230), 10)]
            if len(pts) > 1:
                dr.line(pts, fill=o.rgb(C["water"], 150), width=3)
        dr.line([(x, WATER_TOP + 5 * math.sin(x / 50 + t * 2.4) - oy) for x in range(0, W + 1, 12)],
                fill=o.rgb(C["water"]), width=4)
        f.alpha_composite(lay, (0, oy))
        im = Image.new("RGBA", (W * o.S, 200 * o.S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        for ph, sp, r, col, a0 in self.rollers:                  # Kiesel rollen ueber das Bett und springen
            s = (ph + t * sp) % 1.0
            x = lerp(-60, W + 60, s)
            hop = abs(math.sin(s * 30 + a0)) * 14
            y = BED_Y - r * 0.8 - hop - (BED_Y - 200)
            rot = math.degrees(x / r)
            pts = ellipse_poly(x, y, r, r * 0.8, rot)
            d.polygon([P(*q) for q in pts], fill=o.rgb(col),
                      outline=o.rgb(C["bio"] if glow > 0.02 else "#1E1A15", int(255 * max(0.4, glow)) if glow > 0.02 else 255),
                      width=int((4 if glow > 0.02 else 1.5) * o.S))
            c, s_ = math.cos(math.radians(rot)), math.sin(math.radians(rot))
            d.line([P(x - r * 0.6 * c, y - r * 0.6 * s_), P(x + r * 0.6 * c, y + r * 0.6 * s_)], fill=o.rgb("#FFFFFF", 70),
                   width=int(3 * o.S))
        f.alpha_composite(im.resize((W, 200), Image.LANCZOS), (0, BED_Y - 200))
        return f

    # -------------------------------------------------------------- Frames
    def frame(self, t):
        if t >= T_END:
            return self.outro.frame(t, T_END), 45
        if t < T_HOOK + 0.25:                                     # Szene 1: Hook 1, Hook 2, Quiz
            f = m.zoomed(self.wall_world(t), 1 + 0.03 * ease(seg(t, 0, T_HOOK)), *ZC)
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
                    pul = 1 + 0.03 * math.sin(2 * math.pi * (t - T_GUESS - 0.15 * k) / 0.9) if t >= T_GUESS else 1.0
                    put(f, spr, op=min(1.0, v * 2) * fade, scale=lerp(0.7, 1.0, griff(v)) if v < 1 else pul)
            v = seilzug(seg(t, T_GUESS, EIN))
            if v > 0:
                put(f, self.guess, dx=lerp(-30, 0, v), op=v * fade)
            return f, 41
        if t < T_S3:                                              # Szene 2: Zug 1, Zoom auf die Hand
            z = lerp(1.03, ZOOM, seilzug(seg(t, T_S2, T_ZOOM)))
            f = m.zoomed(self.wall_world(t), z, *ZC)
            put(f, self.rails[1]); self.rail.pop(f, t, 0, T_S2)
            u = seilzug(seg(t, T_S2 + 0.05, EIN))
            put(f, self.text1, dx=lerp(-40, 0, u), op=u * (1 - seg(t, T_S3 - 0.15, 0.15)))
            return f, 42
        if t < T_S5:                                              # Szene 3: Zug 2 (Fluss), Payoff
            x = ease(seg(t, *T_X))
            push = 1 + 0.04 * ease(seg(t, T_S4, T_S5 - T_S4))
            glow = seg(t, T_S4, 0.4)
            if x < 1:
                fw = m.zoomed(self.wall_world(t), ZOOM * (1 + 0.04 * seg(t, T_S3, 1.0)), *ZC)
                f = fw if x <= 0 else Image.blend(fw, self.river_world(t), x)
            else:
                f = m.zoomed(self.river_world(t, glow), push, 540, 1250)
            put(f, self.rails[3] if t >= T_S4 else self.rails[2]); self.rail.pop(f, t, 1, T_S3)
            u = seilzug(seg(t, T_S3 + 0.05, EIN))
            put(f, self.text2, dx=lerp(-40, 0, u), op=u * (1 - seg(t, T_S4 - 0.2, 0.2)))
            v = seg(t, T_S4, 0.3)
            if v > 0:
                self.rail.logo_pop(f, t, T_S4)
                out = 1 - seg(t, T_S5 - 0.2, 0.2)
                put(f, self.answer, op=min(1, v * 2) * out, scale=lerp(1.18, 1.0, seilzug(v)), anchor=(X0, 352))
                for k, hell in enumerate(self.chips_hell):
                    if k == 1:
                        put(f, hell, op=min(1, v * 2) * out, scale=1 + 0.06 * math.sin(math.pi * seg(t, T_S4 + 0.1, 0.4)))
                    else:
                        put(f, self.chips_matt[k], op=0.32 * min(1, v * 2) * out)
            return f, 43
        x = ease(seg(t, T_S5, T_BACK))                            # Szene 4: zurueck an der Wand, Fazit
        fw = m.zoomed(self.wall_world(t), 1.0 + 0.035 * ease(seg(t, T_S5, T_END - T_S5)), *ZC)
        f = fw if x >= 1 else Image.blend(m.zoomed(self.river_world(t, 1.0), 1.04, 540, 1250), fw, x)
        put(f, self.rails[3])
        u = seilzug(seg(t, T_FAZ + 0.05, EIN))
        put(f, self.fazit, dx=lerp(-40, 0, u), op=u)
        return f, 46


# ------------------------------------------------------------------ Ton: Musik in E-Dur / Cis-Moll, 83 BPM
def sound_events(b):
    """Frage offen auf Cis-Moll7 und Amaj7, Rate-Pause mit Countdown aus Toenen der E-Pentatonik, Zug 1 bewegt in E,
    Bindemasse als steigende Funkeltoene, Zeitraffer rueckwaerts mit Figur fallend, Fluss bewegt (rollende Kiesel als
    tiefe Zupftoene), Steigerung auf H, Payoff als Akkordschlag in Cis-Moll, Fazit loest nach E-Dur auf, Klanglogo in E."""
    h1 = rk.Hook1(t_grab=T_GRAB, t_geo=T_GEO, t_out=T_OUT)
    b.hook1(h1, akkord=EADD9, bassnote=40)
    b.musik([
        (T_Q - 0.1, T_CHIPS, CSM7, 37, "ruhig"),
        (T_CHIPS, T_GUESS, AMAJ7, 45, "ruhig"),
        (T_GUESS, T_HOOK, FSM7, 42, "flaeche"),
        (T_HOOK, T_S2, BSUS4, 47, "flaeche"),
        (T_S2, T_S3, E_, 40, "bewegt"),
        (T_S3, T_S3 + 1.2, CSM7, 37, "fallend"),
        (T_S3 + 1.2, T_RISE, AMAJ7, 45, "bewegt"),
        (T_RISE, T_S4 - 0.15, B_, 47, "flaeche"),
        (T_S4, T_S5, CSM7, 37, "flaeche"),
        (T_S5, T_FAZ + 1.7, AMAJ7, 45, "ruhig"),
        (T_FAZ + 1.7, T_END, E_, 40, "ruhig"),
    ], bpm=83.0, gain=-12.0)
    b.musik([(T_END, DUR, E_, 40, "flaeche")], bpm=83.0, gain=-16.0)
    for k, note in enumerate((68, 71, 76)):
        b.ton("zupf", T_CHIPS + 0.3 * k, -15.0, "chips", m=note, dauer=0.8, pan=0.3 * (k - 1))
    b.countdown(T_GUESS + 0.1, T_HOOK - 0.1, step=0.42, gain=-11.0, tonleiter=PENTA_E[:5])
    b.ton("zupf", T_S2, -14.0, "bohrhaken", m=76, dauer=0.9)
    b.ton("schwelle", T_S2, -14.0, "zoom", akkord=E_, dauer=T_ZOOM)
    for k in range(5):                                          # Bindemasse leuchtet: steigende Funkeltoene
        b.ton("zupf", T_GLOW + 0.25 * k, -17.0, "bindemasse", m=PENTA_E[k] + 12, dauer=0.7, pan=0.3 * ((k % 3) - 1))
    b.ton("zupf", T_S3, -14.0, "bohrhaken", m=78, dauer=0.9)
    for k in range(4):                                          # Bindemasse loest sich: fallende Toene
        b.ton("zupf", T_S3 + 0.15 + 0.2 * k, -16.0, "loesen", m=PENTA_E[4 - k] + 12, dauer=0.7)
    b.synth("whoosh", T_X[0], -20.0, "ueberblendung", dur=0.7, seed=4)
    for k in range(6):                                          # rollende Kiesel: tiefe Zupftoene, leises Geroell
        tt = T_X[0] + T_X[1] + 0.15 + 0.3 * k
        b.ton("zupf", tt, -18.0, "kiesel", m=PENTA_E[(k * 2) % 5], dauer=0.6, pan=0.3 * ((k % 3) - 1))
    b.klang("crunch", T_X[0] + T_X[1] + 0.3, -26.0, "geroell", seed=7)
    b.ton("schwelle", T_RISE, -8.0, "steigerung", akkord=B_, dauer=T_S4 - 0.15 - T_RISE)
    b.klang("sub_hit", T_S4 - 0.01, -11.0, "payoff-einschlag", f0=78.0, f1=36.0)
    b.ton("akzent", T_S4, -4.0, "payoff", akkord=CSM7, bassnote=37)
    b.ton("zupf", T_S4 + 0.12, -10.0, "chip", m=80, dauer=1.0)
    b.synth("whoosh", T_S5, -21.0, "zurueck", dur=0.5, seed=9)
    for k in range(4):                                          # Matrix rieselt: leise fallende Toene
        b.ton("zupf", T_WEATHER[0] + 0.3 + 0.35 * k, -19.0, "verwitterung", m=PENTA_E[3 - k] + 12, dauer=0.6)
    b.klang("chalk_slap", T_ZUG[0] + T_ZUG[1] - 0.05, -12.0, "griff", seed=2)
    b.ton("zupf", T_ZUG[0] + T_ZUG[1], -14.0, "griff", m=76, dauer=0.9)
    b.klanglogo(T_END + 0.3, tonika=64, gain=-13.0)
    b.ton("zupf", T_END + 1.3, -17.0, "herz", m=71, dauer=1.2)


cover_t = round(T_Q + 0.85, 2)
META = dict(
    slug="2026-11-20_holdid-04", dur_range=[17.0, 24.0], payoff_t=T_S4, abspann_ab=T_END,
    title="GeoCrimps r013 HOLD ID #04 (Quiz), Fassung 1", ablauf="quiz",
    hook1_bis=T_OUT, hook_ab=T_Q, hook_bis=T_HOOK, weitere_fragen=[[T_GUESS, T_HOOK]], cover_t=cover_t,
    on_screen=["HOLD ID", "CONGLOMERATE:", "WHAT MADE THIS HOLD SO ROUND?", "A LAVA", "B RIVER", "C CLIMBERS",
               "YOUR GUESS?", "GLUED GRAVEL.", "BEFORE: LOOSE GRAVEL.", "A RIVER ROLLED IT.", "GLUE USUALLY WEARS FIRST.",
               rk.Outro.CTA],
    labels=[],
    verdauen=["A RIVER ROLLED IT.", "GLUE USUALLY WEARS FIRST."],
    qc_times=[0.0, T_GRAB, T_GEO, 1.1, 1.6, cover_t, round(T_CHIPS + 1.0, 2), round(T_HOOK - 0.2, 2),
              round(T_S2 + 1.2, 2), round(T_S3 - 0.2, 2), round(T_S3 + 0.6, 2), round(T_RISE - 0.2, 2),
              round(T_S4 + 1.5, 2), round(T_S5 + 1.5, 2), round(T_END - 0.2, 2), round(T_END + 2.0, 2)],
    marks=[(0, "Hook 1"), (T_GRAB, "Griff"), (T_GEO, "x GEOLOGY"), (T_Q, "Hook 2"), (T_CHIPS, "Chips"),
           (T_GUESS, "Rate-Pause"), (T_S2, "Zug 1 Zoom"), (T_S3, "Zug 2 Fluss"), (T_S4, "PAYOFF"),
           (T_S5, "zurueck"), (T_FAZ, "Fazit"), (T_END, "Abspann")])

if __name__ == "__main__":
    if "--reach" in sys.argv:
        print(reach_check()); sys.exit(0)
    rk.run(Reel, sound_events, META)
