#!/usr/bin/env python3
"""Reel 004 -- HOLD ID #01, Neufassung von r002 (Faktenbasis: Post #029, Quarzgang) mit Hook 1 + Hook 2 und Kino-Ton.

Anlass (Markus, 13./14.10.2026): Bei r002 war am Anfang nicht klar, worum es geht; "hook 1 (klettern und geologie)
und dann hook 2 (eigentliches reel thema)", neuer Ton, Neufassung von HOLD ID #01 neu posten.

Ablauf "erklaerkette" (wie r002). Aufbau:
  Hook 1 (0-1,7 s)   Kamera unten an der Wand: Kletterer haengt am Quarzgang und greift nach (CLIMBING, Kreide),
                     Lupe oeffnet sich in den Gang (x GEOLOGY, Einschlag). Danach faehrt die Kamera herunter.
  Hook 2 (1,7-4,95 s) Frage "WHY IS THIS WHITE STRIPE A HOLD?" ueber der Wand, Kletterer bleibt am Gang, Uhr tickt.
  Ab 4,95 s          Szenen von r002 um SHIFT verschoben: Querschnitt (heisses Wasser), viel spaeter (Verwitterung),
                     Payoff "QUARTZ LASTS LONGER." -- dort haengt der Kletterer wieder am Gang (Rueckbezug), Stempel.
Bildmittel (fuer die Abwechslungsregel): Iris-Lupe, Kamerafahrt, Isolinien-Welle (aus r002), Puls 112 BPM in A.
"""
import math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from PIL import Image, ImageDraw

import outcrop as o
import motion as m
import reelkit as rk
import hook1 as h1
import r002_holdid_029 as base
from outcrop import C, P
from motion import X0, W, H, FPS, seg, seilzug, sturz, griff, lerp, put

SHIFT = 1.80                              # so viel spaeter laufen alle Szenen von r002 (Hook 1 + Uebergang)
DUR = base.DUR + SHIFT                    # 14,8 s
SLUG = "2026-10-14_holdid-01"
HOOK2 = ["WHY IS THIS", "WHITE STRIPE", "A HOLD?"]
ON_SCREEN = ["HOLD ID", " ".join(HOOK2), "HOT WATER SEALS A CRACK WITH QUARTZ.",
             "MUCH LATER, THE ROCK AROUND IT WEARS AWAY.", "QUARTZ LASTS LONGER.",
             "HOLD ID #01", "QUARTZ VEIN", "Test it: veins can flake off."]

# Zeiten (neu = alt + SHIFT)
T_Q2 = 1.58                               # Frage schlaegt ein, nachdem die Hook-1-Woerter weg sind
T_Q_IN = T_Q2 + 0.17                      # Frage voll sichtbar (1,75 s)
OUT_DUR = 0.18                            # Hook-1-Woerter gehen schnell
T_SEC = base.T_SEC + SHIFT                # Schnittlinie (4,10 s)
T_W1 = base.T_W1 + SHIFT                  # Welle in den Querschnitt (4,95 s) = Ende Hook 2
T_S2 = base.T_S2 + SHIFT
T_RISE = base.T_RISE + SHIFT
T_S4 = base.T_S4 + SHIFT                  # Payoff (10,90 s)
T_BACK = T_S4 + 0.35                      # Kletterer haengt wieder am Gang
T_END = base.T_END + SHIFT

# Kamera in Hook 1: Welt um DY_H1 nach oben verschoben (Kletterer sichtbar), danach Fahrt auf die Hook-2-Ansicht
DY_H1 = -300
PAD = 420                                 # Wand reicht so weit unter den Bildrand, damit die Fahrt nichts Leeres zeigt
LENS_X = 840                              # Lupe und spaeter die Schnittlinie sitzen rechts vom Kletterer
LENS_R = 140
BPM = 112.0


def vein_y(x):
    """Mittellinie des Gangs in der Wandansicht (wie r002)."""
    (x0, y0), (x1, y1) = base.VEIN_P0, base.VEIN_P1
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


