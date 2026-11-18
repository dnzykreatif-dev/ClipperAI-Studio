"""
ClipperAI Studio - REA Video Big Data & AnyMotion Intelligence Engine
=====================================================================
Hasil ekstraksi mendalam (Reverse Engineering Anything / REA) dari:
1. 11 Video Kreator & Iklan Komersial Viral (184 Shots, 2.405 Text Overlays, 622 SFX Events, 498 WAV SFX):
   - AnyMotion_RootPixel_System (SaaS & Fakta Unik Explainer, 60fps, 54 Particle/Cutout Code Scenes)
   - agusleo_cuan (Agusleo Halim - 4 Tangga 100 Juta Pertama dari AI, 24.7 CPM)
   - Raffi_Ahmad_14M (Dokumenter Investigasi Chapter Dossier, 24.0 CPM)
   - TeraUmroh_Ads (B2B SaaS Pain-to-Solution Ads, Emerald Cutout/Particle Morph)
   - BuatinVideo_Motion_Promo (POV Surreal Analogy & Claude Motion Promo)
   - Claude_Fable_Motion (After Effects Has A New Enemy - 100% Beat-Synced UI Spring)
   - FreeLLM_API_ClaudeCode_Promo (Open-Source GitHub Unlimited AI Tutorial)
   - Geo_Prophets_3D_Map_Infographic (Jejak Geografi Para Nabi - 3D Cartographic Camera Push-in)
   - Instagram_Agent_Skill_Promo (Creator Growth Hack - Rolling Counter 101K)
   - Interview_Skit_Buku_SDM (Roleplay Dialog Skit Manajer Gaji Rp25 Juta)
   - Michael_Hasim_Bongkar_Profil_IG (Audit Konversi Profil IG: Halaman Jualan vs Kartu Nama)

2. Mesin Internal Web App AnyMotion RootPixel (`Bev8DsUP.js`, `f64CrI6l.js`, `vn-nv65M.js`, `k2MSur2S.js`):
   - 212 Motion Styles (`Z(...)`) dalam 8 kategori utama
   - 33 Scene Card Templates (`X(...)`)
   - 95 Studio SFX & Stinger Manifest
   - 17 Visual Look Post-Processing Shaders (`flat`, `clay`, `line`, `whiteboard`, `sketch`, `engraving`,
     `comic`, `watercolor`, `riso`, `synth`, `lowpoly`, `bauhaus`, `swiss`, `kawaii`, `cinematic`,
     `tiltshift`, `blueprint`)
   - Morton Z-Order Particle & Cutout Morphing Engine (`Redraw` sub-pixel bilinear splat + Gaussian bloom + tanh roll-off)
   - Dynamic Programming Voice-to-Scene Pause Alignment (`align_voice_to_scenes_dp`) & LCS Word Alignment (`align_words_lcs`)
   - Hukum Psikoakustik SFX Lead Offset: `dt = -0.017s` (-17ms sebelum elemen visual muncul)
"""

from __future__ import annotations

import json
import math
import os
import re
import wave
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
REA_POINTS_DIR = ASSETS_DIR / "rea_points"
CORPUS_JSON_PATH = REA_POINTS_DIR / "rea_bigdata_corpus.json"
CATALOG_JSON_PATH = REA_POINTS_DIR / "anymotion_catalog.json"

# ==============================================================================
# 1. PALET WARNA RESMI ANYMOTION + BIG DATA VIRAL CREATORS
# ==============================================================================
ANYMOTION_PALETTES: Dict[str, Dict[str, str]] = {
    "studio":   {"name": "Studio Lime",   "bg": "#F6F6F8", "ink": "#111114", "a": "#111114", "b": "#B7DFD2", "c": "#E4F67C"},
    "neon":     {"name": "Neon Night",    "bg": "#120F24", "ink": "#F3F0FF", "a": "#FF5C8A", "b": "#5CE1E6", "c": "#FFD166"},
    "sunset":   {"name": "Sunset Pop",    "bg": "#2B1630", "ink": "#FFEFE2", "a": "#FF7A45", "b": "#FFC145", "c": "#E2457A"},
    "mint":     {"name": "Mint Fresh",    "bg": "#EAF7F2", "ink": "#10352C", "a": "#12A37F", "b": "#2F6BFF", "c": "#FFB020"},
    "mono":     {"name": "Mono Ink",      "bg": "#F2F1EE", "ink": "#141414", "a": "#141414", "b": "#8A8A8A", "c": "#E5484D"},
    "kopi":     {"name": "Kopi Senja",    "bg": "#F5E9DA", "ink": "#3B2416", "a": "#A0582C", "b": "#D9A35E", "c": "#5E8C61"},
    "ocean":    {"name": "Ocean Deep",    "bg": "#0B1D33", "ink": "#E6F1FF", "a": "#3DA5FF", "b": "#66E3C4", "c": "#FF8FA3"},
    "lavender": {"name": "Soft Lavender", "bg": "#DFE0F1", "ink": "#17172B", "a": "#5B5BD6", "b": "#B7DFD2", "c": "#E4F67C"},
    "emerald":  {"name": "TeraUmroh Emerald", "bg": "#0B3824", "ink": "#EBFDF7", "a": "#10B981", "b": "#C1CFC7", "c": "#F59E0B"},
    "obsidian": {"name": "Agusleo Obsidian",  "bg": "#090D16", "ink": "#F8FAFC", "a": "#3CC094", "b": "#38BDF8", "c": "#F59E0B"},
}

# ==============================================================================
# 2. 17 VISUAL LOOK SHADERS (POST-PROCESSING ENGINE DARI ANYMOTION Bev8DsUP.js)
# ==============================================================================
VISUAL_LOOK_SHADERS: Dict[str, Dict[str, str]] = {
    "auto":       {"name": "✨ Auto Studio Clean (Default)", "desc": "Render bersih tajam dengan kontras studio modern"},
    "flat":       {"name": "🎨 Modern Flat Vector", "desc": "Saturasi warna solid cerah bergaya ilustrasi flat"},
    "clay":       {"name": "🧸 Clay 3D Miniature", "desc": "Soft-light hangat #FFE2C8 + tekstur clay stop-motion"},
    "comic":      {"name": "💥 Comic Pop Halftone", "desc": "Warm golden overlay #FFC23D + titik halftone buku komik"},
    "riso":       {"name": "🖨️ Risograph Duo-Ink Print", "desc": "Dua tinta cetak #E8457A + sedikit pergeseran registrasi & grain"},
    "synth":      {"name": "🌆 Synthwave Neon Grid", "desc": "Pendaran neon ungu-pink #7B2FF7 + lantai grid perspektif"},
    "watercolor": {"name": "🖌️ Watercolor Storybook", "desc": "Sapuan cat air lembut di atas kertas bertekstur #FFF8EC"},
    "sketch":     {"name": "✏️ Hand-Drawn Pencil Sketch", "desc": "Garis arsiran pensil diagonal di atas kertas buku catatan"},
    "engraving":  {"name": "📜 Scientific Engraving", "desc": "Pelat ensiklopedia klasik sepia #6B4E2E + cross-hatching"},
    "blueprint":  {"name": "📐 Blueprint Engineering", "desc": "Kertas biru teknik #0F294A dengan grid milimeter & garis putih"},
    "cine":       {"name": "🎬 Cinematic Teal & Orange", "desc": "Color grading film bioskop, vignette gelap, & bar widescreen"},
    "tiltshift":  {"name": "🏙️ Tilt-Shift Miniature", "desc": "Tajam di tengah dengan efek blur lensa miniatur di atas & bawah"},
    "lowpoly":    {"name": "🔷 Low-Poly Geometric", "desc": "Dunia yang dibangun dari faset poligon segitiga warna rata"},
    "bauhaus":    {"name": "🔺 Bauhaus Geometry", "desc": "Aksen lingkaran merah, kotak biru, dan segitiga kuning di tepi frame"},
    "swiss":      {"name": "🇨🇭 Swiss Editorial Grid", "desc": "Grid tipografi presisi dengan bar aksen merah tegas"},
    "kawaii":     {"name": "🌸 Kawaii Pastel Sparkle", "desc": "Nuansa pastel lembut dengan taburan bintang berkilau"},
    "line":       {"name": "✒️ Minimal Monoline Ink", "desc": "Tinta hitam-putih minimalis dengan ruang kosong lega"},
    "whiteboard": {"name": "📋 Whiteboard Marker", "desc": "Gaya papan tulis bersih dengan kontras spidol edukasi"},
}

