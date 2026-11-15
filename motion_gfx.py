"""
ClipperAI Studio - Motion Graphics Engine (Modern Overlay Renderer)

Menggantikan grafis kaku berbasis ffmpeg `drawbox` + ASS dengan layer RGBA yang
dirender per-frame (PIL + numpy) memakai kurva easing & spring ala Remotion / After Effects:

  * Caption karaoke word-pop: kata muncul dengan spring-overshoot, highlight "pill" warna aksen
    yang meluncur halus mengikuti kata aktif, kata kuat diwarnai aksen + emoji berwarna melayang.
  * Hook Title Card intro: label pill + kartu putih rounded, kata ter-reveal bertahap (stagger),
    marker highlight tersapu, keluar dengan slide-up + fade.
  * Keyword Sticker: stiker miring dengan pop elastis.
  * B-Roll Takeaway Panel: panel glass gelap + bar aksen, frasa muncul kata per kata.
  * Progress bar gradien dengan glow, kilau cahaya (light sweep) halus di setiap cut.

Output: aliran frame RGBA mentah (rawvideo) yang di-pipe langsung ke ffmpeg dan di-overlay
di atas video hasil edit. Tanpa dependensi baru (hanya Pillow + numpy).
"""

from __future__ import annotations

import math
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FPS = 30

BASE_DIR = Path(__file__).resolve().parent
FONT_DIR = BASE_DIR / "assets" / "fonts"
WIN_FONTS = Path("C:/Windows/Fonts")

RGBA = Tuple[int, int, int, int]

# ----------------------------------------------------------------------------
# Easing & spring
# ----------------------------------------------------------------------------
def clamp(x: float, a: float = 0.0, b: float = 1.0) -> float:
    return a if x < a else b if x > b else x


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def ease_out_cubic(t: float) -> float:
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in_cubic(t: float) -> float:
    t = clamp(t)
    return t ** 3


def ease_in_out_cubic(t: float) -> float:
    t = clamp(t)
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def ease_out_back(t: float, s: float = 1.9) -> float:
    t = clamp(t)
    t -= 1
    return t * t * ((s + 1) * t + s) + 1


def spring(t: float, freq: float = 11.0, damp: float = 7.0) -> float:
    """Damped spring 0 -> 1 (overshoot lalu settle). t dalam detik."""
    if t <= 0:
        return 0.0
    return 1 - math.exp(-damp * t) * math.cos(freq * t)


# ----------------------------------------------------------------------------
# Font & color helpers
# ----------------------------------------------------------------------------
_FONT_CHAIN = {
    "black": ["Montserrat-Black.ttf", "seguibl.ttf", "ariblk.ttf", "segoeuib.ttf", "arialbd.ttf"],
    "extrabold": ["Montserrat-ExtraBold.ttf", "segoeuib.ttf", "arialbd.ttf"],
    "bold": ["Montserrat-Bold.ttf", "segoeuib.ttf", "arialbd.ttf"],
    "semibold": ["Montserrat-SemiBold.ttf", "seguisb.ttf", "arial.ttf"],
}


@lru_cache(maxsize=64)
def font(weight: str, size: int) -> ImageFont.FreeTypeFont:
    for name in _FONT_CHAIN.get(weight, _FONT_CHAIN["bold"]):
        for d in (FONT_DIR, WIN_FONTS):
            p = d / name
            if p.exists():
                return ImageFont.truetype(str(p), size)
    return ImageFont.load_default(size)


@lru_cache(maxsize=8)
def emoji_font(size: int = 109) -> Optional[ImageFont.FreeTypeFont]:
    p = WIN_FONTS / "seguiemj.ttf"
    if p.exists():
        try:
            return ImageFont.truetype(str(p), size)
        except Exception:
            return None
    return None


def hex_rgb(h: str) -> Tuple[int, int, int]:
    h = h.replace("0x", "").replace("#", "")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def lighten(c: Tuple[int, int, int], f: float) -> Tuple[int, int, int]:
    return tuple(int(v + (255 - v) * f) for v in c)  # type: ignore


def luminance(c: Tuple[int, int, int]) -> float:
    return (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) / 255.0


_EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF\u2B50\u2B06\u2194-\u21AA\uFE0F\u200D]+"
)


def strip_emoji(s: str) -> str:
    return re.sub(r"\s+", " ", _EMOJI_RE.sub("", s)).strip()


def first_emoji(s: str) -> Optional[str]:
    m = _EMOJI_RE.search(s)
    return m.group(0).replace("\u200d", "") if m else None


# ----------------------------------------------------------------------------
# Sprite primitives (anti-aliased via supersampling)
# ----------------------------------------------------------------------------
def rrect(w: int, h: int, r: int, fill: RGBA, outline: Optional[RGBA] = None,
          width: int = 0, ss: int = 3) -> Image.Image:
    w, h = max(2, int(w)), max(2, int(h))
    big = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    d.rounded_rectangle((0, 0, w * ss - 1, h * ss - 1), radius=r * ss, fill=fill,
                        outline=outline, width=width * ss)
    return big.resize((w, h), Image.LANCZOS)


def with_shadow(img: Image.Image, blur: int = 14, offset: Tuple[int, int] = (0, 10),
                opacity: float = 0.55, color: Tuple[int, int, int] = (0, 0, 0)) -> Image.Image:
    pad = blur * 2 + max(abs(offset[0]), abs(offset[1]))
    w, h = img.size
    out = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    a = img.getchannel("A").point(lambda v: int(v * opacity))
    sh = Image.new("RGBA", img.size, color + (0,))
    sh.putalpha(a)
    out.alpha_composite(sh, (pad + offset[0], pad + offset[1]))
    out = out.filter(ImageFilter.GaussianBlur(blur))
    out.alpha_composite(img, (pad, pad))
    return out


def glow(img: Image.Image, color: Tuple[int, int, int], blur: int = 18, strength: float = 0.9) -> Image.Image:
    pad = blur * 2
    w, h = img.size
    out = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    a = img.getchannel("A").point(lambda v: int(v * strength))
    g = Image.new("RGBA", img.size, color + (0,))
    g.putalpha(a)
    out.alpha_composite(g, (pad, pad))
    out = out.filter(ImageFilter.GaussianBlur(blur))
    out.alpha_composite(img, (pad, pad))
    return out


