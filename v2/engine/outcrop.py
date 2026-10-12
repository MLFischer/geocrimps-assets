#!/usr/bin/env python3
"""GeoCrimps V2 "Outcrop" -- frame prototype (Design-System-Referenz).

Zweck: zeigt, dass das CD V2 mit der bestehenden Python-Toolchain (PIL) automatisch
renderbar ist. Kein fertiger Motion-Renderer: liefert Keyframes 1080x1920 fuer
Storyboards und Cover. Interne Aufloesung 2x (Supersampling), Ausgabe 1080x1920.

Tokens: siehe Assets/V2/tokens.json (gleiche Werte). Schriften: Assets/V2/Fonts (OFL).
Aufruf der Beispiele: python3 storyboard.py  bzw.  python3 covergrid.py  (Ausgabe: ../Assets/V2/Storyboard)
"""
import math, random, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = 2                      # supersampling factor
W, H = 1080, 1920
FD = os.environ.get("GC_FONTS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")) + "/"

# ---------------------------------------------------------------- tokens
C = dict(obsidian="#0E1113", graphite="#1A1F24", line="#2C343B", slate="#8C969F",
         magnesia="#F1EFE9", water="#5AA9FF", heat="#FF8A3D", ice="#CDEFFF", bio="#7ED68F")
# ICS / CGMW period colours (via Macrostrat API, abgerufen 2026-10-09), Grenzen in Ma
AGE = [("Quaternary", 0, 2.58, "#F9F97F"), ("Neogene", 2.58, 23.04, "#FFE619"),
       ("Paleogene", 23.04, 66, "#FD9A52"), ("Cretaceous", 66, 143.1, "#7FC64E"),
       ("Jurassic", 143.1, 201.4, "#34B2C9"), ("Triassic", 201.4, 251.902, "#812B92"),
       ("Permian", 251.902, 298.9, "#F04028"), ("Carboniferous", 298.9, 358.86, "#67A599"),
       ("Devonian", 358.86, 419.62, "#CB8C37"), ("Silurian", 419.62, 443.1, "#B3E1B6"),
       ("Ordovician", 443.1, 486.85, "#009270"), ("Cambrian", 486.85, 538.8, "#7FA056")]

def age_of(ma):
    for name, t, b, col in AGE:
        if t <= ma < b:
            return name, col
    return "Precambrian", "#FF70B8"

def rgb(h, a=255):
    h = h.lstrip("#"); return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)

def lum(h):
    r, g, b, _ = rgb(h)
    f = lambda c: (c/255)/12.92 if c/255 <= 0.03928 else (((c/255)+0.055)/1.055)**2.4
    return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b)

def contrast(a, b):
    la, lb = lum(a), lum(b); hi, lo = max(la, lb), min(la, lb); return (hi+0.05)/(lo+0.05)

def on_color(bg):
    """Text colour for a fill: obsidian or magnesia, whichever contrasts more."""
    return C["obsidian"] if contrast(bg, C["obsidian"]) >= contrast(bg, C["magnesia"]) else C["magnesia"]

def shade(h, k):
    r, g, b, _ = rgb(h); return "#%02X%02X%02X" % (int(r*k), int(g*k), int(b*k))

# ---------------------------------------------------------------- fonts
_FC = {}
FONTS = {
    "display": ("BigShoulders[opsz,wght].ttf", {b"Weight": 900, b"Optical size": 72}),
    "display_xb": ("BigShoulders[opsz,wght].ttf", {b"Weight": 800, b"Optical size": 72}),
    "stencil": ("BigShouldersStencil[opsz,wght].ttf", {b"Weight": 800, b"Optical size": 72}),
    "text": ("Archivo[wdth,wght].ttf", {b"Weight": 560, b"Width": 100}),
    "text_b": ("Archivo[wdth,wght].ttf", {b"Weight": 700, b"Width": 100}),
    "mono": ("JetBrainsMono[wght].ttf", {b"Weight": 600}),
}

