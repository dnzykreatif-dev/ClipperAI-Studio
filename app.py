"""
ClipperAI Studio - Web Application (Universal Edition)
FastAPI Server providing Web GUI, REST APIs, YouTube Studio Automation,
and AI Viral SEO Research.
"""

import os
import uuid
import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import clipper_engine
import yt_seo_engine
import yt_uploader

app = FastAPI(title="ClipperAI Studio", version="2.5.0")

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


class YouTubeUploadPayload(BaseModel):
    filename: str
    title: str
    description: str
    tags: str
    category_id: str = "22"
    privacy_status: str = "public"
    made_for_kids: bool = False


def process_video_pipeline(
    job_id: str,
    video_path: Optional[str] = None,
    youtube_url: Optional[str] = None,
    niche: str = "universal",
    custom_watermark: Optional[str] = None,
    model_size: str = "base",
    target_clips: int = 3,
    scan_range: str = "15min",
    min_dur: float = 25.0,
    max_dur: float = 60.0
):
    job = JOBS[job_id]
    try:
        # Step 0: Download YouTube / Google Drive / Web video if requested
        if youtube_url and youtube_url.strip():
            job["status"] = "processing"
            job["step"] = "Mengunduh video dari sumber online (YouTube / Google Drive / Web)..."
            job["progress"] = 5

            def on_yt_progress(pct: int, msg: str):
                job["progress"] = pct
                job["step"] = msg

            downloaded_video = clipper_engine.download_remote_video(
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
            niche=niche,
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

        # Step 4: Render 9:16 Shorts with dynamic captions & SFX + Auto SEO Generation
        total_cand = len(candidates)
        for idx, cand in enumerate(candidates):
            pct = 65 + int((idx / total_cand) * 32)
            job["step"] = f"Rendering Video Short {idx+1}/{total_cand} (9:16 + Dynamic Zoom + SFX)..."
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

            # Auto-generate broadcast-grade YouTube SEO Package
            seo_package = yt_seo_engine.generate_shorts_seo_package(
                transcript_text=cand.get("text", ""),
                title_hint=cand.get("hook_title", ""),
                niche=niche,
                speaker=custom_watermark
            )

            seo_filename = f"{job_id}_{cand['clip_id']}_seo.json"
            seo_path = OUTPUTS_DIR / seo_filename
            try:
                with open(seo_path, "w", encoding="utf-8") as f:
                    json.dump(seo_package, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"[Warning] Failed to save SEO cache: {e}")

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
                "hashtags": cand["hashtags"],
                "seo": seo_package
            })

        job["status"] = "completed"
        job["step"] = "Selesai! Video siap diunduh & diunggah ke YouTube."
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
    model_size: str = Form("base"),
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
    elif youtube_url and (youtube_url.startswith("http://") or youtube_url.startswith("https://")):
        target_path = None
    else:
        raise HTTPException(status_code=400, detail="Pilih file video, masukkan link (YouTube / Google Drive / Web), atau ketik path file lokal yang valid.")

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
        seo_path = OUTPUTS_DIR / f"{f.stem}_seo.json"
        seo_data = None
        if seo_path.exists():
            try:
                with open(seo_path, "r", encoding="utf-8") as sf:
                    seo_data = json.load(sf)
            except Exception:
                pass

        results.append({
            "filename": f.name,
            "url": f"/outputs/{f.name}",
            "size_mb": round(f.stat().st_size / (1024 * 1024), 2),
            "date": f.stat().st_mtime,
            "seo": seo_data
        })
    return {"clips": results}


# =========================================================================
# YOUTUBE SEO & VIRAL RESEARCH APIS
# =========================================================================

@app.get("/api/research_trends")
async def research_trends(query: str = Query(..., min_length=1), niche: str = Query("universal")):
    """
    Scouts live real-time search autocomplete suggestions directly from YouTube.
    """
    data = yt_seo_engine.research_viral_keywords(topic=query, niche=niche, limit=15)
    return data