def tall_background(draw, h):
    im = Image.new("RGBA", (W * o.S, h * o.S), o.rgb(C["obsidian"]))
    draw(im)
    return im.resize((W, h), Image.LANCZOS)


def wall_tall(im, top=930, bottom=1960 + PAD, seed=3):
    """wall_front aus r002, aber nach unten verlaengert und ohne Kreide-Ticks (die Hand des Kletterers zeigt den Griff)."""
    poly = o.ragged(110, top, 1090, bottom, seed=seed, amp=16, n=18, top_only=True)
    mask = base.rock_fill(im, poly, seed)
    d = ImageDraw.Draw(im)
    for pts in ([(260, 1060), (300, 1190), (282, 1330)], [(905, top + 40), (880, 1060), (930, 1150)]):
        d.line([P(x, y) for x, y in pts], fill=o.rgb(C["obsidian"], 210), width=int(3 * o.S), joint="curve")
    base.vein_front(im, mask)
    d.line([P(x, y) for x, y in poly[:19]], fill=o.rgb(C["magnesia"]), width=int(4 * o.S), joint="curve")
    return poly


# ------------------------------------------------------------------ Kletterer am Gang (Weltkoordinaten, Hook-2-Ansicht)
HL = (520, vein_y(520) - 21)              # linke Hand: Leiste oben am Gang
HR = (650, vein_y(650) - 21)              # rechte Hand: Zielgriff
HR0 = (596, 1598)                         # rechte Hand im Chalkbag (Frame 0), greift dann zum Gang
POSE_HANG = dict(pelvis=(588, 1570), lean=0.04, hand_l=HL, hand_r=HR, foot_l=(510, 1735), foot_r=(695, 1715),
                 bend_el_l=-1, bend_el_r=1, bend_kn_l=1, bend_kn_r=-1)
POSE_REACH = dict(POSE_HANG, pelvis=(580, 1586), lean=-0.05, hand_r=HR0)
SCALE = 0.9
FOOTHOLDS = [(506, 1748, 56), (700, 1728, 52)]   # Tritte unter den Fuessen (x, y Oberkante, Breite)


def climber_pose(t):
    """Hook 1: rechte Hand greift bis T_REACH nach, danach haengt er; kleines Atmen."""
    u = griff(seg(t, 0.0, h1.T_REACH))
    p = h1.lerp_pose(POSE_REACH, POSE_HANG, u)
    bob = 3.0 * math.sin(2 * math.pi * 0.9 * max(0.0, t - h1.T_REACH))
    p["pelvis"] = (p["pelvis"][0], p["pelvis"][1] + bob)
    return p


