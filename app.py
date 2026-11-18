"""
ClipperAI Studio - Web Application (Universal Edition)
FastAPI Server providing Web GUI, REST APIs, YouTube Studio Automation,
and AI Viral SEO Research.
"""

import os
import uuid
import json
import shutil
from datetime import datetime
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
import course_sync
import faceless_engine
import ai_brain
import thumbnail_engine
import social_poster
import automation_bridge
import studio_presets
import motion_code_engine
import rea_video_bigdata

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
ASSETS_DIR = BASE_DIR / "assets"
MOTIONCODE_DIR = BASE_DIR / "motioncode_studio"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
MOTIONCODE_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")
app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")
app.mount("/motioncode", StaticFiles(directory=str(MOTIONCODE_DIR), html=True), name="motioncode")

JOBS: Dict[str, Dict[str, Any]] = {}


class YouTubeUploadPayload(BaseModel):
    filename: str
    title: str
    description: str
    tags: str
    category_id: str = "22"
    privacy_status: str = "public"
    made_for_kids: bool = False


class SocialPublishPayload(BaseModel):
    filename: str
    title: str
    caption: str
    tags: str = ""
    platforms: List[str] = ["youtube", "facebook", "tiktok"]
    privacy: str = "public"


class YouTubeKeysPayload(BaseModel):
    client_id: str
    client_secret: str


class FacebookConfigPayload(BaseModel):
    page_id: str
    access_token: str


class TikTokConfigPayload(BaseModel):
    access_token: str
    username: Optional[str] = None


class GDriveUploadPayload(BaseModel):
    filename: str
    folder_id: str
    chrome_profile: Optional[str] = None
    headless: bool = True


class ADBPairPayload(BaseModel):
    ip: str
    port: str
    code: str


class ADBConnectPayload(BaseModel):
    target: Optional[str] = ""


class ADBShopeePayload(BaseModel):
    filename: str
    caption: str
    product_query: Optional[str] = ""
    target_ip: Optional[str] = ""


class SeamlessLoopPayload(BaseModel):
    filename: str
    target_duration: float = 30.0
    overlap_sec: float = 1.0


class HookOverlayPayload(BaseModel):
    filename: str
    hook_text: str
    duration: float = 4.0


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
    max_dur: float = 60.0,
    intensity: str = "normal",
    subtitle_size: str = "small",
    watermark_image: Optional[str] = None,
    watermark_pos: str = "top_right"
):
    job = JOBS[job_id]
    try:
        # Inisialisasi status alur kerja (Workflow 1-7 sesuai Galih Pranowo)
        job["workflow"] = {
            "transcript": "pending",
            "viral_scout": "pending",
            "silence_cut": "pending",
            "face_crop": "pending",
            "subtitles": "pending",
            "loudnorm": "pending",
            "ready": "pending"
        }

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
        job["workflow"]["transcript"] = "running"
        job["step"] = f"1. Transkrip: Mengekstrak audio (16kHz mono)... [Durasi: {int(effective_dur//60)} menit]"
        job["progress"] = 15

        audio_path = str(UPLOADS_DIR / f"{job_id}_audio.wav")
        clipper_engine.extract_audio(video_path, audio_path, max_duration=max_extract)

        # Step 1: High-Speed Multi-Threaded Whisper Transcription
        def on_transcribe_progress(pct: int, msg: str):
            job["progress"] = pct
            job["step"] = f"1. Transkrip kata-per-kata: {msg}"

        transcript = clipper_engine.transcribe_audio_with_progress(
            audio_path=audio_path,
            total_audio_dur=effective_dur,
            model_size=model_size,
            niche=niche,
            progress_callback=on_transcribe_progress
        )
        job["transcript"] = transcript
        job["workflow"]["transcript"] = "done"

        # Step 2: Viral Hook Scouting with Niche Awareness
        job["workflow"]["viral_scout"] = "running"
        job["step"] = f"2. AI Viral Scout sedang menganalisis & memilih momen paling viral ({niche.title()})..."
        job["progress"] = 62

        candidates = clipper_engine.find_viral_clips(
            transcript,
            niche=niche,
            min_duration=min_dur,
            max_duration=max_dur,
            top_k=target_clips
        )
        job["workflow"]["viral_scout"] = "done"

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

        # Step 3: Suruh AI edit (Jeda kosong terbuang, Crop 9:16 ikutin wajah, Subtitle per kata, Suara rata -14 LUFS)
        total_cand = len(candidates)
        for idx, cand in enumerate(candidates):
            pct_base = 65 + int((idx / total_cand) * 30)
            job["step"] = f"3. Suruh AI edit klip {idx+1}/{total_cand}..."
            job["progress"] = pct_base

            def on_render_subtask(task_key: str, msg: str):
                wf = job.get("workflow", {})
                if task_key == "silence_cut":
                    wf["silence_cut"] = "running"
                elif task_key == "face_crop":
                    wf["silence_cut"] = "done"
                    wf["face_crop"] = "running"
                elif task_key == "subtitles":
                    wf["silence_cut"] = "done"
                    wf["face_crop"] = "done"
                    wf["subtitles"] = "running"
                elif task_key == "loudnorm":
                    wf["silence_cut"] = "done"
                    wf["face_crop"] = "done"
                    wf["subtitles"] = "done"
                    wf["loudnorm"] = "running"
                job["step"] = f"3. Suruh AI edit ({idx+1}/{total_cand}): {msg}"

            out_filename = f"{job_id}_{cand['clip_id']}.mp4"
            out_path = str(OUTPUTS_DIR / out_filename)

            clipper_engine.render_clip_to_9_16(
                source_video=video_path,
                clip_info=cand,
                output_mp4=out_path,
                niche=niche,
                custom_watermark=custom_watermark,
                add_sfx=True,
                intensity=intensity,
                subtitle_size=subtitle_size,
                watermark_image=watermark_image,
                watermark_pos=watermark_pos,
                progress_callback=on_render_subtask
            )

            # Auto-generate broadcast-grade YouTube SEO Package (gunakan hasil AI Curation jika sudah ada)
            if cand.get("ai_seo"):
                seo_package = cand["ai_seo"]
            else:
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

            thumb_name = f"{Path(out_filename).stem}_thumb.jpg"
            thumb_url = f"/outputs/{thumb_name}" if (OUTPUTS_DIR / thumb_name).exists() else None

            job["clips"].append({
                "clip_id": cand["clip_id"],
                "filename": out_filename,
                "video_url": f"/outputs/{out_filename}",
                "thumb_url": thumb_url,
                "title": cand["hook_title"],
                "score": cand["hook_score"],
                "duration": cand["duration"],
                "start": cand["start_time"],
                "end": cand["end_time"],
                "summary": cand["text"][:160] + "...",
                "hashtags": cand["hashtags"],
                "seo": seo_package,
                "edl": cand.get("edl")
            })

        job["workflow"]["silence_cut"] = "done"
        job["workflow"]["face_crop"] = "done"
        job["workflow"]["subtitles"] = "done"
        job["workflow"]["loudnorm"] = "done"
        job["workflow"]["ready"] = "done"
        job["status"] = "completed"
        job["step"] = "Selesai! Klip langsung siap ditonton & diunggah."
        job["progress"] = 100

    except Exception as e:
        job["status"] = "error"
        job["error"] = str(e)
        job["step"] = f"Terjadi kesalahan: {str(e)}"


