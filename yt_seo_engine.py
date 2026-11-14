"""
ClipperAI Studio - YouTube SEO & Viral Research Engine
Provides automated metadata generation (Titles, Descriptions, Tags, Best Posting Times)
and live YouTube search trend scouting via YouTube Autocomplete API.
"""

import json
import re
import urllib.parse
import urllib.request
from typing import List, Dict, Any, Optional

NICHE_KEYWORDS = {
    "universal": ["shorts viral", "video viral", "trending hari ini", "tips bermanfaat", "inspirasi hidup"],
    "kajian": ["kajian ustadz", "dakwah pendek", "ceramah singkat", "kajian sunnah", "nasehat islam", "mutiara hikmah", "tanya jawab islam"],
    "podcast": ["podcast indonesia", "obrolan mendalam", "interview inspiratif", "close the door", "bincang santai"],
    "bisnis": ["tips bisnis anak muda", "belajar investasi", "cara cari uang online", "strategi marketing", "ide usaha modal kecil"],
    "motivasi": ["kata mutiara kehidupan", "mindset orang sukses", "motivasi bangkit", "self improvement indonesia", "cara disiplin diri"],
    "edukasi": ["fakta unik dunia", "tahukah kamu", "belajar cepat", "edukasi sains", "pengetahuan umum"],
    "gaming": ["gameplay seru", "momen lucu gaming", "tips trik game", "highlight game", "gameplay indonesia"]
}

NICHE_CATEGORIES = {
    "universal": "22",  # People & Blogs
    "kajian": "27",     # Education
    "podcast": "24",    # Entertainment
    "bisnis": "27",     # Education
    "motivasi": "22",   # People & Blogs
    "edukasi": "27",    # Education
    "gaming": "20"      # Gaming
}


def query_youtube_autocomplete(query: str, hl: str = "id", gl: str = "ID") -> List[str]:
    """
    Fetch live trending autocomplete suggestions directly from YouTube Suggest API.
    Does not require any Google API Key.
    """
    if not query or not query.strip():
        return []

    encoded = urllib.parse.quote_plus(query.strip())
    url = f"https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&hl={hl}&gl={gl}&q={encoded}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            if isinstance(data, list) and len(data) > 1 and isinstance(data[1], list):
                return [str(item).strip() for item in data[1] if item]
    except Exception as e:
        # Fallback if network issue or timeout occurs
        print(f"[YouTube Suggest Warning]: {e}")
        return []

    return []


def research_viral_keywords(topic: str, niche: str = "universal", limit: int = 15) -> Dict[str, Any]:
    """
    Deep-researches live high-demand search keywords around a topic and niche.
    """
    results: List[str] = []
    seen = set()

    def add_keywords(items: List[str]):
        for item in items:
            clean = item.strip().lower()
            if clean and clean not in seen:
                seen.add(clean)
                results.append(clean)

    # 1. Direct query
    add_keywords(query_youtube_autocomplete(topic))

    # 2. Topic + modifier
    add_keywords(query_youtube_autocomplete(f"{topic} shorts"))
    add_keywords(query_youtube_autocomplete(f"{topic} terbaru"))

    # 3. Niche-specific suggestions
    niche_seeds = NICHE_KEYWORDS.get(niche, NICHE_KEYWORDS["universal"])
    for seed in niche_seeds[:2]:
        add_keywords(query_youtube_autocomplete(f"{topic} {seed}"))

    # If few results, populate from niche seeds
    if len(results) < 8:
        for seed in niche_seeds:
            add_keywords(query_youtube_autocomplete(seed))

    ranked = results[:limit]

    # Convert to tag formats
    hashtags = ["#" + re.sub(r'[^a-zA-Z0-9_]', '', w.title()) for w in ranked if len(w) > 2]
    tags_csv = ", ".join(ranked[:15])

    return {
        "topic": topic,
        "niche": niche,
        "total_found": len(ranked),
        "trending_keywords": ranked,
        "hashtags": hashtags[:10],
        "tags_csv": tags_csv
    }


def clean_hook_text(text: str) -> str:
    """Removes extra punctuation and keeps clean words."""
    cleaned = re.sub(r'[^\w\s\d]', '', text)
    return " ".join(cleaned.split())


