"""QA otomatis hasil render: spesifikasi, loudness, bukti gerak kamera/cut, contact sheet."""
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict

import numpy as np

try:
    import cv2
except Exception:  # pragma: no cover
    cv2 = None


def _run(cmd):
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                          encoding="utf-8", errors="replace")


def check_video(path: str, expected_shots: int = 0) -> Dict[str, Any]:
    res: Dict[str, Any] = {"file": Path(path).name, "issues": []}
    p = _run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path])
    j = json.loads(p.stdout)
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    has_audio = any(s["codec_type"] == "audio" for s in j["streams"])
    res.update(width=v["width"], height=v["height"], dur=round(float(j["format"]["duration"]), 2),
               fps=v["r_frame_rate"], audio=has_audio)
    if (v["width"], v["height"]) != (1080, 1920):
        res["issues"].append("resolusi bukan 1080x1920")
    if not has_audio:
        res["issues"].append("tidak ada audio")

    # loudness
    e = _run(["ffmpeg", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"])
    m = re.findall(r"I:\s+(-?\d+\.\d+) LUFS", e.stderr)
    if m:
        res["lufs"] = float(m[-1])
        if abs(res["lufs"] + 14) > 2.5:
            res["issues"].append(f"loudness {res['lufs']} LUFS (target -14)")

    # gerak & cut
    if cv2 is not None:
        cap = cv2.VideoCapture(path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        prev, diffs, frames = None, [], []
        for i in range(0, n, max(1, int(fps / 5))):  # 5 fps sampling
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ok, f = cap.read()
            if not ok:
                break
            g = cv2.cvtColor(cv2.resize(f, (108, 192)), cv2.COLOR_BGR2GRAY).astype(np.float32)
            if prev is not None:
                diffs.append(float(np.mean(np.abs(g - prev))))
            prev = g
            frames.append((i, f))
        cap.release()
        if diffs:
            d = np.array(diffs)
            cuts = int(np.sum(d > max(18.0, d.mean() + 2.5 * d.std())))
            res.update(motion_mean=round(float(d.mean()), 2), cuts_detected=cuts)
            if d.mean() < 1.0:
                res["issues"].append("hampir tidak ada gerakan (video statis)")
            if expected_shots > 3 and cuts == 0:
                res["issues"].append("tidak terdeteksi cut")
        # contact sheet 8 frame
        if frames:
            pick = [frames[int(k)] for k in np.linspace(0, len(frames) - 1, min(8, len(frames)))]
            thumbs = [cv2.resize(f, (270, 480)) for _, f in pick]
            sheet = np.hstack(thumbs)
            sp = Path(path).with_suffix(".qa.jpg")
            cv2.imwrite(str(sp), sheet)
            res["contact_sheet"] = sp.name
    res["expected_shots"] = expected_shots
    res["ok"] = not res["issues"]
    return res