def process_faceless_job(
    job_id: str,
    script_text: str,
    voice_key: str = "ardi",
    theme_key: str = "anymotion",
    header_title: Optional[str] = None,
    storyboard: Optional[Dict[str, Any]] = None
):
    job = JOBS[job_id]
    try:
        def on_progress(pct: int, msg: str):
            job["progress"] = pct
            job["step"] = msg

        out_filename = f"faceless_{job_id[:8]}.mp4"
        out_path = str(OUTPUTS_DIR / out_filename)

        res = faceless_engine.render_faceless_video(
            script_text=script_text,
            output_mp4=out_path,
            voice_key=voice_key,
            theme_key=theme_key,
            header_title=header_title,
            progress_callback=on_progress,
            storyboard=storyboard
        )

        seo_res = res.get("seo", {})

        # Generate thumbnail otomatis untuk video faceless
        thumb_name = f"{Path(out_filename).stem}_thumb.jpg"
        thumb_dest = str(OUTPUTS_DIR / thumb_name)
        try:
            import thumbnail_engine
            thumbnail_engine.generate_thumbnail(
                video_path=out_path,
                output_jpg=thumb_dest,
                headline=seo_res.get("thumbnail_text", header_title or "VIRAL SHORTS"),
                niche="universal"
            )
        except Exception as te:
            print(f"[Warning] Failed to generate faceless thumbnail: {te}")

        thumb_url = f"/outputs/{thumb_name}" if (OUTPUTS_DIR / thumb_name).exists() else None

        job["clips"] = [{
            "clip_id": f"faceless_{job_id[:6]}",
            "filename": out_filename,
            "video_url": f"/outputs/{out_filename}",
            "thumb_url": thumb_url,
            "title": seo_res.get("title", header_title or "AI Faceless Shorts"),
            "score": 99.2,
            "duration": res.get("duration", 15.0),
            "start": 0.0,
            "end": res.get("duration", 15.0),
            "summary": script_text[:160] + ("..." if len(script_text) > 160 else ""),
            "hashtags": " ".join(seo_res.get("tags", ["#shorts", "#faceless", "#viral"])),
            "seo": seo_res,
            "qa_montage_url": res.get("qa_montage_url")
        }]
        job["status"] = "completed"
        job["step"] = "Selesai! Video Faceless siap ditonton & diunggah ke YouTube."
        job["progress"] = 100

    except Exception as e:
        job["status"] = "error"
        job["error"] = str(e)
        job["step"] = f"Terjadi kesalahan render faceless: {str(e)}"


class FacelessPayload(BaseModel):
    script_text: str
    voice_key: str = "ardi"
    theme_key: str = "anymotion"
    header_title: Optional[str] = None
    storyboard: Optional[Dict[str, Any]] = None


class StoryboardRequest(BaseModel):
    script_text: str
    theme_key: str = "anymotion"
    header_title: Optional[str] = None


@app.get("/api/faceless/presets")
async def get_faceless_presets():
    """Returns available voices and themes for AI Faceless Video Maker."""
    return {
        "voices": faceless_engine.VOICES,
        "themes": faceless_engine.THEMES
    }


@app.post("/api/faceless/storyboard")
async def plan_faceless_storyboard(req: StoryboardRequest):
    """
    Rancangan Storyboard AI (Visual Director) sebelum render:
    Memecah naskah menjadi deck adegan visual AnyMotion / Vox yang bisa ditinjau & diedit pengguna.
    """
    text = req.script_text.strip()
    if not text or len(text) < 5:
        raise HTTPException(status_code=400, detail="Teks naskah terlalu pendek (minimal 5 karakter).")

    import ai_director
    theme = faceless_engine.THEMES.get(req.theme_key, faceless_engine.THEMES["anymotion"])
    palette_hint = theme.get("theme_palette", "mint")

    import asyncio
    sb = await asyncio.to_thread(ai_director.direct_visual_storyboard, text, theme_hint=palette_hint)
    return {
        "ok": True,
        "storyboard": sb,
        "theme_key": req.theme_key
    }


