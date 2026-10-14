#!/usr/bin/env python3
"""GeoCrimps V2 -- Hook 1 "CLIMBING x GEOLOGY" (seit 14.10.2026, Wunsch Markus 13.10.: "hook 1 (klettern und geologie)
und dann hook 2 (eigentliches reel thema)").

Erkenntnisse dahinter: Reel #1 verlor 26 % der Zuschauer in der ersten Sekunde, und bei Reel #2 war am Anfang nicht klar,
worum es geht. Hook 1 sagt deshalb in ~1,6 s, wo man gelandet ist: ein Kletterer greift DEN Griff dieses Reels
("CLIMBING", Kreide-Klatscher), dann oeffnet sich eine Lupe in den Fels ("x GEOLOGY", Basseinschlag). Danach stellt
Hook 2 die eigentliche Frage. Jedes Reel zeigt dabei seinen eigenen Fels und Griff, kein gleicher Vorspann.

Bausteine:  Climber (Piktogramm mit Inverser Kinematik), chalk_puff, Lens, Words (CLIMBING in Kreide, GEOLOGY in
Schichtfarben ICS), Zeitplan-Konstanten und sound(book, ...) fuer den Ton von Hook 1.
"""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import outcrop as o
import motion as m
from outcrop import C, P
from motion import W, H, X0, seg, seilzug, sturz, griff, lerp, put

# ------------------------------------------------------------------ Zeitplan Hook 1 (Sekunden ab Reel-Start)
T_REACH = 0.38          # Hand erreicht den Griff (Kreide-Klatscher)
T_GEO = 0.50            # "x GEOLOGY" schlaegt ein, Lupe oeffnet sich
T_OUT = 1.40            # Woerter gehen, Kamera faehrt, Frage kommt
T_Q = 1.50              # Frage (Hook 2) beginnt einzublenden
SHIFT = 1.70            # um so viel verschieben sich alle alten Zeiten eines Reels
WORDS = ("CLIMBING", "GEOLOGY")
STRATA = ["#FFE619", "#FD9A52", "#7FC64E", "#34B2C9"]   # Neogen, Palaeogen, Kreide, Jura (ICS/CGMW), jung oben


# ------------------------------------------------------------------ Kletterer-Piktogramm (Rueckenansicht, an der Wand)
BODY = dict(head_r=26, neck=14, torso=150, sh=40, hip=22, ua=86, fa=80, th=104, sn=98,
            w_torso=46, w_arm=22, w_leg=27, w_out=7)


def _ik(root, target, a, b, bend):
    """Zwei-Glieder-Kinematik: Gelenk (Ellbogen/Knie) und erreichbarer Endpunkt."""
    dx, dy = target[0] - root[0], target[1] - root[1]
    d = math.hypot(dx, dy)
    dd = max(abs(a - b) + 1e-3, min(a + b - 1e-3, d))
    base = math.atan2(dy, dx)
    A = math.acos(max(-1.0, min(1.0, (a * a + dd * dd - b * b) / (2 * a * dd))))
    th = base + bend * A
    return (root[0] + a * math.cos(th), root[1] + a * math.sin(th)), (root[0] + dd * math.cos(base), root[1] + dd * math.sin(base))


def lerp_pose(p, q, u):
    out = {}
    for k in p:
        a, b = p[k], q[k]
        out[k] = tuple(lerp(x, y, u) for x, y in zip(a, b)) if isinstance(a, tuple) else lerp(a, b, u)
    return out


