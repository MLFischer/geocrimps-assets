#!/usr/bin/env python3
"""Reel 003 -- MYTH OR ROCK #01: "Looks dry. So why wait?" (Faktenbasis: Post #015, Font nach Regen).

Fassung 2 vom 13.10.2026, Ablauf "offene_frage" (statt Quiz): offene W-Frage ohne Antwortauswahl, die Hook-Frage
steht 3,3 s; Zug 1 scheint harmlos (die Oberflaeche trocknet zuerst), Zug 2 bringt die Wendung (am Griff ziehen ->
er bricht, innen ist der Sand nass), die Frage kehrt zurueck (Callback, steht 1,25 s), dann die Antwort.
Fassung 3 (13.10.2026, mittags): Meta-Hook "GEOCRIMPS . GEOLOGY OF CLIMBING" in Frame 0 (reelkit.meta_hook),
Formatlabel und Hook 52 px tiefer, Sonne und Wolke deshalb 40 px tiefer.
Fassung 4 (14.10.2026, Markus 13.10.: "hook 1 (klettern und geologie) und dann hook 2 (eigentliches reel thema)"):
Hook 1 0-1,22 s: GEOCRIMPS + CLIMBING ab Frame 0, ein Kletterer startet vom Crashpad und klatscht an den Sloper
(Kreidewolke), "x GEOLOGY" schlaegt ein und der Block klappt in seinen Sandstein auf (Fontainebleau ist Sandstein).
Hook 2 ab 1,5 s: "IT LOOKS DRY. WHY NOT CLIMB?" (vorher "LOOKS DRY. SO WHY WAIT?"), der Kletterer haengt am Block.
Zug 1: er wartet auf dem Pad, waehrend der Block abtrocknet. Zug 2: er zieht am Sloper, der bricht, er faellt aufs Pad
(statt Pfeil). Callback "WHY NOT CLIMB?". Alle Zeiten ab Hook 2 1,5 s spaeter als in Fassung 3. Ton: Hook-1-Signatur
in G, Puls 108 BPM von Hook 2 bis zur Steigerung, Einschlag beim Bruch, Aufprall aufs Pad.
Bildmittel (fuer die Abwechslungsregel): Uebergang Lichtstreifen und Zoom (keine Isolinien-Welle) | Enthuellung
Zeitraffer und Bruch (kein Querschnitt) | Payoff Antwort gross, dann Stempel MYTH und Kreide-Wisch | Flaeche eine
Quarte hoeher (ratio 1.335).
Dramaturgie (Topo): Hook 0-3,3 s | Zug 1 Regen und Abtrocknen 3,55-6,55 s | Zug 2 Zoom, Ziehen, Bruch 6,8-8,7 s |
Callback 8,7-9,95 s | Payoff 9,95 s (72 %) | Folge: Urteil MYTH, warten 11,05-13,0 s | Endsignet 13,0-13,8 s.
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
import kletter as kl
from outcrop import C, P
from motion import X0, W, H, seg, seilzug, sturz, griff, lerp, put

# ------------------------------------------------------------------ Zeitplan
H1 = 1.50                          # 14.10.2026: Hook 1 davor, alles ab Hook 2 1,5 s spaeter
T_GRAB, T_GEO, T_OUT = 0.32, 0.58, 1.22                       # Hook 1: Griff, "x GEOLOGY", Uebergang in die Kopfzeile
T_Q = 1.50                                                    # Hook 2: Formatlabel und Themenfrage fahren ein
T_HOOK = 3.30 + H1                 # Hook-2-Frage steht 3,3 s (Lesezeit), dann Lichtstreifen
T_S2 = 3.55 + H1                   # Zug 1: Regen, dann trocknet die Oberflaeche
T_RAIN = [3.62 + H1 + 0.08 * k for k in range(7)]
FALL = 0.40
T_DRY = 4.95 + H1                  # Abtrocknen
T_Z0, T_Z1 = 6.55 + H1, 7.05 + H1  # Zoom auf die Schulter
ZOOM, ZC = 1.22, (880, 1040)
T_S3 = 6.80 + H1                   # Zug 2
T_PULL, T_JIG, T_CRACK, T_SNAP = 7.10 + H1, 7.45 + H1, 7.85 + H1, 8.10 + H1
T_LAND = T_SNAP + 0.40             # Kletterer landet auf dem Pad
T_DRIPS = (8.45 + H1, 8.85 + H1, 9.25 + H1)
T_LAB = 8.40 + H1
T_CALL = 8.70 + H1                 # Callback: die Frage kehrt zurueck und steht bis zum Payoff (1,25 s Lesezeit)
T_RISE = 9.05 + H1
T_S4 = 9.95 + H1                   # Payoff
T_S5 = 11.05 + H1                  # Zoom zurueck, Urteil und Folge
T_STAMP, T_SWIPE, T_OR = 11.25 + H1, 11.55 + H1, 11.90 + H1
T_END = 13.00 + H1
DUR = T_END + 0.8

META = dict(
    slug="2026-10-16_mythorrock-01", dur_range=[12.5, 17.5], payoff_t=T_S4,
    title="GeoCrimps r003 MYTH OR ROCK #01 (Offene Frage), Fassung 4", ablauf="offene_frage",
    hook1_bis=T_OUT, hook_ab=T_Q, hook_bis=T_HOOK, weitere_fragen=[[T_CALL, T_S4]], cover_t=T_Q + 0.85,
    on_screen=["MYTH OR ROCK", "IT LOOKS DRY. WHY NOT CLIMB?", "THE SURFACE DRIES FIRST.", "BUT PULL ON IT…",
               "WHY NOT CLIMB?", "STILL WET INSIDE.", "MYTH", "WAIT A DAY OR TWO."],
    labels=["WET SAND"],
    qc_times=[0.0, 0.32, 0.6, 1.0, 1.4, 2.35, 4.4, 5.0, 5.4, 6.8, 8.3, 9.0, 9.75, 10.4, 11.8, 13.3],
    marks=[(0, "Hook 1"), (T_GRAB, "Griff"), (T_GEO, "x GEOLOGY"), (T_Q, "Hook 2"), (T_HOOK, "Lichtstreifen"),
           (T_S2, "Zug 1"), (T_DRY, "trocknet"), (T_Z0, "Zoom"), (T_S3, "Zug 2"), (T_PULL, "Ziehen"), (T_SNAP, "Bruch"),
           (T_CALL, "Callback"), (T_S4, "PAYOFF"), (T_S5, "Zoom zurueck"), (T_STAMP, "Stempel"), (T_END, "Klanglogo")])

# ------------------------------------------------------------------ Block (Font-Sloper) und Farben
XL, XR, HB = 120, 1030, 520        # Block: linke/rechte Fusskante, Hoehe
CX, HA = (XL + XR) / 2, (XR - XL) / 2
# Profil eines Font-Blocks: breit, oben flach, rechts eine gerundete Schulter (der Sloper); Catmull-Rom-Spline
_CTRL = [(0.00, 0), (0.02, 150), (0.06, 290), (0.13, 400), (0.25, 470), (0.40, 505), (0.55, 512), (0.68, 495),
         (0.79, 455), (0.88, 390), (0.94, 300), (0.98, 190), (0.995, 80), (1.0, 0)]
CRUST, CRUST_IN, SCAR = "#D8C6A3", "#9E8A68", "#B89A6E"
WET_SAND, WET_EDGE = "#3D352C", "#6E6150"      # feuchter Sand in der Bruchflaeche
YB_MAIN = 1420                     # Fusslinie
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

def boulder_front(im, yb, broken=False, ticks=True, wet=False):
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
        _scar(im, yb, front=True, wet=wet)
    if ticks:
        o.chalk_ticks(im, 640, top_y(640, yb) + 52, angle_deg=-30, seed=2)

def _scar(im, yb, front, wet=False):
    """Bruchstelle: Schulter fehlt, Bruchflaeche ohne Kruste; wet=True: innen dunkel-feucht mit Wasserglanz."""
    inner, outer = crack_curve(yb)
    d = ImageDraw.Draw(im)
    cut = outer + inner[::-1]
    cut_out = [(x + 2.5 * (x - CX) / HA, y - 3) for x, y in outer] + inner[::-1]
    d.polygon([P(*p) for p in cut_out], fill=o.rgb(C["obsidian"]))
    if wet:
        face = offset(inner, 32)
        d.polygon([P(*p) for p in inner + face[::-1]], fill=o.rgb(WET_SAND))
        rnd = random.Random(14)
        for _ in range(150):
            i = rnd.randrange(len(inner)); f = rnd.uniform(0.15, 0.95)
            x = inner[i][0] + (face[i][0] - inner[i][0]) * f; y = inner[i][1] + (face[i][1] - inner[i][1]) * f
            r = rnd.uniform(1.4, 3.2)
            d.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=o.rgb(rnd.choice([C["water"], C["water"], C["ice"]]), 230))
        d.line([P(*p) for p in inner], fill=o.rgb(WET_EDGE), width=int(4 * o.S), joint="curve")
    else:
        face = offset(inner, 13 if front else 8)
        d.polygon([P(*p) for p in inner + face[::-1]], fill=o.rgb(SCAR, 230 if front else 190))
        d.line([P(*p) for p in inner], fill=o.rgb(SCAR), width=int(4 * o.S), joint="curve")
    return cut



# ------------------------------------------------------------------ Kletterer, Crashpad, Geologie (Fassung 4)
BACK = dict(sw=22, hw=13, eb=(-1, 1), kb=(1, -1))       # Rueckenansicht: Ellbogen und Knie nach aussen
PAD = (515, 845, YB_MAIN + 36)                           # Crashpad: x0, x1, Unterkante (vor dem Block)
PAD_TOP = PAD[2] - 40
SLOPER = (902, top_y(902, YB_MAIN) + 12)                 # rechte Hand: der Sloper auf der Schulter (bricht in Zug 2)
FACE = (724, 1150)                                       # linke Hand: Seitgriff in der Wand
POSE_START = dict(BACK, hip=(780, 1292), lean=-4, lh=FACE, rh=(866, 1110), lf=(728, PAD_TOP - 3), rf=(832, PAD_TOP - 3))
POSE_GRAB = dict(BACK, hip=(806, 1228), lean=6, lh=FACE, rh=SLOPER, lf=(744, 1346), rf=(856, 1328))
POSE_SWING = dict(POSE_GRAB, hip=(812, 1218), lean=9)    # Schwung beim Zugreifen
POSE_PULL = dict(POSE_GRAB, hip=(818, 1226), lean=-10, lf=(740, 1352), rf=(846, 1342))   # lehnt sich zurueck, Arm gestreckt
POSE_STAND = dict(BACK, hip=(700, PAD_TOP - 168), lean=0, lh=(676, PAD_TOP - 128), rh=(724, PAD_TOP - 128),
                  lf=(680, PAD_TOP - 2), rf=(720, PAD_TOP - 2))   # wartet auf dem Pad
POSE_DOWN = dict(BACK, hip=(690, PAD_TOP - 26), lean=-28, lh=(612, PAD_TOP - 4), rh=(812, PAD_TOP - 150),
                 lf=(770, PAD_TOP - 4), rf=(812, PAD_TOP - 22))   # nach dem Sturz: sitzt auf dem Pad, Arm noch oben
POSE_SIT = dict(POSE_DOWN, rh=(760, PAD_TOP - 60), lean=-22)


def climber_pose(t):
    """Hook 1: vom Pad an den Block (Frame 0 schon in Bewegung), Griff bei T_GRAB; haengt in Hook 2; springt beim
    Lichtstreifen ab und wartet auf dem Pad; steigt zum Zoom wieder ein, zieht, der Sloper bricht, er faellt aufs Pad."""
    if t < T_GRAB:
        return kl.lerp_pose(POSE_START, POSE_SWING, seilzug(seg(t, 0.0, T_GRAB)))
    if t < T_HOOK:
        u = seg(t, T_GRAB, 0.3)
        p = kl.lerp_pose(POSE_SWING, POSE_GRAB, 0.5 - 0.5 * math.cos(math.pi * u))
        if u >= 1:
            w = math.sin(2 * math.pi * (t - T_GRAB - 0.3) / 2.4)
            p = dict(p, hip=(p["hip"][0] + 4 * w, p["hip"][1] + 1.5 * abs(w)), lean=p["lean"] + 1.5 * w)
        return p
    if t < T_Z0:
        u = seg(t, T_HOOK, 0.42)                                  # Absprung aufs Pad (unter dem Lichtstreifen)
        return kl.lerp_pose(POSE_GRAB, POSE_STAND, sturz(u))
    if t < T_PULL:
        return kl.lerp_pose(POSE_STAND, POSE_GRAB, seilzug(seg(t, T_Z0, T_PULL - 0.05 - T_Z0)))
    if t < T_SNAP:
        p = kl.lerp_pose(POSE_GRAB, POSE_PULL, seilzug(seg(t, T_PULL, T_SNAP - T_PULL)))
        if t >= T_JIG:
            j = 2.5 * math.sin(t * 70)
            p = dict(p, hip=(p["hip"][0] + j, p["hip"][1]))
        return p
    if t < T_LAND:
        u = seg(t, T_SNAP, T_LAND - T_SNAP)
        p = kl.lerp_pose(POSE_PULL, POSE_DOWN, u * u)              # faellt (beschleunigt)
        return dict(p, rh=(SLOPER[0] + 40 * u, SLOPER[1] + 60 * u)) if u < 0.35 else p
    u = seg(t, T_LAND, 0.5)
    return kl.lerp_pose(POSE_DOWN, POSE_SIT, seilzug(u))


class Reel(rk.ReelBase):
    DUR = DUR

    def __init__(self):
        super().__init__()
        self.rail = rk.Rail(2)
        self.end = rk.EndSting()
        self.rails = [rk.rail_sprite(0, 2), rk.rail_sprite(1, 2), rk.rail_sprite(2, 2), rk.rail_sprite(2, 2, logo_on=True)]
        self.hook1 = rk.Hook1(t_grab=T_GRAB, t_geo=T_GEO, t_out=T_OUT)
        self.climber = kl.Climber(scale=1.0, width=18.0, torso_w=36.0)
        self.label = m.text_sprite("MYTH OR ROCK", X0, rk.FORMAT_Y, "stencil", 40, C["slate"], tracking=0.12)
        outer = surface(YB_MAIN)
        # Hintergruende ohne Topo-Linie (die kommt als Sprite, weil Szene 3 gezoomt wird)
        def sky(im):
            o.contour_field(im, 820, 1700, n=9, r0=140, step=64, alpha=80)
            d = ImageDraw.Draw(im); sx, sy, r = 968, 800, 40   # 40 px tiefer, Platz fuer den Meta-Hook
            for k in range(12):                                         # Sonne: Scheibe und Strahlen
                a = 2 * math.pi * k / 12
                d.line([P(sx + math.cos(a) * (r + 14), sy + math.sin(a) * (r + 14)), P(sx + math.cos(a) * (r + 34), sy + math.sin(a) * (r + 34))],
                       fill=o.rgb(C["magnesia"], 170), width=int(4 * o.S))
            d.ellipse([P(sx - r, sy - r), P(sx + r, sy + r)], fill=o.rgb(C["magnesia"], 235))
        def bg_dry(im):
            sky(im); ground(im, YB_MAIN); puddles(im, YB_MAIN); boulder_front(im, YB_MAIN); kl.crash_pad(im, *PAD)
        def bg_wet(im):
            sky(im); ground(im, YB_MAIN); puddles(im, YB_MAIN); boulder_front(im, YB_MAIN, broken=True, wet=True)
            kl.crash_pad(im, *PAD)
        self.bg = m.background(bg_dry)
        self.bg_broken = m.background(bg_wet)
        self.hook, _ = m.lines_sprite(["IT LOOKS DRY.", "WHY NOT", "CLIMB?"], rk.HOOK_Y, size=164)
        # Geologie des Blocks (Hook 1): Sandstein (Fontainebleau), flach liegende Schichten, radial vom Sloper aufgedeckt
        beds = [[(x, y0 + 6 * math.sin(x / 110 + k)) for x in range(XL, XR + 1, 20)] for k, y0 in enumerate(range(1000, 1420, 78))]
        self.geo = kl.GeoReveal(surface(YB_MAIN) + [(XR, YB_MAIN), (XL, YB_MAIN)], "sandstone", SLOPER[0], SLOPER[1],
                                pat_alpha=95, beds=beds, seed=8)
        # Zug 1: Regen -> Perlen auf der Kruste -> Abtrocknen
        rim = offset(outer, 9)
        self.crust_wet = m.sprite(lambda im: ImageDraw.Draw(im).polygon([P(*p) for p in outer + rim[::-1]], fill=o.rgb(C["water"])))
        body_poly = outer + [(XR, YB_MAIN), (XL, YB_MAIN)]
        self.body_dark = m.sprite(lambda im: ImageDraw.Draw(im).polygon([P(*p) for p in body_poly], fill=o.rgb(C["obsidian"])))
        rnd = random.Random(21)
        self.beads = []
        for k in range(30):
            x = rnd.uniform(XL + 40, XR - 40); y = top_y(x, YB_MAIN) + rnd.uniform(-2, 4)
            self.beads.append((x, y, rnd.uniform(4.0, 7.5), T_RAIN[k % 7] + FALL + rnd.uniform(0, 0.15), rnd.uniform(0, 0.5)))
        self.drop = m.sprite(lambda im: o.droplet(im, 540, 960, size=30))
        self.rain_x = [230, 350, 470, 590, 700, 810, 905]
        def cloud(im):
            d = ImageDraw.Draw(im)
            for cx, cy, r in ((900, 810, 70), (975, 782, 62), (1040, 818, 56), (840, 832, 48), (960, 840, 58)):
                d.ellipse([P(cx - r, cy - r * 0.72), P(cx + r, cy + r * 0.72)], fill=o.rgb("#4A545D"))
            d.rectangle([P(800, 830), P(1090, 870)], fill=o.rgb("#4A545D"))
        self.cloud = m.sprite(cloud)
        self.text1, _ = m.lines_sprite(["THE SURFACE", "DRIES FIRST."], 352, role="display_xb", size=118)
        # Zug 2: Bruchstueck (aus dem trockenen Hintergrund geschnitten)
        inner, outer_f = crack_curve(YB_MAIN)
        self.inner = inner
        mk = rk.mask_from(outer_f + inner[::-1])
        self.flake_box = mk.getbbox()
        fl = self.bg.copy(); fl.putalpha(mk); self.flake = fl.crop(self.flake_box)
        sx = (F0 + F1) / 2; sy = top_y(sx, YB_MAIN)
        self.pull = (sx - 26, sy - 78, sx + 70, sy + 22)
        self.text2, y2 = m.lines_sprite(["BUT PULL", "ON IT\u2026"], 352, role="display_xb", size=118)
        mid = inner[len(inner) // 2]
        self.lab = m.text_sprite("WET SAND", mid[0] - 230, mid[1] + 40, "mono", 30, C["magnesia"], tracking=0.1)
        self.lab_tick = m.sprite(lambda im: ImageDraw.Draw(im).line([P(mid[0] - 92, mid[1] + 56), P(mid[0] - 12, mid[1] + 18)],
                                                                     fill=o.rgb(C["magnesia"]), width=int(3 * o.S)))
        self.drip_src = [inner[int(len(inner) * f)] for f in (0.55, 0.75, 0.9)]
        self.call, _ = m.lines_sprite(["WHY NOT CLIMB?"], 352, role="display_xb", size=96, fill=C["slate"])
        # Payoff
        self.answer, ya = m.lines_sprite(["STILL WET", "INSIDE."], 352, size=200)
        # Folge: Urteil und Warten
        sw = o.text_width("WAIT A DAY", "display", 150)
        y5 = 360
        self.swipe = m.sprite(lambda im: o.chalk_swipe(im, X0 - 8, y5 + 18, X0 + sw + 14, y5 + 168, seed=9))
        self.wait = m.text_sprite("WAIT A DAY", X0, y5 + 8, "display", 150, C["obsidian"])
        self.ortwo = m.text_sprite("OR TWO.", X0, y5 + 184, "display", 150, C["magnesia"])
        self.swipe_box = (X0 - 8, y5 + 18, X0 + sw + 14, y5 + 168)
        self.stamp = self.make_stamp(700, 770, -7)

    def make_stamp(self, cx, cy, angle):
        s = o.S; f1 = o.font("stencil", 96); t1 = "MYTH"
        w1 = f1.getlength(t1); bw = int(w1 + 2 * 34 * s); bh = int((96 + 2 * 26) * s)
        im = Image.new("RGBA", (bw + 40 * s, bh + 40 * s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        ox, oy = 20 * s, 20 * s; col = o.rgb(C["magnesia"])
        d.rounded_rectangle([ox, oy, ox + bw, oy + bh], radius=14 * s, outline=col, width=6 * s)
        d.text((ox + bw / 2, oy + bh / 2 + 4 * s), t1, font=f1, fill=col, anchor="mm")
        rng = np.random.default_rng(6)
        a = np.asarray(im.getchannel("A"), np.float32)
        noise = np.asarray(Image.fromarray((rng.random(a.shape) * 255).astype(np.uint8)).resize(im.size), np.float32) / 255
        a *= np.clip(1.4 - noise * 1.05, 0.3, 1.0)
        im.putalpha(Image.fromarray(a.astype(np.uint8)))
        im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
        small = im.resize((im.width // s, im.height // s), Image.LANCZOS)
        return m.Sprite(small, int(cx - small.width / 2), int(cy - small.height / 2))

    # -------------------------------------------------------------- Szene in Weltkoordinaten (vor dem Zoom)
    def world(self, t):
        """Block, Wetter und Bruch zum Zeitpunkt t -- ohne Text und Topo-Linie."""
        if t < T_JIG:
            f = self.bg.copy()
        elif t < T_SNAP:
            f = self.bg.copy()
            jig = 2.0 * math.sin(t * 70)
            bb = self.flake_box
            f.paste(self.bg_broken.crop(bb), (bb[0], bb[1]))
            f.alpha_composite(self.flake, (int(bb[0] + jig), bb[1]))
            if t >= T_CRACK:
                n = max(2, int(len(self.inner) * sturz(seg(t, T_CRACK, 0.22))))
                ImageDraw.Draw(f).line(self.inner[:n], fill=o.rgb(C["magnesia"]), width=4)
        else:
            f = self.bg_broken.copy()
            u = seg(t, T_SNAP, 0.75)
            if u < 1:
                bb = self.flake_box
                rot = self.flake.rotate(-38 * sturz(u), resample=Image.BICUBIC, expand=True)
                cx = (bb[0] + bb[2]) / 2 + 110 * u; cy = (bb[1] + bb[3]) / 2 + 900 * u * u
                rot.putalpha(rot.getchannel("A").point(lambda a, k=1 - 0.3 * u: int(a * k)))
                m.composite(f, rot, int(cx - rot.width / 2), int(cy - rot.height / 2))
            dr = ImageDraw.Draw(f)
            for k, (x0, y0) in enumerate(self.drip_src):           # Wasser tropft aus der Bruchflaeche
                for rep in range(3):
                    t0 = T_DRIPS[k] + rep * 1.15
                    v = seg(t, t0, 0.55)
                    if 0 < v < 1:
                        y = y0 + 8 + 260 * v * v; a = int(230 * (1 - v * 0.6))
                        dr.ellipse([x0 - 4, y - 6, x0 + 4, y + 6], fill=o.rgb(C["water"], a))
        if T_S2 <= t < T_Z0 + 0.3:                                   # Regen, Perlen, Abtrocknen
            wet = seg(t, T_RAIN[0] + FALL - 0.05, 0.4) * (1 - seg(t, T_DRY, 1.1))
            put(f, self.body_dark, op=0.38 * wet)
            put(f, self.crust_wet, op=0.6 * wet)
            dr = ImageDraw.Draw(f)
            for x, y, r, ta, ph in self.beads:
                v = seg(t, ta, 0.2); dry = seg(t, T_DRY + ph, 0.8)
                rr = r * v * (1 - dry)
                if rr > 0.6:
                    dr.ellipse([x - rr, y - rr * 0.8, x + rr, y + rr * 0.55], fill=o.rgb(C["water"], 230))
                    dr.ellipse([x - rr * 0.4, y - rr * 0.6, x - rr * 0.05, y - rr * 0.25], fill=o.rgb(C["ice"], 230))
            cin = seilzug(seg(t, T_S2 - 0.05, 0.35)); cout = seilzug(seg(t, T_DRY - 0.1, 0.6))
            if cin > 0 and cout < 1:                                 # Wolke schiebt sich vor die Sonne, dann wieder weg
                put(f, self.cloud, dx=lerp(260, 0, cin) + lerp(0, 300, cout), op=min(1, cin * 1.5) * (1 - cout))
            for k, (x, t0) in enumerate(zip(self.rain_x, T_RAIN)):
                u = seg(t, t0, FALL)
                if 0 < u < 1:
                    y = lerp(820 + 25 * (k % 3), top_y(x, YB_MAIN) - 14, sturz(u)); put(f, self.drop, dx=x - 540, dy=y - 960, op=min(1, u * 5))
        if t < T_S2 or T_DRY <= t < T_Z0 + 0.3:                      # Verdunstung (Hook und Abtrocknen)
            v = (t % 2.2) / 2.2 if t < T_S2 else seg(t, T_DRY, 1.3)
            dr = ImageDraw.Draw(f)
            for k, x in enumerate(range(230, 990, 95)):
                ph = (v + k * 0.17) % 1.0
                yl = top_y(x, YB_MAIN) - 12 - 80 * ph
                pts = [(x + 6 * math.sin(yy / 9 + k), yy) for yy in range(int(yl), int(yl) - 34, -3)]
                dr.line(pts, fill=o.rgb(C["slate"], int(150 * math.sin(math.pi * ph))), width=3)
        u = seilzug(seg(t, T_GEO, 0.5))                              # Hook 1: Block klappt in seinen Sandstein auf
        if u > 0 and t < T_OUT + 0.4:
            self.geo.put(f, u, fade=1 - seg(t, T_OUT, 0.4))
        put(f, self.climber.sprite(climber_pose(t)))
        kl.chalk_puff(f, t, T_GRAB, SLOPER[0], SLOPER[1] - 4, seed=11)
        kl.chalk_puff(f, t, T_PULL - 0.05, SLOPER[0], SLOPER[1] - 4, seed=12, size=0.6)
        kl.chalk_puff(f, t, T_LAND, 690, PAD_TOP - 6, seed=13, size=0.9)        # Kreidestaub vom Pad beim Aufprall
        return f

    # -------------------------------------------------------------- Frames
    def frame(self, t):
        if t < T_HOOK + 0.25:                                        # Szene 1: Hook (Frame 0 = Cover)
            f = m.zoomed(self.world(t), 1 + 0.03 * seilzug(seg(t, 0, T_HOOK)), 640, 1000)
            put(f, self.rails[0])
            self.hook1.draw(f, t, hook_bis=T_HOOK)
            u = seilzug(seg(t, T_Q, 0.35))
            if u > 0:
                fade = 1 - seg(t, T_HOOK, 0.12)
                put(f, self.label, dx=lerp(-30, 0, u), op=u * fade)
                put(f, self.hook, dx=lerp(-40, 0, u), op=u * fade)
            if t >= T_HOOK:
                put(f, rk.light_sweep(seg(t, T_HOOK, 0.35)))
            return f, 41
        if t < T_S5:
            z = 1.0 if t < T_Z0 else lerp(1.0, ZOOM, seilzug(seg(t, T_Z0, T_Z1 - T_Z0)))
            f = m.zoomed(self.world(t), z, *ZC)
            if t < T_S3:                                             # Szene 2: Zug 1
                put(f, self.rails[1]); self.rail.pop(f, t, 0, T_S2)
                u = seilzug(seg(t, T_S2 + 0.05, 0.35)); put(f, self.text1, dx=lerp(-40, 0, u), op=u * (1 - seg(t, T_Z0, 0.25)))
                if t < T_HOOK + 0.35:
                    put(f, rk.light_sweep(seg(t, T_HOOK, 0.35)))
                return f, 42
            put(f, self.rails[3] if t >= T_S4 else self.rails[2])    # Szene 3: Zug 2, Callback, Payoff
            self.rail.pop(f, t, 1, T_S3)
            u = seilzug(seg(t, T_S3 + 0.05, 0.35)); put(f, self.text2, dx=lerp(-40, 0, u), op=u * (1 - seg(t, T_CALL - 0.15, 0.15)))
            u = seg(t, T_LAB, 0.3)
            if u > 0:
                tx = lambda x: ZC[0] + (x - ZC[0]) * z; ty = lambda y: ZC[1] + (y - ZC[1]) * z
                for spr in (self.lab, self.lab_tick):
                    dx = tx(spr.x) - spr.x; dy = ty(spr.y) - spr.y
                    put(f, spr, dx=dx, dy=dy, op=min(1, u * 1.8) * (1 - seg(t, T_S5 - 0.2, 0.2)))
            u = seilzug(seg(t, T_CALL, 0.3)); put(f, self.call, dx=lerp(-30, 0, u), op=u * (1 - seg(t, T_S4, 0.12)))
            u = seg(t, T_S4, 0.22)
            if u > 0:
                self.rail.logo_pop(f, t, T_S4)
                put(f, self.answer, op=min(1, u * 2) * (1 - seg(t, T_S5 - 0.2, 0.2)), scale=lerp(1.18, 1.0, seilzug(u)), anchor=(X0, 352))
            return f, 43
        if t < T_END:                                                # Szene 4: Urteil und Folge
            z = lerp(ZOOM, 1.0, seilzug(seg(t, T_S5, 0.3)))
            f = m.zoomed(self.world(t), z, *ZC)
            put(f, self.rails[3])
            u = seg(t, T_STAMP, 0.24)
            if u > 0:
                put(f, self.stamp, op=min(1, u * 3), scale=lerp(1.65, 1.0, griff(u)) if u < 1 else 1.0)
            rk.dust(f, t, T_STAMP + 0.18, (self.stamp.x + 30, self.stamp.y + 30, self.stamp.x + self.stamp.w - 30, self.stamp.y + self.stamp.h - 30), seed=78)
            put(f, m.reveal(self.swipe, seilzug(seg(t, T_SWIPE, 0.2))))
            put(f, self.wait, op=seg(t, T_SWIPE + 0.08, 0.12))
            u = seilzug(seg(t, T_OR, 0.3)); put(f, self.ortwo, dx=lerp(-40, 0, u), op=u)
            rk.dust(f, t, T_SWIPE + 0.1, self.swipe_box)
            return f, 44
        return self.end.frame(t, T_END), 45


# ------------------------------------------------------------------ Ton (Flaeche eine Quarte hoeher als r001/r002)
def sound_events(b):
    """Hook 1 aus dem eigenen Klangset (Grundton G), Puls 108 BPM von Hook 2 bis zur Steigerung, Szenenklaenge wie
    Fassung 3 (Kenney CC0 + selbst erzeugt), beim Bruch Einschlag und Gesteinsknacken, Aufprall aufs Pad."""
    h1 = rk.Hook1(t_grab=T_GRAB, t_geo=T_GEO, t_out=T_OUT)
    b.hook1(h1, root=49.0)
    b.synth("whoosh", T_Q + 0.6, -18.0, "dampf", dur=1.4, seed=3)
    b.synth("whoosh", T_HOOK, -9.0, "lichtstreifen", dur=0.5, seed=4)
    b.klang("thud", T_HOOK + 0.42, -11.0, "absprung", seed=1)
    b.kenney("impact-sounds", "impactMetal_light_000.ogg", T_S2, -7.0, "bohrhaken")
    for k, t0 in enumerate(T_RAIN):
        b.kenney("interface-sounds", ("drop_001.ogg", "drop_004.ogg")[k % 2], t0 + FALL, -6.0 - (k % 3), "tropfen")
    b.synth("fizz", T_DRY, -17.0, "abtrocknen", dur=1.3, seed=5)
    b.kenney("interface-sounds", "maximize_001.ogg", T_Z0, -8.0, "zoom")
    b.kenney("impact-sounds", "impactMetal_light_001.ogg", T_S3, -7.0, "bohrhaken")
    b.klang("chalk_slap", T_PULL - 0.05, -8.0, "griff", seed=2)
    b.kenney("interface-sounds", "scratch_001.ogg", T_PULL, -11.0, "zug")
    b.kenney("impact-sounds", "impactMining_000.ogg", T_CRACK, -5.0, "riss")
    b.klang("crunch", T_SNAP, -4.0, "bruch", seed=3)
    b.klang("sub_hit", T_SNAP - 0.01, -7.0, "bruch-einschlag", f0=85.0, f1=36.0)
    b.kenney("impact-sounds", "impactMining_001.ogg", T_SNAP, -5.0, "bruch")
    b.synth("whoosh", T_SNAP + 0.05, -14.0, "fallen", dur=0.4, seed=9)
    b.klang("thud", T_LAND, -4.0, "aufprall-pad", seed=4)
    for k, t0 in enumerate(T_DRIPS):
        b.synth("drip", t0 + 0.5, -9.0 - k, "tropfen-innen", seed=11 + k)
    b.kenney("interface-sounds", "tick_002.ogg", T_LAB, -8.0, "kreide-tick")
    b.kenney("interface-sounds", "question_002.ogg", T_CALL, -9.0, "frage")
    b.synth("riser", T_RISE, -9.0, "steigerung", dur=0.75)
    b.klang("sub_hit", T_S4 - 0.01, -6.0, "payoff-einschlag", f0=78.0, f1=36.0)
    b.kenney("impact-sounds", "impactPunch_heavy_000.ogg", T_S4, -3.0, "treffer")
    b.kenney("impact-sounds", "impactMetal_light_002.ogg", T_S4 + 0.02, -9.0, "bohrhaken")
    b.kenney("interface-sounds", "maximize_001.ogg", T_S5, -10.0, "zoom")
    b.kenney("impact-sounds", "impactPunch_heavy_001.ogg", T_STAMP + 0.16, -5.0, "stempel")
    b.kenney("interface-sounds", "scratch_001.ogg", T_SWIPE, -5.0, "kreide-wisch")
    b.kenney("interface-sounds", "scratch_002.ogg", T_SWIPE + 0.08, -7.0, "kreide-wisch")
    b.kenney("interface-sounds", "tick_004.ogg", T_OR, -8.0, "kreide-tick")
    big = [T_HOOK, T_S2, T_Z0, T_S3, T_CRACK, T_SNAP, T_LAND]
    b.pulse(T_Q + 0.02, T_RISE - 0.05, bpm=108, gain=-16.0, hat_gain=-25.0, avoid=big)
    b.sound_logo(T_END)
    b.pads([(0.0, T_S4 - 0.15, -9.0), (T_S4, T_END, -11.0)], ratio=1.335)

if __name__ == "__main__":
    rk.run(Reel, sound_events, META)
