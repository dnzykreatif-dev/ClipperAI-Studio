"""
ClipperAI Studio - Modern Visual Studio & 3D Component Engine
Menghasilkan aset grafis modern kelas SaaS / AnyMotion:
- 3D Smartphone Device Mockup dengan layar interaktif dinamis & soft ambient shadow
- Floating macOS Application Window dengan kontrol traffic light
- Apple-Style Clean Feature Cards dengan icon & animated checkmark
- Dual-Tone Typography (Modern Sans-Serif + Georgia Italic Editorial Accent)
- Minimalist Pill Subtitle Karaoke
- Timeline Motion Graphics Engine
"""

from __future__ import annotations

import math
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FPS = 30

BASE_DIR = Path(__file__).resolve().parent
FONT_DIR = BASE_DIR / "assets" / "fonts"
WIN_FONTS = Path("C:/Windows/Fonts")

# ---------------------------------------------------------------------------
# Easing & Spring Physics
# ---------------------------------------------------------------------------
def clamp(x: float, a: float = 0.0, b: float = 1.0) -> float:
    return a if x < a else b if x > b else x


def ease_out_cubic(t: float) -> float:
    t = clamp(t)
    return 1 - (1 - t) ** 3


def spring(t: float, freq: float = 11.0, damp: float = 7.0) -> float:
    if t <= 0:
        return 0.0
    return 1 - math.exp(-damp * t) * math.cos(freq * t)


# ---------------------------------------------------------------------------
# Font Manager
# ---------------------------------------------------------------------------
_FONT_CHAIN = {
    "black": ["Montserrat-Black.ttf", "seguibl.ttf", "ariblk.ttf", "arialbd.ttf"],
    "extrabold": ["Montserrat-ExtraBold.ttf", "segoeuib.ttf", "arialbd.ttf"],
    "bold": ["Montserrat-Bold.ttf", "segoeuib.ttf", "arialbd.ttf"],
    "semibold": ["Montserrat-SemiBold.ttf", "seguisb.ttf", "arial.ttf"],
    "italic": ["georgiai.ttf", "timesi.ttf", "segoeuii.ttf", "ariali.ttf"],
    "regular": ["segoeui.ttf", "arial.ttf"]
}

@lru_cache(maxsize=64)
def get_font(style: str, size: int) -> ImageFont.FreeTypeFont:
    for name in _FONT_CHAIN.get(style, _FONT_CHAIN["bold"]):
        for d in (FONT_DIR, WIN_FONTS):
            p = d / name
            if p.exists():
                return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def text_img(text: str, font_obj: ImageFont.FreeTypeFont, fill: Tuple[int, int, int, int]) -> Image.Image:
    bbox = font_obj.getbbox(text)
    w = max(1, bbox[2] - bbox[0] + 12)
    h = max(1, bbox[3] - bbox[1] + 12)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((-bbox[0] + 6, -bbox[1] + 6), text, font=font_obj, fill=fill)
    return im


def round_rect(w: int, h: int, radius: int, fill: Tuple[int, int, int, int],
               outline: Optional[Tuple[int, int, int, int]] = None, width: int = 1) -> Image.Image:
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=fill, outline=outline, width=width)
    return im


def shadow_box(base_im: Image.Image, blur: int = 28, offset_y: int = 18, opacity: float = 0.40) -> Image.Image:
    w, h = base_im.size
    pad = blur * 2
    sh = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    alpha = base_im.getchannel("A")
    black = Image.new("RGBA", (w, h), (0, 0, 0, int(255 * opacity)))
    black.putalpha(alpha)
    sh.alpha_composite(black, (pad, pad + offset_y))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    sh.alpha_composite(base_im, (pad, pad))
    return sh


