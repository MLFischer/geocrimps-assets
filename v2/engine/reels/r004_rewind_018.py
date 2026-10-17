#!/usr/bin/env python3
"""Reel 004 -- REWIND #01: "What was this limestone once?" (Faktenbasis: Post #018, Zugspitze war ein Riff), Ablauf "quiz".

Fassung 1 vom 17.10.2026 nach PRODUKTION.md (Stand 16.10.2026), Vorlage r003 Fassung 6: Hook 1 + Hook 2 mit klarer
Frage, Lesezeit, ruhiges Tempo, Musik statt Klicks, Abspann mit LIKE & FOLLOW.
Hook 1 0-1,45 s: GEOCRIMPS + CLIMBING ab Frame 0, ein Kletterer greift eine Leiste in der Gipfelwand (Kreidewolke),
"x GEOLOGY" schlaegt ein und die Wand klappt in ihre Kalk-Signatur auf (Ziegelmuster, Baenke); verraet das Riff nicht.
Hook 2 ab 1,8 s: Formatlabel REWIND, Kontextzeile "GERMANY'S HIGHEST PEAK:" (Kalkfarbe) ueber "WHAT WAS THIS LIMESTONE
ONCE?"; ab 4,4 s drei Griff-Chips A DESERT / B REEF / C VOLCANO, ab 5,6 s "YOUR GUESS?" mit Countdown aus Toenen (2 s).
Zug 1 (Zeitreise zurueck): der Kletterer verblasst, der Zaehler laeuft von 0 auf 235 Millionen Jahre, die Altersfarbe
wechselt (Zeitleiste nach outcrop.AGE), die Wand sinkt, das Meer steigt; Ziel "235-240 / MILLION YEARS AGO".
Zug 2 (Ursprung): unter Wasser wachsen Korallen, Schwaemme und Algen auf der Plattform: "CORALS, SPONGES, ALGAE BUILT IT."
Payoff: Chip B leuchtet, "A REEF." (Akkordschlag in C-Dur). Folge (zurueck ins Heute): Kalk waechst um das Riff bis unter
den Meeresspiegel (aus dem Riff wird Gestein, die Riffbauer bleiben als Fossilien), das Meer laeuft ab, Kalkpaket und
Wand steigen nach oben: "THE ALPS LIFTED IT." Fazit: der Kletterer ist zurueck und zieht einen Zug, im Fels
schimmern Fossilien: "YOU'RE CLIMBING AN ANCIENT REEF." Abspann mit LIKE & FOLLOW.
Fakten (v2/faktenbasis/018/sources.md): Wettersteinkalk, triassischer Riff- und Plattformkalk der Tethys; etwa 235-240
Mio. Jahre (spaetes Ladin bis fruehes Karn); Korallen, Schwaemme und Algen bauten die Plattform; die alpine Kollision
hob den alten Meeresboden in den Gipfel. Die Zugspitze ist der hoechste Berg Deutschlands.
Bildmittel (Abwechslungsregel): Uebergang Zeitreise mit Zaehler und Altersfarbe (neu) | Enthuellung Meer und wachsendes
Riff (neu) | Payoff Chip leuchtet, Antwort gross | Musik A-Moll nach C-Dur, 84 BPM (r003: G-Dur, 80 BPM).
Aufruf:  python3 r004_rewind_018.py --out ../../../reels --qc <Ordner>   (--stills 0,4.8 fuer Einzelbilder)
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
EIN = 0.5                          # Einblenden von Texten
T_GRAB, T_GEO, T_OUT = 0.40, 0.72, 1.45                       # Hook 1: Griff, "x GEOLOGY", Uebergang in die Kopfzeile
T_Q = 1.80                         # Hook 2: Formatlabel, Kontextzeile und Frage
T_CHIPS = T_Q + 2.6                # drei Griff-Chips (je 0,3 s versetzt)
T_GUESS = T_CHIPS + 1.2            # "YOUR GUESS?" + Countdown
T_HOOK = T_GUESS + 2.0             # Ende der Rate-Pause: Frage, Chips und Kopfzeile blenden aus
T_S2 = T_HOOK + 0.5                # Zug 1 nach einer Atempause: Zeitreise zurueck
T_SEA = T_S2 + 3.6                 # angekommen: 235-240 Mio. Jahre, unter Wasser
T_S3 = T_SEA + 2.8                 # Zug 2: das Riff waechst
T_RISE = T_S3 + 3.1                # Akkord schwillt an, 0,15 s Stille, dann der Payoff
T_S4 = T_RISE + 1.0                # Payoff: Chip B leuchtet, "A REEF."
T_S5 = T_S4 + 2.7                  # Folge: zurueck ins Heute
T_FAZ = T_S5 + 3.2                 # Fazit: der Kletterer ist zurueck
T_END = T_FAZ + 3.9                # Abspann
DUR = T_END + rk.Outro.DUR
MA_ZIEL = 235.0                    # Zaehler-Ziel; danach steht "235-240" (sources.md #018, Kalibrierung)
T_ZAEHL0, T_ZAEHL = T_S2 + 0.3, 3.0                           # Zaehler laeuft 3 s
T_WAND_AB = (T_S2 + 0.6, T_SEA - 0.4)                          # Wand sinkt
T_MEER_AUF = (T_S2 + 1.2, T_SEA - 0.2)                         # Meer steigt
T_ZURUECK = 1.4                                                # Zaehler laeuft in der Folge zurueck auf 0
T_DECKEN = (T_S5 + 0.1, T_S5 + 1.1)                            # Kalk waechst um das Riff (aus dem Riff wird Gestein)
T_MEER_AB = (T_S5 + 0.6, T_S5 + 1.5)                           # Meer laeuft ab
T_HEBEN = (T_S5 + 1.0, T_S5 + 2.6)                             # Wand hebt sich (alpine Kollision)
T_ZUG = (T_FAZ + 0.6, T_FAZ + 1.5)                             # Fazit: Kletterer zieht einen Zug

# ------------------------------------------------------------------ Szene: Gipfelwand im Wettersteinkalk
LIME, LIME_IN, WALL_FILL = "#D9D3C4", "#8F897C", "#16191D"     # Kalk: Kante hell, Baenke gedaempft; Wandflaeche
SEA_Y, PLAT_Y = 905, 1385          # Meeresspiegel und Plattform (Meeresboden) in der Tiefe der Zeit
STEIN_H = 360                      # Kalkpaket ueber der Plattform (deckt die hoechste Koralle, Spitze ~1010)
RIDGE = [(30, 1075), (130, 1040), (230, 1056), (330, 1000), (420, 1018), (515, 978), (600, 996), (690, 960),
         (780, 1004), (870, 1028), (960, 1068), (1050, 1060)]
WALL = RIDGE + [(1050, H + 10), (30, H + 10)]
H_L, H_R = (640, 1150), (772, 1128)                            # Haende: zwei Leisten
H_LF, H_RF = (652, 1452), (752, 1440)                          # Fuesse
H_TOP = (698, 1066)                                            # Fazit: hoeherer Griff fuer die linke Hand (erreichbar mit
                                                               # beiden Fuessen auf den Tritten, Climber.joints geprueft)
HOLDS = [H_L, H_R, H_LF, H_RF, H_TOP, (560, 1260), (835, 1270), (600, 1060), (870, 1160)]

BACK = dict(sw=22, hw=13, eb=(-1, 1), kb=(1, -1))             # Rueckenansicht: Ellbogen und Knie nach aussen
POSE_START = dict(BACK, hip=(692, 1382), lean=0, lh=H_L, rh=(760, 1255), lf=(662, 1530), rf=(744, 1520))
POSE_GRAB = dict(BACK, hip=(702, 1330), lean=3, lh=H_L, rh=H_R, lf=H_LF, rf=H_RF)
POSE_SWING = dict(POSE_GRAB, hip=(708, 1322), lean=6)
POSE_REACH = dict(BACK, hip=(712, 1292), lean=-4, lh=H_TOP, rh=H_R, lf=H_LF, rf=H_RF)   # Fuesse bleiben auf den Tritten

# Tonart A-Moll / C-Dur (MIDI), Bass eine Oktave tiefer
AM9, FMAJ7, DM7, E_, C_, G_, GSUS4 = ([57, 60, 64, 67, 71], [53, 57, 60, 64], [53, 57, 60, 62], [52, 56, 59, 64],
                                      [55, 60, 64, 67], [55, 59, 62, 67], [55, 60, 62, 67])
PENTA_A = [69, 72, 74, 76, 79, 81]                             # A-Moll-Pentatonik (Countdown, Zeitreise)
PENTA_C = [72, 74, 76, 79, 81, 84]                             # C-Dur-Pentatonik (Riff waechst)
GRENZEN = [2.58, 23.04, 66.0, 143.1, 201.4]                    # Periodengrenzen (outcrop.AGE) fuer Toene der Zeitreise


def ma_at(t):
    """Alter in Mio. Jahren, das der Zaehler zum Zeitpunkt t zeigt (0 = heute)."""
    if t < T_S5:
        u = seg(t, T_ZAEHL0, T_ZAEHL)
        return MA_ZIEL * (0.5 - 0.5 * math.cos(math.pi * u))
    u = seg(t, T_S5 + 0.1, T_ZURUECK)
    return MA_ZIEL * (1 - (0.5 - 0.5 * math.cos(math.pi * u)))


def t_bei_ma(ma):
    """Zeitpunkt, an dem der Zaehler auf dem Hinweg ma erreicht (fuer die Toene an den Periodengrenzen)."""
    return T_ZAEHL0 + T_ZAEHL * math.acos(1 - 2 * ma / MA_ZIEL) / math.pi


def ease(u):
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, u)))


def wand_dy(t):
    """Versatz der Wand nach unten: sinkt in der Zeitreise, hebt sich in der Folge wieder."""
    if t < T_S5:
        return 820 * ease(seg(t, T_WAND_AB[0], T_WAND_AB[1] - T_WAND_AB[0]))
    return 820 * (1 - ease(seg(t, T_HEBEN[0], T_HEBEN[1] - T_HEBEN[0])))


def hebung(t):
    """0..1: alpine Hebung in der Folge (Kalkpaket und Wand steigen)."""
    return ease(seg(t, T_HEBEN[0], T_HEBEN[1] - T_HEBEN[0]))


def meer_y(t):
    """Meeresspiegel (None = kein Meer im Bild)."""
    if t < T_MEER_AUF[0] or t >= T_MEER_AB[1]:
        return None
    if t < T_S5:
        return lerp(H + 40, SEA_Y, ease(seg(t, T_MEER_AUF[0], T_MEER_AUF[1] - T_MEER_AUF[0])))
    return lerp(SEA_Y, H + 40, ease(seg(t, T_MEER_AB[0], T_MEER_AB[1] - T_MEER_AB[0])))


def climber_pose(t):
    """Hook 1: vom Wandfuss an die Leiste (Frame 0 schon in Bewegung), Griff bei T_GRAB; haengt durch Hook 2 und die
    Rate-Pause; in der Zeitreise verblasst er (climber_alpha); im Fazit ist er zurueck und zieht an den hoeheren Griff."""
    if t < T_GRAB:
        return kl.lerp_pose(POSE_START, POSE_SWING, seilzug(seg(t, 0.0, T_GRAB)))
    if t < T_FAZ:
        u = seg(t, T_GRAB, 0.3)
        p = kl.lerp_pose(POSE_SWING, POSE_GRAB, 0.5 - 0.5 * math.cos(math.pi * u))
        if u >= 1:
            w = math.sin(2 * math.pi * (t - T_GRAB - 0.3) / 2.6)
            p = dict(p, hip=(p["hip"][0] + 4 * w, p["hip"][1] + 1.5 * abs(w)), lean=p["lean"] + 1.5 * w)
        return p
    p = kl.lerp_pose(POSE_GRAB, POSE_REACH, seilzug(seg(t, T_ZUG[0], T_ZUG[1] - T_ZUG[0])))
    b = math.sin(2 * math.pi * (t - T_FAZ) / 2.8)               # ruhiges Atmen
    return dict(p, hip=(p["hip"][0], p["hip"][1] + 1.5 * b), lean=p["lean"] + 0.6 * b)


def climber_alpha(t):
    if t < T_S2:
        return 1.0
    if t < T_FAZ - 0.4:
        return 1.0 - seg(t, T_S2, 0.6)
    return seg(t, T_FAZ - 0.4, 0.5)


# ------------------------------------------------------------------ Riff (Zug 2): Korallen, Schwaemme, Algen
def _koralle(rnd, x, y, h):
    """Verzweigte Koralle als Liste von Segmenten relativ zur Basis (x, y), Hoehe etwa h."""
    segs = []
    def ast(px, py, ang, L, d):
        if d == 0 or L < 6:
            return
        qx, qy = px + L * math.sin(ang), py - L * math.cos(ang)
        segs.append(((px, py), (qx, qy), d))
        for da in (-0.45, 0.42):
            ast(qx, qy, ang + da + rnd.uniform(-0.15, 0.15), L * rnd.uniform(0.62, 0.78), d - 1)
    ast(x, y, rnd.uniform(-0.15, 0.15), h * 0.38, 4)
    return segs


def _schwamm(x, y, h, w):
    """Vasenfoermiger Schwamm (Umriss) auf der Basis (x, y)."""
    return [(x - w * 0.25, y), (x - w * 0.55, y - h * 0.55), (x - w * 0.5, y - h), (x + w * 0.5, y - h),
            (x + w * 0.55, y - h * 0.55), (x + w * 0.25, y)]


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
        kick = "GERMANY'S HIGHEST PEAK:"
        self.hook_kick = m.text_sprite(kick, X0, rk.HOOK_Y, "display", m.fit(kick, "display", 96), LIME)
        self.hook, y_q = m.lines_sprite(["WHAT WAS THIS", "LIMESTONE ONCE?"], rk.HOOK_Y + 112, size=136)
        self.y_chips = int(y_q) + 26
        labels = ["A  DESERT", "B  REEF", "C  VOLCANO"]
        self.chips, self.chips_hell, x = [], [], X0
        for lab in labels:
            wch = o.text_width(lab, "stencil", 52) + 52
            self.chips.append(self._chip(x, self.y_chips, lab, C["magnesia"]))
            self.chips_hell.append(self._chip(x, self.y_chips, lab, C["bio"]))
            x += wch + 24
        self.chips_matt = [m.Sprite(c.img, c.x, c.y) for c in self.chips]   # abgeblendet: nicht als Info gemessen
        self.guess = m.text_sprite("YOUR GUESS?", X0, self.y_chips + 104, "text_b", 54, C["magnesia"])
        self.unit = m.text_sprite("MILLION YEARS AGO", X0, 548, "stencil", 44, C["magnesia"], tracking=0.1)
        self.ma_final = m.text_sprite("235–240", X0, 352, "display", 180, C["magnesia"])
        self.ziffern = {}
        self.text2, _ = m.lines_sprite(["CORALS, SPONGES,", "ALGAE BUILT IT."], 352, role="display_xb", size=118)
        self.answer, _ = m.lines_sprite(["A REEF."], 352, size=200)
        self.text3, _ = m.lines_sprite(["THE ALPS", "LIFTED IT."], 352, role="display_xb", size=118)
        self.fazit, _ = m.lines_sprite(["YOU'RE CLIMBING", "AN ANCIENT REEF."], 352, size=136)
        # ---- Hintergrund, Wand, Kalk-Signatur, Fossilien
        self.bg = m.background(lambda im: o.contour_field(im, 820, 1720, n=9, r0=140, step=64, alpha=80))
        self.wall = m.sprite(self._draw_wall)
        beds = [[(x, y0 + 0.07 * (x - 30) + 5 * math.sin(x / 120 + k)) for x in range(30, 1051, 30)]
                for k, y0 in enumerate(range(1090, 1900, 92))]
        self.beds = beds
        self.geo = kl.GeoReveal(WALL, "limestone", H_R[0], H_R[1], pat_alpha=90, beds=beds, seed=6)
        self.wall_pat = self._pattern_sprite(WALL, "limestone", 70, beds)
        self.fossils = m.sprite(self._draw_fossils)
        # ---- Zeit: Farbflaechen je Periode, Zeitleiste
        self.tints = {}                                          # Altersfarbe: Verlauf im Himmel, unten durchsichtig
        verlauf = Image.fromarray((np.clip(1 - np.arange(1060) / 1060.0, 0, 1)[:, None] ** 1.4 * 255
                                   * np.ones((1, W))).astype(np.uint8))
        for name, t0_, b_, col in o.AGE:
            lay = Image.new("RGBA", (W, 1060), o.rgb(col)); lay.putalpha(verlauf)
            self.tints[col] = m.Sprite(lay, 0, 0)
        self.leiste = m.sprite(self._draw_leiste)
        # ---- Meer und Plattform
        self.water = m.Sprite(Image.new("RGBA", (W, H + 900), o.rgb("#0F3B66")), 0, 0)
        self.rays = m.sprite(self._draw_rays)
        self.platform = m.sprite(self._draw_platform)
        self.platform_fuss = m.Sprite(Image.new("RGBA", (W, 900), o.rgb("#2B2620")), 0, H)   # deckt unten, wenn sie steigt
        self.stein = self._stein_bild()
        rnd = random.Random(18)
        self.reef = []
        slots = [(150, "a"), (215, "k"), (290, "s"), (360, "k"), (430, "a"), (500, "k"), (575, "s"), (640, "k"), (705, "a"),
                 (770, "k"), (840, "s"), (905, "k"), (965, "a")]
        for k, (x0, kind) in enumerate(slots):
            ts = T_S3 + 0.15 + 0.2 * k + rnd.uniform(0, 0.1)
            if kind == "k":
                self.reef.append(("k", ts, _koralle(rnd, x0, PLAT_Y + 4, rnd.uniform(220, 320))))
            elif kind == "s":
                self.reef.append(("s", ts, (x0, PLAT_Y + 4, rnd.uniform(150, 200), rnd.uniform(70, 92))))
            else:
                self.reef.append(("a", ts, (x0, PLAT_Y + 4, rnd.uniform(130, 190), rnd.uniform(0, 6))))

    # -------------------------------------------------------------- Hilfsbilder
    @staticmethod
    def _chip(x, y, label, fill):
        spr = m.sprite(lambda im: o.hold_label(im, x, y, label, fill, size=52, role="stencil", pad=(26, 13)))
        spr.text = " ".join(label.split())
        return spr

    def _draw_wall(self, im):
        d = ImageDraw.Draw(im)
        d.polygon([P(x, y) for x, y in WALL], fill=o.rgb(WALL_FILL))
        d.line([P(x, y) for x, y in RIDGE], fill=o.rgb(LIME), width=int(7 * o.S), joint="curve")
        for k, y0 in enumerate(range(1090, 1900, 92)):          # Baenke (flach, leicht geneigt)
            pts = [P(x, y0 + 0.07 * (x - 30) + 5 * math.sin(x / 120 + k)) for x in range(30, 1051, 30)]
            d.line(pts, fill=o.rgb(LIME_IN, 120), width=int(2 * o.S))
        for hx, hy in HOLDS:                                     # Leisten und Tritte
            d.rounded_rectangle([P(hx - 17, hy - 6), P(hx + 17, hy + 7)], radius=5 * o.S, fill=o.rgb(LIME, 225))

    def _pattern_sprite(self, poly, kind, alpha, beds):
        S = o.S
        mask = Image.new("L", (W * S, H * S), 0)
        ImageDraw.Draw(mask).polygon([P(x, y) for x, y in poly], fill=255)
        pat = o._pattern_layer(mask.size, kind, LIME, seed=6)
        a = np.asarray(pat.getchannel("A"), np.float32) * (alpha / 255) * (np.asarray(mask, np.float32) / 255)
        lay = Image.new("RGBA", mask.size, o.rgb(LIME))
        lay.putalpha(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)))
        small = lay.resize((W, H), Image.LANCZOS)
        bb = small.getbbox() or (0, 0, W, H)
        return m.Sprite(small.crop(bb), bb[0], bb[1])

    def _draw_fossils(self, im):
        """Fossilien im Fels (Fazit): dieselben Riffbauer wie im Riff (Korallenaeste, Kalkschwaemme, Kalkalgen) als feine
        Umrisse, nur angedeutet. Keine Muscheln: nur, was Text und Quellen tragen (Nittel 2006)."""
        d = ImageDraw.Draw(im); rnd = random.Random(40); col = o.rgb(C["heat"], 150)
        for x0, y0 in ((180, 1150), (330, 1300), (470, 1120), (880, 1330), (950, 1150), (560, 1390), (240, 1420)):
            for (a, b, dd) in _koralle(rnd, x0, y0, rnd.uniform(70, 100)):
                d.line([P(*a), P(*b)], fill=col, width=int(max(1.5, dd * 0.9) * o.S))
        for x0, y0 in ((410, 1262), (845, 1232), (300, 1200)):     # Kalkschwaemme (Becherform wie im Riff)
            poly = [P(x, y) for x, y in _schwamm(x0, y0, rnd.uniform(44, 56), rnd.uniform(22, 28))]
            d.line(poly + [poly[0]], fill=o.rgb(C["ice"], 150), width=int(2 * o.S))
        for x0, y0 in ((140, 1330), (1000, 1300), (520, 1210)):    # Kalkalgen (Wedel)
            for j in range(2):
                d.line([P(x0 + 7 * j - 3 + 5 * math.sin(yy / 8.0 + j), y0 - yy) for yy in range(0, 46, 3)],
                       fill=o.rgb(C["bio"], 140), width=int(2 * o.S))

    def _draw_leiste(self, im):
        """Zeitleiste 0-252 Mio. Jahre (links heute), Farben nach outcrop.AGE."""
        d = ImageDraw.Draw(im)
        for name, t0_, b_, col in o.AGE:
            if t0_ >= 252:
                continue
            x0, x1 = self._lx(t0_), self._lx(min(b_, 252))
            d.rectangle([P(x0, 628), P(x1, 642)], fill=o.rgb(col, 230))

    @staticmethod
    def _lx(ma):
        return X0 + (930 - X0) * ma / 252.0

    def _draw_rays(self, im):
        d = ImageDraw.Draw(im)
        for k, x in enumerate((160, 380, 600, 820)):
            d.polygon([P(x, SEA_Y), P(x + 70, SEA_Y), P(x + 220 + 30 * k, PLAT_Y), P(x + 120 + 30 * k, PLAT_Y)],
                      fill=o.rgb(C["ice"], 18))

    def _draw_platform(self, im):
        d = ImageDraw.Draw(im)
        top = [(x, PLAT_Y + 6 * math.sin(x / 90)) for x in range(0, W + 1, 30)]
        d.polygon([P(*p) for p in top] + [P(W, H), P(0, H)], fill=o.rgb("#2B2620"))
        d.line([P(*p) for p in top], fill=o.rgb(LIME, 200), width=int(4 * o.S))
        for k in range(1, 6):
            d.line([P(x, y + 34 * k) for x, y in top], fill=o.rgb(LIME_IN, 90), width=int(2 * o.S))

    def ziffer(self, n):
        if n not in self.ziffern:
            spr = m.text_sprite(str(n), X0, 352, "display", 180, C["magnesia"])
            spr.text = None                                      # laufender Zaehler: Bewegung, keine Info (Ziel steht als Text)
            self.ziffern[n] = spr
        return self.ziffern[n]

    # -------------------------------------------------------------- Welt
    def world(self, t):
        f = self.bg.copy()
        ma = ma_at(t)
        zeit = seg(t, T_S2, 0.5) * (1 - seg(t, T_HEBEN[1], 0.6))  # Altersfarbe nur auf der Zeitreise
        if zeit > 0:
            put(f, self.tints[o.age_of(ma)[1]], op=0.26 * zeit)
        dy = wand_dy(t)
        if dy < 900:                                              # Gipfelwand
            put(f, self.wall, dy=dy)
            if t >= T_S5:                                         # zurueck: Kalk mit Fossilien
                put(f, self.wall_pat, dy=dy, op=0.9)
                put(f, self.fossils, dy=dy, op=0.55 * seg(t, T_HEBEN[1] - 0.4, 0.8))
        u = seilzug(seg(t, T_GEO, 0.5))                           # Hook 1: Wand klappt in ihre Kalk-Signatur auf
        if u > 0 and t < T_OUT + 0.4:
            self.geo.put(f, u, fade=1 - seg(t, T_OUT, 0.4))
        y = meer_y(t)                                             # Meer: Wasserkoerper ueber der sinkenden Wand
        ablauf = t >= T_MEER_AB[0]                                # beim Ablaufen liegt der Spiegel hinter dem Gestein
        if y is not None:
            put(f, self.water, dy=y, op=0.62)
            if ablauf:
                self._spiegel(f, t, y)
        tiefe = seg(t, T_SEA - 1.0, 0.8) * (1 - seg(t, T_HEBEN[0] + 0.15, 0.55))   # Plattform und Riff in der Tiefe der Zeit
        boden = PLAT_Y
        if tiefe > 0:
            lift = 60 * ease(seg(t, T_S3, T_RISE - T_S3)) + 820 * hebung(t)   # Plattform waechst; dann steigt alles mit der Wand
            put(f, self.platform, dy=-lift, op=tiefe)
            put(f, self.platform_fuss, dy=-lift, op=tiefe)
            boden = self._kalk(f, t, tiefe, PLAT_Y - lift)
            self._riff(f, t, tiefe, PLAT_Y - lift)
        if y is not None:
            put(f, self.rays, dy=y - SEA_Y, op=0.9 * seg(t, T_SEA - 0.6, 0.6) * (1 - seg(t, T_MEER_AB[0], 0.4)))
            if not ablauf:
                self._spiegel(f, t, y)
                self._blasen(f, t, y, boden)
        a = climber_alpha(t)                                      # Kletterer
        if a > 0.01:
            pose = climber_pose(t)
            cdy = dy if t < T_FAZ - 0.5 else 0
            put(f, self.climber.sprite(pose, alpha=int(255 * a)), dy=cdy)
        kl.chalk_puff(f, t, T_GRAB, H_R[0], H_R[1] - 4, seed=11)
        kl.chalk_puff(f, t, T_ZUG[1] - 0.05, H_TOP[0], H_TOP[1] - 4, seed=12, size=0.7)
        return f

    def _riff(self, f, t, op_aussen, base_y):
        """Riff auf eigener Ebene (Band ueber der Plattform), damit Deckkraft und Fossil-Daempfung wirken."""
        y_off = int(round(base_y)) - 400
        lay = Image.new("RGBA", (W, 440), (0, 0, 0, 0))
        dr = ImageDraw.Draw(lay)
        stein = ease(seg(t, T_DECKEN[0], T_DECKEN[1] - T_DECKEN[0]))
        fill_op = 1 - stein                                       # Schwamm-Fuellung verschwindet im Gestein
        op = 1 - 0.55 * stein                                     # Riffbauer bleiben als gedaempfte Fossilien
        shift = base_y - PLAT_Y - y_off                           # Riff steht auf der wachsenden Plattform
        for kind, ts, data in self.reef:
            g = ease(seg(t, ts, 1.1))
            if g <= 0:
                continue
            if kind == "k":
                bx, by = data[0][0]
                for (a, b, d) in data:
                    ax, ay = bx + (a[0] - bx) * g, by + (a[1] - by) * g + shift
                    cx_, cy_ = bx + (b[0] - bx) * g, by + (b[1] - by) * g + shift
                    dr.line([(ax, ay), (cx_, cy_)], fill=o.rgb(C["heat"], int(240 * op)), width=max(3, int(d * 2.2)))
            elif kind == "s":
                x0, y0, h, w = data
                poly = [(x, y0 + (yy - y0) * g + shift) for x, yy in _schwamm(x0, y0, h, w)]
                dr.polygon(poly, outline=o.rgb(C["ice"], int(230 * op)), fill=o.rgb("#21424F", int(200 * fill_op)))
                dr.line(poly + [poly[0]], fill=o.rgb(C["ice"], int(240 * op)), width=5)
            else:
                x0, y0, h, ph = data
                for j in range(3):
                    pts = [(x0 + 12 * j - 12 + 9 * math.sin(yy / 22 + t * 1.6 + ph + j), y0 - yy * g + shift)
                           for yy in range(0, int(h), 8)]
                    if len(pts) > 1:
                        dr.line(pts, fill=o.rgb(C["bio"], int(235 * op)), width=5)
        put(f, m.Sprite(lay, 0, y_off), op=op_aussen)

    def _stein_bild(self):
        """Kalkpaket (Wandflaeche mit Kalk-Signatur und Baenken), STEIN_H ueber der Plattform plus 80 px darunter."""
        S, h = o.S, STEIN_H + 80
        lay = Image.new("RGBA", (W * S, h * S), o.rgb(WALL_FILL))
        pat = o._pattern_layer(lay.size, "limestone", LIME, seed=7)
        a = np.asarray(pat.getchannel("A"), np.float32) * (70 / 255)
        pl = Image.new("RGBA", lay.size, o.rgb(LIME))
        pl.putalpha(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)))
        lay = Image.alpha_composite(lay, pl)
        d = ImageDraw.Draw(lay)
        for k in range(1, 9):                                     # Baenke, flach wie in der Wand
            y0 = STEIN_H - 44 * k
            d.line([P(x, y0 + 4 * math.sin(x / 120 + k)) for x in range(0, W + 1, 30)], fill=o.rgb(LIME_IN, 120),
                   width=int(2 * S))
        return lay.resize((W, h), Image.LANCZOS)

    def _kalk(self, f, t, op, base_y):
        """Aus dem Riff wird Gestein: Kalk waechst um die Riffbauer bis knapp unter den Meeresspiegel (Plattform).
        Gibt die Oberkante zurueck (Blasen steigen erst darueber auf)."""
        u = ease(seg(t, T_DECKEN[0], T_DECKEN[1] - T_DECKEN[0]))
        if u <= 0:
            return base_y
        hoehe = max(1, int(STEIN_H * u))
        top = int(round(base_y)) - hoehe
        stueck = self.stein.crop((0, STEIN_H - hoehe, W, STEIN_H + 80))
        ImageDraw.Draw(stueck).line([(0, 1), (W, 1)], fill=o.rgb(LIME, 210), width=3)   # Oberkante
        put(f, m.Sprite(stueck, 0, top), op=op)
        return top

    def _spiegel(self, f, t, y):
        pts = [(x, y + 7 * math.sin(x / 55 + t * 2.4)) for x in range(0, W + 1, 12)]
        ImageDraw.Draw(f).line(pts, fill=o.rgb(C["water"]), width=4)

    def _blasen(self, f, t, y_meer, boden=PLAT_Y):
        top = int(y_meer)
        if PLAT_Y - top < 40:
            return
        lay = Image.new("RGBA", (W, PLAT_Y - top + 10), (0, 0, 0, 0))
        dr = ImageDraw.Draw(lay)
        rnd = random.Random(5)
        for k in range(22):
            x = rnd.uniform(60, 1020); sp = rnd.uniform(40, 90); ph = rnd.uniform(0, 30)
            yy = PLAT_Y - ((t * sp + ph * 20) % (PLAT_Y - y_meer - 20))
            r = rnd.uniform(2, 4.5)
            if y_meer + 10 < yy < boden - 8:
                dr.ellipse([x - r, yy - top - r, x + r, yy - top + r], outline=o.rgb(C["ice"], 130), width=2)
        put(f, m.Sprite(lay, 0, top))

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
                v = seg(t, T_CHIPS + 0.3 * k, 0.4)
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
            u = seg(t, T_S2, 0.4)
            if t < T_SEA:
                put(f, self.ziffer(int(round(ma_at(t)))), op=u)
            else:
                put(f, self.ma_final, op=out, scale=lerp(1.12, 1.0, seilzug(seg(t, T_SEA, 0.35))), anchor=(X0, 352))
            put(f, self.unit, op=min(u, out))
            self._marker(f, ma_at(t), min(u, out))
            return f, 42
        if t < T_S5:                                              # Szene 3: Riff waechst, Payoff
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
        put(f, self.rails[3])
        if t < T_FAZ:                                             # Szene 4: zurueck ins Heute
            u = seilzug(seg(t, T_S5 + 0.4, EIN))
            put(f, self.text3, dx=lerp(-40, 0, u), op=u * (1 - seg(t, T_FAZ - 0.2, 0.2)))
            self._marker(f, ma_at(t), 1 - seg(t, T_S5 + T_ZURUECK + 0.1, 0.3))
            return f, 44
        u = seilzug(seg(t, T_FAZ + 0.05, EIN))                    # Szene 5: Fazit
        put(f, self.fazit, dx=lerp(-40, 0, u), op=u)
        return f, 46

    def _marker(self, f, ma, op):
        if op <= 0:
            return
        put(f, self.leiste, op=op)
        lay = Image.new("RGBA", (W, 50), (0, 0, 0, 0))           # Marker auf eigener Ebene (Deckkraft wirkt)
        dr = ImageDraw.Draw(lay); x = self._lx(ma)
        col = o.rgb(C["magnesia"])
        dr.polygon([(x - 11, 8), (x + 11, 8), (x, 24)], fill=col)
        dr.line([(x, 24), (x, 48)], fill=col, width=3)
        put(f, m.Sprite(lay, 0, 600), op=op)


# ------------------------------------------------------------------ Ton: Musik in A-Moll / C-Dur
def sound_events(b):
    """Musik nach Szenen (SoundBook.musik, 84 BPM): Frage und Rate-Pause in A-Moll mit Countdown aus Toenen, Zeitreise
    abwaerts (fallendes Arpeggio, je Periodengrenze ein Ton), Tiefe der Zeit als Flaeche, das Riff waechst in C-Dur,
    Payoff als Akkordschlag in C-Dur, Rueckkehr steigend, Fazit ruhig, Klanglogo im Abspann."""
    h1 = rk.Hook1(t_grab=T_GRAB, t_geo=T_GEO, t_out=T_OUT)
    b.hook1(h1, akkord=AM9, bassnote=45)
    b.musik([
        (T_Q - 0.1, T_CHIPS, AM9, 45, "ruhig"),                # Frage
        (T_CHIPS, T_GUESS, FMAJ7, 41, "ruhig"),                # Chips
        (T_GUESS, T_HOOK, DM7, 38, "flaeche"),                 # Rate-Pause (Countdown darueber)
        (T_HOOK, T_S2, E_, 40, "flaeche"),                     # Atempause
        (T_S2, T_S2 + 1.8, AM9, 45, "fallend"),                # Zeitreise zurueck
        (T_S2 + 1.8, T_SEA, FMAJ7, 41, "fallend"),
        (T_SEA, T_S3, AM9, 45, "flaeche"),                     # Tiefe der Zeit, unter Wasser
        (T_S3, T_S3 + 1.6, C_, 36, "bewegt"),                  # das Riff waechst
        (T_S3 + 1.6, T_RISE, FMAJ7, 41, "bewegt"),
        (T_RISE, T_S4 - 0.15, GSUS4, 43, "flaeche"),           # Steigerung, dann 0,15 s Stille
        (T_S4, T_S5, C_, 36, "flaeche"),                       # A REEF.
        (T_S5, T_S5 + 1.6, AM9, 45, "steigend"),               # zurueck: Kalk waechst, Meer laeuft ab
        (T_S5 + 1.6, T_FAZ, G_, 43, "steigend"),               # die Alpen heben den Kalk
        (T_FAZ, T_FAZ + 2.0, FMAJ7, 41, "ruhig"),              # Fazit
        (T_FAZ + 2.0, T_END, C_, 36, "ruhig"),
    ], bpm=84.0, gain=-12.0)
    b.musik([(T_END, DUR, C_, 36, "flaeche")], bpm=84.0, gain=-14.5)   # Abspann 2,5 dB leiser: Payoff bleibt der Hoehepunkt
    b.countdown(T_GUESS + 0.1, T_HOOK - 0.1, step=0.45, gain=-11.0, tonleiter=PENTA_A[:5])
    for k, (spr_t, note) in enumerate(zip((T_CHIPS, T_CHIPS + 0.3, T_CHIPS + 0.6), (69, 72, 76))):
        b.ton("zupf", spr_t, -15.0, "chips", m=note, dauer=0.8, pan=0.3 * (k - 1))
    b.synth("whoosh", T_S2, -20.0, "verblassen", dur=0.7, seed=4)
    for k, g in enumerate(GRENZEN):                             # Zeitreise: ein Ton je Periodengrenze, abwaerts
        b.ton("zupf", t_bei_ma(g), -13.0, "zeitreise", m=[81, 79, 76, 74, 72][k], dauer=0.9, pan=0.3 * ((k % 3) - 1))
    b.ton("schwelle", T_SEA - 0.8, -12.0, "ankunft", akkord=AM9, dauer=0.8)
    b.ton("zupf", T_SEA, -10.0, "ankunft", m=69, dauer=1.4)
    rnd = random.Random(7)
    for k in range(6):                                          # Blasen unter Wasser: leise, hohe Toene
        b.ton("zupf", T_SEA + 0.4 + k * 0.85 + rnd.uniform(0, 0.2), -21.0, "blasen", m=PENTA_A[(k * 2) % 6] + 12, dauer=0.5)
    for k in range(13):                                         # das Riff waechst: je Bauteil ein Ton
        b.ton("zupf", T_S3 + 0.15 + 0.2 * k, -17.0, "riff", m=PENTA_C[k % 6], dauer=0.7, pan=0.4 * ((k % 3) - 1))
    b.ton("schwelle", T_RISE, -8.0, "steigerung", akkord=GSUS4, dauer=T_S4 - 0.15 - T_RISE)
    b.klang("sub_hit", T_S4 - 0.01, -11.0, "payoff-einschlag", f0=78.0, f1=36.0)
    b.ton("akzent", T_S4, -4.0, "payoff", akkord=C_, bassnote=36)
    b.ton("zupf", T_S4 + 0.12, -10.0, "chip", m=84, dauer=1.0)
    b.klang("crunch", T_DECKEN[1] - 0.2, -17.0, "kalk", seed=5)
    b.synth("whoosh", T_MEER_AB[0], -19.0, "meer-ab", dur=0.9, seed=9)
    b.ton("schwelle", T_HEBEN[0], -11.0, "heben", akkord=G_, dauer=T_HEBEN[1] - T_HEBEN[0])
    b.klang("thud", T_HEBEN[1], -13.0, "angekommen", seed=4)
    b.klang("chalk_slap", T_ZUG[1] - 0.05, -12.0, "griff", seed=2)
    b.ton("zupf", T_ZUG[1], -14.0, "griff", m=79, dauer=0.9)
    b.klanglogo(T_END + 0.3, tonika=72, gain=-9.5)                # eine Quarte hoeher als in r003: leiser, Payoff bleibt der Hoehepunkt
    b.ton("zupf", T_END + 1.3, -14.0, "herz", m=79, dauer=1.2)


cover_t = T_CHIPS + 1.0
META = dict(
    slug="2026-10-20_rewind-01", dur_range=[27.0, 38.0], payoff_t=T_S4, abspann_ab=T_END,
    title="GeoCrimps r004 REWIND #01 (Quiz), Fassung 1", ablauf="quiz",
    hook1_bis=T_OUT, hook_ab=T_Q, hook_bis=T_HOOK, weitere_fragen=[[T_GUESS, T_HOOK]], cover_t=cover_t,
    on_screen=["REWIND", "GERMANY'S HIGHEST PEAK:", "WHAT WAS THIS LIMESTONE ONCE?", "A DESERT", "B REEF", "C VOLCANO",
               "YOUR GUESS?", "235–240", "MILLION YEARS AGO", "CORALS, SPONGES, ALGAE BUILT IT.", "A REEF.",
               "THE ALPS LIFTED IT.", "YOU'RE CLIMBING AN ANCIENT REEF.", rk.Outro.CTA],
    labels=[],
    verdauen=["A REEF.", "YOU'RE CLIMBING AN ANCIENT REEF."],
    qc_times=[0.0, 0.4, 0.72, 1.1, 1.6, round(cover_t, 2), round(T_GUESS + 1.0, 2), round(T_S2 + 1.2, 2),
              round(T_S2 + 2.6, 2), round(T_SEA + 1.0, 2), round(T_S3 + 1.8, 2), round(T_S4 + 1.0, 2),
              round(T_S5 + 1.2, 2), round(T_S5 + 2.6, 2), round(T_FAZ + 2.0, 2), round(T_END + 2.0, 2)],
    marks=[(0, "Hook 1"), (T_GRAB, "Griff"), (T_GEO, "x GEOLOGY"), (T_Q, "Hook 2"), (T_CHIPS, "Chips"),
           (T_GUESS, "Rate-Pause"), (T_S2, "Zeitreise"), (T_SEA, "Meer"), (T_S3, "Riff waechst"), (T_S4, "PAYOFF"),
           (T_S5, "zurueck"), (T_FAZ, "Fazit"), (T_END, "Abspann")])

if __name__ == "__main__":
    rk.run(Reel, sound_events, META)
