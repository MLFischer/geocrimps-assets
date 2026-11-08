#!/usr/bin/env python3
"""Reel 011 -- MYTH OR ROCK #03: "Glacier-polished granite: what makes this slab shine?" (Faktenbasis: Post #031,
Gletscherschliff ist eine Schicht), Ablauf "offene_frage".

Fassung 1 vom 08.11.2026 nach PRODUKTION.md (Stand 16.10.2026), Vorlage r003 Fassung 6 (Hook 1 + Hook 2, Lesezeit,
ruhiges Tempo, Musik statt Klicks, Abspann mit LIKE & FOLLOW).
Hook 1 0-1,45 s: GEOCRIMPS + CLIMBING ab Frame 0, ein Kletterer an einer Granitplatte mit glaenzenden Schliff-Flecken greift
eine kleine Leiste (Kreidewolke), "x GEOLOGY" schlaegt ein und die Platte klappt in ihre Granit-Signatur auf (Kreuze);
das verraet nichts ueber die Beschichtung.
Hook 2 ab 1,8 s: Formatlabel MYTH OR ROCK, Kontextzeile "GLACIER-POLISHED GRANITE:" (Schlifffarbe) ueber
"WHAT MAKES THIS SLAB SHINE?", 3,65 s; Lichtreflexe wandern ueber die Schliff-Flecken (Bewegung ohne Info).
Uebergang: Lichtstreifen, dann Ueberblendung in den Profilschnitt der Platte.
Zug 1 (harmlos, und richtig): Ein Gletscher gleitet ueber die raue Platte, Schutt an seiner Basis schleift die Buckel ab:
"ICE SANDED IT SMOOTH."
Zug 2 (Wendung): Zoom in die Oberflaeche (Massstabssprung ohne Zahl): Granitkristalle, oben plan geschliffen, darueber ein
Wasserfilm mit Gesteinsmehl unter dem Eis; die Koernchen loesen sich, eine helle Schicht waechst auf dem Gestein:
"BUT LOOK CLOSER…". Callback als naheliegende falsche Antwort "JUST SANDED SMOOTH?", Stempel MYTH darunter.
Payoff: "A SILICA COATING." gross mit Push-in, die Schicht leuchtet. Fazit: zurueck an die Platte, der Kletterer steigt
an die hoehere Leiste, die Schliff-Flecken glaenzen: "IT OUTLASTS THE ICE." Abspann mit LIKE & FOLLOW.
Fakten (v2/faktenbasis/031/sources.md): Schliff = eigenstaendige Schicht im Mikrometerbereich, nicht nur Abrasion (Siman-Tov
et al. 2017); Loesung und Wiederausfaellung des Abriebs durch subglaziales Wasser, an Silizium angereichert (Geology 2019,
"amorphous silica coating"); Schrammen vom Schutt an der Gletscherbasis; die Schicht ist nahezu undurchlaessig, haelt
Flechten fern und bremst die Verwitterung (Haltbarkeit). Vorbedingung des Slots: KEINE Reibungsaussage (Bild und Text sagen
nichts ueber Rutschigkeit). Schichtdicke im Bild stark ueberhoeht (Schema).
Bildmittel (Abwechslungsregel): Uebergang Lichtstreifen + Ueberblendung, Zoom in die Oberflaeche (r010: Zeitreise mit Zaehler) |
Enthuellung Gletscher schleift im Profil, Mikroschnitt: Gesteinsmehl loest sich, Schicht waechst (r010: Landschaft, Delta) |
Payoff Stempel MYTH auf den Callback, dann Antwort gross, Schicht leuchtet; Fazit Kletterer steigt hoeher (r010: Chip C,
kein Stempel) | Musik D-Moll mit F-Dur-Aufloesung, 85 BPM (r010: E-Moll 81 BPM).
Aufruf:  python3 r011_mythorrock_031.py --out ../../../reels --qc <Ordner>   (--stills 0,4.8 | --reach)
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
T_HOOK = T_Q + 3.65                 # Frage steht 3,65 s (7 Woerter), dann Lichtstreifen
T_X0 = T_HOOK + 0.20                # Ueberblendung in den Profilschnitt (0,8 s)
T_X1 = T_X0 + 0.8
T_S2 = T_X1 + 0.15                  # Zug 1: Gletscher schleift
T_ICE0, T_ICE1 = T_S2 + 0.10, T_S2 + 2.2   # Gletscherstirn laeuft ueber die Platte
T1_OFF = T_S2 + 0.05 + EIN + 2.15 + 0.25    # Text 1 (4 Woerter, 2,15 s) blendet aus
T_Z0 = T1_OFF + 0.25 + 0.40         # Atempause, dann Zoom in die Oberflaeche (0,9 s)
T_Z1 = T_Z0 + 0.9
T_S3 = T_Z0 + 0.40                  # Zug 2: "BUT LOOK CLOSER..."
T_L0, T_L1 = T_Z1 + 0.10, T_Z1 + 2.1   # Gesteinsmehl loest sich, Schicht waechst
T2_OFF = T_S3 + 0.05 + EIN + 1.8 + 0.15
T_CALL = T2_OFF + 0.25 + 0.40       # Callback (falsche Antwort)
T_STAMP = T_CALL + EIN + 1.8 + 0.10 # Stempel MYTH, wenn der Callback gelesen ist
T_PAY = T_STAMP + 0.10 + 1.1 + 0.45 # Payoff "A SILICA COATING."
T_RISE = T_PAY - 1.0
T_S5 = T_PAY + 0.15 + 2.6 + 0.30    # Fazit: zurueck an die Platte (0,8 s)
T_UP = T_S5 + 0.35                  # Kletterer steigt an die hoehere Leiste (1,0 s)
T_F = T_S5 + 0.55                   # Fazit-Text
T_END = T_F + EIN + 2.95 + 0.15     # Abspann
DUR = T_END + rk.Outro.DUR

POLISH, POLISH_HI = "#AEBCC3", "#DCE6EA"       # Schliff: silbrig-hell (Faktenbasis-Hero: helle Krusten)
GRANITE, GRANITE_D = "#3B3F43", "#2D3135"
SPECKS = ["#8E8A84", "#9C978F", "#15181A", "#5B6065"]   # Feldspat hell, Biotit dunkel, Quarz grau

# ------------------------------------------------------------------ Szene A: Granitplatte frontal (Hook, Fazit)
YG_A = 1500
LH_A = (448, 1034)                  # linke Hand: kleine Leiste
RH_A = (652, 1102)                  # rechte Hand: Griff dieses Reels (Leiste)
RH_HI = (700, 952)                  # hoehere Leiste im Fazit
FL_A, FR_A = (470, 1356), (606, 1334)
BACK = dict(sw=22, hw=13, eb=(-1, 1), kb=(1, -1))
POSE_START = dict(BACK, hip=(530, 1248), lean=-3, lh=LH_A, rh=(584, 1176), lf=(462, 1378), rf=(600, 1356))
POSE_HANG = dict(BACK, hip=(540, 1236), lean=6, lh=LH_A, rh=RH_A, lf=FL_A, rf=FR_A)
POSE_SWING = dict(POSE_HANG, hip=(546, 1226), lean=9)
POSE_HIGH = dict(BACK, hip=(586, 1150), lean=8, lh=RH_A, rh=RH_HI, lf=(500, 1290), rf=(640, 1262))
EDGES = [LH_A, RH_A, RH_HI, (500, 1294), (640, 1266), FL_A, FR_A]
PATCHES = [(560, 960, 120, 40, -14), (840, 1190, 125, 50, -10), (250, 1200, 110, 38, -16), (760, 1420, 140, 32, -8),
           (930, 960, 80, 32, -12), (190, 990, 75, 30, -18), (360, 1430, 90, 28, -6)]

# ------------------------------------------------------------------ Szene B: Profilschnitt der Platte
def y0b(x):
    return 960 + 0.36 * (x + 20)


_RB = random.Random(7)
_BH = [(_RB.uniform(28, 46), _RB.uniform(0, 6.28), _RB.uniform(0.6, 1.0)) for _ in range(3)]


def bump(x):
    v = sum(a * math.sin(x / p + ph) for p, ph, a in _BH) / 2.6
    return 16 * max(0.0, v) + 4 * (0.5 + 0.5 * math.sin(x / 9.0))


def front(t):
    return lerp(-140, 1180, seg(t, T_ICE0, T_ICE1 - T_ICE0))


def t_pass(x):
    return T_ICE0 + (T_ICE1 - T_ICE0) * (x + 140) / 1320


def rough(x, t):
    return 1 - seilzug(seg(t, t_pass(x) + 0.15, 1.1))


# ------------------------------------------------------------------ Szene C: Mikroschnitt
TOPC = 1170                          # plan geschliffene Oberkante der Kristalle
WAT0 = 1060                          # Oberkante Wasserfilm (darueber Eis)
TH_MAX = 20.0                        # Schichtdicke im Bild (stark ueberhoeht)


def layer_th(t):
    return TH_MAX * seilzug(seg(t, T_L0 + 0.3, T_L1 - T_L0))


# ------------------------------------------------------------------ Reichweite der Haende
def check_reach():
    cl = kl.Climber(scale=1.0, width=18.0, torso_w=36.0); out = {}
    for name, p in (("start", POSE_START), ("hang", POSE_HANG), ("swing", POSE_SWING), ("high", POSE_HIGH)):
        j = cl.joints(p)
        out[name] = round(max(math.dist(j[k], p[k]) for k in ("lh", "rh", "lf", "rf")), 3)
    return out


def pose_a(t):
    if t < T_GRAB:
        return kl.lerp_pose(POSE_START, POSE_SWING, seilzug(seg(t, 0.0, T_GRAB)))
    if t < T_UP:
        u = seg(t, T_GRAB, 0.3)
        p = kl.lerp_pose(POSE_SWING, POSE_HANG, 0.5 - 0.5 * math.cos(math.pi * u))
        if u >= 1:
            w = math.sin(2 * math.pi * (t - T_GRAB - 0.3) / 2.6)
            p = dict(p, hip=(p["hip"][0] + 3 * w, p["hip"][1] + 1.5 * abs(w)), lean=p["lean"] + 1.2 * w)
        return p
    u = seg(t, T_UP, 1.0)                     # steigt hoeher: erst die Fuesse, dann Haende (eine Bewegung)
    p = kl.lerp_pose(POSE_HANG, POSE_HIGH, 0.5 - 0.5 * math.cos(math.pi * u))
    if u < 1:                                 # Hand loest sich vom Griff und greift im Bogen
        a = math.sin(math.pi * u)
        p = dict(p, lh=(p["lh"][0], p["lh"][1] - 18 * a), rh=(p["rh"][0] + 26 * a, p["rh"][1] - 14 * a))
    else:
        w = math.sin(2 * math.pi * (t - T_UP - 1.0) / 2.6)
        p = dict(p, hip=(p["hip"][0] + 2.5 * w, p["hip"][1] + 1.2 * abs(w)), lean=p["lean"] + 1.0 * w)
    return p


# ------------------------------------------------------------------ META
META = dict(
    slug="2026-11-13_mythorrock-03", dur_range=[20.0, 28.0], payoff_t=T_PAY, abspann_ab=T_END,
    title="GeoCrimps r011 MYTH OR ROCK #03 (Offene Frage), Fassung 1", ablauf="offene_frage",
    hook1_bis=T_OUT, hook_ab=T_Q, hook_bis=T_HOOK, weitere_fragen=[[round(T_CALL, 2), round(T_PAY - 0.25, 2)]],
    cover_t=round(T_Q + 0.85, 2),
    on_screen=["MYTH OR ROCK", "GLACIER-POLISHED GRANITE:", "WHAT MAKES THIS SLAB SHINE?", "ICE SANDED IT SMOOTH.",
               "BUT LOOK CLOSER…", "JUST SANDED SMOOTH?", "MYTH", "A SILICA COATING.", "IT OUTLASTS THE ICE.",
               rk.Outro.CTA],
    labels=[],
    verdauen=["A SILICA COATING.", "IT OUTLASTS THE ICE."],
    qc_times=[0.0, T_GRAB, T_GEO, 1.1, 1.6, round(T_Q + 0.85, 2), round(T_HOOK - 0.1, 2), round(T_X0 + 0.4, 2),
              round(T_ICE0 + 1.2, 2), round(T1_OFF - 0.1, 2), round(T_Z0 + 0.5, 2), round(T_L1 - 0.2, 2),
              round(T_STAMP + 0.8, 2), round(T_PAY + 1.2, 2), round(T_END - 0.2, 2), round(T_END + 2.0, 2)],
    marks=[(0, "Hook 1"), (T_GRAB, "Griff"), (T_GEO, "x GEOLOGY"), (T_Q, "Hook 2"), (T_HOOK, "Licht"),
           (T_S2, "Zug 1"), (T_Z0, "Zoom"), (T_S3, "Zug 2"), (T_CALL, "Callback"), (T_STAMP, "MYTH"),
           (T_PAY, "PAYOFF"), (T_S5, "Platte"), (T_F, "Fazit"), (T_END, "Abspann")])


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
        self.label = m.text_sprite("MYTH OR ROCK", X0, rk.FORMAT_Y, "stencil", 40, C["slate"], tracking=0.12)
        ks = m.fit("GLACIER-POLISHED GRANITE:", "display", 96)
        self.hook_kick = m.text_sprite("GLACIER-POLISHED GRANITE:", X0, rk.HOOK_Y, "display", ks, POLISH_HI)
        self.hook, yq = m.lines_sprite(["WHAT MAKES THIS", "SLAB SHINE?"], rk.HOOK_Y + ks + 16, size=136)
        self.text1, _ = m.lines_sprite(["ICE SANDED", "IT SMOOTH."], 352, role="display_xb", size=118)
        self.text2, _ = m.lines_sprite(["BUT LOOK", "CLOSER…"], 352, role="display_xb", size=118)
        self.call, _ = m.lines_sprite(["JUST SANDED", "SMOOTH?"], 352, role="display_xb", size=118)
        self.answer, _ = m.lines_sprite(["A SILICA", "COATING."], 352, size=200)
        self.fazit, _ = m.lines_sprite(["IT OUTLASTS", "THE ICE."], 360, size=150)
        self.stamp = self.make_stamp(700, 700, -7)
        self.stamp.text = "MYTH"
        self._scene_a()
        self._scene_b()
        self._scene_c()

    # -------------------------------------------------------------- Szene A
    def _scene_a(self):
        wall_poly = o.ragged(-20, 832, 1100, YG_A, seed=11, amp=10, n=26, top_only=True)
        self.wall_poly = wall_poly
        pm = Image.new("L", (W * o.S, H * o.S), 0); dpm = ImageDraw.Draw(pm)
        rnd = random.Random(17)
        self.patch_polys = []
        for cx, cy, rx, ry, ang in PATCHES:
            pts = []
            for k in range(36):
                a = 2 * math.pi * k / 36; rr = 1 + rnd.uniform(-0.16, 0.12)
                x, y = rx * rr * math.cos(a), ry * rr * math.sin(a)
                ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
                pts.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
            self.patch_polys.append(pts)
            dpm.polygon([P(x, y) for x, y in pts], fill=255)
        self.pmask = np.asarray(pm.resize((W, H), Image.BOX), np.float32) / 255

        def bg(im):
            o.contour_field(im, 820, 560, n=8, r0=120, step=58, alpha=70)
            d = ImageDraw.Draw(im)
            d.polygon([P(x, y) for x, y in wall_poly], fill=o.rgb(GRANITE))
            r2 = random.Random(5)
            for _ in range(2600):                                   # Granit: Feldspat, Biotit, Quarz als Flecken
                x = r2.uniform(0, 1080); y = r2.uniform(846, YG_A - 4)
                rr = r2.uniform(1.2, 3.4); d.ellipse([P(x - rr, y - rr), P(x + rr, y + rr)], fill=o.rgb(r2.choice(SPECKS), 200))
            lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
            for pts in self.patch_polys:                            # Schliff-Flecken: hell, glatt, feine Schrammen
                dl.polygon([P(x, y) for x, y in pts], fill=o.rgb(POLISH, 175))
            im.alpha_composite(lay)
            lay2 = Image.new("RGBA", im.size, (0, 0, 0, 0)); d2 = ImageDraw.Draw(lay2)
            for (cx, cy, rx, ry, ang), pts in zip(PATCHES, self.patch_polys):
                d2.line([P(x, y) for x, y in pts + pts[:1]], fill=o.rgb(POLISH_HI, 230), width=int(2 * o.S))
                ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
                for k in range(-3, 4):                              # Schrammen parallel zur Fleckenachse
                    oy = k * ry * 0.24
                    L = rx * 0.75 * (1 - abs(k) / 5)
                    a = (cx - L * ca - oy * sa, cy - L * sa + oy * ca); b = (cx + L * ca - oy * sa, cy + L * sa + oy * ca)
                    d2.line([P(*a), P(*b)], fill=o.rgb("#7F8E96", 170), width=int(1.4 * o.S))
            im.alpha_composite(lay2)
            for ex, ey in EDGES:                                    # kleine Leisten
                d.line([P(ex - 22, ey + 4), P(ex + 22, ey + 2)], fill=o.rgb(C["obsidian"]), width=int(7 * o.S))
                d.line([P(ex - 20, ey - 1), P(ex + 20, ey - 3)], fill=o.rgb("#9C978F"), width=int(2.5 * o.S))
            d.line([P(x, y) for x, y in wall_poly[:27]], fill=o.rgb(C["slate"]), width=int(3 * o.S))
            lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
            ImageDraw.Draw(lay).rectangle([P(-10, YG_A), P(1090, 1930)], fill=o.rgb(C["graphite"]))
            im.alpha_composite(lay)
            r3 = random.Random(3)
            for _ in range(120):
                x, y = r3.uniform(10, 1070), r3.uniform(YG_A + 14, 1900); rr = r3.uniform(1.5, 3.5)
                d.ellipse([P(x - rr, y - rr), P(x + rr, y + rr)], fill=o.rgb(C["line"]))
            d.line([P(-10, YG_A), P(1090, YG_A)], fill=o.rgb(C["slate"]), width=int(3 * o.S))
            kl.crash_pad(im, 380, 700, YG_A + 34)
        self.bg_a = m.background(bg)
        self.geo = kl.GeoReveal(wall_poly, "granite", RH_A[0], RH_A[1], pat_alpha=120, seed=8)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        self.diag = (xx * 0.8 + yy * 0.6)
        self.glint_col = Image.new("RGBA", (W, H), o.rgb(POLISH_HI))

    def glint(self, f, t, strength=1.0):
        """Lichtreflex wandert ueber die Schliff-Flecken (Bewegung ohne Information)."""
        ph = ((t / 2.8) % 1.0) * 1900 + 400
        band = np.clip(1 - np.abs(self.diag - ph) / 70.0, 0, 1) ** 1.6
        a = band * self.pmask * 170 * strength
        y0, y1 = 830, YG_A
        img = self.glint_col.crop((0, y0, W, y1)).copy()
        img.putalpha(Image.fromarray(np.clip(a[y0:y1], 0, 255).astype(np.uint8)))
        f.alpha_composite(img, (0, y0))

    def world_a(self, t):
        f = self.bg_a.copy()
        self.glint(f, t)
        u = seilzug(seg(t, T_GEO, 0.5))
        if u > 0 and t < T_OUT + 0.4:
            self.geo.put(f, u, fade=1 - seg(t, T_OUT, 0.4))
        put(f, self.climber.sprite(pose_a(t)))
        kl.chalk_puff(f, t, T_GRAB, RH_A[0], RH_A[1] - 6, seed=11)
        kl.chalk_puff(f, t, T_UP + 0.9, RH_HI[0], RH_HI[1] - 6, seed=16, size=0.8)
        return f

    # -------------------------------------------------------------- Szene B: Profil mit Gletscher
    def _scene_b(self):
        xs = list(range(-20, 1101, 6))
        self.xs_b = xs
        rock = [(x, y0b(x)) for x in xs] + [(1100, 1960), (-20, 1960)]

        def bg(im):
            o.contour_field(im, 880, 540, n=8, r0=110, step=56, alpha=60)
            o.rock_body(im, rock, fill=GRANITE_D, pattern="granite", pat_color="#4A5056", seed=6)
            d = ImageDraw.Draw(im)
            r2 = random.Random(9)
            for _ in range(1400):
                x = r2.uniform(-10, 1090); y = r2.uniform(y0b(x) + 8, 1910)
                rr = r2.uniform(1.0, 2.6); d.ellipse([P(x - rr, y - rr), P(x + rr, y + rr)], fill=o.rgb(r2.choice(SPECKS), 150))
        self.bg_b = m.background(bg)
        r = random.Random(23)
        self.grit = [(r.uniform(-400, 1000), r.uniform(3, 14), r.uniform(2.0, 4.2), r.choice([C["slate"], "#9C978F", C["magnesia"]]))
                     for _ in range(70)]

    def world_b(self, t):
        f = self.bg_b.copy()
        fr = front(t)

        def draw(d, X, Y):
            top = [(x, y0b(x) - bump(x) * rough(x, t)) for x in self.xs_b]
            d.polygon([(X(x), Y(y)) for x, y in top] + [(X(x), Y(y0b(x) + 2)) for x, _ in top[::-1]], fill=o.rgb(GRANITE_D))
            for (xa, ya), (xb, yb) in zip(top, top[1:]):            # Oberflaeche: rau -> glatt und hell
                k = 1 - rough(xa, t)
                col = C["slate"] if k < 0.5 else POLISH_HI
                d.line([(X(xa), Y(ya)), (X(xb), Y(yb))], fill=o.rgb(col), width=int((3 + 1.5 * k) * o.S))
            if fr > -130 and t < T_Z1 + 0.1:                        # Gletscher: Eiskoerper mit Stirn
                ice = []
                for x in self.xs_b:
                    if x > fr:
                        break
                    th = 270 * min(1.0, max(0.0, (fr - x) / 260.0)) ** 0.5
                    ice.append((x, y0b(x) - bump(x) * rough(x, t) - th))
                if len(ice) > 2:
                    base = [(x, y0b(x) - bump(x) * rough(x, t)) for x, _ in ice]
                    poly = ice + base[::-1]
                    d.polygon([(X(x), Y(y)) for x, y in poly], fill=o.rgb(C["ice"], 70))
                    d.line([(X(x), Y(y)) for x, y in ice], fill=o.rgb(C["ice"], 210), width=int(3 * o.S))
                    flow = (t - T_ICE0) * 260
                    for k, off in enumerate((70, 140, 210, 280)):       # Fliesslinien im Eis wandern mit
                        seg_pts = []
                        for (x, yt), (_, yb) in zip(ice, base):
                            if yb - yt < off + 10:
                                continue
                            on = ((x - flow - 40 * k) % 120) < 70
                            if on:
                                seg_pts.append((X(x), Y(yb - off)))
                            elif len(seg_pts) > 1:
                                d.line(seg_pts, fill=o.rgb(C["ice"], 120), width=int(2 * o.S)); seg_pts = []
                            else:
                                seg_pts = []
                        if len(seg_pts) > 1:
                            d.line(seg_pts, fill=o.rgb(C["ice"], 120), width=int(2 * o.S))
                    for x0, oy, rr, col in self.grit:                    # Schutt an der Gletscherbasis
                        x = x0 + (t - T_ICE0) * 330
                        if -20 < x < fr - 20:
                            y = y0b(x) - bump(x) * rough(x, t) - oy
                            d.ellipse([X(x - rr), Y(y - rr), X(x + rr), Y(y + rr)], fill=o.rgb(col))
        put(f, rk.region(0, 560, 1080, 1420, draw))
        if t >= T_ICE0:                                             # Gesteinsstaub hinter der Stirn
            dr = ImageDraw.Draw(f); rnd = random.Random(int(t * 30))
            for _ in range(14):
                x = rnd.uniform(max(-20, fr - 420), min(1080, fr - 10))
                y = y0b(x) - rnd.uniform(2, 12)
                dr.ellipse([x - 1.5, y - 1.5, x + 1.5, y + 1.5], fill=o.rgb(C["magnesia"], 150))
        return f

    # -------------------------------------------------------------- Szene C: Mikroschnitt
    def _scene_c(self):
        rnd = random.Random(31)
        seeds = [(rnd.uniform(-60, 1140), rnd.uniform(TOPC - 60, 1980)) for _ in range(46)]
        cols = [rnd.choice(["#8E8A84", "#A39D94", "#6F757B", "#5B6065", "#2A2E32", "#7C7770"]) for _ in seeds]
        hh = H - TOPC
        yy, xx = np.mgrid[0:hh, 0:W].astype(np.float32)
        yy += TOPC
        best = np.full((hh, W), 1e12, np.float32); idx = np.zeros((hh, W), np.int32); second = np.full((hh, W), 1e12, np.float32)
        for i, (sx, sy) in enumerate(seeds):
            dd = (xx - sx) ** 2 + (yy - sy) ** 2
            better = dd < best
            second = np.where(better, best, np.minimum(second, dd))
            idx = np.where(better, i, idx); best = np.where(better, dd, best)
        edge = (np.sqrt(second) - np.sqrt(best)) < 3.0
        rgbarr = np.array([o.rgb(c)[:3] for c in cols], np.uint8)[idx]
        rgbarr[edge] = (20, 23, 26)
        crystal = Image.fromarray(rgbarr, "RGB").convert("RGBA")

        def bg(im):
            d = ImageDraw.Draw(im)
            lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
            dl.rectangle([P(-10, 800), P(1090, WAT0)], fill=o.rgb(C["ice"], 46))        # Eis
            r2 = random.Random(4)
            for _ in range(28):
                x = r2.uniform(0, 1080); y = r2.uniform(830, WAT0 - 30); L = r2.uniform(40, 140)
                dl.line([P(x, y), P(x + L, y + 6)], fill=o.rgb(C["ice"], 60), width=int(2 * o.S))
            dl.rectangle([P(-10, WAT0), P(1090, TOPC)], fill=o.rgb(C["water"], 105))    # Wasserfilm
            im.alpha_composite(lay)
            d.line([P(-10, WAT0), P(1090, WAT0)], fill=o.rgb(C["ice"], 200), width=int(2 * o.S))
        base = m.background(bg)
        base.alpha_composite(crystal, (0, TOPC))
        ImageDraw.Draw(base).line([(0, TOPC), (W, TOPC)], fill=o.rgb("#C9C3B8"), width=2)
        self.bg_c = base
        r3 = random.Random(41)
        self.flour = [(r3.uniform(-200, 1080), r3.uniform(WAT0 + 14, TOPC - 26), r3.uniform(3.0, 7.0),
                       r3.uniform(T_L0, T_L1 - 0.6), r3.uniform(0, 6.28)) for _ in range(80)]

    def world_c(self, t, glow=0.0):
        f = self.bg_c.copy()
        dr = ImageDraw.Draw(f)
        for x0, y, r, td, ph in self.flour:                          # Gesteinsmehl treibt im Wasser und loest sich
            x = x0 + (t - T_Z0) * 55
            x = (x + 200) % 1300 - 200
            v = seg(t, td, 0.7)
            rr = r * (1 - v)
            yy = y + 4 * math.sin(t * 1.7 + ph)
            if rr > 0.5:
                dr.ellipse([x - rr, yy - rr, x + rr, yy + rr], fill=o.rgb("#B8B2A8", 230))
            if 0 < v < 1:                                            # geloestes Material sinkt zur Oberflaeche
                for k in range(3):
                    q = seg(t, td + 0.12 * k, 0.8)
                    if 0 < q < 1:
                        sx = x + 6 * (k - 1); sy = lerp(yy, TOPC - layer_th(t) - 2, q)
                        dr.ellipse([sx - 1.6, sy - 1.6, sx + 1.6, sy + 1.6], fill=o.rgb(POLISH_HI, int(220 * (1 - q * 0.5))))
        th = layer_th(t)
        if th > 0.4:                                                 # die Schicht waechst auf dem Gestein
            col = POLISH_HI if glow <= 0 else C["magnesia"]
            lay = Image.new("RGBA", (W, int(th) + 8), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
            dl.rectangle([0, 4, W, 4 + th], fill=o.rgb(col, int(225 + 30 * glow)))
            if glow > 0:
                dl.rectangle([0, 0, W, 8 + th], outline=None, fill=o.rgb(C["magnesia"], int(110 * glow)))
                dl.rectangle([0, 4, W, 4 + th], fill=o.rgb(C["magnesia"]))
            f.alpha_composite(lay, (0, int(TOPC - th - 4)))
        return f

    def make_stamp(self, cx, cy, angle):
        s = o.S; f1 = o.font("stencil", 96); t1 = "MYTH"
        w1 = f1.getlength(t1); bw = int(w1 + 2 * 34 * s); bh = int((96 + 2 * 26) * s)
        im = Image.new("RGBA", (bw + 40 * s, bh + 40 * s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        ox, oy = 20 * s, 20 * s; col = o.rgb(C["magnesia"])
        d.rounded_rectangle([ox, oy, ox + bw, oy + bh], radius=14 * s, outline=col, width=6 * s)
        d.text((ox + bw / 2, oy + bh / 2 + 4 * s), t1, font=f1, fill=col, anchor="mm")
        rng = np.random.default_rng(11)
        a = np.asarray(im.getchannel("A"), np.float32)
        noise = np.asarray(Image.fromarray((rng.random(a.shape) * 255).astype(np.uint8)).resize(im.size), np.float32) / 255
        a *= np.clip(1.4 - noise * 1.05, 0.3, 1.0)
        im.putalpha(Image.fromarray(a.astype(np.uint8)))
        im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
        small = im.resize((im.width // s, im.height // s), Image.LANCZOS)
        return m.Sprite(small, int(cx - small.width / 2), int(cy - small.height / 2))

    # -------------------------------------------------------------- Frames
    ZC_B = (540, int(y0b(540)))

    def frame(self, t):
        if t < T_X0:                                             # Szene 1: Hook (frontal)
            f = m.zoomed(self.world_a(t), 1 + 0.03 * seilzug(seg(t, 0, T_HOOK)), RH_A[0], RH_A[1])
            put(f, self.rails[0])
            self.hook1.draw(f, t, hook_bis=T_HOOK)
            u = seilzug(seg(t, T_Q, EIN))
            if u > 0:
                fade = 1 - seg(t, T_HOOK, 0.12)
                put(f, self.label, dx=lerp(-30, 0, u), op=u * fade)
                put(f, self.hook_kick, dx=lerp(-40, 0, u), op=u * fade)
                put(f, self.hook, dx=lerp(-40, 0, u), op=u * fade)
            if t >= T_HOOK:
                put(f, rk.light_sweep(seg(t, T_HOOK, 0.5), color=POLISH_HI))
            return f, 111
        if t < T_X1:                                             # Uebergang: Ueberblendung in den Profilschnitt
            u = seilzug(seg(t, T_X0, T_X1 - T_X0))
            fa = m.zoomed(self.world_a(t), 1.03, RH_A[0], RH_A[1])
            fb = m.zoomed(self.world_b(t), lerp(1.15, 1.0, u), *self.ZC_B)
            f = Image.blend(fa, fb, u)
            put(f, rk.light_sweep(seg(t, T_HOOK, 0.5), color=POLISH_HI))
            put(f, self.rails[0])
            return f, 112
        if t < T_Z0:                                             # Zug 1: Gletscher schleift
            f = m.zoomed(self.world_b(t), 1 + 0.03 * seg(t, T_X1, T_Z0 - T_X1), *self.ZC_B)
            put(f, self.rails[1]); self.rail.pop(f, t, 0, T_S2)
            u = seilzug(seg(t, T_S2 + 0.05, EIN)); put(f, self.text1, dx=lerp(-40, 0, u), op=u * (1 - seg(t, T1_OFF, 0.25)))
            return f, 113
        if t < T_S5:
            if t < T_Z1:                                         # Zoom in die Oberflaeche, Mikroschnitt blendet ein
                u = seilzug(seg(t, T_Z0, T_Z1 - T_Z0))
                fb = m.zoomed(self.world_b(t), lerp(1.03, 3.2, u), *self.ZC_B)
                fc = m.zoomed(self.world_c(t), lerp(1.6, 1.0, u), 540, TOPC)
                f = Image.blend(fb, fc, seg(t, T_Z0 + 0.25, 0.6))
            else:
                z = 1 + 0.03 * (0.5 - 0.5 * math.cos(math.pi * seg(t, T_Z1, T_PAY - T_Z1)))
                glow = math.sin(math.pi * min(1.0, seg(t, T_PAY, 1.2) * 0.5 + 0.0)) if t >= T_PAY else 0.0
                glow = max(glow, 0.6 * seg(t, T_PAY, 0.3)) if t >= T_PAY else 0.0
                if t >= T_PAY:
                    z *= lerp(1.0, 1.05, 0.5 - 0.5 * math.cos(math.pi * seg(t, T_PAY, T_S5 - T_PAY)))
                f = m.zoomed(self.world_c(t, glow), z, 540, TOPC)
            put(f, self.rails[3] if t >= T_PAY else self.rails[2])
            self.rail.pop(f, t, 1, T_S3)
            u = seilzug(seg(t, T_S3 + 0.05, EIN)); put(f, self.text2, dx=lerp(-40, 0, u), op=u * (1 - seg(t, T2_OFF, 0.25)))
            if t < T_PAY:
                u = seilzug(seg(t, T_CALL, EIN)); put(f, self.call, dx=lerp(-30, 0, u), op=u * (1 - seg(t, T_PAY - 0.25, 0.2)))
                u = seg(t, T_STAMP, 0.3)
                if u > 0:
                    put(f, self.stamp, op=min(1, u * 3) * (1 - seg(t, T_PAY - 0.25, 0.2)),
                        scale=lerp(1.65, 1.0, griff(u)) if u < 1 else 1.0)
                rk.dust(f, t, T_STAMP + 0.18, (self.stamp.x + 30, self.stamp.y + 30, self.stamp.x + self.stamp.w - 30,
                                               self.stamp.y + self.stamp.h - 30), seed=78)
                return f, 114
            u = seg(t, T_PAY, 0.3)
            self.rail.logo_pop(f, t, T_PAY)
            put(f, self.answer, op=min(1, u * 2) * (1 - seg(t, T_S5 - 0.2, 0.2)), scale=lerp(1.18, 1.0, seilzug(u)), anchor=(X0, 352))
            return f, 115
        if t < T_END:                                            # Fazit: zurueck an die Platte
            u = seilzug(seg(t, T_S5, 0.8))
            z = 1 + 0.03 * seg(t, T_S5 + 0.8, T_END - T_S5 - 0.8)
            fa = m.zoomed(self.world_a(t), z, RH_A[0], RH_A[1])
            if u < 1:
                fc = m.zoomed(self.world_c(t, 0.6 * (1 - u)), lerp(1.05, 2.0, u), 540, TOPC)
                f = Image.blend(fc, fa, u)
            else:
                f = fa
            put(f, self.rails[3])
            v = seilzug(seg(t, T_F, EIN)); put(f, self.fazit, dx=lerp(-40, 0, v), op=v)
            return f, 116
        return self.outro.frame(t, T_END), 117


# ------------------------------------------------------------------ Ton: Musik in D-Moll / F-Dur, 85 BPM
DM9, BBMAJ7, F_, C_, GM7, AM7, A7SUS4, FMAJ7 = ([50, 53, 57, 60, 64], [50, 53, 57, 58], [53, 57, 60, 65], [52, 55, 60, 64],
                                             [50, 53, 55, 58], [52, 55, 57, 60], [52, 55, 57, 62], [52, 53, 57, 60])
PENTA = [74, 77, 79, 81, 84, 86, 89]   # D-Moll-Pentatonik ab D5


def sound_events(b):
    """Musik in D-Moll mit F-Dur-Aufloesung (85 BPM) nach Szenen; Hook 1 musikalisch; Gletscher als leises Schleifen,
    Gesteinsmehl als fallende, die wachsende Schicht als steigende Toene der Pentatonik; Akkordschlag zur Aufloesung."""
    h1 = rk.Hook1(t_grab=T_GRAB, t_geo=T_GEO, t_out=T_OUT)
    b.hook1(h1, akkord=DM9, bassnote=38)
    b.musik([
        (T_Q - 0.1, T_Q + 1.9, DM9, 38, "ruhig"),                # Frage: offen
        (T_Q + 1.9, T_HOOK, BBMAJ7, 46, "ruhig"),
        (T_HOOK, T_S2, FMAJ7, 41, "flaeche"),                    # Lichtstreifen, Profil
        (T_S2, T_S2 + 1.6, DM9, 38, "bewegt"),                   # Gletscher gleitet
        (T_S2 + 1.6, T_Z0, GM7, 43, "bewegt"),
        (T_Z0, T_L0, AM7, 45, "flaeche"),                        # Zoom
        (T_L0, T_CALL, DM9, 38, "steigend"),                     # Schicht waechst
        (T_CALL, T_STAMP, BBMAJ7, 46, "ruhig"),                  # "JUST SANDED SMOOTH?"
        (T_STAMP, T_RISE, GM7, 43, "flaeche"),                   # MYTH
        (T_RISE, T_PAY - 0.15, A7SUS4, 45, "flaeche"),           # Steigerung, dann 0,15 s Stille
        (T_PAY, T_S5, DM9, 38, "flaeche"),                       # Aufloesung: verdauen
        (T_S5, T_F + 1.2, BBMAJ7, 46, "ruhig"),                  # zurueck an die Platte
        (T_F + 1.2, T_END, F_, 41, "ruhig"),                     # Fazit: nach F-Dur aufgeloest
        (T_END, DUR, F_, 41, "flaeche"),                         # Abspann (Musik dort leiser: s. u.)
    ], bpm=85.0, gain=-12.0)
    b.synth("whoosh", T_HOOK, -17.0, "lichtstreifen", dur=0.6, seed=4)
    for k in range(4):                                           # Lichtreflexe in Hook 2: hohe, leise Toene
        b.ton("zupf", T_Q + 0.9 + 0.7 * k, -22.0, "glanz", m=PENTA[(k * 2) % 7] + 12, dauer=0.6, pan=0.3)
    b.ton("zupf", T_S2, -14.0, "bohrhaken", m=81, dauer=0.9)
    b.klang("crunch", T_ICE0 + 0.4, -23.0, "schleifen", dur=1.4, seed=3)
    b.klang("crunch", T_ICE0 + 1.3, -24.0, "schleifen", dur=1.2, seed=5)
    b.ton("schwelle", T_Z0 - 0.1, -14.0, "zoom", akkord=AM7, dauer=0.9)
    b.ton("zupf", T_S3, -14.0, "bohrhaken", m=84, dauer=0.9)
    for k in range(6):                                           # Gesteinsmehl loest sich: fallende, die Schicht: steigende Toene
        b.ton("zupf", T_L0 + 0.3 * k, -19.0, "mehl", m=PENTA[6 - k], dauer=0.6, pan=0.2 * (k % 3 - 1))
    for k in range(4):
        b.ton("zupf", T_L0 + 0.5 + 0.4 * k, -17.0, "schicht", m=PENTA[k] - 12, dauer=0.8)
    b.ton("zupf", T_CALL, -10.0, "frage", m=74, dauer=0.9)      # Frage: steigende Quarte
    b.ton("zupf", T_CALL + 0.2, -10.0, "frage", m=79, dauer=1.2)
    b.klang("thud", T_STAMP + 0.16, -9.0, "stempel", seed=8)
    b.ton("zupf", T_STAMP + 0.16, -11.0, "stempel", m=69, dauer=1.0)
    b.ton("schwelle", T_RISE, -8.0, "steigerung", akkord=A7SUS4, dauer=T_PAY - 0.15 - T_RISE)
    b.klang("sub_hit", T_PAY - 0.01, -10.0, "payoff-einschlag", f0=78.0, f1=36.0)
    b.ton("akzent", T_PAY, -4.0, "payoff", akkord=DM9, bassnote=38)
    b.synth("whoosh", T_S5, -20.0, "zurueck", dur=0.7, seed=6)
    b.klang("chalk_slap", T_UP + 0.9, -12.0, "griff", seed=2)
    b.ton("zupf", T_F, -14.0, "fazit", m=77, dauer=0.9)
    b.klanglogo(T_END + 0.3, tonika=65, gain=-10.5)               # Abspann: Logo (F-Dur)
    b.ton("zupf", T_END + 1.3, -15.0, "herz", m=81, dauer=1.2)


if __name__ == "__main__":
    if "--reach" in sys.argv:
        print(check_reach())
        sys.exit(0)
    rk.run(Reel, sound_events, META)
