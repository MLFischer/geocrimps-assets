#!/usr/bin/env python3
"""GeoCrimps V2 "Outcrop" -- Motion-Kern der Reel-Engine.

Prinzip: Alles Gezeichnete entsteht einmal in doppelter Aufloesung (outcrop.S = 2)
und wird zu 1x-Sprites verkleinert. Pro Frame wird nur noch bei 1080x1920
zusammengesetzt; Korn und Vignette sind pro Szene statisch (kleine Dateien).
Video: rgb24-Rohbilder per Pipe an ffmpeg (H.264, yuv420p, 30 fps, faststart).
Ton: Ereignisliste -> 48-kHz-Stereo-Mix in numpy -> Lautheit -14 LUFS / -1 dBTP.
"""
import math, os, random, subprocess, json, tempfile, wave
import numpy as np
from PIL import Image, ImageDraw
import outcrop as o
from outcrop import C

W, H, FPS, SR = 1080, 1920, 30, 48000
X0, XMAX = 96, 930                       # Textspalte: linker Rand, rechte Grenze (IG-Buttons)


# ------------------------------------------------------------------ easing (CD: Bewegung)
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x

def seg(t, t0, dur):
    """Fortschritt 0..1 eines Abschnitts ab t0 mit Dauer dur."""
    if dur <= 0:
        return 1.0 if t >= t0 else 0.0
    return clamp((t - t0) / dur)

def seilzug(u):          # ease-out-quart, Eintritte (250-400 ms)
    return 1 - (1 - u) ** 4

def sturz(u):            # ease-in-cubic, Brueche und Fallen (200-350 ms)
    return u ** 3

def griff(u):            # Chips: ca. 4 % Ueberschwingen (300 ms)
    c1 = 0.62; c3 = c1 + 1
    return 1 + c3 * (u - 1) ** 3 + c1 * (u - 1) ** 2

def lerp(a, b, u):
    return a + (b - a) * u


# ------------------------------------------------------------------ sprites
class Sprite:
    def __init__(self, img, x, y):
        self.img, self.x, self.y = img, x, y

    @property
    def w(self):
        return self.img.width

    @property
    def h(self):
        return self.img.height


def blank2x():
    return Image.new("RGBA", (W * o.S, H * o.S), (0, 0, 0, 0))

