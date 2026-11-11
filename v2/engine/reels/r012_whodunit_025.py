#!/usr/bin/env python3
"""Reel 012 -- WHODUNIT #03: "Phonolite columns: who cut the cracks you climb?" (Faktenbasis: Post #025, Devils Tower,
Saeulenklueftung), Ablauf "erklaerkette".

Fassung 1 vom 11.11.2026 nach PRODUKTION.md (Stand 16.10.2026), Vorlage r003 Fassung 6 (Hook 1 + Hook 2, Lesezeit,
ruhiges Tempo, Musik statt Klicks, Abspann mit LIKE & FOLLOW), Erklaerkette wie r009.
Themen-Tausch: Der Slot 17.11.2026 war fuer #061 (Schuhgummi) vorgesehen, Vorbedingung "Befund (orange) vom 29.08.
beheben"; der Befund ist im Repo weiterhin nicht dokumentiert, also nicht pruefbar. Kein spaeterer Slot derselben
Formatklasse war angelegt -> Tausch mit #025 (Geschichte, Format WHODUNIT bleibt), #061 rueckt auf den naechsten
Geschichte-Slot 24.11.2026.
Hook 1 0-1,45 s: GEOCRIMPS + CLIMBING ab Frame 0, ein Kletterer steigt im Riss zwischen zwei Saeulen einer Saeulenwand und
greift hoeher in den Riss (Kreidewolke), "x GEOLOGY" schlaegt ein und die Wand klappt in eine Porphyr-Signatur auf
(Einsprenglinge als kurze Leisten, eigene Signatur: Phonolith-Porphyr; keine der outcrop-Signaturen passt). Verraet nicht,
wie die Risse entstanden.
Hook 2 ab 1,8 s: Formatlabel WHODUNIT, Kontextzeile "PHONOLITE COLUMNS:" (Felsfarbe grau-gruen) ueber
"WHO CUT THE CRACKS YOU CLIMB?", 4,0 s. Isolinien-Welle vom Riss.
Zug 1 (Profilschnitt, frueher): ein Magmakoerper im umgebenden Gestein, erst fluessig (flimmert), dann waechst Kristall um
Kristall, er wird fest, bleibt aber heiss: "THE MAGMA SET SOLID."
Zug 2: Abkuehlfront von oben und unten nach innen, das abgekuehlte Gestein wird grau und zieht sich zusammen, Risse
wachsen senkrecht zur Abkuehlflaeche von oben und unten nach innen: "COOLING, IT SHRANK..."
Ohne Text: Erosion traegt das weichere Gestein ringsum ab, der Koerper bleibt stehen; Ueberblendung zurueck an die Wand.
Payoff an der Wand: "IT TORE ITSELF APART." gross mit Push-in, alle Saeulenfugen leuchten, der Kletterer zieht einen Zug
hoeher. Fazit: "NOW YOU CLIMB THOSE CRACKS.", der Kletterer steigt weiter. Kein Stempel, kein Chip.
Fakten (v2/faktenbasis/025/sources.md): Phonolith-Porphyr; Saeulenklueftung durch Abkuehlung und Kontraktion, im bereits
erstarrten Gestein (Lamur et al. 2018); Risse wachsen senkrecht zu den Abkuehlflaechen, von oben und unten nach innen
(NPS Columnar Jointing, Nachtrag 11.11.2026); Erosion des weicheren Gesteins ringsum; die Fugen sind Kletterrisse
(NPS Climbing Information, Nachtrag 11.11.2026). Die Entstehungsform (Lakkolith, Schlot, Coulee) ist offen: das Bild zeigt
keine Deckschicht ueber dem Koerper und keinen Zufuhrkanal. Keine Zahlen.
Bildmittel (Abwechslungsregel): Uebergang Isolinien-Welle, Ueberblendung mit Zoom zurueck (r011: Lichtstreifen,
Maßstabssprung) | Enthuellung Profilschnitt: Kristallisation, Abkuehlfront, Risse wachsen, Erosion legt frei (r011:
Gletscher im Profil, Mikroschnitt) | Payoff Antwort gross, Fugen leuchten, Kletterer zieht im Riss, kein Stempel (r011:
Stempel MYTH) | Musik As-Dur mit F-Moll-Flaechen, 79 BPM (r011: D-Moll/F-Dur 85 BPM).
Aufruf:  python3 r012_whodunit_025.py --out ../../../reels --qc <Ordner>   (--stills 0,4.8 | --reach)
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

# ------------------------------------------------------------------ eigene Signatur: Porphyr (nur in diesem Reel)
_pattern_orig = o._pattern_layer


def _pattern_layer(size, kind, color, seed=2, scale=1.0):
    """'porphyry': Einsprenglinge als kurze, zufaellig gedrehte Leisten in feiner Grundmasse (Phonolith-Porphyr)."""
    if kind != "porphyry":
        return _pattern_orig(size, kind, color, seed=seed, scale=scale)
    w, h = size
    L = Image.new("RGBA", size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    rnd = random.Random(seed); col = o.rgb(color); s = int(scale * o.S)
    for _ in range(int(w * h / (2600 * s * s))):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        ln, wd, a = rnd.uniform(9, 17) * s, rnd.uniform(3.5, 5.5) * s, rnd.uniform(0, math.pi)
        c, sn = math.cos(a), math.sin(a)
        pts = [(x + c * ln - sn * wd, y + sn * ln + c * wd), (x + c * ln + sn * wd, y + sn * ln - c * wd),
               (x - c * ln + sn * wd, y - sn * ln - c * wd), (x - c * ln - sn * wd, y - sn * ln + c * wd)]
        d.polygon(pts, fill=col)
    return L


o._pattern_layer = _pattern_layer

# ------------------------------------------------------------------ Zeitplan (ruhiges Tempo, Lesezeit)
EIN = 0.45
T_GRAB, T_GEO, T_OUT = 0.40, 0.72, 1.45
T_Q = 1.80                          # Hook 2
T_HOOK = T_Q + 4.0                  # Frage steht 4,0 s (8 Woerter), dann Isolinien-Welle + Ueberblendung (0,6 s)
T_B = T_HOOK + 0.6                  # Profilschnitt voll da
T_S2 = T_B + 0.45                   # Zug 1: Kristalle wachsen, der Koerper wird fest
T_CR0, T_CR1 = T_S2 + 0.5, T_S2 + 2.2
T1_OFF = T_S2 + 3.0
T_S3 = T1_OFF + 0.45                # Zug 2: Abkuehlfront, Schrumpfen, Risse
T_F0, T_F1 = T_S3 + 0.25, T_S3 + 2.9
T2_OFF = T_S3 + 3.25
T_ER0, T_ER1 = T2_OFF + 0.35, T2_OFF + 1.85   # Erosion (ohne Text)
T_X0 = T_ER1 + 0.15                 # Ueberblendung zurueck an die Wand (0,8 s)
T_X1 = T_X0 + 0.8
T_PAY = T_X1 + 0.45                 # Payoff "IT TORE ITSELF APART."
T_RISE = T_PAY - 1.0
T_MOVE1 = T_PAY + 0.7               # Kletterer zieht einen Zug hoeher (1,0 s)
T_S5 = T_PAY + 3.4                  # Fazit
T_MOVE2 = T_S5 + 1.3
T_END = T_S5 + 4.2                  # Abspann
DUR = T_END + rk.Outro.DUR

ROCK_L, ROCK_D, ROCK_T = "#5E655D", "#444A44", "#737A70"      # Phonolith: grau-gruen (Licht, Schatten, Saeulenkopf)
PHONO = "#AEB5A2"                                              # Kontextzeile in Felsfarbe
HOST, HOST_LINE = "#2A2622", "#3A342D"                         # umgebendes Gestein (neutral, ohne Signatur)
HOT, HOT_DEEP, COOL = C["heat"], "#7A2E16", "#525850"

# ------------------------------------------------------------------ Szene A: Saeulenwand
YG_A = 1500
JOINTS = [-20, 120, 262, 380, 515, 640, 790, 905, 1100]
TOPS = [880, 850, 900, 860, 838, 872, 846, 892]
CRACK_X = 640


def tower_poly():
    pts = []
    for k in range(len(TOPS)):
        pts += [(JOINTS[k], TOPS[k]), (JOINTS[k + 1], TOPS[k])]
    return pts + [(1100, YG_A), (-20, YG_A)]


BACK = dict(sw=22, hw=13, eb=(-1, 1), kb=(1, -1))
LH0, RH0 = (CRACK_X, 1112), (CRACK_X + 1, 1032)
POSE_START = dict(BACK, hip=(580, 1262), lean=4, lh=LH0, rh=(668, 1150), lf=(556, 1410), rf=(640, 1400))
POSE_HANG = dict(BACK, hip=(584, 1238), lean=12, lh=LH0, rh=RH0, lf=(558, 1392), rf=(640, 1376))
POSE_SWING = dict(POSE_HANG, hip=(590, 1228), lean=15)
LH1 = (CRACK_X, 966)
POSE_UP1 = dict(BACK, hip=(588, 1176), lean=11, lh=LH1, rh=RH0, lf=(562, 1330), rf=(640, 1304))
RH2 = (CRACK_X + 1, 892)
POSE_UP2 = dict(BACK, hip=(590, 1108), lean=12, lh=LH1, rh=RH2, lf=(566, 1262), rf=(640, 1236))


def move(p0, p1, u, hand):
    """Zug: Pose mischen, die greifende Hand beschreibt einen Bogen (zieht aus dem Riss und setzt hoeher wieder ein)."""
    p = kl.lerp_pose(p0, p1, seilzug(u))
    if 0 < u < 1:
        x, y = p[hand]
        p = dict(p, **{hand: (x + 34 * math.sin(math.pi * u) * (1 if hand == "rh" else -1), y)})
    return p


def pose_a(t):
    if t < T_GRAB:
        return kl.lerp_pose(POSE_START, POSE_SWING, seilzug(seg(t, 0.0, T_GRAB)))
    if t < T_MOVE1:
        u = seg(t, T_GRAB, 0.3)
        p = kl.lerp_pose(POSE_SWING, POSE_HANG, 0.5 - 0.5 * math.cos(math.pi * u))
    elif t < T_MOVE2:
        p = move(POSE_HANG, POSE_UP1, seg(t, T_MOVE1, 1.0), "lh")
    else:
        p = move(POSE_UP1, POSE_UP2, seg(t, T_MOVE2, 1.0), "rh")
    w = math.sin(2 * math.pi * (t - T_GRAB) / 2.6)                # atmen, leicht pendeln
    return dict(p, hip=(p["hip"][0] + 3 * w, p["hip"][1] + 1.5 * abs(w)), lean=p["lean"] + 1.0 * w)


def check_reach():
    cl = kl.Climber(scale=1.0, width=18.0, torso_w=36.0); out = {}
    for name, p in (("start", POSE_START), ("hang", POSE_HANG), ("swing", POSE_SWING), ("up1", POSE_UP1),
                    ("up2", POSE_UP2)):
        j = cl.joints(p)
        out[name] = round(max(math.dist(j[k], p[k]) for k in ("lh", "rh", "lf", "rf")), 3)
    return out


# ------------------------------------------------------------------ Szene B: Profilschnitt
BX0, BX1, BCX, BTOP = 180, 940, 560, 960
CRACKS = [262, 380, 515, 640, 790, 905]


def ytop(x):
    return BTOP + 6 * math.sin(x / 90.0)


def ybot(x):
    q = (x - BCX) / ((BX1 - BX0) / 2)
    return 1250 + 250 * math.sqrt(max(0.0, 1 - q ** 6))


def body_poly(shrink=0.0):
    xs = np.linspace(BX0, BX1, 80)
    cy = 1250
    top = [(x, ytop(x)) for x in xs]
    bot = [(x, ybot(x)) for x in xs[::-1]]
    pts = top + bot
    if shrink:
        pts = [(BCX + (x - BCX) * (1 - shrink), cy + (y - cy) * (1 - shrink)) for x, y in pts]
    return pts


def front(t):
    return seilzug(seg(t, T_F0, T_F1 - T_F0)) * 0.5 if t < T_F1 else 0.5


def host_level(t):
    return lerp(BTOP + 4, 1370, 0.5 - 0.5 * math.cos(math.pi * seg(t, T_ER0, T_ER1 - T_ER0)))


# ------------------------------------------------------------------ META
META = dict(
    slug="2026-11-17_whodunit-03", dur_range=[24.0, 33.0], payoff_t=T_PAY, abspann_ab=T_END,
    title="GeoCrimps r012 WHODUNIT #03 (Erklaerkette), Fassung 1", ablauf="erklaerkette",
    hook1_bis=T_OUT, hook_ab=T_Q, hook_bis=T_HOOK, weitere_fragen=[], cover_t=round(T_Q + 0.85, 2),
    on_screen=["WHODUNIT", "PHONOLITE COLUMNS:", "WHO CUT THE CRACKS YOU CLIMB?", "THE MAGMA SET SOLID.",
               "COOLING, IT SHRANK…", "IT TORE ITSELF APART.", "NOW YOU CLIMB THOSE CRACKS.", rk.Outro.CTA],
    labels=[],
    verdauen=["IT TORE ITSELF APART.", "NOW YOU CLIMB THOSE CRACKS."],
    qc_times=[0.0, T_GRAB, T_GEO, 1.1, round(T_Q + 0.85, 2), round(T_HOOK - 0.2, 2), round(T_HOOK + 0.3, 2),
              round(T_S2 + 1.2, 2), round(T1_OFF - 0.1, 2), round(T_S3 + 1.5, 2), round(T2_OFF - 0.1, 2),
              round(T_ER1 - 0.3, 2), round(T_PAY + 0.8, 2), round(T_S5 + 2.6, 2), round(T_END - 0.1, 2),
              round(T_END + 2.0, 2)],
    marks=[(0, "Hook 1"), (T_GRAB, "Griff"), (T_GEO, "x GEOLOGY"), (T_Q, "Hook 2"), (T_HOOK, "Welle"),
           (T_S2, "Zug 1"), (T_S3, "Zug 2"), (T_ER0, "Erosion"), (T_X0, "Wand"), (T_PAY, "PAYOFF"),
           (T_MOVE1, "Zug"), (T_S5, "Fazit"), (T_END, "Abspann")])


# ------------------------------------------------------------------ Reel
class Reel(rk.ReelBase):
    DUR = DUR

    def __init__(self):
        super().__init__()
        self.rail = rk.Rail(2)
        self.outro = rk.Outro()
        self.rails = [rk.rail_sprite(0, 2), rk.rail_sprite(1, 2), rk.rail_sprite(2, 2), rk.rail_sprite(2, 2, logo_on=True)]
        self.hook1 = rk.Hook1(t_grab=T_GRAB, t_geo=T_GEO, t_out=T_OUT)
        self.climber = kl.Climber(scale=1.0, width=18.0, torso_w=36.0)
        self.label = m.text_sprite("WHODUNIT", X0, rk.FORMAT_Y, "stencil", 40, C["slate"], tracking=0.12)
        self.hook_kick = m.text_sprite("PHONOLITE COLUMNS:", X0, rk.HOOK_Y, "display", 96, PHONO)
        self.hook, _ = m.lines_sprite(["WHO CUT THE CRACKS", "YOU CLIMB?"], rk.HOOK_Y + 112, size=136)
        self.text1, _ = m.lines_sprite(["THE MAGMA", "SET SOLID."], 352, role="display_xb", size=118)
        self.text2, _ = m.lines_sprite(["COOLING,", "IT SHRANK…"], 352, role="display_xb", size=118)
        self.answer, _ = m.lines_sprite(["IT TORE", "ITSELF APART."], 352, size=190)
        self.fazit, _ = m.lines_sprite(["NOW YOU CLIMB", "THOSE CRACKS."], 352, role="display_xb", size=118)
        self._scene_a()
        self._scene_b()

    # -------------------------------------------------------------- Szene A
    def _scene_a(self):
        def column(d, x0, x1, top, k):
            xm = x0 + (x1 - x0) * 0.42
            d.polygon([P(x0, top + 14), P(xm, top + 26), P(xm, YG_A), P(x0, YG_A)], fill=o.rgb(ROCK_L))
            d.polygon([P(xm, top + 26), P(x1, top + 12), P(x1, YG_A), P(xm, YG_A)], fill=o.rgb(ROCK_D))
            d.polygon([P(x0, top + 14), P(x0 + (x1 - x0) * 0.55, top), P(x1, top + 12), P(xm, top + 26)], fill=o.rgb(ROCK_T))
            d.line([P(xm, top + 26), P(xm, YG_A)], fill=o.rgb("#3A403A"), width=int(2 * o.S))
            rnd = random.Random(30 + k)
            for _ in range(2):                                    # Querbrueche
                y = rnd.uniform(top + 160, YG_A - 120)
                d.line([P(x0 + 4, y), P(xm, y + 10), P(x1 - 4, y - 2)], fill=o.rgb("#3A403A"), width=int(2 * o.S))

        def bg(im):
            o.contour_field(im, 840, 560, n=8, r0=120, step=58, alpha=70)
            d = ImageDraw.Draw(im)
            for k in range(len(TOPS)):
                column(d, JOINTS[k], JOINTS[k + 1], TOPS[k], k)
            for xj in JOINTS[1:-1]:                               # Fugen = Kletterrisse
                top = max(TOPS[JOINTS.index(xj) - 1], TOPS[JOINTS.index(xj)])
                d.line([P(xj, top + 10), P(xj, YG_A)], fill=o.rgb(C["obsidian"]), width=int(6 * o.S))
            lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
            ImageDraw.Draw(lay).rectangle([P(-10, YG_A), P(1090, 1930)], fill=o.rgb(C["graphite"]))
            im.alpha_composite(lay)
            rnd = random.Random(8)                                # Blockhalde am Wandfuss
            for _ in range(26):
                cx, cy = rnd.uniform(-10, 1090), rnd.uniform(YG_A - 10, YG_A + 60)
                wv, hv = rnd.uniform(40, 90), rnd.uniform(22, 40)
                a = rnd.uniform(-0.4, 0.4)
                pts = [(cx + math.cos(a + q) * wv * (0.9 if i % 2 else 1.0) / 2, cy + math.sin(a + q) * hv / 2)
                       for i, q in enumerate(np.linspace(0, 2 * math.pi, 7)[:-1])]
                d.polygon([P(*p) for p in pts], fill=o.rgb(rnd.choice([ROCK_D, "#3A403A", ROCK_L])))
            d.line([P(-10, YG_A + 64), P(1090, YG_A + 64)], fill=o.rgb(C["slate"], 120), width=int(2 * o.S))
        self.bg_a = m.background(bg)
        self.geo = kl.GeoReveal(tower_poly(), "porphyry", RH0[0], RH0[1], pat_alpha=90, seed=8)

        def glow(im):
            d = ImageDraw.Draw(im)
            for xj in JOINTS[1:-1]:
                top = max(TOPS[JOINTS.index(xj) - 1], TOPS[JOINTS.index(xj)])
                d.line([P(xj, top + 10), P(xj, YG_A)], fill=o.rgb(C["magnesia"]), width=int(5 * o.S))
        self.joint_glow = m.sprite(glow)

    def world_a(self, t):
        f = self.bg_a.copy()
        u = seilzug(seg(t, T_GEO, 0.5))
        if u > 0 and t < T_OUT + 0.4:
            self.geo.put(f, u, fade=1 - seg(t, T_OUT, 0.4))
        if T_PAY <= t:
            g = 0.55 + 0.45 * math.sin(math.pi * seg(t, T_PAY, 1.4)) if t < T_PAY + 1.4 else 0.55 * (1 - seg(t, T_S5, 0.8))
            put(f, self.joint_glow, op=g)
        put(f, self.climber.sprite(pose_a(t)))
        kl.chalk_puff(f, t, T_GRAB, RH0[0], RH0[1] - 6, seed=11)
        kl.chalk_puff(f, t, T_MOVE1 + 0.95, LH1[0], LH1[1] - 6, seed=12, size=0.7)
        kl.chalk_puff(f, t, T_MOVE2 + 0.95, RH2[0], RH2[1] - 6, seed=13, size=0.7)
        return f

    # -------------------------------------------------------------- Szene B: Profilschnitt
    def _scene_b(self):
        def bg(im):
            o.contour_field(im, 860, 560, n=8, r0=110, step=56, alpha=60)
        self.bg_b = m.background(bg)
        rnd = random.Random(17)
        self.host_bands = [(y, rnd.uniform(0, 6.28)) for y in range(BTOP + 40, 1960, 46)]
        rnd = random.Random(23)                                    # Einsprenglinge (Kristalle) im Koerper
        self.xtals = []
        mk = Image.new("L", (W, H), 0); ImageDraw.Draw(mk).polygon(body_poly(0.03), fill=255)
        mka = np.asarray(mk)
        while len(self.xtals) < 230:
            x, y = rnd.uniform(BX0, BX1), rnd.uniform(BTOP, 1500)
            if mka[int(y), int(x)] > 128:
                self.xtals.append((x, y, rnd.uniform(0, math.pi), rnd.uniform(6, 12), rnd.uniform(0, 1)))
        rnd = random.Random(29)                                    # gezackte Risslinien
        self.crack_jit = {xc: [rnd.uniform(-5, 5) for _ in range(40)] for xc in CRACKS}
        self.grains = [(rnd.uniform(0, 1080), rnd.uniform(0, 1), rnd.uniform(0, 1)) for _ in range(60)]

    def body_layer(self, t):
        """Koerper im Profil (2x in seinem Rechteck): heiss -> fest -> Abkuehlfront, Risse von oben und unten."""
        fr = front(t)
        shrink = 0.012 * seg(t, T_F0 + 0.6, T_F1 - T_F0)
        crys = seg(t, T_CR0, T_CR1 - T_CR0)
        liquid = 1 - seg(t, T_CR0, 1.2)

        def draw(d, X, Y):
            poly = body_poly(shrink)
            d.polygon([(X(x), Y(y)) for x, y in poly], fill=o.rgb(COOL if fr >= 0.5 else HOT_DEEP))
            if fr < 0.5:                                           # heisser Kern zwischen den Fronten
                xs = np.linspace(BX0, BX1, 80)
                cy = 1250
                sc = lambda x, y: (BCX + (x - BCX) * (1 - shrink), cy + (y - cy) * (1 - shrink))
                top = [sc(x, ytop(x) + fr * (ybot(x) - ytop(x))) for x in xs]
                bot = [sc(x, ybot(x) - fr * (ybot(x) - ytop(x))) for x in xs[::-1]]
                core = [p for p in top + bot]
                if fr > 0:
                    d.polygon([(X(x), Y(y)) for x, y in poly], fill=o.rgb(COOL))
                d.polygon([(X(x), Y(y)) for x, y in core], fill=o.rgb(HOT_DEEP))
                if fr > 0:                                         # die Front als helle Isolinie
                    for line in (top, bot):
                        pts = [(X(x), Y(y)) for x, y in line if ytop(x) + 8 < y < ybot(x) - 8 or fr < 0.02]
                        if len(pts) > 1:
                            d.line(pts, fill=o.rgb(HOT, 230), width=int(3 * o.S))
                if liquid > 0:                                     # fluessig: Flimmern
                    for k in range(7):
                        yy = 1010 + k * 62 + 8 * math.sin(t * 3 + k)
                        pts = [(X(x), Y(yy + 10 * math.sin(x / 40 + t * 4 + k))) for x in range(BX0 + 30, BX1 - 30, 12)
                               if ytop(x) + 10 < yy < ybot(x) - 10]
                        if len(pts) > 1:
                            d.line(pts, fill=o.rgb(HOT, int(150 * liquid)), width=int(3 * o.S))
            for x, y, a, ln, ph in self.xtals:                     # Kristalle wachsen
                v = seg(crys, ph * 0.8, 0.2)
                if v <= 0:
                    continue
                x, y = BCX + (x - BCX) * (1 - shrink), 1250 + (y - 1250) * (1 - shrink)
                l2 = ln * v; c, s = math.cos(a), math.sin(a)
                d.line([(X(x - c * l2), Y(y - s * l2)), (X(x + c * l2), Y(y + s * l2))],
                       fill=o.rgb("#E3C9A8" if fr < 0.5 and fr < 0.15 else "#B9BEB0", 230), width=int(5 * o.S))
            g = max(0.0, (fr - 0.03) / 0.47)                       # Risse folgen der Front nach innen
            if g > 0:
                for xc in CRACKS:
                    jit = self.crack_jit[xc]
                    y0, y1 = ytop(xc), ybot(xc)
                    half = (y1 - y0) / 2
                    for sgn, ys in ((1, y0), (-1, y1)):
                        n = max(2, int(20 * g))
                        pts = []
                        for i in range(n):
                            yy = ys + sgn * half * g * i / (n - 1) * 0.98
                            xx = xc + jit[i + (20 if sgn < 0 else 0)] * (i > 0)
                            xx, yy = BCX + (xx - BCX) * (1 - shrink), 1250 + (yy - 1250) * (1 - shrink)
                            pts.append((X(xx), Y(yy)))
                        d.line(pts, fill=o.rgb(C["obsidian"]), width=int((3 + 2.5 * g) * o.S), joint="curve")
            d.line([(X(x), Y(y)) for x, y in poly + poly[:1]], fill=o.rgb(C["slate"] if fr >= 0.5 else HOT, 200),
                   width=int(3 * o.S), joint="curve")
        return rk.region(BX0 - 10, BTOP - 20, BX1 + 10, 1520, draw)

    def world_b(self, t):
        f = self.bg_b.copy()
        lvl = host_level(t)

        def host(d, X, Y):
            xs = list(range(-20, 1101, 10))
            top = []
            for x in xs:
                y = lvl + 5 * math.sin(x / 70.0)
                if BX0 <= x <= BX1:
                    y = min(y, ybot(x) - 2)
                top.append((x, y))
            d.polygon([(X(x), Y(y)) for x, y in top] + [(X(1100), Y(1930)), (X(-20), Y(1930))], fill=o.rgb(HOST))
            for y, ph in self.host_bands:
                pts = [(X(x), Y(y + 6 * math.sin(x / 120 + ph))) for x in range(-20, 1101, 20)
                       if y + 6 * math.sin(x / 120 + ph) > top[min(len(top) - 1, (x + 20) // 10)][1] + 4]
                if len(pts) > 1:
                    d.line(pts, fill=o.rgb(HOST_LINE), width=int(3 * o.S))
            for seg_ in ([q for q in top if q[0] < BX0 - 4], [q for q in top if q[0] > BX1 + 4]):
                if len(seg_) > 1:
                    d.line([(X(x), Y(y)) for x, y in seg_], fill=o.rgb("#6E6150"), width=int(3 * o.S))
        put(f, rk.region(0, BTOP - 30, W, H, host))
        put(f, self.body_layer(t))
        if T_ER0 <= t < T_X1:                                      # Erosion: Koernchen rieseln ab
            dr = ImageDraw.Draw(f)
            for x, ph, s in self.grains:
                if BX0 - 10 < x < BX1 + 10:
                    continue
                v = ((t - T_ER0) * (0.7 + 0.5 * s) + ph) % 1.0
                y = lvl - 10 + 140 * v
                a = int(200 * math.sin(math.pi * v) * (1 - seg(t, T_ER1, 0.5)))
                dr.ellipse([x - 2.5, y - 2.5, x + 2.5, y + 2.5], fill=o.rgb("#8A7A62", a))
        if t < T_CR0 + 1.6:                                        # Hitzeflimmern ueber dem Koerper
            dr = ImageDraw.Draw(f)
            for k, x in enumerate(range(260, 900, 90)):
                ph = ((t * 0.6) + k * 0.17) % 1.0
                yl = BTOP - 12 - 80 * ph
                pts = [(x + 6 * math.sin(yy / 9 + k), yy) for yy in range(int(yl), int(yl) - 34, -3)]
                dr.line(pts, fill=o.rgb(HOT, int(120 * math.sin(math.pi * ph) * (1 - seg(t, T_CR0, 1.6)))), width=3)
        return f

    # -------------------------------------------------------------- Frames
    def frame(self, t):
        if t < T_HOOK:                                           # Szene 1: Hook (Wand)
            f = m.zoomed(self.world_a(t), 1 + 0.03 * seilzug(seg(t, 0, T_HOOK)), CRACK_X, 1100)
            put(f, self.rails[0])
            self.hook1.draw(f, t, hook_bis=T_HOOK)
            u = seilzug(seg(t, T_Q, EIN))
            if u > 0:
                fade = 1.0
                put(f, self.label, dx=lerp(-30, 0, u), op=u * fade)
                put(f, self.hook_kick, dx=lerp(-40, 0, u), op=u * fade)
                put(f, self.hook, dx=lerp(-40, 0, u), op=u * fade)
            return f, 121
        if t < T_B:                                              # Uebergang: Isolinien-Welle vom Riss, Ueberblendung
            u = seilzug(seg(t, T_HOOK, T_B - T_HOOK))
            fa = m.zoomed(self.world_a(t), lerp(1.03, 1.25, u), CRACK_X, 1100)
            fb = self.world_b(t)
            f = Image.blend(fa, fb, u)
            put(f, rk.wave(seg(t, T_HOOK, 0.6), cx=CRACK_X, cy=1060))
            put(f, self.rails[0])
            self.hook1.draw(f, t, hook_bis=T_HOOK, fade=0.15)
            fade = 1 - seg(t, T_HOOK, 0.15)
            for spr in (self.label, self.hook_kick, self.hook):
                put(f, spr, op=fade)
            return f, 122
        if t < T_X0:                                             # Profilschnitt: Zug 1, Zug 2, Erosion
            z = 1 + 0.035 * (0.5 - 0.5 * math.cos(math.pi * seg(t, T_B, T_ER0 - T_B)))
            if t >= T_ER0:
                z = lerp(1.035, 1.0, seilzug(seg(t, T_ER0, 1.0)))
            f = m.zoomed(self.world_b(t), z, BCX, 1230)
            if t < T_S3:
                put(f, self.rails[1]); self.rail.pop(f, t, 0, T_S2)
                u = seilzug(seg(t, T_S2 + 0.05, EIN)); put(f, self.text1, dx=lerp(-40, 0, u), op=u * (1 - seg(t, T1_OFF, 0.25)))
                return f, 123
            put(f, self.rails[2]); self.rail.pop(f, t, 1, T_S3)
            u = seilzug(seg(t, T_S3 + 0.05, EIN)); put(f, self.text2, dx=lerp(-40, 0, u), op=u * (1 - seg(t, T2_OFF, 0.25)))
            return f, 124
        if t < T_X1:                                             # zurueck an die Wand
            u = seilzug(seg(t, T_X0, T_X1 - T_X0))
            fb = m.zoomed(self.world_b(t), lerp(1.0, 1.15, u), BCX, 1150)
            fa = m.zoomed(self.world_a(t), lerp(1.2, 1.0, u), CRACK_X, 1150)
            f = Image.blend(fb, fa, u)
            put(f, self.rails[2])
            return f, 125
        if t >= T_END:
            return self.outro.frame(t, T_END), 129
        z = lerp(1.0, 1.05, 0.5 - 0.5 * math.cos(math.pi * seg(t, T_PAY, T_S5 - T_PAY)))
        if t >= T_S5:
            z = lerp(1.05, 1.0, seilzug(seg(t, T_S5, 0.9))) * (1 + 0.025 * seg(t, T_S5 + 0.9, T_END - T_S5 - 0.9))
        f = m.zoomed(self.world_a(t), z, CRACK_X, 1100)
        put(f, self.rails[3] if t >= T_PAY else self.rails[2])
        if t < T_S5:                                             # Payoff
            u = seg(t, T_PAY, 0.3)
            self.rail.logo_pop(f, t, T_PAY)
            put(f, self.answer, op=min(1, u * 2) * (1 - seg(t, T_S5 - 0.2, 0.2)), scale=lerp(1.18, 1.0, seilzug(u)),
                anchor=(X0, 352))
            return f, 126
        u = seilzug(seg(t, T_S5 + 0.25, EIN))                     # Fazit
        put(f, self.fazit, dx=lerp(-40, 0, u), op=u)
        return f, 127


# ------------------------------------------------------------------ Ton: Musik in As-Dur mit F-Moll-Flaechen, 79 BPM
FM7, FM9, DBMAJ7, AB, EB, BBM7, EBSUS4, CM7 = ([53, 56, 60, 63], [53, 56, 60, 63, 67], [49, 53, 56, 60], [51, 56, 60, 63],
                                              [51, 55, 58, 63], [53, 56, 58, 61], [51, 56, 58], [55, 58, 60, 63])
PENTA = [80, 82, 84, 87, 89, 92, 94]   # As-Dur-Pentatonik ab As5


def sound_events(b):
    """Musik in As-Dur mit F-Moll-Flaechen (79 BPM) nach Szenen; Hook 1 musikalisch; Kristalle als hohe, steigende
    Toene, Risse als fallende Toene der Pentatonik, Erosion mit Figur "fallend"; Akkordschlag zur Aufloesung (F-Moll),
    Fazit nach As-Dur aufgeloest; Klanglogo im Abspann."""
    h1 = rk.Hook1(t_grab=T_GRAB, t_geo=T_GEO, t_out=T_OUT)
    b.hook1(h1, akkord=FM7, bassnote=41)
    b.musik([
        (T_Q - 0.1, T_Q + 2.0, FM7, 41, "ruhig"),                # Frage: offen
        (T_Q + 2.0, T_HOOK, DBMAJ7, 37, "ruhig"),
        (T_HOOK, T_S2, BBM7, 46, "flaeche"),                     # Welle, Profilschnitt
        (T_S2, T_S2 + 1.5, FM7, 41, "bewegt"),                   # Kristalle wachsen
        (T_S2 + 1.5, T_S3, DBMAJ7, 37, "bewegt"),
        (T_S3, T_S3 + 1.6, CM7, 48, "ruhig"),                    # Abkuehlfront
        (T_S3 + 1.6, T2_OFF, BBM7, 46, "steigend"),              # Risse wachsen
        (T2_OFF, T_X1, AB, 44, "fallend"),                       # Erosion: Absinken
        (T_X1, T_PAY - 0.15, EBSUS4, 39, "flaeche"),             # Steigerung, dann 0,15 s Stille
        (T_PAY, T_S5, FM9, 41, "flaeche"),                       # Aufloesung: verdauen
        (T_S5, T_S5 + 2.0, DBMAJ7, 37, "ruhig"),                 # Fazit ...
        (T_S5 + 2.0, T_END, AB, 44, "ruhig"),                    # ... nach As-Dur aufgeloest
        (T_END, DUR, AB, 44, "flaeche"),                         # Abspann
    ], bpm=79.0, gain=-12.0)
    b.synth("whoosh", T_HOOK, -18.0, "welle", dur=0.6, seed=4)
    b.ton("schwelle", T_HOOK - 0.3, -15.0, "welle", akkord=BBM7, dauer=0.6)
    b.ton("zupf", T_S2, -14.0, "bohrhaken", m=87, dauer=0.9)
    for k in range(6):                                           # Kristalle: hohe, steigende Toene
        b.ton("zupf", T_CR0 + 0.3 * k, -19.0, "kristalle", m=PENTA[k], dauer=0.6, pan=0.3 * ((k % 3) - 1))
    b.ton("zupf", T_S3, -14.0, "bohrhaken", m=89, dauer=0.9)
    for k in range(6):                                           # Risse: fallende Toene, leises Knacken
        tt = T_F0 + 0.6 + 0.35 * k
        b.ton("zupf", tt, -17.0, "risse", m=PENTA[5 - k] - 12, dauer=0.7, pan=0.25 * ((k % 3) - 1))
    b.klang("crunch", T_F0 + 0.9, -22.0, "knacken", seed=5)
    b.klang("crunch", T_F0 + 1.9, -21.0, "knacken", seed=6)
    b.klang("crunch", T_ER0 + 0.2, -23.0, "erosion", seed=7)
    b.ton("schwelle", T_X0 - 0.2, -15.0, "zurueck", akkord=AB, dauer=0.8)
    b.ton("schwelle", T_RISE, -8.0, "steigerung", akkord=EBSUS4, dauer=T_PAY - 0.15 - T_RISE)
    b.klang("sub_hit", T_PAY - 0.01, -10.0, "payoff-einschlag", f0=78.0, f1=36.0)
    b.ton("akzent", T_PAY, -4.0, "payoff", akkord=FM9, bassnote=41)
    b.klang("chalk_slap", T_MOVE1 + 0.95, -12.0, "griff", seed=2)
    b.klang("chalk_slap", T_MOVE2 + 0.95, -13.0, "griff", seed=3)
    b.ton("zupf", T_S5 + 0.25, -14.0, "fazit", m=84, dauer=0.9)
    b.klanglogo(T_END + 0.3, tonika=68, gain=-7.0)               # Abspann: Logo (As-Dur)
    b.ton("zupf", T_END + 1.3, -12.0, "herz", m=87, dauer=1.2)


if __name__ == "__main__":
    if "--reach" in sys.argv:
        print(check_reach())
        sys.exit(0)
    rk.run(Reel, sound_events, META)