@app.get("/api/seo_metadata")
async def get_seo_metadata(
    filename: str = Query(...),
    niche: str = Query("universal"),
    speaker: Optional[str] = Query(None)
):
    """
    Retrieves or generates YouTube Shorts SEO package for a specific output clip.
    """
    base_name = Path(filename).stem
    seo_file = OUTPUTS_DIR / f"{base_name}_seo.json"

    if seo_file.exists():
        try:
            with open(seo_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    # Generate fresh package
    topic_hint = base_name.replace("_", " ").title()
    seo_pkg = yt_seo_engine.generate_shorts_seo_package(
        transcript_text=f"Pembahasan menarik seputar {topic_hint}. Simak penjelasannya sampai tuntas.",
        title_hint=topic_hint,
        niche=niche,
        speaker=speaker
    )

    # Cache for future use
    try:
        with open(seo_file, "w", encoding="utf-8") as f:
            json.dump(seo_pkg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    return seo_pkg


# =========================================================================
# YOUTUBE AUTOMATION & UPLOAD APIS
# =========================================================================

@app.get("/api/youtube/status")
async def youtube_status():
    """
    Returns the current Google OAuth connection status and channel information.
    """
    return yt_uploader.check_auth_status()


@app.post("/api/youtube/auth")
async def youtube_auth():
    """
    Initiates local browser OAuth flow to link creator's YouTube channel.
    """
    result = yt_uploader.authenticate_flow()
    return result


@app.post("/api/youtube/upload")
async def youtube_upload(payload: YouTubeUploadPayload):
    """
    Uploads a short video directly to YouTube with automated metadata.
    Supports files from outputs directory or direct local PC path.
    """
    # Check if absolute path or exists directly
    if os.path.isabs(payload.filename) and os.path.exists(payload.filename):
        video_path = Path(payload.filename)
    else:
        video_path = OUTPUTS_DIR / payload.filename
        if not video_path.exists():
            # Check uploads directory as well
            upl_path = UPLOADS_DIR / payload.filename
            if upl_path.exists():
                video_path = upl_path
            else:
                raise HTTPException(status_code=404, detail=f"File {payload.filename} tidak ditemukan.")

    tags_list = [t.strip() for t in payload.tags.split(",") if t.strip()]

    result = yt_uploader.upload_to_youtube(
        video_path=str(video_path),
        title=payload.title,
        description=payload.description,
        tags=tags_list,
        category_id=payload.category_id,
        privacy_status=payload.privacy_status,
        made_for_kids=payload.made_for_kids
    )

    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("error", "Gagal upload video."))

    return result


@app.post("/api/youtube/prepare_pc_video")
async def prepare_pc_video(
    video_file: Optional[UploadFile] = File(None),
    file_path: Optional[str] = Form(None),
    niche: str = Form("universal"),
    mode: str = Form("shorts")
):
    """
    Analyzes an existing video file from PC or cloud link (Google Drive / Web)
    and generates an automated viral SEO package (Shorts or Long Video) without cutting.
    """
    target_path = None
    if video_file and video_file.filename:
        safe_name = f"pc_direct_{uuid.uuid4().hex[:6]}_{video_file.filename}"
        save_dest = UPLOADS_DIR / safe_name
        with open(save_dest, "wb") as f:
            shutil.copyfileobj(video_file.file, f)
        target_path = str(save_dest)
        display_name = video_file.filename
    elif file_path and (file_path.startswith("http://") or file_path.startswith("https://")):
        # Remote link (Google Drive / Dropbox / Direct Web)
        downloaded = clipper_engine.download_remote_video(file_path.strip(), str(UPLOADS_DIR))
        target_path = downloaded
        display_name = Path(downloaded).name
    elif file_path and os.path.exists(file_path):
        target_path = file_path
        display_name = Path(file_path).name
    else:
        raise HTTPException(status_code=400, detail="File video lokal dari PC atau link cloud (Google Drive / Web) tidak ditemukan.")

    # Extract quick audio for transcription
    audio_path = str(UPLOADS_DIR / f"temp_pc_{uuid.uuid4().hex[:6]}.wav")
    try:
        clipper_engine.extract_audio(target_path, audio_path, max_duration=120.0)
        # Fast transcription with base model
        transcript = clipper_engine.transcribe_audio_with_progress(
            audio_path=audio_path,
            total_audio_dur=120.0,
            model_size="base",
            niche=niche,
            progress_callback=lambda p, m: None
        )
        full_text = transcript.get("full_text", "")
    except Exception as e:
        full_text = display_name.replace("_", " ").replace("-", " ")
    finally:
        if os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except Exception:
                pass

    # Generate viral SEO package (Shorts or Long-Form)
    seo_pkg = yt_seo_engine.generate_shorts_seo_package(
        transcript_text=full_text,
        title_hint=Path(display_name).stem.replace("_", " ").title(),
        niche=niche,
        mode=mode
    )

    return {
        "ok": True,
        "video_path": target_path,
        "filename": display_name,
        "mode": mode,
        "seo": seo_pkg
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