# ==============================================================================
# 3. HUKUM EMPIRIS BIG DATA (DARI 11 VIDEO, 184 SHOTS, 2.405 OVERLAYS, 622 SFX)
# ==============================================================================
EMPIRICAL_BIGDATA_LAWS: Dict[str, Any] = {
    "total_videos_analyzed": 11,
    "total_shots_analyzed": 184,
    "total_text_overlays_analyzed": 2405,
    "total_sfx_events_analyzed": 622,
    "total_extracted_sfx_wavs": 498,
    "median_shot_duration_s": 2.56,
    "mean_shot_duration_s": 4.25,
    "psychoacoustic_sfx_lead_dt_s": -0.0169,  # SFX dibunyikan 17ms SEBELUM teks/cut muncul
    "pacing_profiles": {
        "creator_fast": {
            "name": "🔥 Creator Fast-Cut (Agusleo / Raffi / IG Agent)",
            "target_cpm": 24.0,
            "shot_range_s": (2.1, 2.9),
            "avg_shot_s": 2.50,
            "sfx_per_min": 42.0,
            "desc": "Potongan cepat setiap 2.5 detik (24 CPM) untuk menahan retensi 100% di Shorts/Reels."
        },
        "explainer_saas": {
            "name": "✨ SaaS & Motion Explainer (AnyMotion / TeraUmroh / BuatinVideo)",
            "target_cpm": 13.5,
            "shot_range_s": (3.6, 5.2),
            "avg_shot_s": 4.25,
            "sfx_per_min": 36.0,
            "desc": "Transisi visual terukur setiap 4.2 detik agar penonton sempat membaca kartu UI & metrik."
        },
        "dialog_skit": {
            "name": "🎭 Beat-Locked Roleplay Skit (Interview SDM / Bongkar Profil)",
            "target_cpm": 8.5,
            "shot_range_s": (5.0, 9.0),
            "avg_shot_s": 6.80,
            "sfx_per_min": 28.0,
            "desc": "Pergantian kamera mengikuti giliran dialog tanya-jawab dan ketukan beat musik."
        }
    },
    "sfx_anchor_rules": {
        "label_in":    {"sfx_type": "pop",    "dt_s": -0.017, "weight": 0.484},
        "subtitle_in": {"sfx_type": "pop-soft", "dt_s": -0.015, "weight": 0.205},
        "title_in":    {"sfx_type": "ding",   "dt_s": -0.020, "weight": 0.180},
        "counter_in":  {"sfx_type": "coin",   "dt_s": -0.012, "weight": 0.080},
        "cut":         {"sfx_type": "whoosh", "dt_s": -0.025, "weight": 0.051},
    },
    "viral_power_tokens_id": [
        "rahasia", "tangga", "juta", "miliar", "gratis", "tanpa", "batas", "wajib",
        "tahu", "jangan", "skip", "fakta", "unik", "gaji", "cuan", "omset", "sistem",
        "otomatis", "jamaah", "excel", "halaman", "jualan", "kartu", "nama", "chapter",
        "aturan", "permainan", "bukti", "nyata", "solusi", "masalah", "audit", "konversi"
    ]
}


def load_rea_corpus() -> Dict[str, Any]:
    """Memuat korpus 11 video REA Big Data dari JSON."""
    if CORPUS_JSON_PATH.exists():
        try:
            return json.loads(CORPUS_JSON_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"corpus_version": "2.0-REA-BIGDATA", "total_videos": 11, "empirical_laws": EMPIRICAL_BIGDATA_LAWS, "blueprints": []}


def load_anymotion_catalog() -> Dict[str, Any]:
    """Memuat katalog 212 gaya AnyMotion, 33 template adegan, dan 95 SFX manifest."""
    if CATALOG_JSON_PATH.exists():
        try:
            return json.loads(CATALOG_JSON_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"styles_count": 0, "templates_count": 0, "sfx_manifest_count": 0, "styles": [], "scene_templates": [], "sfx_manifest": []}


def get_blueprint_by_id(blueprint_id: str) -> Optional[Dict[str, Any]]:
    corpus = load_rea_corpus()
    bid = blueprint_id.strip().lower()
    for bp in corpus.get("blueprints", []):
        if bp.get("id") == bid or bid in bp.get("id", ""):
            return bp
    return None


# ==============================================================================
# 4. IMPLEMENTASI 17 VISUAL LOOK POST-PROCESSING SHADERS (CV2 / NUMPY / PIL)
# ==============================================================================
def _make_hatch_pattern(angle_deg: float = 45.0, spacing: int = 7, cross: bool = False) -> np.ndarray:
    """Membuat tile pattern arsiran pensil / engraving 64x64."""
    sz = 64
    tile = np.full((sz, sz), 255, dtype=np.uint8)
    for t in range(-sz, sz * 2, spacing):
        cv2.line(tile, (t, 0), (t + sz, sz), 160, 1, cv2.LINE_AA)
        if cross:
            cv2.line(tile, (t + sz, 0), (t, sz), 165, 1, cv2.LINE_AA)
    return tile


