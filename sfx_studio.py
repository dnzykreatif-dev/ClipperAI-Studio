"""
ClipperAI Studio - Studio Sound Design Generator (Zero-Noise Harmonic & Sub-Bass SFX)

Menggantikan file WAV berbasis white-noise kasar ('serek-serek') dengan Sound Effects
studio modern berbasis gelombang harmonik murni, sub-bass sinematik, marimba pop organik,
dan glass chime lembut (0% white-noise frekuensi tinggi).
"""

from __future__ import annotations

import math
import wave
from pathlib import Path
import numpy as np

SR = 48000
BASE_DIR = Path(__file__).resolve().parent
SFX_DIR = BASE_DIR / "assets" / "argon" / "sfx"


def _save_stereo_wav(path: Path, left: np.ndarray, right: np.ndarray, peak: float = 0.85) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    m = max(float(np.max(np.abs(left))), float(np.max(np.abs(right))), 1e-6)
    left = (left / m) * peak
    right = (right / m) * peak
    stereo = np.stack([left, right], axis=1)
    pcm = np.clip(stereo * 32767.0, -32768, 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def _lowpass_fir(sig: np.ndarray, cutoff_hz: float, taps: int = 127) -> np.ndarray:
    """Filter Low-Pass Windowed-Sinc murni agar tidak ada frekuensi kasar/desis di atas cutoff."""
    fc = cutoff_hz / SR
    n = np.arange(taps) - (taps - 1) / 2.0
    h = np.sinc(2 * fc * n) * np.hamming(taps)
    h /= np.sum(h)
    return np.convolve(sig, h, mode="same")


def _sine_sweep(freqs: np.ndarray) -> np.ndarray:
    phase = 2.0 * np.pi * np.cumsum(freqs) / SR
    return np.sin(phase)


def make_velvet_transition(dur: float = 0.30, f_start: float = 95.0, f_peak: float = 260.0, f_end: float = 75.0) -> tuple[np.ndarray, np.ndarray]:
    """
    Transisi kamera modern (Velvet Sub-Whoosh):
    Bukan white-noise 'serek-serek', melainkan ayunan sub-bass & low-mid hangat (< 350 Hz)
    seperti transisi kamera Ali Abdaal / Iman Gadzhi.
    """
    n = int(dur * SR)
    t = np.linspace(0.0, 1.0, n)
    # Kurva frekuensi naik lalu turun halus
    f_curve = f_start + (f_peak - f_start) * np.sin(np.pi * (t ** 0.85)) ** 1.4
    f_curve = f_curve * (1.0 - 0.25 * t) + f_end * (0.25 * t)

    env = np.sin(np.pi * t) ** 1.8
    body_l = _sine_sweep(f_curve) * env
    body_r = _sine_sweep(f_curve * 1.012) * env

    # Harmonik ke-2 lembut untuk kehangatan di speaker HP
    harm_l = _sine_sweep(f_curve * 1.5) * (env ** 2.2) * 0.28
    harm_r = _sine_sweep(f_curve * 1.508) * (env ** 2.2) * 0.28

    # Sub-punch tipis di tengah transisi
    punch_env = np.exp(-((t - 0.48) / 0.14) ** 2)
    punch = _sine_sweep(np.linspace(110.0, 48.0, n)) * punch_env * 0.55

    l = _lowpass_fir(body_l + harm_l + punch, 420.0)
    r = _lowpass_fir(body_r + harm_r + punch, 420.0)
    return l, r


def make_cinema_boom(dur: float = 0.55) -> tuple[np.ndarray, np.ndarray]:
    """Sub-bass impact sinematik untuk Hook pembuka & poin klimaks."""
    n = int(dur * SR)
    t = np.linspace(0.0, dur, n)
    tn = t / dur

    # Sub drop 88Hz -> 32Hz
    f_sub = 32.0 + 56.0 * np.exp(-t * 14.0)
    env_sub = (1.0 - np.exp(-t * 120.0)) * np.exp(-t * 4.8)
    sub = _sine_sweep(f_sub) * env_sub

    # Warm chest thud 155Hz -> 55Hz (cepat)
    f_thud = 55.0 + 100.0 * np.exp(-t * 28.0)
    env_thud = (1.0 - np.exp(-t * 200.0)) * np.exp(-t * 16.0)
    thud = _sine_sweep(f_thud) * env_thud * 0.55

    # Warm cinematic fifth chord (A2 + E3: 110Hz + 165Hz) sangat halus
    env_pad = np.sin(np.pi * tn) ** 1.5 * np.exp(-t * 3.5) * 0.18
    pad_l = (np.sin(2 * np.pi * 110.0 * t) + 0.6 * np.sin(2 * np.pi * 165.0 * t)) * env_pad
    pad_r = (np.sin(2 * np.pi * 110.4 * t) + 0.6 * np.sin(2 * np.pi * 164.6 * t)) * env_pad

    l = _lowpass_fir(sub + thud + pad_l, 480.0)
    r = _lowpass_fir(sub + thud + pad_r, 480.0)
    return l, r


def make_organic_pop(dur: float = 0.11, f0: float = 340.0, f1: float = 680.0) -> tuple[np.ndarray, np.ndarray]:
    """Pop organik bersih ala UI modern (untuk Keyword Callout & Emoji Pop)."""
    n = int(dur * SR)
    t = np.linspace(0.0, dur, n)
    # Frekuensi naik cepat seperti tetesan air / marimba kayu
    freqs = f0 + (f1 - f0) * (1.0 - np.exp(-t * 45.0))
    env = (1.0 - np.exp(-t * 260.0)) * np.exp(-t * 38.0)
    sig_l = (_sine_sweep(freqs) + 0.22 * _sine_sweep(freqs * 2.0)) * env
    sig_r = (_sine_sweep(freqs * 1.006) + 0.22 * _sine_sweep(freqs * 2.01)) * env
    return _lowpass_fir(sig_l, 1400.0), _lowpass_fir(sig_r, 1400.0)


def make_glass_chime(dur: float = 0.36) -> tuple[np.ndarray, np.ndarray]:
    """Dentingan hangat kristal/marimba lembut saat Panel Insight / B-Roll Card muncul."""
    n = int(dur * SR)
    t = np.linspace(0.0, dur, n)
    env1 = (1.0 - np.exp(-t * 180.0)) * np.exp(-t * 11.0)
    # Note 2 masuk 45ms kemudian (interval Perfect Fifth hangat: C5 523.25Hz -> G5 783.99Hz)
    t2 = np.maximum(0.0, t - 0.045)
    env2 = np.where(t >= 0.045, (1.0 - np.exp(-t2 * 180.0)) * np.exp(-t2 * 10.0), 0.0)

    n1_l = np.sin(2 * np.pi * 523.25 * t) * env1
    n1_r = np.sin(2 * np.pi * 524.0 * t) * env1
    n2_l = np.sin(2 * np.pi * 783.99 * t2) * env2 * 0.75
    n2_r = np.sin(2 * np.pi * 785.0 * t2) * env2 * 0.75
    sub = np.sin(2 * np.pi * 261.63 * t) * env1 * 0.35

    l = _lowpass_fir(n1_l + n2_l + sub, 1600.0)
    r = _lowpass_fir(n1_r + n2_r + sub, 1600.0)
    return l, r


def make_warm_riser(dur: float = 0.45) -> tuple[np.ndarray, np.ndarray]:
    """Swell harmonik lembut menjelang pergantian ke kalimat inti."""
    n = int(dur * SR)
    t = np.linspace(0.0, 1.0, n)
    env = (t ** 2.2) * np.sin(np.pi * t) ** 0.7
    f1 = np.linspace(110.0, 220.0, n)
    f2 = np.linspace(165.0, 330.0, n)
    l = _lowpass_fir((_sine_sweep(f1) + 0.5 * _sine_sweep(f2)) * env, 600.0)
    r = _lowpass_fir((_sine_sweep(f1 * 1.008) + 0.5 * _sine_sweep(f2 * 0.994)) * env, 600.0)
    return l, r


def generate_all_studio_sfx() -> None:
    # 1. Velvet Transitions (menggantikan VL0501..VL0505 yang tadinya white-noise kasar)
    _save_stereo_wav(SFX_DIR / "VL0501.wav", *make_velvet_transition(0.26, 95, 240, 75), peak=0.75)
    _save_stereo_wav(SFX_DIR / "VL0502.wav", *make_velvet_transition(0.32, 85, 220, 68), peak=0.75)
    _save_stereo_wav(SFX_DIR / "VL0503.wav", *make_velvet_transition(0.28, 105, 270, 82), peak=0.75)
    _save_stereo_wav(SFX_DIR / "VL0504.wav", *make_velvet_transition(0.34, 80, 200, 65), peak=0.75)
    _save_stereo_wav(SFX_DIR / "VL0505.wav", *make_velvet_transition(0.38, 75, 190, 60), peak=0.75)

    # 2. Warm Riser Swell (VL0511)
    _save_stereo_wav(SFX_DIR / "VL0511.wav", *make_warm_riser(0.42), peak=0.70)

    # 3. Deep Cinema Sub-Bass Boom (VL0516)
    _save_stereo_wav(SFX_DIR / "VL0516.wav", *make_cinema_boom(0.52), peak=0.88)

    # 4. Crisp Organic UI Pop (VL0526 & VL0531)
    _save_stereo_wav(SFX_DIR / "VL0526.wav", *make_organic_pop(0.10, 320, 640), peak=0.72)
    _save_stereo_wav(SFX_DIR / "VL0531.wav", *make_organic_pop(0.09, 400, 780), peak=0.72)

    # 5. Warm Glass Insight Chime (VL0566)
    _save_stereo_wav(SFX_DIR / "VL0566.wav", *make_glass_chime(0.36), peak=0.74)


if __name__ == "__main__":
    generate_all_studio_sfx()
    print("Studio SFX berhasil digenerate di:", SFX_DIR)
