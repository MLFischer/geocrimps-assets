#!/usr/bin/env python3
"""Reel 006 -- SCALE JUMP #01: "What's this hold made of?" (Faktenbasis: Post #059, Kreide ist Plankton), Ablauf "erklaerkette".

Fassung 1 vom 21.10.2026 nach PRODUKTION.md (Stand 16.10.2026), Vorlage r003 Fassung 6 (Musik, Tempo, Abspann, Lesezeit),
Erklaerkette wie r002. Format SCALE JUMP: Wand -> Griff -> Wuerfel -> Plaettchen, mit Massstabsbalken.
Hook 1 0-1,45 s: GEOCRIMPS + CLIMBING ab Frame 0, ein Kletterer greift eine Leiste an einer Kreidewand (Kreidewolke),
"x GEOLOGY" schlaegt ein und die Wand klappt in ihre Kalk-Signatur auf (Kreide ist ein Kalkstein; verraet nichts).
Hook 2 ab 1,8 s: Formatlabel SCALE JUMP, Kontextzeile "CHALK ROCK:" (Kreidefarbe) ueber "WHAT'S THIS HOLD MADE OF?",
steht 3,75 s; der Kletterer haengt an der Leiste.
Zug 1: Lupenkreis-Sprung vom Griff in einen 1-cm-Wuerfel (Massstab "1 CM · KANSAS"): "SUGAR-CUBE SIZE."
Zug 2: zweiter Lupenkreis-Sprung in den Wuerfel, Feld aus Coccolithen und Bruchstuecken (Massstab 10 µm):
"UP TO 6 BILLION PLATES."
Zug 3: Kamerafahrt nach oben ins Meer: eine Alge (Coccosphaere) treibt: "ALGAE BUILT THEM." Sie zerfaellt, die Plaettchen
sinken, Kamerafahrt zurueck in den Fels; Wendung: nur die ganzen Plaettchen leuchten: "INTACT: A FIFTH AT MOST."
Payoff: "BROKEN PLANKTON." gross mit Push-in. Folge: der Lupenkreis schliesst sich zurueck auf den Griff, der Kletterer
zieht durch: "PULLING ON PLANKTON." Abspann mit LIKE & FOLLOW.
Fakten (v2/faktenbasis/059/sources.md): Coccolithen = Skelettplaettchen einzelliger Algen, 1-20 µm, meist 4-12 µm;
5,3 x 10^8 bis 6,1 x 10^9 je cm³ in der Greenhorn-Kreide, Kansas (Hattin & Darko 1971); ganze Coccolithen <= 20 Vol.-%
(vorlaeufig), viel Matrix aus zerfallenen Coccolithen; Plaettchen sinken nach dem Tod zum Meeresboden und werden zu
Kreide (AGU 2016, Nachtrag 21.10.2026); an Kreidefelsen wird geklettert (BMC RAD, Nachtrag 21.10.2026).
Bildmittel (Abwechslungsregel): Uebergang Lupenkreis-Sprung (Massstabssprung) und Kamerafahrt (r005: Isolinien-Welle und
Zoom) | Enthuellung Massstabssprung mit Massstabsbalken, Zeitraffer Absinken (r005: Laengsschnitt mit Lagen) | Payoff
Antwort gross, ganze Plaettchen leuchten, Kletterer zieht durch, kein Stempel (r005: Stempel HOLD ID) | Musik F-Dur, 86 BPM
(r005: D-Dur 78 BPM).
Aufruf:  python3 r006_scalejump_059.py --out ../../../reels --qc <Ordner>   (--stills 0,4.8 fuer Einzelbilder, --reach)
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
T_GRAB, T_GEO, T_OUT = 0.40, 0.72, 1.45                       # Hook 1
T_Q = 1.80                                                    # Hook 2
T_HOOK = T_Q + 3.75                                           # Frage steht 3,75 s, dann Sprung 1
J1_0, J1_1 = T_HOOK, T_HOOK + 0.8                             # Lupenkreis: Griff -> Wuerfel
T_S2 = J1_1 + 0.05                                            # Zug 1: "SUGAR-CUBE SIZE." + Massstab
T1_OFF = T_S2 + 1.95
J2_0 = T1_OFF + 0.15
J2_1 = J2_0 + 0.8                                             # Lupenkreis: Wuerfel -> Plaettchen
T_S3 = J2_1 + 0.4                                             # Zug 2: "UP TO 6 BILLION PLATES."
T2_OFF = T_S3 + 3.0
P_UP0 = T2_OFF + 0.15                                         # Kamerafahrt nach oben ins Meer
P_UP1 = P_UP0 + 0.8
T_S4 = P_UP1 + 0.05                                           # Zug 3: "ALGAE BUILT THEM."
T3_OFF = T_S4 + 2.25
T_BREAK = T3_OFF                                              # Alge zerfaellt
P_DN0 = T_BREAK + 0.25
P_DN1 = P_DN0 + 0.8                                           # Kamerafahrt zurueck in den Fels
T_S5 = P_DN1 + 0.4                                            # Wendung: "INTACT: A FIFTH AT MOST."
T4_OFF = T_S5 + 3.0
T_RISE = T4_OFF - 1.0
T_P = T4_OFF + 0.15                                           # Payoff "BROKEN PLANKTON."
T_S6 = T_P + 2.6                                              # Folge: Lupenkreis zurueck, Kletterer zieht
J3_1 = T_S6 + 0.8
T_PULL = T_S6 + 0.45
T_FAZ = T_S6 + 0.6                                            # Fazit "PULLING ON PLANKTON."
T_END = T_FAZ + 3.1
DUR = T_END + rk.Outro.DUR

# ------------------------------------------------------------------ Szene 1: Kreidewand mit Kletterer
TOP, YG = 860, 1500
CHALK, CHALK_D, CHALK_L = "#BDB6A6", "#958F80", "#D8D2C4"     # Kreide (Zusatzfarbe, sparsam)
BACK = dict(sw=22, hw=13, eb=(-1, 1), kb=(1, -1))
EDGE = (604, 1008)                                            # Leiste: der Griff dieses Reels
POCKET = (436, 990)
HIGH = (492, 905)                                             # hoehere Leiste fuer den Durchzug
FOOT_L, FOOT_R = (452, 1318), (572, 1300)
FOOT_L2, FOOT_R2 = (474, 1236), (590, 1222)
POSE_START = dict(BACK, hip=(498, 1212), lean=-3, lh=POCKET, rh=(560, 1112), lf=(446, 1338), rf=(560, 1326))
POSE_HANG = dict(BACK, hip=(516, 1172), lean=7, lh=POCKET, rh=EDGE, lf=FOOT_L, rf=FOOT_R)
POSE_SWING = dict(POSE_HANG, hip=(522, 1162), lean=10)
POSE_PULL = dict(BACK, hip=(548, 1096), lean=3, lh=HIGH, rh=EDGE, lf=FOOT_L2, rf=FOOT_R2)
JUMP_Z = 2.3                                                  # Zoom der Aussenszene beim Sprung


def check_reach():
    cl = kl.Climber(scale=1.0, width=18.0, torso_w=36.0); out = {}
    for name, p in (("start", POSE_START), ("hang", POSE_HANG), ("swing", POSE_SWING), ("pull", POSE_PULL)):
        j = cl.joints(p)
        out[name] = round(max(math.dist(j[k], p[k]) for k in ("lh", "rh", "lf", "rf")), 2)
    return out


def climber_pose(t):
    if t < T_GRAB:
        return kl.lerp_pose(POSE_START, POSE_SWING, seilzug(seg(t, 0.0, T_GRAB)))
    if t < T_S6:
        u = seg(t, T_GRAB, 0.3)
        p = kl.lerp_pose(POSE_SWING, POSE_HANG, 0.5 - 0.5 * math.cos(math.pi * u))
        if u >= 1:                                             # haengt, atmet, pendelt leicht
            w = math.sin(2 * math.pi * (t - T_GRAB - 0.3) / 2.6)
            p = dict(p, hip=(p["hip"][0] + 3 * w, p["hip"][1] + 1.5 * abs(w)), lean=p["lean"] + 1.2 * w)
        return p
    u = seg(t, T_PULL, 0.9)                                     # Folge: zieht durch an die hoehere Leiste
    p = kl.lerp_pose(POSE_HANG, POSE_PULL, 0.5 - 0.5 * math.cos(math.pi * u))
    if u >= 1:
        w = math.sin(2 * math.pi * (t - T_PULL - 0.9) / 2.8)
        p = dict(p, hip=(p["hip"][0] + 2 * w, p["hip"][1] + 1.5 * abs(w)), lean=p["lean"] + 0.8 * w)
    return p


# ------------------------------------------------------------------ Coccolithen (Draufsicht, 2x)
def ring_pts(cx, cy, r, sq, rot, a0=0.0, a1=2 * math.pi, n=40):
    c, s = math.cos(rot), math.sin(rot); pts = []
    for k in range(n + 1):
        a = a0 + (a1 - a0) * k / n
        x, y = r * math.cos(a), r * sq * math.sin(a)
        pts.append((cx + x * c - y * s, cy + x * s + y * c))
    return pts


def coccolith(d, X, Y, cx, cy, r, sq, rot, col, body, alpha=255, w=2.0, a0=None, a1=None):
    """Plaettchen wie ein Rad: Aussenrand, Speichen, Innenring, Mitte. a0/a1: nur ein Bruchstueck (Sektor)."""
    Q = lambda pts: [(X(x), Y(y)) for x, y in pts]
    if a0 is None:
        d.polygon(Q(ring_pts(cx, cy, r, sq, rot)), fill=o.rgb(body, alpha), outline=o.rgb(col, alpha))
        d.line(Q(ring_pts(cx, cy, r, sq, rot)), fill=o.rgb(col, alpha), width=max(1, int(w * o.S)))
        d.line(Q(ring_pts(cx, cy, r * 0.52, sq, rot)), fill=o.rgb(col, alpha), width=max(1, int(w * o.S)))
        d.polygon(Q(ring_pts(cx, cy, r * 0.22, sq, rot, n=18)), fill=o.rgb(col, int(alpha * 0.8)))
        a0, a1, full = 0.0, 2 * math.pi, True
    else:
        outer = ring_pts(cx, cy, r, sq, rot, a0, a1, 16); inner = ring_pts(cx, cy, r * 0.52, sq, rot, a0, a1, 10)
        d.polygon(Q(outer + inner[::-1]), fill=o.rgb(body, alpha))
        d.line(Q(outer), fill=o.rgb(col, alpha), width=max(1, int(w * o.S)))
        d.line(Q(inner), fill=o.rgb(col, alpha), width=max(1, int(w * o.S)))
        full = False
    n = 22 if full else max(2, int(22 * (a1 - a0) / (2 * math.pi)))
    for k in range(n + (0 if full else 1)):
        a = a0 + (a1 - a0) * k / n
        p1 = ring_pts(cx, cy, r * 0.55, sq, rot, a, a, 1)[0]; p2 = ring_pts(cx, cy, r * 0.96, sq, rot, a, a, 1)[0]
        d.line(Q([p1, p2]), fill=o.rgb(col, int(alpha * 0.75)), width=max(1, int(w * 0.6 * o.S)))


PLATE, PLATE_B, FRAG, GRAIN, MATRIX = "#D9D4C7", "#5E625F", "#8E918C", "#4C535A", "#1B2025"
SEA0, SEA1 = "#0F1C26", "#162833"
CANV_H, SEAFLOOR = 3420, 1250                                 # hohe Leinwand: Meer oben, Fels darunter
V_SED, V_SEA = 1340, 0                                        # Kamera-Versatz: im Fels / im Meer


def build_field():
    """Feld aus ganzen Coccolithen (wenige, gross), Bruchstuecken und feinem Korn (viel)."""
    rnd = random.Random(21)
    intact = []
    tries = 0
    while len(intact) < 52 and tries < 6000:
        tries += 1
        r = rnd.uniform(46, 66); x = rnd.uniform(-20, 1100); y = rnd.uniform(SEAFLOOR + 40, CANV_H - 20)
        if all(math.hypot(x - a, y - b) > r + rb + 24 for a, b, rb, *_ in intact):
            intact.append((x, y, r, rnd.uniform(0.55, 0.95), rnd.uniform(0, math.pi)))
    frags = []
    for _ in range(520):
        r = rnd.uniform(24, 58); a0 = rnd.uniform(0, 6.28)
        frags.append((rnd.uniform(-20, 1100), rnd.uniform(SEAFLOOR + 20, CANV_H), r, rnd.uniform(0.5, 0.95),
                      rnd.uniform(0, math.pi), a0, a0 + rnd.uniform(0.5, 1.6)))
    return intact, frags


INTACT, FRAGS = build_field()

# Coccosphaere: Plaettchen auf einer Kugel (Mittelpunkt, Radius), Zerfall ab T_BREAK
SPH_C, SPH_R = (600, 900), 104


def sphere_plates():
    rnd = random.Random(5); out = []
    for k in range(18):
        th = math.acos(1 - 2 * (k + 0.5) / 18); ph = k * 2.39996
        x, y, z = math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th)
        if z < -0.15:
            continue
        land = rnd.uniform(140, 1000)
        out.append(dict(x=x, y=y, z=z, r=rnd.uniform(40, 48), land=land, delay=rnd.uniform(0, 0.25),
                        breaks=(k % 3 == 0), rot=rnd.uniform(0, math.pi)))
    return sorted(out, key=lambda q: q["z"])


SPH = sphere_plates()


# ------------------------------------------------------------------ META
META = dict(
    slug="2026-10-27_scalejump-01", dur_range=[21.0, 30.0], payoff_t=T_P, abspann_ab=T_END,
    title="GeoCrimps r006 SCALE JUMP #01 (Erklaerkette), Fassung 1", ablauf="erklaerkette",
    hook1_bis=T_OUT, hook_ab=T_Q, hook_bis=T_HOOK, weitere_fragen=[], cover_t=round(T_Q + 0.85, 2),
    on_screen=["SCALE JUMP", "CHALK ROCK:", "WHAT'S THIS HOLD MADE OF?", "SUGAR-CUBE SIZE.", "UP TO 6 BILLION PLATES.",
               "ALGAE BUILT THEM.", "INTACT: A FIFTH AT MOST.", "BROKEN PLANKTON.", "PULLING ON PLANKTON.", rk.Outro.CTA],
    labels=["1 CM · KANSAS", "10 µm"],
    verdauen=["BROKEN PLANKTON.", "PULLING ON PLANKTON."],
    qc_times=[0.0, T_GRAB, T_GEO, 1.1, 1.6, round(T_Q + 0.85, 2), round(T_HOOK - 0.2, 2), round(J1_0 + 0.4, 2),
              round(T1_OFF - 0.1, 2), round(J2_0 + 0.4, 2), round(T2_OFF - 0.1, 2), round(T3_OFF - 0.3, 2),
              round(P_DN0 + 0.2, 2), round(T4_OFF - 0.2, 2), round(T_P + 1.5, 2), round(T_S6 + 0.4, 2),
              round(T_END - 0.1, 2), round(T_END + 2.0, 2)],
    marks=[(0, "Hook 1"), (T_GRAB, "Griff"), (T_GEO, "x GEOLOGY"), (T_Q, "Hook 2"), (J1_0, "Sprung 1"),
           (T_S2, "Zug 1"), (J2_0, "Sprung 2"), (T_S3, "Zug 2"), (P_UP0, "Meer"), (T_S4, "Zug 3"),
           (T_BREAK, "Zerfall"), (T_S5, "Wendung"), (T_P, "PAYOFF"), (T_S6, "zurueck"), (T_FAZ, "Fazit"),
           (T_END, "Abspann")])


# ------------------------------------------------------------------ Reel
class Reel(rk.ReelBase):
    DUR = DUR

    def __init__(self):
        super().__init__()
        self.rail = rk.Rail(3)
        self.outro = rk.Outro()
        self.rails = [rk.rail_sprite(k, 3) for k in range(4)] + [rk.rail_sprite(3, 3, logo_on=True)]
        self.hook1 = rk.Hook1(t_grab=T_GRAB, t_geo=T_GEO, t_out=T_OUT)
        self.climber = kl.Climber(scale=1.0, width=18.0, torso_w=36.0)
        self.label = m.text_sprite("SCALE JUMP", X0, rk.FORMAT_Y, "stencil", 40, C["slate"], tracking=0.12)
        self.build_cliff()
        self.build_cube()
        self.build_micro()
        # Texte
        self.hook_kick = m.text_sprite("CHALK ROCK:", X0, rk.HOOK_Y, "display", 96, CHALK_L)
        self.hook, _ = m.lines_sprite(["WHAT'S THIS", "HOLD MADE OF?"], rk.HOOK_Y + 112, size=136)
        self.text1, _ = m.lines_sprite(["SUGAR-CUBE", "SIZE."], 352, role="display_xb", size=118)
        self.text2, _ = m.lines_sprite(["UP TO 6 BILLION", "PLATES."], 352, role="display_xb", size=118)
        self.text3, _ = m.lines_sprite(["ALGAE", "BUILT THEM."], 352, role="display_xb", size=118)
        self.text4, _ = m.lines_sprite(["INTACT:", "A FIFTH AT MOST."], 352, role="display_xb", size=118)
        self.answer, _ = m.lines_sprite(["BROKEN", "PLANKTON."], 352, size=200)
        self.fazit, _ = m.lines_sprite(["PULLING ON", "PLANKTON."], 470, size=136)
        self.shade = m.sprite(self._shade)

    @staticmethod
    def _shade(im):
        """Dunkler Verlauf hinter den Zug-Texten (Lesbarkeit ueber dem Plaettchen-Feld)."""
        a = np.zeros((H * o.S, W * o.S), np.float32)
        yy = np.arange(H * o.S) / o.S
        col = np.clip(np.where(yy < 620, 1.0, 1 - (yy - 620) / 260), 0, 1) * np.clip((yy - 180) / 120, 0, 1)
        a[:] = (col * 175)[:, None]
        lay = Image.new("RGBA", im.size, o.rgb(C["obsidian"])); lay.putalpha(Image.fromarray(a.astype(np.uint8)))
        im.alpha_composite(lay)

    # -------------------------------------------------------------- Kreidewand
    def build_cliff(self):
        wall = o.ragged(-20, TOP, 1100, YG, seed=9, amp=10, n=26, top_only=True)
        self.wall = wall

        def bg(im):
            o.contour_field(im, 820, 520, n=8, r0=110, step=60, alpha=70)
            d = ImageDraw.Draw(im)
            d.polygon([P(x, y) for x, y in wall], fill=o.rgb(CHALK))
            mask = Image.new("L", im.size, 0); ImageDraw.Draw(mask).polygon([P(x, y) for x, y in wall], fill=255)
            xx = np.mgrid[0:im.size[1], 0:im.size[0]][1].astype(np.float32) / o.S
            sh = Image.new("RGBA", im.size, o.rgb(C["obsidian"]))       # rechts im Schatten
            sh.putalpha(Image.fromarray((np.asarray(mask, np.float32) * np.clip((xx - 640) / 900, 0, 1) * 0.45).astype(np.uint8)))
            im.alpha_composite(sh)
            rnd = random.Random(4)
            for _ in range(900):                                  # feine Koernung (neutral, keine Signatur)
                x = rnd.uniform(0, 1080); y = rnd.uniform(TOP + 14, YG - 4); r = rnd.uniform(1.0, 2.2)
                d.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=o.rgb(rnd.choice([CHALK_D, CHALK_L]), 150))
            for k, y0 in enumerate(range(950, YG, 118)):          # Baenke, schwach
                pts = [P(x, y0 + 5 * math.sin(x / 140 + k)) for x in range(-20, 1101, 20)]
                d.line(pts, fill=o.rgb(CHALK_D, 120), width=int(2 * o.S))
            for x0, y0, x1, y1 in ((150, 1120, 300, 1180), (760, 980, 840, 1110), (880, 1300, 990, 1340)):
                d.line([P(x0, y0), P((x0 + x1) / 2 + 8, (y0 + y1) / 2), P(x1, y1)], fill=o.rgb(CHALK_D), width=int(3 * o.S))
            for (hx, hy), w_ in ((EDGE, 62), (HIGH, 52), (FOOT_L, 34), (FOOT_R, 34), (FOOT_L2, 30), (FOOT_R2, 30)):
                d.rectangle([P(hx - w_ / 2, hy + 4), P(hx + w_ / 2, hy + 12)], fill=o.rgb("#6F6A5E"))   # Schatten
                d.line([P(hx - w_ / 2, hy + 3), P(hx + w_ / 2, hy + 3)], fill=o.rgb(CHALK_L), width=int(4 * o.S))
            o.pocket(im, POCKET[0] - 2, POCKET[1] + 8, 24, 14)
            d.line([P(x, y) for x, y in wall[:27]], fill=o.rgb(CHALK_L), width=int(3 * o.S))
            lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
            ImageDraw.Draw(lay).rectangle([P(-10, YG), P(1090, 1930)], fill=o.rgb(C["graphite"], 255))
            im.alpha_composite(lay)
            d.line([P(-10, YG), P(1090, YG)], fill=o.rgb(C["slate"]), width=int(3 * o.S))
            kl.crash_pad(im, 330, 690, YG + 4, h=40)
        self.cliff_bg = m.background(bg)
        beds = [[(x, y0 + 5 * math.sin(x / 140 + k)) for x in range(-20, 1101, 20)] for k, y0 in enumerate(range(950, YG, 118))]
        self.geo = kl.GeoReveal(wall, "limestone", EDGE[0], EDGE[1], color="#4A463E", pat_alpha=120, beds=beds, seed=8)

    def cliff(self, t):
        f = self.cliff_bg.copy()
        u = seilzug(seg(t, T_GEO, 0.5))
        if u > 0 and t < T_OUT + 0.4:
            self.geo.put(f, u, fade=1 - seg(t, T_OUT, 0.4))
        if t >= T_Q:                                              # Kreidestaub rieselt im Licht (Bewegung ohne Info)
            dr = ImageDraw.Draw(f); rnd = random.Random(31)
            for _ in range(22):
                x0 = rnd.uniform(80, 1000); y0 = rnd.uniform(TOP + 40, YG - 60); sp = rnd.uniform(12, 30)
                y = TOP + 20 + ((y0 - TOP + sp * (t - T_Q)) % (YG - TOP - 40))
                x = x0 + 8 * math.sin(t * 0.9 + x0)
                dr.ellipse([x - 1.6, y - 1.6, x + 1.6, y + 1.6], fill=o.rgb(C["magnesia"], 120))
        put(f, self.climber.sprite(climber_pose(t)))
        kl.chalk_puff(f, t, T_GRAB, EDGE[0], EDGE[1] - 4, seed=11)
        kl.chalk_puff(f, t, T_PULL + 0.85, HIGH[0], HIGH[1] - 4, seed=15, size=0.8)
        return f

    # -------------------------------------------------------------- Wuerfel (1 cm)
    CUBE = (410, 960, 300, 115, -95)                              # x0, y0 der Vorderseite, Kante, Tiefe dx, dy

    def build_cube(self):
        x0, y0, s, dx, dy = self.CUBE

        def bg(im):
            o.contour_field(im, 560, 1110, n=10, r0=220, step=70, alpha=60)
            d = ImageDraw.Draw(im)
            front = [(x0, y0), (x0 + s, y0), (x0 + s, y0 + s), (x0, y0 + s)]
            top = [(x0, y0), (x0 + dx, y0 + dy), (x0 + s + dx, y0 + dy), (x0 + s, y0)]
            side = [(x0 + s, y0), (x0 + s + dx, y0 + dy), (x0 + s + dx, y0 + s + dy), (x0 + s, y0 + s)]
            for poly, col in ((top, CHALK_L), (side, CHALK_D), (front, CHALK)):
                d.polygon([P(*q) for q in poly], fill=o.rgb(col))
            rnd = random.Random(8)
            for _ in range(520):
                u, v = rnd.random(), rnd.random(); r = rnd.uniform(0.8, 1.8)
                x, y = x0 + u * s, y0 + v * s
                d.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=o.rgb(rnd.choice([CHALK_D, CHALK_L, "#A9A394"])))
            for poly in (front, top, side):
                d.line([P(*q) for q in poly + [poly[0]]], fill=o.rgb(C["magnesia"]), width=int(3 * o.S), joint="curve")
        self.cube_bg = m.background(bg)
        yb = y0 + s + 52

        def bar(im):
            d = ImageDraw.Draw(im); col = o.rgb(C["magnesia"])
            d.line([P(x0, yb), P(x0 + s, yb)], fill=col, width=int(4 * o.S))
            for xx in (x0, x0 + s):
                d.line([P(xx, yb - 14), P(xx, yb + 14)], fill=col, width=int(4 * o.S))
        self.bar1 = m.sprite(bar)
        self.lab1 = m.text_sprite("1 CM · KANSAS", x0 + s / 2, yb + 26, "mono", 32, C["magnesia"], anchor="ma", tracking=0.06)

    def cube(self, t):
        f = self.cube_bg.copy()
        x0, y0, s, dx, dy = self.CUBE
        dr = ImageDraw.Draw(f)
        rnd = random.Random(41)
        for _ in range(26):                                       # Staub schwebt
            px = rnd.uniform(120, 980); py = rnd.uniform(760, 1420); sp = rnd.uniform(6, 16)
            yy = py - sp * (t - J1_0); xx = px + 10 * math.sin(t * 0.7 + px)
            dr.ellipse([xx - 2, yy - 2, xx + 2, yy + 2], fill=o.rgb(C["slate"], 140))
        return f

    # -------------------------------------------------------------- Mikro: Meer und Fels (hohe Leinwand)
    def build_micro(self):
        im = Image.new("RGBA", (W * o.S, CANV_H * o.S), o.rgb(MATRIX))
        d = ImageDraw.Draw(im)
        sea = np.linspace(0, 1, SEAFLOOR * o.S)[:, None]
        c0, c1 = np.array(o.rgb(SEA0)[:3]), np.array(o.rgb(SEA1)[:3])
        grad = (c0 * (1 - sea) + c1 * sea).astype(np.uint8)
        im.paste(Image.fromarray(np.repeat(grad[:, None, :], W * o.S, axis=1).reshape(SEAFLOOR * o.S, W * o.S, 3)), (0, 0))
        X = lambda x: x * o.S; Y = lambda y: y * o.S
        rnd = random.Random(2)
        for _ in range(9000):                                     # feines Korn: zerfallene Plaettchen
            x = rnd.uniform(0, W); y = rnd.uniform(SEAFLOOR, CANV_H); r = rnd.uniform(1.5, 4.5)
            k = rnd.randint(3, 5); a = rnd.uniform(0, 6.28)
            d.polygon([(X(x + r * math.cos(a + 6.28 * j / k)), Y(y + r * math.sin(a + 6.28 * j / k))) for j in range(k)],
                      fill=o.rgb(rnd.choice([GRAIN, "#5A6168", "#3F454B"])))
        for x, y, r, sq, rot, a0, a1 in FRAGS:
            coccolith(d, X, Y, x, y, r, sq, rot, FRAG, "#3A4045", a0=a0, a1=a1, w=1.6)
        for x, y, r, sq, rot in INTACT:
            coccolith(d, X, Y, x, y, r, sq, rot, PLATE, PLATE_B, w=2.2)
        d.line([(0, Y(SEAFLOOR)), (X(W), Y(SEAFLOOR))], fill=o.rgb(C["slate"]), width=2 * o.S)
        self.micro = im.resize((W, CANV_H), Image.LANCZOS)
        glow = Image.new("RGBA", (W * o.S, CANV_H * o.S), (0, 0, 0, 0)); dg = ImageDraw.Draw(glow)
        for x, y, r, sq, rot in INTACT:
            coccolith(dg, X, Y, x, y, r, sq, rot, C["magnesia"], "#8C8778", w=3.4)
        self.glow = glow.resize((W, CANV_H), Image.LANCZOS)
        fg = Image.new("RGBA", (W * o.S, CANV_H * o.S), (0, 0, 0, 0)); dfg = ImageDraw.Draw(fg)
        for x, y, r, sq, rot, a0, a1 in FRAGS:                    # Payoff: die Bruchstuecke leuchten
            coccolith(dfg, X, Y, x, y, r, sq, rot, C["magnesia"], "#7A766A", a0=a0, a1=a1, w=2.2)
        self.fglow = fg.resize((W, CANV_H), Image.LANCZOS)
        dim = Image.new("RGBA", (W, CANV_H), o.rgb(C["obsidian"], 150))
        self.dim = dim
        xb, yb = 120, 1380                                        # Massstab 10 µm (ganze Plaettchen ~6-9 µm)
        sc = 140

        def bar(im_):
            d_ = ImageDraw.Draw(im_); col = o.rgb(C["magnesia"])
            d_.line([P(xb, yb), P(xb + sc, yb)], fill=col, width=int(4 * o.S))
            for xx in (xb, xb + sc):
                d_.line([P(xx, yb - 12), P(xx, yb + 12)], fill=col, width=int(4 * o.S))
        self.bar2 = m.sprite(bar)
        self.lab2 = m.text_sprite("10 µm", xb + sc + 22, yb - 17, "mono", 32, C["magnesia"], tracking=0.06)

    def cam(self, t):
        if t < P_UP0:
            return V_SED
        if t < P_DN0:
            return lerp(V_SED, V_SEA, 0.5 - 0.5 * math.cos(math.pi * seg(t, P_UP0, P_UP1 - P_UP0)))
        return lerp(V_SEA, V_SED, 0.5 - 0.5 * math.cos(math.pi * seg(t, P_DN0, P_DN1 - P_DN0)))

    def sea_life(self, f, t, cy):
        """Meeresschnee, Coccosphaere und ihr Zerfall (in Leinwandkoordinaten, cy = Kamera)."""
        if cy > SEAFLOOR + 40:
            return
        dr = ImageDraw.Draw(f); rnd = random.Random(12)
        for _ in range(60):                                       # Meeresschnee sinkt
            x0 = rnd.uniform(0, W); y0 = rnd.uniform(0, SEAFLOOR); sp = rnd.uniform(14, 34)
            y = (y0 + sp * t) % SEAFLOOR - cy; x = x0 + 6 * math.sin(t + x0)
            if -5 < y < H:
                dr.ellipse([x - 1.8, y - 1.8, x + 1.8, y + 1.8], fill=o.rgb(C["slate"], 110))
        bob = 10 * math.sin(2 * math.pi * t / 3.0)
        cx, ccy = SPH_C[0] + 6 * math.sin(t * 0.8), SPH_C[1] + bob
        v = seg(t, T_BREAK, 0.35)

        def draw(d, X, Y):
            if v < 1:                                             # Zelle (lebende Alge)
                a = int(255 * (1 - v))
                d.ellipse([X(cx - SPH_R * 0.92), Y(ccy - SPH_R * 0.92 - cy), X(cx + SPH_R * 0.92), Y(ccy + SPH_R * 0.92 - cy)],
                          fill=o.rgb("#3E6B50", a))
            for q in SPH:
                bx, by = cx + q["x"] * SPH_R, ccy + q["y"] * SPH_R
                sq = max(0.25, abs(q["z"])) if q["z"] > 0 else 0.25
                rot = math.atan2(q["y"], q["x"]) + math.pi / 2
                if t >= T_BREAK:                                  # Plaettchen loesen sich und sinken
                    w = seg(t, T_BREAK + q["delay"], 1.25)
                    out = seilzug(min(1.0, w * 3))
                    bx += q["x"] * 70 * out + (q["land"] - bx) * w * w * 0.0
                    fall = w * w
                    bx = lerp(bx, q["land"], fall * 0.6)
                    by = lerp(by + q["y"] * 70 * out, SEAFLOOR - 10, fall)
                    sq = lerp(sq, 0.35, w); rot = lerp(rot, 0.0, w)
                    if q["breaks"] and w >= 1:
                        coccolith(d, X, Y, bx - 6, by - cy, q["r"], sq, rot, PLATE, PLATE_B, a0=0.3, a1=2.9, w=2)
                        coccolith(d, X, Y, bx + 10, by - cy + 3, q["r"], sq, rot, PLATE, PLATE_B, a0=3.3, a1=5.9, w=2)
                        continue
                coccolith(d, X, Y, bx, by - cy, q["r"], sq, rot, PLATE, PLATE_B, w=2)
        y_top = min(ccy - SPH_R - 140, 500) - cy
        spr = rk.region(0, max(0, y_top), W, min(H, SEAFLOOR + 60 - cy), draw)
        put(f, spr)

    def micro_frame(self, t, push=1.0):
        cy = self.cam(t)
        f = self.micro.crop((0, int(cy), W, int(cy) + H))
        g = gf = 0.0
        if t >= T_S5:                                             # Wendung: nur ganze Plaettchen leuchten
            g = seilzug(seg(t, T_S5 + 0.1, 0.6)) * (1 - seg(t, T_P + 0.1, 0.5))
            gf = seilzug(seg(t, T_P + 0.1, 0.6))                  # Payoff: jetzt leuchten die Bruchstuecke
        if g > 0 or gf > 0:
            dim = self.dim.crop((0, int(cy), W, int(cy) + H))
            dim.putalpha(dim.getchannel("A").point(lambda a: int(a * max(g, gf))))
            f.alpha_composite(dim)
            for lay, k in ((self.glow, g), (self.fglow, gf)):
                if k > 0:
                    gl = lay.crop((0, int(cy), W, int(cy) + H))
                    gl.putalpha(gl.getchannel("A").point(lambda a, k=k: int(a * k)))
                    f.alpha_composite(gl)
        self.sea_life(f, t, cy)
        z = 1 + 0.04 * seg(t, J2_1, T2_OFF - J2_1) if t < P_UP0 else 1.0
        z *= push
        if z > 1.001:
            f = m.zoomed(f, z, 560, 1000)
        put(f, self.shade, op=lerp(0.35, 1.0, min(1.0, cy / V_SED)))   # im Meer kaum Verlauf (keine Stufe)
        return f

    # -------------------------------------------------------------- Lupenkreis-Sprung
    @staticmethod
    def lens(outer, inner, r, c):
        if r <= 1:
            return outer
        if r >= 2300:
            return inner
        mk = Image.new("L", (W, H), 0); ImageDraw.Draw(mk).ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=255)
        f = Image.composite(inner, outer, mk)
        ImageDraw.Draw(f).ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], outline=o.rgb(C["magnesia"], 230), width=5)
        return f

    # -------------------------------------------------------------- Frames
    def frame(self, t):
        if t < J1_0:                                              # Szene 1: Hook
            f = m.zoomed(self.cliff(t), 1 + 0.03 * seilzug(seg(t, 0, T_HOOK)), 600, 1100)
            put(f, self.rails[0])
            self.hook1.draw(f, t, hook_bis=T_HOOK)
            u = seilzug(seg(t, T_Q, EIN))
            if u > 0:
                put(f, self.label, dx=lerp(-30, 0, u), op=u)
                put(f, self.hook_kick, dx=lerp(-40, 0, u), op=u)
                put(f, self.hook, dx=lerp(-40, 0, u), op=u)
            return f, 61
        if t < J2_0:                                              # Sprung 1 und Zug 1: Wuerfel
            inner = self.cube(t)
            if t < J1_1 + 0.02:
                u = 0.5 - 0.5 * math.cos(math.pi * seg(t, J1_0, J1_1 - J1_0))
                outer = m.zoomed(self.cliff(t), 1.03 * lerp(1.0, JUMP_Z, u), *EDGE)
                if t < J1_0 + 0.12:
                    self.hook1.draw(outer, t, hook_bis=T_HOOK)
                    fade = 1 - seg(t, T_HOOK, 0.12)
                    for s in (self.label, self.hook_kick, self.hook):
                        put(outer, s, op=fade)
                f = self.lens(outer, inner, lerp(0, 2300, u ** 1.6), EDGE)
            else:
                f = m.zoomed(inner, 1 + 0.035 * seg(t, J1_1, J2_0 - J1_1), 560, 1110)
            put(f, self.rails[1] if t >= T_S2 else self.rails[0]); self.rail.pop(f, t, 0, T_S2)
            u = seilzug(seg(t, T_S2, EIN))
            put(f, self.text1, dx=lerp(-40, 0, u), op=u * (1 - seg(t, T1_OFF, 0.25)))
            v = seilzug(seg(t, T_S2 + 0.1, EIN))
            put(f, self.bar1, op=v); put(f, self.lab1, op=v)
            return f, 62
        if t < T_S6:                                              # Sprung 2, Zug 2, Meer, Wendung, Payoff
            push = 1.0
            if t >= T_P:
                push = lerp(1.0, 1.05, 0.5 - 0.5 * math.cos(math.pi * seg(t, T_P, T_S6 - T_P)))
            inner = self.micro_frame(t, push)
            if t < J2_1 + 0.02:
                u = 0.5 - 0.5 * math.cos(math.pi * seg(t, J2_0, J2_1 - J2_0))
                outer = m.zoomed(self.cube(t), 1.035 * lerp(1.0, JUMP_Z, u), 560, 1110)
                put(outer, self.bar1, op=1 - seg(t, J2_0 + 0.45, 0.2)); put(outer, self.lab1, op=1 - seg(t, J2_0 + 0.45, 0.2))
                f = self.lens(outer, inner, lerp(0, 2300, u ** 1.6), (560, 1110))
            else:
                f = inner
            put(f, self.rails[4] if t >= T_P else self.rails[3] if t >= T_S4 else self.rails[2] if t >= T_S3 else self.rails[1])
            self.rail.pop(f, t, 1, T_S3); self.rail.pop(f, t, 2, T_S4)
            v = seilzug(seg(t, J2_1, EIN)) * (1 - seg(t, P_UP0, 0.3))
            put(f, self.bar2, op=v); put(f, self.lab2, op=v)
            u = seilzug(seg(t, T_S3, EIN)); put(f, self.text2, dx=lerp(-40, 0, u), op=u * (1 - seg(t, T2_OFF, 0.25)))
            u = seilzug(seg(t, T_S4, EIN)); put(f, self.text3, dx=lerp(-40, 0, u), op=u * (1 - seg(t, T3_OFF, 0.25)))
            u = seilzug(seg(t, T_S5, EIN)); put(f, self.text4, dx=lerp(-40, 0, u), op=u * (1 - seg(t, T4_OFF, 0.2)))
            u = seg(t, T_P, 0.3)
            if u > 0:
                self.rail.logo_pop(f, t, T_P)
                put(f, self.answer, op=min(1, u * 2) * (1 - seg(t, T_S6 - 0.15, 0.15)), scale=lerp(1.18, 1.0, seilzug(u)),
                    anchor=(X0, 352))
            return f, 63
        if t < T_END:                                             # Folge: Lupenkreis zurueck auf den Griff
            outer_z = lerp(JUMP_Z, 1.0, 0.5 - 0.5 * math.cos(math.pi * seg(t, T_S6, J3_1 - T_S6)))
            outer_z *= 1 + 0.03 * seg(t, J3_1, T_END - J3_1)
            outer = m.zoomed(self.cliff(t), outer_z, *EDGE)
            if t < J3_1:
                u = 0.5 - 0.5 * math.cos(math.pi * seg(t, T_S6, J3_1 - T_S6))
                f = self.lens(outer, self.micro_frame(t, 1.05), lerp(2300, 0, u) ** 1.0 * (1 - u) ** 0.6, EDGE)
            else:
                f = outer
            put(f, self.rails[4])
            u = seilzug(seg(t, T_FAZ, EIN)); put(f, self.fazit, dx=lerp(-40, 0, u), op=u)
            return f, 64
        return self.outro.frame(t, T_END), 65


# ------------------------------------------------------------------ Ton: Musik in F-Dur, 86 BPM
F_, FMAJ7, DM7, GM7, C_, CSUS4, BBMAJ7, AM7, DM9 = (
    [53, 57, 60, 65], [53, 57, 60, 64], [50, 53, 57, 60], [53, 55, 58, 62], [52, 55, 60, 64], [53, 55, 60],
    [53, 57, 58, 62], [52, 55, 57, 60], [50, 53, 57, 60, 64])
PENTA = [77, 79, 81, 84, 86, 89, 91]                           # F-Dur-Pentatonik ab F5


def sound_events(b):
    """Musik in F-Dur (86 BPM) nach Szenen, Hook 1 musikalisch, Spruenge als anschwellende Flaeche mit Zupfton,
    sinkende Plaettchen als fallende Toene der Pentatonik, Akkordschlag zur Aufloesung, Klanglogo im Abspann."""
    h1 = rk.Hook1(t_grab=T_GRAB, t_geo=T_GEO, t_out=T_OUT)
    b.hook1(h1, akkord=DM7, bassnote=38)
    b.musik([
        (T_Q - 0.1, T_Q + 1.9, DM7, 38, "ruhig"),                # Frage: offen
        (T_Q + 1.9, J1_0, BBMAJ7, 46, "ruhig"),
        (J1_0, T_S2, C_, 48, "flaeche"),                         # Sprung 1
        (T_S2, J2_0, F_, 41, "bewegt"),                          # Wuerfel
        (J2_0, T_S3, FMAJ7, 41, "flaeche"),                      # Sprung 2
        (T_S3, P_UP0, AM7, 45, "bewegt"),                        # Plaettchen
        (P_UP0, T_BREAK, BBMAJ7, 46, "ruhig"),                   # Meer, Alge
        (T_BREAK, T_S5, GM7, 43, "fallend"),                     # Zerfall, Absinken
        (T_S5, T_RISE, DM7, 38, "ruhig"),                        # Wendung
        (T_RISE, T_P - 0.15, CSUS4, 48, "steigend"),             # Steigerung, dann 0,15 s Stille
        (T_P, T_S6, DM9, 38, "flaeche"),                         # Aufloesung: verdauen
        (T_S6, T_END, F_, 41, "ruhig"),                          # Fazit: nach F-Dur aufgeloest
        (T_END, DUR, F_, 41, "flaeche"),                         # Abspann
    ], bpm=86.0, gain=-12.0)
    for t0, t1, ak, mm in ((J1_0, J1_1, C_, 84), (J2_0, J2_1, FMAJ7, 86), (P_UP0, P_UP1, BBMAJ7, 81),
                           (P_DN0, P_DN1, GM7, 79)):
        b.ton("schwelle", t0, -14.0, "sprung", akkord=ak, dauer=t1 - t0)
        b.ton("zupf", t1, -13.0, "sprung-landung", m=mm, dauer=1.0)
    b.synth("whoosh", J1_0 + 0.2, -22.0, "lupe", dur=0.55, seed=3)
    b.synth("whoosh", J2_0 + 0.2, -22.0, "lupe", dur=0.55, seed=5)
    b.ton("zupf", T_S2, -14.0, "bohrhaken", m=77, dauer=0.9)
    b.ton("zupf", T_S3, -14.0, "bohrhaken", m=81, dauer=0.9)
    b.ton("zupf", T_S4, -14.0, "bohrhaken", m=84, dauer=0.9)
    b.ton("zupf", T_S2 + 0.1, -17.0, "massstab", m=72, dauer=0.7)
    b.ton("zupf", J2_1, -17.0, "massstab", m=74, dauer=0.7)
    for k, q in enumerate(sorted(SPH, key=lambda q: q["delay"])[:7]):   # Plaettchen sinken: fallende Toene
        b.ton("zupf", T_BREAK + 0.35 + 0.17 * k, -18.0, "plaettchen", m=PENTA[::-1][k % 7], dauer=0.7, pan=0.25 * ((k % 3) - 1))
    b.klang("crunch", T_BREAK + 1.2, -24.0, "bruch")
    for c in range(5):                                           # ganze Plaettchen leuchten: leise Toene aufwaerts
        b.ton("zupf", T_S5 + 0.15 + 0.2 * c, -18.0, "leuchten", m=PENTA[c], dauer=0.8)
    b.ton("schwelle", T_RISE, -8.0, "steigerung", akkord=CSUS4, dauer=T_P - 0.15 - T_RISE)
    b.klang("sub_hit", T_P - 0.01, -10.0, "payoff-einschlag", f0=78.0, f1=36.0)
    b.ton("akzent", T_P, -4.0, "payoff", akkord=DM9, bassnote=38)
    b.ton("schwelle", T_S6, -15.0, "sprung", akkord=F_, dauer=0.7)
    b.klang("chalk_slap", T_PULL + 0.85, -12.0, "griff", seed=2)
    b.ton("zupf", T_FAZ, -14.0, "fazit", m=81, dauer=0.9)
    b.klanglogo(T_END + 0.3, tonika=65, gain=-7.0)               # Abspann: Logo (F-Dur)
    b.ton("zupf", T_END + 1.3, -12.0, "herz", m=84, dauer=1.2)


if __name__ == "__main__":
    if "--reach" in sys.argv:
        print(check_reach())
        sys.exit(0)
    rk.run(Reel, sound_events, META)
