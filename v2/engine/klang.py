#!/usr/bin/env python3
"""GeoCrimps-Klangset (seit 13.10.2026): spannendere Klaenge, selbst erzeugt und damit lizenzfrei per Konstruktion.

Warum selbst erzeugt: Kaufbibliotheken wie Sonniss oder Pixabay erlauben die Nutzung im Video, verbieten aber die
Weitergabe der Rohdateien; das Repo ist oeffentlich. Kenney (CC0) bleibt fuer Klicks, Ticks und Bohrhaken.

Bausteine (alle 48 kHz Stereo float32, wie motion.synth):
  sub_hit      tiefer Einschlag (Sinus faellt 90 -> 34 Hz) mit Knack-Transient     -> Hook 1, Payoff
  braam        Kino-Blechblaeser-Flaeche aus verstimmten Saegezaehnen mit Filterfahrt -> Hook 1 "x GEOLOGY"
  crunch       Gestein knackt und broeselt (Rauschkoerner)                          -> Geologie-Aufklappen, Bruch
  chalk_slap   Hand klatscht mit Kreide auf den Griff                               -> Hook 1 "CLIMBING"
  reverse      rueckwaerts anschwellender Klang, endet auf dem Treffer               -> vor Hook 1 und Payoff
  kick, hat    Puls fuer den Beat (SoundBook.pulse)                                 -> treibt Hook 2 und die Zuege
  tick         kurzer Klick fuer den Countdown der Rate-Pause
  thud         dumpfer Aufprall (z. B. auf dem Crashpad)
"""
import numpy as np

from motion import SR, _stereo


def _filt(x, lo=None, hi=None, order=4):
    """Hoch-/Tiefpass im Frequenzbereich (Butterworth-Betrag), ohne scipy."""
    n = len(x)
    if n < 8:
        return x
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    g = np.ones_like(f)
    if hi:
        g = g / np.sqrt(1 + (f / hi) ** (2 * order))
    if lo:
        g = g / np.sqrt(1 + (lo / np.maximum(f, 1e-6)) ** (2 * order))
    return np.fft.irfft(X * g, n)


def _t(dur):
    n = int(SR * dur)
    return n, np.arange(n) / SR


def sub_hit(dur=1.3, f0=90.0, f1=34.0, seed=0):
    n, t = _t(dur)
    rng = np.random.default_rng(seed)
    f = f1 + (f0 - f1) * np.exp(-t / 0.11)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.5)
    click = _filt(rng.normal(0, 1, n) * np.exp(-t / 0.005), lo=900, hi=7000) * 0.45
    x = np.tanh(1.7 * (body + click)) * 0.85
    return _stereo(x, 0.0)


def braam(dur=1.6, root=55.0, seed=0):
    n, t = _t(dur)
    rng = np.random.default_rng(seed)
    x = np.zeros(n)
    for mult, w in ((1.0, 0.55), (1.5, 0.35), (2.0, 0.3), (3.0, 0.12)):
        for det in (-0.7, 0.0, 0.8):
            ph = rng.uniform(0, 1)
            x += w * (2 * ((t * (root * mult + det) + ph) % 1.0) - 1)
    dark, bright = _filt(x, hi=380), _filt(x, hi=1500)
    open_ = np.clip(t / 0.18, 0, 1) * np.exp(-np.clip(t - 0.18, 0, None) / 0.5)    # Filter oeffnet und schliesst
    y = dark * (1 - open_) + bright * open_
    env = np.minimum(1, t / 0.035) * np.exp(-t / 0.95)
    return _stereo(np.tanh(1.6 * y * env) * 0.55, 0.0)


def crunch(dur=0.5, seed=0):
    n, t = _t(dur)
    rng = np.random.default_rng(seed)
    x = np.zeros(n)
    for _ in range(160):
        L = int(rng.integers(80, 700))
        i = int(rng.integers(0, max(1, n - L)))
        x[i:i + L] += rng.normal(0, 1, L) * np.exp(-np.arange(L) / rng.uniform(12, 90)) * rng.uniform(0.2, 1.0)
    x = _filt(x, lo=110, hi=4800) * np.exp(-t / 0.2)
    return _stereo(np.tanh(x * 0.9) * 0.75, 0.0)


def chalk_slap(seed=0):
    n, t = _t(0.4)
    rng = np.random.default_rng(seed)
    thump = np.sin(2 * np.pi * 170 * t) * np.exp(-t / 0.028)
    slap = _filt(rng.normal(0, 1, n), lo=600, hi=7500) * np.exp(-t / 0.018)
    dust = _filt(rng.normal(0, 1, n), lo=2200, hi=9500) * np.exp(-t / 0.13) * 0.22
    return _stereo(np.tanh((0.6 * thump + 0.9 * slap + dust) * 1.2) * 0.7, 0.0)


def reverse(dur=0.8, seed=0):
    n, t = _t(dur)
    rng = np.random.default_rng(seed)
    x = _filt(rng.normal(0, 1, n), lo=250, hi=6500) * 0.5 + np.sin(2 * np.pi * 220 * t) * 0.25
    return _stereo(x * (t / t[-1]) ** 3 * 0.65, 0.0)


def kick(seed=0):
    n, t = _t(0.3)
    rng = np.random.default_rng(seed)
    f = 46 + 80 * np.exp(-t / 0.032)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16)
    click = _filt(rng.normal(0, 1, n) * np.exp(-t / 0.0025), lo=1500, hi=8000) * 0.3
    return _stereo(np.tanh(1.5 * (body + click)) * 0.8, 0.0)


def hat(seed=0, open_=False):
    n, t = _t(0.18 if open_ else 0.06)
    rng = np.random.default_rng(seed)
    x = _filt(rng.normal(0, 1, n), lo=7000) * np.exp(-t / (0.08 if open_ else 0.018))
    return _stereo(x * 0.35, 0.0)


def tick(seed=0, freq=1900.0):
    n, t = _t(0.05)
    x = np.sin(2 * np.pi * freq * t) * np.exp(-t / 0.008)
    return _stereo(x * 0.5, 0.0)


def thud(seed=0):
    n, t = _t(0.45)
    rng = np.random.default_rng(seed)
    body = np.sin(2 * np.pi * (60 + 40 * np.exp(-t / 0.05)) * t) * np.exp(-t / 0.12)
    noise = _filt(rng.normal(0, 1, n), hi=900) * np.exp(-t / 0.06) * 0.5
    return _stereo(np.tanh(1.3 * (body + noise)) * 0.7, 0.0)


KINDS = {"sub_hit": sub_hit, "braam": braam, "crunch": crunch, "chalk_slap": chalk_slap, "reverse": reverse,
         "kick": kick, "hat": hat, "tick": tick, "thud": thud}


def make(kind, **kw):
    return KINDS[kind](**kw)