def sprite(draw):
    """draw(im2x) zeichnet absolut auf eine transparente 2x-Flaeche -> zugeschnittenes 1x-Sprite."""
    im = blank2x()
    draw(im)
    bb = im.getbbox()
    if not bb:
        return None
    x0, y0 = bb[0] // 2 * 2, bb[1] // 2 * 2
    x1, y1 = min(W * 2, (bb[2] + 1) // 2 * 2), min(H * 2, (bb[3] + 1) // 2 * 2)
    crop = im.crop((x0, y0, x1, y1))
    small = crop.resize(((x1 - x0) // 2, (y1 - y0) // 2), Image.LANCZOS)
    return Sprite(small, x0 // 2, y0 // 2)

def background(draw):
    """Opake Szenen-Grundflaeche (Obsidian + draw) als 1x-RGBA."""
    im = o.canvas()
    draw(im)
    return im.resize((W, H), Image.LANCZOS)

def put(frame, spr, dx=0.0, dy=0.0, op=1.0, scale=1.0, anchor=None):
    """Sprite mit Versatz, Deckkraft und Skalierung (um anchor bzw. Sprite-Mitte) einsetzen."""
    if spr is None or op <= 0.003:
        return
    img, x, y = spr.img, spr.x + dx, spr.y + dy
    if abs(scale - 1.0) > 1e-3:
        ax, ay = anchor if anchor else (spr.x + spr.w / 2, spr.y + spr.h / 2)
        nw, nh = max(1, int(round(spr.w * scale))), max(1, int(round(spr.h * scale)))
        img = img.resize((nw, nh), Image.BICUBIC)
        x = ax + (spr.x - ax) * scale + dx
        y = ay + (spr.y - ay) * scale + dy
    if op < 0.997:
        img = img.copy()
        img.putalpha(img.getchannel("A").point(lambda v, k=op: int(v * k)))
    composite(frame, img, int(round(x)), int(round(y)))

def composite(frame, img, x, y):
    """alpha_composite mit Beschnitt am Bildrand."""
    sx0, sy0 = max(0, -x), max(0, -y)
    dx0, dy0 = max(0, x), max(0, y)
    w = min(img.width - sx0, frame.width - dx0)
    h = min(img.height - sy0, frame.height - dy0)
    if w <= 0 or h <= 0:
        return
    if (sx0, sy0, w, h) != (0, 0, img.width, img.height):
        img = img.crop((sx0, sy0, sx0 + w, sy0 + h))
    frame.alpha_composite(img, (dx0, dy0))

def reveal(spr, u):
    """Sprite von links nach rechts aufdecken (Kreide-Wisch zeichnet sich)."""
    if spr is None or u <= 0:
        return None
    if u >= 1:
        return spr
    w = max(1, int(spr.w * u))
    return Sprite(spr.img.crop((0, 0, w, spr.h)), spr.x, spr.y)

def zoomed(bg, scale, cx, cy):
    """Hintergrund um (cx, cy) vergroessern (langsamer Push-in)."""
    if scale <= 1.0005:
        return bg.copy()
    w, h = W / scale, H / scale
    x0 = clamp(cx - w * (cx / W), 0, W - w)
    y0 = clamp(cy - h * (cy / H), 0, H - h)
    return bg.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h))


# ------------------------------------------------------------------ helfer fuer Text-Sprites
def fit(s, role, size, maxw=XMAX - X0):
    while o.text_width(s, role, size) > maxw and size > 40:
        size -= 2
    return size

def lines_sprite(rows, y, role="display", size=176, lh=0.93, fill=C["magnesia"], x=X0):
    sz = min(fit(r, role, size) for r in rows)
    def d(im):
        yy = y
        for r in rows:
            o.text(im, x, yy, r, role, sz, fill)
            yy += sz * lh
    return sprite(d), y + sz * lh * len(rows)

def text_sprite(s, x, y, role, size, fill, anchor="la", tracking=0.0):
    return sprite(lambda im: o.text(im, x, y, s, role, size, fill, anchor=anchor, tracking=tracking))


# ------------------------------------------------------------------ finish: statisches Korn + Vignette
class Finish:
    def __init__(self, grain=2.6, vignette=0.18):
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        self.vig = (1 - vignette * np.clip(d - 0.55, 0, 1))[..., None].astype(np.float32)
        self.grain_sigma = grain
        self._grain = {}

    def grain(self, seed):
        if seed not in self._grain:
            rng = np.random.default_rng(seed)
            self._grain[seed] = rng.normal(0, self.grain_sigma, (H, W, 1)).astype(np.float32)
        return self._grain[seed]

    def __call__(self, frame, seed):
        a = np.asarray(frame.convert("RGB"), dtype=np.float32)
        a = (a + self.grain(seed)) * self.vig
        return np.clip(a, 0, 255).astype(np.uint8)


# ------------------------------------------------------------------ Video
def encode(frames_iter, n_frames, out_mp4, audio_wav=None, crf=20):
    os.makedirs(os.path.dirname(os.path.abspath(out_mp4)), exist_ok=True)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    if audio_wav:
        cmd += ["-i", audio_wav]
    cmd += ["-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-pix_fmt", "yuv420p",
            "-profile:v", "high", "-level:v", "4.1", "-g", str(FPS * 2), "-bf", "2",
            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
            "-movflags", "+faststart"]
    if audio_wav:
        cmd += ["-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-ac", "2", "-shortest"]
    cmd += [out_mp4]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    k = 0
    for arr in frames_iter:
        p.stdin.write(arr.tobytes())
        k += 1
    p.stdin.close()
    if p.wait() != 0 or k != n_frames:
        raise RuntimeError(f"ffmpeg fehlgeschlagen oder Frames fehlen ({k}/{n_frames})")


# ------------------------------------------------------------------ Ton
def load_audio(path, gain_db=0.0):
    """Beliebige Tondatei -> float32 Stereo 48 kHz (via ffmpeg)."""
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "2",
                          "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()
    return a * (10 ** (gain_db / 20))

def _env(n, attack=0.005, release=0.2):
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    r = np.exp(-np.clip(t - attack, 0, None) / max(release, 1e-4))
    return a * r

def _stereo(x, pan=0.0):
    l, r = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
    return np.stack([x * l, x * r], axis=1).astype(np.float32)

def _lowpass(x, a):
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)):          # einfacher 1-Pol-Tiefpass
        acc += a * (x[i] - acc); y[i] = acc
    return y