def font(role, size):
    key = (role, size)
    if key not in _FC:
        path, ax = FONTS[role]
        f = ImageFont.truetype(FD + path, int(size*S))
        axes = f.get_variation_axes()
        f.set_variation_by_axes([ax.get(a["name"], a["default"]) for a in axes])
        _FC[key] = f
    return _FC[key]

# ---------------------------------------------------------------- canvas
def canvas(bg=C["obsidian"]):
    return Image.new("RGBA", (W*S, H*S), rgb(bg))

def finish(im, grain=5, vignette=0.18, seed=7):
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    rng = np.random.default_rng(seed)
    a += rng.normal(0, grain, a.shape[:2])[..., None]
    if vignette:
        yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
        d = np.sqrt(((xx - a.shape[1]/2)/(a.shape[1]/2))**2 + ((yy - a.shape[0]/2)/(a.shape[0]/2))**2)
        a *= (1 - vignette*np.clip(d-0.55, 0, 1))[..., None]
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return out.resize((W, H), Image.LANCZOS)

def P(*xy):  # scale coordinates
    return tuple(v*S for v in xy)

# ---------------------------------------------------------------- text
def text(im, x, y, s, role, size, fill, anchor="la", tracking=0.0):
    d = ImageDraw.Draw(im)
    f = font(role, size)
    if not tracking:
        d.text((x*S, y*S), s, font=f, fill=rgb(fill) if isinstance(fill, str) else fill, anchor=anchor)
        return d.textbbox((x*S, y*S), s, font=f, anchor=anchor)
    # manual tracking (labels)
    cx = x*S
    if anchor[0] in "mr":
        total = sum(f.getlength(ch) for ch in s) + tracking*size*S*(len(s)-1)
        cx -= total/2 if anchor[0] == "m" else total
    for ch in s:
        d.text((cx, y*S), ch, font=f, fill=rgb(fill), anchor="l" + anchor[1])
        cx += f.getlength(ch) + tracking*size*S
    return None

def text_width(s, role, size):
    return font(role, size).getlength(s)/S

# ---------------------------------------------------------------- chalk
def chalk_swipe(im, x0, y0, x1, y1, seed=3, color=C["magnesia"]):
    """Rough chalk band behind a word: ragged edges, dusty holes, brush streaks."""
    rnd = random.Random(seed); rng = np.random.default_rng(seed)
    w, h = int((x1-x0+60)*S), int((y1-y0+40)*S)
    mask = Image.new("L", (w, h), 0); d = ImageDraw.Draw(mask)
    top, bot = [], []
    n = 40
    yt, yb = 20*S, h-20*S
    for i in range(n+1):
        x = 30*S + (w-60*S)*i/n
        yt += rnd.uniform(-2.2, 2.2)*S; yb += rnd.uniform(-2.2, 2.2)*S
        top.append((x + rnd.uniform(-3, 3)*S, yt)); bot.append((x + rnd.uniform(-3, 3)*S, yb))
    # tapered, slightly skewed ends
    poly = [(8*S, h*0.55)] + top + [(w-6*S, h*0.42)] + bot[::-1]
    d.polygon(poly, fill=255)
    m = np.asarray(mask).astype(np.float32)/255
    noise = rng.random((h, w))
    noise = np.asarray(Image.fromarray((noise*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2*S))).astype(np.float32)/255
    holes = (noise > 0.58).astype(np.float32)*0.85
    streak = np.zeros((h, w), np.float32)
    for _ in range(26):
        yy = rnd.randint(0, h-1); thick = rnd.randint(1, 3)
        streak[max(0, yy-thick):yy+thick, :] += rnd.uniform(0.25, 0.6)
    alpha = np.clip(m*(1-holes)*(1-np.clip(streak, 0, 0.55)), 0, 1)
    edge = np.asarray(mask.filter(ImageFilter.GaussianBlur(5*S))).astype(np.float32)/255
    alpha *= np.clip(edge*1.6, 0, 1)
    a = Image.fromarray((alpha*255).astype(np.uint8)).rotate(rnd.uniform(-1.6, 0.6), resample=Image.BICUBIC, expand=False)
    layer = Image.new("RGBA", (w, h), rgb(color)); layer.putalpha(a)
    im.alpha_composite(layer, (int((x0-30)*S), int((y0-20)*S)))

