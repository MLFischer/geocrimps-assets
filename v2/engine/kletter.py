#!/usr/bin/env python3
"""GeoCrimps-Kletterbausteine (seit 13.10.2026): damit jedes Reel im ersten Moment zeigt, dass es ums Klettern geht.

  Climber      Kletterer-Piktogramm im Outcrop-Stil: dicke runde Striche in Magnesia mit dunkler Kontur.
               Pose = Becken, Neigung, Haende und Fuesse als Zielpunkte; Arme und Beine per Zwei-Gelenk-IK
               (feste Laengen), also bleiben Proportionen bei jeder Bewegung erhalten.
  crash_pad    Crashpad am Wandfuss (Bouldern).
  chalk_puff   Kreidewolke beim Zugreifen.
  GeoReveal    Aufklappen in den geologischen Schnitt: Gesteinssignatur und Schichtlinien im Felsumriss,
               radial vom Griff aus aufgedeckt (fuer Hook 1 "x GEOLOGY").
Alle Koordinaten in 1x-Bildpunkten (1080 x 1920); gezeichnet wird in doppelter Aufloesung (outcrop.S).
"""
import math
import random

import numpy as np
from PIL import Image, ImageDraw

import motion as m
import outcrop as o
from motion import seg, seilzug
from outcrop import C, P

# ------------------------------------------------------------------ Kletterer
LEN = dict(torso=106.0, head=23.0, neck=13.0, upper=70.0, fore=66.0, thigh=86.0, shin=82.0)


def _ik(root, target, a, b, bend):
    """Zwei-Gelenk-IK: Gelenkpunkt und Endpunkt fuer Segmentlaengen a, b; bend = +1/-1 (Knickrichtung)."""
    dx, dy = target[0] - root[0], target[1] - root[1]
    dist = math.hypot(dx, dy) or 1e-3
    ux, uy = dx / dist, dy / dist
    d = max(abs(a - b) + 1e-3, min(dist, a + b - 1e-3))
    ang = math.acos(max(-1.0, min(1.0, (a * a + d * d - b * b) / (2 * a * d)))) * bend
    jx = root[0] + a * (ux * math.cos(ang) - uy * math.sin(ang))
    jy = root[1] + a * (ux * math.sin(ang) + uy * math.cos(ang))
    return (jx, jy), (root[0] + ux * d, root[1] + uy * d)


def lerp_pose(p, q, u):
    """Posen mischen (alle Zahlen und Punkte linear)."""
    out = {}
    for k in p:
        a, b = p[k], q.get(k, p[k])
        if isinstance(a, tuple):
            out[k] = tuple(x + (y - x) * u for x, y in zip(a, b))
        elif isinstance(a, (int, float)):
            out[k] = a + (b - a) * u
        else:
            out[k] = a if u < 0.5 else b
    return out


def move_pose(p, dx=0.0, dy=0.0, rot_deg=0.0, pivot=None):
    """Pose verschieben und um pivot (Standard: Becken) drehen, z. B. fuer einen Sturz."""
    px, py = pivot or p["hip"]
    c, s = math.cos(math.radians(rot_deg)), math.sin(math.radians(rot_deg))
    out = dict(p)
    for k in ("hip", "lh", "rh", "lf", "rf"):
        x, y = p[k][0] - px, p[k][1] - py
        out[k] = (px + x * c - y * s + dx, py + x * s + y * c + dy)
    out["lean"] = p.get("lean", 0.0) + rot_deg
    return out


