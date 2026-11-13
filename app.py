"""
ClipperAI Studio - Web Application (Universal Edition)
FastAPI Server providing Web GUI and REST APIs for All Video Niches.
"""

import os
import uuid
import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import clipper_engine

app = FastAPI(title="ClipperAI Studio", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUTS_DIR = BASE_DIR / "outputs"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")

JOBS: Dict[str, Dict[str, Any]] = {}


def process_video_pipeline(
    job_id: str,
    video_path: Optional[str] = None,
    youtube_url: Optional[str] = None,
    niche: str = "universal",
    custom_watermark: Optional[str] = None,
    model_size: str = "tiny",
    target_clips: int = 3,
    scan_range: str = "15min",
    min_dur: float = 25.0,
    max_dur: float = 60.0
):
    job = JOBS[job_id]
    try:
        # Step 0: Download YouTube video if requested
        if youtube_url and youtube_url.strip():
            job["status"] = "processing"
            job["step"] = "Mengunduh video dari YouTube via yt-dlp..."
            job["progress"] = 5

            def on_yt_progress(pct: int, msg: str):
                job["progress"] = pct
                job["step"] = msg

            downloaded_video = clipper_engine.download_youtube_video(
                url=youtube_url.strip(),
                output_dir=str(UPLOADS_DIR),
                progress_callback=on_yt_progress
            )
            video_path = downloaded_video
            job["video_path"] = video_path

        if not video_path or not os.path.exists(video_path):
            raise FileNotFoundError("File video tidak ditemukan atau gagal diunduh.")

        # Step 1: Check Duration & Extract Audio
        total_vid_dur = clipper_engine.get_video_duration(video_path)
        job["total_duration"] = total_vid_dur

        max_extract = None
        if scan_range == "15min":
            max_extract = min(total_vid_dur, 900.0)
        elif scan_range == "30min":
            max_extract = min(total_vid_dur, 1800.0)

        effective_dur = max_extract if max_extract else total_vid_dur

        job["status"] = "processing"
        job["step"] = f"Mengekstrak audio (16kHz mono)... [Durasi: {int(effective_dur//60)} menit]"
        job["progress"] = 15

        audio_path = str(UPLOADS_DIR / f"{job_id}_audio.wav")
        clipper_engine.extract_audio(video_path, audio_path, max_duration=max_extract)

        # Step 2: High-Speed Multi-Threaded Whisper Transcription
        def on_transcribe_progress(pct: int, msg: str):
            job["progress"] = pct
            job["step"] = msg

        transcript = clipper_engine.transcribe_audio_with_progress(
            audio_path=audio_path,
            total_audio_dur=effective_dur,
            model_size=model_size,
            progress_callback=on_transcribe_progress
        )
        job["transcript"] = transcript

        # Step 3: Viral Hook Scouting with Niche Awareness
        job["step"] = f"AI Viral Scout sedang menganalisis hook ({niche.title()})..."
        job["progress"] = 62

        candidates = clipper_engine.find_viral_clips(
            transcript,
            niche=niche,
            min_duration=min_dur,
            max_duration=max_dur,
            top_k=target_clips
        )

        if not candidates:
            clip_dur = min(effective_dur, 45.0)
            candidates = [{
                "clip_id": "clip_1",
                "start_time": 0.0,
                "end_time": clip_dur,
                "duration": round(clip_dur, 2),
                "hook_score": 90.0,
                "hook_title": "HIGHLIGHT TERBAIK HARI INI",
                "text": transcript.get("full_text", "")[:200],
                "words": transcript.get("segments", [{}])[0].get("words", []),
                "hashtags": "#shorts #reels #viral #fyp"
            }]

        job["candidates"] = candidates
        job["clips"] = []

        # Step 4: Render 9:16 Shorts with dynamic captions & SFX
        total_cand = len(candidates)
        for idx, cand in enumerate(candidates):
            pct = 65 + int((idx / total_cand) * 32)
            job["step"] = f"Rendering Video Short {idx+1}/{total_cand} (9:16 + Dynamic Captions + SFX)..."
            job["progress"] = pct

            out_filename = f"{job_id}_{cand['clip_id']}.mp4"
            out_path = str(OUTPUTS_DIR / out_filename)

            clipper_engine.render_clip_to_9_16(
                source_video=video_path,
                clip_info=cand,
                output_mp4=out_path,
                niche=niche,
                custom_watermark=custom_watermark,
                add_sfx=True
            )

            job["clips"].append({
                "clip_id": cand["clip_id"],
                "filename": out_filename,
                "video_url": f"/outputs/{out_filename}",
                "title": cand["hook_title"],
                "score": cand["hook_score"],
                "duration": cand["duration"],
                "start": cand["start_time"],
                "end": cand["end_time"],
                "summary": cand["text"][:160] + "...",
                "hashtags": cand["hashtags"]
            })

        job["status"] = "completed"
        job["step"] = "Selesai! Video siap diunduh & diunggah."
        job["progress"] = 100

    except Exception as e:
        job["status"] = "error"
        job["error"] = str(e)
        job["step"] = f"Terjadi kesalahan: {str(e)}"


@app.get("/", response_class=HTMLResponse)
async def serve_gui():
    html_file = TEMPLATES_DIR / "index.html"
    if html_file.exists():
        return HTMLResponse(content=html_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Template not found</h1>", status_code=404)


@app.post("/api/start_job")
async def start_job(
    background_tasks: BackgroundTasks,
    video_file: Optional[UploadFile] = File(None),
    file_path: Optional[str] = Form(None),
    youtube_url: Optional[str] = Form(None),
    niche: str = Form("universal"),
    custom_watermark: Optional[str] = Form(None),
    model_size: str = Form("tiny"),
    scan_range: str = Form("15min"),
    num_clips: int = Form(3),
    min_dur: float = Form(25.0),
    max_dur: float = Form(60.0)
):
    job_id = str(uuid.uuid4())[:8]

    target_path = None
    if video_file and video_file.filename:
        safe_name = f"{job_id}_{video_file.filename}"
        save_dest = UPLOADS_DIR / safe_name
        with open(save_dest, "wb") as f:
            shutil.copyfileobj(video_file.file, f)
        target_path = str(save_dest)
    elif file_path and os.path.exists(file_path):
        target_path = file_path
    elif youtube_url and ("youtube.com" in youtube_url or "youtu.be" in youtube_url):
        target_path = None
    else:
        raise HTTPException(status_code=400, detail="Pilih file video, masukkan link YouTube, atau ketik path file lokal yang valid.")

    JOBS[job_id] = {
        "job_id": job_id,
        "video_path": target_path,
        "youtube_url": youtube_url,
        "niche": niche,
        "custom_watermark": custom_watermark,
        "status": "queued",
        "progress": 0,
        "step": "Menyiapkan antrean pemrosesan...",
        "clips": [],
        "error": None
    }

    background_tasks.add_task(
        process_video_pipeline,
        job_id=job_id,
        video_path=target_path,
        youtube_url=youtube_url,
        niche=niche,
        custom_watermark=custom_watermark,
        model_size=model_size,
        target_clips=num_clips,
        scan_range=scan_range,
        min_dur=min_dur,
        max_dur=max_dur
    )

    return {"ok": True, "job_id": job_id}


@app.get("/api/job_status/{job_id}")
async def get_job_status(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job ID tidak ditemukan.")
    return JOBS[job_id]


@app.get("/api/history")
async def get_history():
    files = list(OUTPUTS_DIR.glob("*.mp4"))
    results = []
    for f in sorted(files, key=lambda x: x.stat().st_mtime, reverse=True):
        results.append({
            "filename": f.name,
            "url": f"/outputs/{f.name}",
            "size_mb": round(f.stat().st_size / (1024 * 1024), 2),
            "date": f.stat().st_mtime
        })
    return {"clips": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