def generate_shorts_seo_package(
    transcript_text: str,
    title_hint: Optional[str] = None,
    niche: str = "universal",
    speaker: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generates a full, broadcast-grade YouTube Shorts SEO package:
    - Primary Viral Title (<= 60 chars, curiosity hook, emoji, #Shorts)
    - 4 Alternative Title angles (Curiosity, Question, Warning, Secret)
    - Algorithm-Optimized Description (Hook, 3 Bullets, CTA, Hashtags)
    - Safe Tags list (Strictly under 500 characters limit)
    - Category ID & Peak Engagement Posting Times (WIB)
    - SEO Quality Audit Score (1-100)
    """
    clean_text = transcript_text.strip() if transcript_text else ""
    sentences = [s.strip() for s in re.split(r'[.!?\n]+', clean_text) if len(s.strip()) > 8]

    # Find the punchiest sentence for the hook
    first_sentence = sentences[0] if sentences else "Kebenaran Mengejutkan Yang Wajib Kamu Ketahui"
    second_sentence = sentences[1] if len(sentences) > 1 else "Simak penjelasan penting ini sampai selesai."
    third_sentence = sentences[2] if len(sentences) > 2 else "Jangan sampai terlambat mengetahuinya."

    # Extract base hook title
    base_title = title_hint.strip() if title_hint else first_sentence
    base_title = re.sub(r'#\S+', '', base_title).strip()

    # Niche hook templates
    niche_hooks = {
        "kajian": {
            "curiosity": "JANGAN DIABAIKAN! 😱 Nasihat Ini Bikin Sadar",
            "question": "Benarkah Amalan Ini Bikin Doa Mustajab? ✨",
            "warning": "AWAS KELIRU! ❌ Pahami Makna Sebenarnya",
            "secret": "Kunci Ketenangan Hati Yang Jarang Diketahui 🤍",
            "emoji": "🤍",
            "default_hashtags": ["#Shorts", "#KajianIslam", "#DakwahPendek", "#MutiaraHikmah", "#InspirasiIslam", "#CeramahSingkat"]
        },
        "podcast": {
            "curiosity": "PENGAKUAN MENGEJUTKAN! 🤯 Akhirnya Terungkap",
            "question": "Kenapa Hal Ini Baru Dibongkar Sekarang? 🤔",
            "warning": "JANGAN DILAKUKAN! ⚠️ Fakta Di Balik Layar",
            "secret": "Rahasia Sukses Yang Tak Pernah Diceritakan 💎",
            "emoji": "🎙️",
            "default_hashtags": ["#Shorts", "#PodcastIndonesia", "#ObrolanSeru", "#InsightPenting", "#ViralIndonesia"]
        },
        "bisnis": {
            "curiosity": "TRIK RAHASIA! 🚀 Cara Menghasilkan Uang Cepat",
            "question": "Modal Kecil Tapi Untung Jutaan? Begini Caranya 💡",
            "warning": "KESALAHAN FATAL! ❌ Jangan Buang Modalmu",
            "secret": "Formula Bisnis Yang Dipakai Para Miliarder 💰",
            "emoji": "📈",
            "default_hashtags": ["#Shorts", "#TipsBisnis", "#InvestasiCerdas", "#KeuanganAnakMuda", "#BisnisViral"]
        },
        "motivasi": {
            "curiosity": "DENGAR INI SAAT INGIN MENYERAH! 🔥",
            "question": "Mengapa Sukses Butuh Rasa Sakit? 🧠",
            "warning": "HENTIKAN KEBIASAAN INI! 🛑 Merusak Masa Depan",
            "secret": "Mindset Juara Yang Bikin Kamu Tak Terhentikan 🏆",
            "emoji": "⚡",
            "default_hashtags": ["#Shorts", "#MotivasiHidup", "#MindsetJuara", "#SelfImprovement", "#InspirasiHarian"]
        },
        "edukasi": {
            "curiosity": "FAKTA GILA! 😱 Kebanyakan Orang Tak Tahu",
            "question": "Apa Yang Terjadi Jika Kamu Melakukan Ini? 🧪",
            "warning": "JANGAN SALAH PAHAM! ⚠️ Penjelasan Ilmiahnya",
            "secret": "Trik Belajar Cepat Yang Wajib Kamu Coba 📚",
            "emoji": "💡",
            "default_hashtags": ["#Shorts", "#EdukasiSeru", "#FaktaUnik", "#TahukahKamu", "#SainsPopuler"]
        },
        "gaming": {
            "curiosity": "MOMEN TAK TERDUGA! 🎮 Skill Tingkat Dewa",
            "question": "Bisa Menang Lawan Musuh Terkuat? 🏆",
            "warning": "JANGAN DITIRU! ❌ Momen Paling Ngakak",
            "secret": "Settingan Rahasia Pro Player Terbongkar 🔥",
            "emoji": "🕹️",
            "default_hashtags": ["#Shorts", "#GamingShorts", "#GameplaySeru", "#MomenLucu", "#GamerIndonesia"]
        },
        "universal": {
            "curiosity": "JANGAN SKIP DULU! 😱 Ini Beneran Nyata",
            "question": "Pernahkah Kamu Mengalami Hal Ini? 🤔",
            "warning": "HATI-HATI! ⚠️ Jangan Sampai Terjebak",
            "secret": "Hal Penting Yang Jarang Orang Bicarakan ✨",
            "emoji": "🔥",
            "default_hashtags": ["#Shorts", "#Viral", "#Trending", "#Fyp", "#VideoViral"]
        }
    }

    niche_data = niche_hooks.get(niche, niche_hooks["universal"])

    # Create viral short title (< 60 chars)
    # Truncate base_title if too long
    if len(base_title) > 36:
        short_base = base_title[:33].strip() + "..."
    else:
        short_base = base_title

    main_title = f"{short_base} {niche_data['emoji']} #Shorts"
    if len(main_title) > 65:
        main_title = f"{short_base[:28]}... {niche_data['emoji']} #Shorts"

    # Alternative titles
    alt_titles = [
        f"{niche_data['curiosity']} #Shorts",
        f"{niche_data['question']} #Shorts",
        f"{niche_data['warning']} #Shorts",
        f"{niche_data['secret']} #Shorts"
    ]

    # Research trending keywords via autocomplete
    trend_data = research_viral_keywords(topic=base_title[:25], niche=niche, limit=12)
    trending_keywords = trend_data.get("trending_keywords", [])

    # Assemble Rich Description
    # 1. First 2 lines Hook
    desc_hook = f"{first_sentence}\n{second_sentence}"
    if len(desc_hook) > 180:
        desc_hook = desc_hook[:175] + "..."

    # 2. Key takeaways bullets
    bullets = [
        f"📌 Intisari 1: {first_sentence[:100]}",
        f"💡 Hikmah 2: {second_sentence[:100]}",
        f"🎯 Refleksi: {third_sentence[:100]}"
    ]

    # 3. Call to Action
    cta_text = (
        "🔔 Dukung channel ini dengan Like, Share, dan Subscribe untuk konten bermanfaat setiap hari!\n"
        "💬 Tulis pendapat atau pengalamanmu di kolom komentar di bawah ya!"
    )

    # 4. Hashtags
    combined_hashtags = list(dict.fromkeys(niche_data["default_hashtags"] + trend_data.get("hashtags", [])))[:8]
    hashtags_str = " ".join(combined_hashtags)

    full_description = f"{desc_hook}\n\n---\n" + "\n".join(bullets) + f"\n\n---\n{cta_text}\n\n{hashtags_str}"

    # Build Tags (YouTube strict limit: <= 500 characters total)
    base_tags = [
        "shorts", "youtube shorts", "video viral", "shorts viral",
        niche, f"{niche} shorts"
    ]
    if speaker:
        base_tags.append(speaker.lower())

    for kw in trending_keywords:
        if kw not in base_tags and len(kw) < 40:
            base_tags.append(kw)

    # Build CSV and strictly truncate under 480 chars for safety
    final_tags = []
    char_count = 0
    for t in base_tags:
        clean_tag = t.replace("#", "").strip()
        if not clean_tag:
            continue
        add_len = len(clean_tag) + (2 if final_tags else 0)
        if char_count + add_len < 480:
            final_tags.append(clean_tag)
            char_count += add_len
        else:
            break

    tags_csv = ", ".join(final_tags)

    # Best Upload Times in WIB (GMT+7)
    best_schedule = {
        "lunch_peak": "11:30 - 13:00 WIB (Peak Istirahat Siang)",
        "evening_peak": "17:30 - 20:30 WIB (Prime Time Malam Terbesar)",
        "best_days": "Kamis, Jumat, Sabtu, Minggu",
        "recommended_publish_status": "public"
    }

    # Virality Audit
    seo_score = 95
    if len(main_title) > 60:
        seo_score -= 5
    if len(tags_csv) < 150:
        seo_score -= 5

    return {
        "title": main_title,
        "title_length": len(main_title),
        "alternative_titles": alt_titles,
        "description": full_description,
        "tags": final_tags,
        "tags_csv": tags_csv,
        "tags_char_count": len(tags_csv),
        "hashtags": combined_hashtags,
        "category_id": NICHE_CATEGORIES.get(niche, "22"),
        "best_schedule": best_schedule,
        "seo_score": seo_score,
        "trending_scouted": trending_keywords
    }