class Reel(base.Reel):
    DUR = DUR

    def __init__(self):
        super().__init__()
        self.world = tall_background(lambda im: (o.contour_field(im, 760, 1520, n=10, r0=120, step=60, alpha=110),
                                                 wall_tall(im), h1.holds(im, FOOTHOLDS)), H + PAD)
        self.rail0 = rk.rail_sprite(0, base.RAIL_N)
        self.brand = m.text_sprite("GEOCRIMPS", X0, 250, "stencil", 40, C["magnesia"], tracking=0.12)
        self.words = h1.Words(y=300)
        ang = math.degrees(math.atan2(base.VEIN_P1[1] - base.VEIN_P0[1], base.VEIN_P1[0] - base.VEIN_P0[0]))
        self.lens = h1.Lens(h1.vein_view(LENS_R, ang, base.VEIN_HALF, seed=7), LENS_R)
        self.hook, _ = m.lines_sprite(HOOK2, rk.HOOK_Y, size=164)
        # Schnittlinie wandert mit der Lupe nach rechts (bei r002: x = 640)
        c = (LENS_X, vein_y(LENS_X)); n = (0.353, 0.936)
        a = (c[0] - n[0] * 175, c[1] - n[1] * 175); b = (c[0] + n[0] * 175, c[1] + n[1] * 175)
        def secline(im):
            d = ImageDraw.Draw(im); L = math.hypot(b[0] - a[0], b[1] - a[1]); k = 0.0
            while k < L:
                k1 = min(L, k + 18)
                d.line([P(a[0] + (b[0] - a[0]) * k / L, a[1] + (b[1] - a[1]) * k / L),
                        P(a[0] + (b[0] - a[0]) * k1 / L, a[1] + (b[1] - a[1]) * k1 / L)], fill=o.rgb(C["magnesia"]), width=int(4 * o.S))
                k += 30
            for p in (a, b):
                d.line([P(p[0] - 0.936 * 16, p[1] + 0.353 * 16), P(p[0] + 0.936 * 16, p[1] - 0.353 * 16)],
                       fill=o.rgb(C["magnesia"]), width=int(5 * o.S))
        self.secline = m.sprite(secline)
        self.sec_c = c

    # -------------------------------------------------------------- Hook 1 + Hook 2 (eigene Szene mit Kamerafahrt)
    def scene1(self, t):
        dy = lerp(DY_H1, 0.0, seilzug(seg(t, h1.T_OUT, 0.45)))
        _, sy = h1.shake(t, h1.T_GEO, amp=8.0)
        top = int(round(-dy - sy))
        f = self.world.crop((0, top, W, top + H))
        sp, k = h1.climber_sprite(climber_pose(t), SCALE, dy=dy)
        put(f, sp)
        h1.chalk_puff(f, t, h1.T_REACH, k["ha_r"][0], k["ha_r"][1] + dy, seed=11)
        cy = vein_y(LENS_X) + dy                                     # Lupe: oeffnet bei T_GEO, schliesst bei T_OUT
        r = LENS_R * (sturz(seg(t, h1.T_GEO, 0.24)) * (1 - seilzug(seg(t, h1.T_OUT, 0.22))))
        self.lens.draw(f, LENS_X, cy, r)
        u = seilzug(seg(t, T_SEC, 0.42))
        if u > 0:
            put(f, m.reveal(self.secline, u))
        z = 1 + 0.03 * seilzug(seg(t, 0, T_W1))
        f = m.zoomed(f, z, self.sec_c[0], self.sec_c[1] + dy)
        put(f, self.rail0)
        q = seilzug(seg(t, T_Q2, 0.17))                             # Hook 2: Frage schlaegt ein
        if q > 0:
            put(f, self.meta, op=q); put(f, self.stamp_top, op=q)
            put(f, self.hook, op=min(1, q * 1.6), scale=lerp(1.12, 1.0, q), anchor=(X0, rk.HOOK_Y))
        b = 1 - seilzug(seg(t, h1.T_OUT, OUT_DUR))                  # Hook 1: Marke und Woerter
        if b > 0:
            put(f, self.brand, op=b)
            self.words.draw(f, t, out_dur=OUT_DUR)
        if t >= T_W1:
            put(f, self.wave(seg(t, T_W1, 0.5), cx=self.sec_c[0], cy=self.sec_c[1]))
        return f, 21

    def frame(self, t):
        if t < T_S2:
            return self.scene1(t)
        f, s = base.Reel.frame(self, t - SHIFT)
        if T_S4 <= t < T_END:                                        # Payoff: Kletterer haengt wieder am Gang
            u = seg(t, T_BACK - 0.3, 0.3)
            if u > 0:
                p = dict(POSE_HANG)
                p["pelvis"] = (POSE_HANG["pelvis"][0], POSE_HANG["pelvis"][1] + 3.0 * math.sin(2 * math.pi * 0.9 * (t - T_BACK)))
                sp, k = h1.climber_sprite(p, SCALE, dy=lerp(260, 0, griff(u)))
                put(f, sp, op=min(1.0, u * 2.5))
                h1.chalk_puff(f, t, T_BACK, k["ha_r"][0], k["ha_r"][1], seed=19, n=30)
        return f, s

    def frames(self, draft=False):
        n = int(round(self.DUR * FPS))
        for i in range(n):
            if draft and i % 3:
                continue
            f, s = self.frame(i / FPS)
            yield self.fin(f, s)


