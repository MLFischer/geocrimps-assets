#!/usr/bin/env python3
"""Reel 010 -- REWIND #02: "Gritstone edge: where did its sand come from?" (Faktenbasis: Post #051, Gritstone kommt aus
einem Hochland), Ablauf "quiz".

Fassung 1 vom 04.11.2026 nach PRODUKTION.md (Stand 16.10.2026), Vorlage r003 Fassung 6 (Hook 1 + Hook 2, Lesezeit,
ruhiges Tempo, Musik statt Klicks, Abspann mit LIKE & FOLLOW); Quiz-Chips und Zeitreise wie r004 (REWIND #01).
Hook 1 0-1,45 s: GEOCRIMPS + CLIMBING ab Frame 0, ein Kletterer greift einen runden Gritstone-Riss (Break) unter der
Kante (Kreidewolke), "x GEOLOGY" schlaegt ein und die Wand klappt in ihre Sandstein-Signatur auf (Punkte, flache Baenke);
verraet die Herkunft nicht.
Hook 2 ab 1,8 s: Formatlabel REWIND, Kontextzeile "GRITSTONE EDGE:" (Gritfarbe) ueber "WHERE DID ITS SAND COME FROM?";
ab 4,9 s drei Griff-Chips A DESERT / B REEF / C HIGHLAND, ab 6,2 s "YOUR GUESS?" mit Countdown aus Toenen (2 s).
Zug 1 (Zeitreise zurueck): der Kletterer verblasst, der Zaehler laeuft auf 320 Millionen Jahre (Zeitleiste 0-360 nach
outcrop.AGE, Himmel in Altersfarbe), die Wand sinkt; Ziel "≈320 / MILLION YEARS AGO". Es erscheint die Landschaft
von damals: links ein Hochland mit Granit- und Gneis-Signatur, rechts ein Becken unter Wasser.
Zug 2 (Ursprung): ein Fluss fuehrt Koerner vom Hochland nach rechts (Sueden) ins Becken, ein Delta baut sich mit
schraegen Schuettungslagen vor: "RIVERS CARRIED IT SOUTH."
Payoff: Chip C leuchtet, "A NORTHERN HIGHLAND." (Akkordschlag), der Umriss des Hochlands leuchtet. Folge (zurueck ins
Heute): Zaehler laeuft auf 0, die Wand steigt ueber das Delta zurueck. Fazit: der Kletterer ist zurueck und schlaegt
an die Kante: "THIS EDGE IS IMPORTED HIGHLAND." Abspann mit LIKE & FOLLOW.
Fakten (v2/faktenbasis/051/sources.md; BGS/EA Baseline Report Series 18, Abesser, Shand & Ingram 2005): Millstone Grit,
Namur, Groessenordnung 320 Mio. Jahre; grobkoernige feldspatfuehrende Sandsteine; Liefergebiet "a granitic/gneiss terrain
in the north, probably Scotland and Scandinavia" (das "probably" steht in der Caption, das Bild nennt keinen Ort);
nach Sueden vorbauende Deltas, gespeist von grossen Flusssystemen; kein Wechsel des Liefergebiets im Namur.
Keine Reibungsaussage. Landschaft schematisch, nicht massstaeblich.
Bildmittel (Abwechslungsregel): Uebergang Zeitreise mit Zaehler und Altersfarbe (r009: Riss-Linie und Zoom) |
Enthuellung Fluss traegt Koerner, Delta baut Schuettungslagen vor (r009: Profilschnitt, Zeitraffer Salz) | Payoff Chip C
leuchtet, Antwort gross, Hochland leuchtet, kein Stempel (r009: Stempel HOLD ID) | Musik E-Moll mit G-Dur-Aufloesung,
81 BPM (r009: Es-Dur 88 BPM).
Aufruf:  python3 r010_rewind_051.py --out ../../../reels --qc <Ordner>   (--stills 0,4.8 fuer Einzelbilder | --reach)
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
T_GRAB, T_GEO, T_OUT = 0.40, 0.72, 1.45
T_Q = 1.80                         # Hook 2: Formatlabel, Kontextzeile, Frage
T_CHIPS = T_Q + 3.1                # drei Griff-Chips (je 0,3 s versetzt)
T_GUESS = T_CHIPS + 1.3            # "YOUR GUESS?" + Countdown
T_HOOK = T_GUESS + 2.0             # Ende der Rate-Pause
T_S2 = T_HOOK + 0.5                # Zug 1: Zeitreise zurueck
T_SEA = T_S2 + 4.2                 # angekommen: ≈320 Mio. Jahre, Landschaft von damals
T_S3 = T_SEA + 2.4                 # Zug 2: Fluss und Delta
T_RISE = T_S3 + 4.4                # Akkord schwillt an, 0,15 s Stille, dann Payoff
T_S4 = T_RISE + 1.0                # Payoff: Chip C, "A NORTHERN HIGHLAND."
T_S5 = T_S4 + 3.0                  # Folge: zurueck ins Heute
T_FAZ = T_S5 + 2.8                 # Fazit
T_END = T_FAZ + 3.9                # Abspann
DUR = T_END + rk.Outro.DUR
MA_ZIEL = 320.0
T_ZAEHL0, T_ZAEHL = T_S2 + 0.3, 3.4
T_WAND_AB = (T_S2 + 0.6, T_SEA - 0.6)
T_LAND = (T_SEA - 1.6, 1.2)                                    # Landschaft von damals blendet ein
T_DELTA = (T_S3 + 0.3, T_RISE + 0.6)                           # Delta baut sich vor
T_ZURUECK = 1.6
T_HEBEN = (T_S5 + 0.5, T_S5 + 2.3)                             # Wand steigt zurueck
T_ZUG = (T_FAZ + 0.6, T_FAZ + 1.5)                             # Fazit: Schlag an die Kante

# ------------------------------------------------------------------ Szene: Gritstone-Kante
GRIT, GRIT_IN, WALL_FILL = "#CDB894", "#8C7A5E", "#1A1814"      # Grit: Kante hell, Baenke gedaempft; Wandflaeche
RIDGE = [(30, 1092), (120, 1070), (210, 1080), (300, 1048), (390, 1056), (470, 1040), (560, 1046), (640, 1036),
         (720, 1038), (800, 1046), (880, 1072), (960, 1064), (1050, 1086)]
WALL = RIDGE + [(1050, H + 10), (30, H + 10)]
H_L, H_R = (640, 1150), (772, 1128)                            # Haende: runder Break
H_LF, H_RF = (652, 1452), (752, 1440)                          # Fuesse
H_TOP = (698, 1066)                                            # Fazit: Schlag an die Kante (Lippe ~1037)
BREAKS = [((560, 1150), (690, 1146)), ((715, 1128), (850, 1126)), ((600, 1452), (700, 1454)), ((700, 1440), (800, 1442)),
          ((150, 1250), (330, 1246)), ((830, 1290), (990, 1286)), ((260, 1500), (420, 1496))]
JOINTS = [((470, 1040), (476, 1240)), ((300, 1048), (292, 1380)), ((880, 1072), (888, 1300)), ((960, 1064), (956, 1500))]

BACK = dict(sw=22, hw=13, eb=(-1, 1), kb=(1, -1))
POSE_START = dict(BACK, hip=(694, 1370), lean=0, lh=H_L, rh=(760, 1255), lf=(662, 1530), rf=(744, 1520))
POSE_GRAB = dict(BACK, hip=(702, 1330), lean=3, lh=H_L, rh=H_R, lf=H_LF, rf=H_RF)
POSE_SWING = dict(POSE_GRAB, hip=(708, 1322), lean=6)
POSE_REACH = dict(BACK, hip=(712, 1292), lean=-4, lh=H_TOP, rh=H_R, lf=H_LF, rf=H_RF)

# ------------------------------------------------------------------ Landschaft vor ≈320 Mio. Jahren (schematisch)
SEA_Y = 1180                       # Meeresspiegel im Becken
FLOOR_Y = 1500                     # Beckenboden
COAST_X = 560
LAND = [(0, 880), (50, 830), (110, 880), (170, 815), (235, 870), (290, 845), (340, 905), (385, 990), (430, 1070),
        (480, 1120), (525, 1155), (COAST_X, SEA_Y), (COAST_X, H + 10), (0, H + 10)]
HIGHLAND = LAND[:8]                # Gipfellinie (fuer das Leuchten im Payoff)
RIVER = [(318, 878), (352, 925), (380, 978), (412, 1030), (448, 1072), (492, 1110), (530, 1142), (COAST_X + 6, SEA_Y - 3)]
XF0, XF1 = 256, 860                # Deltafront: Start und Ende des Vorbauens
Y_PAY_CHIPS = 700                  # Chips im Payoff unter der Antwort, ueber dem Hochland
SLOPE = 0.95                       # Front: x-Versatz je px Tiefe

# Tonart E-Moll / G-Dur (MIDI), Bass eine Oktave tiefer
EM9, CMAJ7, AM7, B7, D_, G_, DSUS4 = ([52, 55, 59, 62, 66], [55, 59, 60, 64], [55, 57, 60, 64], [54, 57, 59, 63],
                                      [54, 57, 62, 66], [55, 59, 62, 67], [55, 57, 62, 67])
PENTA_E = [64, 67, 69, 71, 74, 76, 79]
GRENZEN = [2.58, 23.04, 66.0, 143.1, 201.4, 251.902, 298.9]


def ease(u):
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, u)))


def ma_at(t):
    if t < T_S5:
        return MA_ZIEL * ease(seg(t, T_ZAEHL0, T_ZAEHL))
    return MA_ZIEL * (1 - ease(seg(t, T_S5 + 0.1, T_ZURUECK)))


def t_bei_ma(ma):
    return T_ZAEHL0 + T_ZAEHL * math.acos(1 - 2 * ma / MA_ZIEL) / math.pi


def wand_dy(t):
    if t < T_S5:
        return 920 * ease(seg(t, T_WAND_AB[0], T_WAND_AB[1] - T_WAND_AB[0]))
    return 920 * (1 - ease(seg(t, T_HEBEN[0], T_HEBEN[1] - T_HEBEN[0])))


def land_op(t):
    if t < T_S5:
        return ease(seg(t, *T_LAND))
    return 1 - seg(t, T_HEBEN[1] - 0.2, 0.4)


def delta_front(t):
    return lerp(XF0, XF1, ease(seg(t, T_DELTA[0], T_DELTA[1] - T_DELTA[0])))


def climber_pose(t):
    if t < T_GRAB:
        return kl.lerp_pose(POSE_START, POSE_SWING, seilzug(seg(t, 0.0, T_GRAB)))
    if t < T_FAZ:
        u = seg(t, T_GRAB, 0.3)
        p = kl.lerp_pose(POSE_SWING, POSE_GRAB, ease(u))
        if u >= 1:
            w = math.sin(2 * math.pi * (t - T_GRAB - 0.3) / 2.6)
            p = dict(p, hip=(p["hip"][0] + 4 * w, p["hip"][1] + 1.5 * abs(w)), lean=p["lean"] + 1.5 * w)
        return p
    p = kl.lerp_pose(POSE_GRAB, POSE_REACH, seilzug(seg(t, T_ZUG[0], T_ZUG[1] - T_ZUG[0])))
    b = math.sin(2 * math.pi * (t - T_FAZ) / 2.8)
    return dict(p, hip=(p["hip"][0], p["hip"][1] + 1.5 * b), lean=p["lean"] + 0.6 * b)


def climber_alpha(t):
    if t < T_S2:
        return 1.0
    if t < T_FAZ - 0.4:
        return 1.0 - seg(t, T_S2, 0.6)
    return seg(t, T_FAZ - 0.4, 0.5)


def reach_check():
    """Abstand jeder Hand und jedes Fusses zu ihrem Ziel (px) in allen Posen; muss < 1 sein."""
    c = kl.Climber(scale=1.0, width=18.0, torso_w=36.0)
    out = {}
    for name, p in (("start", POSE_START), ("grab", POSE_GRAB), ("swing", POSE_SWING), ("reach", POSE_REACH)):
        j = c.joints(p)
        out[name] = round(max(math.hypot(j[k][0] - p[k][0], j[k][1] - p[k][1]) for k in ("lh", "rh", "lf", "rf")), 2)
    return out


def _pathpos(path, s):
    """Punkt auf der Polylinie bei Anteil s (0..1)."""
    L = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(path, path[1:])]
    d = s * sum(L)
    for (a, b), l in zip(zip(path, path[1:]), L):
        if d <= l:
            u = d / l
            return a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u
        d -= l
    return path[-1]


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
        self.label = m.text_sprite("REWIND", X0, rk.FORMAT_Y, "stencil", 40, C["slate"], tracking=0.12)
        self.hook_kick = m.text_sprite("GRITSTONE EDGE:", X0, rk.HOOK_Y, "display", 96, GRIT)
        self.hook, y_q = m.lines_sprite(["WHERE DID ITS", "SAND COME FROM?"], rk.HOOK_Y + 112, size=136)
        self.y_chips = int(y_q) + 26
        labels = ["A  DESERT", "B  REEF", "C  HIGHLAND"]
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
        self.unit = m.text_sprite("MILLION YEARS AGO", X0, 548, "stencil", 44, C["magnesia"], tracking=0.1)
        self.ma_final = m.text_sprite("≈320", X0, 352, "display", 180, C["magnesia"])
        self.ziffern = {}
        self.text2, _ = m.lines_sprite(["RIVERS CARRIED", "IT SOUTH."], 352, role="display_xb", size=118)
        self.answer, _ = m.lines_sprite(["A NORTHERN", "HIGHLAND."], 352, size=170)
        self.fazit, _ = m.lines_sprite(["THIS EDGE IS", "IMPORTED HIGHLAND."], 352, size=136)
        # ---- Hintergrund, Wand
        self.bg = m.background(lambda im: o.contour_field(im, 820, 1720, n=9, r0=140, step=64, alpha=80))
        self.wall = m.sprite(self._draw_wall)
        beds = [[(x, y0 + 4 * math.sin(x / 140 + k)) for x in range(30, 1051, 30)] for k, y0 in enumerate(range(1120, 1900, 96))]
        self.geo = kl.GeoReveal(WALL, "sandstone", H_R[0], H_R[1], color=GRIT, pat_alpha=120, beds=beds, seed=9)
        self.wall_pat = self._pattern_sprite(WALL, "sandstone", 90, seed=9)
        # ---- Zeit
        self.tints = {}
        verlauf = Image.fromarray((np.clip(1 - np.arange(1060) / 1060.0, 0, 1)[:, None] ** 1.4 * 255
                                   * np.ones((1, W))).astype(np.uint8))
        for name, t0_, b_, col in o.AGE:
            lay = Image.new("RGBA", (W, 1060), o.rgb(col)); lay.putalpha(verlauf)
            self.tints[col] = m.Sprite(lay, 0, 0)
        self.leiste = m.sprite(self._draw_leiste)
        # ---- Landschaft von damals
        self.water = m.sprite(lambda im: ImageDraw.Draw(im).rectangle([P(COAST_X, SEA_Y), P(W, H)], fill=o.rgb("#123A55", 150)))
        self.floor = m.sprite(self._draw_floor)
        self.land = self._land_sprite()
        self.glow = m.sprite(lambda im: ImageDraw.Draw(im).line([P(x, y) for x, y in HIGHLAND], fill=o.rgb(C["bio"]),
                                                               width=int(9 * o.S), joint="curve"))
        self.river = m.sprite(lambda im: ImageDraw.Draw(im).line([P(x, y) for x, y in RIVER], fill=o.rgb(C["water"], 230),
                                                                width=int(10 * o.S), joint="curve"))
        self.delta_full = self._delta_full()
        rnd = random.Random(51)
        self.grains = [(rnd.uniform(0, 1), rnd.uniform(0.16, 0.24), rnd.uniform(5.0, 8.0), rnd.random() < 0.3)
                       for _ in range(22)]

    # -------------------------------------------------------------- Hilfsbilder
    @staticmethod
    def _chip(x, y, label, fill):
        spr = m.sprite(lambda im: o.hold_label(im, x, y, label, fill, size=52, role="stencil", pad=(26, 13)))
        spr.text = " ".join(label.split())
        return spr

    def _draw_wall(self, im):
        d = ImageDraw.Draw(im)
        d.polygon([P(x, y) for x, y in WALL], fill=o.rgb(WALL_FILL))
        d.line([P(x, y) for x, y in RIDGE], fill=o.rgb(GRIT), width=int(9 * o.S), joint="curve")
        for k, y0 in enumerate(range(1120, 1900, 96)):          # flache Baenke
            d.line([P(x, y0 + 4 * math.sin(x / 140 + k)) for x in range(30, 1051, 30)], fill=o.rgb(GRIT_IN, 110),
                   width=int(2 * o.S))
        for a, b in JOINTS:                                      # senkrechte Kluefte (Bloecke der Kante)
            d.line([P(*a), P(*b)], fill=o.rgb(GRIT_IN, 150), width=int(3 * o.S))
        for a, b in BREAKS:                                      # runde Breaks: helle Oberkante, dunkler Schatten darunter
            d.line([P(a[0], a[1] + 5), P(b[0], b[1] + 5)], fill=o.rgb("#0B0A08"), width=int(10 * o.S))
            d.line([P(*a), P(*b)], fill=o.rgb(GRIT, 235), width=int(7 * o.S))

    def _pattern_sprite(self, poly, kind, alpha, seed=6):
        S = o.S
        mask = Image.new("L", (W * S, H * S), 0)
        ImageDraw.Draw(mask).polygon([P(x, y) for x, y in poly], fill=255)
        pat = o._pattern_layer(mask.size, kind, GRIT, seed=seed)
        a = np.asarray(pat.getchannel("A"), np.float32) * (alpha / 255) * (np.asarray(mask, np.float32) / 255)
        lay = Image.new("RGBA", mask.size, o.rgb(GRIT))
        lay.putalpha(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)))
        small = lay.resize((W, H), Image.LANCZOS)
        bb = small.getbbox() or (0, 0, W, H)
        return m.Sprite(small.crop(bb), bb[0], bb[1])

    def _draw_leiste(self, im):
        d = ImageDraw.Draw(im)
        for name, t0_, b_, col in o.AGE:
            if t0_ >= 360:
                continue
            d.rectangle([P(self._lx(t0_), 628), P(self._lx(min(b_, 360)), 642)], fill=o.rgb(col, 230))

    @staticmethod
    def _lx(ma):
        return X0 + (930 - X0) * ma / 360.0

    def _draw_floor(self, im):
        d = ImageDraw.Draw(im)
        d.polygon([P(COAST_X - 10, FLOOR_Y), P(W, FLOOR_Y + 10), P(W, H), P(COAST_X - 10, H)], fill=o.rgb("#221F1A"))
        d.line([P(COAST_X - 10, FLOOR_Y), P(W, FLOOR_Y + 10)], fill=o.rgb(GRIT_IN, 200), width=int(3 * o.S))

    def _land_sprite(self):
        """Hochland (Granit- und Gneis-Signatur) und Ebene bis zur Kueste, eine Flaeche."""
        S = o.S
        lay = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        d.polygon([P(x, y) for x, y in LAND], fill=o.rgb("#202429"))
        mask = Image.new("L", lay.size, 0)
        ImageDraw.Draw(mask).polygon([P(x, y) for x, y in LAND], fill=255)
        for kind, x0, x1, seed in (("granite", 0, 190, 3), ("gneiss", 190, 420, 5)):
            pat = o._pattern_layer(lay.size, kind, C["slate"], seed=seed)
            a = np.asarray(pat.getchannel("A"), np.float32) * 0.75 * (np.asarray(mask, np.float32) / 255)
            box = np.zeros_like(a); box[:, int(x0 * S):int(x1 * S)] = 1
            box[int(1060 * S):, :] = 0                                     # Signatur nur im Hochland
            pl = Image.new("RGBA", lay.size, o.rgb(C["slate"]))
            pl.putalpha(Image.fromarray(np.clip(a * box, 0, 255).astype(np.uint8)))
            lay = Image.alpha_composite(lay, pl)
        d = ImageDraw.Draw(lay)
        d.line([P(x, y) for x, y in LAND[:12]], fill=o.rgb(C["slate"]), width=int(5 * o.S), joint="curve")
        small = lay.resize((W, H), Image.LANCZOS)
        bb = small.getbbox()
        return m.Sprite(small.crop(bb), bb[0], bb[1])

    def _delta_full(self):
        """Delta in voller Groesse: Sand mit Punkt-Signatur und schraegen Schuettungslagen (Foresets)."""
        S = o.S
        x0, y0 = COAST_X - 4, SEA_Y - 4
        w, h = W - x0, FLOOR_Y + 20 - y0
        lay = Image.new("RGBA", (w * S, h * S), o.rgb("#5E5240"))
        pat = o._pattern_layer(lay.size, "sandstone", GRIT, seed=11)
        a = np.asarray(pat.getchannel("A"), np.float32) * 0.8
        pl = Image.new("RGBA", lay.size, o.rgb(GRIT)); pl.putalpha(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)))
        lay = Image.alpha_composite(lay, pl)
        d = ImageDraw.Draw(lay)
        for k in range(24):                                         # Foresets parallel zur Front
            xa = COAST_X - 310 + k * 26
            d.line([((xa - x0) * S, (SEA_Y - y0) * S), ((xa + SLOPE * (FLOOR_Y - SEA_Y) - x0) * S, (FLOOR_Y - y0) * S)],
                   fill=o.rgb(GRIT, 150), width=int(2 * S))
        d.line([(0, (SEA_Y - y0) * S), (w * S, (SEA_Y - y0) * S)], fill=o.rgb(GRIT), width=int(4 * S))
        return m.Sprite(lay.resize((w, h), Image.LANCZOS), x0, y0)

    def ziffer(self, n):
        if n not in self.ziffern:
            spr = m.text_sprite(str(n), X0, 352, "display", 180, C["magnesia"])
            spr.text = None                                      # laufender Zaehler: Bewegung, keine Info
            self.ziffern[n] = spr
        return self.ziffern[n]

    # -------------------------------------------------------------- Welt
    def world(self, t):
        f = self.bg.copy()
        zeit = seg(t, T_S2, 0.5) * (1 - seg(t, T_HEBEN[1], 0.6))
        if zeit > 0:
            put(f, self.tints[o.age_of(ma_at(t))[1]], op=0.26 * zeit)
        lo = land_op(t)
        if lo > 0:                                                # Landschaft von damals (hinter der steigenden Wand)
            self._landschaft(f, t, lo)
        dy = wand_dy(t)
        if dy < 910:
            put(f, self.wall, dy=dy)
            if t >= T_S5:
                put(f, self.wall_pat, dy=dy, op=0.9)
        u = seilzug(seg(t, T_GEO, 0.5))
        if u > 0 and t < T_OUT + 0.4:
            self.geo.put(f, u, fade=1 - seg(t, T_OUT, 0.4))
        a = climber_alpha(t)
        if a > 0.01:
            put(f, self.climber.sprite(climber_pose(t), alpha=int(255 * a)), dy=dy if t < T_FAZ - 0.5 else 0)
        kl.chalk_puff(f, t, T_GRAB, H_R[0], H_R[1] - 4, seed=11)
        kl.chalk_puff(f, t, T_ZUG[1] - 0.05, H_TOP[0], H_TOP[1] - 4, seed=12, size=0.7)
        return f

    def _landschaft(self, f, t, op):
        put(f, self.water, op=op)
        put(f, self.floor, op=op)
        xf = delta_front(t)                                       # Delta bis zur aktuellen Front
        d = self.delta_full
        mk = Image.new("L", (d.w, d.h), 0)
        ImageDraw.Draw(mk).polygon([(0, 0), (xf - d.x, 0), (xf + SLOPE * (FLOOR_Y - SEA_Y) - d.x, FLOOR_Y - d.y + 8),
                                    (0, FLOOR_Y - d.y + 8)], fill=255)
        img = d.img.copy()
        img.putalpha(Image.fromarray((np.asarray(d.img.getchannel("A"), np.float32) * np.asarray(mk, np.float32) / 255
                                      ).astype(np.uint8)))
        put(f, m.Sprite(img, d.x, d.y), op=op)
        wl = [(x, SEA_Y + 5 * math.sin(x / 50 + t * 2.2)) for x in range(COAST_X, W + 1, 12)]
        lay = Image.new("RGBA", (W, 40), (0, 0, 0, 0))
        ImageDraw.Draw(lay).line([(x, y - SEA_Y + 20) for x, y in wl], fill=o.rgb(C["water"]), width=4)
        put(f, m.Sprite(lay, 0, SEA_Y - 20), op=op)
        put(f, self.land, op=op)
        g = seg(t, T_S4, 0.4) * (1 - seg(t, T_S5, 0.5))           # Payoff: Hochland leuchtet
        if g > 0:
            put(f, self.glow, op=g * (0.75 + 0.25 * math.sin(2 * math.pi * (t - T_S4) / 1.2)))
        rv = seg(t, T_S3 - 0.2, 0.6)                              # Fluss und Koerner (Zug 2)
        if rv > 0:
            put(f, self.river, op=op * rv)
            lay = Image.new("RGBA", (420, 520), (0, 0, 0, 0)); dr = ImageDraw.Draw(lay)
            for ph, sp, r, feld in self.grains:
                s = (ph + (t - T_S3) * sp) % 1.0
                x, y = _pathpos(RIVER, s)
                x += 4 * math.sin(s * 19 + ph * 6); y -= 6
                col = o.rgb("#E7B9A0" if feld else GRIT, int(255 * min(1.0, s * 6, (1 - s) * 6)))
                dr.ellipse([x - 280 - r, y - 820 - r, x - 280 + r, y - 820 + r], fill=col)
            put(f, m.Sprite(lay, 280, 820), op=op * rv)

    # -------------------------------------------------------------- Frames
    def frame(self, t):
        if t >= T_END:
            return self.outro.frame(t, T_END), 45
        f = self.world(t)
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
                    put(f, spr, op=min(1.0, v * 2) * fade, scale=lerp(0.7, 1.0, griff(v)) if v < 1 else 1.0)
            v = seilzug(seg(t, T_GUESS, EIN))
            if v > 0:
                pul = 1 + 0.03 * math.sin(2 * math.pi * (t - T_GUESS) / 0.9) if v >= 1 else 1.0
                put(f, self.guess, dx=lerp(-30, 0, v), op=v * fade, scale=pul)
            return f, 41
        if t < T_S3:                                              # Szene 2: Zeitreise zurueck
            put(f, self.rails[1]); self.rail.pop(f, t, 0, T_S2)
            out = 1 - seg(t, T_S3 - 0.2, 0.2)
            u = seg(t, T_S2, 0.45)
            if t < T_SEA:
                put(f, self.ziffer(int(round(ma_at(t)))), op=u)
            else:
                put(f, self.ma_final, op=out, scale=lerp(1.12, 1.0, seilzug(seg(t, T_SEA, 0.4))), anchor=(X0, 352))
            put(f, self.unit, op=min(u, out))
            self._marker(f, ma_at(t), min(u, out))
            return f, 42
        if t < T_S5:                                              # Szene 3: Fluss, Delta, Payoff
            put(f, self.rails[3] if t >= T_S4 else self.rails[2]); self.rail.pop(f, t, 1, T_S3)
            u = seilzug(seg(t, T_S3 + 0.05, EIN))
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
        put(f, self.rails[3])
        if t < T_FAZ:                                             # Szene 4: zurueck ins Heute (ohne Text)
            self._marker(f, ma_at(t), 1 - seg(t, T_S5 + T_ZURUECK + 0.1, 0.3))
            return f, 44
        u = seilzug(seg(t, T_FAZ + 0.05, EIN))                    # Szene 5: Fazit
        put(f, self.fazit, dx=lerp(-40, 0, u), op=u)
        return f, 46

    def _marker(self, f, ma, op):
        if op <= 0:
            return
        put(f, self.leiste, op=op)
        lay = Image.new("RGBA", (W, 50), (0, 0, 0, 0))
        dr = ImageDraw.Draw(lay); x = self._lx(ma)
        col = o.rgb(C["magnesia"])
        dr.polygon([(x - 11, 8), (x + 11, 8), (x, 24)], fill=col)
        dr.line([(x, 24), (x, 48)], fill=col, width=3)
        put(f, m.Sprite(lay, 0, 600), op=op)


# ------------------------------------------------------------------ Ton: Musik in E-Moll / G-Dur, 81 BPM
def sound_events(b):
    """Frage und Rate-Pause in E-Moll mit Countdown aus Toenen der E-Moll-Pentatonik, Zeitreise abwaerts (fallendes
    Arpeggio, je Periodengrenze ein Ton), Landschaft als Flaeche, Fluss und Delta bewegt (Koerner als Zupftoene),
    Steigerung auf H7, Payoff als Akkordschlag in E-Moll, Rueckkehr steigend, Fazit loest nach G-Dur auf, Klanglogo."""
    h1 = rk.Hook1(t_grab=T_GRAB, t_geo=T_GEO, t_out=T_OUT)
    b.hook1(h1, akkord=EM9, bassnote=40)
    b.musik([
        (T_Q - 0.1, T_CHIPS, EM9, 40, "ruhig"),
        (T_CHIPS, T_GUESS, CMAJ7, 36, "ruhig"),
        (T_GUESS, T_HOOK, AM7, 45, "flaeche"),
        (T_HOOK, T_S2, B7, 47, "flaeche"),
        (T_S2, T_S2 + 2.1, EM9, 40, "fallend"),
        (T_S2 + 2.1, T_SEA, CMAJ7, 36, "fallend"),
        (T_SEA, T_S3, EM9, 40, "flaeche"),
        (T_S3, T_S3 + 2.2, G_, 43, "bewegt"),
        (T_S3 + 2.2, T_RISE, D_, 38, "bewegt"),
        (T_RISE, T_S4 - 0.15, B7, 47, "flaeche"),
        (T_S4, T_S5, EM9, 40, "flaeche"),
        (T_S5, T_S5 + 1.4, AM7, 45, "steigend"),
        (T_S5 + 1.4, T_FAZ, DSUS4, 38, "steigend"),
        (T_FAZ, T_FAZ + 2.0, CMAJ7, 36, "ruhig"),
        (T_FAZ + 2.0, T_END, G_, 43, "ruhig"),
    ], bpm=81.0, gain=-12.0)
    b.musik([(T_END, DUR, G_, 43, "flaeche")], bpm=81.0, gain=-16.0)
    b.countdown(T_GUESS + 0.1, T_HOOK - 0.1, step=0.45, gain=-11.0, tonleiter=PENTA_E[:5])
    for k, note in enumerate((64, 67, 71)):
        b.ton("zupf", T_CHIPS + 0.3 * k, -15.0, "chips", m=note, dauer=0.8, pan=0.3 * (k - 1))
    b.synth("whoosh", T_S2, -20.0, "verblassen", dur=0.7, seed=4)
    for k, g in enumerate(GRENZEN):
        b.ton("zupf", t_bei_ma(g), -13.0, "zeitreise", m=[83, 81, 79, 76, 74, 71, 69][k], dauer=0.9, pan=0.3 * ((k % 3) - 1))
    b.ton("schwelle", T_SEA - 0.8, -12.0, "ankunft", akkord=EM9, dauer=0.8)
    b.ton("zupf", T_SEA, -10.0, "ankunft", m=64, dauer=1.4)
    for k in range(9):                                          # Koerner im Fluss: leise Toene der Pentatonik
        b.ton("zupf", T_S3 + 0.3 + 0.45 * k, -18.0, "koerner", m=PENTA_E[(k * 3) % 7] + 12, dauer=0.6, pan=0.3 * ((k % 3) - 1))
    for k in range(6):                                          # Delta: je Schuettungslage ein steigender Ton
        b.ton("zupf", T_DELTA[0] + 0.7 * k + 0.2, -16.0, "delta", m=PENTA_E[k], dauer=0.8)
    b.ton("schwelle", T_RISE, -8.0, "steigerung", akkord=B7, dauer=T_S4 - 0.15 - T_RISE)
    b.klang("sub_hit", T_S4 - 0.01, -11.0, "payoff-einschlag", f0=78.0, f1=36.0)
    b.ton("akzent", T_S4, -4.0, "payoff", akkord=EM9, bassnote=40)
    b.ton("zupf", T_S4 + 0.12, -10.0, "chip", m=83, dauer=1.0)
    b.ton("schwelle", T_HEBEN[0], -11.0, "heben", akkord=DSUS4, dauer=T_HEBEN[1] - T_HEBEN[0])
    b.klang("thud", T_HEBEN[1], -14.0, "angekommen", seed=4)
    b.klang("chalk_slap", T_ZUG[1] - 0.05, -12.0, "griff", seed=2)
    b.ton("zupf", T_ZUG[1], -14.0, "griff", m=79, dauer=0.9)
    b.klanglogo(T_END + 0.3, tonika=67, gain=-13.0)        # leiser: Payoff bleibt der Hoehepunkt
    b.ton("zupf", T_END + 1.3, -17.0, "herz", m=74, dauer=1.2)  # noqa


cover_t = round(T_CHIPS + 1.0, 2)
META = dict(
    slug="2026-11-10_rewind-02", dur_range=[27.0, 38.0], payoff_t=T_S4, abspann_ab=T_END,
    title="GeoCrimps r010 REWIND #02 (Quiz), Fassung 1", ablauf="quiz",
    hook1_bis=T_OUT, hook_ab=T_Q, hook_bis=T_HOOK, weitere_fragen=[[T_GUESS, T_HOOK]], cover_t=cover_t,
    on_screen=["REWIND", "GRITSTONE EDGE:", "WHERE DID ITS SAND COME FROM?", "A DESERT", "B REEF", "C HIGHLAND",
               "YOUR GUESS?", "≈320", "MILLION YEARS AGO", "RIVERS CARRIED IT SOUTH.", "A NORTHERN HIGHLAND.",
               "THIS EDGE IS IMPORTED HIGHLAND.", rk.Outro.CTA],
    labels=[],
    verdauen=["A NORTHERN HIGHLAND.", "THIS EDGE IS IMPORTED HIGHLAND."],
    qc_times=[0.0, T_GRAB, T_GEO, 1.1, 1.6, cover_t, round(T_GUESS + 1.2, 2), round(T_S2 + 1.4, 2),
              round(T_SEA - 0.3, 2), round(T_S3 - 0.2, 2), round(T_S3 + 2.0, 2), round(T_S4 - 0.3, 2),
              round(T_S4 + 1.5, 2), round(T_S5 + 1.4, 2), round(T_END - 0.2, 2), round(T_END + 2.0, 2)],
    marks=[(0, "Hook 1"), (T_GRAB, "Griff"), (T_GEO, "x GEOLOGY"), (T_Q, "Hook 2"), (T_CHIPS, "Chips"),
           (T_GUESS, "Rate-Pause"), (T_S2, "Zeitreise"), (T_SEA, "320 Ma"), (T_S3, "Fluss+Delta"), (T_S4, "PAYOFF"),
           (T_S5, "zurueck"), (T_FAZ, "Fazit"), (T_END, "Abspann")])

if __name__ == "__main__":
    if "--reach" in sys.argv:
        print(reach_check()); sys.exit(0)
    rk.run(Reel, sound_events, META)