def synth(kind, seed=0, dur=None, freq=None):
    """Selbst erzeugte Klaenge (lizenzfrei per Konstruktion)."""
    rng = np.random.default_rng(seed)
    if kind == "drip":                      # Wassertropfen: kurzer, nach oben gleitender Ton
        n = int(SR * 0.16); t = np.arange(n) / SR
        f = 900 + 1700 * (t / t[-1]) ** 2
        ph = 2 * np.pi * np.cumsum(f) / SR
        x = np.sin(ph) * _env(n, 0.002, 0.045) * 0.55
        return _stereo(x, rng.uniform(-0.3, 0.3))
    if kind == "whoosh":                    # Luftzug: gefiltertes Rauschen mit Huellkurve
        n = int(SR * (dur or 0.5)); t = np.linspace(0, 1, n)
        noise = rng.normal(0, 1, n).astype(np.float32)
        x = np.diff(np.concatenate([[0], noise])) * 0.35 + noise * 0.15
        env = np.sin(np.pi * t) ** 2
        return _stereo(x * env * 0.5, 0.0)
    if kind == "rumble":                    # tiefes Grollen (Zeit)
        n = int(SR * (dur or 1.6)); t = np.arange(n) / SR
        x = sum(np.sin(2 * np.pi * f0 * t + rng.uniform(0, 6)) * w for f0, w in ((41, 0.6), (55, 0.4), (63, 0.25)))
        x *= np.minimum(1, t / 0.4) * np.minimum(1, (t[-1] - t) / 0.6)
        return _stereo(x * 0.35, 0.0)
    if kind == "tone":                      # Klanglogo: weicher Glockenton
        n = int(SR * (dur or 0.55)); t = np.arange(n) / SR
        f0 = freq or 523.25
        x = (np.sin(2 * np.pi * f0 * t) + 0.35 * np.sin(2 * np.pi * 2 * f0 * t) + 0.12 * np.sin(2 * np.pi * 3 * f0 * t))
        return _stereo(x * _env(n, 0.006, 0.22) * 0.32, 0.0)
    if kind == "clap":                      # Kreide-Klatsch: Rauschstoss
        n = int(SR * 0.22)
        x = rng.normal(0, 1, n) * _env(n, 0.001, 0.035)
        x = np.diff(np.concatenate([[0], x]))
        return _stereo(x * 0.6, 0.0)
    if kind == "pad":                       # ruhige Flaeche unter den Geraeuschen (Grundton A)
        n = int(SR * (dur or 10.0)); t = np.arange(n) / SR
        x = np.zeros(n)
        for f0, w in ((110.0, 0.5), (164.81, 0.32), (220.0, 0.22), (329.63, 0.08)):
            lfo = 1 + 0.004 * np.sin(2 * np.pi * rng.uniform(0.08, 0.2) * t + rng.uniform(0, 6))
            x += w * np.sin(2 * np.pi * f0 * np.cumsum(lfo) / SR)
        x *= np.minimum(1, t / 1.2) * np.minimum(1, (t[-1] - t) / 0.8)
        return _stereo(x * 0.25, 0.0)
    if kind == "riser":                     # steigender Ton vor der Aufloesung
        n = int(SR * (dur or 0.9)); t = np.arange(n) / SR; u = t / t[-1]
        f = 196 * 2 ** (u * 1.0)
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR)
        return _stereo(x * (u ** 2) * 0.35, 0.0)
    if kind == "fizz":                      # Aufloesen: feines Knistern
        n = int(SR * (dur or 1.0)); x = np.zeros(n, np.float32)
        for _ in range(int(60 * (dur or 1.0))):
            i = rng.integers(0, n - 400); x[i:i + 400] += rng.normal(0, 1, 400) * np.exp(-np.arange(400) / 60) * rng.uniform(0.1, 0.4)
        t = np.linspace(0, 1, n); x *= np.sin(np.pi * t)
        return _stereo(np.diff(np.concatenate([[0], x])) * 0.6, 0.0)
    if kind in KINO:                        # Kino-Set (seit 14.10.2026), siehe unten
        return KINO[kind](rng, dur, freq)
    raise ValueError(kind)


