#!/usr/bin/env python3
"""Reel 002 -- HOLD ID #01: "Why does this edge stick out?" (Faktenbasis: Post #029, Quarzgang).

Format HOLD ID: Griffform -> Querschnitt -> Entstehung in zwei Zuegen -> Stempel mit Nummer. Ablauf "erklaerkette".
Fassung 4 vom 14.10.2026 (Neu-Post am 14.10., ersetzt den Post vom 13.10.): Markus 13.10.: "hook 1 (klettern und
geologie) und dann hook 2 (eigentliches reel thema)". Hook 1 0-1,3 s: GEOCRIMPS + CLIMBING ab Frame 0, ein Kletterer
greift den Quarzgang (Kreidewolke), "× GEOLOGY" schlaegt ein und die Wand klappt in ihre Geologie auf (Sandstein-
Signatur, Gang und Kluefte). Hook 2 1,5-4,75 s: "WHY DOES THIS EDGE STICK OUT?" (vorher "THIS STRIPE"), der Kletterer
haengt am Gang. Alle folgenden Zeiten 1,5 s spaeter als in Fassung 3. Folge fuers Klettern: der Kletterer klopft den
Gang ab ("Test it"). Ton: Hook-1-Signatur aus dem eigenen Klangset, Puls von Hook 2 bis zur Steigerung.
Dramaturgie (Topo): Hook 1 0-1,3 s | Hook 2 1,5-4,75 s (Schnittlinie ab 3,9 s) | Zug 1 im Querschnitt: Riss, heisses
Wasser, Quarz waechst 4,95-7,85 s | Zug 2: viel spaeter wittert das Gestein zurueck 8,05-10,7 s | Payoff 10,7 s (74 %) |
Stempel 11,85 s | Folge fuers Klettern 12,5 s | Endsignet 13,7-14,5 s.
Bildmittel: Uebergang Schnittlinie und Isolinien-Welle | Enthuellung Querschnitt, Zeitraffer der Verwitterung |
Payoff Antwort gross, Kreide-Wisch, Stempel HOLD ID | Flaeche im Grundton, Braam in A.
Aufruf:  python3 r002_holdid_029.py --out ../../../reels --qc <Ordner>   (--stills 0,0.5 fuer Einzelbilder)
"""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import outcrop as o
import motion as m
import reelkit as rk
import kletter as kl
from outcrop import C, P
from motion import X0, W, H, FPS, seg, seilzug, sturz, griff, lerp, put

# Quarz (milchig, etwas waermer als Magnesia, damit Kreide-Ticks und Gang auseinanderzuhalten sind)
QZ, QZ_EDGE, QZ_SIDE = "#DAD5CA", "#A9A395", "#7D786E"
QZ_PATCH = ["#E4DFD5", "#D1CBBF", "#DEDACF", "#CBC5B9", "#E8E4DB"]

# ------------------------------------------------------------------ Zeitplan
HOOK_EXTRA = 1.0                 # 13.10.2026: Hook-Frage steht 1,0 s laenger
H1 = 1.50                        # 14.10.2026: Hook 1 davor, alles ab Hook 2 1,5 s spaeter
T_GRAB, T_GEO, T_OUT = 0.32, 0.58, 1.22                     # Hook 1: Griff, "× GEOLOGY", Uebergang in die Kopfzeile
T_Q = 1.50                                                  # Hook 2: Formatlabel und Themenfrage fahren ein
T_SEC = 2.40 + H1                                           # Schnittlinie quer zum Gang (im letzten Drittel von Hook 2)
T_W1, T_S2 = 2.25 + HOOK_EXTRA + H1, 2.45 + HOOK_EXTRA + H1  # Welle -> Querschnitt (Zug 1)
T_CRACK, T_OPEN = 2.70 + HOOK_EXTRA + H1, 2.95 + HOOK_EXTRA + H1
T_FLOW = (3.00 + HOOK_EXTRA + H1, 4.45 + HOOK_EXTRA + H1)
T_GROW0, T_GROW1 = 3.45 + HOOK_EXTRA + H1, 4.75 + HOOK_EXTRA + H1
T_LAB = 4.85 + HOOK_EXTRA + H1
T_W2, T_S3 = 5.35 + HOOK_EXTRA + H1, 5.55 + HOOK_EXTRA + H1
T_E0, T_E1 = 5.80 + HOOK_EXTRA + H1, 7.95 + HOOK_EXTRA + H1
T_EDGE = 7.55 + HOOK_EXTRA + H1
T_RISE = 7.25 + HOOK_EXTRA + H1
T_S4 = 8.20 + HOOK_EXTRA + H1                               # Payoff
T_SWIPE = 8.75 + HOOK_EXTRA + H1
T_STAMP = 9.35 + HOOK_EXTRA + H1
T_SAFE = 10.00 + HOOK_EXTRA + H1
T_KNOCK = (T_SAFE + 0.25, T_SAFE + 0.55)                    # Kletterer klopft den Gang ab
T_END = 11.20 + HOOK_EXTRA + H1
DUR = T_END + 0.8

META = dict(
    slug="2026-10-13_holdid-01", dur_range=[10.5, 14.5], payoff_t=T_S4,
    title="GeoCrimps r002 HOLD ID #01 (Erklaerkette), Fassung 4", ablauf="erklaerkette",
    hook1_bis=T_OUT, hook_ab=T_Q, hook_bis=T_W1, weitere_fragen=[], cover_t=T_Q + 0.85,
    on_screen=["HOLD ID", "WHY DOES THIS EDGE STICK OUT?", "HOT WATER SEALS A CRACK WITH QUARTZ.",
               "MUCH LATER, THE ROCK AROUND IT WEARS AWAY.", "QUARTZ LASTS LONGER.",
               "HOLD ID #01", "QUARTZ VEIN", "Test it: veins can flake off."],
    labels=["QUARTZ", "EDGE"],
    qc_times=[0.0, 0.36, 0.75, 1.15, 1.45, 2.35, 4.2, 5.1, 5.6, 6.6, 7.6, 9.0, 10.5, 10.9, 12.0, 12.85],
    marks=[(0, "Hook 1"), (T_GRAB, "Griff"), (T_GEO, "x GEOLOGY"), (T_Q, "Hook 2"), (T_SEC, "Schnitt"), (T_W1, "Welle"),
           (T_S2, "Zug 1"), (T_W2, "Welle"), (T_S3, "Zug 2"), (T_RISE, "Steigerung"), (T_S4, "PAYOFF"),
           (T_STAMP, "Stempel"), (T_SAFE, "Folge"), (T_END, "Klanglogo")])