def skeleton(pose, s=1.0):
    """pose: pelvis (x, y), lean (rad), hand_l, hand_r, foot_l, foot_r (Ziele) -> Gelenkpunkte."""
    B = {k: v * s for k, v in BODY.items()}
    px, py = pose["pelvis"]; lean = pose.get("lean", 0.0)
    up = (math.sin(lean), -math.cos(lean)); rt = (math.cos(lean), math.sin(lean))
    neck = (px + up[0] * B["torso"], py + up[1] * B["torso"])
    head = (neck[0] + up[0] * (B["neck"] + B["head_r"]), neck[1] + up[1] * (B["neck"] + B["head_r"]))
    sh_l = (neck[0] - rt[0] * B["sh"], neck[1] - rt[1] * B["sh"]); sh_r = (neck[0] + rt[0] * B["sh"], neck[1] + rt[1] * B["sh"])
    hp_l = (px - rt[0] * B["hip"], py - rt[1] * B["hip"]); hp_r = (px + rt[0] * B["hip"], py + rt[1] * B["hip"])
    el_l, ha_l = _ik(sh_l, pose["hand_l"], B["ua"], B["fa"], pose.get("bend_el_l", -1))
    el_r, ha_r = _ik(sh_r, pose["hand_r"], B["ua"], B["fa"], pose.get("bend_el_r", 1))
    kn_l, ft_l = _ik(hp_l, pose["foot_l"], B["th"], B["sn"], pose.get("bend_kn_l", 1))
    kn_r, ft_r = _ik(hp_r, pose["foot_r"], B["th"], B["sn"], pose.get("bend_kn_r", -1))
    return dict(B=B, pelvis=(px, py), neck=neck, head=head, sh_l=sh_l, sh_r=sh_r, hp_l=hp_l, hp_r=hp_r,
                el_l=el_l, ha_l=ha_l, el_r=el_r, ha_r=ha_r, kn_l=kn_l, ft_l=ft_l, kn_r=kn_r, ft_r=ft_r)


def draw_climber(d, X, Y, pose, s=1.0, fill=C["magnesia"], line=C["obsidian"]):
    """Zeichnet das Piktogramm mit ImageDraw d; X/Y rechnen Bildkoordinaten in Flaechen-Pixel um (2x)."""
    k = skeleton(pose, s); B = k["B"]; S2 = o.S
    def seg_(a, b, w, col):
        d.line([(X(a[0]), Y(a[1])), (X(b[0]), Y(b[1]))], fill=o.rgb(col), width=int(w * S2))
        for q in (a, b):                                               # runde Enden
            r = w * S2 / 2; d.ellipse([X(q[0]) - r, Y(q[1]) - r, X(q[0]) + r, Y(q[1]) + r], fill=o.rgb(col))
    def dot(c, r, col):
        d.ellipse([X(c[0]) - r * S2, Y(c[1]) - r * S2, X(c[0]) + r * S2, Y(c[1]) + r * S2], fill=o.rgb(col))
    def shoe(ft, kn, col, extra):
        dx = ft[0] - kn[0]; sgn = 1 if dx >= 0 else -1
        seg_((ft[0] - sgn * 6, ft[1]), (ft[0] + sgn * 26 * s, ft[1] + 4 * s), B["w_leg"] * 0.62 + extra, col)
    for pas, col, ex in ((0, line, 2 * B["w_out"]), (1, fill, 0)):       # erst Umriss (Obsidian), dann Flaeche
        for a, b in (("hp_l", "kn_l"), ("kn_l", "ft_l"), ("hp_r", "kn_r"), ("kn_r", "ft_r")):
            seg_(k[a], k[b], B["w_leg"] + ex, col)
        shoe(k["ft_l"], k["kn_l"], col, ex); shoe(k["ft_r"], k["kn_r"], col, ex)
        seg_(k["pelvis"], ((k["neck"][0] + k["pelvis"][0]) / 2, (k["neck"][1] + k["pelvis"][1]) / 2), B["w_torso"] * 1.02 + ex, col)
        seg_(((k["neck"][0] + k["pelvis"][0]) / 2, (k["neck"][1] + k["pelvis"][1]) / 2), k["neck"], B["w_torso"] + ex, col)
        seg_(k["sh_l"], k["sh_r"], B["w_arm"] + 4 + ex, col)
        for a, b in (("sh_l", "el_l"), ("el_l", "ha_l"), ("sh_r", "el_r"), ("el_r", "ha_r")):
            seg_(k[a], k[b], B["w_arm"] + ex, col)
        dot(k["ha_l"], B["w_arm"] * 0.66 + ex / 2, col); dot(k["ha_r"], B["w_arm"] * 0.66 + ex / 2, col)
        dot(k["head"], B["head_r"] + ex / 2, col)
    # Gurt und Chalkbag (Rueckenansicht): kleine Details, die "Klettern" sagen
    px, py = k["pelvis"]
    d.line([(X(k["hp_l"][0] - 4), Y(k["hp_l"][1] - 10)), (X(k["hp_r"][0] + 4), Y(k["hp_r"][1] - 10))],
           fill=o.rgb(line), width=int(5 * S2))
    d.rounded_rectangle([X(px - 13 * s), Y(py - 2 * s), X(px + 13 * s), Y(py + 26 * s)], radius=int(6 * S2),
                        fill=o.rgb(C["slate"]), outline=o.rgb(line), width=int(4 * S2))
    return k