# ------------------------------------------------------------------ Kino-Set (14.10.2026): Bass, Braam, Beat, Swell
# Alles selbst erzeugt (Sinus, Saegezahn, Rauschen, Filter) und damit lizenzfrei. Pegel relativ; die Mischung
# wird ohnehin auf -14 LUFS normiert. Filter: scipy.signal (Butterworth, zweite Ordnung).
from scipy import signal as _sig


def _bw(x, f, kind="low", order=2):
    sos = _sig.butter(order, f, btype=kind, fs=SR, output="sos")
    return _sig.sosfilt(sos, x).astype(np.float32)

def _saw(ph):
    return 2.0 * (ph - np.floor(ph + 0.5))

def _k_sub(rng, dur, freq):
    """Tiefer Einschlag: Sinus faellt in 50 ms von ~130 auf ~38 Hz, Saettigung, kurzer Klick."""
    n = int(SR * (dur or 1.3)); t = np.arange(n) / SR
    f = (freq or 38.0) + 95 * np.exp(-t / 0.05)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.5)
    x = np.tanh(2.4 * x) / np.tanh(2.4)
    click = np.diff(np.concatenate([[0], rng.normal(0, 1, n) * np.exp(-t / 0.003)])) * 0.25
    # Handy-Lautsprecher geben unter ~200 Hz kaum etwas wieder: hoerbarer Koerper (220->90 Hz) und Anschlag (bis 3 kHz)
    fb = 90 + 130 * np.exp(-t / 0.03)
    body = np.sin(2 * np.pi * np.cumsum(fb) / SR) * np.exp(-t / 0.09)
    hit = _bw(rng.normal(0, 1, n), 3000) * np.exp(-t / 0.018)
    x = (0.75 * x + 0.55 * np.tanh(1.8 * body) + 0.35 * hit + click) * np.minimum(1, t / 0.002) * np.minimum(1, (t[-1] - t) / 0.05)
    return _stereo(x * 0.75)

def _k_braam(rng, dur, freq):
    """Kino-Blech: verstimmte Saegezaehne (Grundton, Quinte, Oktaven), Filter oeffnet kurz und schliesst."""
    n = int(SR * (dur or 1.4)); t = np.arange(n) / SR; f0 = freq or 110.0
    x = np.zeros(n)
    for mul, w in ((1.0, 1.0), (1.007, 0.8), (0.993, 0.8), (1.5, 0.4), (2.0, 0.55), (3.0, 0.2), (4.0, 0.12)):
        x += w * _saw(f0 * mul * t + rng.uniform(0, 1))
    x += 0.9 * np.sin(2 * np.pi * f0 / 2 * t)                              # Fundament eine Oktave tiefer
    bright, dark = _bw(x, 3200), _bw(x, 420)
    eb = np.exp(-t / 0.45)
    y = bright * eb + dark * (1 - eb)
    y *= np.minimum(1, t / 0.025) * (0.25 + 0.75 * np.exp(-t / 0.8)) * np.minimum(1, (t[-1] - t) / 0.25)
    y = np.tanh(1.6 * y / (np.max(np.abs(y)) + 1e-9))
    l = _bw(y + 0.02 * rng.normal(0, 1, n), 9000); r = np.roll(l, int(SR * 0.012))       # leichte Breite
    return np.stack([l, r], axis=1).astype(np.float32) * 0.6