RAIL_N = 2
RAIL_Y = [1300 - (1300 - 330 - 60) / RAIL_N * (i + 0.5) for i in range(RAIL_N)]

# Gang in der Wandansicht (Mittellinie, halbe Dicke) und im Querschnitt
VEIN_P0, VEIN_P1, VEIN_HALF = (110, 1520), (1090, 1150), 25
Y_V, HALF_S = 1180, 34           # Querschnitt: Ganglage und halbe Dicke
SEC_TOP = 880                    # Querschnitt: Oberkante (weich ausgeblendet bis +80)
WALL_TOP = 930


def vein_top(x):
    """Oberkante (Leiste) des Quarzgangs in der Wandansicht."""
    return VEIN_P0[1] + (VEIN_P1[1] - VEIN_P0[1]) * (x - VEIN_P0[0]) / (VEIN_P1[0] - VEIN_P0[0]) - VEIN_HALF


def jit(x):
    """Feste, glatte Unruhe der Rissflanken im Querschnitt."""
    return 4.0 * math.sin(x / 47 + 0.7) + 3.0 * math.sin(x / 19 + 2.1) + 1.4 * math.sin(x / 7.3)

def face_noise(y, u=0.0):
    """Unruhe der zurueckwitternden Wandflaeche (Querschnitt)."""
    return 9 * math.sin(y / 53 + 1.3) + 6 * math.sin(y / 21 + 0.4) + 3 * math.sin(y / 9.7) + 2.5 * math.sin(y / 15 + 9 * u)


# ------------------------------------------------------------------ Bausteine (2x, absolute Koordinaten)
def specks_layer(size, seed, per=950):
    """Neutrales Gesteinskorn: kleine Punkte und Striche in zwei Toenen (keine Lithologie-Signatur)."""
    L = Image.new("RGBA", size, (0, 0, 0, 0)); d = ImageDraw.Draw(L); rnd = random.Random(seed)
    w, h = size; s = o.S
    cols = [o.rgb(C["line"]), o.rgb("#353E46"), o.rgb(C["slate"], 60)]
    for _ in range(int(w * h / (per * s * s))):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h); col = rnd.choice(cols)
        if rnd.random() < 0.3:
            a = rnd.uniform(0, math.pi); ln = rnd.uniform(4, 9) * s
            d.line([(x, y), (x + math.cos(a) * ln, y + math.sin(a) * ln)], fill=col, width=int(2 * s))
        else:
            r = rnd.uniform(1.4, 3.2) * s
            d.ellipse([x - r, y - r, x + r, y + r], fill=col)
    return L

def rock_fill(im, poly, seed, fade=None):
    """Graphit + Korn in einem Polygon; fade=(y0, y1) blendet die Oberkante weich aus."""
    mask = Image.new("L", im.size, 0); ImageDraw.Draw(mask).polygon([P(x, y) for x, y in poly], fill=255)
    if fade:
        a = np.asarray(mask, np.float32)
        yy = np.arange(a.shape[0], dtype=np.float32)[:, None] / o.S
        a *= np.clip((yy - fade[0]) / (fade[1] - fade[0]), 0, 1)
        mask = Image.fromarray(a.astype(np.uint8))
    layer = Image.new("RGBA", im.size, o.rgb(C["graphite"])); layer.putalpha(mask); im.alpha_composite(layer)
    sp = specks_layer(im.size, seed)
    sa = np.asarray(sp.getchannel("A"), np.float32) * (np.asarray(mask, np.float32) / 255)
    sp.putalpha(Image.fromarray(sa.astype(np.uint8))); im.alpha_composite(sp)
    return mask

def vein_geom(p0, p1, half, seed, n=140):
    rnd = random.Random(seed)
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]; L = math.hypot(dx, dy); nx, ny = -dy / L, dx / L
    ph1, ph2 = rnd.uniform(0, 6), rnd.uniform(0, 6)
    up, lo, mid = [], [], []
    for i in range(n + 1):
        s = i / n; cx, cy = p0[0] + dx * s, p0[1] + dy * s
        eu = half + 3.0 * math.sin(i * 0.27 + ph1) + 1.6 * math.sin(i * 0.83) + rnd.uniform(-0.6, 0.6)
        el = half + 3.0 * math.sin(i * 0.23 + ph2) + 1.6 * math.sin(i * 0.71 + 1) + rnd.uniform(-0.6, 0.6)
        mo = 1.4 * math.sin(i * 0.9 + ph1)
        up.append((cx - nx * eu, cy - ny * eu)); lo.append((cx + nx * el, cy + ny * el)); mid.append((cx + nx * mo, cy + ny * mo))
    return up, lo, mid