def text_img(text: str, fnt: ImageFont.FreeTypeFont, fill: RGBA,
             stroke: int = 0, stroke_fill: RGBA = (0, 0, 0, 255),
             tracking: int = 0) -> Image.Image:
    """Render teks tight-bbox (dengan letter-spacing opsional)."""
    if tracking:
        chars = [text_img(c, fnt, fill, stroke, stroke_fill) if c != " " else None for c in text]
        sp = int(fnt.size * 0.28)
        widths = [c.size[0] if c is not None else sp for c in chars]
        hh = max([c.size[1] for c in chars if c is not None] or [fnt.size])
        tw = sum(widths) + tracking * max(0, len(chars) - 1)
        out = Image.new("RGBA", (max(1, tw), hh), (0, 0, 0, 0))
        x = 0
        asc = fnt.getbbox("H", stroke_width=stroke)
        for c, cw in zip(chars, widths):
            if c is not None:
                out.alpha_composite(c, (x, 0))
            x += cw + tracking
        return out
    l, t, r, b = fnt.getbbox("HÁgy" if not text.strip() else text, stroke_width=stroke)
    # gunakan tinggi baris konsisten (cap-height + descender) supaya baseline sejajar
    L, T, R, B = fnt.getbbox("HÁgy", stroke_width=stroke)
    t, b = min(t, T), max(b, B)
    l2, _, r2, _ = fnt.getbbox(text, stroke_width=stroke)
    pad_x = 6
    w = max(1, (r2 - l2) + pad_x * 2)
    img = Image.new("RGBA", (w, b - t), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((pad_x - l2, -t), text, font=fnt, fill=fill,
                             stroke_width=stroke, stroke_fill=stroke_fill)
    return img


def emoji_img(e: str, size: int) -> Optional[Image.Image]:
    f = emoji_font(109)
    if f is None or not e:
        return None
    canvas = Image.new("RGBA", (180 * max(1, len(e)), 160), (0, 0, 0, 0))
    try:
        ImageDraw.Draw(canvas).text((10, 10), e, font=f, embedded_color=True)
    except Exception:
        return None
    bb = canvas.getbbox()
    if not bb:
        return None
    im = canvas.crop(bb)
    s = size / max(im.size)
    return im.resize((max(1, int(im.size[0] * s)), max(1, int(im.size[1] * s))), Image.LANCZOS)


# ----------------------------------------------------------------------------
# Frame compositor helpers
# ----------------------------------------------------------------------------
def fade(img: Image.Image, a: float) -> Image.Image:
    if a >= 0.999:
        return img
    im = img.copy()
    im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    return im


def transform(img: Image.Image, scale: float = 1.0, alpha: float = 1.0, rot: float = 0.0) -> Optional[Image.Image]:
    if alpha <= 0.01 or scale <= 0.02:
        return None
    im = img
    if abs(scale - 1.0) > 0.004:
        im = im.resize((max(1, int(im.size[0] * scale)), max(1, int(im.size[1] * scale))), Image.BICUBIC)
    if abs(rot) > 0.05:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    return fade(im, alpha)


def paste_center(canvas: Image.Image, img: Optional[Image.Image], cx: float, cy: float) -> None:
    if img is None:
        return
    paste_at(canvas, img, int(round(cx - img.size[0] / 2)), int(round(cy - img.size[1] / 2)))


def paste_at(canvas: Image.Image, img: Image.Image, x: int, y: int) -> None:
    w, h = img.size
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(canvas.size[0], x + w), min(canvas.size[1], y + h)
    if x1 <= x0 or y1 <= y0:
        return
    if (x0, y0, x1, y1) != (x, y, x + w, y + h):
        img = img.crop((x0 - x, y0 - y, x1 - x, y1 - y))
    canvas.alpha_composite(img, (x0, y0))


# ----------------------------------------------------------------------------
# Elements
# ----------------------------------------------------------------------------
class Element:
    t0: float = 0.0
    t1: float = 0.0

    def active(self, t: float) -> bool:
        return self.t0 - 0.05 <= t <= self.t1 + 0.05

    def draw(self, canvas: Image.Image, t: float) -> None:  # pragma: no cover
        raise NotImplementedError


def _clean_word(w: str) -> str:
    # Hanya izinkan huruf Latin/angka/tanda baca umum (membuang karakter halusinasi non-Latin seperti huruf India/Arab acak)
    w = re.sub(r"[^A-Za-z0-9À-ÿ\-\'?!.,]", "", w.strip()).upper()
    w = re.sub(r"^[\"'“”‘’(\[]+|[\"'“”‘’)\],.;:]+$", "", w)
    return w


class TopGradient(Element):
    """Gradien sinematik di bagian atas layar untuk membingkai visual & meredam watermark video sumber."""

    def __init__(self, total: float, height: int = 240, max_alpha: int = 185):
        self.t0, self.t1 = 0.0, total
        ramp = (1.0 - np.linspace(0.0, 1.0, height)) ** 1.7
        arr = np.zeros((height, W, 4), dtype=np.uint8)
        arr[:, :, 3] = (ramp * max_alpha).astype(np.uint8)[:, None]
        self.img = Image.fromarray(arr, "RGBA")

    def draw(self, canvas: Image.Image, t: float) -> None:
        canvas.alpha_composite(self.img, (0, 0))


class BottomGradient(Element):
    """Gradien gelap sinematik di bagian bawah layar agar teks caption & kartu insight selalu kontras."""

    def __init__(self, total: float, height: int = 820, max_alpha: int = 225):
        self.t0, self.t1 = 0.0, total
        ramp = np.linspace(0.0, 1.0, height) ** 1.55
        arr = np.zeros((height, W, 4), dtype=np.uint8)
        arr[:, :, 3] = (ramp * max_alpha).astype(np.uint8)[:, None]
        self.img = Image.fromarray(arr, "RGBA")
        self.y = H - height

    def draw(self, canvas: Image.Image, t: float) -> None:
        canvas.alpha_composite(self.img, (0, self.y))


class TopHeaderPill(Element):
    """Kapsul dark-glass modern di bagian atas (y=96) dengan indikator live berpendar & penutup watermark sumber."""

    def __init__(self, label: str, total: float, accent: Tuple[int, int, int], y: int = 96):
        self.t0, self.t1, self.y = 0.0, total, y
        self.accent = accent
        clean_lbl = strip_emoji(label).upper() or "SOROTAN UTAMA"
        em = first_emoji(label) or "🔥"
        f = font("extrabold", 26)
        txt = text_img(clean_lbl, f, (248, 250, 252, 255), tracking=3)
        eimg = emoji_img(em, 34)
        pw = max(440, txt.size[0] + 124 + (eimg.size[0] if eimg else 0))
        ph = 76
        body = rrect(pw, ph, 38, (10, 14, 24, 245), outline=accent + (180,), width=2)
        # Garis aksen tipis di bawah kapsul
        hl_bar = rrect(int(pw * 0.45), 4, 2, accent + (220,))
        body.alpha_composite(hl_bar, ((pw - hl_bar.size[0]) // 2, ph - 6))
        content_w = 24 + (eimg.size[0] + 10 if eimg else 0) + txt.size[0]
        x = (pw - content_w) // 2 + 18
        if eimg:
            body.alpha_composite(eimg, (x, (ph - eimg.size[1]) // 2))
            x += eimg.size[0] + 10
        body.alpha_composite(txt, (x, (ph - txt.size[1]) // 2))
        self.dot_x = (pw - content_w) // 2 + 4
        self.pw, self.ph = pw, ph
        self.pill = with_shadow(body, blur=14, offset=(0, 8), opacity=0.55)
        dot_core = rrect(14, 14, 7, accent + (255,))
        self.dot_glow = glow(dot_core, accent, blur=8, strength=1.0)

    def draw(self, canvas: Image.Image, t: float) -> None:
        paste_center(canvas, self.pill, W / 2, self.y)
        pulse = 0.75 + 0.25 * math.sin(t * 4.2)
        dx = W / 2 - self.pw / 2 + self.dot_x
        paste_center(canvas, transform(self.dot_glow, 0.9 + 0.15 * pulse, pulse), dx, self.y)


class CinemaParticles(Element):
    """Partikel bokeh sinematik halus di area atas & bawah layar agar visual terasa hidup dan mewah."""

    def __init__(self, total: float, accent: Tuple[int, int, int], count: int = 12):
        self.t0, self.t1 = 0.0, total
        rng = np.random.default_rng(42)
        self.particles = []
        light_acc = lighten(accent, 0.45)
        for i in range(count):
            sz = int(rng.integers(14, 34))
            col = accent if i % 2 == 0 else light_acc
            core = rrect(sz, sz, sz // 2, col + (160,))
            sp = glow(core, col, blur=10, strength=0.75)
            x0 = float(rng.uniform(70, W - 70))
            y0 = float(rng.uniform(1180, H - 140) if i < count * 0.75 else rng.uniform(60, 280))
            vx = float(rng.uniform(-18, 18))
            vy = float(rng.uniform(-34, -14))
            ph = float(rng.uniform(0, 6.28))
            self.particles.append((sp, x0, y0, vx, vy, ph))

    def draw(self, canvas: Image.Image, t: float) -> None:
        for sp, x0, y0, vx, vy, ph in self.particles:
            x = (x0 + vx * t + 16 * math.sin(t * 1.3 + ph)) % W
            y = y0 + (vy * t) % 520 - 120 if y0 > 900 else (y0 + vy * 0.4 * t) % 260
            a = 0.18 + 0.16 * math.sin(t * 2.4 + ph)
            paste_center(canvas, fade(sp, a), x, y)


class CaptionTrack(Element):
    """Caption karaoke modern: word-pop spring + highlight pill berpendar + emoji pop cerdas."""

    SIZE = 86
    MAX_WORDS = 3
    MAX_W = 920
    GAP = 36

    def __init__(self, words: List[Dict[str, Any]], accent: Tuple[int, int, int],
                 power_words: Sequence[str] = (), emoji_map: Optional[Dict[str, str]] = None,
                 y_center: int = 1490, alt_zones: Sequence[Tuple[float, float, int]] = (),
                 card_zones: Sequence[Tuple[float, float]] = ()):
        self.accent = accent
        self.dark_text = luminance(accent) > 0.5
        self.power = set(power_words)
        self.emoji_map = emoji_map or {}
        self.y_default = y_center
        self.alt_zones = list(alt_zones)
        self.card_zones = list(card_zones)
        self.f = font("black", self.SIZE)
        self._cache: Dict[Tuple[str, str], Image.Image] = {}
        ws = []
        for w in words:
            txt = _clean_word(w.get("word", ""))
            if not txt:
                continue
            st = float(w["start"])
            en = min(float(w["end"]), st + 1.20)
            ws.append(dict(text=txt, start=st, end=max(en, st + 0.12),
                           key=re.sub(r"[^\w]", "", txt.lower()),
                           punct=w.get("word", "").strip()[-1:] in ".?!,;"))
        self.words = ws
        self.pages = self._paginate(ws)
        self.t0 = self.pages[0]["t0"] if self.pages else 0
        self.t1 = self.pages[-1]["t1"] if self.pages else 0

    # -- sprites --
    def sprite(self, text: str, kind: str) -> Image.Image:
        k = (text, kind)
        if k not in self._cache:
            if kind == "active":
                col = (10, 12, 18, 255) if self.dark_text else (255, 255, 255, 255)
                im = text_img(text, self.f, col)
            else:
                col = self.accent + (255,) if kind == "power" else (255, 255, 255, 255)
                im = text_img(text, self.f, col, stroke=8, stroke_fill=(0, 0, 0, 255))
                im = with_shadow(im, blur=12, offset=(0, 7), opacity=0.68)
            self._cache[k] = im
        return self._cache[k]

    def _wwidth(self, text: str) -> int:
        l, _, r, _ = self.f.getbbox(text, stroke_width=8)
        return r - l

    def _paginate(self, ws):
        pages, cur = [], []

        def flush():
            if cur:
                pages.append(dict(words=list(cur)))
                cur.clear()

        for w in ws:
            if cur:
                gap = w["start"] - cur[-1]["end"]
                width = sum(self._wwidth(x["text"]) for x in cur + [w]) + self.GAP * len(cur)
                if len(cur) >= self.MAX_WORDS or gap > 0.55 or width > self.MAX_W or cur[-1]["punct"]:
                    flush()
            cur.append(w)
        flush()

        for i, p in enumerate(pages):
            p["t0"] = p["words"][0]["start"] - 0.06
            nxt = pages[i + 1]["words"][0]["start"] - 0.06 if i + 1 < len(pages) else 1e9
            p["t1"] = min(nxt, p["words"][-1]["end"] + 0.55)
            widths = [self._wwidth(w["text"]) for w in p["words"]]
            total = sum(widths) + self.GAP * (len(widths) - 1)
            p["scale"] = min(1.0, self.MAX_W / max(1, total))
            x = -total / 2
            p["xs"] = []
            for wd in widths:
                p["xs"].append((x + wd / 2) * p["scale"])
                x += wd + self.GAP
            p["widths"] = [wd * p["scale"] for wd in widths]
            p["y"] = self.y_default
            for (a, b, y) in self.alt_zones:
                if a - 0.05 <= p["t0"] < b:
                    p["y"] = y
            p["emoji"] = None
            for j, w in enumerate(p["words"]):
                e = self.emoji_map.get(w["key"])
                if e:
                    em = first_emoji(e)
                    if em:
                        p["emoji"] = (j, em)
                        break
        return pages

    def draw(self, canvas: Image.Image, t: float) -> None:
        page = None
        for p in self.pages:
            if p["t0"] <= t < p["t1"]:
                page = p
                break
        if page is None:
            return
        ws, sc, cy = page["words"], page["scale"], page["y"]

        act = -1
        for j, w in enumerate(ws):
            if t >= w["start"] - 0.03:
                act = j
        exit_a = 1.0
        if page["t1"] - t < 0.10 and page["t1"] < 1e8:
            exit_a = clamp((page["t1"] - t) / 0.10)

        # Highlight pill tepat di bawah kata aktif dengan neon glow & pop-spring
        if act >= 0:
            w_on = ws[act]
            since = max(0.0, t - (w_on["start"] - 0.03))
            px = page["xs"][act]
            pw = page["widths"][act]
            pop = 0.88 + 0.12 * spring(since, 18, 9.5)
            ph = (self.SIZE * 1.22) * sc
            pill = rrect(int(pw + 48 * sc), int(ph), int(24 * sc), self.accent + (255,),
                         outline=lighten(self.accent, 0.55) + (240,), width=3)
            pill = glow(pill, self.accent, blur=14, strength=0.55)
            paste_center(canvas, transform(pill, pop, exit_a, 0.0), W / 2 + px, cy + 2)

        for j, w in enumerate(ws):
            appear = page["t0"] + j * 0.025
            if t < appear:
                continue
            dt = t - appear
            s = (0.85 + 0.15 * spring(dt, 14, 9.0)) * sc
            rise = (1 - ease_out_cubic(dt / 0.15)) * 14
            a = clamp(dt / 0.06) * exit_a
            if j > act:
                a *= 0.90
            kind = "active" if j == act else ("power" if (w["key"] in self.power or w["key"] in self.emoji_map) else "normal")
            img = self.sprite(w["text"], kind)
            if j == act:
                w_dt = max(0.0, t - (w["start"] - 0.03))
                s *= 1.0 + 0.07 * math.sin(clamp(w_dt / 0.20) * math.pi)
            paste_center(canvas, transform(img, s, a), W / 2 + page["xs"][j], cy + rise)

        # Emoji 3D pop (otomatis pindah ke bawah teks jika di atas teks sedang ada kartu Hook/Insight/Keyword)
        if page["emoji"] is not None:
            j, em = page["emoji"]
            appear = ws[j]["start"] - 0.03
            if t >= appear:
                dt = t - appear
                img = self._emoji(em)
                if img is not None:
                    s = spring(dt, 13, 6.5)
                    rot = 14 * math.exp(-5 * dt) * math.sin(dt * 18) + 4 * math.sin(t * 3.2)
                    bob = 6 * math.sin(t * 4.0)
                    ex = W / 2 + clamp(page["xs"][j], -300, 300)
                    card_busy = any(ca - 0.1 <= t <= cb + 0.1 for (ca, cb) in self.card_zones)
                    ey = (cy + 135 * max(sc, 0.85) + bob) if card_busy else (cy - 142 * max(sc, 0.85) + bob)
                    paste_center(canvas, transform(img, s, exit_a * clamp(dt / 0.06), rot), ex, ey)

    @lru_cache(maxsize=32)
    def _emoji(self, em: str) -> Optional[Image.Image]:
        im = emoji_img(em, 134)
        return with_shadow(im, blur=10, offset=(0, 8), opacity=0.50) if im is not None else None


class HookTitle(Element):
    """Kartu judul pembuka: label pill + kartu dark-glass modern, reveal kata bertahap + marker sweep."""

    def __init__(self, title: str, label: str, accent: Tuple[int, int, int],
                 t0: float = 0.15, t1: float = 3.2, y: int = 150,
                 highlight: Optional[str] = None):
        self.t0, self.t1, self.y = t0, t1, y
        self.accent = accent
        dark_acc = luminance(accent) > 0.55
        title = strip_emoji(title).upper()
        f = font("black", 52)
        maxw = 840
        lines: List[List[str]] = [[]]
        for word in title.split():
            trial = " ".join(lines[-1] + [word])
            l, _, r, _ = f.getbbox(trial)
            if lines[-1] and r - l > maxw:
                lines.append([word])
            else:
                lines[-1].append(word)
        lines = [ln for ln in lines if ln][:2]
        hl = (highlight or "").upper()
        if not hl:
            cand = [w for ln in lines for w in ln]
            hl = max(cand, key=len) if cand else ""
        self.word_sprites: List[Tuple[Image.Image, Image.Image, int, int, bool]] = []
        line_h = 68
        sp = 16
        for li, ln in enumerate(lines):
            imgs_w = [text_img(w, f, (255, 255, 255, 255)) for w in ln]
            imgs_d = [text_img(w, f, (12, 14, 22, 255) if dark_acc else (255, 255, 255, 255)) for w in ln]
            tw = sum(im.size[0] for im in imgs_w) + sp * (len(imgs_w) - 1)
            x = -tw / 2
            for w, im_w, im_d in zip(ln, imgs_w, imgs_d):
                is_h = re.sub(r"[^\w]", "", w) == re.sub(r"[^\w]", "", hl)
                self.word_sprites.append((im_w, im_d, int(x + im_w.size[0] / 2), li * line_h, is_h))
                x += im_w.size[0] + sp
        n_lines = max(1, len(lines))
        self.card_w = 930
        self.card_h = 64 + n_lines * line_h
        card = rrect(self.card_w, self.card_h, 30, (11, 15, 27, 232), outline=accent + (210,), width=3)
        self.card = with_shadow(card, blur=20, offset=(0, 14), opacity=0.55)

        lab = strip_emoji(label).upper() or "HIGHLIGHT"
        em = first_emoji(label)
        lf = font("extrabold", 28)
        ltxt = text_img(lab, lf, (12, 12, 16, 255) if dark_acc else (255, 255, 255, 255), tracking=3)
        eimg = emoji_img(em, 34) if em else None
        lw = ltxt.size[0] + 52 + (eimg.size[0] + 12 if eimg else 0)
        pill = rrect(lw, 54, 27, accent + (255,))
        x = 26
        if eimg:
            pill.alpha_composite(eimg, (x, (54 - eimg.size[1]) // 2))
            x += eimg.size[0] + 12
        pill.alpha_composite(ltxt, (x, (54 - ltxt.size[1]) // 2))
        self.label = with_shadow(pill, blur=10, offset=(0, 6), opacity=0.45)
        self.n_lines = n_lines
        self.line_h = line_h

    def draw(self, canvas: Image.Image, t: float) -> None:
        lt = t - self.t0
        if lt < 0 or t > self.t1 + 0.4:
            return
        out = clamp((t - (self.t1 - 0.05)) / 0.35)
        out_e = ease_in_cubic(out)
        a = 1 - out_e
        dy = -55 * out_e

        # Card spring scale-in (langsung terlihat di frame pertama t=0.0)
        cs = 0.88 + 0.12 * spring(lt + 0.04, 11, 7.5)
        cy = self.y + self.card_h / 2 + dy
        paste_center(canvas, transform(self.card, cs, a * clamp((lt + 0.06) / 0.10)), W / 2, cy)

        # Label pill (dari atas, sedikit miring)
        ls = 0.85 + 0.15 * spring(lt + 0.04, 14, 8)
        lrot = 4 * (1 - ease_out_cubic(lt / 0.35)) - 1.2
        paste_center(canvas, transform(self.label, ls, a, lrot), W / 2, self.y - 4 + dy)

        # Kata-kata judul reveal (stagger cepat sehingga di frame awal sudah muncul)
        top = self.y + 50 + dy
        for i, (im_w, im_d, x, yoff, is_hl) in enumerate(self.word_sprites):
            st = lt + 0.06 - i * 0.045
            if st <= 0:
                continue
            k = ease_out_back(st / 0.26, 1.8)
            wy = top + yoff + self.line_h / 2 - 6 + (1 - ease_out_cubic(st / 0.26)) * 22
            im_use = im_w
            if is_hl:
                hk = ease_in_out_cubic((st - 0.10) / 0.28)
                if hk > 0:
                    mw = int((im_w.size[0] + 24) * hk)
                    mark = rrect(max(4, mw), int(im_w.size[1] + 10), 12, self.accent + (245,))
                    paste_at(canvas, fade(mark, a), int(W / 2 + x - im_w.size[0] / 2 - 12),
                             int(wy - im_w.size[1] / 2 - 5))
                    if hk > 0.50:
                        im_use = im_d
            paste_center(canvas, transform(im_use, 0.72 + 0.28 * k, a * clamp(st / 0.08)), W / 2 + x, wy)


class KeywordSticker(Element):
    """Kapsul Callout Kata Kunci modern di area lower-third (y=1245, di atas teks caption, aman dari wajah)."""

    def __init__(self, text: str, t0: float, dur: float, accent: Tuple[int, int, int],
                 emoji: Optional[str] = None, y: int = 1245, rot: float = -1.8):
        self.t0, self.t1, self.y, self.rot = t0, t0 + dur, y, rot
        f = font("black", 50)
        txt = text_img(strip_emoji(text).upper(), f, (255, 255, 255, 255))
        use_em = emoji if (emoji and emoji != "⚡") else "🔥"
        e = emoji_img(use_em, 56)
        w = txt.size[0] + 72 + (e.size[0] + 18 if e else 0)
        h = 96
        body = rrect(w, h, 48, (11, 15, 28, 242), outline=accent + (245,), width=4)
        if e:
            badge_bg = rrect(72, 72, 36, accent + (255,))
            body.alpha_composite(badge_bg, (12, (h - 72) // 2))
            body.alpha_composite(e, (12 + (72 - e.size[0]) // 2, (h - e.size[1]) // 2))
            x = 98
        else:
            x = 36
        body.alpha_composite(txt, (x, (h - txt.size[1]) // 2))
        glowed = glow(body, accent, blur=14, strength=0.55)
        self.img = glowed.rotate(rot, resample=Image.BICUBIC, expand=True)

    def draw(self, canvas: Image.Image, t: float) -> None:
        lt = t - self.t0
        if lt < 0 or t > self.t1:
            return
        s = spring(lt, 16, 7.5)
        out = clamp((t - (self.t1 - 0.18)) / 0.18)
        s *= 1 - 0.25 * ease_in_cubic(out)
        a = clamp(lt / 0.06) * (1 - ease_in_cubic(out))
        paste_center(canvas, transform(self.img, s, a), W / 2, self.y + 4 * math.sin(lt * 4.5))


class BrollPanel(Element):
    """Kartu Glassmorphic Insight / Poin Inti di lower-middle stage (y=1120..1315, aman dari wajah)."""

    def __init__(self, badge: str, phrase: str, t0: float, t1: float, accent: Tuple[int, int, int],
                 y_top: int = 1120):
        self.t0, self.t1 = t0, t1
        self.accent = accent
        self.y_top = y_top
        pw, ph = 940, 198
        panel = rrect(pw, ph, 32, (10, 14, 26, 242), outline=accent + (210,), width=3)
        bar = rrect(12, ph - 52, 6, accent + (255,))
        bar_glow = glow(bar, accent, blur=10, strength=0.85)
        panel.alpha_composite(bar_glow, (26 - (bar_glow.size[0] - 12) // 2, 26 - (bar_glow.size[1] - (ph - 52)) // 2))
        panel.alpha_composite(bar_glow, (pw - 38 - (bar_glow.size[0] - 12) // 2, 26 - (bar_glow.size[1] - (ph - 52)) // 2))
        self.panel = with_shadow(panel, blur=20, offset=(0, 14), opacity=0.62)
        self.pw, self.ph = pw, ph
        self.badge = text_img("✦ " + (strip_emoji(badge).upper() or "POIN INTI") + " ✦", font("extrabold", 26), accent + (255,), tracking=3)
        f = font("black", 48)
        words = strip_emoji(phrase).upper().split()
        hl_word = max(words, key=len) if words else ""
        lines: List[List[str]] = [[]]
        for wd in words:
            trial = " ".join(lines[-1] + [wd])
            l, _, r, _ = f.getbbox(trial)
            if lines[-1] and r - l > pw - 140:
                lines.append([wd])
            else:
                lines[-1].append(wd)
        lines = [ln for ln in lines if ln][:2]
        self.words: List[Tuple[Image.Image, int, int]] = []
        sp = 16
        for li, ln in enumerate(lines):
            imgs = [text_img(wd, f, accent + (255,) if wd == hl_word else (255, 255, 255, 255)) for wd in ln]
            tw = sum(im.size[0] for im in imgs) + sp * max(0, len(imgs) - 1)
            x = (pw - tw) // 2
            for im in imgs:
                self.words.append((im, int(x), li * 56))
                x += im.size[0] + sp
        self.n_lines = len(lines)

    def draw(self, canvas: Image.Image, t: float) -> None:
        lt = t - self.t0
        if lt < 0 or t > self.t1:
            return
        out = clamp((t - (self.t1 - 0.16)) / 0.16)
        a = clamp(lt / 0.12) * (1 - out)
        dy = (1 - ease_out_cubic(lt / 0.35)) * 38 + 26 * ease_in_cubic(out)
        top = self.y_top + dy
        pad = (self.panel.size[0] - self.pw) // 2
        paste_at(canvas, fade(self.panel, a), int(70 - pad), int(top - pad + 6))
        bk = ease_out_cubic((lt - 0.06) / 0.26)
        if bk > 0:
            paste_center(canvas, fade(self.badge, a * bk), W / 2, top + 38)
        base_y = top + 72 + (26 if self.n_lines == 1 else 0)
        for i, (im, x, yoff) in enumerate(self.words):
            st = lt - 0.12 - i * 0.05
            if st <= 0:
                continue
            k = ease_out_cubic(st / 0.22)
            paste_at(canvas, fade(im, a * clamp(st / 0.09)), int(70 + x), int(base_y + yoff + (1 - k) * 20))


class ProgressBar(Element):
    def __init__(self, total: float, accent: Tuple[int, int, int]):
        self.t0, self.t1, self.total = 0.0, total, max(0.1, total)
        g = np.zeros((10, W, 4), dtype=np.uint8)
        c1, c2 = np.array(accent, float), np.array(lighten(accent, 0.45), float)
        ramp = np.linspace(0, 1, W)[:, None]
        g[:, :, :3] = (c1 * (1 - ramp) + c2 * ramp).astype(np.uint8)[None, :, :]
        g[:, :, 3] = 255
        self.grad = Image.fromarray(g, "RGBA")
        self.track = Image.new("RGBA", (W, 10), (255, 255, 255, 46))
        dot = rrect(22, 22, 11, lighten(accent, 0.6) + (255,))
        self.dot = glow(dot, accent, blur=10, strength=1.0)

    def draw(self, canvas: Image.Image, t: float) -> None:
        p = clamp(t / self.total)
        canvas.alpha_composite(self.track, (0, 0))
        wfill = int(W * p)
        if wfill > 1:
            canvas.alpha_composite(self.grad.crop((0, 0, wfill, 10)), (0, 0))
        paste_center(canvas, self.dot, wfill, 5)


class CutSweep(Element):
    """Kilau cahaya anamorphic diagonal berwarna aksen yang menyapu layar di setiap pergantian kamera."""

    def __init__(self, cuts: Sequence[float], accent: Tuple[int, int, int] = (245, 158, 11), strength: float = 0.34):
        self.cuts = list(cuts)
        self.dur = 0.26
        self.strength = strength
        self.accent = accent
        bw = 560
        x = np.linspace(-1, 1, bw)
        prof = np.exp(-(x ** 2) * 4.5)
        core = np.exp(-(x ** 2) * 18.0)
        band = np.zeros((H + 600, bw, 4), dtype=np.uint8)
        for ch_i in range(3):
            col_curve = accent[ch_i] * (1.0 - core) + 255.0 * core
            band[:, :, ch_i] = np.clip(col_curve, 0, 255).astype(np.uint8)[None, :]
        band[:, :, 3] = (prof * 255).astype(np.uint8)[None, :]
        self.band = Image.fromarray(band, "RGBA").rotate(-18, resample=Image.BICUBIC, expand=True)
        self.t0, self.t1 = (min(cuts) - 0.1, max(cuts) + 0.4) if cuts else (0, 0)

    def draw(self, canvas: Image.Image, t: float) -> None:
        for c in self.cuts:
            lt = t - c + 0.04
            if 0 <= lt <= self.dur:
                k = ease_in_out_cubic(lt / self.dur)
                a = self.strength * math.sin(math.pi * clamp(lt / self.dur))
                x = lerp(-self.band.size[0], W + 100, k)
                paste_at(canvas, fade(self.band, a), int(x), int((H - self.band.size[1]) / 2))
                # Optical warm bloom ringan sesaat (2 frame) saat kamera berganti
                if lt < 0.08:
                    bloom_a = int(255 * 0.14 * (1 - lt / 0.08))
                    r, g, b = lighten(self.accent, 0.5)
                    canvas.alpha_composite(Image.new("RGBA", (W, H), (r, g, b, bloom_a)))


# ----------------------------------------------------------------------------
# Vox 2.5D Torn-Paper & Parallax Collage Primitives
# ----------------------------------------------------------------------------
def torn_paper_card(w: int, h: int, fill: RGBA = (248, 246, 238, 255),
                    fibers: bool = True, seed: int = 42) -> Image.Image:
    """
    Menghasilkan potongan kertas fisik dengan tepi sobekan kasar (fibrous torn edge)
    khas gaya dokumenter Vox / Johnny Harris.
    """
    w, h = max(20, int(w)), max(20, int(h))
    pad = 16
    cw, ch = w + pad * 2, h + pad * 2
    im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    rng = np.random.default_rng(seed)
    n_pts_x = max(12, int(w / 18))
    n_pts_y = max(8, int(h / 18))

    # Top edge
    top = []
    for x in np.linspace(pad, pad + w, n_pts_x):
        top.append((float(x), float(pad + rng.uniform(-4.5, 4.5))))
    # Right edge
    right = []
    for y in np.linspace(pad, pad + h, n_pts_y)[1:]:
        right.append((float(pad + w + rng.uniform(-4.5, 4.5)), float(y)))
    # Bottom edge
    bottom = []
    for x in np.linspace(pad + w, pad, n_pts_x)[1:]:
        bottom.append((float(x), float(pad + h + rng.uniform(-4.5, 4.5))))
    # Left edge
    left = []
    for y in np.linspace(pad + h, pad, n_pts_y)[1:-1]:
        left.append((float(pad + rng.uniform(-4.5, 4.5)), float(y)))

    poly = top + right + bottom + left
    d.polygon(poly, fill=fill)

    # Efek serat robekan kertas putih di tepian (fibers)
    if fibers:
        for p in poly[::2]:
            fx = p[0] + rng.uniform(-2, 2)
            fy = p[1] + rng.uniform(-2, 2)
            d.line([(p[0], p[1]), (fx, fy)], fill=(255, 255, 255, 220), width=2)

    return im


def make_slab(pw: int, ph: int, accent: Tuple[int, int, int], is_paper: bool = True, seed: int = 42) -> Tuple[Image.Image, int, int]:
    """
    Menghasilkan slab kanvas (Torn-Paper untuk Vox, atau Remotion Glassmorphic untuk tema Modern).
    Mengembalikan (slab_image, content_offset_x, content_offset_y).
    """
    if is_paper:
        paper = torn_paper_card(pw, ph, fill=(248, 245, 237, 255), fibers=True, seed=seed)
        d_p = ImageDraw.Draw(paper)
        d_p.rectangle((24, 24, pw - 24, 30), fill=accent + (220,))
        return paper, 42, 38
    else:
        pad = 16
        cw, ch = pw + pad * 2, ph + pad * 2
        im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((pad, pad, pad + pw, pad + ph), radius=28, fill=(13, 19, 33, 248),
                            outline=accent + (230,), width=3)
        # Specular reflection bar at the top
        d.rounded_rectangle((pad + 20, pad + 14, pad + pw - 20, pad + 20), radius=3, fill=(255, 255, 255, 90))
        return im, pad + 42, pad + 38


class VoxTornCardHero(Element):
    """
    Kartu utama Vox 2.5D: Teks naskah tercetak di atas potongan kertas sobek (torn paper slab)
    atau Modern Remotion Glass Slab dengan bayangan jatuh tebal, rotasi dinamis, dan efek 2.5D.
    """

    def __init__(self, tag: str, headline: str, t0: float, t1: float, accent: Tuple[int, int, int],
                 y_top: int = 700, rot: float = -2.0, seed: int = 101, is_paper: bool = True):
        self.t0, self.t1 = t0, t1
        self.accent = accent
        self.y_top = y_top
        self.rot = rot
        self.is_paper = is_paper

        f_tag = font("extrabold", 28)
        f_head = font("black", 52)
        clean_tag = strip_emoji(tag).upper() or "INSIGHT"
        tag_color = (185, 28, 28, 255) if is_paper else accent + (255,)
        tag_im = text_img("📌 " + clean_tag, f_tag, tag_color, tracking=3)

        head_color = (18, 18, 24, 255) if is_paper else (255, 255, 255, 255)
        words = strip_emoji(headline).upper().split()
        lines: List[List[str]] = [[]]
        for wd in words:
            trial = " ".join(lines[-1] + [wd])
            l, _, r, _ = f_head.getbbox(trial)
            if lines[-1] and r - l > 820:
                lines.append([wd])
            else:
                lines[-1].append(wd)
        lines = [ln for ln in lines if ln][:3]

        rendered_lines = [text_img(" ".join(ln), f_head, head_color) for ln in lines]

        content_w = max([tag_im.size[0]] + [im.size[0] for im in rendered_lines])
        pw = min(960, content_w + 110)
        ph = 70 + tag_im.size[1] + sum(im.size[1] + 16 for im in rendered_lines)

        slab, ox, oy = make_slab(pw, ph, accent, is_paper=is_paper, seed=seed)
        curr_y = oy
        slab.alpha_composite(tag_im, (ox, curr_y))
        curr_y += tag_im.size[1] + 20
        for im in rendered_lines:
            slab.alpha_composite(im, (ox, curr_y))
            curr_y += im.size[1] + 16

        self.card = with_shadow(slab, blur=22, offset=(0, 16), opacity=0.68)
        self.card_rot = self.card.rotate(rot, resample=Image.BICUBIC, expand=True)

    def draw(self, canvas: Image.Image, t: float) -> None:
        lt = t - self.t0
        if lt < 0 or t > self.t1:
            return
        out = clamp((t - (self.t1 - 0.16)) / 0.16)
        a = clamp(lt / 0.12) * (1 - out)
        glide_x = -40 * (1 - ease_out_cubic(lt / 0.40)) + (t - self.t0) * 14
        rise_y = (1 - ease_out_cubic(lt / 0.32)) * 45
        paste_center(canvas, transform(self.card_rot, 1.0, a), W / 2 + glide_x, self.y_top + rise_y)


class VoxBigStatCard(Element):
    """
    Kartu Angka/Statistik Raksasa (e.g. '87%', '1 KLIK', '100+').
    Torn-Paper untuk Vox atau Remotion Dark Glass untuk Modern Themes.
    """

    def __init__(self, tag: str, stat_num: str, headline: str, t0: float, t1: float,
                 accent: Tuple[int, int, int], y_top: int = 700, rot: float = 2.2, seed: int = 202,
                 is_paper: bool = True):
        self.t0, self.t1 = t0, t1
        self.accent = accent
        self.y_top = y_top
        self.rot = rot
        self.is_paper = is_paper

        f_tag = font("extrabold", 26)
        f_num = font("black", 128)
        f_head = font("extrabold", 44)
        f_stamp = font("black", 26)

        clean_tag = strip_emoji(tag).upper() or "FAKTA PENTING"
        tag_color = (185, 28, 28, 255) if is_paper else accent + (255,)
        tag_im = text_img("📊 " + clean_tag, f_tag, tag_color, tracking=3)

        num_str = strip_emoji(stat_num).strip().upper() or "100%"
        num_im = text_img(num_str, f_num, accent + (255,))

        head_color = (24, 24, 32, 255) if is_paper else (255, 255, 255, 255)
        words = strip_emoji(headline).upper().split()
        lines: List[List[str]] = [[]]
        for wd in words:
            trial = " ".join(lines[-1] + [wd])
            l, _, r, _ = f_head.getbbox(trial)
            if lines[-1] and r - l > 780:
                lines.append([wd])
            else:
                lines[-1].append(wd)
        lines = [ln for ln in lines if ln][:2]

        rendered_lines = [text_img(" ".join(ln), f_head, head_color) for ln in lines]

        # Stempel verifikasi
        stamp_raw = text_img("★ TERVERIFIKASI ★", f_stamp, (185, 28, 28, 255) if is_paper else accent + (255,), tracking=2)
        sw, sh = stamp_raw.size[0] + 32, stamp_raw.size[1] + 16
        stamp_card = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
        d_st = ImageDraw.Draw(stamp_card)
        d_st.rectangle((0, 0, sw - 1, sh - 1), outline=(185, 28, 28, 200) if is_paper else accent + (220,), width=4)
        stamp_card.alpha_composite(stamp_raw, (16, 8))
        stamp_rot = stamp_card.rotate(-14, resample=Image.BICUBIC, expand=True)

        pw = min(960, max(num_im.size[0], max([im.size[0] for im in rendered_lines] or [200])) + 160)
        ph = 110 + tag_im.size[1] + num_im.size[1] + sum(im.size[1] + 14 for im in rendered_lines)

        slab, ox, oy = make_slab(pw, ph, accent, is_paper=is_paper, seed=seed)
        curr_y = oy
        slab.alpha_composite(tag_im, (ox, curr_y))
        curr_y += tag_im.size[1] + 16
        slab.alpha_composite(num_im, (ox, curr_y))
        curr_y += num_im.size[1] + 16
        for im in rendered_lines:
            slab.alpha_composite(im, (ox, curr_y))
            curr_y += im.size[1] + 14

        slab.alpha_composite(stamp_rot, (pw - stamp_rot.size[0] - 28, oy - 6))

        self.card = with_shadow(slab, blur=24, offset=(0, 18), opacity=0.70)
        self.card_rot = self.card.rotate(rot, resample=Image.BICUBIC, expand=True)

    def draw(self, canvas: Image.Image, t: float) -> None:
        lt = t - self.t0
        if lt < 0 or t > self.t1:
            return
        out = clamp((t - (self.t1 - 0.16)) / 0.16)
        a = clamp(lt / 0.12) * (1 - out)
        s = spring(lt, freq=12.0, damp=8.0) if lt < 0.6 else 1.0
        glide_x = -35 * (1 - ease_out_cubic(lt / 0.35)) + (t - self.t0) * 12
        paste_center(canvas, transform(self.card_rot, s, a), W / 2 + glide_x, self.y_top)


class VoxComparisonCard(Element):
    """
    Kartu Perbandingan (SEBELUM vs SESUDAH / MASALAH vs SOLUSI).
    Dua lempengan kontras yang meluncur dari kiri dan kanan secara teratur tanpa tumpang tindih.
    """

    def __init__(self, tag: str, left_text: str, right_text: str, t0: float, t1: float,
                 accent: Tuple[int, int, int], y_top: int = 700, seed: int = 303,
                 is_paper: bool = True):
        self.t0, self.t1 = t0, t1
        self.accent = accent
        self.y_top = y_top

        f_lbl = font("extrabold", 28)
        f_body = font("bold", 38)

        clean_left = strip_emoji(left_text).upper() or "CARA LAMA MANUAL"
        l_words = clean_left.split()
        l_lines = [l_words[:4], l_words[4:8]] if len(l_words) > 4 else [l_words]
        l_color = (32, 24, 24, 255) if is_paper else (255, 235, 235, 255)
        l_rendered = [text_img(" ".join(ln), f_body, l_color) for ln in l_lines if ln]

        pw = 900
        ph1 = 110 + sum(im.size[1] + 12 for im in l_rendered)
        if is_paper:
            paper1 = torn_paper_card(pw, ph1, fill=(244, 233, 233, 255), fibers=True, seed=seed)
        else:
            paper1 = rrect(pw, ph1, 24, (32, 14, 18, 246), outline=(220, 38, 38, 220), width=3)
        d1 = ImageDraw.Draw(paper1)
        d1.rounded_rectangle((32, 24, 230, 68), radius=8, fill=(185, 28, 28, 255))
        d1.text((46, 32), "✕ SEBELUM", font=f_lbl, fill=(255, 255, 255, 255))
        y_c = 82
        for im in l_rendered:
            paper1.alpha_composite(im, (38, y_c))
            y_c += im.size[1] + 10

        self.card_before = with_shadow(paper1, blur=20, offset=(0, 14), opacity=0.65).rotate(-1.8, resample=Image.BICUBIC, expand=True)

        clean_right = strip_emoji(right_text).upper() or "SOLUSI MODERN TERPADU"
        r_words = clean_right.split()
        r_lines = [r_words[:4], r_words[4:8]] if len(r_words) > 4 else [r_words]
        r_color = (16, 28, 20, 255) if is_paper else (235, 255, 240, 255)
        r_rendered = [text_img(" ".join(ln), f_body, r_color) for ln in r_lines if ln]

        ph2 = 110 + sum(im.size[1] + 12 for im in r_rendered)
        if is_paper:
            paper2 = torn_paper_card(pw, ph2, fill=(242, 248, 240, 255), fibers=True, seed=seed + 11)
        else:
            paper2 = rrect(pw, ph2, 24, (12, 32, 22, 246), outline=accent + (220,), width=3)
        d2 = ImageDraw.Draw(paper2)
        d2.rounded_rectangle((32, 24, 240, 68), radius=8, fill=(22, 101, 52, 255))
        d2.text((46, 32), "✓ SESUDAH", font=f_lbl, fill=(255, 255, 255, 255))
        y_c = 82
        for im in r_rendered:
            paper2.alpha_composite(im, (38, y_c))
            y_c += im.size[1] + 10

        self.card_after = with_shadow(paper2, blur=20, offset=(0, 14), opacity=0.65).rotate(1.9, resample=Image.BICUBIC, expand=True)

    def draw(self, canvas: Image.Image, t: float) -> None:
        lt = t - self.t0
        if lt < 0 or t > self.t1:
            return
        out = clamp((t - (self.t1 - 0.16)) / 0.16)
        a = clamp(lt / 0.12) * (1 - out)

        slide1 = (1 - ease_out_cubic(clamp(lt / 0.35))) * -80
        paste_center(canvas, transform(self.card_before, 1.0, a), W / 2 + slide1, self.y_top - 120)

        lt2 = max(0.0, lt - 0.18)
        a2 = clamp(lt2 / 0.12) * (1 - out)
        slide2 = (1 - ease_out_cubic(clamp(lt2 / 0.35))) * 80
        paste_center(canvas, transform(self.card_after, 1.0, a2), W / 2 + slide2, self.y_top + 160)


class VoxChecklistCard(Element):
    """
    Kartu Checklist Fitur / Poin Kunci.
    Torn-Paper untuk Vox atau Remotion Dark Glass untuk Modern Themes.
    """

    def __init__(self, tag: str, headline: str, items: List[str], t0: float, t1: float,
                 accent: Tuple[int, int, int], y_top: int = 700, seed: int = 404,
                 is_paper: bool = True):
        self.t0, self.t1 = t0, t1
        self.accent = accent
        self.y_top = y_top
        self.items = [strip_emoji(it).strip().upper() for it in items if strip_emoji(it).strip()][:3]
        self.is_paper = is_paper

        f_tag = font("extrabold", 26)
        f_head = font("extrabold", 42)
        self.f_item = font("bold", 34)

        clean_tag = strip_emoji(tag).upper() or "FITUR UNGGULAN"
        tag_color = (185, 28, 28, 255) if is_paper else accent + (255,)
        self.tag_im = text_img("📋 " + clean_tag, f_tag, tag_color, tracking=2)

        head_color = (20, 20, 28, 255) if is_paper else (255, 255, 255, 255)
        self.head_im = text_img(strip_emoji(headline).upper()[:36], f_head, head_color)

        pw = 920
        ph = 140 + self.head_im.size[1] + len(self.items) * 72

        slab, ox, oy = make_slab(pw, ph, accent, is_paper=is_paper, seed=seed)
        slab.alpha_composite(self.tag_im, (ox, oy))
        slab.alpha_composite(self.head_im, (ox, oy + self.tag_im.size[1] + 12))

        self.base_card = with_shadow(slab, blur=22, offset=(0, 16), opacity=0.68)
        self.ox = ox
        self.item_start_y = oy + self.tag_im.size[1] + 12 + self.head_im.size[1] + 28

    def draw(self, canvas: Image.Image, t: float) -> None:
        lt = t - self.t0
        if lt < 0 or t > self.t1:
            return
        out = clamp((t - (self.t1 - 0.16)) / 0.16)
        a = clamp(lt / 0.12) * (1 - out)

        card_copy = self.base_card.copy()
        d = ImageDraw.Draw(card_copy)

        item_txt_color = (24, 24, 32) if self.is_paper else (255, 255, 255)
        for i, item_text in enumerate(self.items):
            item_delay = 0.20 + i * 0.28
            if lt >= item_delay:
                it_t = lt - item_delay
                it_a = clamp(it_t / 0.12)
                y_pos = self.item_start_y + i * 68
                d.rounded_rectangle((self.ox, y_pos, self.ox + 48, y_pos + 48), radius=10, fill=(22, 101, 52, int(255 * it_a)))
                d.text((self.ox + 10, y_pos + 6), "✓", font=self.f_item, fill=(255, 255, 255, int(255 * it_a)))
                d.text((self.ox + 66, y_pos + 8), item_text, font=self.f_item, fill=item_txt_color + (int(255 * it_a),))

        glide_x = -30 * (1 - ease_out_cubic(lt / 0.35)) + (t - self.t0) * 10
        paste_center(canvas, transform(card_copy, 1.0, a), W / 2 + glide_x, self.y_top)


class VoxCtaCard(Element):
    """
    Kartu Call-to-Action (CTA Slam).
    Tombol aksi interaktif dengan breathing pulse ala Remotion.
    """

    def __init__(self, tag: str, headline: str, cta_text: str, t0: float, t1: float,
                 accent: Tuple[int, int, int], y_top: int = 720, seed: int = 505,
                 is_paper: bool = True):
        self.t0, self.t1 = t0, t1
        self.accent = accent
        self.y_top = y_top

        f_tag = font("extrabold", 28)
        f_head = font("black", 48)
        f_btn = font("black", 40)

        clean_tag = strip_emoji(tag).upper() or "LANGKAH SELANJUTNYA"
        tag_color = (185, 28, 28, 255) if is_paper else accent + (255,)
        tag_im = text_img("⚡ " + clean_tag, f_tag, tag_color, tracking=3)

        head_color = (20, 20, 28, 255) if is_paper else (255, 255, 255, 255)
        words = strip_emoji(headline).upper().split()
        lines: List[List[str]] = [[]]
        for wd in words:
            trial = " ".join(lines[-1] + [wd])
            l, _, r, _ = f_head.getbbox(trial)
            if lines[-1] and r - l > 800:
                lines.append([wd])
            else:
                lines[-1].append(wd)
        lines = [ln for ln in lines if ln][:2]

        rendered_lines = [text_img(" ".join(ln), f_head, head_color) for ln in lines]

        btn_str = strip_emoji(cta_text).strip().upper() or "COBA SEKARANG!"
        btn_im = text_img(btn_str, f_btn, (255, 255, 255, 255), tracking=2)

        pw = 940
        btn_h = 100
        ph = 140 + tag_im.size[1] + sum(im.size[1] + 14 for im in rendered_lines) + btn_h

        slab, ox, oy = make_slab(pw, ph, accent, is_paper=is_paper, seed=seed)
        curr_y = oy
        slab.alpha_composite(tag_im, (ox, curr_y))
        curr_y += tag_im.size[1] + 18
        for im in rendered_lines:
            slab.alpha_composite(im, (ox, curr_y))
            curr_y += im.size[1] + 14

        curr_y += 18
        btn_box = (ox, curr_y, ox + pw - 96, curr_y + btn_h)
        d_p = ImageDraw.Draw(slab)
        d_p.rounded_rectangle(btn_box, radius=24, fill=accent + (255,))
        d_p.rounded_rectangle((btn_box[0] + 4, btn_box[1] + 4, btn_box[2] - 4, btn_box[3] - 4),
                              radius=20, outline=(255, 255, 255, 120), width=3)
        bx = btn_box[0] + (btn_box[2] - btn_box[0] - btn_im.size[0]) // 2
        by = btn_box[1] + (btn_h - btn_im.size[1]) // 2
        slab.alpha_composite(btn_im, (bx, by))

        self.card = with_shadow(slab, blur=24, offset=(0, 18), opacity=0.72)

    def draw(self, canvas: Image.Image, t: float) -> None:
        lt = t - self.t0
        if lt < 0 or t > self.t1:
            return
        out = clamp((t - (self.t1 - 0.16)) / 0.16)
        a = clamp(lt / 0.12) * (1 - out)
        s = spring(lt, freq=11.0, damp=7.0) if lt < 0.5 else 1.0 + 0.02 * math.sin((t - self.t0) * 4.0)
        paste_center(canvas, transform(self.card, s, a), W / 2, self.y_top)




class VoxParchmentBackground(Element):
    """
    Latar kanvas tekstur kertas kusut/krem (Wrinkled Parchment Floor)
    dengan efek pencahayaan sinematik & pergerakan kamera paralaks kontinu ke kanan.
    """

    def __init__(self, total: float, accent: Tuple[int, int, int]):
        self.t0, self.t1 = 0.0, total
        rng = np.random.default_rng(77)
        # Sintesis tekstur serat kertas krem bertekstur
        grid_w, grid_h = W // 4, H // 4
        base_noise = rng.integers(232, 248, (grid_h, grid_w), dtype=np.uint8)
        # Tambahkan lipatan & kerutan kertas
        for _ in range(16):
            y_fold = rng.integers(0, grid_h)
            base_noise[max(0, y_fold - 2):min(grid_h, y_fold + 3), :] = np.clip(
                base_noise[max(0, y_fold - 2):min(grid_h, y_fold + 3), :].astype(int) - 18, 0, 255
            ).astype(np.uint8)

        base_im = Image.fromarray(base_noise, "L").resize((W, H), Image.BICUBIC)
        base_im = base_im.filter(ImageFilter.GaussianBlur(1.2))

        # Warnai menjadi krem hangat vintage (warm parchment cream)
        arr = np.zeros((H, W, 4), dtype=np.uint8)
        lum = np.array(base_im, dtype=float) / 255.0
        arr[:, :, 0] = np.clip(lum * 242, 0, 255).astype(np.uint8)
        arr[:, :, 1] = np.clip(lum * 236, 0, 255).astype(np.uint8)
        arr[:, :, 2] = np.clip(lum * 222, 0, 255).astype(np.uint8)
        arr[:, :, 3] = 255

        # Vignette gelap di sekeliling bingkai kanvas
        y_coords, x_coords = np.ogrid[:H, :W]
        cx, cy = W / 2, H / 2
        dist = np.sqrt(((x_coords - cx) / cx) ** 2 + ((y_coords - cy) / cy) ** 2)
        vig = np.clip(1.0 - 0.42 * (dist ** 2), 0.55, 1.0)
        arr[:, :, :3] = (arr[:, :, :3] * vig[:, :, None]).astype(np.uint8)

        self.canvas_bg = Image.fromarray(arr, "RGBA")

    def draw(self, canvas: Image.Image, t: float) -> None:
        # Pergerakan drift sangat lambat pada lantai kanvas (efek 2.5D camera pan)
        drift_x = int(-20 + (t * 8) % 40)
        paste_at(canvas, self.canvas_bg, drift_x, 0)


# ----------------------------------------------------------------------------
# Timeline renderer
# ----------------------------------------------------------------------------
class Timeline:
    def __init__(self, total: float, elements: List[Element]):
        self.total = total
        # Urutan gambar: dari bawah ke atas
        self.elements = elements
        self._empty = bytes(W * H * 4)

    def frame(self, i: int) -> bytes:
        t = i / FPS
        act = [e for e in self.elements if e.active(t)]
        if not act:
            return self._empty
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for e in act:
            e.draw(canvas, t)
        return canvas.tobytes()

    def n_frames(self) -> int:
        return int(math.ceil(self.total * FPS))

    def preview(self, t: float) -> Image.Image:
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for e in self.elements:
            if e.active(t):
                e.draw(canvas, t)
        return canvas


# ----------------------------------------------------------------------------
# Video-card assets (mask & shadow untuk B-Roll Split Card rounded)
# ----------------------------------------------------------------------------
def make_card_assets(out_dir: Path, accent: Tuple[int, int, int],
                     cw: int = 880, ch: int = 1080, r: int = 44) -> Tuple[Path, Path, int]:
    """Buat mask rounded (grayscale) + layer bayangan/border glow. Return (mask, shadow, pad)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    mask = rrect(cw, ch, r, (255, 255, 255, 255)).getchannel("A")
    mask_p = out_dir / "card_mask.png"
    Image.merge("RGB", (mask, mask, mask)).save(mask_p)

    pad = 60
    sh = Image.new("RGBA", (cw + pad * 2, ch + pad * 2), (0, 0, 0, 0))
    base = rrect(cw, ch, r, (0, 0, 0, 255))
    sh.alpha_composite(fade(base, 0.75), (pad, pad + 22))
    sh = sh.filter(ImageFilter.GaussianBlur(26))
    ring = rrect(cw + 12, ch + 12, r + 6, (0, 0, 0, 0), outline=accent + (255,), width=6)
    g = glow(ring, accent, blur=16, strength=0.8)
    gp = (g.size[0] - ring.size[0]) // 2
    paste_at(sh, g, pad - 6 - gp, pad - 6 - gp)
    shadow_p = out_dir / "card_shadow.png"
    sh.save(shadow_p)
    return mask_p, shadow_p, pad