def _k_kick(rng, dur, freq):
    n = int(SR * 0.32); t = np.arange(n) / SR
    f = 46 + 115 * np.exp(-t / 0.032)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.15)
    x = np.tanh(1.6 * x) + np.diff(np.concatenate([[0], rng.normal(0, 1, n) * np.exp(-t / 0.002)])) * 0.15
    x += 0.6 * _bw(_bw(rng.normal(0, 1, n), 1200, "high"), 5000) * np.exp(-t / 0.006)   # Anschlag, auch auf dem Handy hoerbar
    x += 0.45 * np.sin(2 * np.pi * 185 * t) * np.exp(-t / 0.05)
    return _stereo(x * 0.75)

def _k_hat(rng, dur, freq):
    n = int(SR * (dur or 0.07)); t = np.arange(n) / SR
    x = _bw(rng.normal(0, 1, n), 7500, "high") * np.exp(-t / 0.018)
    return _stereo(x * 0.5, rng.uniform(-0.25, 0.25))

def _k_swell(rng, dur, freq):
    """Rueckwaerts anschwellendes Rauschen (wie ein rueckwaerts gespieltes Becken), endet hart."""
    n = int(SR * (dur or 0.8)); t = np.arange(n) / SR; u = t / t[-1]
    noise = rng.normal(0, 1, n)
    x = _bw(noise, 900, "high") * (1 - u) * 0.4 + _bw(noise, 3500, "high") * u
    x *= u ** 2.6 * np.minimum(1, (t[-1] - t) / 0.006)
    return _stereo(x * 0.6)

def _k_scan(rng, dur, freq):
    """Abtasten: gleitender Ton mit schnellem Tremolo plus feines Rauschen (Blick ins Gestein)."""
    n = int(SR * (dur or 0.9)); t = np.arange(n) / SR; u = t / t[-1]
    f = 420 * 2 ** (u * 2.3)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.55 + 0.45 * np.sign(np.sin(2 * np.pi * 26 * t)))
    x = x * 0.5 + _bw(rng.normal(0, 1, n), 2500, "high") * 0.25
    x *= np.sin(np.pi * u) ** 0.6
    return _stereo(x * 0.45)

def _k_shimmer(rng, dur, freq):
    """Kristall: hohe, leicht verstimmte Teiltoene mit langem Ausklang, breit verteilt."""
    n = int(SR * (dur or 1.3)); t = np.arange(n) / SR
    l = np.zeros(n); r = np.zeros(n)
    for k in range(7):
        f = (freq or 1760.0) * rng.choice([1, 1.5, 2, 2.5, 3, 4]) * rng.uniform(0.995, 1.005)
        ph = rng.uniform(0, 6); dec = rng.uniform(0.35, 1.0); pan = rng.uniform(-0.8, 0.8)
        s = np.sin(2 * np.pi * f * t + ph) * np.exp(-t / dec) * np.minimum(1, t / rng.uniform(0.002, 0.03))
        l += s * math.cos((pan + 1) * math.pi / 4); r += s * math.sin((pan + 1) * math.pi / 4)
    return (np.stack([l, r], axis=1) / 7 * 0.9).astype(np.float32)

def _k_tick(rng, dur, freq):
    """Uhr-Tick fuer Rate-Pausen."""
    n = int(SR * 0.06); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * (freq or 2600) * t) * np.exp(-t / 0.004) + 0.6 * np.sin(2 * np.pi * 1180 * t) * np.exp(-t / 0.012)
    return _stereo(x * 0.5)

