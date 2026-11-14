"""
ClipperAI Studio - Course LMS Synchronizer (Web dnzykreatif Edition)
Directly synchronizes YouTube Unlisted course lessons into the Google Spreadsheet
database of 'Web dnzykreatif' (Ustadz Dede Nuriman Az-Zailiy | DN-ZY Kreatif).
"""

import os
import json
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

BASE_DIR = Path(__file__).resolve().parent
TOKEN_FILE = BASE_DIR / "token.json"

# Spreadsheet ID from Web dnzykreatif (Config.gs)
SPREADSHEET_ID = "1uhes6wkdRqdgqGtFQ57BWfAZt5pvTukuzO3-vBw-TR4"

# Fallback default courses and modules from Web dnzykreatif
DEFAULT_COURSES = [
    {
        "slug": "apps-script-bundle",
        "title": "⭐ Paket Lengkap Master Google Apps Script (All Level)",
        "level": "bundle",
        "modules": [
            {"id": "mod-bundle-1", "title": "Bab 1: Pondasi Dasar JavaScript & Apps Script"},
            {"id": "mod-bundle-2", "title": "Bab 2: Database Google Sheets & CRUD Engine"},
            {"id": "mod-bundle-3", "title": "Bab 3: Web App, QRIS Payment & Sistem LMS"}
        ]
    },
    {
        "slug": "apps-script-basic",
        "title": "🌱 Google Apps Script Basic / Pemula",
        "level": "basic",
        "modules": [
            {"id": "mod-basic-1", "title": "Bab 1: Pengenalan Google Apps Script & Cloud IDE"},
            {"id": "mod-basic-2", "title": "Bab 2: Manipulasi Spreadsheet & Otomasi Cell"},
            {"id": "mod-basic-3", "title": "Bab 3: Triggers, Event Handler & Notifikasi Email"}
        ]
    },
    {
        "slug": "apps-script-intermediate",
        "title": "⚡ Google Apps Script Intermediate / Menengah",
        "level": "intermediate",
        "modules": [
            {"id": "mod-int-1", "title": "Bab 1: Arsitektur Database Relasional di Google Sheets"},
            {"id": "mod-int-2", "title": "Bab 2: REST API, JSON & Integrasi Eksternal"},
            {"id": "mod-int-3", "title": "Bab 3: Session Auth, Token & Manajemen Hak Akses"}
        ]
    },
    {
        "slug": "apps-script-pro",
        "title": "🔥 Google Apps Script Pro / Mahir (Production Apps)",
        "level": "pro",
        "modules": [
            {"id": "mod-pro-1", "title": "Bab 1: Full-Stack Web App dengan Alpine.js & Tailwind"},
            {"id": "mod-pro-2", "title": "Bab 2: QRIS Payment Gateway Dinamis Shopee/BCA"},
            {"id": "mod-pro-3", "title": "Bab 3: Optimasi Cache, Deployment & Keamanan"}
        ]
    },
    {
        "slug": "bahasa-arab-dasar",
        "title": "📖 Kursus Bahasa Arab & Kaidah Nahwu-Sharaf Dasar",
        "level": "basic",
        "modules": [
            {"id": "mod-arab-1", "title": "Bab 1: Pengantar Kalimah (Isim, Fi'il, Huruf)"},
            {"id": "mod-arab-2", "title": "Bab 2: Mengenal I'rab & Tanda-Tanda Asli"},
            {"id": "mod-arab-3", "title": "Bab 3: Jumlah Ismiyyah & Fi'liyyah"}
        ]
    }
]


def get_sheets_service():
    """Builds and returns Google Sheets API client if authenticated."""
    if not GOOGLE_API_AVAILABLE or not TOKEN_FILE.exists():
        return None
    try:
        creds = Credentials.from_authorized_user_file(
            str(TOKEN_FILE),
            [
                "https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/youtube.readonly",
                "https://www.googleapis.com/auth/spreadsheets"
            ]
        )
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_FILE, "w") as f:
                f.write(creds.to_json())
        return build("sheets", "v4", credentials=creds)
    except Exception as e:
        print(f"[Sheets Service Warning]: {e}")
        return None


def fetch_course_catalog() -> Dict[str, Any]:
    """
    Fetches the live list of courses and modules from Google Spreadsheet.
    Falls back to predefined catalog if offline.
    """
    service = get_sheets_service()
    if not service:
        return {"online": False, "courses": DEFAULT_COURSES}

    try:
        # Fetch Courses
        courses_res = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range="Courses!A2:J"
        ).execute()
        courses_rows = courses_res.get("values", [])

        # Fetch CourseModules
        modules_res = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range="CourseModules!A2:E"
        ).execute()
        modules_rows = modules_res.get("values", [])

        if not courses_rows:
            return {"online": True, "courses": DEFAULT_COURSES}

        # Build module mapping by course slug
        modules_by_course: Dict[str, List[Dict[str, str]]] = {}
        for row in modules_rows:
            if len(row) >= 3:
                mod_id = str(row[0]).strip()
                course_slug = str(row[1]).strip()
                mod_title = str(row[2]).strip()
                if course_slug not in modules_by_course:
                    modules_by_course[course_slug] = []
                modules_by_course[course_slug].append({
                    "id": mod_id,
                    "title": mod_title
                })

        # Assemble courses
        courses_list = []
        for r in courses_rows:
            if len(r) >= 7:
                title = str(r[0]).strip()
                level = str(r[1]).strip() if len(r) > 1 else "basic"
                slug = str(r[6]).strip()
                mods = modules_by_course.get(slug, [
                    {"id": f"mod_{slug}_1", "title": "Bab 1: Materi Pengantar"},
                    {"id": f"mod_{slug}_2", "title": "Bab 2: Pembahasan Utama"}
                ])
                courses_list.append({
                    "slug": slug,
                    "title": title,
                    "level": level,
                    "modules": mods
                })

        return {"online": True, "courses": courses_list}

    except Exception as e:
        print(f"[Fetch Catalog Warning]: {e}")
        return {"online": False, "courses": DEFAULT_COURSES}


