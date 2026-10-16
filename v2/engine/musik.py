#!/usr/bin/env python3
"""GeoCrimps-Musik (seit 16.10.2026): musikalische Untermalung statt metallischer Klicks, selbst erzeugt.

Markus, 16.10.2026: "die toene nicht ganz so klirrend metallisch bitte, eher musikalische untermalung".
Alles additiv aus harmonischen Teiltoenen (keine unharmonischen Metall-Teiltoene, kein Hochton-Rauschen), weich
gefiltert und in einer Tonart je Reel. Damit lizenzfrei per Konstruktion wie klang.py.

Bausteine (48 kHz Stereo float32, wie motion.synth):
  flaeche(akkord, dauer)    warme Akkordflaeche aus leicht verstimmten Stimmen, langsamer Einsatz, links/rechts verschieden
  zupf(note)                weicher Holzton (Grundton + harmonische Obertoene, schnell abklingend), z. B. Tropfen, Bohrhaken
  bass(note, dauer)         runder Bass auf dem Grundton
  schwelle(akkord, dauer)   anschwellende Flaeche, endet auf dem Zielzeitpunkt (statt Rauschen oder Sinus-Riser)
  akzent(akkord, bassnote)  weicher Akkordschlag fuer Payoff und Stempel

Noten als MIDI-Nummern (69 = A4 = 440 Hz). Akkorde fuer G-Dur (r003): G = [55, 59, 62, 67], Em9 = [52, 55, 59, 62, 66],
Cmaj7 = [55, 59, 60, 64], Am7 = [55, 57, 60, 64], Bm7 = [54, 57, 59, 62], D = [54, 57, 62, 66], Dsus4 = [55, 57, 62].
Den Arrangeur (Abschnitte, Figuren, Tempo) stellt reelkit.SoundBook.musik bereit.
"""
import numpy as np

from motion import SR, _stereo
from klang import _filt


def hz(m):
    return 440.0 * 2.0 ** ((m - 69) / 12.0)


def _n(dur):
    n = max(1, int(SR * dur))
    return n, np.arange(n) / SR


def flaeche(akkord, dauer, seed=0, hell=2300.0, attack=0.45, release=0.8):
    """Akkordflaeche: je Note zwei leicht verstimmte Stimmen pro Kanal, vier harmonische Teiltoene, sanftes Vibrato,
    Tiefpass bei hell Hz. Laenge dauer + release (die Ausklingzeit ueberlappt den naechsten Akkord)."""
    n, t = _n(dauer + release)
    rng = np.random.default_rng(seed)
    out = np.zeros((n, 2), np.float64)
    for ch, cents in ((0, (-7.0, 3.0)), (1, (-3.0, 7.0))):
        x = np.zeros(n)
        for m in akkord:
            for c in cents:
                f = hz(m) * 2 ** (c / 1200)
                vib = 1 + 0.0025 * np.sin(2 * np.pi * rng.uniform(0.15, 0.35) * t + rng.uniform(0, 6.28))
                ph = 2 * np.pi * f * np.cumsum(vib) / SR + rng.uniform(0, 6.28)
                for k, w in ((1, 1.0), (2, 0.32), (3, 0.14), (4, 0.06)):
                    x += w * np.sin(k * ph)
        out[:, ch] = _filt(x, hi=hell, order=2)
    env = np.clip(t / max(attack, 1e-3), 0, 1) * np.clip((dauer + release - t) / max(release, 1e-3), 0, 1)
    out *= env[:, None] * (0.10 / np.sqrt(max(1, len(akkord))))
    return out.astype(np.float32)


def zupf(m, dauer=1.1, hell=1.0, pan=0.0):
    """Weicher Holzton: Grundton (klingt 0,55 s), Oktave und Doppeloktave (klingen schnell ab), 6 ms Einschwingen,
    Tiefpass 4,8 kHz (klarer Anschlag). Harmonisch, also nicht metallisch."""
    n, t = _n(dauer)
    f = hz(m)
    x = (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.55)
         + 0.18 * hell * np.sin(4 * np.pi * f * t) * np.exp(-t / 0.22)
         + 0.10 * hell * np.sin(8 * np.pi * f * t) * np.exp(-t / 0.05))
    x *= np.clip(t / 0.006, 0, 1)
    return _stereo(_filt(x, hi=4800, order=2) * 0.42, pan)


def bass(m, dauer=2.0):
    """Runder Bass: Grundton mit zwei Obertoenen, Tiefpass 420 Hz, kurzer Einsatz, haelt mit 35 % und klingt aus."""
    n, t = _n(dauer)
    f = hz(m)
    x = np.sin(2 * np.pi * f * t) + 0.28 * np.sin(4 * np.pi * f * t) + 0.08 * np.sin(6 * np.pi * f * t)
    env = np.clip(t / 0.015, 0, 1) * (0.35 + 0.65 * np.exp(-t / 0.5)) * np.clip((dauer - t) / 0.35, 0, 1)
    return _stereo(_filt(x * env, hi=420, order=2) * 0.5, 0.0)


def schwelle(akkord, dauer=0.9, seed=0):
    """Anschwellende Akkordflaeche ueber dauer s, am Ende am lautesten (vor Uebergaengen und vor der Aufloesung)."""
    p = flaeche(akkord, dauer, seed=seed, hell=2800.0, attack=0.01, release=0.05)[: int(SR * dauer)]
    u = np.arange(len(p)) / max(1, len(p) - 1)
    return (p * (u ** 2.2)[:, None] * 2.4).astype(np.float32)


def akzent(akkord, bassnote, seed=0):
    """Weicher Akkordschlag: Flaeche mit schnellem Einsatz und Ausklingen, die oberen drei Toene gezupft, Bass darunter."""
    p = flaeche(akkord, 1.4, seed=seed, hell=2400.0, attack=0.012, release=1.2)
    t = np.arange(len(p)) / SR
    p = p * np.exp(-t / 0.9)[:, None] * 2.0
    teile = [p, bass(bassnote, 2.0)] + [zupf(m, 1.6, hell=0.8, pan=0.3 * (k - 1)) for k, m in enumerate(sorted(akkord)[-3:])]
    L = max(len(x) for x in teile)
    out = np.zeros((L, 2), np.float32)
    for x in teile:
        out[: len(x)] += x
    return out * 0.8


def zerlegt(akkord, oktave=12):
    """Toene fuer das Arpeggio: der Akkord eine Oktave hoeher, aufsteigend."""
    return [m + oktave for m in sorted(akkord)]


KINDS = {"flaeche": flaeche, "zupf": zupf, "bass": bass, "schwelle": schwelle, "akzent": akzent}