class Climber:
    """Piktogramm: Rumpf als breite Kapsel, Kopf mit Luft zum Rumpf, Gliedmassen schmaler (wie Sport-Piktogramme).
    Pose-Schluessel: hip (Becken), lean (Grad, 0 = aufrecht, + = Oberkoerper nach rechts), lh/rh/lf/rf (Zielpunkte),
    sw/hw (halbe Schulter-/Beckenbreite; > 0 fuer die Rueckenansicht an der Wand), eb/kb (Knickrichtung Ellbogen/Knie
    je links/rechts; Rueckenansicht: eb = (-1, 1), kb = (1, -1), also Ellbogen und Knie nach aussen)."""

    def __init__(self, scale=1.0, color=C["magnesia"], outline=C["obsidian"], width=16.0, outline_w=5.0, torso_w=32.0):
        self.k = scale
        self.color, self.outline = color, outline
        self.w, self.ow, self.tw = width * scale, outline_w * scale, torso_w * scale

    def joints(self, pose):
        k = self.k
        hip = pose["hip"]
        lean = math.radians(pose.get("lean", 0.0))
        ux, uy = math.sin(lean), -math.cos(lean)                     # Richtung Becken -> Hals
        neck = (hip[0] + ux * LEN["torso"] * k, hip[1] + uy * LEN["torso"] * k)
        sh = (hip[0] + ux * LEN["torso"] * k * 0.9, hip[1] + uy * LEN["torso"] * k * 0.9)
        r = LEN["head"] * k
        head = (neck[0] + ux * (LEN["neck"] * k + r), neck[1] + uy * (LEN["neck"] * k + r))
        eb = pose.get("eb", (1, -1)); kb = pose.get("kb", (-1, 1))
        sw, hw = pose.get("sw", 0.0) * k, pose.get("hw", 0.0) * k      # halbe Schulter-/Beckenbreite (Rueckenansicht)
        px, py = -uy, ux                                                 # quer zum Rumpf
        lsh, rsh = (sh[0] - px * sw, sh[1] - py * sw), (sh[0] + px * sw, sh[1] + py * sw)
        lhp, rhp = (hip[0] - px * hw, hip[1] - py * hw), (hip[0] + px * hw, hip[1] + py * hw)
        le, lh = _ik(lsh, pose["lh"], LEN["upper"] * k, LEN["fore"] * k, eb[0])
        re, rh = _ik(rsh, pose["rh"], LEN["upper"] * k, LEN["fore"] * k, eb[1])
        lk, lf = _ik(lhp, pose["lf"], LEN["thigh"] * k, LEN["shin"] * k, kb[0])
        rk_, rf = _ik(rhp, pose["rf"], LEN["thigh"] * k, LEN["shin"] * k, kb[1])
        return dict(hip=hip, neck=neck, sh=sh, head=head, r=r, le=le, lh=lh, re=re, rh=rh, lk=lk, lf=lf, rk=rk_, rf=rf,
                    lsh=lsh, rsh=rsh, lhp=lhp, rhp=rhp)

    def draw(self, im, pose, alpha=255, off=(0.0, 0.0)):
        """In eine 2x-Flaeche zeichnen; off = Bildkoordinate der linken oberen Ecke der Flaeche (fuer kleine Flaechen)."""
        j = self.joints(pose)
        limbs = [(j["lsh"], j["le"]), (j["le"], j["lh"]), (j["rsh"], j["re"]), (j["re"], j["rh"]),
                 (j["lhp"], j["lk"]), (j["lk"], j["lf"]), (j["rhp"], j["rk"]), (j["rk"], j["rf"])]
        d = ImageDraw.Draw(im)
        ox, oy = off

        def Q(x, y):
            return ((x - ox) * o.S, (y - oy) * o.S)

        def dot(q, rr, col):
            d.ellipse([Q(q[0] - rr, q[1] - rr), Q(q[0] + rr, q[1] + rr)], fill=col)

        def capsule(a, b, w, col):
            d.line([Q(*a), Q(*b)], fill=col, width=max(1, int(w * o.S)))
            dot(a, w / 2, col); dot(b, w / 2, col)

        for col, extra in ((o.rgb(self.outline, alpha), self.ow), (o.rgb(self.color, alpha), 0.0)):
            for a, b in limbs:
                capsule(a, b, self.w + 2 * extra, col)
            capsule(j["hip"], j["sh"], self.tw + 2 * extra, col)                  # Rumpf
            capsule(j["lsh"], j["rsh"], self.w * 1.2 + 2 * extra, col)            # Schultern
            for q in (j["lh"], j["rh"]):                                          # Haende etwas kraeftiger
                dot(q, self.w * 0.66 + extra, col)
            dot(j["head"], j["r"] + extra, col)
        return j

    def sprite(self, pose, alpha=255):
        """Nur die Umgebung der Figur in 2x zeichnen (schnell genug fuer jedes Bild)."""
        j = self.joints(pose)
        pts = [v for v in j.values() if isinstance(v, tuple)]
        pad = self.tw + self.ow * 2 + j["r"] + 6
        x0 = int(min(p[0] for p in pts) - pad); y0 = int(min(p[1] for p in pts) - pad)
        x1 = int(max(p[0] for p in pts) + pad) + 1; y1 = int(max(p[1] for p in pts) + pad) + 1
        im = Image.new("RGBA", ((x1 - x0) * o.S, (y1 - y0) * o.S), (0, 0, 0, 0))
        self.draw(im, pose, alpha, off=(x0, y0))
        return m.Sprite(im.resize((x1 - x0, y1 - y0), Image.LANCZOS), x0, y0)


# ------------------------------------------------------------------ Crashpad, Kreide
def crash_pad(im, x0, x1, y_ground, h=40, seed=3):
    """Crashpad liegt auf dem Boden (y_ground = Unterkante); Naht in der Mitte, Tragegriffe an den Enden."""
    d = ImageDraw.Draw(im)
    y0 = y_ground - h
    d.rounded_rectangle([P(x0, y0), P(x1, y_ground)], radius=int(10 * o.S), fill=o.rgb("#2E3A44"),
                        outline=o.rgb(C["magnesia"]), width=int(4 * o.S))
    d.line([P(x0 + 10, y0 + h * 0.5), P(x1 - 10, y0 + h * 0.5)], fill=o.rgb(C["slate"]), width=int(2 * o.S))
    for xx in ((x0 + x1) / 2 - 1.5, (x0 + x1) / 2 + 1.5):
        d.line([P(xx, y0 + 4), P(xx, y_ground - 4)], fill=o.rgb(C["slate"], 160), width=int(2 * o.S))
    for xh in (x0 + 26, x1 - 46):
        d.arc([P(xh, y0 - 12), P(xh + 20, y0 + 8)], 180, 360, fill=o.rgb(C["magnesia"], 220), width=int(3 * o.S))