def format_dnzy_lesson_content(
    title: str,
    summary_text: str,
    timestamps_text: Optional[str] = None
) -> str:
    """
    Formats the lesson description adhering to Web dnzykreatif styles:
    - Text blocks with 'Faedah:' and 'Kaidah:' trigger the .hadith-box styling in CourseView.html.
    - Timestamps formatted cleanly for the built-in timer component.
    """
    clean_summary = summary_text.strip() if summary_text else "Pembahasan materi pelajaran ini."
    
    parts = [
        f"📌 MATERI PELAJARAN: {title.upper()}\n",
        f"Faedah: {clean_summary}\n"
    ]

    if timestamps_text and timestamps_text.strip():
        parts.append(f"⏱️ DAFTAR MENIT PEMBAHASAN MATERI:\n{timestamps_text.strip()}\n")
    else:
        parts.append(
            "⏱️ DAFTAR MENIT PEMBAHASAN MATERI:\n"
            "00:00 - Pengantar & Konsep Utama\n"
            "03:15 - Penjelasan Praktis & Contoh Kasus\n"
            "12:40 - Latihan / Tugas Mandiri Siswa\n"
        )

    parts.append(
        "Kaidah: Pelajari dan praktikkan materi ini secara bertahap. "
        "Gunakan tombol '+ Catat di Menit Ini' di ruang belajar jika ingin mencatat poin penting."
    )

    return "\n".join(parts)


def append_lesson_to_database(
    course_slug: str,
    module_id: str,
    title: str,
    video_url: str,
    summary_text: str,
    timestamps_text: Optional[str] = None
) -> Dict[str, Any]:
    """
    Saves a new video lesson directly into the 'Lessons' sheet of Web dnzykreatif spreadsheet.
    Columns: [LessonId, CourseSlug, ModuleId, Title, Type, Content, VideoURL, FileURL, SortOrder, Status]
    """
    lesson_id = f"lesson_{uuid.uuid4().hex[:8]}"
    content = format_dnzy_lesson_content(title, summary_text, timestamps_text)

    # Extract clean video ID for embed
    video_id = ""
    if "youtu.be/" in video_url:
        video_id = video_url.split("youtu.be/")[1].split("?")[0]
    elif "v=" in video_url:
        video_id = video_url.split("v=")[1].split("&")[0]

    embed_iframe = (
        f'<iframe width="100%" height="480" '
        f'src="https://www.youtube-nocookie.com/embed/{video_id}" '
        f'frameborder="0" allowfullscreen></iframe>'
    ) if video_id else ""

    tsv_row = f"{lesson_id}\t{course_slug}\t{module_id}\t{title}\tvideo\t{content.replace(chr(10), ' ')}\t{video_url}\t\t1\tpublish"

    service = get_sheets_service()
    if not service:
        return {
            "ok": True,
            "synced_live": False,
            "message": "Kredensial Google Sheets belum terhubung. Salin baris di bawah ke sheet 'Lessons' Web dnzykreatif.",
            "lesson_id": lesson_id,
            "course_slug": course_slug,
            "module_id": module_id,
            "title": title,
            "video_url": video_url,
            "content": content,
            "embed_iframe": embed_iframe,
            "tsv_row": tsv_row
        }

    try:
        # Determine current rows count for sort order
        existing_res = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range="Lessons!A:A"
        ).execute()
        current_rows = len(existing_res.get("values", []))
        sort_order = max(1, current_rows)

        row_values = [
            lesson_id,
            course_slug,
            module_id,
            title,
            "video",
            content,
            video_url,
            "",          # FileURL
            sort_order,
            "publish"
        ]

        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range="Lessons!A1",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": [row_values]}
        ).execute()

        return {
            "ok": True,
            "synced_live": True,
            "message": f"🎉 Berhasil diterbitkan ke Web Kursus DN-ZY Kreatif! Materi langsung aktif di sheet 'Lessons' (Baris ke-{sort_order + 1}).",
            "lesson_id": lesson_id,
            "course_slug": course_slug,
            "module_id": module_id,
            "title": title,
            "video_url": video_url,
            "embed_iframe": embed_iframe,
            "content": content,
            "tsv_row": tsv_row
        }

    except Exception as e:
        return {
            "ok": True,
            "synced_live": False,
            "message": f"Gagal auto-sync langsung ({str(e)}). Gunakan baris salin di bawah:",
            "lesson_id": lesson_id,
            "course_slug": course_slug,
            "module_id": module_id,
            "title": title,
            "video_url": video_url,
            "embed_iframe": embed_iframe,
            "content": content,
            "tsv_row": tsv_row
        }