@app.post("/api/faceless/generate")
async def generate_faceless(payload: FacelessPayload, background_tasks: BackgroundTasks):
    """
    Starts an AI Faceless Video generation pipeline from raw text/script or pre-approved storyboard.
    """
    text = payload.script_text.strip()
    if not text or len(text) < 5:
        raise HTTPException(status_code=400, detail="Teks naskah terlalu pendek (minimal 5 karakter).")

    job_id = str(uuid.uuid4())
    JOBS[job_id] = {
        "id": job_id,
        "status": "queued",
        "progress": 5,
        "step": "Menyiapkan mesin AI Faceless...",
        "created_at": datetime.now().isoformat(),
        "type": "faceless"
    }

    background_tasks.add_task(
        process_faceless_job,
        job_id=job_id,
        script_text=text,
        voice_key=payload.voice_key,
        theme_key=payload.theme_key,
        header_title=payload.header_title,
        storyboard=payload.storyboard
    )

    return {"ok": True, "job_id": job_id}


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
    max_dur: float = Form(60.0),
    intensity: str = Form("normal"),
    subtitle_size: str = Form("small"),
    watermark_image: Optional[str] = Form(None),
    watermark_pos: str = Form("top_right")
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
        "subtitle_size": subtitle_size,
        "watermark_pos": watermark_pos,
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
        max_dur=max_dur,
        intensity=intensity,
        subtitle_size=subtitle_size,
        watermark_image=watermark_image,
        watermark_pos=watermark_pos
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

        edl_path = OUTPUTS_DIR / f"{f.stem}.edl.json"
        edl_data = None
        if edl_path.exists():
            try:
                with open(edl_path, "r", encoding="utf-8") as ef:
                    edl_data = json.load(ef)
            except Exception:
                pass

        thumb_file = OUTPUTS_DIR / f"{f.stem}_thumb.jpg"
        results.append({
            "filename": f.name,
            "url": f"/outputs/{f.name}",
            "thumb_url": f"/outputs/{thumb_file.name}" if thumb_file.exists() else None,
            "size_mb": round(f.stat().st_size / (1024 * 1024), 2),
            "date": f.stat().st_mtime,
            "seo": seo_data,
            "edl": edl_data
        })
    return {"clips": results}


@app.delete("/api/history/{filename}")
async def delete_history_item(filename: str):
    """Hapus 1 video dari riwayat outputs beserta file metadata terkait."""
    safe_name = Path(filename).name
    stem = Path(safe_name).stem
    removed = []
    for ext in [".mp4", "_seo.json", ".edl.json", ".qa.jpg", "_thumb.jpg"]:
        target = OUTPUTS_DIR / f"{stem}{ext}"
        if target.exists():
            try:
                target.unlink()
                removed.append(target.name)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Gagal menghapus {target.name}: {e}")
    return {"ok": True, "removed": removed}


@app.post("/api/history/clear")
async def clear_all_history(clean_uploads: bool = Query(False)):
    """Bersihkan seluruh riwayat video di folder outputs/ (dan opsional uploads/temp)."""
    removed_count = 0
    for f in OUTPUTS_DIR.glob("*"):
        if f.is_file() and f.suffix.lower() in (".mp4", ".json", ".jpg", ".png", ".ass"):
            try:
                f.unlink()
                removed_count += 1
            except Exception:
                pass

    temp_dir = UPLOADS_DIR / "temp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)
        temp_dir.mkdir(parents=True, exist_ok=True)

    if clean_uploads:
        for uf in UPLOADS_DIR.glob("*"):
            if uf.is_file():
                try:
                    uf.unlink()
                except Exception:
                    pass

    JOBS.clear()
    return {"ok": True, "removed_files": removed_count}


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


# =========================================================================
# MULTI-PLATFORM SOCIAL MEDIA ENDPOINTS (YOUTUBE, TIKTOK, FACEBOOK REELS)
# =========================================================================

@app.get("/api/social/status")
async def get_social_account_status():
    """
    Returns unified connection status for YouTube, Facebook, and TikTok.
    """
    return social_poster.get_social_status()