def vein_front(im, wall_mask, seed=5):
    """Quarzgang in der Wandansicht: steht vor (Seitenflaeche und Schlagschatten unten, Lichtkante oben),
    milchig mit Kristallflecken und feinen Querrissen."""
    up, lo, _ = vein_geom(VEIN_P0, VEIN_P1, VEIN_HALF, seed)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon([P(*p) for p in lo + [(x + 9, y + 28) for x, y in lo][::-1]], fill=o.rgb(C["obsidian"], 230))
    sh = sh.filter(ImageFilter.GaussianBlur(5 * o.S))
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); lay.alpha_composite(sh)
    ImageDraw.Draw(lay).polygon([P(*p) for p in lo + [(x + 3, y + 11) for x, y in lo][::-1]], fill=o.rgb(QZ_SIDE))
    vm = Image.new("L", im.size, 0); ImageDraw.Draw(vm).polygon([P(*p) for p in up + lo[::-1]], fill=255)
    top = Image.new("RGBA", im.size, o.rgb(QZ)); dt = ImageDraw.Draw(top); rnd = random.Random(seed + 1)
    for _ in range(300):                                        # milchige Kristallflecken
        i = rnd.randrange(len(up)); f = rnd.uniform(0.08, 0.92)
        cx = up[i][0] + (lo[i][0] - up[i][0]) * f; cy = up[i][1] + (lo[i][1] - up[i][1]) * f
        r = rnd.uniform(5, 12); k = rnd.randint(4, 6); a0 = rnd.uniform(0, 6.28)
        dt.polygon([P(cx + r * rnd.uniform(0.6, 1.0) * math.cos(a0 + 2 * math.pi * j / k),
                      cy + r * rnd.uniform(0.6, 1.0) * math.sin(a0 + 2 * math.pi * j / k)) for j in range(k)],
                   fill=o.rgb(rnd.choice(QZ_PATCH)))
    for _ in range(9):                                          # feine Querrisse im Gang
        i = rnd.randrange(4, len(up) - 4); j = i + rnd.randint(-2, 2)
        dt.line([P(*up[i]), P(*lo[j])], fill=o.rgb(QZ_EDGE), width=int(1.2 * o.S))
    top.putalpha(vm); lay.alpha_composite(top)
    d = ImageDraw.Draw(lay)
    d.line([P(*p) for p in lo], fill=o.rgb(QZ_EDGE), width=int(2 * o.S))
    d.line([P(*p) for p in up], fill=o.rgb(C["magnesia"]), width=int(3 * o.S))
    lay.putalpha(ImageChops.multiply(lay.getchannel("A"), wall_mask)); im.alpha_composite(lay)

JOINTS = ([(260, 1060), (300, 1190), (282, 1330)], [(905, WALL_TOP + 40), (880, 1060), (930, 1150)])   # Kluefte

def wall_poly(seed=3):
    return o.ragged(110, WALL_TOP, 1090, 1960, seed=seed, amp=16, n=18, top_only=True)

def wall_front(im, seed=3, ticks=True):
    poly = wall_poly(seed)
    mask = rock_fill(im, poly, seed)
    d = ImageDraw.Draw(im)
    for pts in JOINTS:
        d.line([P(x, y) for x, y in pts], fill=o.rgb(C["obsidian"], 210), width=int(3 * o.S), joint="curve")
    vein_front(im, mask)
    d.line([P(x, y) for x, y in poly[:19]], fill=o.rgb(C["magnesia"]), width=int(4 * o.S), joint="curve")
    if ticks:
        o.chalk_ticks(im, 596, 1266, angle_deg=-38, seed=2)
    return poly

def section_rock(im, seed=6):
    rock_fill(im, [(110, SEC_TOP), (1200, SEC_TOP), (1200, 1960), (110, 1960)], seed, fade=(SEC_TOP, SEC_TOP + 80))

def heat_tint(im, alpha=78):
    yy, xx = np.mgrid[0:im.size[1], 0:im.size[0]].astype(np.float32) / o.S
    dd = np.sqrt((xx - 600) ** 2 + ((yy - 1980) * 1.15) ** 2)
    a = alpha * np.clip(1 - dd / 1150, 0, 1) ** 1.5
    lay = Image.new("RGBA", im.size, o.rgb(C["heat"])); lay.putalpha(Image.fromarray(a.astype(np.uint8)))
    im.alpha_composite(lay)

def band_edges(x):
    c = Y_V + jit(x)
    return c - HALF_S, c + HALF_S

def section_band(im):
    """Fertiger Gang im Querschnitt: Quarzkristalle von beiden Waenden, in der Mitte verzahnt (wie im Wachstum)."""
    xs = list(range(110, 1204, 4))
    up = [(x, band_edges(x)[0]) for x in xs]; lo = [(x, band_edges(x)[1]) for x in xs]
    d = ImageDraw.Draw(im)
    d.polygon([P(*p) for p in up + lo[::-1]], fill=o.rgb(QZ))
    for c in CRYSTALS:
        d.polygon([P(*q) for q in crystal_poly(c, 2 * HALF_S, HALF_S + 2.5)], fill=o.rgb(QZ), outline=o.rgb(QZ_EDGE), width=2)
    for pts in (up, lo):
        d.line([P(*p) for p in pts], fill=o.rgb(QZ_EDGE), width=int(2 * o.S))

def crack_line(im):
    d = ImageDraw.Draw(im)
    d.line([P(x, Y_V + jit(x)) for x in range(110, 1094, 4)], fill=o.rgb(C["magnesia"]), width=int(3 * o.S), joint="curve")

def bolt_sprite(i):
    y = RAIL_Y[i]; s = 10
    def d(im):
        dr = ImageDraw.Draw(im); col = o.rgb(C["magnesia"])
        dr.line([P(56 - s, y - s), P(56 + s, y + s)], fill=col, width=int(4 * o.S))
        dr.line([P(56 - s, y + s), P(56 + s, y - s)], fill=col, width=int(4 * o.S))
    return m.sprite(d)

