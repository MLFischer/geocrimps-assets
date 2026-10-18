#!/usr/bin/env python3
"""Reel 005 -- HOLD ID #02: "How did this hold form?" (Faktenbasis: Post #012, Sinter waechst), Ablauf "offene_frage".

Fassung 1 vom 18.10.2026 nach PRODUKTION.md (Stand 16.10.2026), Vorlage r003 Fassung 6: Hook 1 + Hook 2 mit klarer
Frage, Lesezeit, ruhiges Tempo, Musik statt Klicks, Abspann mit LIKE & FOLLOW.
Hook 1 0-1,45 s: GEOCRIMPS + CLIMBING ab Frame 0, ein Kletterer kneift eine Sinterroehre (Tufa) an einer Kalkwand
(Kreidewolke), "x GEOLOGY" schlaegt ein und die Wand klappt in ihre Kalk-Signatur auf (Ziegelmuster, Baenke); die Tufa
bleibt ohne Signatur, verraet also nicht, wie sie entstand.
Hook 2 ab 1,8 s: Formatlabel HOLD ID, Kontextzeile "TUFA ON LIMESTONE:" (Tufa-Farbe) ueber "HOW DID THIS HOLD FORM?",
steht 3,75 s. Isolinien-Welle von der Tufa-Spitze, der Kletterer springt ab und wartet am Boden.
Zug 1 (harmlos): Wasser tritt ueber der Tufa aus und laeuft an ihr herab, tropft von der Spitze: "WATER SEEPS OUT."
Zug 2 (Wendung): Zoom auf die Spitze, die Tufa wird im Laengsschnitt gezeigt (Anwachslagen); im Zeitraffer gibt jeder
Tropfen CO2 ab (Blaeschen, Label CO2), eine neue Lage Kalk bleibt haengen, die Spitze waechst nach unten:
"BUT IT LOSES CO2..." Callback als naheliegende falsche Antwort: "CARVED OUT?" Payoff: "DRIP BY DRIP." gross, die
Lagen leuchten nacheinander auf. Folge: Zoom zurueck, Stempel HOLD ID #02, der Kletterer steigt wieder ein und kneift
die gewachsene Tufa: "A GROWN-ON HOLD." Abspann mit LIKE & FOLLOW.
Fakten (v2/faktenbasis/012/sources.md): Tufa/Kalksinter faellt aus mit Kalk uebersaettigtem Wasser aus, Ausloeser vor
allem CO2-Entgasung (Ford & Pedley 1996; BGS OR/14/043); Wasser tritt an Quellen und Sickerstellen aus, sein Kalk stammt
aus geloestem Karbonatgestein (BGS OR/14/043); Tropfsteine wachsen nach unten aus unzaehligen Tropfen (NPS); Wachstum
schichtweise auf bestehender Wand, also juenger als die Wand. Kein Alter, kein Ort im Bild.
Bildmittel (Abwechslungsregel): Uebergang Isolinien-Welle von der Spitze, Zoom auf die Spitze (r004: Zeitreise mit
Zaehler) | Enthuellung Laengsschnitt mit Anwachslagen im Zeitraffer, Blaeschen (r004: Meer und Riff) | Payoff Antwort
gross, Lagen leuchten, Stempel HOLD ID, Kletterer kneift die Tufa (r004: Chip leuchtet) | Musik D-Dur, 78 BPM
(r004: A-Moll/C-Dur 84 BPM, r003: G-Dur 80 BPM).
Aufruf:  python3 r005_holdid_012.py --out ../../../reels --qc <Ordner>   (--stills 0,4.8 fuer Einzelbilder)
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
EIN = 0.45                         # Einblenden von Texten
T_GRAB, T_GEO, T_OUT = 0.40, 0.72, 1.45                       # Hook 1: Griff, "x GEOLOGY", Uebergang in die Kopfzeile
T_Q = 1.80                         # Hook 2: Formatlabel, Kontextzeile und Frage
T_HOOK = T_Q + 3.75                # Frage steht 3,75 s, dann Isolinien-Welle, der Kletterer springt ab
T_S2 = T_HOOK + 0.45               # Zug 1: Wasser tritt aus
T1_OFF = T_S2 + 2.25               # Zug-1-Text blendet aus
T_Z0 = T1_OFF + 0.05               # Zoom auf die Spitze (0,8 s)
T_Z1 = T_Z0 + 0.8
ZOOM, ZC = 1.45, (650, 1340)
T_S3 = T_Z0 + 0.45                 # Zug 2: Laengsschnitt, Zeitraffer
T_CUT = T_S3                       # Schnitt blendet ein
T_G0 = T_S3 + 0.4                  # Zeitraffer: vier Tropfen, vier neue Lagen
CYC, NCYC = 0.6, 4
T_G1 = T_G0 + CYC * NCYC
T2_OFF = T_S3 + 2.55               # Zug-2-Text blendet aus
T_CALL = T2_OFF + 0.45             # Callback "CARVED OUT?"
T_RISE = T_CALL + 1.0              # Akkord schwillt an, 0,15 s Stille, dann der Payoff
T_S4 = T_CALL + 2.15               # Payoff "DRIP BY DRIP."
T_S5 = T_S4 + 3.05                 # Folge: Zoom zurueck, Stempel, Kletterer steigt ein
PUSH = 1.05
T_STAMP = T_S5 + 0.45
T_CLIMB = T_S5 + 0.15
T_FAZ = T_S5 + 0.95                # Fazit "A GROWN-ON HOLD."
T_END = T_FAZ + 2.95               # Abspann
DUR = T_END + rk.Outro.DUR

# ------------------------------------------------------------------ Szene: Kalkwand mit Tufa
ROOF = 845                         # Dachkante (oben: Hoehle, unten: Wand)
YG = 1500                          # Boden
L0, L1 = 1270.0, 1330.0            # Tufa-Spitze vor und nach dem Zeitraffer
STAGES = [980, 1030, 1075, 1115, 1150, 1185, 1215, 1245, L0]          # aeltere Anwachslagen (Laengsschnitt)
NEW = [L0 + (L1 - L0) * (k + 1) / NCYC for k in range(NCYC)]          # neue Lagen im Zeitraffer
TUFA, TUFA_IN, TUFA_LINE = "#CDBF9F", "#7E735C", "#E6DCC4"            # Tufa-Farbe (Zusatzfarbe wie Kruste in r003)
WALL = "#20272D"


def tcx(y):
    return 640 + 8 * math.sin((y - ROOF) / 70)


def thw(y, L):
    """Halbe Breite der Tufa bei y fuer eine Spitze bei L: Knollen, oben ausgestellt, unten gerundet."""
    if y >= L:
        return 0.0
    u = max(0.0, (y - ROOF) / (L - ROOF))
    base = 38 + 7 * math.sin((y - ROOF) / 45 + 0.5) + 22 * (1 - min(1.0, max(0.0, y - ROOF) / 60)) ** 2
    return base * max(0.0, 1 - u ** 2.4) ** 0.5


def tufa_poly(L, n=90):
    ys = [ROOF - 4 + (L - ROOF + 4) * (k / n) ** 0.9 for k in range(n + 1)]
    left = [(tcx(y) - thw(y, L), y) for y in ys]
    right = [(tcx(y) + thw(y, L), y) for y in ys[::-1]]
    return left + [(tcx(L), L)] + right


def tufa_outline(L, n=90):
    """Umrisslinie (offen oben) fuer eine Lage."""
    ys = [ROOF + (L - ROOF) * (k / n) ** 0.9 for k in range(n + 1)]
    return [(tcx(y) - thw(y, L), y) for y in ys] + [(tcx(L), L)] + [(tcx(y) + thw(y, L), y) for y in ys[::-1]]


def tip_len(t):
    """Spitze: waechst im Zeitraffer in vier Schueben (je Tropfen eine Lage)."""
    if t < T_G0:
        return L0
    k = min(NCYC, int((t - T_G0) / CYC)); v = seg(t, T_G0 + k * CYC + 0.3, 0.25) if k < NCYC else 1.0
    return L0 + (L1 - L0) * (k + seilzug(v) if k < NCYC else NCYC) / NCYC


# Kletterer (Rueckenansicht), Haende und Fuesse an Griffen; vor dem Rendern geprueft (check_reach)
BACK = dict(sw=22, hw=13, eb=(-1, 1), kb=(1, -1))
YP = 1012                                                       # Hoehe der Kneifstelle an der Tufa
PINCH0 = (tcx(YP) - thw(YP, L0) + 3, YP)                        # rechte Hand kneift die Tufa (Hook)
PINCH1 = (tcx(YP) - thw(YP, L1) + 3, YP)                        # ... und nach dem Zeitraffer (Folge)
POCKET = (436, 990)                                             # linke Hand: Loch in der Wand
FOOT_L, FOOT_R = (452, 1318), (572, 1300)
POSE_START = dict(BACK, hip=(498, 1212), lean=-3, lh=POCKET, rh=(560, 1112), lf=(446, 1338), rf=(560, 1326))
POSE_HANG = dict(BACK, hip=(516, 1172), lean=7, lh=POCKET, rh=PINCH0, lf=FOOT_L, rf=FOOT_R)
POSE_SWING = dict(POSE_HANG, hip=(522, 1162), lean=10)
POSE_HANG1 = dict(POSE_HANG, rh=PINCH1)
POSE_STAND = dict(BACK, hip=(330, YG - 168), lean=0, lh=(308, YG - 140), rh=(352, YG - 140),
                  lf=(312, YG - 2), rf=(350, YG - 2))
POSE_LOOK = dict(POSE_STAND, lean=4, rh=(372, YG - 150))


def check_reach():
    cl = kl.Climber(scale=1.0, width=18.0, torso_w=36.0); out = {}
    for name, p in (("start", POSE_START), ("hang", POSE_HANG), ("hang1", POSE_HANG1), ("stand", POSE_STAND),
                    ("look", POSE_LOOK)):
        j = cl.joints(p)
        out[name] = max(math.dist(j[k], p[k]) for k in ("lh", "rh", "lf", "rf"))
    return out


def climber_pose(t):
    if t < T_GRAB:                                               # Hook 1: greift die Tufa (Frame 0 schon in Bewegung)
        return kl.lerp_pose(POSE_START, POSE_SWING, seilzug(seg(t, 0.0, T_GRAB)))
    if t < T_HOOK:
        u = seg(t, T_GRAB, 0.3)
        p = kl.lerp_pose(POSE_SWING, POSE_HANG, 0.5 - 0.5 * math.cos(math.pi * u))
        if u >= 1:                                               # haengt, atmet, pendelt leicht
            w = math.sin(2 * math.pi * (t - T_GRAB - 0.3) / 2.6)
            p = dict(p, hip=(p["hip"][0] + 3 * w, p["hip"][1] + 1.5 * abs(w)), lean=p["lean"] + 1.2 * w)
        return p
    if t < T_CLIMB:
        u = seg(t, T_HOOK, 0.55)                                 # springt ab (unter der Welle), wartet am Boden
        p = kl.lerp_pose(POSE_HANG, POSE_STAND, sturz(u))
        if u >= 1:
            if T_S2 + 0.9 <= t < T_S2 + 1.8:                     # schuettelt die Zughand aus
                w = math.sin(2 * math.pi * 3.0 * (t - T_S2 - 0.9)) * math.sin(math.pi * seg(t, T_S2 + 0.9, 0.9))
                p = dict(p, rh=(p["rh"][0] + 14 * w, p["rh"][1] + 6 * abs(w)))
            if t >= T_S3:                                        # schaut zur Spitze (keine neue Info)
                p = kl.lerp_pose(p, POSE_LOOK, seilzug(seg(t, T_S3, 0.8)))
            b = math.sin(2 * math.pi * (t - T_HOOK) / 2.8)
            p = dict(p, hip=(p["hip"][0], p["hip"][1] + 1.8 * b), lean=p["lean"] + 0.7 * b)
        return p
    u = seg(t, T_CLIMB, 1.0)                                     # Folge: steigt wieder ein und kneift die Tufa
    p = kl.lerp_pose(POSE_LOOK, POSE_HANG1, seilzug(u))
    if u >= 1:
        w = math.sin(2 * math.pi * (t - T_CLIMB - 1.0) / 2.6)
        p = dict(p, hip=(p["hip"][0] + 3 * w, p["hip"][1] + 1.5 * abs(w)), lean=p["lean"] + 1.2 * w)
    return p


# ------------------------------------------------------------------ META
META = dict(
    slug="2026-10-23_holdid-02", dur_range=[17.0, 24.0], payoff_t=T_S4, abspann_ab=T_END,
    title="GeoCrimps r005 HOLD ID #02 (Offene Frage), Fassung 1", ablauf="offene_frage",
    hook1_bis=T_OUT, hook_ab=T_Q, hook_bis=T_HOOK, weitere_fragen=[[T_CALL, T_S4]], cover_t=round(T_Q + 0.85, 2),
    on_screen=["HOLD ID", "TUFA ON LIMESTONE:", "HOW DID THIS HOLD FORM?", "WATER SEEPS OUT.", "BUT IT LOSES CO₂…",
               "CARVED OUT?", "DRIP BY DRIP.", "HOLD ID #02", "A GROWN-ON HOLD.", rk.Outro.CTA],
    labels=["CO₂"],
    verdauen=["DRIP BY DRIP.", "A GROWN-ON HOLD."],
    qc_times=[0.0, T_GRAB, T_GEO, 1.1, 1.6, round(T_Q + 0.85, 2), round(T_HOOK - 0.2, 2), round(T_S2 + 1.2, 2),
              round(T_Z1 + 0.1, 2), round(T_G0 + 1.3, 2), round(T_CALL + 1.0, 2), round(T_S4 + 0.6, 2),
              round(T_S5 - 0.25, 2), round(T_FAZ + 1.0, 2), round(T_END - 0.1, 2), round(T_END + 2.0, 2)],
    marks=[(0, "Hook 1"), (T_GRAB, "Griff"), (T_GEO, "x GEOLOGY"), (T_Q, "Hook 2"), (T_HOOK, "Welle"),
           (T_S2, "Zug 1"), (T_Z0, "Zoom"), (T_S3, "Zug 2"), (T_G0, "Zeitraffer"), (T_CALL, "Callback"),
           (T_S4, "PAYOFF"), (T_S5, "Zoom zurueck"), (T_STAMP, "Stempel"), (T_FAZ, "Fazit"), (T_END, "Abspann")])


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
        self.label = m.text_sprite("HOLD ID", X0, rk.FORMAT_Y, "stencil", 40, C["slate"], tracking=0.12)

        wall_poly = o.ragged(-20, ROOF, 1100, YG, seed=6, amp=6, n=30, top_only=True)
        self.wall_poly = wall_poly

        def bg(im):
            o.contour_field(im, 760, 520, n=8, r0=120, step=58, alpha=70)        # Hoehlendunkel ueber dem Dach
            d = ImageDraw.Draw(im)
            d.polygon([P(x, y) for x, y in wall_poly], fill=o.rgb(WALL))
            mask = Image.new("L", im.size, 0); ImageDraw.Draw(mask).polygon([P(x, y) for x, y in wall_poly], fill=255)
            yy = np.mgrid[0:im.size[1], 0:im.size[0]][0].astype(np.float32) / o.S
            sh = Image.new("RGBA", im.size, o.rgb(C["obsidian"]))              # Dach wirft Schatten nach unten
            sh.putalpha(Image.fromarray((np.asarray(mask, np.float32) * np.clip(1 - (yy - ROOF) / 260, 0, 1) * 0.55).astype(np.uint8)))
            im.alpha_composite(sh)
            rnd = random.Random(5)
            for _ in range(700):
                x = rnd.uniform(0, 1080); y = rnd.uniform(ROOF + 12, YG - 6)
                if abs(x - tcx(y)) < 60 and y < L1 + 10:
                    continue
                r = rnd.uniform(1.2, 2.6); d.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=o.rgb(rnd.choice([C["line"], "#39434C"])))
            for x0, y0, x1, y1 in ((150, 1080, 330, 1092), (720, 960, 990, 975), (760, 1240, 1010, 1256), (90, 1380, 260, 1392)):
                d.line([P(x0, y0), P((x0 + x1) / 2, y0 + 6), P(x1, y1)], fill=o.rgb(C["line"]), width=int(3 * o.S))
            o.pocket(im, POCKET[0] - 2, POCKET[1] + 8, 24, 14)
            d.line([P(x, y) for x, y in wall_poly[:31]], fill=o.rgb(C["slate"]), width=int(3 * o.S))   # Dachkante
            lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
            ImageDraw.Draw(lay).rectangle([P(-10, YG), P(1090, 1930)], fill=o.rgb(C["graphite"], 255))
            im.alpha_composite(lay)
            rnd = random.Random(3)
            for _ in range(120):
                x, y = rnd.uniform(10, 1070), rnd.uniform(YG + 14, 1900); r = rnd.uniform(1.5, 3.5)
                d.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=o.rgb(C["line"]))
            d.line([P(-10, YG), P(1090, YG)], fill=o.rgb(C["slate"]), width=int(3 * o.S))
            d.ellipse([P(tcx(L1) - 70, YG + 8), P(tcx(L1) + 70, YG + 22)], fill=o.rgb(C["water"], 110))   # Pfuetze
        self.bg = m.background(bg)

        # Hook 2: Gestein und Gegenstand in Tufa-Farbe, darunter die Frage (rechts frei fuer die Tufa)
        self.hook_kick = m.text_sprite("TUFA ON LIMESTONE:", X0, rk.HOOK_Y, "display", 96, TUFA)
        self.hook, _ = m.lines_sprite(["HOW DID THIS", "HOLD FORM?"], rk.HOOK_Y + 112, size=136)
        # Hook 1: Wand klappt in ihren Kalk auf (Ziegelmuster, Baenke), die Tufa bleibt aussen vor
        beds = [[(x, y0 + 5 * math.sin(x / 130 + k)) for x in range(-20, 1101, 20)] for k, y0 in enumerate(range(930, YG, 96))]
        self.geo = kl.GeoReveal(wall_poly, "limestone", PINCH0[0], PINCH0[1], pat_alpha=70, beds=beds,
                                holes=[tufa_poly(L0)], seed=8)
        # Texte
        self.text1, _ = m.lines_sprite(["WATER", "SEEPS OUT."], 352, role="display_xb", size=118)
        self.text2, _ = m.lines_sprite(["BUT IT", "LOSES CO₂…"], 352, role="display_xb", size=118)
        self.call, _ = m.lines_sprite(["CARVED", "OUT?"], 352, role="display_xb", size=118)
        self.answer, _ = m.lines_sprite(["DRIP BY DRIP."], 352, size=200)
        self.co2 = m.text_sprite("CO₂", 0, 0, "mono", 38, C["ice"], tracking=0.1)
        self.stamp = self.make_stamp(X0 + 250, 420, -6)
        self.stamp.text = "HOLD ID #02"
        self.fazit, _ = m.lines_sprite(["A GROWN-ON", "HOLD."], 540, size=136)
        self.drop = m.sprite(lambda im: o.droplet(im, 540, 960, size=13))
        self.tcache = {}

    def make_stamp(self, cx, cy, angle):
        s = o.S; f1 = o.font("stencil", 76); t1 = "HOLD ID #02"
        w1 = f1.getlength(t1); bw = int(w1 + 2 * 30 * s); bh = int((76 + 2 * 22) * s)
        im = Image.new("RGBA", (bw + 40 * s, bh + 40 * s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        ox, oy = 20 * s, 20 * s; col = o.rgb(C["magnesia"])
        d.rounded_rectangle([ox, oy, ox + bw, oy + bh], radius=14 * s, outline=col, width=6 * s)
        d.text((ox + bw / 2, oy + bh / 2 + 4 * s), t1, font=f1, fill=col, anchor="mm")
        rng = np.random.default_rng(7)
        a = np.asarray(im.getchannel("A"), np.float32)
        noise = np.asarray(Image.fromarray((rng.random(a.shape) * 255).astype(np.uint8)).resize(im.size), np.float32) / 255
        a *= np.clip(1.4 - noise * 1.05, 0.3, 1.0)
        im.putalpha(Image.fromarray(a.astype(np.uint8)))
        im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
        small = im.resize((im.width // s, im.height // s), Image.LANCZOS)
        return m.Sprite(small, int(cx - small.width / 2), int(cy - small.height / 2))

    # -------------------------------------------------------------- Tufa (2x, je Frame; Laengsschnitt mit Lagen)
    def tufa(self, L, cut, glow=None):
        key = (round(L, 1), round(cut, 2), None if glow is None else round(glow, 2))
        if key in self.tcache:
            return self.tcache[key]

        def draw(d, X, Y):
            poly = tufa_poly(L)
            d.polygon([(X(x), Y(y)) for x, y in poly], fill=o.rgb(TUFA))
            if cut > 0:                                          # Laengsschnitt: dunkler Kern, helle Anwachslagen
                d.polygon([(X(x), Y(y)) for x, y in poly], fill=o.rgb(TUFA_IN, int(255 * cut)))
                lagen = [s for s in STAGES + NEW if s <= L + 0.5]
                for k, s in enumerate(lagen):
                    a = int(220 * cut)
                    col = TUFA_LINE
                    if glow is not None:                         # Payoff: Lagen leuchten nacheinander von innen nach aussen
                        g = max(0.0, 1 - abs(glow * (len(lagen) + 2) - k - 1) / 1.6)
                        if g > 0:
                            col, a = C["magnesia"], int(255 * cut)
                    d.line([(X(x), Y(y)) for x, y in tufa_outline(s)], fill=o.rgb(col, a), width=int((2.4 + (1.2 if col == C["magnesia"] else 0)) * o.S))
            else:
                rnd = random.Random(9)                           # Aussenhaut: Knollen und Rillen
                for _ in range(26):
                    y = rnd.uniform(ROOF + 20, L - 30); hw = thw(y, L)
                    if hw < 10:
                        continue
                    x = tcx(y) + rnd.uniform(-0.6, 0.6) * hw
                    d.arc([X(x - 10), Y(y - 6), X(x + 10), Y(y + 6)], 200, 340, fill=o.rgb("#A89C80"), width=int(2 * o.S))
            d.line([(X(x), Y(y)) for x, y in poly[1:-1]], fill=o.rgb(C["magnesia"]), width=int(3 * o.S), joint="curve")
        spr = rk.region(560, ROOF - 10, 730, L + 8, draw)
        if len(self.tcache) > 400:
            self.tcache.clear()
        self.tcache[key] = spr
        return spr

    # -------------------------------------------------------------- Welt (vor dem Zoom)
    def world(self, t):
        f = self.bg.copy()
        L = tip_len(t)
        cut = seilzug(seg(t, T_CUT, 0.5)) * (1 - seg(t, T_S5 + 0.3, 0.6))
        glow = seg(t, T_S4, 1.6) if T_S4 <= t < T_S4 + 1.6 else None
        u = seilzug(seg(t, T_GEO, 0.5))                          # Hook 1: Wand klappt in ihren Kalk auf
        if u > 0 and t < T_OUT + 0.4:
            self.geo.put(f, u, fade=1 - seg(t, T_OUT, 0.4))
        put(f, self.tufa(L, cut, glow))
        dr = ImageDraw.Draw(f)
        tipx = tcx(L)
        # Zug 1: Wasserfilm laeuft an der Tufa herab (rechte Flanke), glaenzt danach weiter
        if T_S2 <= t < T_S5 + 0.3:
            v = seilzug(seg(t, T_S2 + 0.15, 1.1))
            yb = ROOF + (L - ROOF) * v
            ys = np.linspace(ROOF + 4, max(ROOF + 5, yb - 6), 60)
            pts = [(tcx(y) + thw(y, L) - 5, y) for y in ys]
            a = int(200 * (0.75 + 0.25 * math.sin(t * 5))) if v >= 1 else 220
            if len(pts) > 1:
                dr.line(pts, fill=o.rgb(C["water"], a), width=4)
            dr.ellipse([tcx(ROOF + 6) + 18, ROOF - 3, tcx(ROOF + 6) + 34, ROOF + 7], fill=o.rgb(C["water"], 230))
        # Tropfen an der Spitze: ruhig (ab Hook 2), im Zeitraffer je Zyklus ein Tropfen mit CO2-Blaeschen
        if t >= T_Q:
            if T_G0 <= t < T_G1:
                k = int((t - T_G0) / CYC); tc = t - T_G0 - k * CYC
                swell = seilzug(min(1.0, tc / 0.3))
                if tc < 0.32:
                    r = 4 + 6 * swell
                    dr.ellipse([tipx - r, L - 2, tipx + r, L - 2 + 2.2 * r], fill=o.rgb(C["water"], 235))
                for b in range(4):                                # Blaeschen steigen aus dem Tropfen auf
                    bt = tc - 0.04 - 0.06 * b
                    if 0 < bt < 0.5:
                        bx = tipx + 16 + 10 * b + 20 * bt; by = L + 8 - 90 * bt - 8 * b
                        rr = 4.0 + 1.5 * (b % 2)
                        dr.ellipse([bx - rr, by - rr, bx + rr, by + rr], outline=o.rgb(C["ice"], int(240 * (1 - bt / 0.5))), width=2)
                fv = seg(tc, 0.3, 0.3)
                if 0 < fv < 1:
                    put(f, self.drop, dx=tipx - 540, dy=L + 10 + (YG - L) * fv * fv - 960, op=1 - 0.3 * fv)
                if tc >= 0.3:                                    # neue Lage blitzt auf
                    lay = NEW[min(k, NCYC - 1)]
                    a = int(255 * (1 - seg(tc, 0.3, 0.3)))
                    if a > 0 and cut > 0.5:
                        dr.line([(x, y) for x, y in tufa_outline(min(lay, L))], fill=o.rgb(C["magnesia"], a), width=4)
            else:
                per = 1.35; tc = (t - T_Q) % per; v = seg(tc, 0.0, 0.9)
                r = 3 + 6 * seilzug(v)
                if tc < 0.95:
                    dr.ellipse([tipx - r, L - 2, tipx + r, L - 2 + 2.2 * r], fill=o.rgb(C["water"], 235))
                fv = seg(tc, 0.95, 0.35)
                if 0 < fv < 1:
                    put(f, self.drop, dx=tipx - 540, dy=L + 10 + (YG - L) * fv * fv - 960)
                rs = seg((t - T_Q - 1.3) % per, 0, 0.6)          # Ring in der Pfuetze
                if t - T_Q > 1.3 and rs < 1:
                    rx = 14 + 50 * rs
                    dr.ellipse([tipx - rx, YG + 15 - rx * 0.18, tipx + rx, YG + 15 + rx * 0.18], outline=o.rgb(C["ice"], int(200 * (1 - rs))), width=2)
        put(f, self.climber.sprite(climber_pose(t)))
        kl.chalk_puff(f, t, T_GRAB, PINCH0[0], PINCH0[1] - 4, seed=11)
        kl.chalk_puff(f, t, T_HOOK + 0.55, 330, YG - 6, seed=13, size=0.7)                 # Landung
        kl.chalk_puff(f, t, T_S2 + 1.05, POSE_STAND["rh"][0], POSE_STAND["rh"][1], seed=14, size=0.45)
        kl.chalk_puff(f, t, T_CLIMB + 0.95, PINCH1[0], PINCH1[1] - 4, seed=15, size=0.8)
        return f

    def label_co2(self, f, t, z):
        """Label CO2 neben den Blaeschen (im Zoom, Bildkoordinaten), steht waehrend des Zeitraffers."""
        u = seg(t, T_S3 + 0.1, EIN)
        if u <= 0 or t >= T_G1 + 0.6:
            return
        L = tip_len(t)
        bx, by = tcx(L) + 40, L - 30
        sx = ZC[0] + (bx - ZC[0]) * z; sy = ZC[1] + (by - ZC[1]) * z
        put(f, self.co2, dx=sx + 30 - self.co2.x, dy=sy - 60 - self.co2.y, op=seilzug(u) * (1 - seg(t, T_G1 + 0.3, 0.3)))

    # -------------------------------------------------------------- Frames
    def frame(self, t):
        if t < T_HOOK + 0.5:                                     # Szene 1: Hook
            f = m.zoomed(self.world(t), 1 + 0.03 * seilzug(seg(t, 0, T_HOOK)), 640, 1100)
            put(f, self.rails[0])
            self.hook1.draw(f, t, hook_bis=T_HOOK)
            u = seilzug(seg(t, T_Q, EIN))
            if u > 0:
                fade = 1 - seg(t, T_HOOK, 0.12)
                put(f, self.label, dx=lerp(-30, 0, u), op=u * fade)
                put(f, self.hook_kick, dx=lerp(-40, 0, u), op=u * fade)
                put(f, self.hook, dx=lerp(-40, 0, u), op=u * fade)
            if t >= T_HOOK:
                put(f, rk.wave(seg(t, T_HOOK, 0.5), cx=tcx(L0), cy=L0))
            return f, 51
        if t < T_S5:
            z = 1.0 if t < T_Z0 else lerp(1.0, ZOOM, seilzug(seg(t, T_Z0, T_Z1 - T_Z0)))
            if t >= T_S4:                                        # langsamer Push-in, solange die Aufloesung steht
                z *= lerp(1.0, PUSH, 0.5 - 0.5 * math.cos(math.pi * seg(t, T_S4, T_S5 - T_S4)))
            f = m.zoomed(self.world(t), z, *ZC)
            if t < T_S3:                                         # Szene 2: Zug 1
                put(f, self.rails[1]); self.rail.pop(f, t, 0, T_S2)
                u = seilzug(seg(t, T_S2 + 0.05, EIN)); put(f, self.text1, dx=lerp(-40, 0, u), op=u * (1 - seg(t, T1_OFF, 0.25)))
                return f, 52
            put(f, self.rails[3] if t >= T_S4 else self.rails[2])   # Szene 3: Zug 2, Callback, Payoff
            self.rail.pop(f, t, 1, T_S3)
            u = seilzug(seg(t, T_S3 + 0.05, EIN)); put(f, self.text2, dx=lerp(-40, 0, u), op=u * (1 - seg(t, T2_OFF, 0.25)))
            self.label_co2(f, t, z)
            u = seilzug(seg(t, T_CALL, EIN)); put(f, self.call, dx=lerp(-30, 0, u), op=u * (1 - seg(t, T_S4, 0.12)))
            u = seg(t, T_S4, 0.3)
            if u > 0:
                self.rail.logo_pop(f, t, T_S4)
                put(f, self.answer, op=min(1, u * 2) * (1 - seg(t, T_S5 - 0.2, 0.2)), scale=lerp(1.18, 1.0, seilzug(u)), anchor=(X0, 352))
            return f, 53
        if t < T_END:                                            # Szene 4: Folge
            z = lerp(ZOOM * PUSH, 1.0, seilzug(seg(t, T_S5, 0.8)))
            z *= 1 + 0.03 * (0.5 - 0.5 * math.cos(math.pi * seg(t, T_S5 + 0.8, T_END - T_S5 - 0.8)))
            f = m.zoomed(self.world(t), z, *ZC)
            put(f, self.rails[3])
            u = seg(t, T_STAMP, 0.3)
            if u > 0:
                put(f, self.stamp, op=min(1, u * 3), scale=lerp(1.65, 1.0, griff(u)) if u < 1 else 1.0)
            rk.dust(f, t, T_STAMP + 0.18, (self.stamp.x + 30, self.stamp.y + 30, self.stamp.x + self.stamp.w - 30,
                                           self.stamp.y + self.stamp.h - 30), seed=78)
            u = seilzug(seg(t, T_FAZ, EIN)); put(f, self.fazit, dx=lerp(-40, 0, u), op=u)
            return f, 54
        return self.outro.frame(t, T_END), 55


# ------------------------------------------------------------------ Ton: Musik in D-Dur, 78 BPM
D_, GMAJ7, BM7, EM7, A_, ASUS4, FSM7, EM9 = ([54, 57, 62, 66], [55, 59, 62, 66], [54, 57, 59, 62], [52, 55, 59, 62],
                                            [52, 57, 61, 64], [52, 57, 62], [54, 57, 61, 64], [52, 55, 59, 62, 66])
PENTA = [74, 76, 78, 81, 83, 86, 88]   # D-Dur-Pentatonik ab D5: Tropfen als Toene


def sound_events(b):
    """Musik in D-Dur (78 BPM) nach Szenen, Hook 1 musikalisch, Tropfen als Toene der Pentatonik, im Zeitraffer jeder
    Tropfen ein Ton hoeher (die Tufa waechst), Akkordschlag zur Aufloesung, Klanglogo im Abspann. Geraeusche leise."""
    h1 = rk.Hook1(t_grab=T_GRAB, t_geo=T_GEO, t_out=T_OUT)
    b.hook1(h1, akkord=BM7, bassnote=47)
    b.musik([
        (T_Q - 0.1, T_Q + 1.9, BM7, 47, "ruhig"),               # Frage: offen
        (T_Q + 1.9, T_HOOK, GMAJ7, 43, "ruhig"),
        (T_HOOK, T_S2, D_, 50, "flaeche"),                      # Welle, Absprung
        (T_S2, T_S2 + 1.3, D_, 50, "ruhig"),                    # Wasser tritt aus
        (T_S2 + 1.3, T_Z0, A_, 45, "ruhig"),
        (T_Z0, T_G0, FSM7, 42, "bewegt"),                       # Zoom, Schnitt
        (T_G0, T_G0 + 1.2, EM7, 40, "bewegt"),                  # Zeitraffer
        (T_G0 + 1.2, T_CALL, A_, 45, "bewegt"),
        (T_CALL, T_RISE, BM7, 47, "ruhig"),                     # "CARVED OUT?"
        (T_RISE, T_S4 - 0.15, ASUS4, 45, "flaeche"),            # Steigerung, dann 0,15 s Stille
        (T_S4, T_S5, EM9, 40, "flaeche"),                       # Aufloesung: verdauen
        (T_S5, T_S5 + 1.4, GMAJ7, 43, "ruhig"),                 # Stempel
        (T_S5 + 1.4, T_END, D_, 50, "ruhig"),                   # Fazit: nach D-Dur aufgeloest
        (T_END, DUR, D_, 50, "flaeche"),                        # Abspann
    ], bpm=78.0, gain=-12.0)
    b.synth("whoosh", T_HOOK, -18.0, "welle", dur=0.55, seed=4)
    b.klang("thud", T_HOOK + 0.55, -14.0, "landung", seed=1)
    per, k, tt = 1.35, 0, T_Q + 0.95 + 0.35                      # ruhige Tropfen (landen in der Pfuetze)
    while tt < T_END:
        if not (T_G0 - 0.2 <= tt < T_G1 + 0.2):
            b.ton("zupf", tt, -17.0 - (k % 2), "tropfen", m=PENTA[(0, 2, 1, 3)[k % 4]], dauer=0.7, pan=0.2)
        tt += per; k += 1
    b.ton("zupf", T_S2, -14.0, "bohrhaken", m=81, dauer=0.9)
    b.ton("schwelle", T_Z0 - 0.3, -15.0, "zoom", akkord=FSM7, dauer=0.5)
    b.ton("zupf", T_S3, -14.0, "bohrhaken", m=83, dauer=0.9)
    b.ton("zupf", T_S3 + 0.1, -16.0, "label", m=78, dauer=0.8)
    for c in range(NCYC):                                        # Zeitraffer: Tropfen faellt, neue Lage, Ton steigt
        t0 = T_G0 + c * CYC
        b.ton("zupf", t0 + 0.3, -13.0, "lage", m=PENTA[c + 1], dauer=0.8, pan=0.15 * (c - 1.5))
        b.ton("zupf", t0 + 0.08, -20.0, "blaeschen", m=PENTA[c + 3], dauer=0.4, pan=0.3)
    b.ton("zupf", T_CALL, -10.0, "frage", m=74, dauer=0.9)      # Frage: steigende Quarte
    b.ton("zupf", T_CALL + 0.2, -10.0, "frage", m=79, dauer=1.2)
    b.synth("whoosh", T_S2 + 0.9, -22.0, "hand-ausschuetteln", dur=0.5, seed=12)
    b.ton("schwelle", T_RISE, -8.0, "steigerung", akkord=ASUS4, dauer=T_S4 - 0.15 - T_RISE)
    b.klang("sub_hit", T_S4 - 0.01, -10.0, "payoff-einschlag", f0=78.0, f1=36.0)
    b.ton("akzent", T_S4, -4.0, "payoff", akkord=EM9, bassnote=40)
    for c in range(5):                                           # Lagen leuchten: leise Toene aufwaerts
        b.ton("zupf", T_S4 + 0.35 + 0.22 * c, -17.0, "lagen-leuchten", m=PENTA[c], dauer=0.8)
    b.klang("thud", T_STAMP + 0.16, -9.0, "stempel", seed=8)
    b.ton("zupf", T_STAMP + 0.16, -11.0, "stempel", m=74, dauer=1.0)
    b.klang("chalk_slap", T_CLIMB + 0.95, -12.0, "griff", seed=2)
    b.ton("zupf", T_FAZ, -14.0, "fazit", m=78, dauer=0.9)
    b.klanglogo(T_END + 0.3, tonika=62, gain=-7.0)               # Abspann: Logo (D-Dur)
    b.ton("zupf", T_END + 1.3, -12.0, "herz", m=81, dauer=1.2)


if __name__ == "__main__":
    if "--reach" in sys.argv:
        print(check_reach())
        sys.exit(0)
    rk.run(Reel, sound_events, META)
