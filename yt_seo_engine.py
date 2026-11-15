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
    speaker: Optional[str] = None,
    mode: str = "shorts"
) -> Dict[str, Any]:
    """
    Generates a full, broadcast-grade YouTube SEO package:
    - Mode 'shorts': Primary Viral Title (<= 60 chars, curiosity hook, emoji, #Shorts)
    - Mode 'long_form': High CTR Long Video Title (up to 100 chars, no #Shorts), Chapters, Deep Description.
    """
    clean_text = transcript_text.strip() if transcript_text else ""

    # 1. Coba generate SEO via AI (Gemini / SumoPod / 9Router) terlebih dahulu
    try:
        import ai_brain
        ai_pkg = ai_brain.generate_seo_with_ai(
            transcript_text=clean_text,
            title_hint=title_hint,
            niche=niche,
            speaker=speaker,
            mode=mode,
        )
        if ai_pkg:
            # Perkaya dengan live YouTube Autocomplete keywords
            trend_data = research_viral_keywords(topic=(title_hint or clean_text[:25]), niche=niche, limit=12)
            ai_pkg["trending_scouted"] = trend_data.get("trending_keywords", [])
            return ai_pkg
    except Exception as e:
        print(f"[SEO AI Fallback] {e}")

    sentences = [s.strip() for s in re.split(r'[.!?\n]+', clean_text) if len(s.strip()) > 8]

    first_sentence = sentences[0] if sentences else "Kebenaran Mengejutkan Yang Wajib Kamu Ketahui"
    second_sentence = sentences[1] if len(sentences) > 1 else "Simak penjelasan penting ini sampai selesai."
    third_sentence = sentences[2] if len(sentences) > 2 else "Jangan sampai terlambat mengetahuinya."

    base_title = title_hint.strip() if title_hint else first_sentence
    base_title = re.sub(r'#\S+', '', base_title).strip()

    is_long = (mode.lower() == "long_form" or mode.lower() == "long")

    # Niche hook templates
    niche_hooks = {
        "kajian": {
            "curiosity": "JANGAN DIABAIKAN! 😱 Nasihat Ini Bikin Sadar",
            "question": "Benarkah Amalan Ini Bikin Doa Mustajab? ✨",
            "warning": "AWAS KELIRU! ❌ Pahami Makna Sebenarnya",
            "secret": "Kunci Ketenangan Hati Yang Jarang Diketahui 🤍",
            "emoji": "🤍",
            "tagline": "Kajian Penuh Hikmah & Nasehat Kehidupan",
            "default_hashtags": ["#KajianIslam", "#Dakwah", "#MutiaraHikmah", "#InspirasiIslam", "#CeramahLengkap" if is_long else "#Shorts"]
        },
        "podcast": {
            "curiosity": "PENGAKUAN MENGEJUTKAN! 🤯 Akhirnya Terungkap",
            "question": "Kenapa Hal Ini Baru Dibongkar Sekarang? 🤔",
            "warning": "JANGAN DILAKUKAN! ⚠️ Fakta Di Balik Layar",
            "secret": "Rahasia Sukses Yang Tak Pernah Diceritakan 💎",
            "emoji": "🎙️",
            "tagline": "Obrolan Mendalam & Fakta Terbuka",
            "default_hashtags": ["#PodcastIndonesia", "#ObrolanSeru", "#InsightPenting", "#ViralIndonesia", "#Wawancara" if is_long else "#Shorts"]
        },
        "bisnis": {
            "curiosity": "TRIK RAHASIA! 🚀 Cara Menghasilkan Uang Cepat",
            "question": "Modal Kecil Tapi Untung Jutaan? Begini Caranya 💡",
            "warning": "KESALAHAN FATAL! ❌ Jangan Buang Modalmu",
            "secret": "Formula Bisnis Yang Dipakai Para Miliarder 💰",
            "emoji": "📈",
            "tagline": "Strategi Bisnis & Keuangan Masa Depan",
            "default_hashtags": ["#TipsBisnis", "#InvestasiCerdas", "#KeuanganAnakMuda", "#BisnisViral", "#EdukasiFinansial" if is_long else "#Shorts"]
        },
        "motivasi": {
            "curiosity": "DENGAR INI SAAT INGIN MENYERAH! 🔥",
            "question": "Mengapa Sukses Butuh Rasa Sakit? 🧠",
            "warning": "HENTIKAN KEBIASAAN INI! 🛑 Merusak Masa Depan",
            "secret": "Mindset Juara Yang Bikin Kamu Tak Terhentikan 🏆",
            "emoji": "⚡",
            "tagline": "Pemicu Semangat & Perubahan Hidup",
            "default_hashtags": ["#MotivasiHidup", "#MindsetJuara", "#SelfImprovement", "#InspirasiHarian", "#PengembanganDiri" if is_long else "#Shorts"]
        },
        "edukasi": {
            "curiosity": "FAKTA GILA! 😱 Kebanyakan Orang Tak Tahu",
            "question": "Apa Yang Terjadi Jika Kamu Melakukan Ini? 🧪",
            "warning": "JANGAN SALAH PAHAM! ⚠️ Penjelasan Ilmiahnya",
            "secret": "Trik Belajar Cepat Yang Wajib Kamu Coba 📚",
            "emoji": "💡",
            "tagline": "Wawasan Sains & Pengetahuan Populer",
            "default_hashtags": ["#EdukasiSeru", "#FaktaUnik", "#TahukahKamu", "#SainsPopuler", "#BelajarOnline" if is_long else "#Shorts"]
        },
        "gaming": {
            "curiosity": "MOMEN TAK TERDUGA! 🎮 Skill Tingkat Dewa",
            "question": "Bisa Menang Lawan Musuh Terkuat? 🏆",
            "warning": "JANGAN DITIRU! ❌ Momen Paling Ngakak",
            "secret": "Settingan Rahasia Pro Player Terbongkar 🔥",
            "emoji": "🕹️",
            "tagline": "Gameplay Seru & Trik Kemenangan",
            "default_hashtags": ["#GamingIndonesia", "#GameplaySeru", "#MomenLucu", "#GamerIndonesia", "#FullGameplay" if is_long else "#Shorts"]
        },
        "universal": {
            "curiosity": "JANGAN SKIP DULU! 😱 Ini Beneran Nyata",
            "question": "Pernahkah Kamu Mengalami Hal Ini? 🤔",
            "warning": "HATI-HATI! ⚠️ Jangan Sampai Terjebak",
            "secret": "Hal Penting Yang Jarang Orang Bicarakan ✨",
            "emoji": "🔥",
            "tagline": "Video Pilihan Paling Banyak Dicari",
            "default_hashtags": ["#Viral", "#Trending", "#Fyp", "#VideoViral", "#VideoPilihan" if is_long else "#Shorts"]
        }
    }

    niche_data = niche_hooks.get(niche, niche_hooks["universal"])

    if is_long:
        # Long-form video title (high CTR, up to 95 chars, NO #Shorts)
        speaker_prefix = f"[{speaker}] " if speaker else ""
        main_title = f"{speaker_prefix}{base_title} - {niche_data['tagline']} {niche_data['emoji']}"
        if len(main_title) > 95:
            main_title = main_title[:92].strip() + "..."

        alt_titles = [
            f"{niche_data['curiosity']} | {base_title[:45]}",
            f"{niche_data['question']} - Simak Penjelasannya!",
            f"{niche_data['warning']} | Penjelasan Lengkap",
            f"{niche_data['secret']} - Trik Mendalam"
        ]
    else:
        # Shorts title (< 60 chars with #Shorts) — potong di batas kata utuh
        if len(base_title) > 40:
            cut = base_title[:40].rsplit(" ", 1)[0].strip()
            short_base = cut if len(cut) >= 14 else base_title[:37].strip()
        else:
            short_base = base_title

        main_title = f"{short_base} {niche_data['emoji']} #Shorts"
        if len(main_title) > 68:
            cut2 = short_base[:32].rsplit(" ", 1)[0].strip()
            main_title = f"{cut2} {niche_data['emoji']} #Shorts"

        alt_titles = [
            f"{niche_data['curiosity']} #Shorts",
            f"{niche_data['question']} #Shorts",
            f"{niche_data['warning']} #Shorts",
            f"{niche_data['secret']} #Shorts"
        ]

    # Research trending keywords via autocomplete
    trend_data = research_viral_keywords(topic=base_title[:25], niche=niche, limit=12)
    trending_keywords = trend_data.get("trending_keywords", [])

    # Assemble Description
    if is_long:
        desc_intro = (
            f"Selamat datang di video lengkap ini! Di video kali ini kita membahas secara tuntas mengenai: {base_title}.\n\n"
            f"{first_sentence}\n{second_sentence}\n{third_sentence}"
        )
        chapters = (
            "⏱️ TIMESTAMPS / DAFTAR ISI VIDEO:\n"
            "00:00 - Pembukaan & Latar Belakang Permasalahan\n"
            "02:15 - Pokok Pembahasan & Penjelasan Utama\n"
            "08:40 - Dalil, Logika & Landasan Teori Penting\n"
            "15:30 - Solusi Nyata, Tips & Langkah Praktis\n"
            "22:00 - Doa, Hikmah Refleksi & Penutup"
        )
        bullets = [
            f"📌 Poin 1: {first_sentence[:120]}",
            f"💡 Poin 2: {second_sentence[:120]}",
            f"🎯 Kesimpulan: {third_sentence[:120]}"
        ]
        cta_text = (
            "🔔 Jangan lupa klik tombol LIKE, SUBSCRIBE, dan aktifkan lonceng notifikasi agar tidak ketinggalan video bermanfaat berikutnya!\n"
            "💬 Tulis pertanyaan, tanggapan, atau pengalaman Anda di kolom komentar di bawah."
        )
        combined_hashtags = list(dict.fromkeys(niche_data["default_hashtags"] + trend_data.get("hashtags", [])))[:8]
        hashtags_str = " ".join(combined_hashtags)
        full_description = f"{desc_intro}\n\n---\n{chapters}\n\n---\n📌 INTISARI PEMBAHASAN:\n" + "\n".join(bullets) + f"\n\n---\n{cta_text}\n\n{hashtags_str}"
    else:
        desc_hook = f"{first_sentence}\n{second_sentence}"
        if len(desc_hook) > 180:
            desc_hook = desc_hook[:175] + "..."

        bullets = [
            f"📌 Intisari 1: {first_sentence[:100]}",
            f"💡 Hikmah 2: {second_sentence[:100]}",
            f"🎯 Refleksi: {third_sentence[:100]}"
        ]

        cta_text = (
            "🔔 Dukung channel ini dengan Like, Share, dan Subscribe untuk konten bermanfaat setiap hari!\n"
            "💬 Tulis pendapat atau pengalamanmu di kolom komentar di bawah ya!"
        )

        combined_hashtags = list(dict.fromkeys(niche_data["default_hashtags"] + trend_data.get("hashtags", [])))[:8]
        hashtags_str = " ".join(combined_hashtags)
        full_description = f"{desc_hook}\n\n---\n" + "\n".join(bullets) + f"\n\n---\n{cta_text}\n\n{hashtags_str}"

    # Build Tags (strictly under 480 chars)
    if is_long:
        base_tags = [
            "video full", "video lengkap", "pembahasan lengkap", niche, f"kajian {niche}"
        ]
    else:
        base_tags = [
            "shorts", "youtube shorts", "video viral", "shorts viral", niche, f"{niche} shorts"
        ]

    if speaker:
        base_tags.append(speaker.lower())

    for kw in trending_keywords:
        if kw not in base_tags and len(kw) < 40:
            base_tags.append(kw)

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

    best_schedule = {
        "lunch_peak": "11:30 - 13:00 WIB (Peak Siang)",
        "evening_peak": "17:30 - 20:30 WIB (Prime Time Malam)",
        "best_days": "Kamis, Jumat, Sabtu, Minggu",
        "recommended_publish_status": "public"
    }

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
        "seo_score": 96,
        "mode": mode,
        "trending_scouted": trending_keywords
    }

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