def chalk_ticks(im, x, y, angle_deg=-35, n=3, length=34, gap=16, color=C["magnesia"], seed=1):
    """Three short chalk dashes, the way climbers tick a hold."""
    rnd = random.Random(seed); d = ImageDraw.Draw(im)
    a = math.radians(angle_deg); nx, ny = -math.sin(a), math.cos(a)
    for i in range(n):
        off = (i-(n-1)/2)*gap
        cx, cy = x + nx*off, y + ny*off
        dx, dy = math.cos(a)*length/2, math.sin(a)*length/2
        d.line([P(cx-dx, cy-dy), P(cx+dx+rnd.uniform(-3, 3), cy+dy+rnd.uniform(-3, 3))],
               fill=rgb(color, 235), width=int(7*S))

# ---------------------------------------------------------------- logo mark
LOGO = [
 "M -46,10 C -50,-14 -34,-34 -8,-38 C 20,-42 44,-30 48,-8 C 52,14 40,32 14,38 C -14,44 -42,34 -46,10 Z",
 "M -30,8 C -33,-8 -22,-22 -4,-25 C 16,-28 32,-19 35,-4 C 38,11 29,22 10,26 C -10,30 -27,22 -30,8 Z",
 "M -14,6 C -16,-3 -9,-11 2,-12 C 13,-13 22,-8 23,0 C 24,9 18,15 7,16 C -4,18 -12,14 -14,6 Z"]

def _bezier_path(d, steps=24):
    tok = d.replace(",", " ").split(); pts = []; i = 0; cur = None
    while i < len(tok):
        t = tok[i]
        if t == "M":
            cur = (float(tok[i+1]), float(tok[i+2])); pts.append(cur); i += 3
        elif t == "C":
            p1 = (float(tok[i+1]), float(tok[i+2])); p2 = (float(tok[i+3]), float(tok[i+4])); p3 = (float(tok[i+5]), float(tok[i+6]))
            for k in range(1, steps+1):
                u = k/steps
                x = (1-u)**3*cur[0] + 3*(1-u)**2*u*p1[0] + 3*(1-u)*u**2*p2[0] + u**3*p3[0]
                y = (1-u)**3*cur[1] + 3*(1-u)**2*u*p1[1] + 3*(1-u)*u**2*p2[1] + u**3*p3[1]
                pts.append((x, y))
            cur = p3; i += 7
        elif t == "Z":
            i += 1
        else:
            i += 1
    return pts

def logo_mark(im, cx, cy, scale, color=C["magnesia"], width=5.5, rings=3):
    d = ImageDraw.Draw(im)
    for path in LOGO[:rings]:
        pts = [P(cx + x*scale, cy + y*scale) for x, y in _bezier_path(path)]
        d.line(pts + [pts[1]], fill=rgb(color), width=max(1, int(width*scale*S)), joint="curve")

# ---------------------------------------------------------------- isolines
def contour_field(im, cx, cy, n=9, r0=60, step=46, color=C["line"], alpha=150, width=2.2, seed=4, squash=0.78):
    rnd = random.Random(seed)
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    harm = [(k, rnd.uniform(0.02, 0.07), rnd.uniform(0, 2*math.pi)) for k in (2, 3, 5)]
    for i in range(n):
        r = r0 + i*step; pts = []
        for j in range(181):
            th = 2*math.pi*j/180
            rr = r*(1 + sum(a*math.cos(k*th + ph + i*0.13) for k, a, ph in harm))
            pts.append(P(cx + rr*math.cos(th), cy + rr*squash*math.sin(th)))
        d.line(pts, fill=rgb(color, alpha), width=int(width*S))
    im.alpha_composite(layer)