@app.post("/api/social/youtube_keys")
async def save_yt_keys_endpoint(payload: YouTubeKeysPayload):
    """
    Saves Client ID & Client Secret directly to client_secrets.json.
    """
    res = social_poster.save_youtube_keys(payload.client_id, payload.client_secret)
    if not res.get("ok"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res


@app.post("/api/social/youtube_secrets_file")
async def save_yt_secrets_file_endpoint(file: UploadFile = File(...)):
    """
    Accepts client_secrets.json uploaded directly from browser.
    """
    try:
        content = await file.read()
        res = social_poster.save_youtube_secrets_file(content.decode("utf-8"))
        if not res.get("ok"):
            raise HTTPException(status_code=400, detail=res.get("error"))
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Gagal membaca file: {str(e)}")


@app.post("/api/social/facebook_config")
async def save_fb_config_endpoint(payload: FacebookConfigPayload):
    """
    Validates and saves Facebook Page ID & Access Token.
    """
    res = social_poster.save_facebook_config(payload.page_id, payload.access_token)
    if not res.get("ok"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res


@app.post("/api/social/tiktok_config")
async def save_tt_config_endpoint(payload: TikTokConfigPayload):
    """
    Saves TikTok Access Token & Username.
    """
    res = social_poster.save_tiktok_config(payload.access_token, payload.username)
    if not res.get("ok"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res


@app.post("/api/social/publish")
async def publish_social_all(payload: SocialPublishPayload):
    """
    One-Click Cross-Post to all selected platforms (YouTube Shorts, TikTok, Facebook Reels).
    """
    # Locate video file
    if os.path.isabs(payload.filename) and os.path.exists(payload.filename):
        video_path = Path(payload.filename)
    else:
        video_path = OUTPUTS_DIR / payload.filename
        if not video_path.exists():
            upl_path = UPLOADS_DIR / payload.filename
            if upl_path.exists():
                video_path = upl_path
            else:
                raise HTTPException(status_code=404, detail=f"File {payload.filename} tidak ditemukan.")

    tags_list = [t.strip() for t in payload.tags.split(",") if t.strip()]

    result = social_poster.publish_to_all_platforms(
        video_path=str(video_path),
        title=payload.title,
        caption=payload.caption,
        tags=tags_list,
        platforms=payload.platforms,
        privacy=payload.privacy
    )
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
        # Remote link (Google Drive / Google Photos / Dropbox / Direct Web)
        try:
            downloaded = clipper_engine.download_remote_video(file_path.strip(), str(UPLOADS_DIR))
        except Exception as dl_err:
            raise HTTPException(status_code=400, detail=str(dl_err))
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


class CourseSyncPayload(BaseModel):
    course_slug: str
    module_id: str
    title: str
    video_url: str
    summary_text: str
    timestamps_text: Optional[str] = None


@app.get("/api/course/catalog")
async def get_course_catalog():
    """
    Returns the live or cached list of Courses and Modules from Web dnzykreatif.
    """
    return course_sync.fetch_course_catalog()


@app.post("/api/course/sync_lesson")
async def sync_course_lesson(payload: CourseSyncPayload):
    """
    Directly appends a new lesson into Web dnzykreatif's Google Spreadsheet database.
    """
    result = course_sync.append_lesson_to_database(
        course_slug=payload.course_slug,
        module_id=payload.module_id,
        title=payload.title,
        video_url=payload.video_url,
        summary_text=payload.summary_text,
        timestamps_text=payload.timestamps_text
    )
    return result


class AIConfigPayload(BaseModel):
    enabled: bool = True
    provider: str = "gemini"
    base_url: Optional[str] = None
    model: Optional[str] = None
    api_keys: Any = None
    active_key_index: int = 0
    auto_rotate_on_limit: bool = True


class AIModelsQueryPayload(BaseModel):
    provider: str = "gemini"
    base_url: Optional[str] = None
    api_key: Optional[str] = None


class AIIdeasPayload(BaseModel):
    topic: str
    style: str = "fakta"
    duration_sec: int = 35


class ThumbnailRegenPayload(BaseModel):
    filename: str
    headline: str
    sub_badge: Optional[str] = None
    niche: str = "universal"


@app.get("/api/ai/config")
async def get_ai_config():
    """Mengambil status & konfigurasi Multi-Provider AI Router (Gemini / SumoPod / 9Router / dll)."""
    return ai_brain.get_public_status()


@app.post("/api/ai/config")
async def update_ai_config(payload: AIConfigPayload):
    """Menyimpan konfigurasi AI Provider, Model, dan daftar Multi-API Key."""
    ai_brain.save_config(payload.dict())
    return {"ok": True, "status": ai_brain.get_public_status()}


@app.post("/api/ai/models")
async def list_ai_models(payload: AIModelsQueryPayload):
    """Menarik daftar model yang tersedia langsung dari provider (Gemini / SumoPod / 9Router / OpenRouter)."""
    models = ai_brain.fetch_available_models(
        provider=payload.provider,
        base_url=payload.base_url,
        api_key=payload.api_key,
    )
    return {"ok": True, "models": models}


@app.post("/api/ai/test")
async def test_ai_router():
    """Menguji koneksi AI dengan provider, model, dan API key aktif."""
    try:
        res = ai_brain.test_ai_connection()
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/ai/ideas")
async def generate_ai_ideas(payload: AIIdeasPayload):
    """Membuat naskah & ide konten viral menggunakan AI (atau fallback lokal cerdas jika offline/key invalid)."""
    ai_res = ai_brain.generate_script_or_ideas_with_ai(
        topic=payload.topic,
        style=payload.style,
        duration_sec=payload.duration_sec,
    )
    if ai_res:
        return {"ok": True, "ai_generated": True, **ai_res}
    rich_pkg = faceless_engine.generate_rich_topic_package(
        topic=payload.topic,
        style=payload.style,
        duration_sec=payload.duration_sec,
    )
    return {
        "ok": True,
        "ai_generated": False,
        "header_title": rich_pkg["header_title"],
        "thumbnail_text": rich_pkg["thumbnail_text"],
        "script": rich_pkg["script"],
        "ideas": rich_pkg["ideas"],
    }


@app.post("/api/thumbnail/regenerate")
async def regenerate_clip_thumbnail(payload: ThumbnailRegenPayload):
    """Merender ulang thumbnail ber-CTR tinggi dengan teks custom atau AI."""
    safe_name = Path(payload.filename).name
    video_path = OUTPUTS_DIR / safe_name
    if not video_path.exists():
        raise HTTPException(status_code=404, detail=f"Video {safe_name} tidak ditemukan.")
    thumb_name = f"{video_path.stem}_thumb.jpg"
    thumb_path = OUTPUTS_DIR / thumb_name
    thumbnail_engine.generate_thumbnail(
        video_path=str(video_path),
        output_jpg=str(thumb_path),
        headline=payload.headline,
        sub_badge=payload.sub_badge,
        niche=payload.niche,
    )
    return {"ok": True, "thumb_url": f"/outputs/{thumb_name}?t={int(datetime.now().timestamp())}"}


# ==============================================================================
# CLIPPERAI REMOTE & MOBILE AUTOMATION SUITE (REMOTE TUNNEL, GDRIVE, WIRELESS ADB, LOOPER)
# ==============================================================================

@app.post("/api/remote/tunnel/start")
async def start_remote_tunnel():
    """Aktivasi Cloudflare Quick Tunnel untuk remote access dari smartphone."""
    res = automation_bridge.start_cloudflare_tunnel(port_local=8000)
    return {"ok": True, "tunnel": res}


@app.post("/api/remote/tunnel/stop")
async def stop_remote_tunnel():
    """Menghentikan Cloudflare Quick Tunnel."""
    res = automation_bridge.stop_cloudflare_tunnel()
    return {"ok": True, "tunnel": res}


@app.get("/api/remote/tunnel/status")
async def get_remote_tunnel_status():
    """Mengecek status dan URL publik Cloudflare Quick Tunnel."""
    res = automation_bridge.get_cloudflare_tunnel_status()
    return {"ok": True, "tunnel": res}


@app.post("/api/cloud/gdrive/upload")
async def upload_gdrive_session(payload: GDriveUploadPayload):
    """Mengunggah video ke Folder Google Drive via sesi login Chrome (Tanpa API Key)."""
    safe_name = Path(payload.filename).name
    video_path = OUTPUTS_DIR / safe_name
    if not video_path.exists():
        video_path = UPLOADS_DIR / safe_name
    if not video_path.exists():
        raise HTTPException(status_code=404, detail=f"File {safe_name} tidak ditemukan.")

    success = automation_bridge.upload_via_chrome_ke_folder_gdrive(
        path_file=str(video_path),
        folder_id=payload.folder_id,
        profil_chrome_target=payload.chrome_profile,
        headless=payload.headless
    )
    if not success:
        raise HTTPException(status_code=500, detail="Gagal mengunggah ke Google Drive via sesi Chrome.")
    return {"ok": True, "message": f"'{safe_name}' berhasil diunggah ke Google Drive."}


@app.get("/api/mobile/adb/status")
async def get_adb_status():
    """Mengecek ketersediaan ADB dan daftar perangkat Android yang terhubung."""
    conn = automation_bridge.connect_adb()
    return {"ok": True, "adb": conn}


@app.post("/api/mobile/adb/pair")
async def pair_android_adb(payload: ADBPairPayload):
    """Pairing nirkabel 1x (Sekali Saja) ke HP Android 11+ via Wi-Fi."""
    res = automation_bridge.pair_adb_wireless(payload.ip, payload.port, payload.code)
    return {"ok": res.get("success", False), "result": res}


@app.post("/api/mobile/adb/connect")
async def connect_android_adb(payload: ADBConnectPayload):
    """Menghubungkan ke HP Android secara nirkabel (IP:Port) atau USB."""
    res = automation_bridge.connect_adb(payload.target)
    return {"ok": res.get("success", False), "result": res}


@app.post("/api/mobile/adb/upload_shopee")
async def upload_to_shopee_via_adb(payload: ADBShopeePayload):
    """Mentransfer video ke Galeri HP dan memandu auto-upload Shopee Video via ADB."""
    safe_name = Path(payload.filename).name
    video_path = OUTPUTS_DIR / safe_name
    if not video_path.exists():
        video_path = UPLOADS_DIR / safe_name
    if not video_path.exists():
        raise HTTPException(status_code=404, detail=f"File {safe_name} tidak ditemukan.")

    # Hubungkan ADB
    conn = automation_bridge.connect_adb(payload.target_ip)
    if not conn.get("success"):
        raise HTTPException(status_code=400, detail="Tidak ada HP Android terhubung via ADB.")

    dev_id = conn["device_id"]

    # 1. Transfer video ke HP Android DCIM/Camera
    rc_push, out_push = automation_bridge.run_adb_cmd(["-s", dev_id, "push", str(video_path), "/sdcard/DCIM/Camera/"])
    if rc_push != 0:
        raise HTTPException(status_code=500, detail=f"Gagal transfer video ke HP: {out_push}")

    # 2. Trigger Media Scanner agar langsung muncul di Galeri HP
    remote_path = f"/sdcard/DCIM/Camera/{safe_name}"
    automation_bridge.run_adb_cmd([
        "-s", dev_id, "shell", "am", "broadcast",
        "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
        "-d", f"file://{remote_path}"
    ])

    # 3. Salin caption & hashtags ke clipboard HP Android
    if payload.caption:
        automation_bridge.set_clipboard_and_paste_adb(dev_id, payload.caption)

    return {
        "ok": True,
        "device_id": dev_id,
        "message": f"Video '{safe_name}' berhasil ditransfer ke Galeri HP Android & Caption telah disalin ke Clipboard!"
    }


@app.post("/api/video/seamless_loop")
async def render_seamless_video_loop(payload: SeamlessLoopPayload):
    """Merender perulangan video mulus (Cross-fade Alpha) tanpa jump-cut."""
    safe_name = Path(payload.filename).name
    video_path = OUTPUTS_DIR / safe_name
    if not video_path.exists():
        video_path = UPLOADS_DIR / safe_name
    if not video_path.exists():
        raise HTTPException(status_code=404, detail=f"File {safe_name} tidak ditemukan.")

    out_name = f"{video_path.stem}_loop_{int(payload.target_duration)}s.mp4"
    out_path = OUTPUTS_DIR / out_name

    ok = automation_bridge.create_seamless_loop(
        input_path=str(video_path),
        output_path=str(out_path),
        target_duration_sec=payload.target_duration,
        overlap_sec=payload.overlap_sec
    )
    if not ok:
        raise HTTPException(status_code=500, detail="Gagal merender seamless video loop.")

    return {
        "ok": True,
        "output_filename": out_name,
        "download_url": f"/outputs/{out_name}"
    }


@app.post("/api/video/hook_overlay")
async def render_high_contrast_hook(payload: HookOverlayPayload):
    """Menempelkan banner Hook berdaya pikat tinggi di bagian atas video (Shorts / Reels)."""
    safe_name = Path(payload.filename).name
    video_path = OUTPUTS_DIR / safe_name
    if not video_path.exists():
        video_path = UPLOADS_DIR / safe_name
    if not video_path.exists():
        raise HTTPException(status_code=404, detail=f"File {safe_name} tidak ditemukan.")

    out_name = f"{video_path.stem}_hooked.mp4"
    out_path = OUTPUTS_DIR / out_name

    res = automation_bridge.overlay_high_contrast_hook(
        video_path=str(video_path),
        hook_text=payload.hook_text,
        output_path=str(out_path),
        durasi_tampil_detik=payload.duration
    )
    if not res:
        raise HTTPException(status_code=500, detail="Gagal menempelkan banner hook.")

    return {
        "ok": True,
        "output_filename": out_name,
        "download_url": f"/outputs/{out_name}"
    }


# ==============================================================================
# STUDIO PRESETS & ARMAGICFLOW EXTENSIONS
# ==============================================================================

class StudioPromptPayload(BaseModel):
    preset_type: str
    params: Dict[str, Any] = {}


class HookCaptionPayload(BaseModel):
    topic: str
    niche: str = "Umum"
    formula: str = "campuran_terbaik"
    tone: str = "Santai"


class StoryboardScriptPayload(BaseModel):
    product_or_topic: str
    duration_sec: int = 30
    kinetic_style: str = "Bold Impact"
    niche: str = "Umum"


class TikTokExtractPayload(BaseModel):
    url: str


@app.get("/api/studio/presets")
async def get_studio_presets():
    """Mengembalikan katalog master preset AI Visual & Storyboard."""
    return {"ok": True, "catalog": studio_presets.STUDIO_CATALOG}


@app.post("/api/studio/generate-prompt")
async def generate_studio_master_prompt(payload: StudioPromptPayload):
    """Menyusun master prompt berdasarkan parameter preset terpilih."""
    p = payload.params
    pt = payload.preset_type.lower()
    
    if pt == "thumbnail":
        prompt = studio_presets.build_thumbnail_prompt(
            headline=p.get("headline", ""),
            subheadline=p.get("subheadline", ""),
            ratio=p.get("ratio", "16:9"),
            visual_style=p.get("visual_style", "high_ctr_commercial"),
            typo_style=p.get("typo_style", "bold_3d_bevel"),
            subject_theme=p.get("subject_theme", "")
        )
    elif pt == "product_studio":
        prompt = studio_presets.build_product_studio_prompt(
            product_name=p.get("product_name", ""),
            backdrop=p.get("backdrop", "white_marble"),
            lighting=p.get("lighting", "softbox"),
            extra_details=p.get("extra_details", ""),
            has_ref_image=p.get("has_ref_image", False)
        )
    elif pt == "kuliner_umkm":
        prompt = studio_presets.build_kuliner_umkm_prompt(
            dish_name=p.get("dish_name", ""),
            serving_effect=p.get("serving_effect", "uap_panas"),
            camera_angle=p.get("camera_angle", "hero_45"),
            extra_details=p.get("extra_details", ""),
            has_ref_image=p.get("has_ref_image", False)
        )
    elif pt == "figurine_3d":
        prompt = studio_presets.build_figurine_3d_prompt(
            character_desc=p.get("character_desc", ""),
            toy_style=p.get("toy_style", "pop_mart"),
            packaging=p.get("packaging", "creator_desk"),
            material=p.get("material", "Smooth matte vinyl with gloss highlights"),
            extra_details=p.get("extra_details", ""),
            has_ref_image=p.get("has_ref_image", False)
        )
    elif pt == "virtual_tryon":
        prompt = studio_presets.build_virtual_tryon_prompt(
            garment_description=p.get("garment_description", ""),
            custom_notes=p.get("custom_notes", "")
        )
    elif pt == "banner_promo":
        prompt = studio_presets.build_banner_promo_prompt(
            business_name=p.get("business_name", ""),
            promo_text=p.get("promo_text", ""),
            format_type=p.get("format_type", "social_square"),
            color_scheme=p.get("color_scheme", "Kuning Merah Berani"),
            extra_details=p.get("extra_details", ""),
            has_ref_image=p.get("has_ref_image", False)
        )
    elif pt == "desain_rumah":
        prompt = studio_presets.build_desain_rumah_prompt(
            room_type=p.get("room_type", "Ruang Tamu"),
            interior_style=p.get("interior_style", "japandi"),
            lighting=p.get("lighting", "Daylight natural sunlight"),
            extra_details=p.get("extra_details", "")
        )
    elif pt == "character_sheet":
        prompt = studio_presets.build_character_sheet_prompt(
            character_name=p.get("character_name", ""),
            character_description=p.get("character_description", ""),
            visual_style=p.get("visual_style", "3D Pixar Animation"),
            costume=p.get("costume", "Casual modern streetwear")
        )
    else:
        raise HTTPException(status_code=400, detail=f"Preset type '{payload.preset_type}' belum didukung.")
        
    return {"ok": True, "tool_type": payload.preset_type, "prompt": prompt}


@app.post("/api/studio/hook-caption")
async def generate_hook_and_caption(payload: HookCaptionPayload):
    """Menghasilkan 10 Hooks + Caption + CTA + Hashtags menggunakan AI Brain."""
    sys_prompt = studio_presets.build_hook_caption_system_prompt(
        topic=payload.topic,
        niche=payload.niche,
        formula=payload.formula,
        tone=payload.tone
    )
    user_prompt = f"Hasilkan 10 hooks + caption + cta + hashtags untuk topik: '{payload.topic}', kategori: '{payload.niche}'."

    if ai_brain.is_ai_ready():
        try:
            raw_res = ai_brain.generate_text(sys_prompt, user_prompt, json_mode=True, timeout=60)
            parsed = ai_brain.extract_json(raw_res)
            if parsed and isinstance(parsed, dict) and "hooks" in parsed:
                return {"ok": True, "data": parsed, "generated_by": "ai"}
        except Exception:
            pass

    # Fallback template responsif jika API key AI belum diinput
    return {
        "ok": True,
        "data": {
            "hooks": [
                f"Jangan tonton video ini kalau kamu masih belum tahu rahasia {payload.topic}!",
                f"90% orang keliru saat membahas {payload.topic}, padahal caranya simpel banget...",
                f"Ini dia 1 trik tentang {payload.topic} yang jarang dibongkar para ahli!",
                f"Pernah kepikiran gak, kenapa {payload.topic} bisa berdampak sebesar ini?",
                f"Hentikan kebiasaan lama kamu! Coba pahami {payload.topic} dari sudut pandang ini.",
                f"Ternyata cuma butuh 1 menit buat menguasai konsep dasar {payload.topic}!",
                f"Kalau kamu mau hasil maksimal di bidang {payload.niche}, pahami {payload.topic} sekarang.",
                f"Trik tersembunyi {payload.topic} yang bakal bikin kamu geleng-geleng kepala!",
                f"Fakta mengejutkan tentang {payload.topic} yang baru terungkap minggu ini!",
                f"Simpan video ini sekarang, karena rahasia {payload.topic} ini jarang dibagikan gratis!"
            ],
            "caption": f"Banyak yang belum sadar pentingnya {payload.topic}. Padahal kalau dipraktikkan dengan konsisten, hasilnya luar biasa. Yuk tonton sampai selesai dan terapkan tips di atas!",
            "cta": "Save video ini biar gak lupa dan share ke teman kamu yang butuh!",
            "hashtags": f"#{payload.topic.replace(' ', '')} #{payload.niche.replace(' ', '')} #ViralTips #BelajarCepat #FYPIndonesia #EdukasiViral"
        },
        "system_prompt": sys_prompt,
        "generated_by": "template_fallback"
    }


@app.post("/api/studio/storyboard-script")
async def generate_storyboard_script(payload: StoryboardScriptPayload):
    """Menghasilkan script multi-part scene dan kinetic typography words."""
    sys_prompt = studio_presets.build_storyboard_script_prompt(
        product_or_topic=payload.product_or_topic,
        duration_sec=payload.duration_sec,
        kinetic_style=payload.kinetic_style,
        niche=payload.niche
    )
    user_prompt = f"Susun naskah video {payload.duration_sec} detik untuk: '{payload.product_or_topic}'."

    if ai_brain.is_ai_ready():
        try:
            raw_res = ai_brain.generate_text(sys_prompt, user_prompt, json_mode=True, timeout=60)
            parsed = ai_brain.extract_json(raw_res)
            if parsed and isinstance(parsed, dict) and "narasi" in parsed:
                return {"ok": True, "data": parsed, "generated_by": "ai"}
        except Exception:
            pass

    return {
        "ok": True,
        "system_prompt": sys_prompt,
        "message": "Model AI belum terhubung atau fallback aktif. Gunakan prompt di atas langsung di ChatGPT / Claude."
    }


@app.post("/api/tiktok/extract")
async def extract_tiktok_metadata(payload: TikTokExtractPayload):
    """Mengekstrak metadata TikTok dan direct download link tanpa watermark via tikwm API."""
    import urllib.request
    import urllib.parse
    
    clean_url = payload.url.strip()
    if not clean_url:
        raise HTTPException(status_code=400, detail="URL TikTok tidak boleh kosong.")

    try:
        api_url = f"https://www.tikwm.com/api/?url={urllib.parse.quote(clean_url, safe='')}"
        req = urllib.request.Request(
            api_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
                "Accept": "application/json"
            }
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))

        if data.get("code") == 0 and data.get("data"):
            d = data["data"]
            return {
                "ok": True,
                "id": d.get("id"),
                "title": d.get("title", ""),
                "duration": d.get("duration", 0),
                "play_url": d.get("play"),
                "cover_url": d.get("cover"),
                "author": d.get("author", {}).get("nickname", "TikTok Creator")
            }
        else:
            raise HTTPException(status_code=502, detail=f"Gagal mengambil metadata TikTok: {data.get('msg', 'Error')}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menghubungkan ke API TikTok: {str(e)}")


# ==============================================================================
# MOTIONCODE STUDIO (CANVAS CODE-TO-VIDEO ENGINE) ENDPOINTS
# ==============================================================================

class MotionPromptPayload(BaseModel):
    theme: str
    duration: int = 10
    scene: int = 1
    visual_style: str = "Flat Design & Corporate Memphis"
    format_type: str = "16:9"


class MotionCodeGeneratePayload(BaseModel):
    theme: str
    visual_style: str = "Flat Design & Corporate Memphis"
    format_type: str = "16:9"
    duration: int = 10
    scene_count: int = 1


@app.get("/api/motioncode/presets")
async def get_motion_presets():
    """Mengembalikan 5 preset komersial MotionCode Studio siap eksekusi."""
    return {"ok": True, "presets": motion_code_engine.MOTION_PRESETS}


@app.get("/api/motioncode/database")
async def get_motion_database():
    """Mengembalikan basis data 15 kategori industri (150 topik) dan 13 gaya visual."""
    return {
        "ok": True,
        "categories": motion_code_engine.MICROSTOCK_DATABASE,
        "visual_styles": motion_code_engine.VISUAL_STYLES
    }


@app.post("/api/motioncode/prompt")
async def generate_motion_prompt_api(payload: MotionPromptPayload):
    """Menghasilkan prompt formula Motion Graphics Canvas API untuk ChatGPT/Claude."""
    if payload.format_type == "9:16":
        p = motion_code_engine.generate_vertical_prompt(payload.theme, payload.duration, payload.scene, payload.visual_style)
    elif payload.format_type == "alpha":
        p = motion_code_engine.generate_transparent_prompt(payload.theme, payload.duration, payload.scene, payload.visual_style)
    else:
        p = motion_code_engine.generate_concept_prompt(payload.theme, payload.duration, payload.scene, payload.visual_style)
    return {"ok": True, "prompt": p, "format_type": payload.format_type}


@app.post("/api/motioncode/generate-code")
async def generate_motion_code_api(payload: MotionCodeGeneratePayload):
    """Menghasilkan kode JavaScript Canvas API murni menggunakan AI Brain."""
    res = motion_code_engine.generate_motion_code_with_ai(
        theme=payload.theme,
        visual_style=payload.visual_style,
        format_type=payload.format_type,
        duration=payload.duration,
        scene_count=payload.scene_count
    )
    return res


# ==============================================================================
# 10. REA VIDEO BIG DATA & ANYMOTION 212 STYLES ENGINE ENDPOINTS
# ==============================================================================
class ReaDirectorPromptPayload(BaseModel):
    topic: str
    style_id: str = "e-vox"
    blueprint_id: str = "agusleo_cuan"
    visual_look: str = "auto"
    palette: str = "mint"
    duration_s: int = 45
    aspect_ratio: str = "9:16"
    language: str = "Bahasa Indonesia"
    execute_ai: bool = False


class ReaScoreScriptPayload(BaseModel):
    transcript_text: str
    duration_s: float = 30.0
    shots_count: int = 10
    niche: str = "universal"


@app.get("/api/rea-bigdata/summary")
async def get_rea_bigdata_summary():
    """Mengembalikan ringkasan Hukum Empiris 11 Video Viral REA, 18 Shaders, dan 10 Palet AnyMotion."""
    corpus = rea_video_bigdata.load_rea_corpus()
    catalog = rea_video_bigdata.load_anymotion_catalog()
    blueprints = corpus.get("blueprints") or corpus.get("videos") or []
    return {
        "ok": True,
        "empirical_laws": rea_video_bigdata.EMPIRICAL_BIGDATA_LAWS,
        "total_blueprints": len(blueprints),
        "total_anymotion_styles": len(catalog.get("styles", [])),
        "total_scene_templates": len(catalog.get("scene_templates", [])),
        "total_sfx": len(catalog.get("sfx_manifest", [])),
        "shaders": rea_video_bigdata.VISUAL_LOOK_SHADERS,
        "palettes": rea_video_bigdata.ANYMOTION_PALETTES,
    }


@app.get("/api/rea-bigdata/blueprints")
async def get_rea_bigdata_blueprints():
    """Mengembalikan daftar lengkap 11 Blueprint Video Viral hasil ekstraksi REA."""
    corpus = rea_video_bigdata.load_rea_corpus()
    blueprints = corpus.get("blueprints") or corpus.get("videos") or []
    return {
        "ok": True,
        "blueprints": blueprints,
        "empirical_laws": corpus.get("empirical_laws", rea_video_bigdata.EMPIRICAL_BIGDATA_LAWS),
    }


@app.get("/api/rea-bigdata/anymotion-styles")
async def get_rea_anymotion_styles(category: Optional[str] = None):
    """Mengembalikan katalog 212 Gaya Visual AnyMotion, 33 Template Adegan, dan 95 SFX Studio."""
    catalog = rea_video_bigdata.load_anymotion_catalog()
    styles = catalog.get("styles", [])
    if category and category != "all":
        styles = [s for s in styles if s.get("category", "").lower() == category.lower()]
    return {
        "ok": True,
        "total_styles": len(styles),
        "categories": catalog.get("categories", {}),
        "styles": styles,
        "scene_templates": catalog.get("scene_templates", []),
        "sfx_manifest": catalog.get("sfx_manifest", []),
    }


@app.post("/api/rea-bigdata/director-prompt")
async def generate_rea_director_prompt(payload: ReaDirectorPromptPayload):
    """Menyusun Master Prompt Sutradara Kreatif AnyMotion + Big Data REA (opsional eksekusi AI)."""
    res = rea_video_bigdata.build_anymotion_director_prompt(
        topic=payload.topic,
        style_id=payload.style_id,
        blueprint_id=payload.blueprint_id,
        visual_look=payload.visual_look,
        palette=payload.palette,
        duration_s=payload.duration_s,
        aspect_ratio=payload.aspect_ratio,
        language=payload.language,
    )
    if payload.execute_ai and ai_brain.is_ai_ready():
        try:
            raw_res = ai_brain.generate_text(
                system_prompt="You are an award-winning Creative Director and JSON Storyboard Architect.",
                user_prompt=res["prompt"],
                json_mode=True,
                timeout=60,
            )
            parsed = ai_brain.extract_json(raw_res) if hasattr(ai_brain, "extract_json") else None
            res["ai_storyboard"] = parsed or raw_res
        except Exception as e:
            res["ai_error"] = str(e)
    return res


@app.post("/api/rea-bigdata/score-script")
async def score_script_with_rea_bigdata(payload: ReaScoreScriptPayload):
    """Menghitung skor retensi & pacing naskah berdasarkan Big Data 11 Video Viral REA."""
    metrics = rea_video_bigdata.score_clip_with_bigdata(
        transcript_text=payload.transcript_text,
        duration_s=payload.duration_s,
        shots_count=payload.shots_count,
        niche=payload.niche,
    )
    return {"ok": True, "metrics": metrics}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