# ------------------------------------------------------------------ Ton
def sound_events(b):
    """Hook 1 aus hook1.sound; Uhr unter der Hook-2-Frage; Szenenklaenge von r002 (verschoben); Puls 112 BPM bis kurz
    vor den Payoff (dort 0,15 s Stille, dann Bass, Braam und der Treffer aus r002); Flaeche in Hook 2 und im Payoff."""
    h1.sound(b)
    ev, used = base.sound_events()
    for t, smp, g in ev[:-2]:                                        # ohne die alten Flaechen (die zwei letzten Ereignisse)
        if t < 0.5:                                                  # alter Hook-Tick entfaellt
            continue
        b.ev.append((t + SHIFT, smp, g))
    for k, v in used.items():
        if k != "flaeche":
            b.used.setdefault(k, set()).add(v)
    beat_s = 60.0 / BPM                                              # ein Raster fuer Hook 2 und Erklaerteil
    k = 0
    while T_Q_IN + k * beat_s < T_W1 - 0.1:                          # Hook 2: Herzschlag + Uhr auf den Zwischenschlaegen
        t = T_Q_IN + k * beat_s
        b.synth("kick", t, -13.0 + 0.5 * k, "herzschlag", seed=30 + k)
        b.synth("tick2", t + beat_s / 2, -14.0 if k % 2 == 0 else -17.0, "uhr", freq=2600 if k % 2 == 0 else 1900)
        k += 1
    b.synth("swell", T_W1 - 0.45, -15.0, "uebergang", seed=21, dur=0.45)
    t0 = T_Q_IN + math.ceil((T_S2 - T_Q_IN) / beat_s) * beat_s       # Beat setzt im selben Raster fort
    for t, smp, g in m.beat(t0, T_S4 - 0.15, bpm=BPM, root=55.0, build_from=T_RISE - 0.6, seed=4):
        b.ev.append((t, smp, g))
    b.used.setdefault("puls", set()).add("selbst erzeugt (Kick, Hi-Hat, Bass)")
    b.synth("sub", T_S4, -4.0, "payoff", seed=13, dur=1.2)
    b.synth("braam", T_S4, -10.0, "payoff", seed=14, dur=1.5, freq=110.0)
    b.synth("clap", T_BACK, -11.0, "kreide", seed=15)
    b.pads([(T_Q_IN, T_W1, -15.0), (T_S4 + 0.2, T_END, -14.0)], depth_db=-6.0)


T_W2 = base.T_W2 + SHIFT; T_S3 = base.T_S3 + SHIFT; T_STAMP = base.T_STAMP + SHIFT
META = dict(
    slug=SLUG, dur_range=[11, 15], payoff_t=T_S4, on_screen=ON_SCREEN, labels=base.LABELS,
    qc_times=[0.0, 0.2, 0.4, 0.62, 1.0, 1.55, 1.9, 2.6, 4.3, 5.6, 7.0, 9.0, 10.2, 11.4, 12.6, 14.3],
    marks=[(0, "Hook 1"), (h1.T_GEO, "GEOLOGY"), (T_Q_IN, "Hook 2"), (T_SEC, "Schnitt"), (T_W1, "Zug 1"), (T_W2, "Welle"),
           (T_S3, "Zug 2"), (T_RISE, "Steigerung"), (T_S4, "PAYOFF"), (T_STAMP, "Stempel"), (T_END, "Klanglogo")],
    title="GeoCrimps r004 HOLD ID #01 Neufassung (Hook 1 + Hook 2, Erklaerkette)",
    ablauf="erklaerkette", hook1=True, hook_von=T_Q_IN, hook_bis=T_W1, cover_t=2.6, weitere_fragen=[])

if __name__ == "__main__":
    rk.run(Reel, sound_events, META)