def _k_crack(rng, dur, freq):
    """Gesteinsknacken: mehrere sehr kurze Rauschimpulse in schneller Folge, tiefpassig."""
    n = int(SR * (dur or 0.35)); x = np.zeros(n)
    k = 0
    while k < n - 600:
        L = int(SR * rng.uniform(0.004, 0.012))
        x[k:k + L] += rng.normal(0, 1, L) * np.exp(-np.arange(L) / (L / 4)) * rng.uniform(0.4, 1.0)
        k += int(SR * rng.uniform(0.008, 0.045))
    x = _bw(x, 4200) + 0.3 * _bw(x, 180)
    x *= np.exp(-np.arange(n) / SR / 0.12)
    return _stereo(x * 0.9)

KINO = {"sub": _k_sub, "braam": _k_braam, "kick": _k_kick, "hat": _k_hat, "swell": _k_swell,
        "scan": _k_scan, "shimmer": _k_shimmer, "tick2": _k_tick, "crack": _k_crack}


def beat(t0, t1, bpm=118.0, root=55.0, build_from=None, seed=3):
    """Puls unter dem Erzaehlteil: Kick auf jedem Schlag, Hi-Hat auf den Zwischenschlaegen, ab build_from zusaetzlich
    Sechzehntel und ein Bass-Ton auf jedem Schlag (Steigerung). Rueckgabe: Liste (zeit, samples, gain_db) fuer mix()."""
    rng = np.random.default_rng(seed); ev = []
    beat_s = 60.0 / bpm; k = 0
    kick = KINO["kick"](rng, None, None)
    while t0 + k * beat_s < t1 - 0.05:
        t = t0 + k * beat_s
        build = build_from is not None and t >= build_from
        ev.append((t, kick, -4.0 if build else -7.0))
        ev.append((t + beat_s / 2, KINO["hat"](rng, None, None), -10.0 if build else -13.0))
        if build:
            for q in (0.25, 0.75):
                ev.append((t + beat_s * q, KINO["hat"](rng, 0.04, None), -16.0))
            nb = int(SR * beat_s * 0.9); tt = np.arange(nb) / SR
            bass = np.tanh(1.5 * np.sin(2 * np.pi * root * tt)) * np.exp(-tt / 0.22) * np.minimum(1, tt / 0.004)
            ev.append((t, _stereo(bass * 0.7), -9.0))
        k += 1
    return ev

def limit(x, crest_db=11.0, release_s=0.08, look_s=0.003):
    """Spitzenbegrenzer (14.10.2026): Spitzen hoechstens crest_db ueber dem Effektivpegel der lauten Abschnitte.
    Ohne ihn scheitert -14 LUFS bei <= -1 dBTP an den Bass-Einschlaegen des Kino-Sets (gemessen r004: -14,7 LUFS).
    Sofortiger Angriff mit kurzer Vorausschau, exponentielles Loslassen; beide Kanaele gemeinsam (kein Stereo-Wandern)."""
    from scipy.ndimage import maximum_filter1d
    a = np.max(np.abs(x), axis=1)
    win = int(SR * 0.4)
    rms = np.sqrt(np.convolve(a ** 2, np.ones(win) / win, mode="same"))
    ref = np.percentile(rms[rms > 1e-4], 90) if np.any(rms > 1e-4) else 1e-4
    thr = ref * 10 ** (crest_db / 20)
    L = max(1, int(SR * look_s))
    pk = maximum_filter1d(a, size=2 * L + 1)
    g = np.minimum(1.0, thr / np.maximum(pk, 1e-9)).astype(np.float64)
    rel = 1 - math.exp(-1.0 / (SR * release_s))
    out = np.empty_like(g); cur = 1.0
    for i in range(len(g)):                       # Loslassen glaetten (Angriff sofort)
        gi = g[i]
        cur = gi if gi < cur else cur + (gi - cur) * rel
        out[i] = cur
    return (x * out[:, None]).astype(np.float32)

def pitch(smp, ratio):
    """Tonhoehe per Neuabtastung aendern (Dauer aendert sich mit)."""
    n = int(len(smp) / ratio)
    idx = np.arange(n) * ratio
    return np.stack([np.interp(idx, np.arange(len(smp)), smp[:, c]) for c in range(2)], axis=1).astype(np.float32)

