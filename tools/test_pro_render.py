import sys, json, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import clipper_engine as ce, pro_editor

src = sys.argv[1]
niche = sys.argv[2] if len(sys.argv) > 2 else "universal"
intensity = sys.argv[3] if len(sys.argv) > 3 else "normal"
scan = float(sys.argv[4]) if len(sys.argv) > 4 else 150.0
base = Path(__file__).resolve().parent.parent
cache_json = base / "uploads" / "test_pro_cand.json"

if cache_json.exists():
    cand = json.loads(cache_json.read_text(encoding="utf-8"))
else:
    wav = str(base / "uploads" / "test_pro_audio.wav")
    if not Path(wav).exists():
        ce.extract_audio(src, wav, max_duration=scan)
    tr = ce.transcribe_audio_with_progress(wav, scan, model_size="base", niche=niche)
    cands = ce.find_viral_clips(tr, niche=niche, min_duration=25, max_duration=50, top_k=1)
    cand = cands[0]
    cache_json.write_text(json.dumps(cand, ensure_ascii=False, indent=2), encoding="utf-8")

print("clip:", cand["start_time"], cand["end_time"], cand["hook_title"])
out = str(base / "outputs" / "test_pro_render.mp4")
t = time.time()
edl = pro_editor.render_clip_pro(src, cand, out, niche=niche, intensity=intensity)
print("render sec:", round(time.time() - t, 1))
print(json.dumps({k: v for k, v in edl.items() if k in ("duration", "qa")}, indent=1, ensure_ascii=False))
print("shots:", [(s["framing"], round(s["src"][1] - s["src"][0], 1), s.get("keyword") or s.get("broll_phrase")) for s in edl["shots"]])