# ---------------------------------------------------------------- route rail (progress topo)
RAIL_X = 56
def route_rail(im, clipped, total, y_top=330, y_bot=1300, logo_on=False):
    d = ImageDraw.Draw(im)
    d.line([P(RAIL_X, y_top+24), P(RAIL_X, y_bot)], fill=rgb(C["line"]), width=int(4*S))
    ys = [y_bot - (y_bot-y_top-60)*(i+0.5)/total for i in range(total)]
    for i, yv in enumerate(ys):
        on = i < clipped
        if on:
            d.line([P(RAIL_X, min(y_bot, yv+ (y_bot-y_top)/total)), P(RAIL_X, yv)], fill=rgb(C["magnesia"]), width=int(4*S))
        col = rgb(C["magnesia"]) if on else rgb(C["slate"], 150)
        s = 10
        d.line([P(RAIL_X-s, yv-s), P(RAIL_X+s, yv+s)], fill=col, width=int(4*S))
        d.line([P(RAIL_X-s, yv+s), P(RAIL_X+s, yv-s)], fill=col, width=int(4*S))
    logo_mark(im, RAIL_X, y_top, 0.26, C["magnesia"] if logo_on else C["slate"], width=7)

# ---------------------------------------------------------------- hold label (chip)
def hold_label(im, x, y, label, fill, size=30, role="mono", pad=(22, 14), text_color=None):
    f = font(role, size); tw = f.getlength(label)/S; th = size*0.95
    w, h = tw + 2*pad[0], th + 2*pad[1]
    d = ImageDraw.Draw(im)
    r = h*0.48
    # hold silhouette: rounded body with one sharp, slightly lifted 'crimp edge' at the top right
    poly = []
    for j in range(0, 91, 6):
        a = math.radians(180 + j); poly.append(P(x + r + r*math.cos(a), y + r + r*math.sin(a)))
    poly += [P(x + w - 10, y - 4), P(x + w, y + 8)]
    for j in range(0, 91, 6):
        a = math.radians(j); poly.append(P(x + w - r*0.6 + r*0.6*math.cos(a), y + h - r*0.6 + r*0.6*math.sin(a)))
    for j in range(90, 181, 6):
        a = math.radians(j); poly.append(P(x + r + r*math.cos(a), y + h - r + r*math.sin(a)))
    d.polygon(poly, fill=rgb(fill))
    tc = text_color or on_color(fill)
    d.text(P(x + pad[0], y + h/2 + 1), label, font=f, fill=rgb(tc), anchor="lm")
    return w, h

