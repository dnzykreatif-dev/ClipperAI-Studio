"""
ClipperAI Studio - Multi-Provider AI Brain & Key Rotation Router
Mendukung:
  1. Google Gemini Native API (Google AI Studio Free Tier & Gemini Pro / Paid Tier)
  2. SumoPod AI (https://ai.sumopod.com/v1 - Provider Token AI OpenAI-Compatible)
  3. 9Router (http://localhost:20128/v1 atau URL kustom - Multi-AI Router)
  4. OpenRouter (https://openrouter.ai/api/v1)
  5. Groq Cloud (https://api.groq.com/openai/v1)
  6. Custom OpenAI-Compatible Endpoint

Fitur Utama:
  - Multi-API Key Pool + Auto-Rotation otomatis saat terkena Limit (HTTP 429 / Quota Exhausted)
  - Pemilihan Model bebas (bisa pilih dari daftar populer, tarik otomatis dari server /models, atau ketik manual)
  - AI Viral Clip Curation (memilih potongan cerita utuh Hook -> Isi -> Kesimpulan + koreksi otomatis salah ketik Whisper)
  - AI Video Director (menentukan power words, judul hook, teks thumbnail, dan alasan viral)
  - AI SEO Copywriter (Judul CTR tinggi, Deskripsi lengkap, Hashtag, Keyword Tag, dan Ide Konten Baru)
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "ai_config.json"

PROVIDER_PRESETS: Dict[str, Dict[str, Any]] = {
    "gemini": {
        "name": "Google Gemini (AI Studio Gratis / Gemini Pro)",
        "type": "gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "default_model": "gemini-3.8-pro",
        "models": [
            "gemini-4-argon",
            "gemini-3.8-argon",
            "gemini-3.8-pro",
            "gemini-3.8-flash",
            "gemini-3.8-pro-preview",
            "gemini-3.8-flash-preview",
            "gemini-3.1-pro-preview",
            "gemini-3.1-flash-preview",
            "gemini-3.1-flash-lite-preview",
            "gemini-3-pro-preview",
            "gemini-3-flash-preview",
            "gemini-2.5-pro",
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.0-flash",
        ],
        "key_hint": "Masukkan 1 atau beberapa API Key Google AI Studio (aistudio.google.com/apikey) atau Gemini Pro. Pisahkan per baris untuk rotasi otomatis jika limit.",
    },
    "sumopod": {
        "name": "SumoPod AI (ai.sumopod.com)",
        "type": "openai",
        "base_url": "https://ai.sumopod.com/v1",
        "default_model": "gemini-3.8-pro",
        "models": [
            "gemini-4-argon",
            "gemini-3.8-argon",
            "gemini-3.8-pro",
            "gemini-3.8-flash",
            "gemini-3.1-pro-preview",
            "gemini-3-pro-preview",
            "gemini-3-flash-preview",
            "gemini-2.5-pro",
            "gemini-2.5-flash",
            "gpt-4o-mini",
            "gpt-4o",
            "claude-3-7-sonnet",
            "claude-3-5-sonnet-20241022",
            "deepseek-chat",
        ],
        "key_hint": "Masukkan API Key dari dashboard SumoPod (sk-...), bisa lebih dari 1 baris untuk cadangan saldo/limit.",
    },
    "9router": {
        "name": "9Router (Multi-AI Local / Cloud Router)",
        "type": "openai",
        "base_url": "http://localhost:20128/v1",
        "default_model": "gemini-3.8-pro",
        "models": [
            "gemini-4-argon",
            "gemini-3.8-argon",
            "gemini-3.8-pro",
            "gemini-3.8-flash",
            "gemini-3.1-pro-preview",
            "gemini-3-pro-preview",
            "gemini-3-flash-preview",
            "gemini-2.5-pro",
            "gemini-2.5-flash",
            "claude-sonnet-4-20250514",
            "claude-3-7-sonnet",
            "gpt-4o",
            "gpt-4o-mini",
            "qwen-max",
            "deepseek-chat",
        ],
        "key_hint": "Masukkan API Key 9Router (atau kosongkan / isi '9router' jika berjalan lokal tanpa autentikasi).",
    },
    "openrouter": {
        "name": "OpenRouter (openrouter.ai)",
        "type": "openai",
        "base_url": "https://openrouter.ai/api/v1",
        "default_model": "google/gemini-3.8-pro",
        "models": [
            "google/gemini-4-argon",
            "google/gemini-3.8-pro",
            "google/gemini-3.8-flash",
            "google/gemini-3.1-pro-preview",
            "google/gemini-3-pro-preview",
            "google/gemini-3-flash-preview",
            "google/gemini-2.5-pro",
            "google/gemini-2.5-flash",
            "anthropic/claude-3.7-sonnet",
            "openai/gpt-4o-mini",
            "deepseek/deepseek-chat:free",
        ],
        "key_hint": "Masukkan API Key OpenRouter (sk-or-v1-...), satu per baris.",
    },
    "groq": {
        "name": "Groq Cloud (Super Cepat / Gratis)",
        "type": "openai",
        "base_url": "https://api.groq.com/openai/v1",
        "default_model": "llama-3.3-70b-versatile",
        "models": [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "deepseek-r1-distill-llama-70b",
            "gemma2-9b-it",
        ],
        "key_hint": "Masukkan API Key Groq (gsk_...), satu per baris.",
    },
    "custom": {
        "name": "Custom OpenAI-Compatible Endpoint",
        "type": "openai",
        "base_url": "https://api.openai.com/v1",
        "default_model": "gemini-3.8-pro",
        "models": [
            "gemini-4-argon",
            "gemini-3.8-pro",
            "gemini-3.8-flash",
            "gemini-3.1-pro-preview",
            "gemini-3-flash-preview",
            "gemini-2.5-flash",
            "gpt-4o-mini",
            "gpt-4o",
            "deepseek-chat",
        ],
        "key_hint": "Masukkan Base URL (/v1) dan API Key provider Anda (satu per baris).",
    },
}

DEFAULT_CONFIG: Dict[str, Any] = {
    "enabled": True,
    "provider": "gemini",
    "base_url": "https://generativelanguage.googleapis.com/v1beta",
    "model": "gemini-2.5-flash",
    "api_keys": [],
    "active_key_index": 0,
    "temperature": 0.4,
    "auto_rotate_on_limit": True,
    "provider_configs": {},
}


def load_config() -> Dict[str, Any]:
    cfg = dict(DEFAULT_CONFIG)
    if CONFIG_PATH.exists():
        try:
            saved = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            if isinstance(saved, dict):
                cfg.update(saved)
        except Exception:
            pass
    # Cek juga environment variable jika user belum isi di UI
    env_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if env_key and not cfg.get("api_keys"):
        cfg["api_keys"] = [k.strip() for k in re.split(r"[\r\n,]+", env_key) if k.strip()]
    return cfg


def save_config(new_cfg: Dict[str, Any]) -> Dict[str, Any]:
    cfg = load_config()
    provider = new_cfg.get("provider", cfg.get("provider", "gemini"))
    preset = PROVIDER_PRESETS.get(provider, PROVIDER_PRESETS["gemini"])

    # Simpan histori per-provider supaya saat ganti tab provider, key & URL lama tidak hilang
    prov_cfgs = dict(cfg.get("provider_configs") or {})

    raw_keys = new_cfg.get("api_keys", cfg.get("api_keys", []))
    if isinstance(raw_keys, str):
        keys = [k.strip() for k in re.split(r"[\r\n]+", raw_keys) if k.strip()]
    elif isinstance(raw_keys, list):
        keys = [str(k).strip() for k in raw_keys if str(k).strip()]
    else:
        keys = []

    base_url = (new_cfg.get("base_url") or preset["base_url"]).strip().rstrip("/")
    model = (new_cfg.get("model") or preset["default_model"]).strip()
    active_idx = int(new_cfg.get("active_key_index", 0) or 0)
    if keys:
        active_idx = max(0, min(active_idx, len(keys) - 1))
    else:
        active_idx = 0

    prov_cfgs[provider] = {
        "base_url": base_url,
        "model": model,
        "api_keys": keys,
        "active_key_index": active_idx,
    }

    cfg.update({
        "enabled": bool(new_cfg.get("enabled", True)),
        "provider": provider,
        "base_url": base_url,
        "model": model,
        "api_keys": keys,
        "active_key_index": active_idx,
        "auto_rotate_on_limit": bool(new_cfg.get("auto_rotate_on_limit", True)),
        "provider_configs": prov_cfgs,
    })
    CONFIG_PATH.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    return cfg


def mask_key(k: str) -> str:
    k = k.strip()
    if len(k) <= 8:
        return "*" * len(k)
    return f"{k[:6]}...{k[-4:]}"


def is_ai_ready() -> bool:
    cfg = load_config()
    if not cfg.get("enabled", True):
        return False
    prov = cfg.get("provider", "gemini")
    keys = cfg.get("api_keys") or []
    if prov == "9router":
        return True
    return len(keys) > 0


def get_public_status() -> Dict[str, Any]:
    cfg = load_config()
    prov = cfg.get("provider", "gemini")
    preset = PROVIDER_PRESETS.get(prov, PROVIDER_PRESETS["gemini"])
    keys = cfg.get("api_keys") or []
    idx = min(int(cfg.get("active_key_index", 0)), max(0, len(keys) - 1))
    return {
        "enabled": cfg.get("enabled", True),
        "ready": is_ai_ready(),
        "provider": prov,
        "provider_name": preset["name"],
        "base_url": cfg.get("base_url") or preset["base_url"],
        "model": cfg.get("model") or preset["default_model"],
        "key_count": len(keys),
        "active_key_index": idx,
        "active_key_masked": mask_key(keys[idx]) if keys else ("Tanpa Key (Local)" if prov == "9router" else "Belum Diisi"),
        "keys_masked": [mask_key(k) for k in keys],
        "api_keys_raw": "\n".join(keys),
        "auto_rotate_on_limit": cfg.get("auto_rotate_on_limit", True),
        "presets": PROVIDER_PRESETS,
        "provider_configs": cfg.get("provider_configs", {}),
    }


def _call_gemini_native(base_url: str, model: str, api_key: str, system_prompt: str, user_prompt: str,
                        json_mode: bool = True, timeout: int = 45) -> str:
    clean_model = model.replace("models/", "").strip()
    # Daftar fallback cerdas: jika model Argon/Pro terkena limit kuota gratis (429) atau 404, otomatis turun ke Flash yang kuotanya longgar
    fallback_chain = [clean_model]
    for fb in ("gemini-2.5-flash", "gemini-3-flash-preview", "gemini-2.0-flash", "gemini-2.5-pro"):
        if fb not in fallback_chain:
            fallback_chain.append(fb)

    gen_cfg: Dict[str, Any] = {"temperature": 0.35}
    if json_mode:
        gen_cfg["responseMimeType"] = "application/json"

    payload: Dict[str, Any] = {
        "contents": [{"role": "user", "parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}],
        "generationConfig": gen_cfg,
    }
    data = json.dumps(payload).encode("utf-8")

    last_http_err = None
    for idx_m, cand_model in enumerate(fallback_chain):
        url = f"{base_url.rstrip('/')}/models/{urllib.parse.quote(cand_model)}:generateContent?key={urllib.parse.quote(api_key)}"
        req = urllib.request.Request(
            url, data=data,
            headers={"Content-Type": "application/json", "User-Agent": "ClipperAI-Studio/3.0"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = json.loads(resp.read().decode("utf-8", errors="replace"))
            candidates = raw.get("candidates") or []
            if not candidates:
                raise RuntimeError(f"Respons Gemini kosong: {raw}")
            parts = (candidates[0].get("content") or {}).get("parts") or []
            texts = [p.get("text", "") for p in parts if p.get("text")]
            return "\n".join(texts).strip()
        except urllib.error.HTTPError as he:
            last_http_err = he
            # Jika 404 (model belum tersedia) atau 429 (kuota model habis), otomatis coba model berikutnya di fallback_chain
            # Jika 403 (API Key leaked / invalid), langsung stop dan raise agar tidak membuang waktu
            if he.code == 403:
                raise
            if he.code in (404, 429) and idx_m + 1 < len(fallback_chain):
                continue
            raise
    if last_http_err:
        raise last_http_err
    raise RuntimeError("Gagal memanggil Gemini API.")


def _call_openai_compatible(base_url: str, model: str, api_key: str, system_prompt: str, user_prompt: str,
                            json_mode: bool = True, timeout: int = 45) -> str:
    base = base_url.rstrip("/")
    if not base.endswith("/chat/completions"):
        url = f"{base}/chat/completions"
    else:
        url = base

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "ClipperAI-Studio/3.0",
    }
    token = api_key.strip() if api_key else "9router"
    headers["Authorization"] = f"Bearer {token}"

    payload: Dict[str, Any] = {
        "model": model.strip(),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.35,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = json.loads(resp.read().decode("utf-8", errors="replace"))
    choices = raw.get("choices") or []
    if not choices:
        raise RuntimeError(f"Respons API kosong: {raw}")
    msg = choices[0].get("message") or {}
    content = msg.get("content") or ""
    if isinstance(content, list):
        content = "\n".join(c.get("text", "") for c in content if isinstance(c, dict))
    return str(content).strip()


def generate_text(system_prompt: str, user_prompt: str, json_mode: bool = True, timeout: int = 45) -> str:
    """
    Memanggil AI dengan dukungan rotasi API Key otomatis saat salah satu API Key terkena limit (429 / Quota).
    """
    cfg = load_config()
    if not cfg.get("enabled", True):
        raise RuntimeError("AI Brain sedang dinonaktifkan di pengaturan.")

    prov = cfg.get("provider", "gemini")
    preset = PROVIDER_PRESETS.get(prov, PROVIDER_PRESETS["gemini"])
    ptype = preset["type"]
    base_url = (cfg.get("base_url") or preset["base_url"]).strip()
    model = (cfg.get("model") or preset["default_model"]).strip()
    keys: List[str] = list(cfg.get("api_keys") or [])

    if not keys:
        if prov == "9router":
            keys = ["9router"]
        else:
            raise RuntimeError(f"Belum ada API Key untuk provider '{preset['name']}'. Silakan isi di menu Pengaturan AI.")

    start_idx = min(int(cfg.get("active_key_index", 0)), len(keys) - 1)
    auto_rotate = cfg.get("auto_rotate_on_limit", True)
    max_attempts = len(keys) if auto_rotate else 1

    last_err = None
    for attempt in range(max_attempts):
        idx = (start_idx + attempt) % len(keys)
        key = keys[idx]
        try:
            if ptype == "gemini":
                out = _call_gemini_native(base_url, model, key, system_prompt, user_prompt, json_mode=json_mode, timeout=timeout)
            else:
                out = _call_openai_compatible(base_url, model, key, system_prompt, user_prompt, json_mode=json_mode, timeout=timeout)

            # Jika sempat berotasi ke key berikutnya, simpan posisi key yang berhasil sebagai active_key_index
            if idx != start_idx:
                cfg["active_key_index"] = idx
                try:
                    CONFIG_PATH.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
                except Exception:
                    pass
            return out
        except urllib.error.HTTPError as he:
            err_body = ""
            try:
                err_body = he.read().decode("utf-8", errors="ignore")[:500]
            except Exception:
                pass
            last_err = f"HTTP {he.code} pada Key #{idx + 1} ({mask_key(key)}): {err_body or he.reason}"
            print(f"[AI Router Warning] {last_err}")
            # Rotasi ke key berikutnya jika key invalid (400/401), terkena rate limit (429), quota habis (402/403), atau server sibuk (500/503)
            if he.code in (400, 401, 402, 403, 429, 500, 502, 503, 504) and attempt + 1 < max_attempts:
                continue
            break
        except Exception as e:
            last_err = f"Error pada Key #{idx + 1} ({mask_key(key)}): {e}"
            print(f"[AI Router Warning] {last_err}")
            if attempt + 1 < max_attempts:
                continue
            break

    raise RuntimeError(last_err or "Gagal menghubungi server AI.")


def extract_json(raw: str) -> Any:
    """Ekstrak objek/array JSON dengan aman meskipun dibungkus blok ```json ... ```."""
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except Exception:
        pass
    # Cari kurung kurawal pertama hingga terakhir
    m = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", cleaned)
    if m:
        return json.loads(m.group(1))
    raise ValueError(f"Output AI bukan JSON valid: {raw[:300]}")


def fetch_available_models(provider: Optional[str] = None, base_url: Optional[str] = None,
                           api_key: Optional[str] = None) -> List[str]:
    """Mengambil daftar model langsung dari endpoint provider (/models) + menggabungkan dengan preset populer."""
    cfg = load_config()
    prov = provider or cfg.get("provider", "gemini")
    preset = PROVIDER_PRESETS.get(prov, PROVIDER_PRESETS["gemini"])
    b_url = (base_url or cfg.get("base_url") or preset["base_url"]).strip().rstrip("/")
    keys = cfg.get("api_keys") or []
    key = (api_key or (keys[0] if keys else "")).strip()

    models: List[str] = list(preset.get("models", []))
    try:
        if preset["type"] == "gemini" and key:
            url = f"{b_url}/models?key={urllib.parse.quote(key)}"
            req = urllib.request.Request(url, headers={"User-Agent": "ClipperAI-Studio/3.0"})
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                for item in data.get("models", []):
                    methods = item.get("supportedGenerationMethods") or []
                    if "generateContent" in methods:
                        name = str(item.get("name", "")).replace("models/", "")
                        if name and name not in models:
                            models.append(name)
        else:
            url = f"{b_url}/models"
            headers = {"User-Agent": "ClipperAI-Studio/3.0"}
            if key:
                headers["Authorization"] = f"Bearer {key}"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                for item in data.get("data", []):
                    mid = str(item.get("id", "")).strip()
                    if mid and mid not in models:
                        models.append(mid)
    except Exception as e:
        print(f"[Model Discovery Info] Menggunakan daftar model preset ({e})")
    return models


def test_ai_connection() -> Dict[str, Any]:
    """Menguji koneksi AI saat ini dan mengukur waktu respons (ms)."""
    t0 = time.time()
    cfg = load_config()
    reply = generate_text(
        system_prompt="Jawab hanya dalam format JSON singkat.",
        user_prompt='Kembalikan JSON: {"status": "ok", "salam": "Koneksi AI ClipperAI Studio aktif!"}',
        json_mode=True,
        timeout=20,
    )
    dt = int((time.time() - t0) * 1000)
    parsed = extract_json(reply)
    st = get_public_status()
    return {
        "ok": True,
        "latency_ms": dt,
        "provider": st["provider_name"],
        "model": st["model"],
        "active_key": st["active_key_masked"],
        "response": parsed,
    }


# ==============================================================================
# 1. AI VIRAL CLIP CURATION + TRANSCRIPT CORRECTION + DIRECTOR PLAN
# ==============================================================================
def curate_viral_clips_with_ai(
    transcript_data: Dict[str, Any],
    niche: str = "universal",
    min_duration: float = 25.0,
    max_duration: float = 60.0,
    top_k: int = 3,
) -> Optional[List[Dict[str, Any]]]:
    """
    Menggunakan AI (Gemini / SumoPod / 9Router) untuk:
      1. Mengoreksi kata-kata yang salah dengar oleh Whisper di transkrip (misal 'marau lama' -> 'para ulama')
      2. Memilih top_k segmen cerita paling viral & utuh (Hook -> Isi -> Punchline/Kesimpulan)
      3. Membuat Judul Hook Banner, Teks Thumbnail, Power Words, dan Paket SEO lengkap.
    Mengembalikan None jika AI tidak aktif atau gagal (sehingga mesin otomatis fallback ke algoritma lokal).
    """
    if not is_ai_ready():
        return None

    segments = transcript_data.get("segments") or []
    if not segments:
        return None

    # Susun daftar segmen ber-timestamp untuk dikirim ke AI
    seg_lines = []
    for s in segments[:220]:
        sid = s.get("id", 0)
        st = float(s.get("start", 0.0))
        en = float(s.get("end", 0.0))
        txt = s.get("text", "").strip()
        if txt:
            seg_lines.append(f"[{sid}|{st:.2f}-{en:.2f}] {txt}")

    transcript_block = "\n".join(seg_lines)

    target_clips_str = "SEMUA bagian klip potensial (sebanyak mungkin momen menarik yang memenuhi kriteria)" if top_k >= 90 else f"{top_k} bagian klip"

    system_prompt = (
        "Kamu adalah Sutradara Video Shorts/Reels Viral & Editor Bahasa Indonesia profesional sekelas tim kreator papan atas.\n"
        "Tugasmu:\n"
        "1. BACA transkrip video ber-timestamp berikut (Niche: " + niche.upper() + ").\n"
        "2. KOREKSI salah dengar (typo ASR Whisper) yang terlihat jelas berdasarkan konteks kalimat (contoh: 'marau lama' -> 'para ulama', 'anak perumpuan' -> 'anak perempuan', 'daripang' -> 'gampang', 'sebeginak' -> 'sebegitu'). Masukkan koreksi kata per kata di kamus `word_replacements`.\n"
        f"3. PILIH {target_clips_str} paling menarik, menyentuh, atau membuka wawasan dengan durasi masing-masing antara {min_duration:.0f} hingga {max_duration:.0f} detik (tidak boleh tumpang tindih).\n"
        "   - Wajib dimulai dari kalimat pembuka (Hook) yang kuat dan berhenti tepat di akhir kalimat kesimpulan/punchline (cerita utuh, tidak gantung!).\n"
        "4. Untuk setiap klip, buatkan:\n"
        "   - `start_time` (float detik, sesuai awal segmen pembuka)\n"
        "   - `end_time` (float detik, sesuai akhir segmen penutup)\n"
        "   - `hook_title`: Judul banner atas 3-6 kata HURUF KAPITAL yang memancing rasa penasaran (tanpa titik-titik/potongan kata, contoh: 'RAHASIA MENDIDIK ANAK PEREMPUAN')\n"
        "   - `thumbnail_text`: 2-4 kata super singkat & nendang untuk teks besar di Thumbnail (contoh: 'JAMINAN SURGA!')\n"
        "   - `hook_score`: Skor potensi viral 88.0 - 99.5\n"
        "   - `viral_reason`: 1 kalimat alasan kenapa bagian ini kuat secara emosional/edukatif\n"
        "   - `power_words`: Array berisi 4-8 kata kunci penting di dalam klip tersebut untuk diberi warna highlight khusus\n"
        "   - `seo_title`: Judul YouTube Shorts memikat (< 60 karakter, akhiri dengan emoji & #Shorts)\n"
        "   - `alt_titles`: Array 4 opsi judul alternatif yang bikin penasaran\n"
        "   - `description`: Deskripsi video lengkap (2 kalimat pembuka kuat + 3 poin intisari hikmah/materi + ajakan komentar)\n"
        "   - `hashtags`: Array 6-8 hashtag relevan (diawali #)\n"
        "   - `tags`: Array 10-12 keyword tag pencarian YouTube\n"
        "   - `content_ideas`: Array 3 ide konten lanjutan dari topik ini\n"
        "Kembalikan HANYA JSON valid dengan struktur:\n"
        "{\n"
        '  "word_replacements": {"kata_salah_1": "kata_benar_1"},\n'
        '  "clips": [ { ... } ]\n'
        "}"
    )

    user_prompt = f"TRANSKRIP VIDEO ({len(seg_lines)} segmen):\n{transcript_block}"

    try:
        raw = generate_text(system_prompt, user_prompt, json_mode=True, timeout=55)
        data = extract_json(raw)
        if not isinstance(data, dict):
            return None

        # 1. Terapkan koreksi kata dari AI ke seluruh segmen & kata di transkrip
        replacements: Dict[str, str] = data.get("word_replacements") or {}
        if isinstance(replacements, dict) and replacements:
            for seg in segments:
                txt = seg.get("text", "")
                for wrong, right in replacements.items():
                    if wrong and right and len(wrong) >= 3:
                        txt = re.sub(rf"\b{re.escape(wrong)}\b", right, txt, flags=re.IGNORECASE)
                seg["text"] = txt
                for w in seg.get("words") or []:
                    w_clean = re.sub(r"[^\w\-]", "", w.get("word", "")).lower()
                    for wrong, right in replacements.items():
                        if w_clean == wrong.strip().lower() and " " not in right.strip():
                            w["word"] = right.strip()

        ai_clips = data.get("clips") or []
        if not isinstance(ai_clips, list) or not ai_clips:
            return None

        results: List[Dict[str, Any]] = []
        for idx, ac in enumerate(ai_clips[:top_k]):
            st = float(ac.get("start_time", 0.0))
            en = float(ac.get("end_time", st + 35.0))
            # Snap ke batas segmen terdekat agar kata tidak terpotong di tengah
            matched_segs = [s for s in segments if s["end"] > st + 0.2 and s["start"] < en - 0.2]
            if not matched_segs:
                continue
            real_start = float(matched_segs[0]["start"])
            real_end = float(matched_segs[-1]["end"])
            dur = round(real_end - real_start, 2)
            if dur < 10.0:
                continue

            words = []
            texts = []
            for s in matched_segs:
                texts.append(s.get("text", "").strip())
                words.extend(s.get("words") or [])

            hashtags_list = ac.get("hashtags") or ["#Shorts", "#Viral", "#Fyp"]
            if isinstance(hashtags_list, str):
                hashtags_list = hashtags_list.split()
            tags_list = ac.get("tags") or ["shorts", "video viral", niche]

            hook_title = str(ac.get("hook_title") or "POIN PENTING HARI INI").strip().upper()
            thumb_text = str(ac.get("thumbnail_text") or hook_title[:24]).strip().upper()

            ai_seo = {
                "title": str(ac.get("seo_title") or f"{hook_title.title()} 🔥 #Shorts"),
                "title_length": len(str(ac.get("seo_title") or "")),
                "alternative_titles": ac.get("alt_titles") or [],
                "description": str(ac.get("description") or " ".join(texts)),
                "tags": tags_list,
                "tags_csv": ", ".join(tags_list),
                "tags_char_count": len(", ".join(tags_list)),
                "hashtags": hashtags_list,
                "thumbnail_text": thumb_text,
                "viral_reason": str(ac.get("viral_reason") or ""),
                "content_ideas": ac.get("content_ideas") or [],
                "category_id": "27" if niche in ("kajian", "edukasi", "bisnis") else "22",
                "best_schedule": {
                    "lunch_peak": "11:30 - 13:00 WIB (Peak Siang)",
                    "evening_peak": "17:30 - 20:30 WIB (Prime Time Malam)",
                    "best_days": "Kamis, Jumat, Sabtu, Minggu",
                    "recommended_publish_status": "public",
                },
                "seo_score": 99,
                "mode": "shorts",
                "ai_generated": True,
            }

            results.append({
                "clip_id": f"clip_{idx + 1}",
                "start_time": real_start,
                "end_time": real_end,
                "duration": dur,
                "hook_score": float(ac.get("hook_score", 96.5)),
                "hook_title": hook_title,
                "thumbnail_text": thumb_text,
                "viral_reason": str(ac.get("viral_reason") or ""),
                "power_words": [str(pw).lower().strip() for pw in (ac.get("power_words") or []) if pw],
                "text": " ".join(texts),
                "words": words,
                "hashtags": " ".join(hashtags_list),
                "ai_seo": ai_seo,
            })

        return results if results else None
    except Exception as e:
        print(f"[AI Clip Curation Fallback] Gagal kurasi via AI, kembali ke algoritma lokal: {e}")
        return None


# ==============================================================================
# 2. AI SEO & COPYWRITING ENGINE (JUDUL, DESKRIPSI, HASHTAG, KEYWORD, IDE KONTEN)
# ==============================================================================
def generate_seo_with_ai(
    transcript_text: str,
    title_hint: Optional[str] = None,
    niche: str = "universal",
    speaker: Optional[str] = None,
    mode: str = "shorts",
) -> Optional[Dict[str, Any]]:
    if not is_ai_ready():
        return None

    is_long = mode.lower() in ("long_form", "long")
    system_prompt = (
        "Kamu adalah Pakar YouTube SEO, TikTok Strategist, & Copywriter Viral Indonesia.\n"
        f"Buatkan paket metadata SEO lengkap untuk video {'Long-Form YouTube' if is_long else 'YouTube Shorts / Reels'} "
        f"dengan kategori '{niche}'{f' (Pembicara/Channel: {speaker})' if speaker else ''}.\n"
        "Kembalikan HANYA JSON valid dengan struktur:\n"
        "{\n"
        '  "title": "Judul utama memikat CTR tinggi (Utuh, tidak terpotong titik-titik, akhiri #Shorts jika mode shorts)",\n'
        '  "thumbnail_text": "2-4 KATA HOOK BESAR UNTUK THUMBNAIL",\n'
        '  "alternative_titles": ["Opsi judul 1", "Opsi judul 2", "Opsi judul 3", "Opsi judul 4"],\n'
        '  "description": "Deskripsi lengkap berisi 2 kalimat hook pembuka, 3 bullet point intisari pembahasan, dan kalimat ajakan subscribe/komentar serta hashtag di bawah",\n'
        '  "hashtags": ["#Hashtag1", "#Hashtag2", "#Hashtag3", "#Hashtag4", "#Hashtag5", "#Shorts"],\n'
        '  "tags": ["keyword 1", "keyword 2", "keyword 3", "keyword 4", "keyword 5", "keyword 6", "keyword 7", "keyword 8"],\n'
        '  "content_ideas": ["Ide video lanjutan 1", "Ide video lanjutan 2", "Ide video lanjutan 3"]\n'
        "}"
    )
    user_prompt = f"Judul Awal/Hint: {title_hint or '-'}\nIsi Transkrip Video:\n{transcript_text[:3500]}"

    try:
        raw = generate_text(system_prompt, user_prompt, json_mode=True, timeout=35)
        d = extract_json(raw)
        if not isinstance(d, dict) or not d.get("title"):
            return None
        tags = d.get("tags") or ["shorts", "viral", niche]
        hashtags = d.get("hashtags") or ["#Shorts", "#Viral"]
        return {
            "title": str(d["title"]).strip(),
            "title_length": len(str(d["title"]).strip()),
            "thumbnail_text": str(d.get("thumbnail_text") or title_hint or "WAJIB TAHU!").upper().strip(),
            "alternative_titles": d.get("alternative_titles") or [],
            "description": str(d.get("description") or transcript_text[:300]),
            "tags": tags,
            "tags_csv": ", ".join(tags),
            "tags_char_count": len(", ".join(tags)),
            "hashtags": hashtags,
            "content_ideas": d.get("content_ideas") or [],
            "category_id": "27" if niche in ("kajian", "edukasi", "bisnis") else "22",
            "best_schedule": {
                "lunch_peak": "11:30 - 13:00 WIB (Peak Siang)",
                "evening_peak": "17:30 - 20:30 WIB (Prime Time Malam)",
                "best_days": "Kamis, Jumat, Sabtu, Minggu",
                "recommended_publish_status": "public",
            },
            "seo_score": 99,
            "mode": mode,
            "ai_generated": True,
        }
    except Exception as e:
        print(f"[AI SEO Fallback] {e}")
        return None


# ==============================================================================
# 3. AI IDEA & SCRIPT GENERATOR (UNTUK FACELESS STUDIO & RISET IDE)
# ==============================================================================
def generate_script_or_ideas_with_ai(topic: str, style: str = "fakta", duration_sec: int = 35) -> Optional[Dict[str, Any]]:
    if not is_ai_ready():
        return None

    target_words = max(45, int(duration_sec * 2.3))
    system_prompt = (
        "Kamu adalah Penulis Naskah Video Pendek (Shorts/Reels/TikTok) terbaik di Indonesia.\n"
        f"Gaya penulisan: {style.upper()}.\n"
        f"Buat naskah narasi voice-over yang sangat memikat tentang topik yang diminta (sekitar {target_words} kata, "
        "kalimat pendek-pendek, mengalir natural saat dibacakan, memiliki Hook kuat di 3 detik pertama, isi padat, dan penutup yang berkesan).\n"
        "Kembalikan HANYA JSON valid dengan struktur:\n"
        "{\n"
        '  "header_title": "JUDUL BANNER SINGKAT 3-4 KATA",\n'
        '  "thumbnail_text": "TEKS THUMBNAIL 2-3 KATA",\n'
        '  "script": "Naskah narasi lengkap siap dibacakan TTS...",\n'
        '  "ideas": ["Ide topik turunan 1", "Ide topik turunan 2", "Ide topik turunan 3"]\n'
        "}"
    )
    user_prompt = f"Topik: {topic}"
    try:
        raw = generate_text(system_prompt, user_prompt, json_mode=True, timeout=30)
        d = extract_json(raw)
        if isinstance(d, dict) and d.get("script"):
            return d
        return None
    except Exception as e:
        print(f"[AI Script Fallback] {e}")
        return None