def region(x0, y0, x1, y1, draw):
    """Kleine 2x-Flaeche fuer bewegte Details: draw(d, X, Y) mit X/Y = Umrechnung in Flaechen-Pixel."""
    w, h = int(x1 - x0), int(y1 - y0)
    im = Image.new("RGBA", (w * o.S, h * o.S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    X = lambda x: (x - x0) * o.S
    Y = lambda y: (y - y0) * o.S
    draw(d, X, Y)
    return m.Sprite(im.resize((w, h), Image.LANCZOS), int(x0), int(y0))

def mask_from(poly):
    mk = Image.new("L", (W * o.S, H * o.S), 0); ImageDraw.Draw(mk).polygon([P(x, y) for x, y in poly], fill=255)
    return mk.resize((W, H), Image.BOX)


# ------------------------------------------------------------------ Kristalle und Wasser (Zug 1)
def make_crystals(seed, upper):
    rnd = random.Random(seed); out = []; x = 112.0
    while x < 1092:
        out.append(dict(x=x, w=rnd.uniform(12, 20), tilt=math.radians(rnd.uniform(-12, 12)),
                        delay=rnd.uniform(0, 0.3), speed=rnd.uniform(0.8, 1.2), upper=upper))
        x += rnd.uniform(13, 21)
    return out

def crystal_poly(c, a, L):
    yb = band_edges(c["x"])[0] + (HALF_S - a / 2) if c["upper"] else band_edges(c["x"])[1] - (HALF_S - a / 2)
    sgn = 1 if c["upper"] else -1
    dx, dy = math.sin(c["tilt"]), sgn * math.cos(c["tilt"])
    x, w = c["x"], c["w"]
    b0, b1 = (x - w / 2, yb - sgn * 2), (x + w / 2, yb - sgn * 2)
    s0 = (x - w / 2 + dx * 0.7 * L, yb + dy * 0.7 * L); s1 = (x + w / 2 + dx * 0.7 * L, yb + dy * 0.7 * L)
    tip = (x + dx * L, yb + dy * L)
    return [b0, b1, s1, tip, s0]


CRYSTALS = make_crystals(21, True) + make_crystals(22, False)


# ------------------------------------------------------------------ Kletterer (Rueckenansicht an der Wand)
BACK = dict(sw=22, hw=13, eb=(-1, 1), kb=(1, -1))
GRIP_L, GRIP_R = (770, vein_top(770) + 9), (895, vein_top(895) + 9)
POSE_HANG = dict(BACK, hip=(838, 1430), lean=8, lh=GRIP_L, rh=GRIP_R, lf=(772, 1562), rf=(906, 1546))
POSE_REACH = dict(BACK, hip=(826, 1452), lean=-3, lh=GRIP_L, rh=(936, 1318), lf=(772, 1562), rf=(906, 1546))
POSE_PULL = dict(POSE_HANG, hip=(842, 1414), lean=9)          # Schwung am Ende des Zugs


def climber_pose(t):
    """Hook 1: Zug zum Gang (Frame 0 schon in Bewegung), Griff bei T_GRAB, kurzes Nachfedern; danach leichtes Pendeln."""
    if t < T_GRAB:
        return kl.lerp_pose(POSE_REACH, POSE_PULL, seilzug(seg(t, 0.0, T_GRAB)))
    u = seg(t, T_GRAB, 0.28)
    p = kl.lerp_pose(POSE_PULL, POSE_HANG, 0.5 - 0.5 * math.cos(math.pi * u))
    if u >= 1:
        w = math.sin(2 * math.pi * (t - T_GRAB - 0.28) / 2.6)
        p = dict(p, hip=(p["hip"][0] + 5 * w, p["hip"][1] + 1.5 * abs(w)), lean=p["lean"] + 2.0 * w)
    return p


def climber_pose_end(t):
    """Folge fuers Klettern: am Gang haengen, bei "Test it" zweimal mit der rechten Hand auf die Leiste klopfen."""
    p = dict(POSE_HANG)
    for tk in T_KNOCK:
        v = seg(t, tk - 0.14, 0.28)
        if 0 < v < 1:
            lift = math.sin(math.pi * v)
            p = dict(p, rh=(GRIP_R[0] + 10 * lift, GRIP_R[1] - 34 * lift), hip=(p["hip"][0] - 4 * lift, p["hip"][1] + 4 * lift))
    return p


class Reel(rk.ReelBase):
    DUR = DUR

    def __init__(self):
        super().__init__()
        self.hook1 = rk.Hook1(t_grab=T_GRAB, t_geo=T_GEO, t_out=T_OUT)
        self.stamp_top = m.text_sprite("HOLD ID", X0, rk.FORMAT_Y, "stencil", 40, C["slate"], tracking=0.12)
        self.climber = kl.Climber(scale=1.0, width=18.0, torso_w=36.0)
        # Szene 1: Hook 1 + Hook 2 an der Wand
        def bg1(im):
            o.contour_field(im, 760, 1520, n=10, r0=120, step=60, alpha=110)
            wall_front(im)
            o.route_rail(im, 0, RAIL_N)
        self.bg1 = m.background(bg1)
        up, lo, _ = vein_geom(VEIN_P0, VEIN_P1, VEIN_HALF, 5)
        # Geologie der Wand (Hook 1): Sandstein (Signatur Punkte, wie im Foto von Post #029), flach liegende Schichten,
        # Kluefte; der Gang durchschlaegt die Schichten (keine Signatur im Gang, Gangraender hell)
        beds = [[(x, y0 - 0.05 * (x - 110) + 5 * math.sin(x / 95 + k)) for x in range(100, 1101, 20)]
                for k, y0 in enumerate(range(1010, 1960, 88))]
        self.geo = kl.GeoReveal(wall_poly(), "sandstone", GRIP_R[0], GRIP_R[1], pat_alpha=95,
                                beds=beds + [list(j) for j in JOINTS], contacts=[up, lo], holes=[up + lo[::-1]], seed=8)
        self.hook, _ = m.lines_sprite(["WHY DOES", "THIS EDGE", "STICK OUT?"], rk.HOOK_Y, size=164)
        c = (640, 1520 + (1150 - 1520) * (640 - 110) / 980); n = (0.353, 0.936)
        a = (c[0] - n[0] * 175, c[1] - n[1] * 175); b = (c[0] + n[0] * 175, c[1] + n[1] * 175)
        def secline(im):
            d = ImageDraw.Draw(im); L = math.hypot(b[0] - a[0], b[1] - a[1]); k = 0.0
            while k < L:
                k1 = min(L, k + 18)
                d.line([P(a[0] + (b[0] - a[0]) * k / L, a[1] + (b[1] - a[1]) * k / L),
                        P(a[0] + (b[0] - a[0]) * k1 / L, a[1] + (b[1] - a[1]) * k1 / L)], fill=o.rgb(C["magnesia"]), width=int(4 * o.S))
                k += 30
            for p in (a, b):        # Endmarken der Schnittlinie
                d.line([P(p[0] - 0.936 * 16, p[1] + 0.353 * 16), P(p[0] + 0.936 * 16, p[1] - 0.353 * 16)],
                       fill=o.rgb(C["magnesia"]), width=int(5 * o.S))
        self.secline = m.sprite(secline)
        self.sec_c = c
        # Szene 2: Querschnitt, Zug 1 (heiss, tief)
        def bg2(im):
            section_rock(im); heat_tint(im); o.route_rail(im, 1, RAIL_N)
        self.bg2 = m.background(bg2)
        self.text2, _ = m.lines_sprite(["HOT WATER SEALS", "A CRACK", "WITH QUARTZ."], 352, role="display_xb", size=118)
        self.crack = m.sprite(crack_line)
        self.band = m.sprite(section_band)
        self.cry = CRYSTALS
        rnd = random.Random(5)
        self.parts = [dict(t0=rnd.uniform(T_FLOW[0], T_FLOW[1] - 0.5), v=rnd.uniform(520, 820), off=rnd.uniform(-0.62, 0.62),
                           r=rnd.uniform(4.0, 7.0), ph=rnd.uniform(0, 6), hot=rnd.random() < 0.6) for _ in range(95)]
        self.lab = m.text_sprite("QUARTZ", 520, 1242, "mono", 30, C["magnesia"], tracking=0.1)
        self.lab_edge = m.text_sprite("EDGE", 812, 1098, "mono", 30, C["magnesia"], tracking=0.1)
        # Szene 3: viel spaeter, Gestein wittert zurueck (kuehl)
        self.rock3 = m.background(lambda im: section_rock(im))
        self.air3 = m.background(lambda im: o.route_rail(im, RAIL_N, RAIL_N))
        band_full = Image.new("RGBA", (W, H), (0, 0, 0, 0)); band_full.alpha_composite(self.band.img, (self.band.x, self.band.y))
        self.band_full = band_full
        self.text3, _ = m.lines_sprite(["MUCH LATER,", "THE ROCK AROUND", "IT WEARS AWAY."], 352, role="display_xb", size=118)
        rnd = random.Random(9); self.grains = []
        for _ in range(110):
            te = rnd.uniform(T_E0 + 0.1, T_E1 - 0.05); y0 = rnd.uniform(965, 1760)
            if abs(y0 - Y_V) < HALF_S + 10:
                continue
            self.grains.append(dict(t0=te, y0=y0, vx=rnd.uniform(40, 190), vy=rnd.uniform(-60, 20), r=rnd.uniform(1.8, 4.2),
                                    col=rnd.choice([C["slate"], "#4A545D", C["line"], "#5B656E"]), q=False))
        for k in range(4):                                       # Quarz verwittert auch, nur viel langsamer
            self.grains.append(dict(t0=T_E0 + 0.5 + 0.45 * k, y0=Y_V + rnd.uniform(-14, 14), vx=rnd.uniform(60, 120), vy=-20,
                                    r=rnd.uniform(1.6, 2.6), col=QZ, q=True))
        # Szene 4: Payoff + Stempel + Folge fuers Klettern
        def bg4(im):
            o.contour_field(im, 760, 1520, n=10, r0=120, step=60, alpha=110)
            wall_front(im)
            o.route_rail(im, RAIL_N, RAIL_N, logo_on=True)
        self.bg4 = m.background(bg4)
        self.quartz, yq = m.lines_sprite(["QUARTZ"], 330, size=260)
        sz2 = m.fit("LASTS LONGER.", "display", 132)
        sw = o.text_width("LASTS LONGER.", "display", sz2)
        y5 = yq + 26
        self.swipe = m.sprite(lambda im: o.chalk_swipe(im, X0 - 8, y5 + 16, X0 + sw + 14, y5 + 16 + sz2, seed=9))
        self.longer = m.text_sprite("LASTS LONGER.", X0, y5 + 8, "display", sz2, C["obsidian"])
        self.swipe_box = (X0 - 8, y5 + 16, X0 + sw + 14, y5 + 16 + sz2)
        self.safe = m.text_sprite("Test it: veins can flake off.", X0, y5 + sz2 + 62, "text_b", 50, C["magnesia"])
        self.stamp = self.make_stamp(716, 1072, -6)
        self.end = rk.EndSting()
        self.bolts = [bolt_sprite(i) for i in range(RAIL_N)]
        self.top_logo = m.sprite(lambda im: o.logo_mark(im, o.RAIL_X, 330, 0.26, C["magnesia"], width=7))
        def glow(im):                                              # Gang leuchtet im Payoff kurz auf
            lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
            d.line([P(*p) for p in up + lo[::-1] + [up[0]]], fill=o.rgb(C["magnesia"]), width=int(6 * o.S), joint="curve")
            wm = Image.new("L", im.size, 0)
            ImageDraw.Draw(wm).polygon([P(x, y) for x, y in wall_poly()], fill=255)
            lay.putalpha(ImageChops.multiply(lay.getchannel("A"), wm)); im.alpha_composite(lay)
        self.glow = m.sprite(glow)

    # -------------------------------------------------------------- Stempel "HOLD ID #01 / QUARTZ VEIN"
    def make_stamp(self, cx, cy, angle):
        s = o.S; f1 = o.font("stencil", 58); f2 = o.font("mono", 27)
        t1, t2 = "HOLD ID #01", "QUARTZ VEIN"
        w1 = f1.getlength(t1); w2 = f2.getlength(t2) + 0.14 * 27 * s * (len(t2) - 1)
        bw = int(max(w1, w2) + 2 * 30 * s); bh = int((58 + 27 + 18 + 2 * 22) * s)
        im = Image.new("RGBA", (bw + 40 * s, bh + 40 * s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        ox, oy = 20 * s, 20 * s; col = o.rgb(C["magnesia"])
        d.rounded_rectangle([ox, oy, ox + bw, oy + bh], radius=14 * s, outline=col, width=5 * s)
        d.rounded_rectangle([ox + 10 * s, oy + 10 * s, ox + bw - 10 * s, oy + bh - 10 * s], radius=9 * s, outline=o.rgb(C["magnesia"], 150), width=2 * s)
        d.text((ox + bw / 2, oy + 24 * s), t1, font=f1, fill=col, anchor="mt")
        x = ox + bw / 2 - w2 / 2; y = oy + (24 + 58 + 14) * s
        for ch in t2:
            d.text((x, y), ch, font=f2, fill=col, anchor="lt"); x += f2.getlength(ch) + 0.14 * 27 * s
        rng = np.random.default_rng(4)              # Stempelfarbe: unregelmaessig aufgetragen
        a = np.asarray(im.getchannel("A"), np.float32)
        noise = np.asarray(Image.fromarray((rng.random(a.shape) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.6 * s)), np.float32) / 255
        a *= np.clip(1.35 - noise * 1.1, 0.25, 1.0)
        im.putalpha(Image.fromarray(a.astype(np.uint8)))
        im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
        small = im.resize((im.width // s, im.height // s), Image.LANCZOS)
        return m.Sprite(small, int(cx - small.width / 2), int(cy - small.height / 2))

    # -------------------------------------------------------------- Uebergaenge (2x gezeichnet)
    def wave(self, u, cx=540, cy=1100):
        rnd = random.Random(4)
        harm = [(k, rnd.uniform(0.02, 0.06), rnd.uniform(0, 6.28)) for k in (2, 3, 5)]
        def d(im):
            dr = ImageDraw.Draw(im)
            for i in range(7):
                r = u * 1750 - i * 95
                if r <= 4:
                    continue
                a = int(210 * (1 - u) * (1 - i / 8))
                pts = []
                for j in range(121):
                    th = 2 * math.pi * j / 120
                    rr = r * (1 + sum(am * math.cos(k * th + ph + i * 0.13) for k, am, ph in harm))
                    pts.append(P(cx + rr * math.cos(th), cy + rr * 0.8 * math.sin(th)))
                dr.line(pts, fill=o.rgb(C["magnesia"], a), width=int(3 * o.S))
        return m.sprite(d)

    def bolt_pop(self, f, t, i, t0):
        u = seg(t, t0, 0.3)
        if 0 < u < 1:
            put(f, self.bolts[i], scale=lerp(1.9, 1.0, griff(u)))

    # -------------------------------------------------------------- Zug 1: Riss -> Wasser -> Quarz
    def crack_region(self, t):
        a = 3 + (2 * HALF_S - 3) * seilzug(seg(t, T_OPEN, 0.4))
        fl = [p for p in self.parts if p["t0"] <= t]
        def draw(d, X, Y):
            xs = list(range(110, 1094, 6))
            upw = [(x, Y_V + jit(x) - a / 2) for x in xs]; low = [(x, Y_V + jit(x) + a / 2) for x in xs]
            d.polygon([(X(x), Y(y)) for x, y in upw + low[::-1]], fill=o.rgb(C["obsidian"]))
            for p in fl:                                         # heisses Wasser mit geloester Kieselsaeure
                x = 110 + (t - p["t0"]) * p["v"]
                if x > 1092:
                    continue
                gfrac = seilzug(seg(t, T_GROW0, T_GROW1 - T_GROW0))
                room = max(0.0, a / 2 - p["r"] - 2) * (1 - 0.85 * gfrac)
                y = Y_V + jit(x) + p["off"] * room + 1.5 * math.sin(x / 23 + p["ph"])
                al = int(235 * min(1, (t - p["t0"]) * 6) * (1 - seg(t, T_GROW1 - 0.45, 0.4)))
                if al <= 0:
                    continue
                col = o.rgb(C["heat"] if p["hot"] else "#FFB27A", al); r = p["r"] * o.S
                d.ellipse([X(x) - r, Y(y) - r, X(x) + r, Y(y) + r], fill=col)
            for c in self.cry:                                   # Quarz waechst von beiden Waenden nach innen
                u = seilzug(clamp01((t - T_GROW0 - c["delay"]) * c["speed"] / 1.0))
                if t >= T_GROW1:
                    u = 1.0
                L = (a / 2 + 2.5) * u
                if L < 2:
                    continue
                d.polygon([(X(x), Y(y)) for x, y in crystal_poly(c, a, L)], fill=o.rgb(QZ), outline=o.rgb(QZ_EDGE), width=2)
            for pts in (upw, low):
                d.line([(X(x), Y(y)) for x, y in pts], fill=o.rgb(C["magnesia"], 210), width=int(2 * o.S))
        return region(100, Y_V - 70, 1094, Y_V + 70, draw)

    # -------------------------------------------------------------- Zug 2: Wand wittert zurueck
    def erosion(self, f, t):
        u = seilzug(seg(t, T_E0, T_E1 - T_E0)) if t < T_E1 else 1.0
        u = 0.5 - 0.5 * math.cos(math.pi * u)                    # weich an beiden Enden
        F = lerp(1125, 720, u); V = lerp(1125, 868, u)
        ys = list(range(SEC_TOP, 1964, 8))
        face = [(F + face_noise(y, u), y) for y in ys]
        mk = mask_from([(110, SEC_TOP)] + face + [(110, 1964)])
        f.paste(self.rock3, (0, 0), mk)
        cap = [(V - 7, band_edges(V)[0] + 3), (V + 1, Y_V + jit(V) - 6), (V - 2, Y_V + jit(V) + 7), (V - 9, band_edges(V)[1] - 2)]
        mv = mask_from([(0, Y_V - 80)] + [(x, band_edges(x)[0] - 6) for x in range(110, int(V - 7), 8)] + cap +
                       [(x, band_edges(x)[1] + 6) for x in range(int(V - 9), 110, -8)] + [(0, Y_V + 80)])
        b = self.band_full.copy(); b.putalpha(ImageChops.multiply(b.getchannel("A"), mv)); f.alpha_composite(b)
        if F < 1090:                                              # Oberflaechenprofil: Wand + vorstehender Gang
            yb0, yb1 = band_edges(F)
            prof_a = [(x, y) for x, y in face if 955 <= y <= yb0]
            prof_b = [(x, band_edges(x)[0]) for x in np.arange(F + face_noise(yb0, u), V - 7, 4)] + cap + \
                     [(x, band_edges(x)[1]) for x in np.arange(V - 9, F + face_noise(yb1, u), -4)]
            prof_c = [(x, y) for x, y in face if y >= yb1]
            x0 = min(F, V) - 40; x1 = min(1080, max(F, V) + 40)
            prof = prof_a + prof_b + prof_c
            def draw(d, X, Y):
                d.line([(X(x), Y(y)) for x, y in prof], fill=o.rgb(C["magnesia"]), width=int(4 * o.S), joint="curve")
                for k in range(8):                                # Kante blendet nach oben weich aus
                    y = 955 - k * 6
                    d.line([(X(F + face_noise(y, u)), Y(y)), (X(F + face_noise(y - 6, u)), Y(y - 6))],
                           fill=o.rgb(C["magnesia"], int(255 * (1 - k / 8))), width=int(4 * o.S))
            put(f, region(max(110, x0), 900, x1, 1920, draw))
        dr = ImageDraw.Draw(f)                                   # abbroeckelnde Koerner
        for g in self.grains:
            tau = t - g["t0"]
            if tau < 0 or tau > 0.75:
                continue
            ue = 0.5 - 0.5 * math.cos(math.pi * seilzug(seg(g["t0"], T_E0, T_E1 - T_E0)))
            x0g = (lerp(1125, 868, ue) - 3) if g["q"] else lerp(1125, 720, ue) + face_noise(g["y0"], ue)
            if x0g > 1075:
                continue
            x = x0g + g["vx"] * tau; y = g["y0"] + g["vy"] * tau + 0.5 * 1700 * tau * tau
            al = int(230 * (1 - tau / 0.75)); r = g["r"]
            dr.ellipse([x - r, y - r, x + r, y + r], fill=o.rgb(g["col"], al))
        return F, V

    # -------------------------------------------------------------- Frames
    def scene1_world(self, t):
        """Wand mit Kletterer, Kreidewolke und (Hook 1) aufgeklappter Geologie, vor dem leichten Push-in."""
        f = self.bg1.copy()
        u = seilzug(seg(t, T_GEO, 0.5))
        if u > 0 and t < T_OUT + 0.4:
            self.geo.put(f, u, fade=1 - seg(t, T_OUT, 0.4))
        put(f, self.climber.sprite(climber_pose(t)))
        kl.chalk_puff(f, t, T_GRAB, GRIP_R[0], GRIP_R[1] - 4, seed=11)
        return f

    def frame(self, t):
        if t < T_S2:                                               # Szene 1: Hook 1 + Hook 2 an der Wand
            f = m.zoomed(self.scene1_world(t), 1 + 0.035 * seilzug(seg(t, 0, T_W1)), self.sec_c[0], self.sec_c[1])
            self.hook1.draw(f, t, hook_bis=T_W1)
            u = seilzug(seg(t, T_Q, 0.35))
            if u > 0:
                fade = 1 - seg(t, T_W1, 0.12)
                put(f, self.stamp_top, dx=lerp(-30, 0, u), op=u * fade)
                put(f, self.hook, dx=lerp(-40, 0, u), op=u * fade)
            u = seilzug(seg(t, T_SEC, 0.42))
            if u > 0:
                put(f, m.reveal(self.secline, u))
            if t >= T_W1:
                put(f, self.wave(seg(t, T_W1, 0.5), cx=self.sec_c[0], cy=self.sec_c[1]))
            return f, 21
        if t < T_S3:                                               # Szene 2: Querschnitt, Zug 1
            f = self.bg2.copy()
            shimmer(f, t)
            u = seilzug(seg(t, T_S2 + 0.03, 0.35)); put(f, self.text2, dx=lerp(-40, 0, u), op=u)
            if t < T_OPEN:
                put(f, m.reveal(self.crack, sturz(seg(t, T_CRACK, 0.25))))
            else:
                bo = seg(t, T_GROW1 + 0.05, 0.3)
                if bo < 1:
                    put(f, self.crack_region(t))
                put(f, self.band, op=bo)
            u = seg(t, T_LAB, 0.3)
            put(f, self.lab, op=min(1, u * 1.8), scale=lerp(0.7, 1.0, griff(u)) if u < 1 else 1.0)
            self.bolt_pop(f, t, 0, T_S2)
            if t < T_W1 + 0.5:
                put(f, self.wave(seg(t, T_W1, 0.5), cx=self.sec_c[0], cy=self.sec_c[1]))
            if t >= T_W2:
                put(f, self.wave(seg(t, T_W2, 0.45), cy=500))
            return f, 22
        if t < T_S4:                                               # Szene 3: viel spaeter, Zug 2
            f = self.air3.copy()
            self.erosion(f, t)
            u = seilzug(seg(t, T_S3 + 0.03, 0.35)); put(f, self.text3, dx=lerp(-40, 0, u), op=u)
            u = seg(t, T_EDGE, 0.3)
            put(f, self.lab_edge, op=min(1, u * 1.8), scale=lerp(0.7, 1.0, griff(u)) if u < 1 else 1.0)
            self.bolt_pop(f, t, 1, T_S3)
            if t < T_W2 + 0.45:
                put(f, self.wave(seg(t, T_W2, 0.45), cy=500))
            return f, 23
        if t < T_END:                                              # Szene 4: Payoff, Stempel, Folge
            f = self.bg4.copy()
            v = seg(t, T_S4 + 0.05, 0.9)
            if 0 < v < 1:
                put(f, self.glow, op=math.sin(math.pi * v) ** 0.7)
            put(f, self.climber.sprite(climber_pose_end(t)), op=seilzug(seg(t, T_S4, 0.25)))
            for k, tk in enumerate(T_KNOCK):
                kl.chalk_puff(f, t, tk, GRIP_R[0], GRIP_R[1] - 4, seed=31 + k, size=0.6)
            u = seg(t, T_S4, 0.3)
            if 0 < u < 1:
                put(f, self.top_logo, scale=lerp(1.9, 1.0, griff(u)))
            u = seg(t, T_S4, 0.22)
            put(f, self.quartz, op=min(1, u * 2), scale=lerp(1.18, 1.0, seilzug(u)), anchor=(X0, 330))
            put(f, m.reveal(self.swipe, seilzug(seg(t, T_SWIPE, 0.2))))
            put(f, self.longer, op=seg(t, T_SWIPE + 0.08, 0.12))
            u = seg(t, T_STAMP, 0.24)
            if u > 0:
                sh = (1 - seg(t, T_STAMP + 0.2, 0.12)) * 3 if t >= T_STAMP + 0.2 else 0
                put(f, self.stamp, dx=sh * math.sin(t * 90), op=min(1, u * 3), scale=lerp(1.65, 1.0, griff(u)) if u < 1 else 1.0)
            u = seilzug(seg(t, T_SAFE, 0.3)); put(f, self.safe, dx=lerp(-30, 0, u), op=u)
            rk.dust(f, t, T_SWIPE + 0.1, self.swipe_box, seed=77)
            rk.dust(f, t, T_STAMP + 0.18, (self.stamp.x + 20, self.stamp.y + 20, self.stamp.x + self.stamp.w - 20,
                                           self.stamp.y + self.stamp.h - 20), seed=78)
            return f, 24
        return self.end.frame(t, T_END), 25


def shimmer(f, t):
    """Aufsteigende Waerme unter dem Riss (Zug 1)."""
    v = seg(t, 2.55 + HOOK_EXTRA + H1, 0.4) * (1 - seg(t, 4.95 + HOOK_EXTRA + H1, 0.35))
    if v <= 0:
        return
    dr = ImageDraw.Draw(f)
    for k, xk in enumerate((250, 420, 600, 780, 950)):
        for j in range(9):
            y0 = 1880 - ((t * 140 + j * 70 + k * 23) % 600)
            if y0 < 1290:
                continue
            pts = [(xk + 7 * math.sin(yy / 34 + k + t * 4), yy) for yy in range(int(y0), int(y0) - 34, -4)]
            al = int(95 * v * min(1, (1880 - y0) / 120) * min(1, (y0 - 1290) / 120))
            dr.line(pts, fill=o.rgb(C["heat"], al), width=3)


def clamp01(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


# ------------------------------------------------------------------ Ton
def sound_events(b):
    """Hook 1 aus dem eigenen Klangset, Puls in Hook 2 und den Zuegen, sonst wie Fassung 3 (Kenney CC0 + selbst erzeugt)."""
    h1 = rk.Hook1(t_grab=T_GRAB, t_geo=T_GEO, t_out=T_OUT)
    b.hook1(h1, root=55.0)
    b.kenney("interface-sounds", "tick_002.ogg", T_Q + 0.05, -10.0, "kreide-tick")
    b.kenney("interface-sounds", "scratch_002.ogg", T_SEC, -12.0, "schnittlinie")
    b.kenney("interface-sounds", "maximize_001.ogg", T_W1, -7.0, "uebergang")
    b.kenney("impact-sounds", "impactMetal_light_000.ogg", T_S2, -7.0, "bohrhaken")
    b.kenney("impact-sounds", "impactMining_000.ogg", T_CRACK, -4.0, "riss")
    b.synth("fizz", T_FLOW[0], -14.0, "heisses-wasser", dur=1.5, seed=3)
    for k, fr in enumerate((1567.98, 1760.0, 2093.0, 2349.3, 2637.0)):
        b.synth("tone", T_GROW0 + 0.1 + 0.28 * k, -21.0 + k * 0.8, "kristall", dur=0.4, freq=fr)
    b.kenney("interface-sounds", "tick_002.ogg", T_LAB, -6.0, "kreide-tick")
    b.kenney("interface-sounds", "maximize_001.ogg", T_W2, -7.0, "uebergang")
    b.kenney("impact-sounds", "impactMetal_light_001.ogg", T_S3, -7.0, "bohrhaken")
    b.synth("rumble", T_S3 + 0.05, -8.5, "zeit-grollen", dur=2.5, seed=2)
    for t0, nm in ((T_E0 + 0.55, "impactMining_001.ogg"), (T_E0 + 1.15, "impactMining_002.ogg"), (T_E0 + 1.70, "impactMining_001.ogg")):
        b.kenney("impact-sounds", nm, t0, -16.0, "abbroeckeln")
    b.synth("riser", T_RISE, -9.0, "steigerung", dur=0.8)
    b.klang("sub_hit", T_S4 - 0.01, -6.0, "payoff-einschlag", f0=80.0, f1=38.0)
    b.kenney("impact-sounds", "impactPunch_heavy_000.ogg", T_S4, -3.0, "treffer")
    b.kenney("impact-sounds", "impactMetal_light_002.ogg", T_S4 + 0.02, -9.0, "bohrhaken")
    b.kenney("interface-sounds", "scratch_001.ogg", T_SWIPE, -5.0, "kreide-wisch")
    b.kenney("interface-sounds", "scratch_002.ogg", T_SWIPE + 0.08, -7.0, "kreide-wisch")
    b.kenney("impact-sounds", "impactPunch_heavy_001.ogg", T_STAMP + 0.16, -5.0, "stempel")
    b.kenney("interface-sounds", "tick_004.ogg", T_SAFE, -8.0, "kreide-tick")
    for k, tk in enumerate(T_KNOCK):
        b.klang("thud", tk, -12.0, "abklopfen", ratio=1.6, seed=k)
    big = [T_W1, T_S2, T_CRACK, T_W2, T_S3]
    b.pulse(T_Q + 0.02, T_RISE - 0.05, bpm=116, gain=-16.0, hat_gain=-25.0, avoid=big)
    b.sound_logo(T_END)
    b.pads([(0.0, T_S4 - 0.15, -9.0), (T_S4, T_END, -11.0)])


if __name__ == "__main__":
    rk.run(Reel, sound_events, META)
