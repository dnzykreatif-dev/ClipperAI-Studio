"""
ClipperAI Studio - AI Thumbnail Generator
Memilih frame ekspresi wajah terbaik dari video secara cerdas (YuNet Face Score + Laplacian Sharpness)
dan merender tipografi Hook Thumbnail ber-CTR tinggi dengan Montserrat-Black + Glow/Shadow.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

import motion_gfx as mg

try:
    import cv2
    CV2_OK = True
except Exception:
    CV2_OK = False

BASE_DIR = Path(__file__).resolve().parent
YUNET = BASE_DIR / "assets" / "models" / "face_detection_yunet_2023mar.onnx"

NICHE_ACCENTS = {
    "kajian": ((245, 158, 11), "MUTIARA HIKMAH"),
    "bisnis": ((16, 185, 129), "STRATEGI CUAN"),
    "podcast": ((56, 189, 248), "SOROTAN PODCAST"),
    "motivasi": ((244, 63, 94), "MINDSET JUARA"),
    "edukasi": ((99, 102, 241), "FAKTA PENTING"),
    "gaming": ((168, 85, 247), "HIGHLIGHT GAMING"),
    "universal": ((245, 158, 11), "VIRAL SHORTS"),
}


def pick_best_frame(video_path: str, t_start: float = 0.0, t_end: Optional[float] = None) -> Image.Image:
    """Memilih frame paling tajam dengan posisi wajah paling proporsional dari video."""
    if not CV2_OK:
        return Image.new("RGB", (1080, 1920), (18, 22, 36))

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return Image.new("RGB", (1080, 1920), (18, 22, 36))

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    dur = n_frames / max(fps, 1.0)
    a = max(0.0, t_start)
    b = min(dur, t_end if t_end and t_end > a else dur)
    if b <= a:
        a, b = 0.0, max(1.0, dur)

    fw = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 1080)
    fh = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 1920)
    scale = 480.0 / max(fw, 1) if fw > 480 else 1.0
    dw, dh = max(16, int(fw * scale)), max(16, int(fh * scale))

    det = None
    if YUNET.exists():
        try:
            det = cv2.FaceDetectorYN.create(str(YUNET), "", (dw, dh), 0.6, 0.3, 5000)
        except Exception:
            det = None

    sample_times = np.linspace(a + 0.12 * (b - a), a + 0.88 * (b - a), 10)
    best_frame = None
    best_score = -1e9

    for t in sample_times:
        cap.set(cv2.CAP_PROP_POS_MSEC, float(t) * 1000.0)
        ok, frame = cap.read()
        if not ok or frame is None:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        brightness = float(gray.mean())
        if brightness < 25 or brightness > 235:
            continue

        face_bonus = 0.0
        if det is not None:
            small = cv2.resize(frame, (dw, dh)) if scale != 1.0 else frame
            det.setInputSize((dw, dh))
            _, faces = det.detect(small)
            if faces is not None and len(faces):
                f = max(faces, key=lambda r: r[2] * r[3])
                cx = (f[0] + f[2] / 2) / dw
                cy = (f[1] + f[3] / 2) / dh
                area = (f[2] * f[3]) / (dw * dh)
                conf = float(f[-1])
                center_dist = abs(cx - 0.5) + abs(cy - 0.42)
                face_bonus = conf * 500.0 + area * 1200.0 - center_dist * 300.0

        score = sharpness + face_bonus
        if score > best_score:
            best_score = score
            best_frame = frame

    cap.release()
    if best_frame is None:
        return Image.new("RGB", (1080, 1920), (18, 22, 36))

    rgb = cv2.cvtColor(best_frame, cv2.COLOR_BGR2RGB)
    im = Image.fromarray(rgb)
    # Reframe ke 1080x1920 jika belum 9:16
    w, h = im.size
    target_ratio = 1080 / 1920
    if abs((w / h) - target_ratio) > 0.02:
        if w / h > target_ratio:
            nw = int(h * target_ratio)
            x0 = (w - nw) // 2
            im = im.crop((x0, 0, x0 + nw, h))
        else:
            nh = int(w / target_ratio)
            y0 = (h - nh) // 2
            im = im.crop((0, y0, w, y0 + nh))
    return im.resize((1080, 1920), Image.LANCZOS)


def generate_thumbnail(
    video_path: str,
    output_jpg: str,
    headline: str,
    sub_badge: Optional[str] = None,
    niche: str = "universal",
    clean_frame_jpg: Optional[str] = None,
) -> str:
    """
    Membuat thumbnail 9:16 ber-CTR tinggi dari frame bersih (tanpa teks subtitle bertumpuk).
    """
    accent, default_badge = NICHE_ACCENTS.get(niche, NICHE_ACCENTS["universal"])
    badge_text = (sub_badge or default_badge).strip().upper()
    badge_text = re.sub(r"[^A-Z0-9À-Ÿ\s\-&!]", "", badge_text).strip() or default_badge

    # Gunakan frame bersih (_clean.jpg) jika tersedia agar tidak bertumpuk dengan subtitle video
    auto_clean = Path(output_jpg).with_name(Path(output_jpg).name.replace("_thumb.jpg", "_clean.jpg"))
    if clean_frame_jpg and Path(clean_frame_jpg).exists():
        base = Image.open(clean_frame_jpg).convert("RGB")
    elif auto_clean.exists():
        base = Image.open(str(auto_clean)).convert("RGB")
    else:
        base = pick_best_frame(video_path).convert("RGB")
        try:
            base.save(str(auto_clean), "JPEG", quality=92)
        except Exception:
            pass
    # Tingkatkan kontras & ketajaman sedikit agar wajah lebih hidup di thumbnail
    base = ImageEnhance.Contrast(base).enhance(1.10)
    base = ImageEnhance.Color(base).enhance(1.12)
    base = ImageEnhance.Sharpness(base).enhance(1.25)

    canvas = base.convert("RGBA")

    # Gradien gelap sinematik di bagian bawah (y=1050..1920)
    grad_h = 870
    ramp = (np.linspace(0.0, 1.0, grad_h) ** 1.35 * 235).astype(np.uint8)
    grad_arr = np.zeros((grad_h, 1080, 4), dtype=np.uint8)
    grad_arr[:, :, 0] = 6
    grad_arr[:, :, 1] = 9
    grad_arr[:, :, 2] = 18
    grad_arr[:, :, 3] = ramp[:, None]
    canvas.alpha_composite(Image.fromarray(grad_arr, "RGBA"), (0, 1920 - grad_h))

    # Bersihkan headline & bagi menjadi 1-2 baris besar
    clean_hl = re.sub(r"[^A-Za-z0-9À-ÿ\s?!\-]", "", headline.upper()).strip()
    words = clean_hl.split()[:6]
    if not words:
        words = ["WAJIB", "SIMAK!"]
    if len(words) <= 2:
        lines = [" ".join(words)]
    else:
        mid = (len(words) + 1) // 2
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]

    # Render Badge Atas
    f_badge = mg.font("bold", 32)
    b_txt = mg.text_img(badge_text, f_badge, (12, 14, 22, 255) if mg.luminance(accent) > 0.5 else (255, 255, 255, 255), tracking=2)
    b_pill = mg.rrect(b_txt.size[0] + 52, b_txt.size[1] + 24, (b_txt.size[1] + 24) // 2, accent + (255,))
    b_pill.alpha_composite(b_txt, (26, 12))
    b_pill = mg.with_shadow(b_pill, blur=14, offset=(0, 6), opacity=0.6)

    y_cursor = 1360
    mg.paste_center(canvas, b_pill, 540, y_cursor)
    y_cursor += 95

    # Render Baris Headline Besar (baris terakhir memakai kotak aksen kuning/hijau agar menonjol)
    for idx, line in enumerate(lines):
        f_sz = 92 if len(line) <= 12 else (78 if len(line) <= 16 else 64)
        f_hl = mg.font("black", f_sz)
        is_last = idx == len(lines) - 1
        if is_last:
            t_col = (12, 12, 16, 255) if mg.luminance(accent) > 0.5 else (255, 255, 255, 255)
            t_im = mg.text_img(line, f_hl, t_col)
            box = mg.rrect(min(1000, t_im.size[0] + 56), t_im.size[1] + 28, 24, accent + (255,))
            mg.paste_center(box, t_im, box.size[0] / 2, box.size[1] / 2)
            box = mg.with_shadow(box, blur=18, offset=(0, 10), opacity=0.7)
            mg.paste_center(canvas, box, 540, y_cursor)
            y_cursor += box.size[1] + 22
        else:
            t_im = mg.text_img(line, f_hl, (255, 255, 255, 255), stroke=10, stroke_fill=(0, 0, 0, 255))
            t_im = mg.with_shadow(t_im, blur=16, offset=(0, 10), opacity=0.75)
            mg.paste_center(canvas, t_im, 540, y_cursor)
            y_cursor += t_im.size[1] + 18

    Path(output_jpg).parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output_jpg, "JPEG", quality=93)
    return output_jpg
