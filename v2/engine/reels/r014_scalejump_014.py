#!/usr/bin/env python3
"""Reel 014 -- SCALE JUMP #02: "Red sandstone: what colour are the grains?" (Faktenbasis: Post #014, Rotfaerbung), Ablauf
"offene_frage".

Fassung 1 vom 22.11.2026 nach PRODUKTION.md (Stand 16.11.2026, Kennzahlen-Regeln 5a), Vorlage r003 Fassung 6 (Musik,
Abspann, Lesezeit), Lupenkreis-Sprung wie r006, aber kuerzer: Hook 1 0,75 s, Themenfrage ab 1,05 s, zwei Zuege, 25 Woerter.
Hook 1 0-0,75 s: GEOCRIMPS + CLIMBING ab Frame 0, ein Kletterer greift eine Leiste an einer roten Sandsteinwand
(Kreidewolke), "x GEOLOGY" schlaegt ein und die Wand klappt in ihre Sandstein-Signatur auf (Punkte; verraet die Farbe
der Koerner nicht).
Hook 2 ab 1,05 s: Formatlabel SCALE JUMP, Kontextzeile "RED SANDSTONE:" (Felsfarbe) ueber "WHAT COLOUR ARE THE GRAINS?",
steht 3,8 s; Raetsel ohne Vorwissen: jeder sieht die rote Wand und kann raten.
Zug 1: Lupenkreis neben dem Kletterer (er haengt weiter an der Leiste), darin die Koerner, alle rot: die naheliegende
Antwort als Frage "RED, RIGHT?" (steht 2,65 s, Bedenkzeit).
Zug 2: Lupenkreis-Sprung auf ein einzelnes Korn, eine Schnittlinie zieht sich darueber: "BUT CUT ONE OPEN…".
Payoff: das Korn bricht entlang der Linie auf, innen hellgrau, aussen ein duenner roter Saum: "MOSTLY PALE GREY."
(Quelle: Quarzkoerner "usually pale grey", daher MOSTLY). Fazit: der Saum leuchtet, der Lupenkreis schliesst sich auf
die Leiste, der Kletterer zieht durch: "THE RED IS SKIN-DEEP." (Haematit-Ueberzug um jedes Korn). Abspann LIKE & FOLLOW.
Fakten (v2/faktenbasis/014/sources.md): Rotfaerbung durch feinkoernigen Haematit (Eisenoxid) als Kornueberzug; Haematit
volumetrisch unbedeutend, optisch dominant; Quarzkoerner meist hellgrau. Keine Zahlen im Bild, kein Ortsname.
Bildmittel (Abwechslungsregel, voriges Reel r013): Uebergang Lupenkreis neben dem Kletterer, dann Lupenkreis-Sprung (r013:
Zoom auf die Hand, Zeitraffer rueckwaerts) | Enthuellung Massstabssprung und Schnitt durch ein Korn (r013: Bindemasse loest
sich, Fluss im Seitenschnitt) | Payoff Antwort gross mit Push-in, Korn klappt auf, Saum leuchtet, kein Stempel, kein Chip
(r013: Chip B) | Musik H-Moll mit D-Dur-Aufloesung, 77 BPM (r013: E-Dur 83 BPM).
Aufruf:  python3 r014_scalejump_014.py --out ../../../reels --qc <Ordner>   (--stills 0,4.8 fuer Einzelbilder, --reach)
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

# ------------------------------------------------------------------ Zeitplan (Kennzahlen-Regeln seit 17.11.2026)
EIN = 0.45
T_GRAB, T_GEO, T_OUT = 0.25, 0.45, 0.75                       # Hook 1 (kurz)
T_Q = 1.05                                                    # Hook 2: Themenfrage
T_HOOK = T_Q + 3.8                                            # Frage steht 3,8 s
J1_0, J1_1 = T_HOOK, T_HOOK + 0.85                            # Lupenkreis oeffnet sich neben dem Kletterer
T_S2 = J1_1 + 0.05                                            # Zug 1: "RED, RIGHT?"
T1_OFF = T_S2 + 2.65
J2_0 = T1_OFF + 0.30                                          # Sprung auf ein Korn
J2_1 = J2_0 + 0.80
T_S3 = J2_1 + 0.10                                            # Zug 2: "BUT CUT ONE OPEN…"
T_CUT0, T_CUT1 = T_S3 + 0.55, T_S3 + 1.75                     # Schnittlinie zieht sich ueber das Korn
T2_OFF = T_S3 + 3.0
T_RISE = T2_OFF - 1.2                                         # Akkord schwillt an, 0,15 s Stille
T_P = T2_OFF + 0.40                                           # Payoff: Korn klappt auf, "MOSTLY PALE GREY."
T_ANS_OFF = T_P + 2.85
T_FAZ = T_ANS_OFF + 0.60                                      # Fazit nach einer Atempause
T_GLOW = T_FAZ + 0.10                                         # Saum leuchtet
J3_0, J3_1 = T_FAZ + 0.85, T_FAZ + 2.05                       # Lupenkreis schliesst sich auf die Leiste (langsam)
T_PULL = J3_1 - 0.15                                          # Kletterer zieht durch
T_END = T_FAZ + 3.45
DUR = T_END + rk.Outro.DUR

# ------------------------------------------------------------------ Szene: rote Sandsteinwand, Kletterer links
TOP, YG = 860, 1500
ROCK, ROCK_D, ROCK_L = "#A24E39", "#7A3727", "#C8785A"        # roter Sandstein (Zusatzfarbe, begruendet: das Thema ist die Farbe)
COAT, COAT_D, COAT_H = "#B0472F", "#7E2E1E", "#D9785C"        # Haematit-Ueberzug der Koerner
QUARTZ, QUARTZ_D, QUARTZ_L = "#C9C6BF", "#9C9890", "#E2DFD8"  # Quarz, "usually pale grey"
PORE = "#24140F"
BACK = dict(sw=22, hw=13, eb=(-1, 1), kb=(1, -1))
DXS = -220                                                    # Posen aus r006, nach links verschoben (Platz fuer die Lupe)
EDGE = (604 + DXS, 1008)
POCKET = (436 + DXS, 990)
HIGH = (492 + DXS, 905)
FOOT_L, FOOT_R = (452 + DXS, 1318), (572 + DXS, 1300)
FOOT_L2, FOOT_R2 = (474 + DXS, 1236), (590 + DXS, 1222)
POSE_START = dict(BACK, hip=(498 + DXS, 1212), lean=-3, lh=POCKET, rh=(560 + DXS, 1112), lf=(446 + DXS, 1338), rf=(560 + DXS, 1326))
POSE_HANG = dict(BACK, hip=(516 + DXS, 1172), lean=7, lh=POCKET, rh=EDGE, lf=FOOT_L, rf=FOOT_R)
POSE_SWING = dict(POSE_HANG, hip=(522 + DXS, 1162), lean=10)
POSE_PULL = dict(BACK, hip=(548 + DXS, 1096), lean=3, lh=HIGH, rh=EDGE, lf=FOOT_L2, rf=FOOT_R2)
LC, LR = (705, 1150), 235                                     # Lupenkreis in Zug 1
S1, S2 = 44.0, 285.0                                          # Massstab der Kornwelt: Lupe bzw. ein Korn (px je Einheit)
GC = (560, 1160)                                              # Bildmitte des grossen Korns
JUMP_Z = 2.3


def check_reach():
    cl = kl.Climber(scale=1.0, width=18.0, torso_w=36.0); out = {}
    for name, p in (("start", POSE_START), ("hang", POSE_HANG), ("swing", POSE_SWING), ("pull", POSE_PULL)):
        j = cl.joints(p)
        out[name] = round(max(math.dist(j[k], p[k]) for k in ("lh", "rh", "lf", "rf")), 2)
    return out


def climber_pose(t):
    if t < T_GRAB:
        return kl.lerp_pose(POSE_START, POSE_SWING, seilzug(seg(t, 0.0, T_GRAB)))
    if t < T_PULL:
        u = seg(t, T_GRAB, 0.3)
        p = kl.lerp_pose(POSE_SWING, POSE_HANG, 0.5 - 0.5 * math.cos(math.pi * u))
        if u >= 1:                                             # haengt, atmet, pendelt leicht
            w = math.sin(2 * math.pi * (t - T_GRAB - 0.3) / 2.6)
            p = dict(p, hip=(p["hip"][0] + 3 * w, p["hip"][1] + 1.5 * abs(w)), lean=p["lean"] + 1.2 * w)
            if T_S2 + 0.8 <= t < T_S2 + 1.7:                   # schaut kurz zur Lupe: Gewicht nach rechts
                v = math.sin(math.pi * seg(t, T_S2 + 0.8, 0.9))
                p = dict(p, hip=(p["hip"][0] + 8 * v, p["hip"][1]), lean=p["lean"] + 4 * v)
        return p
    u = seg(t, T_PULL, 0.9)
    p = kl.lerp_pose(POSE_HANG, POSE_PULL, 0.5 - 0.5 * math.cos(math.pi * u))
    if u >= 1:
        w = math.sin(2 * math.pi * (t - T_PULL - 0.9) / 2.8)
        p = dict(p, hip=(p["hip"][0] + 2 * w, p["hip"][1] + 1.5 * abs(w)), lean=p["lean"] + 0.8 * w)
    return p


# ------------------------------------------------------------------ Kornwelt (Einheiten: Zielkorn Radius 1 bei 0,0)
def grain_shape(rad, seed, n=48):
    rnd = random.Random(seed)
    harm = [(k, rnd.uniform(0.02, 0.07), rnd.uniform(0, 6.28)) for k in (2, 3, 4, 5)]
    sq = rnd.uniform(0.82, 1.0); rot = rnd.uniform(0, 6.28)
    pts = []
    for j in range(n):
        a = 2 * math.pi * j / n
        r = rad * (1 + sum(am * math.cos(k * a + ph) for k, am, ph in harm))
        x, y = r * math.cos(a), r * sq * math.sin(a)
        pts.append((x * math.cos(rot) - y * math.sin(rot), x * math.sin(rot) + y * math.cos(rot)))
    return pts


def build_grains():
    rnd = random.Random(14)
    gs = [dict(x=0.0, y=0.0, r=1.0, shape=grain_shape(1.0, 99), tone=0)]
    tries = 0
    while tries < 9000:
        tries += 1
        x, y = rnd.uniform(-7.5, 7.5), rnd.uniform(-7.5, 7.5)
        r = rnd.uniform(0.62, 1.12)
        if all(math.hypot(x - g["x"], y - g["y"]) > (r + g["r"]) * 0.97 for g in gs):
            gs.append(dict(x=x, y=y, r=r, shape=grain_shape(r, tries), tone=rnd.randrange(3)))
    return gs


GRAINS = build_grains()


def draw_field(im, s, cx, cy, skip_target=False, w_line=2.0):
    """Kornwelt im Massstab s (px je Einheit), Zielkorn bei (cx, cy); alle Koerner rot ueberzogen."""
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, im.size[0], im.size[1]], fill=o.rgb(PORE))   # Porenraum
    for k, g in enumerate(GRAINS):
        if skip_target and k == 0:
            continue
        gx, gy = cx + g["x"] * s, cy + g["y"] * s
        if gx + 1.3 * s < -40 or gx - 1.3 * s > W + 40 or gy + 1.3 * s < -40 or gy - 1.3 * s > H + 40:
            continue
        col = (COAT, "#A84129", "#B9503A")[g["tone"]]
        pts = [P(gx + x * s, gy + y * s) for x, y in g["shape"]]
        d.polygon(pts, fill=o.rgb(col))
        d.line(pts + [pts[0]], fill=o.rgb(COAT_D), width=max(2, int(w_line * o.S)))
        hl = [P(gx + x * s * 0.78 - 0.08 * s, gy + y * s * 0.78 - 0.1 * s) for x, y in g["shape"][26:38]]
        d.line(hl, fill=o.rgb(COAT_H, 170), width=max(2, int(w_line * 1.4 * o.S)), joint="curve")


def grain_sprite(s, cx, cy, opened):
    """Zielkorn als 2x-Sprite: geschlossen (rot) oder aufgeschnitten (hellgrau, duenner roter Saum)."""
    shape = GRAINS[0]["shape"]
    R = 1.25 * s; x0, y0 = int(cx - R), int(cy - R); size = int(2 * R) + 2
    im = Image.new("RGBA", (size * o.S, size * o.S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    Q = lambda x, y: ((cx + x * s - x0) * o.S, (cy + y * s - y0) * o.S)
    outer = [Q(x, y) for x, y in shape]
    if not opened:
        d.polygon(outer, fill=o.rgb(COAT))
        d.line(outer + [outer[0]], fill=o.rgb(COAT_D), width=int(4 * o.S))
        hl = [Q(x * 0.78 - 0.08, y * 0.78 - 0.1) for x, y in shape[26:38]]
        d.line(hl, fill=o.rgb(COAT_H, 190), width=int(6 * o.S), joint="curve")
    else:
        rim = 7.0 / s                                           # duenner Saum (7 px bei einem Korn von ~570 px)
        inner = [Q(x * (1 - rim), y * (1 - rim)) for x, y in shape]
        d.polygon(outer, fill=o.rgb(COAT))
        d.polygon(inner, fill=o.rgb(QUARTZ))
        rnd = random.Random(5)                                  # muschelige Bruchlinien im Quarz (neutral)
        for _ in range(7):
            ax, ay = rnd.uniform(-0.6, 0.6), rnd.uniform(-0.55, 0.55); rr = rnd.uniform(0.15, 0.35)
            a0 = rnd.uniform(0, 360)
            bx = [Q(ax - rr, ay - rr * 0.7)[0], Q(ax - rr, ay - rr * 0.7)[1], Q(ax + rr, ay + rr * 0.7)[0], Q(ax + rr, ay + rr * 0.7)[1]]
            d.arc(bx, a0, a0 + 110, fill=o.rgb(rnd.choice([QUARTZ_D, QUARTZ_L]), 200), width=int(2.5 * o.S))
        d.line(outer + [outer[0]], fill=o.rgb(COAT_D), width=int(2 * o.S))
    small = im.resize((size, size), Image.LANCZOS)
    return m.Sprite(small, x0, y0)


# ------------------------------------------------------------------ Meta
META = dict(
    slug="2026-11-24_scalejump-02", dur_range=[18.0, 24.0], payoff_t=T_P, abspann_ab=T_END,
    title="GeoCrimps r014 SCALE JUMP #02 (Offene Frage)", ablauf="offene_frage",
    hook1_bis=T_OUT, hook_ab=T_Q, hook_bis=T_HOOK, weitere_fragen=[[T_S2, T1_OFF]], cover_t=round(T_Q + 0.85, 2),
    on_screen=["SCALE JUMP", "RED SANDSTONE:", "WHAT COLOUR ARE THE GRAINS?", "RED, RIGHT?", "BUT CUT ONE OPEN…",
               "MOSTLY PALE GREY.", "THE RED IS SKIN-DEEP.", rk.Outro.CTA],
    labels=[],
    verdauen=["MOSTLY PALE GREY.", "THE RED IS SKIN-DEEP."],
    qc_times=[0.0, T_GRAB, T_GEO, 0.9, round(T_Q + 0.85, 2), round(T_HOOK - 0.3, 2), round(J1_0 + 0.5, 2), round(T1_OFF - 0.3, 2),
              round(J2_0 + 0.5, 2), round(T_CUT1, 2), round(T_P + 0.6, 2), round(T_ANS_OFF - 0.3, 2), round(T_GLOW + 0.5, 2),
              round(J3_1 + 0.3, 2), round(T_END - 0.2, 2), round(T_END + 2.0, 2)],
    marks=[(0, "Hook 1"), (T_GRAB, "Griff"), (T_GEO, "x GEOLOGY"), (T_Q, "Hook 2"), (J1_0, "Lupe"), (T_S2, "Zug 1"),
           (J2_0, "Sprung"), (T_S3, "Zug 2"), (T_CUT0, "Schnitt"), (T_P, "PAYOFF"), (T_FAZ, "Fazit"), (J3_0, "Lupe zu"),
           (T_END, "Abspann")])


# ------------------------------------------------------------------ Reel
class Reel(rk.ReelBase):
    DUR = DUR

    def __init__(self):
        super().__init__()
        self.rail = rk.Rail(2)
        self.outro = rk.Outro()
        self.rails = [rk.rail_sprite(k, 2) for k in range(3)] + [rk.rail_sprite(2, 2, logo_on=True)]
        self.hook1 = rk.Hook1(t_grab=T_GRAB, t_geo=T_GEO, t_out=T_OUT)
        self.climber = kl.Climber(scale=1.0, width=18.0, torso_w=36.0)
        self.label = m.text_sprite("SCALE JUMP", X0, rk.FORMAT_Y, "stencil", 40, C["slate"], tracking=0.12)
        self.build_wall()
        # Kornwelt: Lupe (Zug 1) und ein Korn (Zug 2)
        self.field1 = self.render_field(S1, LC[0], LC[1], w_line=1.6)
        self.field2 = self.render_field(S2, GC[0], GC[1], skip_target=True, w_line=3.0)
        self.g_closed = grain_sprite(S2, GC[0], GC[1], opened=False)
        self.g_open = grain_sprite(S2, GC[0], GC[1], opened=True)
        self.shade = m.sprite(self._shade)
        # Texte
        self.hook_kick = m.text_sprite("RED SANDSTONE:", X0, rk.HOOK_Y, "display", 96, ROCK_L)
        self.hook, _ = m.lines_sprite(["WHAT COLOUR ARE", "THE GRAINS?"], rk.HOOK_Y + 112, size=136)
        self.text1, _ = m.lines_sprite(["RED,", "RIGHT?"], 352, role="display_xb", size=118)
        self.text2, _ = m.lines_sprite(["BUT CUT", "ONE OPEN…"], 352, role="display_xb", size=118)
        self.answer, _ = m.lines_sprite(["MOSTLY", "PALE GREY."], 352, size=200)
        self.fazit, _ = m.lines_sprite(["THE RED IS", "SKIN-DEEP."], 400, size=150)

    @staticmethod
    def render_field(s, cx, cy, skip_target=False, w_line=2.0):
        im = o.canvas()
        draw_field(im, s, cx, cy, skip_target, w_line)
        return im.resize((W, H), Image.LANCZOS)

    @staticmethod
    def _shade(im):
        """Dunkler Verlauf hinter den Texten (Lesbarkeit ueber dem Kornfeld)."""
        yy = np.arange(H * o.S) / o.S
        col = np.clip(np.where(yy < 700, 1.0, 1 - (yy - 700) / 200), 0, 1) * np.clip((yy - 200) / 120, 0, 1)
        a = np.repeat((col * 200)[:, None], W * o.S, axis=1).astype(np.uint8)
        lay = Image.new("RGBA", im.size, o.rgb(C["obsidian"])); lay.putalpha(Image.fromarray(a))
        im.alpha_composite(lay)

    # -------------------------------------------------------------- Wand
    def build_wall(self):
        wall = o.ragged(-20, TOP, 1100, YG, seed=21, amp=12, n=26, top_only=True)
        self.wall_poly = wall

        def bg(im):
            o.contour_field(im, 840, 520, n=8, r0=110, step=60, alpha=70)
            d = ImageDraw.Draw(im)
            d.polygon([P(x, y) for x, y in wall], fill=o.rgb(ROCK))
            mask = Image.new("L", im.size, 0); ImageDraw.Draw(mask).polygon([P(x, y) for x, y in wall], fill=255)
            xx = np.mgrid[0:im.size[1], 0:im.size[0]][1].astype(np.float32) / o.S
            sh = Image.new("RGBA", im.size, o.rgb(C["obsidian"]))
            sh.putalpha(Image.fromarray((np.asarray(mask, np.float32) * np.clip((xx - 520) / 900, 0, 1) * 0.5).astype(np.uint8)))
            im.alpha_composite(sh)
            rnd = random.Random(4)
            for _ in range(700):                                  # feine neutrale Koernung
                x = rnd.uniform(0, 1080); y = rnd.uniform(TOP + 14, YG - 4); r = rnd.uniform(1.0, 2.0)
                d.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=o.rgb(rnd.choice([ROCK_D, ROCK_L]), 120))
            for k, y0 in enumerate(range(960, YG, 126)):          # flache Baenke, schwach
                pts = [P(x, y0 + 5 * math.sin(x / 150 + k)) for x in range(-20, 1101, 20)]
                d.line(pts, fill=o.rgb(ROCK_D, 130), width=int(2 * o.S))
            for (hx, hy), w_ in ((EDGE, 62), (HIGH, 52), (FOOT_L, 34), (FOOT_R, 34), (FOOT_L2, 30), (FOOT_R2, 30)):
                d.rectangle([P(hx - w_ / 2, hy + 4), P(hx + w_ / 2, hy + 12)], fill=o.rgb("#5A2618"))
                d.line([P(hx - w_ / 2, hy + 3), P(hx + w_ / 2, hy + 3)], fill=o.rgb(ROCK_L), width=int(4 * o.S))
            o.pocket(im, POCKET[0] - 2, POCKET[1] + 8, 24, 14, rim=ROCK_L)
            d.line([P(x, y) for x, y in wall[:27]], fill=o.rgb(ROCK_L), width=int(3 * o.S))
            lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
            ImageDraw.Draw(lay).rectangle([P(-10, YG), P(1090, 1930)], fill=o.rgb(C["graphite"], 255))
            im.alpha_composite(lay)
            d.line([P(-10, YG), P(1090, YG)], fill=o.rgb(C["slate"]), width=int(3 * o.S))
            kl.crash_pad(im, 110, 470, YG + 4, h=40)
        self.wall_bg = m.background(bg)
        beds = [[(x, y0 + 5 * math.sin(x / 150 + k)) for x in range(-20, 1101, 20)] for k, y0 in enumerate(range(960, YG, 126))]
        self.geo = kl.GeoReveal(wall, "sandstone", EDGE[0], EDGE[1], color=C["magnesia"], pat_alpha=105, beds=beds, seed=8)
        # Lupenkreis: Ring um die Leiste und Verbindungslinien (Tangenten) zur Lupe
        hx, hy = EDGE[0] + 8, EDGE[1] + 6; hr = 30
        dx, dy = LC[0] - hx, LC[1] - hy; dist = math.hypot(dx, dy); base = math.atan2(dy, dx)
        off = math.asin((LR - hr) / dist)
        def call(im):
            d = ImageDraw.Draw(im); col = o.rgb(C["magnesia"], 230)
            d.ellipse([P(hx - hr, hy - hr), P(hx + hr, hy + hr)], outline=col, width=int(4 * o.S))
            for sgn in (1, -1):
                a = base + sgn * (math.pi / 2 + off)
                p1 = (hx + hr * math.cos(a), hy + hr * math.sin(a)); p2 = (LC[0] + LR * math.cos(a), LC[1] + LR * math.sin(a))
                d.line([P(*p1), P(*p2)], fill=o.rgb(C["magnesia"], 150), width=int(3 * o.S))
        self.callout = m.sprite(call)

    def wall(self, t):
        f = self.wall_bg.copy()
        u = seilzug(seg(t, T_GEO, 0.5))
        if u > 0 and t < T_OUT + 0.4:
            self.geo.put(f, u, fade=1 - seg(t, T_OUT, 0.4))
        if t >= T_OUT:                                            # Sandkoerner rieseln im Licht (Bewegung ohne Info)
            dr = ImageDraw.Draw(f); rnd = random.Random(31)
            for _ in range(20):
                x0 = rnd.uniform(80, 1000); y0 = rnd.uniform(TOP + 40, YG - 60); sp = rnd.uniform(14, 32)
                y = TOP + 20 + ((y0 - TOP + sp * (t - T_OUT)) % (YG - TOP - 40))
                x = x0 + 8 * math.sin(t * 0.9 + x0)
                dr.ellipse([x - 1.6, y - 1.6, x + 1.6, y + 1.6], fill=o.rgb(ROCK_L, 150))
        put(f, self.climber.sprite(climber_pose(t)))
        kl.chalk_puff(f, t, T_GRAB, EDGE[0], EDGE[1] - 4, seed=11)
        kl.chalk_puff(f, t, T_PULL + 0.85, HIGH[0], HIGH[1] - 4, seed=15, size=0.8)
        return f

    def lens_inset(self, f, t, r, op=1.0):
        """Lupenkreis (Zug 1) auf der Wand: Kornfeld mit langsamer Drift, Rand, Verbindungslinien."""
        if r <= 1:
            return
        drift = 0.4 * seg(t, J1_0, J2_1 - J1_0)
        inner = self.field1 if drift < 0.01 else m.zoomed(self.field1, 1 + 0.06 * drift, *LC)
        mk = Image.new("L", (W, H), 0)
        ImageDraw.Draw(mk).ellipse([LC[0] - r, LC[1] - r, LC[0] + r, LC[1] + r], fill=int(255 * op))
        f.paste(Image.composite(inner, f, mk), (0, 0))
        put(f, self.callout, op=op * min(1.0, r / LR))
        ImageDraw.Draw(f).ellipse([LC[0] - r, LC[1] - r, LC[0] + r, LC[1] + r], outline=o.rgb(C["magnesia"], int(235 * op)), width=5)

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

    # -------------------------------------------------------------- ein Korn (Zug 2, Payoff, Fazit)
    def grain_view(self, t):
        z = 1 + 0.035 * seg(t, J2_1, T_P - J2_1)                  # langsamer Push-in
        if t >= T_P:
            z = 1.035 * lerp(1.0, 1.05, 0.5 - 0.5 * math.cos(math.pi * seg(t, T_P, T_END - T_P)))
        f = self.field2.copy()
        if t < T_P:
            tr = 1.5 * math.sin(t * 60) * seg(t, T_RISE + 0.5, 0.6)     # Korn zittert vor dem Bruch
            put(f, self.g_closed, dx=tr)
            u = seilzug(seg(t, T_CUT0, T_CUT1 - T_CUT0))            # Schnittlinie (gestrichelt) zieht sich darueber
            if u > 0:
                x0, x1 = GC[0] - 1.3 * S2, GC[0] + 1.3 * S2; xe = lerp(x0, x1, u)
                glow = seg(t, T_RISE, T_P - T_RISE)
                d = ImageDraw.Draw(f); x = x0
                while x < xe:
                    d.line([(x, GC[1]), (min(xe, x + 22), GC[1])], fill=o.rgb(C["magnesia"], int(lerp(200, 255, glow))),
                           width=int(lerp(4, 7, glow)))
                    x += 36
        else:
            v = seg(t, T_P, 0.3)
            gap = lerp(0, 40, seilzug(v)) + 6 * seg(t, T_P + 0.3, T_END - T_P - 0.3)
            spr = self.g_open if v >= 0.5 else self.g_closed
            cut = int(GC[1] - spr.y)
            top = m.Sprite(spr.img.crop((0, 0, spr.w, cut)), spr.x, spr.y)
            bot = m.Sprite(spr.img.crop((0, cut, spr.w, spr.h)), spr.x, spr.y + cut)
            put(f, top, dy=-gap / 2, dx=-gap * 0.15); put(f, bot, dy=gap / 2, dx=gap * 0.15)
            if v < 0.5:
                ImageDraw.Draw(f).line([(GC[0] - 1.3 * S2, GC[1]), (GC[0] + 1.3 * S2, GC[1])],
                                       fill=o.rgb(C["magnesia"], int(255 * (1 - 2 * v))), width=7)
            if t >= T_GLOW:                                        # der Saum leuchtet (ruhiger Puls)
                w = seg(t, T_GLOW, 0.5) * (0.6 + 0.4 * math.sin(2 * math.pi * (t - T_GLOW) / 1.1))
                shape = GRAINS[0]["shape"]
                d = ImageDraw.Draw(f)
                for half, sgn in ((top, -1), (bot, 1)):
                    pts = [(GC[0] + x * S2 + sgn * gap * 0.15, GC[1] + y * S2 + sgn * gap / 2) for x, y in shape
                           if (y < 0) == (sgn < 0)]
                    if len(pts) > 2:
                        pts.sort(key=lambda q: math.atan2(q[1] - GC[1] - sgn * gap / 2, q[0] - GC[0]))
                        d.line(pts, fill=o.rgb(C["heat"], int(230 * w)), width=6, joint="curve")
        if z > 1.001:
            f = m.zoomed(f, z, GC[0], GC[1] - 200)
        put(f, self.shade)
        return f

    # -------------------------------------------------------------- Frames
    def frame(self, t):
        if t < J2_0:                                              # Hook und Zug 1 an der Wand
            f = m.zoomed(self.wall(t), 1 + 0.03 * seilzug(seg(t, 0, J2_0)), 520, 1100)
            if t >= J1_0:
                r = lerp(0, LR, seilzug(seg(t, J1_0, J1_1 - J1_0)))
                self.lens_inset(f, t, r)
            put(f, self.rails[1] if t >= T_S2 else self.rails[0]); self.rail.pop(f, t, 0, T_S2)
            self.hook1.draw(f, t, hook_bis=T_HOOK)
            u = seilzug(seg(t, T_Q, EIN))
            if u > 0 and t < T_HOOK + 0.15:
                fade = 1 - seg(t, T_HOOK, 0.12)
                put(f, self.label, dx=lerp(-30, 0, u), op=u * fade)
                put(f, self.hook_kick, dx=lerp(-40, 0, u), op=u * fade)
                put(f, self.hook, dx=lerp(-40, 0, u), op=u * fade)
            u = seilzug(seg(t, T_S2, EIN)); put(f, self.text1, dx=lerp(-40, 0, u), op=u * (1 - seg(t, T1_OFF, 0.25)))
            return f, 141
        if t < J3_0:                                              # Sprung 2, Zug 2, Payoff, Fazit (ein Korn)
            inner = self.grain_view(t)
            if t < J2_1 + 0.02:
                u = 0.5 - 0.5 * math.cos(math.pi * seg(t, J2_0, J2_1 - J2_0))
                outer = self.wall(t); self.lens_inset(outer, t, LR)
                outer = m.zoomed(outer, lerp(1.03, JUMP_Z, u), *LC)
                f = self.lens(outer, inner, lerp(0, 2300, u ** 1.6), LC)
            else:
                f = inner
            put(f, self.rails[3] if t >= T_P else self.rails[2] if t >= T_S3 else self.rails[1])
            self.rail.pop(f, t, 1, T_S3)
            u = seilzug(seg(t, T_S3, EIN)); put(f, self.text2, dx=lerp(-40, 0, u), op=u * (1 - seg(t, T2_OFF, 0.25)))
            u = seg(t, T_P, 0.3)
            if u > 0:
                self.rail.logo_pop(f, t, T_P)
                put(f, self.answer, op=min(1, u * 2) * (1 - seg(t, T_ANS_OFF, 0.2)), scale=lerp(1.18, 1.0, seilzug(u)),
                    anchor=(X0, 352))
            u = seilzug(seg(t, T_FAZ, EIN)); put(f, self.fazit, dx=lerp(-40, 0, u), op=u)
            return f, 142
        if t < T_END:                                             # Fazit: Lupenkreis schliesst sich auf die Leiste
            u = 0.5 - 0.5 * math.cos(math.pi * seg(t, J3_0, J3_1 - J3_0))
            outer = m.zoomed(self.wall(t), lerp(JUMP_Z, 1.03, u), *EDGE)
            f = self.lens(outer, self.grain_view(t), lerp(2300, 0, u) * (1 - u) ** 0.6, EDGE) if t < J3_1 else outer
            put(f, self.rails[3])
            put(f, self.fazit)
            return f, 143
        return self.outro.frame(t, T_END), 144


# ------------------------------------------------------------------ Ton: Musik in H-Moll, 77 BPM, Aufloesung nach D-Dur
BM9, GMAJ7, D_, A_, EM7, FS_SUS4, FS7, BM7 = (
    [47, 50, 54, 57, 61], [55, 59, 62, 66], [50, 54, 57, 62], [49, 52, 57, 61], [52, 55, 59, 62], [54, 59, 61],
    [54, 58, 61, 64], [50, 54, 57, 59])
PENTA = [71, 74, 76, 78, 81, 83, 86]                          # H-Moll-Pentatonik ab H4


def sound_events(b):
    """Musik in H-Moll (77 BPM) nach Szenen, Hook 1 musikalisch, Lupe und Sprung als anschwellende Flaeche mit Zupfton,
    Schnittlinie als leise steigende Toene, Aufbrechen als weicher Akkordschlag mit leisem Knacken, der leuchtende Saum
    als ruhige Toene, Fazit nach D-Dur aufgeloest, Klanglogo im Abspann."""
    h1 = rk.Hook1(t_grab=T_GRAB, t_geo=T_GEO, t_out=T_OUT)
    b.hook1(h1, akkord=BM9, bassnote=47)
    b.musik([
        (T_Q - 0.1, T_Q + 1.9, BM9, 47, "ruhig"),                 # Frage: offen
        (T_Q + 1.9, J1_0, GMAJ7, 43, "ruhig"),
        (J1_0, T_S2, EM7, 40, "flaeche"),                         # Lupe oeffnet sich
        (T_S2, T1_OFF, BM7, 47, "ruhig"),                         # "RED, RIGHT?": Bedenkzeit
        (T1_OFF, J2_1, GMAJ7, 43, "flaeche"),                     # Sprung auf ein Korn
        (J2_1, T_RISE, EM7, 40, "bewegt"),                        # Schnitt
        (T_RISE, T_P - 0.15, FS_SUS4, 42, "steigend"),            # Steigerung, dann 0,15 s Stille
        (T_P, T_ANS_OFF, BM9, 47, "flaeche"),                     # Aufloesung: verdauen
        (T_ANS_OFF, T_FAZ + 1.4, GMAJ7, 43, "ruhig"),             # Fazit ...
        (T_FAZ + 1.4, T_END, D_, 38, "ruhig"),                    # ... nach D-Dur aufgeloest
        (T_END, DUR, D_, 38, "flaeche"),                          # Abspann
    ], bpm=77.0, gain=-12.0)
    for t0, t1, ak, mm in ((J1_0, J1_1, EM7, 76), (J2_0, J2_1, GMAJ7, 78)):
        b.ton("schwelle", t0, -14.0, "lupe", akkord=ak, dauer=t1 - t0)
        b.ton("zupf", t1, -13.0, "lupe-landung", m=mm, dauer=1.0)
    b.synth("whoosh", J2_0 + 0.2, -22.0, "sprung", dur=0.55, seed=5)
    b.ton("zupf", T_S2, -14.0, "bohrhaken", m=74, dauer=0.9)
    b.ton("zupf", T_S2 + 0.05, -11.0, "frage", m=71, dauer=0.9)  # Frage: steigende Quarte
    b.ton("zupf", T_S2 + 0.25, -11.0, "frage", m=76, dauer=1.2)
    b.ton("zupf", T_S3, -14.0, "bohrhaken", m=78, dauer=0.9)
    for k in range(5):                                           # Schnittlinie: leise steigende Toene
        b.ton("zupf", T_CUT0 + 0.24 * k, -19.0, "schnitt", m=PENTA[k], dauer=0.6, pan=0.3 * (k / 2 - 1))
    b.ton("schwelle", T_RISE, -8.0, "steigerung", akkord=FS_SUS4, dauer=T_P - 0.15 - T_RISE)
    b.klang("sub_hit", T_P - 0.01, -11.0, "payoff-einschlag", f0=78.0, f1=36.0)
    b.klang("crunch", T_P + 0.01, -20.0, "korn-bricht", seed=6)
    b.ton("akzent", T_P, -4.0, "payoff", akkord=BM9, bassnote=47)
    for k in range(3):                                           # Saum leuchtet: ruhige Toene
        b.ton("zupf", T_GLOW + 0.5 + 1.1 * k, -18.0, "saum", m=(78, 81, 86)[k], dauer=0.9)
    b.ton("zupf", T_FAZ, -14.0, "fazit", m=74, dauer=0.9)
    b.ton("schwelle", J3_0, -16.0, "lupe-zu", akkord=D_, dauer=J3_1 - J3_0)
    b.klang("chalk_slap", T_PULL + 0.85, -12.0, "griff", seed=2)
    b.klanglogo(T_END + 0.3, tonika=62, gain=-7.0)               # Abspann: Logo (D-Dur)
    b.ton("zupf", T_END + 1.3, -12.0, "herz", m=78, dauer=1.2)


if __name__ == "__main__":
    if "--reach" in sys.argv:
        print(check_reach())
        sys.exit(0)
    rk.run(Reel, sound_events, META)
