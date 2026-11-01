#!/usr/bin/env python3
"""Reel 009 -- HOLD ID #03: "Sandstone hueco: how did it get hollow?" (Faktenbasis: Post #026, Tafoni), Ablauf "erklaerkette".

Fassung 1 vom 01.11.2026 nach PRODUKTION.md (Stand 16.10.2026), Vorlage r003 Fassung 6 (Hook 1 + Hook 2, Lesezeit,
ruhiges Tempo, Musik statt Klicks, Abspann mit LIKE & FOLLOW), Erklaerkette wie r002/r006.
Hook 1 0-1,45 s: GEOCRIMPS + CLIMBING ab Frame 0, ein Kletterer greift in einen grossen Hueco einer Sandsteinwand voller
Waben (Kreidewolke), "x GEOLOGY" schlaegt ein und die Wand klappt in ihre Sandstein-Signatur auf (Punkte); Hueco und Waben
bleiben ohne Signatur, verraten also nicht, wie sie entstanden.
Hook 2 ab 1,8 s: Formatlabel HOLD ID, Kontextzeile "SANDSTONE HUECO:" (Sandfarbe) ueber "HOW DID IT GET HOLLOW?", 3,9 s.
Uebergang: Riss-Linie durch den Hueco, dann Zoom mit Ueberblendung in den Profilschnitt (Fels links, Luft rechts,
Koerner und Poren sichtbar, der Hueco als Mulde in der Wandflaeche, der Kletterer in Seitenansicht am Wandfuss).
Zug 1: Salziges Wasser zieht durch die Poren bis an die Oberflaeche: "SALTY WATER SOAKS IN."
Zug 2 (die Kette): Es trocknet ab, die Raender (Lippen) zuerst; feucht bleibt es nur am Grund der Mulde, dort steigt
Dunst auf, dort wachsen Salzkristalle in den Poren, Koerner fallen heraus, die Mulde wird tiefer, die Lippen bleiben:
"IT DRIES IN THE HOLE." Der Kletterer steigt ein und haengt an der unteren Lippe.
Payoff: "HOLLOWED BY SALT." gross mit Push-in, die Muldenwand leuchtet. Folge: Stempel HOLD ID #03, die Mulde wird
weiter langsam tiefer, der Kletterer schuettelt aus. Abspann mit LIKE & FOLLOW.
Fakten (v2/faktenbasis/026/sources.md): Waben/Tafoni in poroesem koernigem Gestein (Sandstein); Salzverwitterung: geloeste
Salze in den Poren kristallisieren und erzeugen Spannungen; Bruthans et al. (2018, Geomorphology 303) bzw. Slavik et al.
(EGU 2018): bei geringem Wasserfluss erreicht die Verdunstungsfront die Mulden, die Lippen bleiben trocken; wo es
verdunstet, wirkt die Salzverwitterung; die Haerte (Case hardening) erklaerte die Waben dort nicht. Deshalb keine Kruste
im Bild. Entstehung insgesamt umstritten bzw. polygenetisch: die Caption sagt "largely salt".
Bildmittel (Abwechslungsregel): Uebergang Riss-Linie + Zoom mit Ueberblendung (r008: Isolinien-Welle, Schaufenster) |
Enthuellung Profilschnitt mit Koernern und Poren, Zeitraffer Wasser -> Abtrocknen -> Salz -> Koerner fallen (r008:
Schaufenster, Buersten) | Payoff Antwort gross, Muldenwand leuchtet, Stempel HOLD ID #03, Kletterer haengt an der Lippe
(r008: kein Stempel) | Musik Es-Dur mit C-Moll-Flaechen, 88 BPM (r008: A-Dur 76 BPM).
Aufruf:  python3 r009_holdid_026.py --out ../../../reels --qc <Ordner>   (--stills 0,4.8 | --reach)
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
T_Q = 1.80                          # Hook 2
T_HOOK = T_Q + 3.9                  # Frage steht 3,9 s (7 Woerter), dann Riss-Linie
T_X0 = T_HOOK + 0.30                # Zoom + Ueberblendung in den Profilschnitt (0,8 s)
T_X1 = T_X0 + 0.8
T_S2 = T_X1 + 0.20                  # Zug 1: Wasser zieht ein
T_WET0, T_WET1 = T_S2 + 0.25, T_S2 + 2.2
T1_OFF = T_S2 + 3.2
T_S3 = T1_OFF + 0.45                # Zug 2: trocknet in der Mulde, Salz, Koerner fallen
T_DRY0, T_DRY1 = T_S3 + 0.15, T_S3 + 1.3
T_CRYS = T_S3 + 0.7                 # Kristalle wachsen
T_DIG0 = T_S3 + 1.2                 # Mulde wird tiefer
T_CLIMB = T_S3 + 2.2                # Kletterer steigt ein (1,0 s)
T2_OFF = T_S3 + 3.3
T_PAY = T2_OFF + 0.45               # Payoff "HOLLOWED BY SALT."
T_RISE = T_PAY - 1.0
T_DIG1 = T_PAY + 0.4
T_S5 = T_PAY + 3.0                  # Folge: Stempel
T_STAMP = T_S5 + 0.35
T_SHAKE = T_S5 + 1.0
T_END = T_STAMP + 2.4               # Abspann
DUR = T_END + rk.Outro.DUR

SAND, SAND_LIP, PORE = "#D8C6A3", "#B9A47E", "#16191C"        # Sandfarbe (wie Kruste r003), Lippe, Porenraum
GRAINS = ["#6E6250", "#7D705B", "#5F5545", "#867862"]
WALL = "#2A2622"

# ------------------------------------------------------------------ Szene A: Sandsteinwand mit Waben (frontal, Hook)
YG_A = 1500
HUECO = (660, 1062, 80, 58)
PITS = [(448, 1030, 27, 19), (470, 1352, 24, 16), (606, 1330, 22, 15), (300, 960, 30, 22), (205, 1080, 36, 26),
        (330, 1170, 26, 19), (220, 1290, 30, 21), (800, 960, 34, 24), (880, 1080, 30, 22), (812, 1190, 40, 28),
        (930, 1300, 30, 21), (760, 1390, 26, 18), (340, 1420, 30, 20), (130, 930, 26, 19), (980, 940, 26, 18),
        (560, 920, 30, 20), (420, 1250, 22, 15), (120, 1420, 28, 19), (1010, 1180, 30, 22), (700, 1255, 26, 17)]


def ell(cx, cy, rx, ry, n=40):
    return [(cx + rx * math.cos(2 * math.pi * k / n), cy + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]


BACK = dict(sw=22, hw=13, eb=(-1, 1), kb=(1, -1))
RH_A = (652, HUECO[1] + HUECO[3] - 18)                        # rechte Hand an der unteren Lippe im Hueco
LH_A = (448, 1034)                                             # linke Hand in einer Wabe
FL_A, FR_A = (470, 1356), (606, 1334)
POSE_START = dict(BACK, hip=(530, 1248), lean=-3, lh=LH_A, rh=(584, 1176), lf=(462, 1378), rf=(600, 1356))
POSE_HANG = dict(BACK, hip=(540, 1236), lean=6, lh=LH_A, rh=RH_A, lf=FL_A, rf=FR_A)
POSE_SWING = dict(POSE_HANG, hip=(546, 1226), lean=9)

# ------------------------------------------------------------------ Szene B: Profilschnitt
ROCK_TOP, YG_B = 790, 1540
MYC, HH = 1110, 64                  # Mulde: Mitte und halbe Hoehe an der Wandflaeche (die Lippen bleiben)
D0, D1, D2 = 70.0, 190.0, 214.0     # Tiefe der Mulde: vorher, nach Zug 2, am Ende


def face(y):
    return 700 + 9 * math.sin(y / 85.0)


FX = face(MYC)


def depth(t):
    if t < T_DIG0:
        return D0
    if t < T_DIG1:                  # in Schueben (je Salzzyklus), insgesamt weich
        u = seg(t, T_DIG0, T_DIG1 - T_DIG0)
        steps = 6
        k = u * steps; base = math.floor(k); frac = k - base
        v = (base + seilzug(min(1.0, frac * 1.6))) / steps
        return D0 + (D1 - D0) * v
    return D1 + (D2 - D1) * seg(t, T_DIG1 + 0.3, T_END - T_DIG1 - 0.3)


def pit_x(y, d):
    """x des Muldengrunds in Zeile y (None ausserhalb der Mulde)."""
    q = (y - MYC) / HH
    if abs(q) >= 1:
        return None
    return face(y) - d * (1 - q * q) ** 0.55


def pit_poly(d, n=48):
    ys = [MYC - HH + 2 * HH * k / n for k in range(n + 1)]
    pts = [(pit_x(y, d) if pit_x(y, d) is not None else face(y), y) for y in ys]
    return [(face(MYC - HH) + 40, MYC - HH)] + pts + [(face(MYC + HH) + 40, MYC + HH)]


LIP_LO = (FX - 14, MYC + HH - 2)                              # untere Lippe
SIDE = dict(sw=0, hw=0, eb=(-1, -1), kb=(1, 1))               # Seitenansicht, Blick zur Wand (links)
POSE_B_STAND = dict(SIDE, hip=(860, YG_B - 168), lean=0, lh=(852, YG_B - 138), rh=(868, YG_B - 138),
                    lf=(846, YG_B - 2), rf=(874, YG_B - 2))
POSE_B_LOOK = dict(POSE_B_STAND, lean=-5)
POSE_B_HANG = dict(SIDE, hip=(792, 1312), lean=-12, lh=(LIP_LO[0] - 8, LIP_LO[1] - 1), rh=LIP_LO,
                   lf=(face(1385) + 6, 1385), rf=(face(1440) + 6, 1440))


def check_reach():
    cl = kl.Climber(scale=1.0, width=18.0, torso_w=36.0); out = {}
    for name, p in (("start", POSE_START), ("hang", POSE_HANG), ("swing", POSE_SWING), ("b_stand", POSE_B_STAND),
                    ("b_look", POSE_B_LOOK), ("b_hang", POSE_B_HANG)):
        j = cl.joints(p)
        out[name] = round(max(math.dist(j[k], p[k]) for k in ("lh", "rh", "lf", "rf")), 3)
    return out


def pose_a(t):
    if t < T_GRAB:
        return kl.lerp_pose(POSE_START, POSE_SWING, seilzug(seg(t, 0.0, T_GRAB)))
    u = seg(t, T_GRAB, 0.3)
    p = kl.lerp_pose(POSE_SWING, POSE_HANG, 0.5 - 0.5 * math.cos(math.pi * u))
    if u >= 1:
        w = math.sin(2 * math.pi * (t - T_GRAB - 0.3) / 2.6)
        p = dict(p, hip=(p["hip"][0] + 3 * w, p["hip"][1] + 1.5 * abs(w)), lean=p["lean"] + 1.2 * w)
    return p


def pose_b(t):
    if t < T_CLIMB:
        p = POSE_B_STAND if t < T_S2 + 1.0 else kl.lerp_pose(POSE_B_STAND, POSE_B_LOOK, seilzug(seg(t, T_S2 + 1.0, 0.9)))
        b = math.sin(2 * math.pi * (t - T_X0) / 2.8)
        return dict(p, hip=(p["hip"][0], p["hip"][1] + 1.8 * b), lean=p["lean"] + 0.7 * b)
    u = seg(t, T_CLIMB, 1.0)
    p = kl.lerp_pose(POSE_B_LOOK, POSE_B_HANG, seilzug(u))
    if u >= 1:
        w = math.sin(2 * math.pi * (t - T_CLIMB - 1.0) / 2.6)
        p = dict(p, hip=(p["hip"][0] + 2.5 * w, p["hip"][1] + 1.5 * abs(w)), lean=p["lean"] + 1.0 * w)
        if T_SHAKE <= t < T_SHAKE + 0.9:                         # schuettelt die linke Hand aus (keine neue Info)
            s = math.sin(2 * math.pi * 3.0 * (t - T_SHAKE)) * math.sin(math.pi * seg(t, T_SHAKE, 0.9))
            p = dict(p, lh=(p["lh"][0] + 60 + 12 * s, p["lh"][1] + 90 + 8 * abs(s)))
    return p


# ------------------------------------------------------------------ META
META = dict(
    slug="2026-11-06_holdid-03", dur_range=[17.0, 24.0], payoff_t=T_PAY, abspann_ab=T_END,
    title="GeoCrimps r009 HOLD ID #03 (Erklaerkette), Fassung 1", ablauf="erklaerkette",
    hook1_bis=T_OUT, hook_ab=T_Q, hook_bis=T_HOOK, weitere_fragen=[], cover_t=round(T_Q + 0.85, 2),
    on_screen=["HOLD ID", "SANDSTONE HUECO:", "HOW DID IT GET HOLLOW?", "SALTY WATER SOAKS IN.",
               "IT DRIES IN THE HOLE.", "HOLLOWED BY SALT.", "HOLD ID #03", rk.Outro.CTA],
    labels=[],
    verdauen=["HOLLOWED BY SALT."],
    qc_times=[0.0, T_GRAB, T_GEO, 1.1, 1.6, round(T_Q + 0.85, 2), round(T_HOOK - 0.2, 2), round(T_X0 + 0.4, 2),
              round(T_S2 + 1.4, 2), round(T1_OFF - 0.1, 2), round(T_S3 + 1.6, 2), round(T2_OFF - 0.1, 2),
              round(T_PAY + 0.8, 2), round(T_STAMP + 0.6, 2), round(T_END - 0.1, 2), round(T_END + 2.0, 2)],
    marks=[(0, "Hook 1"), (T_GRAB, "Griff"), (T_GEO, "x GEOLOGY"), (T_Q, "Hook 2"), (T_HOOK, "Riss"),
           (T_X0, "Schnitt"), (T_S2, "Zug 1"), (T_S3, "Zug 2"), (T_DIG0, "tiefer"), (T_CLIMB, "steigt ein"),
           (T_PAY, "PAYOFF"), (T_STAMP, "Stempel"), (T_END, "Abspann")])


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
        self.hook_kick = m.text_sprite("SANDSTONE HUECO:", X0, rk.HOOK_Y, "display", 96, SAND)
        self.hook, _ = m.lines_sprite(["HOW DID IT", "GET HOLLOW?"], rk.HOOK_Y + 112, size=136)
        self.text1, _ = m.lines_sprite(["SALTY WATER", "SOAKS IN."], 352, role="display_xb", size=118)
        self.text2, _ = m.lines_sprite(["IT DRIES IN", "THE HOLE."], 352, role="display_xb", size=118)
        self.answer, _ = m.lines_sprite(["HOLLOWED", "BY SALT."], 352, size=190)
        self.stamp = self.make_stamp(X0 + 250, 440, -6)
        self.stamp.text = "HOLD ID #03"
        self._scene_a()
        self._scene_b()

    # -------------------------------------------------------------- Szene A
    def _scene_a(self):
        wall_poly = o.ragged(-20, 832, 1100, YG_A, seed=9, amp=10, n=26, top_only=True)

        def pit(d, cx, cy, rx, ry):
            d.ellipse([P(cx - rx - 5, cy - ry - 4), P(cx + rx + 5, cy + ry + 5)], fill=o.rgb("#3A342D"))   # Wabenwand
            d.ellipse([P(cx - rx, cy - ry), P(cx + rx, cy + ry)], fill=o.rgb(C["obsidian"]))
            d.ellipse([P(cx - rx * 0.8, cy - ry * 0.55), P(cx + rx * 0.8, cy + ry * 0.95)], fill=o.rgb("#14171A"))
            d.arc([P(cx - rx, cy - ry), P(cx + rx, cy + ry)], 20, 160, fill=o.rgb(SAND_LIP), width=int(3 * o.S))

        def bg(im):
            o.contour_field(im, 820, 560, n=8, r0=120, step=58, alpha=70)
            d = ImageDraw.Draw(im)
            d.polygon([P(x, y) for x, y in wall_poly], fill=o.rgb(WALL))
            rnd = random.Random(5)
            for _ in range(900):
                x = rnd.uniform(0, 1080); y = rnd.uniform(846, YG_A - 6)
                r = rnd.uniform(1.0, 2.4); d.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=o.rgb(rnd.choice(["#3A342D", "#463E35"])))
            for p in PITS:
                pit(d, *p)
            pit(d, *HUECO)
            d.line([P(x, y) for x, y in wall_poly[:27]], fill=o.rgb(SAND_LIP), width=int(3 * o.S))
            lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
            ImageDraw.Draw(lay).rectangle([P(-10, YG_A), P(1090, 1930)], fill=o.rgb(C["graphite"]))
            im.alpha_composite(lay)
            rnd = random.Random(3)
            for _ in range(120):
                x, y = rnd.uniform(10, 1070), rnd.uniform(YG_A + 14, 1900); r = rnd.uniform(1.5, 3.5)
                d.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=o.rgb(C["line"]))
            d.line([P(-10, YG_A), P(1090, YG_A)], fill=o.rgb(C["slate"]), width=int(3 * o.S))
            kl.crash_pad(im, 380, 700, YG_A + 34)
        self.bg_a = m.background(bg)
        holes = [ell(*p) for p in PITS] + [ell(*HUECO)]
        self.geo = kl.GeoReveal(wall_poly, "sandstone", RH_A[0], RH_A[1], pat_alpha=95, holes=holes, seed=8)

    def world_a(self, t):
        f = self.bg_a.copy()
        u = seilzug(seg(t, T_GEO, 0.5))
        if u > 0 and t < T_OUT + 0.4:
            self.geo.put(f, u, fade=1 - seg(t, T_OUT, 0.4))
        put(f, self.climber.sprite(pose_a(t)))
        kl.chalk_puff(f, t, T_GRAB, RH_A[0], RH_A[1] - 6, seed=11)
        return f

    # -------------------------------------------------------------- Szene B: Profilschnitt
    def _scene_b(self):
        ys = list(range(ROCK_TOP, YG_B + 1, 6))
        rnd = random.Random(12)
        topline = [(x, ROCK_TOP + rnd.uniform(-8, 8)) for x in range(-20, int(face(ROCK_TOP)) + 1, 40)]
        rock_poly = topline + [(face(y), y) for y in ys] + [(face(YG_B), YG_B + 400), (-20, YG_B + 400)]
        self.rock_poly = rock_poly
        # Koerner: gerastert mit Zufallsversatz, Poren dazwischen
        g = []
        rnd = random.Random(21)
        for gy in range(ROCK_TOP + 14, YG_B + 40, 19):
            for gx in range(-10, 760, 19):
                x = gx + rnd.uniform(-4, 4) + (9 if (gy // 19) % 2 else 0); y = gy + rnd.uniform(-4, 4)
                if x > face(y) - 7:
                    continue
                g.append((x, y, rnd.uniform(6.8, 9.2), rnd.choice(GRAINS)))
        self.grains = g
        rock_mask = Image.new("L", (W, H), 0)
        ImageDraw.Draw(rock_mask).polygon(rock_poly, fill=255)
        gm = Image.new("L", (W, H), 0); dg = ImageDraw.Draw(gm)
        for x, y, r, _ in g:
            dg.ellipse([x - r, y - r, x + r, y + r], fill=255)
        self.pore = (np.asarray(rock_mask) > 128) & (np.asarray(gm) < 60)
        self.pore = self.pore[:, :780]

        def bg(im):
            o.contour_field(im, 900, 560, n=8, r0=110, step=56, alpha=60)
            d = ImageDraw.Draw(im)
            d.polygon([P(x, y) for x, y in rock_poly], fill=o.rgb(PORE))
            for x, y, r, col in g:
                d.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=o.rgb(col))
            lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
            ImageDraw.Draw(lay).rectangle([P(face(YG_B) - 2, YG_B), P(1090, 1930)], fill=o.rgb(C["graphite"]))
            im.alpha_composite(lay)
            d.line([P(face(YG_B) - 2, YG_B), P(1090, YG_B)], fill=o.rgb(C["slate"]), width=int(3 * o.S))
            d.line([P(x, y) for x, y in topline], fill=o.rgb(SAND_LIP), width=int(3 * o.S))
            d.line([P(face(y), y) for y in ys], fill=o.rgb(SAND_LIP), width=int(3 * o.S))
        self.bg_b = m.background(bg)
        # Kandidaten fuer Salzkristalle: Porenpunkte nahe der Mulde
        rnd = random.Random(31); cand = []
        while len(cand) < 900:
            x = rnd.uniform(FX - D2 - 30, FX); y = rnd.uniform(MYC - HH - 10, MYC + HH + 10)
            if self.pore[int(y), int(x)]:
                cand.append((x, y, rnd.uniform(0, 0.8), rnd.uniform(0, 3.14)))
        self.cand = cand
        # Zeitpunkt, zu dem die Mulde jedes Korn erreicht (fuer fallende Koerner)
        ts = np.arange(T_DIG0, T_END, 1 / 30)
        ds = np.array([depth(t) for t in ts])
        self.fall = []
        for x, y, r, col in g:
            px = pit_x(y, D2)
            if px is None or x < px - 2:
                continue
            for tt, dd in zip(ts, ds):
                p2 = pit_x(y, dd)
                if p2 is not None and x >= p2:
                    self.fall.append((x, y, r, col, float(tt)))
                    break
        rnd = random.Random(41)
        self.wisps = [(rnd.uniform(0, 1), rnd.uniform(-0.6, 0.6)) for _ in range(6)]

    def pit_sprite(self, d, glow=0.0):
        def draw(dr, X, Y):
            poly = pit_poly(d)
            dr.polygon([(X(x), Y(y)) for x, y in poly], fill=o.rgb(C["obsidian"]))
            wall = poly[1:-1]
            col = C["magnesia"] if glow > 0 else "#4E4639"
            dr.line([(X(x), Y(y)) for x, y in wall], fill=o.rgb(col, int(150 + 105 * glow) if glow > 0 else 255),
                    width=int((2.5 + 2.5 * glow) * o.S), joint="curve")
            for yy in (MYC - HH, MYC + HH):                    # Lippen
                dr.ellipse([X(face(yy) - 6), Y(yy - 6), X(face(yy) + 6), Y(yy + 6)], fill=o.rgb(SAND_LIP))
        return rk.region(FX - D2 - 30, MYC - HH - 12, FX + 46, MYC + HH + 12, draw)

    def wet_layer(self, t, d):
        """Wasser in den Poren: Front zieht von links ein; beim Abtrocknen bleiben nur Zeilen am Muldengrund feucht."""
        if t < T_WET0 or t >= T_S5 + 0.5:
            return None
        front = lerp(-20, 760, seilzug(seg(t, T_WET0, T_WET1 - T_WET0)))
        dry = seilzug(seg(t, T_DRY0, T_DRY1 - T_DRY0))
        y0, y1 = ROCK_TOP - 12, YG_B + 1
        rows = np.arange(y0, y1)
        xb = np.array([face(y) if pit_x(y, d) is None else pit_x(y, d) for y in rows])
        q = np.clip(1 - ((rows - MYC) / (HH + 24.0)) ** 2, 0, 1) ** 0.6       # 1 am Muldengrund, 0 an den Lippen
        dryw = dry * (90 * (1 - q) + 4 * q + 400 * (1 - q) * seg(t, T_DRY1, 1.2))
        lim = np.minimum(front, xb - dryw)
        xs = np.arange(0, 780)
        wet = self.pore[y0:y1] & (xs[None, :] < lim[:, None])
        a = (wet * 175 * (1 - seg(t, T_S5, 0.5))).astype(np.uint8)
        img = Image.new("RGBA", (780, y1 - y0), o.rgb(C["water"]))
        img.putalpha(Image.fromarray(a))
        return img, y0

    def world_b(self, t):
        f = self.bg_b.copy()
        d = depth(t)
        wl = self.wet_layer(t, d)
        if wl:
            m.composite(f, wl[0], 0, wl[1])
        glow = math.sin(math.pi * seg(t, T_PAY, 1.6)) if T_PAY <= t < T_PAY + 1.6 else 0.0
        put(f, self.pit_sprite(d, glow))
        dr = ImageDraw.Draw(f)
        if t >= T_CRYS:                                          # Salzkristalle in den Poren am Muldengrund
            for x, y, ph, ang in self.cand:
                px = pit_x(y, d)
                if px is None or not (px - 26 < x < px - 1):
                    continue
                v = seg(t, T_CRYS + ph, 0.6)
                s = 4.2 * v
                if s < 0.6:
                    continue
                c, sn = math.cos(ang) * s, math.sin(ang) * s
                dr.polygon([(x + c, y + sn), (x - sn, y + c), (x - c, y - sn), (x + sn, y - c)], fill=o.rgb(C["ice"], 240))
        for x, y, r, col, tt in self.fall:                       # Koerner fallen aus der Mulde
            v = seg(t, tt, 0.8)
            if 0 < v < 1:
                qx = x + 90 * seilzug(v); qy = y + 420 * v * v
                dr.ellipse([qx - r, qy - r, qx + r, qy + r], fill=o.rgb(col, int(255 * (1 - v * 0.7))))
        if T_DRY0 <= t < T_END:                                  # Dunst steigt aus dem Muldengrund
            per = 1.8
            for k, (ph, dy) in enumerate(self.wisps):
                v = ((t - T_DRY0) / per + ph) % 1.0
                bx = pit_x(MYC + dy * HH * 0.5, d) or FX
                x = lerp(bx + 8, FX + 60, v); y = MYC + dy * HH * 0.5 - 70 * v * v
                a = int(140 * math.sin(math.pi * v) * seg(t, T_DRY0, 0.6))
                pts = [(x + 5 * math.sin(yy / 8 + k), yy) for yy in range(int(y), int(y) - 30, -3)]
                dr.line(pts, fill=o.rgb(C["slate"], a), width=3)
        put(f, self.climber.sprite(pose_b(t)))
        kl.chalk_puff(f, t, T_CLIMB + 0.95, LIP_LO[0], LIP_LO[1] - 6, seed=15, size=0.8)
        kl.chalk_puff(f, t, T_SHAKE + 0.15, POSE_B_HANG["lh"][0] + 60, POSE_B_HANG["lh"][1] + 90, seed=14, size=0.45)
        return f

    def make_stamp(self, cx, cy, angle):
        s = o.S; f1 = o.font("stencil", 76); t1 = "HOLD ID #03"
        w1 = f1.getlength(t1); bw = int(w1 + 2 * 30 * s); bh = int((76 + 2 * 22) * s)
        im = Image.new("RGBA", (bw + 40 * s, bh + 40 * s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        ox, oy = 20 * s, 20 * s; col = o.rgb(C["magnesia"])
        d.rounded_rectangle([ox, oy, ox + bw, oy + bh], radius=14 * s, outline=col, width=6 * s)
        d.text((ox + bw / 2, oy + bh / 2 + 4 * s), t1, font=f1, fill=col, anchor="mm")
        rng = np.random.default_rng(9)
        a = np.asarray(im.getchannel("A"), np.float32)
        noise = np.asarray(Image.fromarray((rng.random(a.shape) * 255).astype(np.uint8)).resize(im.size), np.float32) / 255
        a *= np.clip(1.4 - noise * 1.05, 0.3, 1.0)
        im.putalpha(Image.fromarray(a.astype(np.uint8)))
        im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
        small = im.resize((im.width // s, im.height // s), Image.LANCZOS)
        return m.Sprite(small, int(cx - small.width / 2), int(cy - small.height / 2))

    # -------------------------------------------------------------- Frames
    def frame(self, t):
        if t < T_X0:                                             # Szene 1: Hook (frontal)
            f = m.zoomed(self.world_a(t), 1 + 0.03 * seilzug(seg(t, 0, T_HOOK)), HUECO[0], HUECO[1])
            put(f, self.rails[0])
            self.hook1.draw(f, t, hook_bis=T_HOOK)
            u = seilzug(seg(t, T_Q, EIN))
            if u > 0:
                fade = 1 - seg(t, T_HOOK, 0.12)
                put(f, self.label, dx=lerp(-30, 0, u), op=u * fade)
                put(f, self.hook_kick, dx=lerp(-40, 0, u), op=u * fade)
                put(f, self.hook, dx=lerp(-40, 0, u), op=u * fade)
            if t >= T_HOOK:
                put(f, rk.crackline(seilzug(seg(t, T_HOOK, 0.35)), x=HUECO[0], y0=840, seed=26))
            return f, 91
        if t < T_X1:                                             # Uebergang: Zoom in den Hueco, Profilschnitt blendet ein
            u = seilzug(seg(t, T_X0, T_X1 - T_X0))
            fa = m.zoomed(self.world_a(t), lerp(1.03, 1.7, u), HUECO[0], HUECO[1])
            put(fa, rk.crackline(1.0, alpha=int(255 * (1 - u)), x=HUECO[0], y0=840, seed=26))
            fb = m.zoomed(self.world_b(t), lerp(1.35, 1.0, u), FX, MYC)
            f = Image.blend(fa, fb, u)
            put(f, self.rails[0])
            return f, 92
        if t >= T_END:
            return self.outro.frame(t, T_END), 95
        z = 1 + 0.03 * (0.5 - 0.5 * math.cos(math.pi * seg(t, T_S3, T_PAY - T_S3)))
        if t >= T_PAY:
            z *= lerp(1.0, 1.05, 0.5 - 0.5 * math.cos(math.pi * seg(t, T_PAY, T_S5 - T_PAY)))
        if t >= T_S5:
            z = lerp(1.03 * 1.05, 1.0, seilzug(seg(t, T_S5, 0.9))) * (1 + 0.02 * seg(t, T_S5 + 0.9, T_END - T_S5))
        f = m.zoomed(self.world_b(t), z, FX, MYC)
        if t < T_S3:                                             # Zug 1
            put(f, self.rails[1]); self.rail.pop(f, t, 0, T_S2)
            u = seilzug(seg(t, T_S2 + 0.05, EIN)); put(f, self.text1, dx=lerp(-40, 0, u), op=u * (1 - seg(t, T1_OFF, 0.25)))
            return f, 93
        put(f, self.rails[3] if t >= T_PAY else self.rails[2])
        self.rail.pop(f, t, 1, T_S3)
        if t < T_PAY:                                            # Zug 2
            u = seilzug(seg(t, T_S3 + 0.05, EIN)); put(f, self.text2, dx=lerp(-40, 0, u), op=u * (1 - seg(t, T2_OFF, 0.25)))
            return f, 94
        if t < T_S5:                                             # Payoff
            u = seg(t, T_PAY, 0.3)
            self.rail.logo_pop(f, t, T_PAY)
            put(f, self.answer, op=min(1, u * 2) * (1 - seg(t, T_S5 - 0.2, 0.2)), scale=lerp(1.18, 1.0, seilzug(u)), anchor=(X0, 352))
            return f, 96
        u = seg(t, T_STAMP, 0.3)                                 # Folge: Stempel
        if u > 0:
            put(f, self.stamp, op=min(1, u * 3), scale=lerp(1.65, 1.0, griff(u)) if u < 1 else 1.0)
        rk.dust(f, t, T_STAMP + 0.18, (self.stamp.x + 30, self.stamp.y + 30, self.stamp.x + self.stamp.w - 30,
                                       self.stamp.y + self.stamp.h - 30), seed=78)
        return f, 97


# ------------------------------------------------------------------ Ton: Musik in Es-Dur, 88 BPM
EB, CM7, ABMAJ7, GM7, FM7, BBSUS4, CM9 = ([51, 55, 58, 63], [55, 58, 60, 63], [51, 55, 56, 60], [50, 53, 55, 58],
                                          [51, 53, 56, 60], [51, 53, 58], [50, 55, 58, 60, 63])
PENTA = [75, 77, 79, 82, 84, 87, 89]   # Es-Dur-Pentatonik ab Es5


def sound_events(b):
    """Musik in Es-Dur mit C-Moll-Flaechen (88 BPM) nach Szenen; Hook 1 musikalisch; Wasser als steigende, Salzkristalle
    als hohe leise, fallende Koerner als tiefe Toene der Pentatonik; Akkordschlag zur Aufloesung; Klanglogo im Abspann."""
    h1 = rk.Hook1(t_grab=T_GRAB, t_geo=T_GEO, t_out=T_OUT)
    b.hook1(h1, akkord=CM7, bassnote=48)
    b.musik([
        (T_Q - 0.1, T_Q + 2.0, CM7, 48, "ruhig"),               # Frage: offen
        (T_Q + 2.0, T_HOOK, ABMAJ7, 44, "ruhig"),
        (T_HOOK, T_S2, FM7, 41, "flaeche"),                     # Riss, Schnitt
        (T_S2, T_S2 + 1.6, EB, 51, "bewegt"),                   # Wasser zieht ein
        (T_S2 + 1.6, T_S3, ABMAJ7, 44, "bewegt"),
        (T_S3, T_DIG0, GM7, 43, "ruhig"),                       # trocknet
        (T_DIG0, T_RISE, CM7, 48, "steigend"),                  # Salz, Mulde wird tiefer
        (T_RISE, T_PAY - 0.15, BBSUS4, 46, "flaeche"),          # Steigerung, dann 0,15 s Stille
        (T_PAY, T_S5, CM9, 48, "flaeche"),                      # Aufloesung: verdauen
        (T_S5, T_END, EB, 51, "ruhig"),                         # Stempel: nach Es-Dur aufgeloest
        (T_END, DUR, EB, 51, "flaeche"),                        # Abspann
    ], bpm=88.0, gain=-12.0)
    b.klang("crunch", T_HOOK + 0.05, -18.0, "riss", seed=6)
    b.ton("schwelle", T_X0 - 0.2, -14.0, "schnitt", akkord=FM7, dauer=0.7)
    b.ton("zupf", T_S2, -14.0, "bohrhaken", m=82, dauer=0.9)
    for k in range(5):                                          # Wasser zieht ein: Toene aufwaerts
        b.ton("zupf", T_WET0 + 0.38 * k, -17.0, "wasser", m=PENTA[k], dauer=0.7, pan=0.15 * (k - 2))
    b.ton("zupf", T_S3, -14.0, "bohrhaken", m=84, dauer=0.9)
    for k in range(6):                                          # Kristalle: hohe, leise Toene
        b.ton("zupf", T_CRYS + 0.15 * k, -21.0, "kristalle", m=PENTA[(k * 2) % 7] + 12 if k % 2 else PENTA[6], dauer=0.5, pan=0.3)
    for k in range(6):                                          # je Schub fallen Koerner: tiefe Toene abwaerts
        tt = T_DIG0 + (T_DIG1 - T_DIG0) * (k + 0.2) / 6
        b.ton("zupf", tt, -16.0, "koerner", m=PENTA[5 - k] - 12, dauer=0.8, pan=0.2)
    b.klang("crunch", T_DIG0 + 0.1, -22.0, "broeseln", seed=7)
    b.klang("chalk_slap", T_CLIMB + 0.95, -12.0, "griff", seed=2)
    b.ton("schwelle", T_RISE, -8.0, "steigerung", akkord=BBSUS4, dauer=T_PAY - 0.15 - T_RISE)
    b.klang("sub_hit", T_PAY - 0.01, -10.0, "payoff-einschlag", f0=78.0, f1=36.0)
    b.ton("akzent", T_PAY, -4.0, "payoff", akkord=CM9, bassnote=48)
    b.klang("thud", T_STAMP + 0.16, -9.0, "stempel", seed=8)
    b.ton("zupf", T_STAMP + 0.16, -11.0, "stempel", m=75, dauer=1.0)
    b.synth("whoosh", T_SHAKE, -22.0, "hand-ausschuetteln", dur=0.5, seed=12)
    b.klanglogo(T_END + 0.3, tonika=63, gain=-7.0)               # Abspann: Logo (Es-Dur)
    b.ton("zupf", T_END + 1.3, -12.0, "herz", m=82, dauer=1.2)


if __name__ == "__main__":
    if "--reach" in sys.argv:
        print(check_reach())
        sys.exit(0)
    rk.run(Reel, sound_events, META)