def draw_vector_checkmark(d: ImageDraw.ImageDraw, cx: int, cy: int, size: int,
                          color: Tuple[int, int, int, int], width: int = 4):
    """Menggambar centang vektor anti-aliased halus tanpa tergantung simbol font."""
    p0 = (cx - size // 2, cy)
    p1 = (cx - size // 6, cy + size // 3)
    p2 = (cx + size // 2, cy - size // 3)
    d.line([p0, p1, p2], fill=color, width=width)


def draw_vector_cross(d: ImageDraw.ImageDraw, cx: int, cy: int, size: int,
                      color: Tuple[int, int, int, int], width: int = 4):
    half = size // 3
    d.line([(cx - half, cy - half), (cx + half, cy + half)], fill=color, width=width)
    d.line([(cx - half, cy + half), (cx + half, cy - half)], fill=color, width=width)


def draw_vector_star(draw: ImageDraw.ImageDraw, cx: float, cy: float, radius: float,
                     fill: Tuple[int, int, int, int]) -> None:
    """Draws a clean geometric 5-point star without font unicode dependency."""
    points = []
    r_in = radius * 0.44
    for i in range(10):
        angle = -math.pi / 2 + i * (math.pi / 5)
        r = radius if i % 2 == 0 else r_in
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(points, fill=fill)


def paste_center(dst: Image.Image, src: Image.Image, cx: float, cy: float) -> None:
    x = int(round(cx - src.size[0] / 2))
    y = int(round(cy - src.size[1] / 2))
    dst.alpha_composite(src, (x, y))


def transform(im: Image.Image, scale: float = 1.0, alpha: float = 1.0) -> Image.Image:
    if scale != 1.0:
        nw = max(1, int(round(im.size[0] * scale)))
        nh = max(1, int(round(im.size[1] * scale)))
        im = im.resize((nw, nh), resample=Image.BILINEAR)
    if alpha < 0.999:
        r, g, b, a = im.split()
        a = a.point(lambda v: int(v * max(0.0, min(1.0, alpha))))
        im = Image.merge("RGBA", (r, g, b, a))
    return im


# ---------------------------------------------------------------------------
# Visual Components
# ---------------------------------------------------------------------------

def render_dual_tone_title(regular_text: str, italic_text: str, trailing_text: str = "",
                           theme_accent: Tuple[int, int, int] = (16, 185, 129),
                           is_dark: bool = False) -> Image.Image:
    f_reg = get_font("bold", 54)
    f_ita = get_font("italic", 58)
    main_col = (255, 255, 255, 255) if is_dark else (24, 30, 42, 255)
    accent_col = theme_accent + (255,)

    im_reg = text_img(regular_text + " ", f_reg, main_col)
    im_ita = text_img(italic_text + " ", f_ita, accent_col)
    im_tra = text_img(trailing_text, f_reg, main_col) if trailing_text else None

    tot_w = im_reg.size[0] + im_ita.size[0] + (im_tra.size[0] if im_tra else 0)
    tot_h = max(im_reg.size[1], im_ita.size[1], im_tra.size[1] if im_tra else 0) + 10

    canvas = Image.new("RGBA", (tot_w, tot_h), (0, 0, 0, 0))
    curr_x = 0
    canvas.alpha_composite(im_reg, (curr_x, (tot_h - im_reg.size[1]) // 2))
    curr_x += im_reg.size[0]
    canvas.alpha_composite(im_ita, (curr_x, (tot_h - im_ita.size[1]) // 2))
    curr_x += im_ita.size[0]
    if im_tra:
        canvas.alpha_composite(im_tra, (curr_x, (tot_h - im_tra.size[1]) // 2))
    return canvas


def render_smartphone_mockup(screen_content: Image.Image,
                             phone_w: int = 560, phone_h: int = 1040,
                             is_dark: bool = False) -> Image.Image:
    body_col = (28, 32, 44, 255) if is_dark else (242, 244, 248, 255)
    border_col = (60, 68, 88, 255) if is_dark else (208, 214, 226, 255)

    base = round_rect(phone_w, phone_h, radius=56, fill=body_col, outline=border_col, width=4)
    d = ImageDraw.Draw(base)

    screen_inset = 18
    sw = phone_w - screen_inset * 2
    sh = phone_h - screen_inset * 2

    resized_content = screen_content.resize((sw, sh), Image.LANCZOS)
    screen_mask = round_rect(sw, sh, radius=42, fill=(255, 255, 255, 255)).getchannel("A")
    base.paste(resized_content, (screen_inset, screen_inset), screen_mask)

    # Dynamic Island / Pill Camera
    pill_w, pill_h = 130, 32
    pill_x = (phone_w - pill_w) // 2
    pill_y = screen_inset + 14
    d.rounded_rectangle((pill_x, pill_y, pill_x + pill_w, pill_y + pill_h), radius=16, fill=(10, 12, 18, 255))
    d.ellipse((pill_x + pill_w - 24, pill_y + 8, pill_x + pill_w - 8, pill_y + 24), fill=(24, 30, 48, 255))

    glare = Image.new("RGBA", (phone_w, phone_h), (0, 0, 0, 0))
    d_g = ImageDraw.Draw(glare)
    d_g.polygon([(0, 0), (phone_w // 2, 0), (0, phone_h // 2)], fill=(255, 255, 255, 22))
    base.alpha_composite(glare)

    return shadow_box(base, blur=34, offset_y=28, opacity=0.38)


def render_macos_window(title: str, content_im: Image.Image,
                        win_w: int = 880, win_h: int = 680,
                        is_dark: bool = False,
                        theme_accent: Tuple[int, int, int] = (16, 185, 129)) -> Image.Image:
    body_col = (18, 24, 38, 250) if is_dark else (255, 255, 255, 252)
    border_col = (theme_accent[0], theme_accent[1], theme_accent[2], 180) if is_dark else (226, 232, 240, 255)

    base = round_rect(win_w, win_h, radius=28, fill=body_col, outline=border_col, width=2)
    d = ImageDraw.Draw(base)

    d.line([(0, 68), (win_w, 68)], fill=(40, 48, 68, 180) if is_dark else (241, 245, 249, 255), width=2)

    # Traffic Lights
    d.ellipse((26, 26, 44, 44), fill=(255, 95, 87, 255))
    d.ellipse((54, 26, 72, 44), fill=(254, 188, 46, 255))
    d.ellipse((82, 26, 100, 44), fill=(40, 200, 64, 255))

    f_title = get_font("semibold", 24)
    t_color = (203, 213, 225, 255) if is_dark else (71, 85, 105, 255)
    t_im = text_img(title, f_title, t_color)
    base.alpha_composite(t_im, ((win_w - t_im.size[0]) // 2, 22))

    cw = win_w - 32
    ch = win_h - 96
    res_content = content_im.resize((cw, ch), Image.LANCZOS)
    c_mask = round_rect(cw, ch, radius=16, fill=(255, 255, 255, 255)).getchannel("A")
    base.paste(res_content, (16, 80), c_mask)

    return shadow_box(base, blur=32, offset_y=24, opacity=0.35)


def render_apple_feature_card(title: str, subtitle: str,
                              card_w: int = 860, card_h: int = 140,
                              theme_accent: Tuple[int, int, int] = (16, 185, 129),
                              is_dark: bool = False) -> Image.Image:
    card_bg = (24, 30, 44, 248) if is_dark else (255, 255, 255, 252)
    border_col = (51, 65, 85, 255) if is_dark else (241, 245, 249, 255)

    base = round_rect(card_w, card_h, radius=24, fill=card_bg, outline=border_col, width=2)
    d = ImageDraw.Draw(base)

    circle_size = 56
    cx, cy = 34, (card_h - circle_size) // 2
    d.ellipse((cx, cy, cx + circle_size, cy + circle_size), fill=theme_accent + (230,))
    draw_vector_checkmark(d, cx + circle_size // 2, cy + circle_size // 2, 26, (255, 255, 255, 255), width=4)

    f_t = get_font("extrabold", 34)
    f_s = get_font("semibold", 22)
    t_col = (255, 255, 255, 255) if is_dark else (30, 41, 59, 255)
    s_col = (148, 163, 184, 255) if is_dark else (100, 116, 139, 255)

    t_im = text_img(title, f_t, t_col)
    s_im = text_img(subtitle, f_s, s_col)

    text_x = cx + circle_size + 24
    base.alpha_composite(t_im, (text_x, 28))
    base.alpha_composite(s_im, (text_x, 76))

    pill_w, pill_h = 48, 48
    px = card_w - pill_w - 34
    py = (card_h - pill_h) // 2
    d.rounded_rectangle((px, py, px + pill_w, py + pill_h), radius=12,
                        fill=(241, 245, 249, 255) if not is_dark else (30, 41, 59, 255))
    draw_vector_checkmark(d, px + pill_w // 2, py + pill_h // 2, 22, theme_accent + (255,), width=3)

    return shadow_box(base, blur=22, offset_y=12, opacity=0.25)


def render_mesh_gradient_background(theme: str = "mint", total_w: int = W, total_h: int = H) -> Image.Image:
    arr = np.zeros((total_h, total_w, 4), dtype=np.uint8)
    arr[:, :, 3] = 255

    y_grid, x_grid = np.ogrid[:total_h, :total_w]
    ny = y_grid / float(total_h)
    nx = x_grid / float(total_w)

    if theme == "mint":
        c_top = np.array([216, 238, 228], dtype=float)
        c_bot = np.array([244, 246, 242], dtype=float)
    elif theme == "obsidian":
        c_top = np.array([12, 17, 28], dtype=float)
        c_bot = np.array([7, 10, 16], dtype=float)
    elif theme == "cream":
        c_top = np.array([253, 250, 242], dtype=float)
        c_bot = np.array([242, 236, 224], dtype=float)
    elif theme == "emerald":
        c_top = np.array([12, 38, 28], dtype=float)
        c_bot = np.array([6, 20, 14], dtype=float)
    else:  # azure
        c_top = np.array([238, 244, 252], dtype=float)
        c_bot = np.array([248, 250, 253], dtype=float)

    for ch in range(3):
        arr[:, :, ch] = np.clip(c_top[ch] * (1.0 - ny) + c_bot[ch] * ny, 0, 255).astype(np.uint8)

    cx, cy = total_w / 2, total_h / 2
    dist = np.sqrt(((x_grid - cx) / cx) ** 2 + ((y_grid - cy) / cy) ** 2)
    vig = np.clip(1.0 - 0.12 * (dist ** 2), 0.88, 1.0)
    arr[:, :, :3] = (arr[:, :, :3] * vig[:, :, None]).astype(np.uint8)

    return Image.fromarray(arr, "RGBA")


# ---------------------------------------------------------------------------
# Timeline Elements & Anti-Slideshow Camera System
# ---------------------------------------------------------------------------

def camera_drift(lt: float, dur: float) -> Tuple[float, float, float]:
    """
    Anti-slideshow dynamic camera:
    Continuous gentle push-in scale (1.00 -> 1.038) + organic multi-axis micro-drift.
    Prevents any scene from freezing into a dead still frame. Inspired by video-talkcraft.
    """
    prog = clamp(lt / max(1.0, dur))
    push_in = 1.0 + 0.038 * prog
    bob_y = math.sin(lt * 1.8) * 7.5 + math.cos(lt * 0.9) * 3.5
    bob_x = math.cos(lt * 1.3) * 4.5
    return push_in, bob_x, bob_y


class Element:
    def active(self, t: float) -> bool:
        return self.t0 <= t <= self.t1

    def draw(self, canvas: Image.Image, t: float) -> None:
        pass


class DualToneTitleElement(Element):
    def __init__(self, regular: str, italic: str, trailing: str, t0: float, t1: float,
                 accent: Tuple[int, int, int], is_dark: bool = False, y_pos: int = 160):
        self.t0, self.t1 = t0, t1
        self.y_pos = y_pos
        self.im = render_dual_tone_title(regular, italic, trailing, theme_accent=accent, is_dark=is_dark)

    def draw(self, canvas: Image.Image, t: float) -> None:
        lt = t - self.t0
        if lt < 0 or t > self.t1:
            return
        out = clamp((t - (self.t1 - 0.16)) / 0.16)
        a = clamp(lt / 0.12) * (1 - out)
        slide_y = (1 - ease_out_cubic(clamp(lt / 0.35))) * -30
        paste_center(canvas, transform(self.im, 1.0, a), W / 2, self.y_pos + slide_y)


class PhoneHeroElement(Element):
    def __init__(self, screen_title: str, stat_title: str, stat_value: str,
                 card2_title: str, card2_value: str, t0: float, t1: float,
                 accent: Tuple[int, int, int], is_dark: bool = False):
        self.t0, self.t1 = t0, t1
        self.accent = accent

        # Synthesize clean modern UI on phone screen
        screen = Image.new("RGBA", (500, 960), (255, 255, 255, 255) if not is_dark else (20, 26, 38, 255))
        d = ImageDraw.Draw(screen)
        d.rectangle((0, 0, 500, 140), fill=accent + (255,))
        d.text((36, 60), screen_title[:22], font=get_font("bold", 34), fill=(255, 255, 255, 255))

        # Card 1
        d.rounded_rectangle((30, 170, 470, 320), radius=20, fill=(241, 245, 249, 255) if not is_dark else (30, 38, 56, 255))
        d.text((50, 195), stat_title.upper()[:28], font=get_font("extrabold", 20), fill=(100, 116, 139, 255))
        d.text((50, 230), stat_value[:14], font=get_font("black", 48), fill=accent + (255,))

        # Card 2
        d.rounded_rectangle((30, 350, 470, 500), radius=20, fill=(241, 245, 249, 255) if not is_dark else (30, 38, 56, 255))
        d.text((50, 375), card2_title.upper()[:28], font=get_font("extrabold", 20), fill=(100, 116, 139, 255))
        d.text((50, 410), card2_value[:14], font=get_font("black", 48), fill=(30, 41, 59, 255) if not is_dark else (255, 255, 255, 255))

        self.phone_im = render_smartphone_mockup(screen, phone_w=520, phone_h=980, is_dark=is_dark)

    def draw(self, canvas: Image.Image, t: float) -> None:
        lt = t - self.t0
        dur = self.t1 - self.t0
        if lt < 0 or t > self.t1:
            return
        out = clamp((t - (self.t1 - 0.16)) / 0.16)
        a = clamp(lt / 0.12) * (1 - out)
        s = spring(lt, freq=11.0, damp=7.0) if lt < 0.5 else 1.0
        push_in, bob_x, bob_y = camera_drift(lt, dur)
        paste_center(canvas, transform(self.phone_im, s * push_in, a), W / 2 + bob_x, 850 + bob_y)


class AppWindowElement(Element):
    def __init__(self, window_title: str, headline: str, subtext: str,
                 t0: float, t1: float, accent: Tuple[int, int, int], is_dark: bool = False):
        self.t0, self.t1 = t0, t1

        # Synthesize desktop interior
        interior = Image.new("RGBA", (840, 560), (248, 250, 252, 255) if not is_dark else (15, 20, 32, 255))
        d = ImageDraw.Draw(interior)

        d.rounded_rectangle((40, 40, 800, 220), radius=20, fill=(255, 255, 255, 255) if not is_dark else (24, 32, 48, 255))
        d.text((70, 70), headline[:32].upper(), font=get_font("extrabold", 36), fill=accent + (255,))
        d.text((70, 130), subtext[:48], font=get_font("semibold", 26), fill=(71, 85, 105, 255) if not is_dark else (203, 213, 225, 255))

        d.rounded_rectangle((40, 260, 390, 500), radius=20, fill=accent + (40,))
        d.text((70, 290), "AKTIVITAS DATA", font=get_font("extrabold", 22), fill=accent + (255,))
        d.text((70, 340), "Realtime", font=get_font("black", 44), fill=(30, 41, 59, 255) if not is_dark else (255, 255, 255, 255))

        d.rounded_rectangle((450, 260, 800, 500), radius=20, fill=(255, 255, 255, 255) if not is_dark else (24, 32, 48, 255))
        d.text((480, 290), "STATUS SERVER", font=get_font("extrabold", 22), fill=(100, 116, 139, 255))
        d.text((480, 340), "100% Aktif", font=get_font("black", 44), fill=accent + (255,))

        self.win_im = render_macos_window(window_title, interior, win_w=880, win_h=660, is_dark=is_dark, theme_accent=accent)

    def draw(self, canvas: Image.Image, t: float) -> None:
        lt = t - self.t0
        dur = self.t1 - self.t0
        if lt < 0 or t > self.t1:
            return
        out = clamp((t - (self.t1 - 0.16)) / 0.16)
        a = clamp(lt / 0.12) * (1 - out)
        s = spring(lt, freq=11.0, damp=7.0) if lt < 0.5 else 1.0
        push_in, bob_x, bob_y = camera_drift(lt, dur)
        paste_center(canvas, transform(self.win_im, s * push_in, a), W / 2 + bob_x, 850 + bob_y)


class StatShockElement(Element):
    def __init__(self, stat_number: str, stat_label: str, t0: float, t1: float,
                 accent: Tuple[int, int, int], is_dark: bool = False):
        self.t0, self.t1 = t0, t1
        card_w, card_h = 880, 400
        base = round_rect(card_w, card_h, radius=32, fill=(255, 255, 255, 252) if not is_dark else (20, 28, 44, 250),
                          outline=accent + (180,), width=2)
        d = ImageDraw.Draw(base)

        tag_im = text_img("DATA & FAKTA UTAMA", get_font("extrabold", 20), accent + (255,))
        pw, ph = tag_im.size[0] + 32, 44
        d.rounded_rectangle((50, 45, 50 + pw, 45 + ph), radius=22, fill=accent + (35,))
        base.alpha_composite(tag_im, (50 + 16, 45 + (ph - tag_im.size[1]) // 2))

        stat_im = text_img(stat_number[:12], get_font("black", 108), accent + (255,))
        base.alpha_composite(stat_im, (50, 110))

        lbl_im = text_img(stat_label[:40], get_font("bold", 34), (30, 41, 59, 255) if not is_dark else (226, 232, 240, 255))
        base.alpha_composite(lbl_im, (50, 260))

        self.card = shadow_box(base, blur=28, offset_y=16, opacity=0.35)

    def draw(self, canvas: Image.Image, t: float) -> None:
        lt = t - self.t0
        dur = self.t1 - self.t0
        if lt < 0 or t > self.t1:
            return
        out = clamp((t - (self.t1 - 0.16)) / 0.16)
        a = clamp(lt / 0.12) * (1 - out)
        s = spring(lt, freq=11.0, damp=7.0) if lt < 0.5 else 1.0
        push_in, bob_x, bob_y = camera_drift(lt, dur)
        paste_center(canvas, transform(self.card, s * push_in, a), W / 2 + bob_x, 850 + bob_y)


class MetricCounterElement(Element):
    """
    Animated counter card that ticks upwards from 0 to target value (e.g. 0% -> 99.8% or 0 -> 10,000)
    with a live progress bar fill! Inspired by video-talkcraft and video-shotcraft.
    """
    def __init__(self, target_val: str, label: str, sublabel: str, t0: float, t1: float,
                 accent: Tuple[int, int, int], is_dark: bool = False):
        self.t0, self.t1 = t0, t1
        self.target_val = target_val
        self.label = label
        self.sublabel = sublabel
        self.accent = accent
        self.is_dark = is_dark

        import re
        nums = re.findall(r"[\d\.,]+", target_val)
        self.num_str = nums[0] if nums else ""
        if self.num_str:
            idx = target_val.find(self.num_str)
            self.prefix = target_val[:idx]
            self.suffix = target_val[idx + len(self.num_str):]
        else:
            self.prefix, self.suffix = "", ""
        try:
            self.clean_target = float(self.num_str.replace(",", "."))
            self.is_float = "." in self.num_str or "," in self.num_str
        except Exception:
            self.clean_target = 100.0
            self.is_float = False

    def draw(self, canvas: Image.Image, t: float) -> None:
        lt = t - self.t0
        dur = self.t1 - self.t0
        if lt < 0 or t > self.t1:
            return
        out = clamp((t - (self.t1 - 0.16)) / 0.16)
        a = clamp(lt / 0.12) * (1 - out)
        s = spring(lt, freq=11.0, damp=7.0) if lt < 0.5 else 1.0
        push_in, bob_x, bob_y = camera_drift(lt, dur)

        prog = ease_out_cubic(clamp(lt / 1.5))
        if self.num_str:
            curr_num = self.clean_target * prog
            if self.is_float:
                cur_text = f"{self.prefix}{curr_num:0.1f}{self.suffix}"
            else:
                cur_text = f"{self.prefix}{int(round(curr_num))}{self.suffix}"
        else:
            cur_text = self.target_val

        card_w, card_h = 880, 420
        base = round_rect(card_w, card_h, radius=32,
                          fill=(255, 255, 255, 252) if not self.is_dark else (20, 28, 44, 250),
                          outline=self.accent + (180,), width=2)
        d = ImageDraw.Draw(base)

        tag_im = text_img("METRIK & PERFORMA TERTINGGI", get_font("extrabold", 20), self.accent + (255,))
        pw, ph = tag_im.size[0] + 32, 44
        d.rounded_rectangle((50, 45, 50 + pw, 45 + ph), radius=22, fill=self.accent + (35,))
        base.alpha_composite(tag_im, (50 + 16, 45 + (ph - tag_im.size[1]) // 2))

        val_im = text_img(cur_text, get_font("black", 108), self.accent + (255,))
        base.alpha_composite(val_im, (50, 105))

        lbl_im = text_img(self.label[:36], get_font("bold", 34),
                          (30, 41, 59, 255) if not self.is_dark else (226, 232, 240, 255))
        base.alpha_composite(lbl_im, (50, 250))

        bar_w, bar_h = 780, 14
        bx, by = 50, 320
        d.rounded_rectangle((bx, by, bx + bar_w, by + bar_h), radius=7,
                            fill=(241, 245, 249, 255) if not self.is_dark else (30, 41, 59, 255))
        fill_w = int(round(bar_w * prog))
        if fill_w > 0:
            d.rounded_rectangle((bx, by, bx + fill_w, by + bar_h), radius=7, fill=self.accent + (255,))

        sub_im = text_img(self.sublabel[:48], get_font("semibold", 22),
                          (100, 116, 139, 255) if not self.is_dark else (148, 163, 184, 255))
        base.alpha_composite(sub_im, (50, 355))

        card = shadow_box(base, blur=28, offset_y=16, opacity=0.35)
        paste_center(canvas, transform(card, s * push_in, a), W / 2 + bob_x, 850 + bob_y)


class TweetQuoteElement(Element):
    """
    Modern verified testimonial & quote card. Inspired by herk-edit-kit & video-shotcraft.
    """
    def __init__(self, author: str, handle: str, quote: str, role: str, t0: float, t1: float,
                 accent: Tuple[int, int, int], is_dark: bool = False):
        self.t0, self.t1 = t0, t1
        self.accent = accent
        self.is_dark = is_dark

        card_w, card_h = 880, 430
        base = round_rect(card_w, card_h, radius=32,
                          fill=(255, 255, 255, 252) if not is_dark else (20, 28, 44, 250),
                          outline=(226, 232, 240, 255) if not is_dark else (51, 65, 85, 255), width=2)
        d = ImageDraw.Draw(base)

        av_size = 72
        ax, ay = 50, 45
        d.ellipse((ax, ay, ax + av_size, ay + av_size), fill=accent + (230,))
        initials = "".join([w[0].upper() for w in author.split()[:2]]) or "U"
        init_im = text_img(initials, get_font("black", 32), (255, 255, 255, 255))
        base.alpha_composite(init_im, (ax + (av_size - init_im.size[0]) // 2, ay + (av_size - init_im.size[1]) // 2))

        name_im = text_img(author[:24], get_font("extrabold", 30),
                           (30, 41, 59, 255) if not is_dark else (255, 255, 255, 255))
        base.alpha_composite(name_im, (ax + av_size + 20, ay + 6))

        v_size = 28
        vx = ax + av_size + 20 + name_im.size[0] + 12
        vy = ay + 8
        d.ellipse((vx, vy, vx + v_size, vy + v_size), fill=(14, 165, 233, 255))
        draw_vector_checkmark(d, vx + v_size // 2, vy + v_size // 2, 14, (255, 255, 255, 255), width=2)

        handle_str = handle if handle.startswith("@") else f"@{handle}"
        handle_im = text_img(handle_str[:28], get_font("semibold", 20),
                             (100, 116, 139, 255) if not is_dark else (148, 163, 184, 255))
        base.alpha_composite(handle_im, (ax + av_size + 20, ay + 42))

        # 5 Vector Gold Stars
        star_start_x = card_w - 50 - (5 * 28)
        for s_i in range(5):
            draw_vector_star(d, star_start_x + s_i * 28 + 14, ay + 24, 12, (245, 158, 11, 255))

        q_lines = []
        words = quote.split()
        cur_l = []
        for w in words:
            cur_l.append(w)
            if len(" ".join(cur_l)) >= 38:
                q_lines.append(" ".join(cur_l))
                cur_l = []
        if cur_l:
            q_lines.append(" ".join(cur_l))

        f_q = get_font("bold", 30)
        qy = 150
        for line in q_lines[:3]:
            line_im = text_img(line, f_q, (30, 41, 59, 255) if not is_dark else (241, 245, 249, 255))
            base.alpha_composite(line_im, (50, qy))
            qy += 44

        d.line([(50, card_h - 75), (card_w - 50, card_h - 75)],
               fill=(241, 245, 249, 255) if not is_dark else (40, 48, 68, 255), width=1)
        foot_im = text_img(f"✓ {role.upper()[:24]} • TERVERIFIKASI RESMI", get_font("extrabold", 18), accent + (255,))
        base.alpha_composite(foot_im, (50, card_h - 52))

        self.card = shadow_box(base, blur=28, offset_y=16, opacity=0.35)

    def draw(self, canvas: Image.Image, t: float) -> None:
        lt = t - self.t0
        dur = self.t1 - self.t0
        if lt < 0 or t > self.t1:
            return
        out = clamp((t - (self.t1 - 0.16)) / 0.16)
        a = clamp(lt / 0.12) * (1 - out)
        s = spring(lt, freq=11.0, damp=7.0) if lt < 0.5 else 1.0
        push_in, bob_x, bob_y = camera_drift(lt, dur)
        paste_center(canvas, transform(self.card, s * push_in, a), W / 2 + bob_x, 850 + bob_y)


class SplitVsElement(Element):
    """
    Dramatic Versus battle comparison: Left vs Right or Problem vs Solution with golden VS badge.
    Inspired by video-talkcraft and huashu-art-motion.
    """
    def __init__(self, left_title: str, left_desc: str, right_title: str, right_desc: str,
                 t0: float, t1: float, accent: Tuple[int, int, int], is_dark: bool = False):
        self.t0, self.t1 = t0, t1

        b1 = round_rect(880, 180, radius=24,
                        fill=(254, 242, 242, 250) if not is_dark else (40, 24, 28, 250),
                        outline=(239, 68, 68, 140), width=2)
        d1 = ImageDraw.Draw(b1)
        tag_l = text_img(left_title.upper()[:26], get_font("extrabold", 20), (220, 38, 38, 255))
        lw = tag_l.size[0] + 52
        d1.rounded_rectangle((36, 20, 36 + lw, 20 + 38), radius=19, fill=(239, 68, 68, 30))
        draw_vector_cross(d1, 36 + 20, 20 + 19, 16, (220, 38, 38, 255), width=3)
        b1.alpha_composite(tag_l, (36 + 40, 20 + (38 - tag_l.size[1]) // 2))
        d_l = text_img(left_desc[:44], get_font("bold", 28), (71, 85, 105, 255) if not is_dark else (226, 232, 240, 255))
        b1.alpha_composite(d_l, (36, 80))
        self.card_left = shadow_box(b1, blur=20, offset_y=10, opacity=0.25)

        b2 = round_rect(880, 180, radius=24,
                        fill=(240, 253, 244, 250) if not is_dark else (20, 42, 34, 250),
                        outline=accent + (180,), width=2)
        d2 = ImageDraw.Draw(b2)
        tag_r = text_img(right_title.upper()[:26], get_font("extrabold", 20), accent + (255,))
        rw = tag_r.size[0] + 52
        d2.rounded_rectangle((36, 20, 36 + rw, 20 + 38), radius=19, fill=accent + (35,))
        draw_vector_checkmark(d2, 36 + 20, 20 + 19, 18, accent + (255,), width=3)
        b2.alpha_composite(tag_r, (36 + 40, 20 + (38 - tag_r.size[1]) // 2))
        d_r = text_img(right_desc[:44], get_font("black", 28), accent + (255,))
        b2.alpha_composite(d_r, (36, 80))
        self.card_right = shadow_box(b2, blur=24, offset_y=12, opacity=0.30)

        vs_b = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
        dv = ImageDraw.Draw(vs_b)
        dv.ellipse((6, 6, 94, 94), fill=(245, 158, 11, 255), outline=(255, 255, 255, 255), width=4)
        vs_t = text_img("VS", get_font("black", 36), (255, 255, 255, 255))
        vs_b.alpha_composite(vs_t, ((100 - vs_t.size[0]) // 2, (100 - vs_t.size[1]) // 2))
        self.vs_badge = shadow_box(vs_b, blur=18, offset_y=6, opacity=0.40)

    def draw(self, canvas: Image.Image, t: float) -> None:
        lt = t - self.t0
        dur = self.t1 - self.t0
        if lt < 0 or t > self.t1:
            return
        out = clamp((t - (self.t1 - 0.16)) / 0.16)
        push_in, bob_x, bob_y = camera_drift(lt, dur)

        a1 = clamp(lt / 0.12) * (1 - out)
        s1 = ease_out_cubic(clamp(lt / 0.35))
        paste_center(canvas, transform(self.card_left, 1.0 * push_in, a1), W / 2 + bob_x, 720 + (1 - s1) * -30 + bob_y)

        lt2 = lt - 0.20
        if lt2 > 0:
            a2 = clamp(lt2 / 0.12) * (1 - out)
            s2 = spring(lt2, freq=11.0, damp=7.0) if lt2 < 0.5 else 1.0
            paste_center(canvas, transform(self.card_right, s2 * push_in, a2), W / 2 + bob_x, 970 + bob_y)

        lt_vs = lt - 0.30
        if lt_vs > 0:
            a_vs = clamp(lt_vs / 0.10) * (1 - out)
            s_vs = spring(lt_vs, freq=13.0, damp=6.0) if lt_vs < 0.5 else 1.0 + 0.05 * math.sin(lt * 4.0)
            paste_center(canvas, transform(self.vs_badge, s_vs * push_in, a_vs), W / 2 + bob_x, 845 + bob_y)


class CodeTerminalElement(Element):
    """
    macOS Dark Code Terminal with typing effect and live sync status.
    Inspired by openfilm and video-shotcraft developer promos.
    """
    def __init__(self, command: str, line1: str, line2: str, status: str,
                 t0: float, t1: float, accent: Tuple[int, int, int], is_dark: bool = False):
        self.t0, self.t1 = t0, t1
        self.command = command
        self.line1 = line1
        self.line2 = line2
        self.status = status
        self.accent = accent

    def draw(self, canvas: Image.Image, t: float) -> None:
        lt = t - self.t0
        dur = self.t1 - self.t0
        if lt < 0 or t > self.t1:
            return
        out = clamp((t - (self.t1 - 0.16)) / 0.16)
        a = clamp(lt / 0.12) * (1 - out)
        s = spring(lt, freq=11.0, damp=7.0) if lt < 0.5 else 1.0
        push_in, bob_x, bob_y = camera_drift(lt, dur)

        win_w, win_h = 880, 480
        base = round_rect(win_w, win_h, radius=24, fill=(15, 23, 42, 252), outline=(51, 65, 85, 255), width=2)
        d = ImageDraw.Draw(base)

        d.line([(0, 60), (win_w, 60)], fill=(30, 41, 59, 255), width=2)
        d.ellipse((26, 22, 42, 38), fill=(255, 95, 87, 255))
        d.ellipse((50, 22, 66, 38), fill=(254, 188, 46, 255))
        d.ellipse((74, 22, 90, 38), fill=(40, 200, 64, 255))
        t_title = text_img("terminal ~ system_sync", get_font("semibold", 20), (148, 163, 184, 255))
        base.alpha_composite(t_title, ((win_w - t_title.size[0]) // 2, 18))

        f_code = get_font("bold", 24)
        typed_len = int(round(len(self.command) * clamp(lt / 0.8)))
        cmd_str = f"> {self.command[:typed_len]}" + ("_" if int(lt * 4) % 2 == 0 else "")
        base.alpha_composite(text_img(cmd_str, f_code, self.accent + (255,)), (40, 90))

        if lt >= 0.8:
            base.alpha_composite(text_img(f"[OK] {self.line1[:42]}", f_code, (226, 232, 240, 255)), (40, 150))
        if lt >= 1.4:
            base.alpha_composite(text_img(f"[SYNC] {self.line2[:42]}", f_code, (148, 163, 184, 255)), (40, 210))

        if lt >= 1.8:
            stat_str = f"● {self.status.upper()[:32]}"
            st_im = text_img(stat_str, get_font("extrabold", 20), (34, 197, 94, 255))
            sw, sh = st_im.size[0] + 32, 40
            d.rounded_rectangle((40, 390, 40 + sw, 390 + sh), radius=20, fill=(34, 197, 94, 35))
            base.alpha_composite(st_im, (40 + 16, 390 + (sh - st_im.size[1]) // 2))

        card = shadow_box(base, blur=28, offset_y=16, opacity=0.35)
        paste_center(canvas, transform(card, s * push_in, a), W / 2 + bob_x, 850 + bob_y)


class FloatingBadgeElement(Element):
    """
    Luxury stamped seal / badge that floats with gentle breathing tilt.
    """
    def __init__(self, badge_title: str, badge_sub: str, t0: float, t1: float,
                 accent: Tuple[int, int, int], is_dark: bool = False):
        self.t0, self.t1 = t0, t1

        card_w, card_h = 820, 360
        base = round_rect(card_w, card_h, radius=36,
                          fill=(255, 255, 255, 252) if not is_dark else (20, 28, 44, 250),
                          outline=accent + (220,), width=3)
        d = ImageDraw.Draw(base)

        t_im = text_img(badge_title.upper()[:28], get_font("black", 44), accent + (255,))
        tx = (card_w - t_im.size[0]) // 2
        base.alpha_composite(t_im, (tx, 70))
        draw_vector_star(d, tx - 36, 70 + t_im.size[1] // 2, 16, (245, 158, 11, 255))
        draw_vector_star(d, tx + t_im.size[0] + 36, 70 + t_im.size[1] // 2, 16, (245, 158, 11, 255))

        s_im = text_img(badge_sub[:38], get_font("bold", 30),
                        (30, 41, 59, 255) if not is_dark else (226, 232, 240, 255))
        base.alpha_composite(s_im, ((card_w - s_im.size[0]) // 2, 150))

        pill_w, pill_h = 440, 60
        px = (card_w - pill_w) // 2
        py = 230
        d.rounded_rectangle((px, py, px + pill_w, py + pill_h), radius=30, fill=accent + (255,))
        guar_im = text_img("100% RESMI & TERUJI", get_font("extrabold", 24), (255, 255, 255, 255))
        base.alpha_composite(guar_im, (px + (pill_w - guar_im.size[0]) // 2, py + (pill_h - guar_im.size[1]) // 2))

        self.card = shadow_box(base, blur=28, offset_y=16, opacity=0.35)

    def draw(self, canvas: Image.Image, t: float) -> None:
        lt = t - self.t0
        dur = self.t1 - self.t0
        if lt < 0 or t > self.t1:
            return
        out = clamp((t - (self.t1 - 0.16)) / 0.16)
        a = clamp(lt / 0.12) * (1 - out)
        s = spring(lt, freq=11.0, damp=7.0) if lt < 0.5 else 1.0
        push_in, bob_x, bob_y = camera_drift(lt, dur)
        paste_center(canvas, transform(self.card, s * push_in, a), W / 2 + bob_x, 850 + bob_y)


class ComparisonElement(Element):
    def __init__(self, compare_before: str, compare_after: str, t0: float, t1: float,
                 accent: Tuple[int, int, int], is_dark: bool = False):
        self.t0, self.t1 = t0, t1

        b_base = round_rect(880, 200, radius=24,
                            fill=(254, 242, 242, 250) if not is_dark else (40, 24, 28, 250),
                            outline=(239, 68, 68, 140), width=2)
        d1 = ImageDraw.Draw(b_base)
        t_before = text_img("SEBELUM (CARA LAMA)", get_font("extrabold", 20), (220, 38, 38, 255))
        d1.rounded_rectangle((36, 25, 36 + t_before.size[0] + 28, 25 + 38), radius=19, fill=(239, 68, 68, 35))
        b_base.alpha_composite(t_before, (36 + 14, 25 + (38 - t_before.size[1]) // 2))
        msg_before = text_img(compare_before[:38], get_font("bold", 30), (71, 85, 105, 255) if not is_dark else (226, 232, 240, 255))
        b_base.alpha_composite(msg_before, (36, 88))
        self.card_before = shadow_box(b_base, blur=20, offset_y=10, opacity=0.25)

        a_base = round_rect(880, 200, radius=24,
                            fill=(240, 253, 244, 250) if not is_dark else (20, 42, 34, 250),
                            outline=accent + (180,), width=2)
        d2 = ImageDraw.Draw(a_base)
        t_after = text_img("SESUDAH (SOLUSI OTOMATIS)", get_font("extrabold", 20), accent + (255,))
        d2.rounded_rectangle((36, 25, 36 + t_after.size[0] + 28, 25 + 38), radius=19, fill=accent + (40,))
        a_base.alpha_composite(t_after, (36 + 14, 25 + (38 - t_after.size[1]) // 2))
        msg_after = text_img(compare_after[:38], get_font("black", 32), accent + (255,))
        a_base.alpha_composite(msg_after, (36, 88))
        self.card_after = shadow_box(a_base, blur=24, offset_y=12, opacity=0.30)

    def draw(self, canvas: Image.Image, t: float) -> None:
        lt = t - self.t0
        dur = self.t1 - self.t0
        if lt < 0 or t > self.t1:
            return
        out = clamp((t - (self.t1 - 0.16)) / 0.16)
        push_in, bob_x, bob_y = camera_drift(lt, dur)

        a1 = clamp(lt / 0.12) * (1 - out)
        s1 = ease_out_cubic(clamp(lt / 0.35))
        slide_y1 = (1 - s1) * -30
        paste_center(canvas, transform(self.card_before, 1.0 * push_in, a1), W / 2 + bob_x, 720 + slide_y1 + bob_y)

        lt2 = lt - 0.20
        if lt2 > 0:
            a2 = clamp(lt2 / 0.12) * (1 - out)
            s2 = spring(lt2, freq=11.0, damp=7.0) if lt2 < 0.5 else 1.0
            paste_center(canvas, transform(self.card_after, s2 * push_in, a2), W / 2 + bob_x, 970 + bob_y)


class FeatureListElement(Element):
    def __init__(self, features: List[Dict[str, str]], t0: float, t1: float,
                 accent: Tuple[int, int, int], is_dark: bool = False):
        self.t0, self.t1 = t0, t1
        self.accent = accent
        self.is_dark = is_dark
        self.cards = []
        for feat in features[:3]:
            card_im = render_apple_feature_card(feat.get("title", ""), feat.get("subtitle", ""),
                                                card_w=880, card_h=140, theme_accent=accent, is_dark=is_dark)
            self.cards.append(card_im)

    def draw(self, canvas: Image.Image, t: float) -> None:
        lt = t - self.t0
        dur = self.t1 - self.t0
        if lt < 0 or t > self.t1:
            return
        out = clamp((t - (self.t1 - 0.16)) / 0.16)
        push_in, bob_x, bob_y = camera_drift(lt, dur)

        base_y = 660
        spacing = 175
        for i, card_im in enumerate(self.cards):
            card_lt = lt - i * 0.22
            if card_lt > 0:
                card_a = clamp(card_lt / 0.12) * (1 - out)
                slide_x = (1 - ease_out_cubic(clamp(card_lt / 0.35))) * 60
                paste_center(canvas, transform(card_im, 1.0 * push_in, card_a), W / 2 + slide_x + bob_x, base_y + i * spacing + bob_y)


class CtaSlamElement(Element):
    def __init__(self, headline: str, button_text: str, t0: float, t1: float,
                 accent: Tuple[int, int, int], is_dark: bool = False):
        self.t0, self.t1 = t0, t1

        base = round_rect(900, 360, radius=32, fill=(255, 255, 255, 252) if not is_dark else (20, 28, 44, 250),
                          outline=accent + (220,), width=3)
        d = ImageDraw.Draw(base)

        f_h = get_font("black", 48)
        f_b = get_font("extrabold", 38)

        h_im = text_img(headline[:32], f_h, (30, 41, 59, 255) if not is_dark else (255, 255, 255, 255))
        base.alpha_composite(h_im, ((900 - h_im.size[0]) // 2, 60))

        btn_w, btn_h = 760, 94
        bx = (900 - btn_w) // 2
        by = 180
        d.rounded_rectangle((bx, by, bx + btn_w, by + btn_h), radius=26, fill=accent + (255,))
        b_im = text_img(button_text.upper()[:28], f_b, (255, 255, 255, 255))
        base.alpha_composite(b_im, (bx + (btn_w - b_im.size[0]) // 2, by + (btn_h - b_im.size[1]) // 2))

        self.card = shadow_box(base, blur=28, offset_y=16, opacity=0.35)

    def draw(self, canvas: Image.Image, t: float) -> None:
        lt = t - self.t0
        dur = self.t1 - self.t0
        if lt < 0 or t > self.t1:
            return
        out = clamp((t - (self.t1 - 0.16)) / 0.16)
        a = clamp(lt / 0.12) * (1 - out)
        s = spring(lt, freq=11.0, damp=7.0) if lt < 0.5 else 1.0
        push_in, bob_x, bob_y = camera_drift(lt, dur)
        paste_center(canvas, transform(self.card, s * push_in, a), W / 2 + bob_x, 850 + bob_y)


class PillCaptionElement(Element):
    """
    Subtitle Karaoke Kapsul Minimalis di Area Bawah (y=1560)
    Sangat rapi, elegan, berjarak aman dari panggung visual, dan menyorot kata aktif.
    """
    def __init__(self, all_words: List[Dict[str, Any]], accent: Tuple[int, int, int], is_dark: bool = False):
        self.all_words = all_words
        self.accent = accent
        self.t0 = all_words[0]["start"] if all_words else 0.0
        self.t1 = all_words[-1]["end"] if all_words else 999.0
        self.is_dark = is_dark
        self.f_cap = get_font("bold", 30)

        # Kelompokkan kata menjadi chunk kalimat 3-5 kata
        self.chunks = []
        chunk_size = 4
        for i in range(0, len(all_words), chunk_size):
            self.chunks.append(all_words[i:i + chunk_size])

    def draw(self, canvas: Image.Image, t: float) -> None:
        cur_chunk = None
        for chk in self.chunks:
            if chk[0]["start"] - 0.08 <= t <= chk[-1]["end"] + 0.10:
                cur_chunk = chk
                break
        if not cur_chunk:
            return

        # Render tokens in current chunk
        tokens_img = []
        for w in cur_chunk:
            w_str = w["word"].strip().upper()
            is_active = w["start"] <= t <= w["end"] + 0.08
            color = self.accent + (255,) if is_active else ((255, 255, 255, 255) if self.is_dark else (240, 244, 250, 255))
            tokens_img.append(text_img(w_str, self.f_cap, color))

        sp = 14
        tot_tw = sum(im.size[0] for im in tokens_img) + sp * max(0, len(tokens_img) - 1)
        pill_w = max(360, tot_tw + 64)
        pill_h = 72

        pill = round_rect(pill_w, pill_h, radius=pill_h // 2,
                          fill=(15, 23, 42, 242) if not self.is_dark else (24, 32, 48, 246),
                          outline=(51, 65, 85, 180) if not self.is_dark else self.accent + (160,), width=2)
        sh_pill = shadow_box(pill, blur=18, offset_y=8, opacity=0.30)

        cur_x = (pill_w - tot_tw) // 2
        for im in tokens_img:
            pill.alpha_composite(im, (cur_x, (pill_h - im.size[1]) // 2))
            cur_x += im.size[0] + sp

        paste_center(canvas, pill, W / 2, 1560)


class ProgressLineElement(Element):
    def __init__(self, total_dur: float, accent: Tuple[int, int, int]):
        self.t0, self.t1 = 0.0, total_dur
        self.accent = accent

    def draw(self, canvas: Image.Image, t: float) -> None:
        prog = clamp(t / max(0.1, self.t1))
        line_w = int(round(W * prog))
        if line_w > 0:
            d = ImageDraw.Draw(canvas)
            d.rectangle((0, H - 8, line_w, H), fill=self.accent + (255,))


# ---------------------------------------------------------------------------
# Timeline Renderer
# ---------------------------------------------------------------------------

class VisualTimeline:
    def __init__(self, total_dur: float, elements: List[Element], background_theme: str = "mint"):
        self.total_dur = total_dur
        self.elements = elements
        self.bg_frame = render_mesh_gradient_background(theme=background_theme)

    def frame(self, i: int) -> bytes:
        t = i / FPS
        canvas = self.bg_frame.copy()
        for e in self.elements:
            if e.active(t):
                e.draw(canvas, t)
        return canvas.tobytes()

    def n_frames(self) -> int:
        return int(math.ceil(self.total_dur * FPS))

    def preview(self, t: float) -> Image.Image:
        canvas = self.bg_frame.copy()
        for e in self.elements:
            if e.active(t):
                e.draw(canvas, t)
        return canvas