def duck(bed, events, depth_db=-8.0, hold=0.25):
    """Flaeche unter Ereignissen absenken (einfaches Sidechain)."""
    g = np.ones(len(bed), np.float32)
    for t0, smp, _ in events:
        i0 = int(t0 * SR); i1 = min(len(bed), i0 + int(SR * hold) + len(smp) // 2)
        if i0 < len(bed):
            g[i0:i1] = np.minimum(g[i0:i1], 10 ** (depth_db / 20))
    k = int(SR * 0.05)
    g = np.convolve(g, np.ones(k) / k, mode="same").astype(np.float32)
    return bed * g[:, None]

def mix(events, duration):
    """events: Liste (zeit_s, samples[n,2], gain_db). Ergebnis float32 [N,2]."""
    out = np.zeros((int(SR * duration) + SR, 2), np.float32)
    for t0, smp, gdb in events:
        i = int(t0 * SR)
        if i >= len(out):
            continue
        s = smp[: len(out) - i] * (10 ** (gdb / 20))
        out[i:i + len(s)] += s
    return out[: int(SR * duration)]

def write_wav(path, a):
    a = np.clip(a, -1, 1)
    pcm = (a * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())

def loudnorm(src_wav, dst_wav, target=-14.0, tp=-1.0, lra=11.0):
    """Zweistufige EBU-R128-Normierung (ffmpeg loudnorm). Rueckgabe: Messwerte nach der Normierung."""
    p1 = subprocess.run(["ffmpeg", "-hide_banner", "-i", src_wav, "-af",
                         f"loudnorm=I={target}:TP={tp}:LRA={lra}:print_format=json", "-f", "null", "-"],
                        capture_output=True, text=True)
    js = json.loads(p1.stderr[p1.stderr.rindex("{"):p1.stderr.rindex("}") + 1])
    af = (f"loudnorm=I={target}:TP={tp}:LRA={lra}:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
          f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:"
          f"linear=true:print_format=json")
    p2 = subprocess.run(["ffmpeg", "-hide_banner", "-y", "-i", src_wav, "-af", af, "-ar", str(SR), dst_wav],
                        capture_output=True, text=True)
    js2 = json.loads(p2.stderr[p2.stderr.rindex("{"):p2.stderr.rindex("}") + 1])
    return {"input_i": js["input_i"], "output_i": js2["output_i"], "output_tp": js2["output_tp"],
            "normalization_type": js2.get("normalization_type")}

def master(src_wav, dst_wav, target=-14.0, tp=-2.5, tol=0.3, max_iter=5):
    """Lautheit so einstellen, dass das fertige AAC im MP4 bei target LUFS und <= -1 dBTP liegt.
    loudnorm verfehlt bei kurzen, transientenreichen Mischungen das Ziel; daher Probe-Encodes und Nachregeln."""
    t, meas = target, {}
    probe = dst_wav + ".probe.m4a"
    for _ in range(max_iter):
        loudnorm(src_wav, dst_wav, target=t, tp=tp)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", dst_wav, "-c:a", "aac", "-b:a", "192k",
                        "-ar", str(SR), probe], check=True)
        meas = measure(probe)
        ok_i = abs(meas.get("I_LUFS", -99) - target) <= tol
        ok_tp = meas.get("TP_dBFS", 0) <= -1.0
        if ok_i and ok_tp:
            break
        if not ok_i:
            t = max(-30.0, min(-5.0, t + (target - meas["I_LUFS"])))
        if not ok_tp:
            tp -= 0.5
    if os.path.exists(probe):
        os.remove(probe)
    return {"loudnorm_ziel": round(t, 2), "tp_grenze": tp, **meas}

def measure(path):
    """Integrierte Lautheit und True Peak einer fertigen Datei (ebur128)."""
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    txt = p.stderr[p.stderr.rfind("Summary:"):]
    vals = {}
    for line in txt.splitlines():
        line = line.strip()
        if line.startswith("I:"):
            vals["I_LUFS"] = float(line.split()[1])
        if line.startswith("Peak:"):
            vals["TP_dBFS"] = float(line.split()[1])
    return vals