def climber_sprite(pose, s=1.0, dy=0.0, margin=60):
    """Piktogramm als 1x-Sprite (in 2x gezeichnet), dy verschiebt mit der Kamera."""
    k = skeleton(pose, s)
    pts = [v for key, v in k.items() if key != "B"]
    x0 = min(p[0] for p in pts) - margin; x1 = max(p[0] for p in pts) + margin
    y0 = min(p[1] for p in pts) - margin; y1 = max(p[1] for p in pts) + margin
    x0, y0, x1, y1 = int(x0), int(y0 + dy), int(math.ceil(x1)), int(math.ceil(y1 + dy))
    w, h = max(1, x1 - x0), max(1, y1 - y0)
    im = Image.new("RGBA", (w * o.S, h * o.S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    draw_climber(d, lambda x: (x - x0) * o.S, lambda y: (y + dy - y0) * o.S, pose, s)
    return m.Sprite(im.resize((w, h), Image.LANCZOS), x0, y0), k


def holds(im, pts, dy=0.0):
    """Kleine Tritte/Griffe (Leiste mit Schatten) an den Punkten (x, y, Breite) -- in 2x auf im."""
    d = ImageDraw.Draw(im)
    for x, y, w in pts:
        y = y + dy
        d.polygon([P(x - w / 2, y), P(x + w / 2, y - 3), P(x + w / 2 + 4, y + 9), P(x - w / 2 - 3, y + 11)], fill=o.rgb(C["obsidian"], 220))
        d.line([P(x - w / 2, y), P(x + w / 2, y - 3)], fill=o.rgb(C["magnesia"]), width=int(3 * o.S))


# ------------------------------------------------------------------ Kreidewolke beim Zugreifen
def chalk_puff(f, t, t0, x, y, seed=11, n=46, dur=0.75):
    v = (t - t0) / dur
    if not 0 < v < 1:
        return
    dr = ImageDraw.Draw(f); rnd = random.Random(seed)
    for _ in range(n):
        ang = rnd.uniform(-math.pi, 0.15) if rnd.random() < 0.8 else rnd.uniform(0, math.pi)
        sp = rnd.uniform(50, 230); r0 = rnd.uniform(1.8, 5.5)
        e = 1 - (1 - v) ** 2
        qx = x + math.cos(ang) * sp * e * 0.55; qy = y + math.sin(ang) * sp * e * 0.55 - 30 * v
        r = r0 * (1 + 1.6 * v)
        dr.ellipse([qx - r, qy - r, qx + r, qy + r], fill=o.rgb(C["magnesia"], int(190 * (1 - v) ** 1.3)))


# ------------------------------------------------------------------ Lupe in den Fels (10x)
class Lens:
    """Kreisrunder Blick ins Gestein. view: RGBA-Bild 2R x 2R (1x), zentriert gezeichnet; die Lupe oeffnet sich als Iris."""
    def __init__(self, view, R):
        self.view, self.R = view, R
        lab = Image.new("RGBA", (120 * o.S, 50 * o.S), (0, 0, 0, 0))
        o.text(lab, 0, 0, "10×", "mono", 26, C["magnesia"])
        self.label = lab.resize((120, 50), Image.LANCZOS)

    def draw(self, f, cx, cy, r, alpha=1.0, label=True):
        if r < 2 or alpha <= 0.01:
            return
        R = self.R; s = o.S
        x0, y0 = int(round(cx - R)), int(round(cy - R))
        mk = Image.new("L", (2 * R * s, 2 * R * s), 0)
        ImageDraw.Draw(mk).ellipse([(R - r) * s, (R - r) * s, (R + r) * s, (R + r) * s], fill=int(255 * alpha))
        mk = mk.resize((2 * R, 2 * R), Image.LANCZOS)
        v = self.view.copy(); v.putalpha(Image.fromarray(np.minimum(np.asarray(v.getchannel("A")), np.asarray(mk))))
        m.composite(f, v, x0, y0)
        ring = Image.new("RGBA", ((2 * R + 40) * s, (2 * R + 40) * s), (0, 0, 0, 0)); d = ImageDraw.Draw(ring)
        c = (R + 20) * s; col = o.rgb(C["magnesia"], int(255 * alpha))
        d.ellipse([c - r * s, c - r * s, c + r * s, c + r * s], outline=col, width=int(5 * s))
        d.ellipse([c - (r + 9) * s, c - (r + 9) * s, c + (r + 9) * s, c + (r + 9) * s], outline=o.rgb(C["magnesia"], int(90 * alpha)), width=int(2 * s))
        for a in (0, 90, 180, 270):
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            d.line([(c + ca * (r - 16) * s, c + sa * (r - 16) * s), (c + ca * (r + 2) * s, c + sa * (r + 2) * s)], fill=col, width=int(4 * s))
        ring = ring.resize((2 * R + 40, 2 * R + 40), Image.LANCZOS)
        m.composite(f, ring, x0 - 20, y0 - 20)
        if label and r > R * 0.7:
            lb = self.label.copy(); lb.putalpha(lb.getchannel("A").point(lambda q: int(q * alpha * seg(r, R * 0.7, R * 0.3))))
            m.composite(f, lb, int(cx + r * 0.72 + 8), int(cy + r * 0.72 - 6))


def vein_view(R, angle_deg, half, seed=7, qz=("#DAD5CA", "#A9A395", ["#E4DFD5", "#D1CBBF", "#DEDACF", "#CBC5B9", "#E8E4DB"]),
              mag=2.2, offset=0.0):
    """Lupen-Inhalt fuer einen Quarzgang: neutrales Wirtsgestein (grobe Koerner) und Quarzkristalle, die von beiden
    Gangwaenden nach innen wachsen und sich in der Mitte treffen (wie in #029 belegt). Vergroessert um mag."""
    s = o.S; N = 2 * R * s
    im = Image.new("RGBA", (N, N), o.rgb(C["graphite"])); d = ImageDraw.Draw(im); rnd = random.Random(seed)
    for _ in range(int(N * N / (380 * s * s))):                      # Wirtsgestein: grobe Koerner
        x, y = rnd.uniform(0, N), rnd.uniform(0, N); r = rnd.uniform(5, 15) * s; k = rnd.randint(5, 7); a0 = rnd.uniform(0, 6.28)
        col = rnd.choice([C["line"], "#353E46", "#4A545D", "#272E35", "#3B444C", C["slate"]])
        d.polygon([(x + r * rnd.uniform(0.6, 1.0) * math.cos(a0 + 2 * math.pi * j / k),
                    y + r * rnd.uniform(0.6, 1.0) * math.sin(a0 + 2 * math.pi * j / k)) for j in range(k)], fill=o.rgb(col))
    a = math.radians(angle_deg); ux, uy = math.cos(a), math.sin(a); nx, ny = -uy, ux
    c0 = (R * s + nx * offset * s, R * s + ny * offset * s)
    hw = half * mag * s
    def P2(t, n):                                                   # Gangkoordinaten (laengs t, quer n) -> Pixel
        return (c0[0] + ux * t + nx * n, c0[1] + uy * t + ny * n)
    L = N * 1.6
    QZ, QZ_EDGE, PATCH = qz
    d.polygon([P2(-L, -hw), P2(L, -hw), P2(L, hw), P2(-L, hw)], fill=o.rgb(QZ))
    for side in (-1, 1):                                            # Kristalle von der Wand nach innen
        t = -L
        while t < L:
            w = rnd.uniform(16, 30) * s; ln = hw * rnd.uniform(0.85, 1.12); tilt = rnd.uniform(-0.18, 0.18)
            base = side * hw; tip_n = base - side * ln
            b0 = P2(t - w / 2, base); b1 = P2(t + w / 2, base)
            s0 = P2(t - w / 2 + tilt * ln * 0.7, base - side * ln * 0.72); s1 = P2(t + w / 2 + tilt * ln * 0.7, base - side * ln * 0.72)
            tip = P2(t + tilt * ln, tip_n)
            d.polygon([b0, b1, s1, tip, s0], fill=o.rgb(rnd.choice(PATCH)), outline=o.rgb(QZ_EDGE), width=int(2 * s))
            d.line([P2(t + w * 0.15, base - side * 6 * s), P2(t + w * 0.15 + tilt * ln * 0.6, base - side * ln * 0.6)],
                   fill=o.rgb(C["magnesia"], 150), width=int(2 * s))
            for _ in range(rnd.randint(0, 2)):                       # Fluessigkeitseinschluesse
                q = P2(t + rnd.uniform(-w / 3, w / 3), base - side * rnd.uniform(0.2, 0.6) * ln)
                rr = rnd.uniform(1.5, 3.0) * s; d.ellipse([q[0] - rr, q[1] - rr, q[0] + rr, q[1] + rr], fill=o.rgb(QZ_EDGE))
            t += w * rnd.uniform(0.8, 1.0)
    for side in (-1, 1):
        d.line([P2(-L, side * hw), P2(L, side * hw)], fill=o.rgb(C["magnesia"]), width=int(3 * s))
    vign = Image.new("L", (N, N), 0); ImageDraw.Draw(vign).ellipse([0, 0, N, N], fill=255)
    im.putalpha(vign)
    return im.resize((2 * R, 2 * R), Image.LANCZOS)


# ------------------------------------------------------------------ Woerter: CLIMBING (Kreide) / x GEOLOGY (Schichten)
class Words:
    def __init__(self, y=300, size=160, x=X0):
        sz = min(m.fit(WORDS[0], "display", size), m.fit("× " + WORDS[1], "display", size))
        self.size = sz; lh = sz * 0.95
        self.y1, self.y2 = y, y + lh
        self.climb = self._chalk_word(WORDS[0], x, self.y1, sz)
        xw = o.text_width("× ", "display", sz)
        self.times = m.text_sprite("×", x, self.y2, "display", sz, C["heat"])
        self.geo = self._strata_word(WORDS[1], x + xw, self.y2, sz)
        self.bottom = self.y2 + lh

    def _chalk_word(self, s, x, y, size, seed=5):
        def d(im):
            mask = Image.new("L", im.size, 0); o.text(mask, x, y, s, "display", size, 255)
            a = np.asarray(mask, np.float32) / 255
            rng = np.random.default_rng(seed)
            noise = np.asarray(Image.fromarray((rng.random(a.shape) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.3 * o.S)), np.float32) / 255
            a *= np.where(noise > 0.6, 0.45, 1.0)
            lay = Image.new("RGBA", im.size, o.rgb(C["magnesia"])); lay.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
            im.alpha_composite(lay)
        return m.sprite(d)

    def _strata_word(self, s, x, y, size):
        def d(im):
            mask = Image.new("L", im.size, 0); bb = o.text(mask, x, y, s, "display", size, 255)
            x0, y0, x1, y1 = bb
            lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
            n = len(STRATA); hh = (y1 - y0) / n
            for i, col in enumerate(STRATA):                        # leicht wellige Schichtgrenzen
                top = [(xx, y0 + i * hh + 7 * o.S * math.sin(xx / (95 * o.S) + i * 1.3)) for xx in range(int(x0) - 10, int(x1) + 12, 8)]
                bot = [(xx, y0 + (i + 1) * hh + 7 * o.S * math.sin(xx / (95 * o.S) + (i + 1) * 1.3)) for xx in range(int(x0) - 10, int(x1) + 12, 8)]
                if i == 0:
                    top = [(xx, y0 - 20 * o.S) for xx, _ in top]
                if i == n - 1:
                    bot = [(xx, y1 + 20 * o.S) for xx, _ in bot]
                dl.polygon(top + bot[::-1], fill=o.rgb(col))
                if i:
                    dl.line(top, fill=o.rgb(C["obsidian"]), width=int(3 * o.S))
            lay.putalpha(Image.fromarray(np.minimum(np.asarray(lay.getchannel("A")), np.asarray(mask))))
            im.alpha_composite(lay)
        return m.sprite(d)

    def draw(self, f, t, out_dur=0.28):
        """CLIMBING steht ab Frame 0 (leichter Zoom), x GEOLOGY schlaegt bei T_GEO ein; ab T_OUT gehen beide nach oben."""
        out = seilzug(seg(t, T_OUT, out_dur)); dy = -90 * out; op = 1 - out
        if op <= 0:
            return
        put(f, self.climb, dy=dy, op=op, scale=lerp(1.05, 1.0, seilzug(seg(t, 0, 0.6))), anchor=(X0, self.y1))
        u = seg(t, T_GEO, 0.22)
        if u > 0:
            sc = lerp(1.38, 1.0, griff(u)) if u < 1 else 1.0
            put(f, self.times, dy=dy, op=op * min(1, u * 4), scale=sc, anchor=(X0, self.y2 + self.size * 0.5))
            put(f, self.geo, dy=dy, op=op * min(1, u * 4), scale=sc, anchor=(X0, self.y2 + self.size * 0.5))


# ------------------------------------------------------------------ Kamera-Rucken beim Einschlag
def shake(t, t0, amp=7.0, dur=0.22):
    v = seg(t, t0, dur)
    if not 0 < v < 1:
        return 0.0, 0.0
    k = (1 - v) ** 2 * amp
    return k * math.sin(t * 173.0), k * math.cos(t * 131.0)


# ------------------------------------------------------------------ Ton fuer Hook 1 (relativ zu t=0)
def sound(book, kenney=True):
    """Hook-1-Ton: Bass-Anschlag ab 0,0 s, Luftzug zum Griff, Kreide-Klatscher beim Zugreifen, Einschlag mit Braam,
    Gesteinsknacken und Kristall-Schimmer bei 'x GEOLOGY', Abtasten in der Lupe, Swell in die Frage."""
    book.synth("sub", 0.0, -9.0, "hook1-start", seed=2, dur=0.9)
    book.synth("whoosh", 0.04, -15.0, "hook1-griff", dur=0.36, seed=4)
    if kenney:
        book.kenney("impact-sounds", "impactGeneric_light_000.ogg", T_REACH, -4.0, "hook1-kreide")
    book.synth("clap", T_REACH + 0.005, -9.0, "hook1-kreide", seed=5)
    book.synth("sub", T_GEO, -2.0, "hook1-einschlag", seed=3, dur=1.3)
    if kenney:
        book.kenney("impact-sounds", "impactPunch_heavy_000.ogg", T_GEO, -4.0, "hook1-einschlag")
        book.kenney("impact-sounds", "impactMining_000.ogg", T_GEO + 0.02, -9.0, "hook1-fels")
    book.synth("braam", T_GEO, -9.0, "hook1-braam", seed=6, dur=1.3)
    book.synth("crack", T_GEO + 0.03, -6.0, "hook1-fels", seed=7)
    book.synth("shimmer", T_GEO + 0.06, -13.0, "hook1-kristall", seed=8, dur=1.2)
    book.synth("scan", T_GEO + 0.25, -21.0, "hook1-lupe", seed=9, dur=0.95)
    book.synth("swell", T_OUT - 0.42, -16.0, "hook1-uebergang", seed=10, dur=0.42)
    book.synth("whoosh", T_OUT, -12.0, "hook1-uebergang", dur=0.4, seed=12)