def chalk_puff(f, t, t0, x, y, seed=11, size=1.0):
    """Kreidewolke an (x, y) ab t0: weiche Wolke waechst und verblasst, Kreidekoerner fliegen."""
    v = seg(t, t0, 0.7)
    if not 0 < v < 1:
        return
    lay = Image.new("RGBA", f.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    rnd = random.Random(seed)
    for _ in range(9):
        ang = rnd.uniform(0, 2 * math.pi); dist = rnd.uniform(6, 34) * size * seilzug(v)
        cx, cy = x + math.cos(ang) * dist, y + math.sin(ang) * dist - 18 * v * size
        r = (14 + 30 * seilzug(v)) * size * rnd.uniform(0.6, 1.0)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=o.rgb(C["magnesia"], int(70 * (1 - v))))
    for _ in range(46):
        ang = rnd.uniform(0, 2 * math.pi); sp = rnd.uniform(25, 95) * size
        qx = x + math.cos(ang) * sp * seilzug(v); qy = y + math.sin(ang) * sp * seilzug(v) + 30 * v * v
        r = rnd.uniform(1.4, 3.2)
        d.ellipse([qx - r, qy - r, qx + r, qy + r], fill=o.rgb(C["magnesia"], int(220 * (1 - v))))
    f.alpha_composite(lay)


# ------------------------------------------------------------------ Aufklappen in den geologischen Schnitt
class GeoReveal:
    """Gesteinssignatur (outcrop-Muster) und Schichtlinien im Felsumriss, radial vom Griff (cx, cy) aufgedeckt.
    beds: Polylinien (Schichtung, Kluefte), kraeftig; contacts: Polylinien (Kontakte, z. B. Gangraender), hell;
    holes: Polygone ohne Signatur (z. B. ein Gang, der die Schichten durchschlaegt). pat_alpha: Deckkraft der Signatur."""

    def __init__(self, poly, kind, cx, cy, color=C["magnesia"], pat_alpha=110, beds=(), contacts=(), holes=(), seed=4,
                 bed_w=3.0):
        S = o.S
        mask = Image.new("L", (m.W * S, m.H * S), 0)
        dm = ImageDraw.Draw(mask)
        dm.polygon([P(x, y) for x, y in poly], fill=255)
        for hp in holes:
            dm.polygon([P(x, y) for x, y in hp], fill=0)
        pat = o._pattern_layer(mask.size, kind, color, seed=seed)
        a_pat = np.asarray(pat.getchannel("A"), np.float32) * (pat_alpha / 255)
        lines = Image.new("L", mask.size, 0); dl = ImageDraw.Draw(lines)
        for line in beds:
            dl.line([P(*q) for q in line], fill=215, width=int(bed_w * S), joint="curve")
        a_lin = np.asarray(lines, np.float32)
        a = np.maximum(a_pat, a_lin) * (np.asarray(mask, np.float32) / 255)
        cont = Image.new("L", mask.size, 0); dc = ImageDraw.Draw(cont)
        for line in contacts:
            dc.line([P(*q) for q in line], fill=255, width=int(4 * S), joint="curve")
        a = np.maximum(a, np.asarray(cont, np.float32))
        lay = Image.new("RGBA", mask.size, o.rgb(color))                 # Farbe ueberall, Deckkraft aus Signatur/Linien
        lay.putalpha(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)))
        small = lay.resize((m.W, m.H), Image.LANCZOS)
        bb = small.getbbox() or (0, 0, m.W, m.H)
        self.img = small.crop(bb)
        self.x, self.y = bb[0], bb[1]
        yy, xx = np.mgrid[bb[1]:bb[3], bb[0]:bb[2]].astype(np.float32)
        self.dist = np.hypot(xx - cx, yy - cy)
        self.rmax = float(self.dist.max()) + 1
        self.alpha0 = np.asarray(self.img.getchannel("A"), np.float32)
        inside = np.asarray(mask.resize((m.W, m.H), Image.BOX), np.float32)[bb[1]:bb[3], bb[0]:bb[2]] / 255
        self.inside = inside

    def put(self, f, u, fade=1.0):
        """u = Aufdeck-Fortschritt 0..1 (Radius), fade = Deckkraft 0..1. Die Front der Welle leuchtet als heller Saum."""
        if u <= 0 or fade <= 0:
            return
        r = self.rmax * u
        a = self.alpha0 * np.clip((r - self.dist) / 18.0 + 1, 0, 1) * fade
        if u < 1:
            edge = np.clip(1 - np.abs(self.dist - r) / 12.0, 0, 1) ** 1.5 * self.inside
            a = np.maximum(a, edge * 150 * fade * (1 - u) ** 0.5)
        img = self.img.copy()
        img.putalpha(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)))
        m.composite(f, img, self.x, self.y)