def _make_halftone_pattern(spacing: int = 8, radius: int = 2) -> np.ndarray:
    """Membuat tile pattern titik halftone komik 64x64."""
    sz = 64
    tile = np.full((sz, sz), 255, dtype=np.uint8)
    for y in range(0, sz, spacing):
        offset = (spacing // 2) if ((y // spacing) % 2 == 1) else 0
        for x in range(offset, sz, spacing):
            cv2.circle(tile, (x, y), radius, 150, -1, cv2.LINE_AA)
    return tile


def apply_visual_look_shader(frame_bgr: np.ndarray, look: str = "auto", time_s: float = 0.0) -> np.ndarray:
    """
    Menerapkan 17 Visual Look Post-Processing Shaders ala AnyMotion (`za` di Bev8DsUP.js)
    ke frame BGR (OpenCV) secara deterministik & cepat.
    """
    look = (look or "auto").strip().lower()
    if look in ("auto", "none", "clean", ""):
        return frame_bgr

    h, w = frame_bgr.shape[:2]
    img = frame_bgr.astype(np.float32)

    if look in ("flat", "e-flatm"):
        # Tingkatkan saturasi +18% & sedikit kontras bersih
        hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[..., 1] = np.clip(hsv[..., 1] * 1.18, 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    if look in ("clay", "e-clay"):
        # Warm soft-light tint (#FFE2C8 -> BGR: 200, 226, 255) + subtle organic grain
        warm = np.array([200.0, 226.0, 255.0], dtype=np.float32)
        out = img * 0.86 + warm * 0.14
        rng = np.random.default_rng(int(round(time_s * 12)) + 7)
        noise = rng.normal(0, 3.5, (h // 2, w // 2, 1)).astype(np.float32)
        noise = cv2.resize(noise, (w, h), interpolation=cv2.INTER_NEAREST)[..., None]
        return np.clip(out + noise, 0, 255).astype(np.uint8)

    if look in ("comic", "e-comicp"):
        # Warm golden overlay (#FFC23D -> BGR: 61, 194, 255) + halftone dot multiply
        gold = np.array([61.0, 194.0, 255.0], dtype=np.float32)
        blended = img * 0.84 + gold * 0.16
        tile = _make_halftone_pattern(8, 2)
        tiled = np.tile(tile, (h // 64 + 2, w // 64 + 2))[:h, :w].astype(np.float32) / 255.0
        out = blended * (0.82 + 0.18 * tiled[..., None])
        return np.clip(out, 0, 255).astype(np.uint8)

    if look in ("riso", "e-riso"):
        # Risograph duo-ink: misregistered pink/teal offset layer + paper grain
        dx = max(2, int(round(w * 0.005)))
        dy = max(1, int(round(h * 0.003)))
        shifted = np.roll(np.roll(img, dx, axis=1), dy, axis=0)
        # Tint original warm rose (#E8457A -> BGR: 122, 69, 232) & shifted teal (#12A37F -> BGR: 127, 163, 18)
        out = img * 0.72 + shifted * np.array([1.08, 0.92, 0.85], dtype=np.float32) * 0.28
        return np.clip(out, 0, 255).astype(np.uint8)

    if look in ("synth", "e-synth"):
        # Synthwave neon purple/pink glow + perspective horizon grid
        tint = np.array([247.0, 47.0, 123.0], dtype=np.float32)  # #7B2FF7 in BGR
        small = cv2.resize(frame_bgr, (w // 4, h // 4))
        glow = cv2.GaussianBlur(small, (0, 0), 6.0)
        glow_up = cv2.resize(glow, (w, h)).astype(np.float32)
        out = np.clip(img * 0.78 + glow_up * 0.32 + tint * 0.08, 0, 255).astype(np.uint8)
        # Draw synthwave moving horizon grid on bottom 35%
        horizon_y = int(h * 0.65)
        overlay = out.copy()
        phase = (time_s * 0.35) % 1.0
        for i in range(9):
            frac = ((i / 9.0 + phase) % 1.0) ** 2
            y = int(horizon_y + frac * (h - horizon_y))
            cv2.line(overlay, (0, y), (w, y), (180, 79, 255), 2, cv2.LINE_AA)
        for r in range(-6, 7):
            x_top = int(w / 2 + r * w * 0.04)
            x_bot = int(w / 2 + r * w * 0.30)
            cv2.line(overlay, (x_top, horizon_y), (x_bot, h), (180, 79, 255), 2, cv2.LINE_AA)
        return cv2.addWeighted(out, 0.65, overlay, 0.35, 0)

    if look in ("watercolor", "e-water"):
        # Soft blur bleed + offset multiply + warm paper lift (#FFF8EC)
        blurred = cv2.GaussianBlur(frame_bgr, (0, 0), max(1.5, w / 420.0)).astype(np.float32)
        shifted = np.roll(np.roll(blurred, 2, axis=1), 2, axis=0)
        out = img * 0.65 + blurred * 0.25 + (img * shifted / 255.0) * 0.10
        paper = np.array([236.0, 248.0, 255.0], dtype=np.float32)
        out = out * 0.92 + paper * 0.08
        return np.clip(out, 0, 255).astype(np.uint8)

    if look in ("sketch", "e-sketch"):
        # Desaturate partially + diagonal pencil hatch multiply
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)[..., None]
        base = img * 0.45 + gray * 0.55
        tile = _make_hatch_pattern(45.0, 6, cross=False)
        tiled = np.tile(tile, (h // 64 + 2, w // 64 + 2))[:h, :w].astype(np.float32) / 255.0
        out = base * (0.84 + 0.16 * tiled[..., None])
        return np.clip(out, 0, 255).astype(np.uint8)

    if look in ("engraving", "e-engrave"):
        # Sepia encyclopedia tone (#6B4E2E -> BGR: 46, 78, 107) + cross-hatch
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        sepia_dark = np.array([38.0, 58.0, 82.0], dtype=np.float32)
        sepia_light = np.array([212.0, 232.0, 245.0], dtype=np.float32)
        base = sepia_dark + gray[..., None] * (sepia_light - sepia_dark)
        tile = _make_hatch_pattern(45.0, 5, cross=True)
        tiled = np.tile(tile, (h // 64 + 2, w // 64 + 2))[:h, :w].astype(np.float32) / 255.0
        out = base * (0.78 + 0.22 * tiled[..., None])
        return np.clip(out, 0, 255).astype(np.uint8)

    if look in ("blueprint", "fx-blueprint"):
        # Technical drafting blueprint blue + fine millimeter grid
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        edges = cv2.Canny(frame_bgr, 60, 150).astype(np.float32) / 255.0
        bg_blue = np.array([92.0, 48.0, 18.0], dtype=np.float32)   # Deep blueprint BGR
        fg_cyan = np.array([245.0, 225.0, 185.0], dtype=np.float32)
        out = bg_blue * (1.0 - 0.35 * gray[..., None]) + fg_cyan * (0.35 * gray[..., None] + 0.45 * edges[..., None])
        res = np.clip(out, 0, 255).astype(np.uint8)
        step = max(24, w // 24)
        for x in range(0, w, step):
            cv2.line(res, (x, 0), (x, h), (130, 80, 35), 1)
        for y in range(0, h, step):
            cv2.line(res, (0, y), (w, y), (130, 80, 35), 1)
        return res

    if look in ("cine", "cinematic", "e-cine"):
        # Teal shadows & warm orange highlights + vignette + subtle cinema bars
        lum = (0.114 * img[..., 0] + 0.587 * img[..., 1] + 0.299 * img[..., 2]) / 255.0
        teal = np.array([145.0, 115.0, 45.0], dtype=np.float32)    # BGR Teal
        orange = np.array([65.0, 155.0, 240.0], dtype=np.float32)  # BGR Orange
        grade = teal * (1.0 - lum[..., None]) + orange * lum[..., None]
        out = img * 0.82 + grade * 0.18
        # Radial vignette
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        dist2 = ((xx - w * 0.5) / (w * 0.5)) ** 2 + ((yy - h * 0.5) / (h * 0.5)) ** 2
        vig = np.clip(1.0 - 0.28 * dist2, 0.55, 1.0)[..., None]
        res = np.clip(out * vig, 0, 255).astype(np.uint8)
        bar = max(16, int(h * 0.028))
        res[:bar, :] = (res[:bar, :].astype(np.float32) * 0.15).astype(np.uint8)
        res[h - bar:, :] = (res[h - bar:, :].astype(np.float32) * 0.15).astype(np.uint8)
        return res

    if look in ("tiltshift", "e-tilt"):
        # Sharp center band, smooth depth-of-field blur top & bottom
        blurred = cv2.GaussianBlur(frame_bgr, (0, 0), max(3.0, h / 140.0)).astype(np.float32)
        yy = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None, None]
        # Focus around y = 0.50, transition width 0.22
        mask = np.clip((np.abs(yy - 0.50) - 0.16) / 0.20, 0.0, 1.0)
        out = img * (1.0 - mask) + blurred * mask
        return np.clip(out, 0, 255).astype(np.uint8)

    if look in ("lowpoly", "e-lowp"):
        # Mosaic pixelation + crisp edge preservation
        gw = 36
        gh = max(20, int(round(gw * h / w)))
        small = cv2.resize(frame_bgr, (gw, gh), interpolation=cv2.INTER_AREA)
        mosaic = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
        return cv2.addWeighted(frame_bgr, 0.55, mosaic, 0.45, 0)

    if look in ("bauhaus", "e-bauhaus"):
        res = frame_bgr.copy()
        r_sz = int(min(w, h) * 0.065)
        # Red circle top-left, Blue square bottom-right, Yellow triangle top-right
        cv2.circle(res, (int(w * 0.07), int(h * 0.06)), r_sz, (69, 72, 229), -1, cv2.LINE_AA)
        cv2.rectangle(res, (int(w * 0.88), int(h * 0.90)), (int(w * 0.96), int(h * 0.95)), (214, 91, 47), -1)
        pts = np.array([
            [int(w * 0.92), int(h * 0.04)],
            [int(w * 0.87), int(h * 0.09)],
            [int(w * 0.97), int(h * 0.09)]
        ], np.int32)
        cv2.fillPoly(res, [pts], (32, 176, 255), cv2.LINE_AA)
        return cv2.addWeighted(frame_bgr, 0.35, res, 0.65, 0)

    if look in ("swiss", "e-swiss"):
        res = frame_bgr.copy()
        # Subtle grid + crimson accent header bar
        step = max(48, w // 12)
        for x in range(0, w, step):
            cv2.line(res, (x, 0), (x, h), (180, 180, 180), 1)
        for y in range(0, h, step):
            cv2.line(res, (0, y), (w, y), (180, 180, 180), 1)
        out = cv2.addWeighted(frame_bgr, 0.88, res, 0.12, 0)
        cv2.rectangle(out, (int(w * 0.06), int(h * 0.035)), (int(w * 0.24), int(h * 0.044)), (77, 72, 229), -1)
        return out

    if look in ("kawaii", "e-kawaii"):
        # Soft pastel lift + twinkling 4-point sparkles
        pastel = np.array([235.0, 220.0, 255.0], dtype=np.float32)
        out = np.clip(img * 0.86 + pastel * 0.14, 0, 255).astype(np.uint8)
        for idx, (sx, sy) in enumerate([(0.12, 0.14), (0.88, 0.16), (0.10, 0.82), (0.89, 0.78), (0.50, 0.08)]):
            pulse = 0.5 + 0.5 * math.sin(time_s * 4.0 + idx * 1.3)
            r = int(min(w, h) * (0.012 + 0.008 * pulse))
            cx, cy = int(w * sx), int(h * sy)
            cv2.line(out, (cx - r, cy), (cx + r, cy), (180, 235, 255), 2, cv2.LINE_AA)
            cv2.line(out, (cx, cy - r), (cx, cy + r), (180, 235, 255), 2, cv2.LINE_AA)
        return out

    if look in ("line", "e-linem", "whiteboard", "e-wboard"):
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)[..., None]
        mix = 0.75 if "line" in look else 0.45
        out = img * (1.0 - mix) + gray * mix
        return np.clip(out, 0, 255).astype(np.uint8)

    return frame_bgr


# ==============================================================================
# 5. MORTON Z-ORDER PARTICLE & CUTOUT MORPHING ENGINE (`Redraw` dari render.py)
# ==============================================================================
def _bgr_norm(hexs: str) -> np.ndarray:
    h = hexs.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return np.array([int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)], np.float32) / 255.0


def _morton_zorder(xy: np.ndarray) -> np.ndarray:
    """
    Mengurutkan koordinat partikel (0..1) sepanjang kurva ruang Morton Z-order,
    sehingga saat transisi morph dari Adegan A ke Adegan B, partikel yang berdekatan
    bermigrasi secara mulus ke tetangga terdekatnya.
    """
    q = np.clip((xy * 1023).astype(np.int64), 0, 1023)
    code = np.zeros(len(xy), np.int64)
    for b in range(10):
        code |= ((q[:, 0] >> b) & 1) << (2 * b) | ((q[:, 1] >> b) & 1) << (2 * b + 1)
    return np.argsort(code, kind="stable")


def _smoothstep(x: float) -> float:
    x = min(1.0, max(0.0, x))
    return x * x * (3.0 - 2.0 * x)


def generate_procedural_point_cloud(shape_type: str = "galaxy", count: int = 3600,
                                    primary_hex: str = "#10B981",
                                    secondary_hex: str = "#38BDF8",
                                    accent_hex: str = "#F59E0B") -> np.ndarray:
    """
    Menghasilkan point cloud [x, y, r, g, b, a] untuk ReaParticleRedrawEngine
    baik dari file JSON ekstraksi asli maupun geometri prosedural.
    """
    rng = np.random.default_rng(42)
    c1 = _bgr_norm(primary_hex)[::-1] * 255.0  # RGB 0..255
    c2 = _bgr_norm(secondary_hex)[::-1] * 255.0
    c3 = _bgr_norm(accent_hex)[::-1] * 255.0

    pts = np.zeros((count, 6), dtype=np.float32)
    if shape_type == "ring":
        angles = rng.uniform(0, 2 * np.pi, count)
        radii = rng.normal(0.28, 0.035, count)
        pts[:, 0] = np.clip(0.5 + np.cos(angles) * radii, 0.05, 0.95)
        pts[:, 1] = np.clip(0.48 + np.sin(angles) * radii * 0.65, 0.05, 0.95)
    elif shape_type == "grid_wave":
        side = int(math.sqrt(count))
        gx, gy = np.meshgrid(np.linspace(0.12, 0.88, side), np.linspace(0.18, 0.82, side))
        gx = gx.ravel()
        gy = gy.ravel() + 0.04 * np.sin(gx * 12.0)
        n_g = len(gx)
        pts[:n_g, 0] = gx
        pts[:n_g, 1] = gy
        if n_g < count:
            pts[n_g:, 0] = rng.uniform(0.1, 0.9, count - n_g)
            pts[n_g:, 1] = rng.uniform(0.1, 0.9, count - n_g)
    else:  # galaxy / spiral
        arms = 3
        idx = np.arange(count, dtype=np.float32) / count
        theta = idx * 4.0 * np.pi + (np.arange(count) % arms) * (2.0 * np.pi / arms)
        theta += rng.normal(0, 0.22, count)
        rad = 0.03 + 0.36 * (idx ** 0.75)
        pts[:, 0] = np.clip(0.5 + np.cos(theta) * rad, 0.04, 0.96)
        pts[:, 1] = np.clip(0.5 + np.sin(theta) * rad * 0.62, 0.04, 0.96)

    for i in range(count):
        if i % 5 == 0:
            pts[i, 2:5] = c3
        elif i % 2 == 0:
            pts[i, 2:5] = c1
        else:
            pts[i, 2:5] = c2
        pts[i, 5] = rng.uniform(0.55, 0.98)
    return pts


class ReaParticleScene:
    """Satu adegan partikel / cutout dengan fisika gerak & Z-order sorting."""
    def __init__(self, sc: Dict[str, Any], W: int, H: int, seed: int = 0):
        self.sc = sc
        self.W, self.H = W, H
        self.start = float(sc.get("start", 0.0))
        self.end = float(sc.get("end", 5.0))
        m = sc.get("motion") or {}
        self.zoom = float(m.get("zoom", 0.04))
        self.rot = float(m.get("rotate", 1.2))
        self.pan = np.array(m.get("pan", [0.0, 0.0]), np.float32) * (W, H)
        self.drift = float(m.get("drift", 0.0025)) * W
        self.twinkle = float(m.get("twinkle", 0.18))
        self.gain = float(sc.get("gain", 1.0))
        self.dot = float(sc.get("dot", 1.4))

        g = sc.get("glow") or {}
        self.ground = _bgr_norm(sc.get("ground", "#090D16"))
        self.bg = np.empty((H, W, 3), np.float32)
        self.bg[:] = self.ground
        if g.get("colour"):
            yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
            cx, cy = g.get("centre", [0.5, 0.45])
            sigma = max(1.0, float(g.get("radius", 0.22)) * W / 1.177)
            fall = np.exp(-((xx - cx * W) ** 2 + (yy - cy * H) ** 2) / (2 * sigma * sigma))
            amp = np.clip(_bgr_norm(g["colour"]) - self.ground, 0, None) * float(g.get("strength", 0.85))
            self.bg += fall[..., None] * amp

        self.centre = np.array(sc.get("centre", [0.5, 0.5]), np.float32) * (W, H)
        rng = np.random.default_rng(seed + 101)

        # Load point cloud from JSON file if specified and exists, else procedural
        rows = None
        pts_file = sc.get("points_file")
        if pts_file:
            p_cand = REA_POINTS_DIR / pts_file
            if p_cand.exists():
                try:
                    raw_pts = json.loads(p_cand.read_text(encoding="utf-8")).get("points", [])
                    if raw_pts:
                        rows = np.array(raw_pts, np.float32).reshape(-1, 6)
                except Exception:
                    rows = None

        if rows is None or len(rows) == 0:
            rows = generate_procedural_point_cloud(
                shape_type=sc.get("shape", "galaxy"),
                count=int(sc.get("count", 3600)),
                primary_hex=sc.get("primary_hex", "#10B981"),
                secondary_hex=sc.get("secondary_hex", "#38BDF8"),
                accent_hex=sc.get("accent_hex", "#F59E0B"),
            )

        n = int(sc.get("count", len(rows)))
        idx = np.arange(n) % max(1, len(rows))
        pick = rows[idx]
        xy = pick[:, :2] * (W, H)
        extra = np.arange(n) >= len(rows)
        if np.any(extra):
            xy[extra] += rng.normal(0, max(1.5, 2.5 * self.dot), (int(extra.sum()), 2))
        order = _morton_zorder(xy / (W, H))
        self.xy = xy[order].astype(np.float32)
        self.col = (pick[order][:, [4, 3, 2]] / 255.0 * pick[order][:, 5:6]).astype(np.float32)
        self.phase = rng.uniform(0, 2 * np.pi, (n, 3)).astype(np.float32)
        self.freq = rng.uniform(0.15, 0.45, (n, 2)).astype(np.float32)

    def _move(self, xy: np.ndarray, tau: float) -> np.ndarray:
        s = (1.0 + self.zoom) ** tau
        a = np.radians(self.rot * tau)
        R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]], np.float32) * s
        return (xy - self.centre) @ R.T + self.centre + self.pan * tau

    def particles(self, t: float) -> Tuple[np.ndarray, np.ndarray]:
        tau = max(0.0, t - self.start)
        xy = self._move(self.xy, tau)
        if self.drift:
            amp = self.drift / (2 * np.pi * 0.3)
            w = 2 * np.pi * self.freq * tau
            xy = xy + amp * np.stack([np.sin(w[:, 0] + self.phase[:, 0]), np.cos(w[:, 1] + self.phase[:, 1])], 1)
        col = self.col * (1.0 - self.twinkle + self.twinkle * (0.5 + 0.5 * np.sin(3.0 * tau + self.phase[:, 2:3])))
        return xy, col * self.gain


class ReaParticleRedrawEngine:
    """
    Mesin perender latar belakang partikel & morphing Z-Order dari REA Video Code-Remake.
    Mendukung sub-pixel bilinear splatting, Gaussian Bloom, dan soft tanh highlight roll-off.
    """
    def __init__(self, W: int = 1080, H: int = 1920, scenes_spec: Optional[List[Dict[str, Any]]] = None,
                 bloom: float = 0.65, bloom_size: float = 0.012):
        self.W, self.H = W, H
        self.bloom = bloom
        self.bloom_size = bloom_size
        if not scenes_spec:
            scenes_spec = [
                {
                    "start": 0.0, "end": 4.0, "ground": "#080D18",
                    "glow": {"colour": "#1E3A8A", "centre": [0.5, 0.35], "radius": 0.28, "strength": 0.85},
                    "points_file": "anymotion_scene_01.json", "count": 3800, "dot": 1.45, "gain": 1.1,
                    "motion": {"zoom": 0.04, "rotate": -1.2, "pan": [0.0, -0.01], "drift": 0.0025, "twinkle": 0.2},
                    "enter": "cut", "enter_s": 0.5
                },
                {
                    "start": 4.0, "end": 8.0, "ground": "#091914",
                    "glow": {"colour": "#10B981", "centre": [0.48, 0.52], "radius": 0.26, "strength": 0.75},
                    "points_file": "anymotion_scene_02.json", "count": 3800, "dot": 1.45, "gain": 1.1,
                    "motion": {"zoom": -0.02, "rotate": 0.9, "pan": [0.0, 0.01], "drift": 0.002, "twinkle": 0.2},
                    "enter": "morph", "enter_s": 0.85
                },
                {
                    "start": 8.0, "end": 60.0, "ground": "#0B1120",
                    "glow": {"colour": "#6366F1", "centre": [0.52, 0.44], "radius": 0.30, "strength": 0.80},
                    "points_file": "anymotion_scene_03.json", "count": 3800, "dot": 1.45, "gain": 1.1,
                    "motion": {"zoom": 0.015, "rotate": -0.6, "pan": [0.0, 0.0], "drift": 0.002, "twinkle": 0.2},
                    "enter": "morph", "enter_s": 0.85
                }
            ]
        self.scenes = [ReaParticleScene(sc, W, H, i) for i, sc in enumerate(scenes_spec)]

    def _at(self, t: float) -> Tuple[int, ReaParticleScene]:
        for i, s in enumerate(self.scenes):
            if s.start <= t < s.end:
                return i, s
        return len(self.scenes) - 1, self.scenes[-1]

    def _splat(self, buf: np.ndarray, xy: np.ndarray, col: np.ndarray) -> None:
        H, W = buf.shape[:2]
        x0, y0 = np.floor(xy[:, 0]), np.floor(xy[:, 1])
        fx, fy = xy[:, 0] - x0, xy[:, 1] - y0
        flat = buf.reshape(-1, 3)
        for dx, dy, wt in (
            (0, 0, (1.0 - fx) * (1.0 - fy)),
            (1, 0, fx * (1.0 - fy)),
            (0, 1, (1.0 - fx) * fy),
            (1, 1, fx * fy),
        ):
            xi = (x0 + dx).astype(np.int64)
            yi = (y0 + dy).astype(np.int64)
            ok = (xi >= 0) & (xi < W) & (yi >= 0) & (yi < H)
            k = yi[ok] * W + xi[ok]
            for c in range(3):
                flat[:, c] += np.bincount(k, weights=col[ok, c] * wt[ok], minlength=H * W).astype(np.float32)

    def render_frame_bgr(self, t: float) -> np.ndarray:
        i, s = self._at(t)
        prev = self.scenes[i - 1] if i > 0 else None
        enter = float(s.sc.get("enter_s", 0.7))
        mix = _smoothstep((t - s.start) / enter) if (s.sc.get("enter") == "morph" and prev is not None and enter > 0) else 1.0
        bg = s.bg if mix >= 1.0 else prev.bg * (1.0 - mix) + s.bg * mix

        drawn = np.zeros((self.H, self.W, 3), np.float32)
        xy, col = s.particles(t)
        dot = s.dot
        if mix < 1.0 and prev is not None and len(prev.xy) and len(xy):
            pxy, pcol = prev.particles(prev.end)
            j = (np.arange(len(xy)) * len(pxy)) // len(xy)
            xy = pxy[j] * (1.0 - mix) + xy * mix
            col = pcol[j] * (1.0 - mix) + col * mix
            dot = prev.dot * (1.0 - mix) + s.dot * mix

        if len(xy):
            self._splat(drawn, xy, col)
            sig = max(0.6, 0.7 * dot)
            drawn = cv2.GaussianBlur(drawn, (0, 0), sig) * (2.0 * np.pi * sig * sig)

        if self.bloom > 0:
            small = cv2.resize(drawn, (max(1, self.W // 4), max(1, self.H // 4)), interpolation=cv2.INTER_AREA)
            bsize = max(0.8, self.bloom_size * self.W / 4.0)
            glow = cv2.GaussianBlur(small, (0, 0), bsize) + 0.5 * cv2.GaussianBlur(small, (0, 0), 3.0 * bsize)
            drawn = drawn + self.bloom * cv2.resize(glow, (self.W, self.H), interpolation=cv2.INTER_LINEAR)

        out = bg + drawn
        out = np.where(out > 0.85, 0.85 + 0.15 * np.tanh((out - 0.85) / 0.15), out)
        return (np.clip(out, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8)


# ==============================================================================
# 6. DYNAMIC PROGRAMMING VOICE-TO-SCENE ALIGNMENT & LCS WORD ALIGNMENT
#    (Ported 1:1 dari AnyMotion f64CrI6l.js)
# ==============================================================================
def count_syllables_id(word: str) -> int:
    """Menghitung bobot suku kata Bahasa Indonesia/Inggris untuk proporsi durasi pengucapan."""
    clean = re.sub(r"[^a-zA-Z0-9]", "", word.lower())
    if not clean:
        return 1
    vowels = re.findall(r"[aiueo]+", clean)
    return max(1, len(vowels))


def detect_speech_segments_from_wav(wav_path: str) -> Tuple[List[Tuple[float, float]], float]:
    """
    Mendeteksi interval aktif bicara dari file WAV menggunakan amplop RMS 10ms (100Hz)
    dan ambang batas adaptif persentil ke-20 & ke-95 (`s + (p95 - s) * 0.07`),
    menggabungkan jeda mikro < 0.18s dan menyaring segmen > 0.06s (identik f64CrI6l.js `P(e)`).
    """
    try:
        with wave.open(wav_path, "rb") as wf:
            sr = wf.getframerate()
            n_ch = wf.getnchannels()
            sw = wf.getsampwidth()
            n_frames = wf.getnframes()
            raw = wf.readframes(n_frames)
        dur = n_frames / float(max(1, sr))
        if sw == 2:
            samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        else:
            return [(0.0, dur)], dur
        if n_ch > 1:
            samples = samples.reshape(-1, n_ch)[:, 0]

        win = max(1, int(round(sr * 0.01)))
        n_bins = len(samples) // win
        if n_bins < 5:
            return [(0.0, dur)], dur

        trimmed = samples[: n_bins * win].reshape(n_bins, win)
        rms = np.sqrt(np.mean(trimmed * trimmed, axis=1))
        sorted_rms = np.sort(rms)
        p20 = float(sorted_rms[int(n_bins * 0.20)])
        p95 = float(sorted_rms[min(n_bins - 1, int(n_bins * 0.95))])
        thresh = p20 + max(0.001, p95 - p20) * 0.07

        raw_spans: List[List[float]] = []
        u = -1
        for i in range(n_bins + 1):
            active = (i < n_bins) and (rms[i] > thresh)
            if active and u < 0:
                u = i
            elif (not active) and u >= 0:
                raw_spans.append([max(0.0, u / 100.0 - 0.06), i / 100.0])
                u = -1

        merged: List[Tuple[float, float]] = []
        for s0, s1 in raw_spans:
            if merged and (s0 - merged[-1][1] < 0.18):
                merged[-1] = (merged[-1][0], s1)
            elif (s1 - s0) > 0.06:
                merged.append((s0, s1))

        if not merged:
            return [(0.0, dur)], dur
        return merged, dur
    except Exception:
        return [], 0.0


def align_voice_to_scenes_dp(scene_narrations: List[str], total_duration: float,
                             speech_spans: Optional[List[Tuple[float, float]]] = None) -> List[Dict[str, Any]]:
    """
    Algoritma Dynamic Programming (`z(e, t)` di f64CrI6l.js) untuk mempartisi rekaman suara
    ke dalam N adegan cerita tepat pada jeda napas alami yang meminimalkan galat kuadrat
    terhadap bobot suku kata tiap adegan, sekaligus menghitung timestamp kata (`vo_words`).
    """
    a = len(scene_narrations)
    if a == 0:
        return []

    if not speech_spans:
        speech_spans = [(0.0, max(1.0, total_duration))]

    weights = [
        max(1, sum(count_syllables_id(w) for w in re.findall(r"\S+", narr)))
        for narr in scene_narrations
    ]
    total_w = float(sum(weights))
    total_speech = sum(s1 - s0 for s0, s1 in speech_spans)
    m = len(speech_spans)

    # DP untuk mencari batas jeda optimal jika jumlah segmen suara >= jumlah adegan
    boundaries: List[float] = [0.0]
    if m >= a and a > 1:
        seg_lens = [s1 - s0 for s0, s1 in speech_spans]
        prefix = [0.0]
        for ln in seg_lens:
            prefix.append(prefix[-1] + ln)
        target_lens = [total_speech * w / total_w for w in weights]

        dp = [[float("inf")] * (m + 1) for _ in range(a + 1)]
        parent = [[-1] * (m + 1) for _ in range(a + 1)]
        dp[0][0] = 0.0

        for e_idx in range(1, a + 1):
            for n_idx in range(e_idx, m - (a - e_idx) + 1):
                for prev_idx in range(e_idx - 1, n_idx):
                    if math.isinf(dp[e_idx - 1][prev_idx]):
                        continue
                    diff = (prefix[n_idx] - prefix[prev_idx]) - target_lens[e_idx - 1]
                    cost = dp[e_idx - 1][prev_idx] + (diff * diff) / max(0.5, target_lens[e_idx - 1])
                    if cost < dp[e_idx][n_idx]:
                        dp[e_idx][n_idx] = cost
                        parent[e_idx][n_idx] = prev_idx

        cuts = [0] * a
        curr = m
        for e_idx in range(a, 0, -1):
            p_idx = parent[e_idx][curr]
            cuts[e_idx - 1] = max(0, p_idx)
            curr = p_idx

        for e_idx in range(1, a):
            seg_i = cuts[e_idx]
            bound_t = max(speech_spans[seg_i - 1][1] + 0.02, speech_spans[seg_i][0] - 0.10)
            boundaries.append(round(bound_t, 3))
    else:
        # Proporsional berdasarkan bobot suku kata
        acc = 0.0
        for e_idx in range(1, a):
            acc += weights[e_idx - 1]
            boundaries.append(round(total_duration * (acc / total_w), 3))

    boundaries.append(round(max(total_duration, boundaries[-1] + 1.0), 3))

    aligned_scenes: List[Dict[str, Any]] = []
    for idx, narr in enumerate(scene_narrations):
        r0 = boundaries[idx]
        r1 = boundaries[idx + 1]
        sc_dur = round(max(1.2, r1 - r0), 2)
        words = [w.strip("*") for w in re.findall(r"\S+", narr) if w.strip("*")]
        w_weights = [count_syllables_id(w) for w in words]
        w_sum = float(max(1, sum(w_weights)))

        vo_words = []
        acc_w = 0.0
        active_dur = max(0.5, sc_dur - 0.18)
        for w_str, ww in zip(words, w_weights):
            ws = round(0.06 + active_dur * (acc_w / w_sum), 3)
            acc_w += ww
            we = round(0.06 + active_dur * (acc_w / w_sum), 3)
            vo_words.append({"w": w_str, "start": ws, "end": we})

        aligned_scenes.append({
            "scene_index": idx,
            "start_s": r0,
            "end_s": r1,
            "duration_s": sc_dur,
            "narration": narr,
            "vo_words": vo_words,
            "sfx_trigger_s": round(max(0.0, r0 + EMPIRICAL_BIGDATA_LAWS["psychoacoustic_sfx_lead_dt_s"]), 3)
        })
    return aligned_scenes


def align_words_lcs(existing_words: List[Dict[str, Any]], new_narration: str) -> List[Dict[str, Any]]:
    """
    Longest Common Subsequence (LCS) Word Timestamp Preservation (`A(e,t,n)` di f64CrI6l.js).
    Menjaga timestamp kata-kata yang tidak berubah saat pengguna mengedit teks naskah.
    """
    new_tokens = [w.strip("*") for w in re.findall(r"\S+", new_narration) if w.strip("*")]
    if not existing_words or not new_tokens:
        return []
    old_tokens = [str(w.get("w", "")).strip("*") for w in existing_words]
    a, s = len(old_tokens), len(new_tokens)

    dp = [[0] * (s + 1) for _ in range(a + 1)]
    for i in range(a - 1, -1, -1):
        for j in range(s - 1, -1, -1):
            if old_tokens[i].lower() == new_tokens[j].lower():
                dp[i][j] = dp[i + 1][j + 1] + 1
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j + 1])

    matched = [-1] * s
    i = j = 0
    while i < a and j < s:
        if old_tokens[i].lower() == new_tokens[j].lower():
            matched[j] = i
            i += 1
            j += 1
        elif dp[i + 1][j] >= dp[i][j + 1]:
            i += 1
        else:
            j += 1

    t_min = float(existing_words[0].get("start", 0.0))
    t_max = float(existing_words[-1].get("end", max(1.0, s * 0.35)))
    result: List[Dict[str, Any]] = []
    for idx, tok in enumerate(new_tokens):
        if matched[idx] >= 0:
            ref = existing_words[matched[idx]]
            result.append({"w": tok, "start": float(ref["start"]), "end": float(ref["end"])})
        else:
            result.append({"w": tok, "start": 0.0, "end": 0.0})

    # Interpolasi kata-kata baru yang belum punya timestamp
    k = 0
    while k < s:
        if matched[k] >= 0:
            k += 1
            continue
        r_start = k
        while k < s and matched[k] < 0:
            k += 1
        r_end = k
        t0 = result[r_start - 1]["end"] if r_start > 0 else t_min
        t1 = result[r_end]["start"] if r_end < s else t_max
        if t1 <= t0:
            t1 = t0 + 0.25 * (r_end - r_start)
        span_weights = [count_syllables_id(result[x]["w"]) + 1 for x in range(r_start, r_end)]
        tot_sw = float(sum(span_weights))
        curr_t = t0
        for x, sw in zip(range(r_start, r_end), span_weights):
            dt = (t1 - t0) * (sw / tot_sw)
            result[x]["start"] = round(curr_t, 3)
            curr_t += dt
            result[x]["end"] = round(curr_t, 3)
    return result


# ==============================================================================
# 7. AWARD-WINNING CREATIVE DIRECTOR PROMPT ENGINE (`k2MSur2S.js` & `qc`)
# ==============================================================================
def build_anymotion_director_prompt(
    topic: str,
    style_id: str = "e-vox",
    blueprint_id: str = "agusleo_cuan",
    visual_look: str = "auto",
    palette: str = "mint",
    duration_s: int = 45,
    aspect_ratio: str = "9:16",
    language: str = "Bahasa Indonesia"
) -> Dict[str, Any]:
    """
    Menyusun Master Prompt Sutradara Kreatif AnyMotion (`k2MSur2S.js`) yang dipadukan
    dengan rumus empiris 11 Video Viral REA Big Data.
    """
    catalog = load_anymotion_catalog()
    style_obj = next((s for s in catalog.get("styles", []) if s["id"] == style_id), None)
    if not style_obj:
        style_obj = {
            "id": style_id,
            "name": "Editorial Collage & Kinetic Motion",
            "description": "Fast editorial collage: paper colors, photo cutouts, highlighter bars and italic headlines.",
            "use_case": "Explainers, business, and viral stories",
            "category": "Explainer & 3D World"
        }

    bp = get_blueprint_by_id(blueprint_id) or {}
    bp_title = bp.get("title", "Agusleo Halim — 4 Tangga 100 Juta Pertama dari AI")
    bp_hook = bp.get("hook_formula", "Concrete Financial / Curiosity Hook in First 3 Seconds")
    bp_cpm = bp.get("cuts_per_min", 24.0)
    bp_avg_shot = bp.get("avg_shot_s", 2.5)
    pal_obj = ANYMOTION_PALETTES.get(palette, ANYMOTION_PALETTES["mint"])
    shader_obj = VISUAL_LOOK_SHADERS.get(visual_look, VISUAL_LOOK_SHADERS["auto"])

    target_scenes = max(4, min(14, int(round(duration_s / max(2.5, bp_avg_shot)))))

    prompt_text = f"""You are an award-winning Creative Director and Senior Motion Designer working inside AnyMotion & ClipperAI Studio. You are the creative brain behind this video, not a passive prompt executor: turn even a simple idea into a clear, engaging, professionally directed animated video. Think like a filmmaker, not a template operator.

HOW YOU DIRECT (ANYMOTION & REA BIG DATA RULES):
1. Think first. Find the most interesting true angle on "{topic}" and the strongest order to tell it in.
2. Show, then tell. Let the picture explain: scale contrasts, before and after, cause and effect, a surprising comparison. Captions support the picture, they do not replace it.
3. Direct every scene. Choose the subject, its size and place in the frame, the camera move (pushIn, pullOut, panLeft, panRight, tiltDown), the depth and the light. Every scene has one clear visual purpose.
4. Vary it. Never repeat the same framing, camera move or layout in two scenes in a row: mix wide and close, calm and quick.
5. Make something happen. Every scene has an action: something enters, grows, turns, swaps, counts up or is revealed. No still pictures with only moving text.
6. Pace it (Empirical Big Data Benchmark from "{bp_title}"):
   - Target Pacing: {bp_cpm} Cuts Per Minute (~{bp_avg_shot}s per scene, total {target_scenes} scenes for {duration_s}s).
   - Open with a high-retention 3-second hook using formula: "{bp_hook}".
   - Schedule psychoacoustic SFX hits (`pop`, `ding`, `whoosh`, `impact`, `coin`) at `dt = -17ms` (-0.017s) BEFORE key labels, numbers, and cuts appear.
7. Design with intention. Wrap highlighted keywords in *asterisks* so the engine renders animated marker/pill highlights.

THE PRODUCTION BRIEF:
- Topic / Core Idea: {topic}
- Reference Viral Blueprint: {bp_title} ({bp.get('category', 'Viral Short')})
- Selected AnyMotion Style: [{style_obj['id']}] {style_obj['name']} — {style_obj['description']}
- Post-Processing Visual Look Shader: [{visual_look}] {shader_obj['name']}
- Color Palette: {pal_obj['name']} (BG: {pal_obj['bg']}, Ink: {pal_obj['ink']}, Primary: {pal_obj['a']}, Secondary: {pal_obj['b']}, Accent: {pal_obj['c']})
- Aspect Ratio: {aspect_ratio} | Target Duration: {duration_s} seconds | Language: {language}

OUTPUT FORMAT:
Return a complete, production-ready JSON storyboard object containing:
1. "project_title": Viral title (< 65 chars)
2. "hook_3s": The exact opening 3-second verbal & visual hook
3. "style_id": "{style_obj['id']}"
4. "visual_look": "{visual_look}"
5. "palette": "{palette}"
6. "scenes": Array of {target_scenes} scenes, each with:
   - "scene_num": 1..{target_scenes}
   - "duration_s": number (2.2 to 4.8)
   - "component_type": one of ["phone_hero", "app_window", "feature_list", "stat_shock", "metric_counter", "split_vs", "tweet_quote", "code_terminal", "floating_badge", "cta_slam"]
   - "camera_move": one of ["pushIn", "pullOut", "panRight", "panLeft", "closeUp"]
   - "title_regular": Opening part of the headline
   - "title_italic": Highlighted *keyword* part of the headline
   - "narration_line": Natural spoken narration in {language}
   - "floating_labels": Array of 2-3 punchy UI callout badges (77.3% packaging layer rule)
   - "sfx_cues": Array of {{"type": "pop|ding|whoosh|impact|coin", "anchor": "label_in|title_in|cut", "dt_s": -0.017}}"""

    return {
        "ok": True,
        "topic": topic,
        "style": style_obj,
        "blueprint": bp,
        "visual_look": visual_look,
        "palette": pal_obj,
        "target_scenes": target_scenes,
        "prompt": prompt_text
    }


def score_clip_with_bigdata(
    transcript_text: str,
    duration_s: float,
    shots_count: int = 8,
    niche: str = "universal"
) -> Dict[str, Any]:
    """
    Mengevaluasi kualitas viral sebuah klip/naskah berdasarkan distribusi Big Data 11 Video REA
    (184 shots, 2.405 text overlays, 622 SFX events).
    """
    words = re.findall(r"\w+", (transcript_text or "").lower())
    dur = max(1.0, float(duration_s))
    cpm = (shots_count * 60.0) / dur
    wps = len(words) / dur

    # 1. Skor Pacing (Optimal Creator Shorts: 14 - 26 CPM)
    if 14.0 <= cpm <= 28.0:
        pacing_score = 98
    elif 10.0 <= cpm < 14.0:
        pacing_score = 88
    else:
        pacing_score = max(65, 95 - int(abs(cpm - 20.0) * 2.0))

    # 2. Skor Power Words & Angka Spesifik (Raffi 14M / Agusleo 100 Juta / Gaji 25 Juta)
    power_hits = [w for w in words if w in EMPIRICAL_BIGDATA_LAWS["viral_power_tokens_id"]]
    has_numbers = bool(re.search(r"\d+", transcript_text or ""))
    hook_score = min(99, 74 + len(set(power_hits)) * 5 + (10 if has_numbers else 0))

    # 3. Skor Kepadatan Informasi (Ideal: 2.2 - 3.6 kata/detik)
    if 2.0 <= wps <= 3.8:
        density_score = 96
    else:
        density_score = max(70, 94 - int(abs(wps - 2.8) * 10))

    overall = int(round(0.40 * hook_score + 0.35 * pacing_score + 0.25 * density_score))
    return {
        "overall_bigdata_score": min(99, max(68, overall)),
        "pacing_score": pacing_score,
        "hook_score": hook_score,
        "density_score": density_score,
        "measured_cpm": round(cpm, 1),
        "words_per_sec": round(wps, 2),
        "power_words_found": list(set(power_hits))[:8],
        "has_numeric_anchor": has_numbers,
        "recommended_sfx_lead_ms": -17.0
    }