# ---------------------------------------------------------------- lithology patterns (FGDC-inspiriert)
def _pattern_layer(size, kind, color, seed=2, scale=1.0):
    w, h = size; L = Image.new("RGBA", size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    rnd = random.Random(seed); col = rgb(color); s = int(scale*S)
    if kind == "limestone":   # brick
        bh, bw = 40*s, 84*s
        for r, y in enumerate(range(0, h, bh)):
            d.line([(0, y), (w, y)], fill=col, width=3*s)
            off = 0 if r % 2 == 0 else bw//2
            for x in range(-bw + off, w, bw):
                d.line([(x, y), (x, y + bh)], fill=col, width=3*s)
    elif kind == "dolomite":  # brick with diagonals
        bh, bw = 40*s, 84*s
        for r, y in enumerate(range(0, h, bh)):
            d.line([(0, y), (w, y)], fill=col, width=3*s)
            off = 0 if r % 2 == 0 else bw//2
            for x in range(-bw + off, w, bw):
                d.line([(x, y), (x + bh*0.7, y + bh)], fill=col, width=3*s)
    elif kind == "sandstone": # stipple
        for _ in range(int(w*h/(900*s*s))):
            x, y = rnd.uniform(0, w), rnd.uniform(0, h); r = rnd.uniform(2.5, 4.5)*s
            d.ellipse([x-r, y-r, x+r, y+r], fill=col)
    elif kind == "shale":     # dashes
        for y in range(0, h, 26*s):
            off = rnd.uniform(0, 60)*s
            for x in range(int(-off), w, 64*s):
                d.line([(x, y), (x + 34*s, y)], fill=col, width=3*s)
    elif kind == "granite":   # random crosses
        for _ in range(int(w*h/(4200*s*s))):
            x, y = rnd.uniform(0, w), rnd.uniform(0, h); a = 9*s
            d.line([(x-a, y), (x+a, y)], fill=col, width=3*s); d.line([(x, y-a), (x, y+a)], fill=col, width=3*s)
    elif kind == "basalt":    # v marks
        for y in range(0, h, 46*s):
            for x in range(int(rnd.uniform(0, 40)*s), w, 70*s):
                d.line([(x, y), (x+10*s, y+16*s), (x+20*s, y)], fill=col, width=3*s)
    elif kind == "conglomerate":
        for _ in range(int(w*h/(5200*s*s))):
            x, y = rnd.uniform(0, w), rnd.uniform(0, h); r = rnd.uniform(8, 18)*s
            d.ellipse([x-r, y-r*0.75, x+r, y+r*0.75], outline=col, width=3*s)
    elif kind == "gneiss":    # wavy bands
        for y0 in range(0, h, 30*s):
            pts = [(x, y0 + 8*s*math.sin(x/(40*s) + y0)) for x in range(0, w+10, 10)]
            d.line(pts, fill=col, width=3*s)
    return L

def rock_body(im, poly, fill=None, pattern="limestone", pat_color=None, outline=None, ow=4, seed=2, sketch=False):
    """Rock body: age-colour fill + lithology pattern, or 'chalk sketch' (outline + pattern lines only)."""
    mask = Image.new("L", im.size, 0); ImageDraw.Draw(mask).polygon([P(x, y) for x, y in poly], fill=255)
    if not sketch and fill:
        layer = Image.new("RGBA", im.size, rgb(fill)); layer.putalpha(mask); im.alpha_composite(layer)
        pc = pat_color or shade(fill, 0.72)
    else:
        pc = pat_color or C["line"]
    pat = _pattern_layer(im.size, pattern, pc, seed=seed)
    pa = np.asarray(pat.split()[-1]).astype(np.float32)*(np.asarray(mask).astype(np.float32)/255)
    pat.putalpha(Image.fromarray(pa.astype(np.uint8))); im.alpha_composite(pat)
    if outline:
        ImageDraw.Draw(im).line([P(x, y) for x, y in poly] + [P(*poly[0])], fill=rgb(outline), width=int(ow*S), joint="curve")

def ragged(x0, y0, x1, y1, seed=1, amp=14, n=24, top_only=False):
    rnd = random.Random(seed); pts = []
    for i in range(n+1):
        pts.append((x0 + (x1-x0)*i/n, y0 + rnd.uniform(-amp, amp)))
    if top_only:
        return pts + [(x1, y1), (x0, y1)]
    return pts

def pocket(im, cx, cy, rx, ry, rim=C["slate"]):
    d = ImageDraw.Draw(im)
    d.ellipse([P(cx-rx, cy-ry), P(cx+rx, cy+ry)], fill=rgb(C["obsidian"]))
    d.arc([P(cx-rx, cy-ry), P(cx+rx, cy+ry)], 200, 340, fill=rgb(rim), width=int(4*S))

def droplet(im, x, y, size=26, color=C["water"]):
    d = ImageDraw.Draw(im); s = size
    pts = [P(x, y - s)]
    for j in range(0, 181, 12):
        a = math.radians(j); pts.append(P(x + s*0.62*math.cos(a), y + s*0.62*math.sin(a)))
    d.polygon(pts, fill=rgb(color))

def spiral(im, cx, cy, r=46, color=C["magnesia"], width=4, dashed=False):
    d = ImageDraw.Draw(im); pts = []
    for j in range(0, 900):
        t = j/900*4.2*math.pi; rr = r*(t/(4.2*math.pi))
        pts.append(P(cx + rr*math.cos(t), cy + rr*math.sin(t)))
    if dashed:
        for k in range(0, len(pts)-12, 24):
            d.line(pts[k:k+12], fill=rgb(color), width=int(width*S))
    else:
        d.line(pts, fill=rgb(color), width=int(width*S))

def crack(im, pts, color=C["magnesia"], width=4):
    ImageDraw.Draw(im).line([P(x, y) for x, y in pts], fill=rgb(color), width=int(width*S), joint="curve")
