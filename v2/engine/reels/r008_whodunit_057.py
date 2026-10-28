#!/usr/bin/env python3
"""Reel 008 -- WHODUNIT #02: "Which way was up?" (Faktenbasis: Post #057, gradierte Schichtung), Ablauf "offene_frage".

Fassung 1 vom 28.10.2026 nach PRODUKTION.md (Stand 16.10.2026), Vorlage r003 Fassung 6 (Musik, Tempo, Abspann, Lesezeit).
Themen-Tausch: Der Slot 03.11.2026 war fuer #061 (Schuhgummi) vorgesehen, Vorbedingung "Befund (orange) vom 29.08.
beheben"; der Befund ist im Repo nicht dokumentiert, also nicht pruefbar -> Tausch mit #057 (naechstes Thema derselben
Formatklasse, Slot 10.11.2026), Ablauf je Slot bleibt.
Hook 1 0-1,45 s: GEOCRIMPS + CLIMBING ab Frame 0, ein Kletterer greift eine Leiste in einer gebankten Sandsteinwand
(Kreidewolke), "x GEOLOGY" schlaegt ein und die Wand klappt in ihre Sandstein-Signatur (gleichmaessige Punkte) und ihre
Baenke auf; die Koernung (die Antwort) bleibt verborgen.
Hook 2 ab 1,8 s: Formatlabel WHODUNIT, Kontextzeile "SANDSTONE CRAG:" (Sandfarbe) ueber "WHICH WAY WAS UP?", 3,75 s.
Isolinien-Welle von der Leiste.
Zug 1 (harmlos): ein Schaufenster rechts, darin setzt sich eine Bank ab, grob unten, fein oben (Labels COARSE, FINE):
"COARSE BELOW, FINE ON TOP."
Zug 2 (Wendung): Zoom auf die Bank an der Hand; der Kletterer buerstet die Wand (Buerste, Staub) und legt die Koernung frei:
grob oben, fein unten: "BUT HERE: COARSE ON TOP..." Danach zeigen sich alle Baenke nacheinander, die grobe Oberkante
leuchtet jeweils auf: "EVERY BED AGREES." (mehrere Indikatoren, die uebereinstimmen, wie die Quelle verlangt)
Callback als naheliegende falsche Antwort: "UP THE WALL?" (der Kletterer lehnt sich zurueck und schaut hoch).
Payoff: "UP WAS DOWN." gross mit Push-in, die Koernung aller Baenke dreht sich um die waagrechte Achse in die
Ablagerungslage (grob unten). Folge: Zoom zurueck, die Koernung dreht zurueck, der Kletterer zieht eine Bank hoeher:
"HERE, UP MEANS OLDER." Abspann mit LIKE & FOLLOW.
Fakten (v2/faktenbasis/057/sources.md): normale Gradierung grob unten, fein oben, "in most cases" (OpenGeology);
juengere Schichten in Richtung fein ("younging direction"); Ueberschiebungs-/Faltungsdruck kann Baenke auf den Kopf
stellen (Nachtrag 28.10.2026, LibreTexts-Ausgabe von Bentley et al.); ein Indikator reicht nicht, viele sollen
uebereinstimmen. Die Wand ist schematisch, kein Ort, keine Zahl, keine Reibungsaussage.
Bildmittel (Abwechslungsregel): Uebergang Isolinien-Welle, Schaufenster, Zoom (r007: Scanlinie) | Enthuellung Buersten
der Wand, Baenke zeigen sich nacheinander (r007: Scan und Gitter) | Payoff Antwort gross, Koernung dreht sich um, kein
Chip, kein Stempel (r007: Chip IT DEPENDS) | Musik A-Dur mit Fis-Moll-Flaechen, 76 BPM (r007: B-Dur, 82 BPM).
Aufruf:  python3 r008_whodunit_057.py --out ../../../reels --qc <Ordner>   (--stills 0,4.8 fuer Einzelbilder, --reach)
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
T_Q = 1.80
T_HOOK = T_Q + 3.75                # Hook-2-Frage steht 3,75 s, dann Isolinien-Welle
T_S2 = T_HOOK + 0.45               # Zug 1: Schaufenster, Bank setzt sich ab
T_FALL0, T_FALL1 = T_S2 + 0.35, T_S2 + 1.75
T_LAB_C, T_LAB_F = T_S2 + 1.0, T_S2 + 1.9
T1_OFF = T_S2 + 3.9
T_Z0 = T1_OFF + 0.1                # Zoom auf die Bank an der Hand (0,8 s)
T_Z1 = T_Z0 + 0.8
ZOOM, ZC = 1.45, (540, 1170)
T_S3 = T_Z0 + 0.45                 # Zug 2: Buersten
T_BR0, T_BR1 = T_S3 + 0.5, T_S3 + 2.3          # drei Buerstenstriche
T_TXT2 = T_S3 + 1.1
T_LAB2 = T_S3 + 1.4
T2_OFF = T_S3 + 4.1
T_EVERY = T2_OFF + 0.45            # alle Baenke zeigen sich
T3_OFF = T_EVERY + 2.6
T_CALL = T3_OFF + 0.45             # Callback "UP THE WALL?"
T_S4 = T_CALL + 2.4                # Payoff "UP WAS DOWN."
T_RISE = T_S4 - 1.1
T_FLIP = T_S4 + 0.6                # Koernung dreht sich (1,0 s)
T_S5 = T_S4 + 3.5                  # Folge: Zoom zurueck, Koernung dreht zurueck
T_BACK = T_S5 + 0.9
T_FAZ = T_S5 + 1.9                 # Fazit "HERE, UP MEANS OLDER."
T_CLIMB = T_FAZ + 0.6
T_END = T_FAZ + 3.6
DUR = T_END + rk.Outro.DUR
PUSH = 1.05

# ------------------------------------------------------------------ Szene: gebankte Sandsteinwand
WX0, WX1, WTOP, YG = 140, 1060, 822, 1480
BB = [840 + k * (YG - 840) / 6 for k in range(7)]          # Bankgrenzen (6 gleich dicke Baenke)
YC = (BB[0] + BB[6]) / 2                                     # Drehachse der Koernung
SAND, SAND_D, WALL = "#CDB894", "#9C8A68", "#222A30"
BRUSH_X0, BRUSH_X1, BRUSH_Y = 486, 598, 1213                 # gebuersteter Streifen in Bank 3
ORDER = [3, 2, 4, 1, 5, 0]                                   # Reihenfolge "EVERY BED AGREES"
PANEL = (590, 630, 960, 1030)                                # Schaufenster Zug 1
PB0, PB1 = 795, 1005                                         # Bank im Schaufenster (oben, unten)

# Kletterer (Rueckenansicht), vor dem Rendern geprueft (check_reach)
BACK = dict(sw=22, hw=13, eb=(-1, 1), kb=(1, -1))
EDGE = BB[2]
LH, RH = (372, EDGE + 2), (505, EDGE)
LF, RF = (382, BB[5]), (478, BB[5])
DY = BB[1] - BB[2]                                           # eine Bank hoeher (negativ)
POSE_START = dict(BACK, hip=(410, 1300), lean=-3, lh=(384, 1112), rh=(468, 1150), lf=(390, 1404), rf=(470, 1398))
POSE_HANG = dict(BACK, hip=(420, 1262), lean=3, lh=LH, rh=RH, lf=LF, rf=RF)
POSE_SWING = dict(POSE_HANG, hip=(426, 1254), lean=6)
POSE_LOOK = dict(POSE_HANG, hip=(422, 1252), lean=-4)
POSE_UP = kl.move_pose(POSE_HANG, dy=DY)


def pose_brush(x):
    return dict(POSE_HANG, hip=(450, 1262), lean=6, rh=(x, BRUSH_Y))


def check_reach():
    cl = kl.Climber(scale=1.0, width=18.0, torso_w=36.0); out = {}
    for name, p in (("start", POSE_START), ("hang", POSE_HANG), ("swing", POSE_SWING), ("look", POSE_LOOK),
                    ("up", POSE_UP), ("brush_l", pose_brush(BRUSH_X0 + 4)), ("brush_r", pose_brush(BRUSH_X1 - 6))):
        j = cl.joints(p)
        out[name] = round(max(math.dist(j[k], p[k]) for k in ("lh", "rh", "lf", "rf")), 3)
    return out


def brush_x(t):
    """Buerste: drei Striche hin und her; liefert x der Hand und den aufgedeckten rechten Rand."""
    if t < T_BR0:
        return BRUSH_X0 + 4, BRUSH_X0
    u = seg(t, T_BR0, T_BR1 - T_BR0)
    reach = BRUSH_X0 + (BRUSH_X1 - BRUSH_X0) * seilzug(min(1.0, u * 1.25))
    ph = 0.5 - 0.5 * math.cos(2 * math.pi * 1.5 * u)                   # 1,5 Perioden = 3 Striche
    return lerp(BRUSH_X0 + 4, max(BRUSH_X0 + 10, reach - 6), ph), reach


def climber_pose(t):
    if t < T_GRAB:
        return kl.lerp_pose(POSE_START, POSE_SWING, seilzug(seg(t, 0.0, T_GRAB)))
    breathe = math.sin(2 * math.pi * (t - T_GRAB) / 2.7)
    if t < T_S3 + 0.2:
        u = seg(t, T_GRAB, 0.3)
        p = kl.lerp_pose(POSE_SWING, POSE_HANG, 0.5 - 0.5 * math.cos(math.pi * u))
        if u >= 1:
            p = dict(p, hip=(p["hip"][0] + 3 * breathe, p["hip"][1] + 1.5 * abs(breathe)), lean=p["lean"] + 1.2 * breathe)
        return p
    if t < T_BR1 + 0.7:                                                 # Buerste holen, buersten, zuruecklegen
        bx, _ = brush_x(t)
        if t < T_BR0:
            return kl.lerp_pose(POSE_HANG, pose_brush(bx), seilzug(seg(t, T_S3 + 0.2, T_BR0 - T_S3 - 0.2)))
        if t < T_BR1:
            return pose_brush(bx)
        return kl.lerp_pose(pose_brush(bx), POSE_HANG, seilzug(seg(t, T_BR1, 0.6)))
    if t < T_CALL:
        p = POSE_HANG
    elif t < T_S5:                                                      # Callback: lehnt sich zurueck, schaut hoch
        p = kl.lerp_pose(POSE_HANG, POSE_LOOK, seilzug(seg(t, T_CALL, 0.7)))
        if t >= T_S4:
            p = kl.lerp_pose(POSE_LOOK, POSE_HANG, seilzug(seg(t, T_S4 + 0.2, 0.7)))
    else:                                                               # Folge: zieht eine Bank hoeher
        p = kl.lerp_pose(POSE_HANG, POSE_UP, seilzug(seg(t, T_CLIMB, 1.0)))
    return dict(p, hip=(p["hip"][0] + 3 * breathe, p["hip"][1] + 1.5 * abs(breathe)), lean=p["lean"] + 1.0 * breathe)


# ------------------------------------------------------------------ META
META = dict(
    slug="2026-11-03_whodunit-02", dur_range=[24.0, 33.0], payoff_t=T_S4, abspann_ab=T_END,
    title="GeoCrimps r008 WHODUNIT #02 (Offene Frage), Fassung 1", ablauf="offene_frage",
    hook1_bis=T_OUT, hook_ab=T_Q, hook_bis=T_HOOK, weitere_fragen=[[T_CALL, T_S4]], cover_t=round(T_Q + 0.85, 2),
    on_screen=["WHODUNIT", "SANDSTONE CRAG:", "WHICH WAY WAS UP?", "COARSE BELOW, FINE ON TOP.",
               "BUT HERE: COARSE ON TOP…", "EVERY BED AGREES.", "UP THE WALL?", "UP WAS DOWN.",
               "HERE, UP MEANS OLDER.", rk.Outro.CTA],
    labels=["COARSE", "FINE"],
    verdauen=["UP WAS DOWN.", "HERE, UP MEANS OLDER."],
    qc_times=[0.0, T_GRAB, T_GEO, 1.1, 1.6, round(T_Q + 0.85, 2), round(T_HOOK - 0.2, 2), round(T_S2 + 2.6, 2),
              round(T_S3 + 1.0, 2), round(T2_OFF - 0.2, 2), round(T_EVERY + 2.2, 2), round(T_S4 - 0.3, 2),
              round(T_FLIP + 1.2, 2), round(T_BACK + 0.4, 2), round(T_END - 0.2, 2), round(T_END + 2.0, 2)],
    marks=[(0, "Hook 1"), (T_GRAB, "Griff"), (T_GEO, "x GEOLOGY"), (T_Q, "Hook 2"), (T_HOOK, "Welle"),
           (T_S2, "Zug 1"), (T_Z0, "Zoom"), (T_S3, "Zug 2"), (T_BR0, "Buersten"), (T_EVERY, "alle Baenke"),
           (T_CALL, "Callback"), (T_S4, "PAYOFF"), (T_FLIP, "Drehung"), (T_S5, "Zoom zurueck"), (T_FAZ, "Fazit"),
           (T_END, "Abspann")])


# ------------------------------------------------------------------ Koernung
def grains(bed, x0=WX0 + 14, x1=WX1 - 14, overturned=True, seed=0, dens=0.42):
    """Koerner einer Bank: (x, y, r). overturned: grob oben, fein unten (heutige Lage); sonst grob unten."""
    rnd = random.Random(100 + bed * 7 + seed)
    yt, yb = BB[bed] + 5, BB[bed + 1] - 5
    out = []
    for _ in range(int((x1 - x0) * dens)):
        y = rnd.uniform(yt, yb)
        frac = (yb - y) / (yb - yt) if overturned else (y - yt) / (yb - yt)      # 1 = grobe Seite
        r = (1.6 + 7.4 * frac ** 1.4) * rnd.uniform(0.75, 1.05)
        if rnd.random() > 0.35 + 0.65 * (1 - frac) and frac < 0.6:
            continue
        out.append((rnd.uniform(x0, x1), y, r))
    return out


def draw_grains(im, gs, alpha=220):
    d = ImageDraw.Draw(im)
    for x, y, r in sorted(gs, key=lambda g: g[2]):
        col = SAND if r > 3.2 else SAND_D
        d.ellipse([P(x - r, y - r * 0.82), P(x + r, y + r * 0.82)], fill=o.rgb(col, alpha))
        if r > 5.5:
            d.arc([P(x - r * 0.7, y - r * 0.6), P(x + r * 0.2, y + r * 0.1)], 190, 300, fill=o.rgb(C["magnesia"], 120),
                  width=int(1.6 * o.S))


def crop_x(spr, xa, xb):
    """Sprite auf den Bildbereich xa..xb beschneiden."""
    if spr is None:
        return None
    a, b = int(max(0, xa - spr.x)), int(min(spr.w, xb - spr.x))
    if b <= a:
        return None
    return m.Sprite(spr.img.crop((a, 0, b, spr.h)), spr.x + a, spr.y)


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

        wall_poly = o.ragged(WX0, WTOP, WX1, YG, seed=9, amp=7, n=28, top_only=True)
        self.wall_poly = wall_poly

        def bg(im):
            o.contour_field(im, 860, 560, n=8, r0=110, step=56, alpha=70)
            d = ImageDraw.Draw(im)
            d.polygon([P(x, y) for x, y in wall_poly], fill=o.rgb(WALL))
            mask = Image.new("L", im.size, 0); ImageDraw.Draw(mask).polygon([P(x, y) for x, y in wall_poly], fill=255)
            yy, xx = np.mgrid[0:im.size[1], 0:im.size[0]].astype(np.float32) / o.S
            shade = np.clip((xx - WX0) / (WX1 - WX0), 0, 1) * 0.28 + np.clip((yy - WTOP) / (YG - WTOP), 0, 1) * 0.22
            sh = Image.new("RGBA", im.size, o.rgb(C["obsidian"]))
            sh.putalpha(Image.fromarray((np.asarray(mask, np.float32) * shade).astype(np.uint8))); im.alpha_composite(sh)
            rnd = random.Random(5)
            for _ in range(600):                                        # neutrale Koernung (verraet nichts)
                x = rnd.uniform(WX0 + 8, WX1 - 8); y = rnd.uniform(WTOP + 14, YG - 6)
                r = rnd.uniform(1.0, 2.2); d.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=o.rgb(rnd.choice([C["line"], "#333C44"])))
            for k in range(1, 6):                                       # Bankfugen, leicht gewellt, mit Leisten
                y0 = BB[k]
                pts = [(x, y0 + 2.5 * math.sin(x / 90 + k)) for x in range(WX0, WX1 + 1, 12)]
                d.line([P(*q) for q in pts], fill=o.rgb("#0B0E10"), width=int(5 * o.S))
                d.line([P(x, y - 4) for x, y in pts], fill=o.rgb(C["slate"], 150), width=int(2 * o.S))
            d.line([P(x, y) for x, y in wall_poly[:29]], fill=o.rgb(C["slate"]), width=int(3 * o.S))
            d.line([P(WX0, WTOP), P(WX0, YG)], fill=o.rgb(C["slate"], 160), width=int(3 * o.S))
            lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
            ImageDraw.Draw(lay).rectangle([P(-10, YG), P(1090, 1930)], fill=o.rgb(C["graphite"], 255))
            im.alpha_composite(lay)
            rnd = random.Random(3)
            for _ in range(120):
                x, y = rnd.uniform(10, 1070), rnd.uniform(YG + 14, 1900); r = rnd.uniform(1.5, 3.5)
                d.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=o.rgb(C["line"]))
            d.line([P(-10, YG), P(1090, YG)], fill=o.rgb(C["slate"]), width=int(3 * o.S))
            kl.crash_pad(im, 300, 600, YG + 30)
        self.bg = m.background(bg)

        # Hook 2
        self.hook_kick = m.text_sprite("SANDSTONE CRAG:", X0, rk.HOOK_Y, "display", 96, SAND)
        self.hook, _ = m.lines_sprite(["WHICH WAY", "WAS UP?"], rk.HOOK_Y + 112, size=136)
        # Hook 1: Wand klappt in Sandstein-Signatur und Baenke auf (gleichmaessige Punkte: keine Koernung, keine Antwort)
        beds = [[(x, BB[k] + 2.5 * math.sin(x / 90 + k)) for x in range(WX0, WX1 + 1, 20)] for k in range(1, 6)]
        self.geo = kl.GeoReveal(wall_poly, "sandstone", RH[0], RH[1], pat_alpha=85, beds=beds, seed=8)

        # Koernung je Bank (heutige Lage: grob oben) und alle zusammen (fuer die Drehung)
        self.bed_spr = [m.sprite(lambda im, k=k: draw_grains(im, grains(k))) for k in range(6)]
        self.brushed = m.sprite(lambda im: draw_grains(im, grains(3, BRUSH_X0, BRUSH_X1, seed=1, dens=0.9)))
        self.all_grains = m.sprite(lambda im: [draw_grains(im, grains(k)) for k in range(6)])
        def tops(im):
            d = ImageDraw.Draw(im)
            for k in range(6):
                d.line([P(WX0 + 10, BB[k] + 9), P(WX1 - 10, BB[k] + 9)], fill=o.rgb(C["magnesia"]), width=int(4 * o.S))
        self.top_lines = [m.sprite(lambda im, k=k: ImageDraw.Draw(im).line([P(WX0 + 10, BB[k] + 9), P(WX1 - 10, BB[k] + 9)],
                                                                           fill=o.rgb(C["magnesia"]), width=int(4 * o.S)))
                          for k in range(6)]

        # Zug 1: Schaufenster mit einer normal gradierten Bank (grob unten)
        x0, y0, x1, y1 = PANEL
        def panel(im):
            d = ImageDraw.Draw(im)
            d.rounded_rectangle([P(x0, y0), P(x1, y1)], radius=int(18 * o.S), fill=o.rgb(C["obsidian"], 245),
                                outline=o.rgb(C["magnesia"]), width=int(4 * o.S))
            d.rectangle([P(x0 + 14, y0 + 60), P(x1 - 14, y1 - 14)], fill=o.rgb(C["water"], 38))
            d.line([P(x0 + 14, PB1 + 6), P(x1 - 14, PB1 + 6)], fill=o.rgb(C["slate"]), width=int(3 * o.S))
        self.panel = m.sprite(panel)
        rnd = random.Random(31); self.pgrains = []
        for _ in range(260):
            y = rnd.uniform(PB0, PB1); frac = (y - PB0) / (PB1 - PB0)
            if rnd.random() > 0.35 + 0.65 * (1 - frac) and frac < 0.6:
                continue
            r = (1.6 + 7.4 * frac ** 1.4) * rnd.uniform(0.75, 1.05)
            self.pgrains.append((rnd.uniform(x0 + 26, x1 - 26), y, r, rnd.uniform(0, 1)))
        self.pgrains.sort(key=lambda g: -g[1])                         # unten zuerst
        n = len(self.pgrains)
        self.pg_t = [T_FALL0 + (T_FALL1 - T_FALL0 - 0.3) * (k / n) ** 0.9 for k in range(n)]
        self.lab_c = m.text_sprite("COARSE", 456, PB1 - 34, "mono", 30, C["magnesia"], tracking=0.1)
        self.lab_f = m.text_sprite("FINE", 498, PB0 - 26, "mono", 30, C["magnesia"], tracking=0.1)
        self.tick_c = m.sprite(lambda im: ImageDraw.Draw(im).line([P(582, PB1 - 18), P(x0 - 6, PB1 - 18)], fill=o.rgb(C["magnesia"]), width=int(3 * o.S)))
        self.tick_f = m.sprite(lambda im: ImageDraw.Draw(im).line([P(582, PB0 - 10), P(x0 - 6, PB0 - 10)], fill=o.rgb(C["magnesia"]), width=int(3 * o.S)))

        # Zug 2: Labels an der gebuersteten Bank (Bildkoordinaten im Zoom)
        tx = lambda x: ZC[0] + (x - ZC[0]) * ZOOM; ty = lambda y: ZC[1] + (y - ZC[1]) * ZOOM
        xr = tx(BRUSH_X1)
        self.lab2_c = m.text_sprite("COARSE", int(xr + 30), int(ty(BB[3] + 14) - 14), "mono", 30, C["magnesia"], tracking=0.1)
        self.lab2_f = m.text_sprite("FINE", int(xr + 30), int(ty(BB[4] - 14) - 16), "mono", 30, C["magnesia"], tracking=0.1)
        self.tick2 = m.sprite(lambda im: [ImageDraw.Draw(im).line([P(xr + 4, ty(yy)), P(xr + 24, ty(yy))], fill=o.rgb(C["magnesia"]), width=int(3 * o.S))
                                          for yy in (BB[3] + 14, BB[4] - 14)])

        # Texte
        self.text1, _ = m.lines_sprite(["COARSE BELOW,", "FINE ON TOP."], 352, role="display_xb", size=118)
        self.text2, _ = m.lines_sprite(["BUT HERE:", "COARSE ON TOP…"], 352, role="display_xb", size=118)
        self.text3, _ = m.lines_sprite(["EVERY BED", "AGREES."], 352, role="display_xb", size=118)
        self.call, _ = m.lines_sprite(["UP THE", "WALL?"], 352, role="display_xb", size=118)
        self.answer, _ = m.lines_sprite(["UP WAS DOWN."], 352, size=200)
        self.fazit, _ = m.lines_sprite(["HERE, UP", "MEANS OLDER."], 352, size=150)

    # -------------------------------------------------------------- Teile
    def brush(self, f, t, pose):
        """Buerste in der rechten Hand (Holzgriff, helle Borsten), nur waehrend des Buerstens."""
        op = seg(t, T_S3 + 0.2, 0.3) * (1 - seg(t, T_BR1 + 0.2, 0.3))
        if op <= 0:
            return
        hx, hy = self.climber.joints(pose)["rh"]
        lay = Image.new("RGBA", f.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        a = int(255 * op)
        d.line([(hx - 4, hy + 4), (hx + 18, hy - 22)], fill=o.rgb("#8C6A48", a), width=7)
        d.rounded_rectangle([hx - 16, hy + 2, hx + 16, hy + 14], radius=3, fill=o.rgb("#5C4632", a))
        for k in range(7):
            d.line([(hx - 13 + 4.3 * k, hy + 14), (hx - 14 + 4.3 * k, hy + 24)], fill=o.rgb(C["magnesia"], a), width=2)
        f.alpha_composite(lay)

    def flip_grains(self, f, s):
        """Koernung aller Baenke um die waagrechte Achse YC drehen: s = 1 heute, -1 Ablagerungslage."""
        spr = self.all_grains
        hh = max(1, int(round(spr.h * abs(s))))
        img = spr.img.resize((spr.w, hh), Image.BICUBIC)
        if s < 0:
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
        y = YC + (spr.y - YC) * abs(s) if s >= 0 else YC - (spr.y + spr.h - YC) * abs(s)
        m.composite(f, img, spr.x, int(round(y)))

    def world(self, t):
        f = self.bg.copy()
        u = seilzug(seg(t, T_GEO, 0.5))                                # Hook 1: Wand klappt in Sandstein auf
        if u > 0 and t < T_OUT + 0.4:
            self.geo.put(f, u, fade=1 - seg(t, T_OUT, 0.4))
        pose = climber_pose(t)
        # Koernung: gebuersteter Streifen, dann alle Baenke, Drehung im Payoff
        if T_BR0 <= t < T_EVERY + 0.4:
            _, reach = brush_x(t)
            put(f, crop_x(self.brushed, BRUSH_X0, reach), op=1 - seg(t, T_EVERY + 0.1, 0.3))
        if t >= T_EVERY:
            if t < T_FLIP:
                for i, k in enumerate(ORDER):
                    v = seg(t, T_EVERY + 0.3 * i, 0.4)
                    put(f, self.bed_spr[k], op=v)
                    g = seg(t, T_EVERY + 0.3 * i + 0.2, 0.7)
                    if 0 < g < 1:
                        put(f, self.top_lines[k], op=math.sin(math.pi * g))
            else:
                v = seilzug(seg(t, T_FLIP, 1.0)); w = seilzug(seg(t, T_BACK, 0.8))
                ang = math.pi * v * (1 - w)
                self.flip_grains(f, math.cos(ang))
        # Staub beim Buersten
        if T_BR0 <= t < T_BR1 + 0.8:
            dr = ImageDraw.Draw(f); rnd = random.Random(int(t * 30) // 3)
            bx, _ = brush_x(t)
            for k in range(14):
                life = ((t * 1.7 + k * 0.137) % 1.0)
                px = bx + rnd.uniform(-22, 22) + 10 * life; py = BRUSH_Y + 10 + 120 * life * life
                if t > T_BR1:
                    life = max(life, seg(t, T_BR1, 0.8))
                a = int(170 * (1 - life))
                if a > 8:
                    dr.ellipse([px - 2, py - 2, px + 2, py + 2], fill=o.rgb(SAND, a))
        put(f, self.climber.sprite(pose))
        self.brush(f, t, pose)
        kl.chalk_puff(f, t, T_GRAB, RH[0], RH[1] - 4, seed=11)
        kl.chalk_puff(f, t, T_BR1 + 0.6, RH[0], RH[1] - 4, seed=12, size=0.5)
        kl.chalk_puff(f, t, T_CLIMB + 0.85, RH[0], RH[1] + DY - 4, seed=15, size=0.8)
        # Schwebstaub im Licht (Bewegung in den Haltezeiten)
        dr = ImageDraw.Draw(f); rnd = random.Random(44)
        for k in range(18):
            x = rnd.uniform(160, 1040); y0 = rnd.uniform(860, 1440); sp = rnd.uniform(6, 14)
            yy = y0 - (t * sp) % 120; xx = x + 8 * math.sin(t * 0.7 + k)
            a = int(60 + 40 * math.sin(t * 1.3 + k))
            dr.ellipse([xx - 1.6, yy - 1.6, xx + 1.6, yy + 1.6], fill=o.rgb(C["magnesia"], a))
        return f

    def panel_layer(self, f, t):
        """Zug 1: Schaufenster, die Bank setzt sich ab (unten zuerst, grob unten), Labels."""
        op = seilzug(seg(t, T_S2, 0.5)) * (1 - seg(t, T1_OFF, 0.4))
        if op <= 0:
            return
        sc = lerp(0.92, 1.0, seilzug(seg(t, T_S2, 0.5)))
        x0, y0, x1, y1 = PANEL
        put(f, self.panel, op=op, scale=sc, anchor=((x0 + x1) / 2, (y0 + y1) / 2))
        if sc < 0.995:
            return
        lay = Image.new("RGBA", f.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        for (x, y, r, ph), ts in zip(self.pgrains, self.pg_t):
            u = seg(t, ts, 0.32)
            if u <= 0:
                continue
            yy = lerp(y0 + 70, y, sturz(u)) + (2 * math.sin(t * 3 + ph * 6) if u >= 1 else 0)
            col = SAND if r > 3.2 else SAND_D
            d.ellipse([x - r, yy - r * 0.82, x + r, yy + r * 0.82], fill=o.rgb(col, int(230 * op)))
        for k in range(5):                                             # Wasser bewegt sich
            yy = y0 + 90 + k * 34 + 4 * math.sin(t * 1.5 + k)
            d.line([(x0 + 40 + 30 * k, yy), (x0 + 110 + 30 * k, yy)], fill=o.rgb(C["ice"], int(60 * op)), width=2)
        f.alpha_composite(lay)
        for lab, tick, t0 in ((self.lab_c, self.tick_c, T_LAB_C), (self.lab_f, self.tick_f, T_LAB_F)):
            v = seilzug(seg(t, t0, EIN)) * (1 - seg(t, T1_OFF, 0.3))
            put(f, tick, op=v); put(f, lab, dx=lerp(-20, 0, v), op=v)

    # -------------------------------------------------------------- Frames
    def frame(self, t):
        if t < T_HOOK + 0.5:                                           # Szene 1: Hook
            f = m.zoomed(self.world(t), 1 + 0.03 * seilzug(seg(t, 0, T_HOOK)), 520, 1150)
            put(f, self.rails[0])
            self.hook1.draw(f, t, hook_bis=T_HOOK)
            u = seilzug(seg(t, T_Q, EIN))
            if u > 0:
                fade = 1 - seg(t, T_HOOK, 0.12)
                put(f, self.label, dx=lerp(-30, 0, u), op=u * fade)
                put(f, self.hook_kick, dx=lerp(-40, 0, u), op=u * fade)
                put(f, self.hook, dx=lerp(-40, 0, u), op=u * fade)
            if t >= T_HOOK:
                put(f, rk.wave(seg(t, T_HOOK, 0.5), cx=RH[0], cy=RH[1]))
            return f, 81
        if t < T_S5:
            z = 1.0 if t < T_Z0 else lerp(1.0, ZOOM, seilzug(seg(t, T_Z0, T_Z1 - T_Z0)))
            if t < T_Z0:
                z = 1 + 0.03 * (1 - seg(t, T_HOOK + 0.5, 0.6)) + 0.025 * seg(t, T_S2, T_Z0 - T_S2)   # sanfter Push-in
            if t >= T_S4:
                z *= lerp(1.0, PUSH, 0.5 - 0.5 * math.cos(math.pi * seg(t, T_S4, T_S5 - T_S4)))
            f = m.zoomed(self.world(t), z, *ZC)
            if t < T_S3:                                               # Szene 2: Zug 1
                put(f, self.rails[1]); self.rail.pop(f, t, 0, T_S2)
                self.panel_layer(f, t)
                u = seilzug(seg(t, T_S2 + 0.6, EIN)); put(f, self.text1, dx=lerp(-40, 0, u), op=u * (1 - seg(t, T1_OFF, 0.25)))
                if t < T_HOOK + 0.5:
                    put(f, rk.wave(seg(t, T_HOOK, 0.5), cx=RH[0], cy=RH[1]))
                return f, 82
            put(f, self.rails[3] if t >= T_S4 else self.rails[2])     # Szene 3: Zug 2, Callback, Payoff
            self.rail.pop(f, t, 1, T_S3)
            u = seilzug(seg(t, T_TXT2, EIN)); put(f, self.text2, dx=lerp(-40, 0, u), op=u * (1 - seg(t, T2_OFF, 0.25)))
            v = seilzug(seg(t, T_LAB2, EIN)) * (1 - seg(t, T2_OFF, 0.25))
            put(f, self.tick2, op=v); put(f, self.lab2_c, op=v); put(f, self.lab2_f, op=v)
            u = seilzug(seg(t, T_EVERY + 0.1, EIN)); put(f, self.text3, dx=lerp(-40, 0, u), op=u * (1 - seg(t, T3_OFF, 0.25)))
            u = seilzug(seg(t, T_CALL, EIN)); put(f, self.call, dx=lerp(-30, 0, u), op=u * (1 - seg(t, T_S4, 0.12)))
            u = seg(t, T_S4, 0.3)
            if u > 0:
                self.rail.logo_pop(f, t, T_S4)
                put(f, self.answer, op=min(1, u * 2) * (1 - seg(t, T_S5 - 0.2, 0.2)), scale=lerp(1.18, 1.0, seilzug(u)), anchor=(X0, 352))
            return f, 83
        if t < T_END:                                                  # Szene 4: Folge
            z = lerp(ZOOM * PUSH, 1.0, seilzug(seg(t, T_S5, 0.8)))
            z *= 1 + 0.03 * (0.5 - 0.5 * math.cos(math.pi * seg(t, T_S5 + 0.8, T_END - T_S5 - 0.8)))
            f = m.zoomed(self.world(t), z, *ZC)
            put(f, self.rails[3])
            u = seilzug(seg(t, T_FAZ, EIN)); put(f, self.fazit, dx=lerp(-40, 0, u), op=u)
            return f, 84
        return self.outro.frame(t, T_END), 85


# ------------------------------------------------------------------ Ton: Musik in A-Dur, 76 BPM
A_, FSM7, DMAJ7, BM7, E_, ESUS4, CSM7, FSM9 = ([57, 61, 64, 69], [54, 57, 61, 64], [54, 57, 61, 62], [54, 57, 59, 62],
                                              [56, 59, 64, 68], [57, 59, 64], [56, 59, 61, 64], [54, 57, 61, 64, 68])
PENTA = [69, 71, 73, 76, 78, 81, 83, 85, 88]   # A-Dur-Pentatonik ab A4


def sound_events(b):
    """Musik in A-Dur mit Fis-Moll-Flaechen (76 BPM) nach Szenen; Hook 1 musikalisch; Koerner im Schaufenster als
    steigende Toene (grob zuerst, tief), Baenke als Tonleiter aufwaerts, Drehung mit fallender Figur, Akkordschlag zur
    Aufloesung, Klanglogo im Abspann. Geraeusche leise (Buerste, Kreide)."""
    h1 = rk.Hook1(t_grab=T_GRAB, t_geo=T_GEO, t_out=T_OUT)
    b.hook1(h1, akkord=FSM7, bassnote=42)
    b.musik([
        (T_Q - 0.1, T_Q + 1.9, FSM7, 42, "ruhig"),              # Frage: offen
        (T_Q + 1.9, T_HOOK, DMAJ7, 38, "ruhig"),
        (T_HOOK, T_S2, A_, 45, "flaeche"),                      # Welle
        (T_S2, T_S2 + 2.0, A_, 45, "flaeche"),                  # Bank setzt sich ab (Koerner als Toene)
        (T_S2 + 2.0, T1_OFF, E_, 40, "ruhig"),
        (T1_OFF, T_S3, BM7, 47, "flaeche"),                     # Zoom
        (T_S3, T_S3 + 2.0, FSM7, 42, "bewegt"),                 # Buersten
        (T_S3 + 2.0, T2_OFF, DMAJ7, 38, "bewegt"),
        (T2_OFF, T_CALL, CSM7, 37, "steigend"),                 # alle Baenke
        (T_CALL, T_RISE, BM7, 47, "ruhig"),                     # "UP THE WALL?"
        (T_RISE, T_S4 - 0.15, ESUS4, 40, "flaeche"),            # Steigerung, dann 0,15 s Stille
        (T_S4, T_FLIP, FSM9, 42, "flaeche"),                    # Aufloesung
        (T_FLIP, T_FLIP + 1.0, FSM9, 42, "fallend"),            # Koernung dreht sich
        (T_FLIP + 1.0, T_S5, FSM9, 42, "flaeche"),
        (T_S5, T_FAZ, DMAJ7, 38, "ruhig"),                      # Zoom zurueck, zurueckdrehen
        (T_FAZ, T_END, A_, 45, "ruhig"),                        # Fazit: nach A-Dur aufgeloest
        (T_END, DUR, A_, 45, "flaeche"),                        # Abspann
    ], bpm=76.0, gain=-12.0)
    b.synth("whoosh", T_HOOK, -18.0, "welle", dur=0.55, seed=4)
    b.ton("zupf", T_S2, -14.0, "bohrhaken", m=81, dauer=0.9)
    for k in range(8):                                           # Koerner setzen sich: grob/tief zuerst, fein/hoch zuletzt
        b.ton("zupf", T_FALL0 + 0.3 + k * (T_FALL1 - T_FALL0 - 0.3) / 8, -17.0, "koerner", m=PENTA[k] - 12, dauer=0.6,
              pan=0.3 * ((k % 3) - 1))
    b.ton("zupf", T_LAB_C, -16.0, "label", m=69, dauer=0.8)
    b.ton("zupf", T_LAB_F, -16.0, "label", m=81, dauer=0.8)
    b.ton("schwelle", T_Z0 - 0.3, -15.0, "zoom", akkord=BM7, dauer=0.5)
    b.ton("zupf", T_S3, -14.0, "bohrhaken", m=83, dauer=0.9)
    for k in range(3):                                           # Buerstenstriche (leise)
        b.kenney("interface-sounds", "scratch_002.ogg", T_BR0 + k * (T_BR1 - T_BR0) / 3, -22.0, "buerste")
    b.ton("zupf", T_LAB2, -16.0, "label", m=76, dauer=0.8)
    for i in range(6):                                           # Baenke zeigen sich: Tonleiter aufwaerts
        b.ton("zupf", T_EVERY + 0.3 * i + 0.2, -15.0, "baenke", m=PENTA[i + 1], dauer=0.8, pan=0.2 * (i % 3 - 1))
    b.ton("zupf", T_CALL, -10.0, "frage", m=73, dauer=0.9)      # Frage: steigende Quarte
    b.ton("zupf", T_CALL + 0.2, -10.0, "frage", m=78, dauer=1.2)
    b.ton("schwelle", T_RISE, -8.0, "steigerung", akkord=ESUS4, dauer=T_S4 - 0.15 - T_RISE)
    b.klang("sub_hit", T_S4 - 0.01, -10.0, "payoff-einschlag", f0=78.0, f1=36.0)
    b.ton("akzent", T_S4, -4.0, "payoff", akkord=FSM9, bassnote=42)
    b.synth("whoosh", T_FLIP, -20.0, "drehung", dur=0.9, seed=7)
    b.ton("schwelle", T_BACK - 0.1, -16.0, "zurueckdrehen", akkord=DMAJ7, dauer=0.8)
    b.ton("zupf", T_FAZ, -14.0, "fazit", m=76, dauer=0.9)
    b.klang("chalk_slap", T_CLIMB + 0.85, -12.0, "griff", seed=2)
    b.klanglogo(T_END + 0.3, tonika=69, gain=-7.0)               # Abspann: Logo (A-Dur)
    b.ton("zupf", T_END + 1.3, -12.0, "herz", m=81, dauer=1.2)


if __name__ == "__main__":
    if "--reach" in sys.argv:
        print(check_reach())
        sys.exit(0)
    rk.run(Reel, sound_events, META)
