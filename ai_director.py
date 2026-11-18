"""
ClipperAI Studio - AI Visual Art Director
Menganalisis naskah atau ide pengguna menggunakan Otak AI (Gemini / AI Router)
untuk merancang STORYBOARD DINAMIS KELAS DUNIA (AnyMotion & Apple Style):
1. Menentukan Palet Warna (mint, obsidian, cream, azure, emerald)
2. Memecah naskah menjadi adegan visual dengan komponen modern:
   - 'phone_hero': Mockup smartphone melayang dengan konten aplikasi / data
   - 'app_window': Jendela software macOS melayang dengan header traffic lights
   - 'feature_list': 2-3 Kartu Apple-style dengan icon & checklist
   - 'stat_shock': Angka raksasa dengan progress ring / fakta
   - 'metric_counter': Angka metrik yang berputar naik dengan progress bar
   - 'tweet_quote': Kartu testimoni & review bintang 5 terverifikasi
   - 'split_vs': Pertarungan dramatis VS antara Masalah Lama vs Solusi Baru
   - 'code_terminal': Jendela terminal macOS dengan animasi ketikan kode
   - 'floating_badge': Stempel lencana emas rekomendasi resmi
   - 'comparison': Dua kartu kontras (Sebelum vs Sesudah)
   - 'cta_slam': Ajakan bertindak dengan tombol interaktif melayang
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Tuple

import ai_brain


STOP_WORDS = {
    "yang", "untuk", "pada", "ke", "para", "namun", "menurut", "antara", "dia", "dua",
    "ia", "seperti", "jika", "sehingga", "kembali", "dan", "tidak", "ini", "karena",
    "oleh", "saat", "harus", "bisa", "ada", "juga", "dari", "dalam", "akan", "serta"
}


def build_dynamic_heuristic_storyboard(script_text: str, theme_hint: Optional[str] = None) -> Dict[str, Any]:
    """
    Offline Intelligent NLP Storyboard Parser:
    Menganalisis teks naskah secara dinamis dan memecahnya menjadi 3-5 adegan visual
    yang 100% relevan dengan isi teks pengguna (BUKAN teks statis dummy!).
    """
    clean_text = script_text.strip()
    # 1. Pisahkan naskah menjadi kalimat-kalimat logis
    raw_sentences = [s.strip() for s in re.split(r'[\.\?!;\n]+', clean_text) if len(s.strip()) > 6]
    
    # Jika kalimat terlalu sedikit (kurang dari 3), pecah berdasarkan tanda koma atau kata hubung
    if len(raw_sentences) < 3:
        chunks = []
        for s in (raw_sentences or [clean_text]):
            sub_chunks = [sc.strip() for sc in re.split(r'[,]+|\b(?:karena|supaya|agar|dan|sehingga|tetapi)\b', s) if len(sc.strip()) > 8]
            if len(sub_chunks) >= 2:
                chunks.extend(sub_chunks)
            else:
                chunks.append(s)
        raw_sentences = chunks

    if not raw_sentences:
        raw_sentences = [clean_text[:50], clean_text[50:100] or clean_text[:40], "Silakan hubungi kami"]

    # Batasi 3-5 adegan
    target_count = min(5, max(3, len(raw_sentences)))
    if len(raw_sentences) > target_count:
        step = len(raw_sentences) / target_count
        sampled = [raw_sentences[int(i * step)] for i in range(target_count)]
        # Pastikan kalimat terakhir (biasanya CTA) selalu masuk
        if raw_sentences[-1] not in sampled:
            sampled[-1] = raw_sentences[-1]
        raw_sentences = sampled

    # Deteksi Palet
    chosen_palette = theme_hint if theme_hint and theme_hint != "auto" else "mint"
    lower_all = clean_text.lower()
    if chosen_palette == "mint":
        if any(w in lower_all for w in ["islam", "santri", "pondok", "ustadz", "pesantren", "masjid", "dakwah"]):
            chosen_palette = "emerald"
        elif any(w in lower_all for w in ["bisnis", "cuan", "uang", "finansial", "omset", "investasi"]):
            chosen_palette = "obsidian"

    accent_map = {
        "mint": "#10B981",
        "emerald": "#059669",
        "obsidian": "#0EA5E9",
        "cream": "#F59E0B",
        "azure": "#38BDF8"
    }
    accent_hex = accent_map.get(chosen_palette, "#10B981")

    # Pool komponen yang siap dipakai
    available_comps = [
        "phone_hero", "split_vs", "feature_list", "stat_shock",
        "metric_counter", "app_window", "tweet_quote", "code_terminal", "floating_badge"
    ]
    used_comps: List[str] = []

    scenes: List[Dict[str, Any]] = []
    n_sc = len(raw_sentences)

    for idx, sentence in enumerate(raw_sentences):
        is_last = (idx == n_sc - 1)
        lower_s = sentence.lower()
        words = [w for w in re.sub(r'[^\w\s]', '', sentence).split() if w]

        # Ekstrak Judul Dua Nada (Dual-Tone Headline)
        reg_title, ita_title, tra_title = _extract_dual_tone_title(words)

        # Tentukan tipe komponen berdasarkan makna semantik kalimat
        comp_type = "phone_hero"
        
        # 1. Cek Call-to-Action di akhir
        if is_last or any(w in lower_s for w in ["inbox", "dm", "hubungi", "pesan", "coba", "demo", "klik", "daftar", "sekarang", "komen"]):
            comp_type = "cta_slam"
        
        # 2. Cek Angka / Statistik / Persentase
        elif re.search(r'\d+%?|\b(?:100%|99%|10x|jutaan|ribu|jam|detik)\b', lower_s):
            comp_type = "metric_counter" if idx % 2 == 0 else "stat_shock"
        
        # 3. Cek Perbandingan / Kontras
        elif any(w in lower_s for w in ["berbeda", "sebelum", "sesudah", "manual", "lama", "baru", "daripada", "vs"]):
            comp_type = "split_vs"
        
        # 4. Cek Multi-Peran / Fitur / Daftar
        elif any(w in lower_s for w in ["admin", "ustadz", "santri", "guru", "wali", "fitur", "modul", "keunggulan", "alurnya"]) or "," in sentence:
            comp_type = "feature_list"
            
        # 5. Cek Testimoni / Kutipan
        elif any(w in lower_s for w in ["kata", "menurut", "bilang", "testimoni", "puas", "rekomendasi"]):
            comp_type = "tweet_quote"

        # 6. Default Fallback yang bervariasi
        else:
            candidates = [c for c in available_comps if c not in used_comps[-1:]]
            comp_type = candidates[(idx * 3 + 1) % len(candidates)]

        # Hindari pengulangan berturut-turut
        if used_comps and comp_type == used_comps[-1] and comp_type != "cta_slam":
            alt = [c for c in available_comps if c != comp_type]
            comp_type = alt[idx % len(alt)]

        used_comps.append(comp_type)

        # Buat data komponen yang dinamis sesuai kalimat pengguna
        sc_data: Dict[str, Any] = {
            "scene_num": idx + 1,
            "component_type": comp_type,
            "title_regular": reg_title,
            "title_italic": ita_title,
            "title_trailing": tra_title,
            "narration_line": sentence
        }

        # Isi field spesifik komponen 100% dari isi kalimat naskah pengguna
        short_phrase = " ".join(words[:6]) if words else "Inti Pembahasan"
        second_phrase = " ".join(words[6:13]) if len(words) > 6 else short_phrase
        clauses = [c.strip() for c in re.split(r'\b(?:tapi|namun|sedangkan|justru|karena|daripada)\b|,', sentence, flags=re.IGNORECASE) if len(c.strip()) > 4]

        num_words_map = {
            "delapan puluh": "80+",
            "lima puluh": "50 HARI",
            "tiga sahabat": "3 SAHABAT",
            "tiga fakta": "3 FAKTA",
            "empat babak": "4 BABAK",
            "seratus": "100%",
        }
        detected_num = None
        match_num = re.search(r'(\d+[\+%]?(?:\s*(?:hari|orang|tahun|kali|fakta|sahabat|juta|ribu))?)', sentence, re.IGNORECASE)
        if match_num:
            detected_num = match_num.group(1).upper()
        else:
            for kw_num, val_num in num_words_map.items():
                if kw_num in lower_s:
                    detected_num = val_num
                    break

        if comp_type == "cta_slam":
            sc_data["cta_headline"] = short_phrase
            if "inbox" in lower_s or "dm" in lower_s:
                sc_data["cta_button_text"] = "KIRIM INBOX SEKARANG"
            elif "demo" in lower_s:
                sc_data["cta_button_text"] = "COBA AKUN DEMO"
            elif any(w in lower_s for w in ("komen", "tulis", "pendapat")):
                sc_data["cta_button_text"] = "TULIS DI KOMENTAR"
            else:
                sc_data["cta_button_text"] = "SIMPAN & BAGIKAN"

        elif comp_type == "split_vs":
            left_c = clauses[0] if len(clauses) >= 2 else " ".join(words[:5])
            right_c = clauses[1] if len(clauses) >= 2 else " ".join(words[5:11] or words[:5])
            sc_data["vs_left_title"] = " ".join(left_c.split()[:3]).title() or "Kondisi Awal"
            sc_data["vs_left_desc"] = left_c[:52]
            sc_data["vs_right_title"] = " ".join(right_c.split()[:3]).title() or "Fakta & Hasil"
            sc_data["vs_right_desc"] = right_c[:52]

        elif comp_type == "feature_list":
            feats = []
            if len(clauses) >= 2:
                for cl in clauses[:3]:
                    cl_words = cl.split()
                    feats.append({
                        "title": " ".join(cl_words[:3]).title(),
                        "subtitle": cl[:50],
                        "icon": "✓"
                    })
            if len(feats) < 2:
                feats = []
                for s_near in raw_sentences[max(0, idx - 1):min(len(raw_sentences), idx + 2)]:
                    sn_words = [w for w in re.sub(r'[^\w\s\'\-]', '', s_near).split() if w]
                    if sn_words:
                        feats.append({
                            "title": " ".join(sn_words[:3]).title(),
                            "subtitle": " ".join(sn_words[:8]),
                            "icon": "✓"
                        })
            while len(feats) < 3:
                feats.append({"title": short_phrase[:24].title(), "subtitle": sentence[:48], "icon": "✓"})
            sc_data["features"] = feats[:3]

        elif comp_type in ("metric_counter", "stat_shock"):
            num_val = detected_num or f"0{idx + 1}"
            sc_data["counter_target"] = num_val
            sc_data["counter_label"] = short_phrase.title()
            sc_data["counter_sublabel"] = sentence[:58]
            sc_data["stat_number"] = num_val
            sc_data["stat_label"] = short_phrase.title()

        elif comp_type == "app_window":
            sc_data["window_title"] = f"Babak 0{idx + 1} • Sorotan Utama"
            sc_data["window_headline"] = short_phrase.title()
            sc_data["window_subtext"] = sentence[:72] + ("..." if len(sentence) > 72 else "")

        elif comp_type == "tweet_quote":
            sc_data["quote_author"] = "Sorotan Kisah & Hikmah" if any(k in lower_all for k in ("nabi", "sahabat", "ka'ab", "kaab", "allah", "taubat")) else "Catatan Penting"
            sc_data["quote_handle"] = f"babak_0{idx + 1}"
            sc_data["quote_text"] = sentence[:90] + ("..." if len(sentence) > 90 else "")
            sc_data["quote_role"] = short_phrase.title()[:32]

        elif comp_type == "code_terminal":
            sc_data["term_cmd"] = f"analyze --scene 0{idx + 1}"
            sc_data["term_line1"] = short_phrase[:46]
            sc_data["term_line2"] = second_phrase[:46]
            sc_data["term_status"] = detected_num or "Fakta Utama"

        elif comp_type == "floating_badge":
            sc_data["badge_title"] = short_phrase.title()[:30]
            sc_data["badge_sub"] = sentence[:52]

        else:  # phone_hero
            sc_data["screen_title"] = short_phrase.title()[:26]
            sc_data["screen_stat_title"] = "SOROTAN"
            sc_data["screen_stat_value"] = detected_num or f"0{idx + 1}"
            sc_data["screen_card2_title"] = "INTI"
            sc_data["screen_card2_value"] = (" ".join(words[3:6]) or words[-1]).title()[:18] if words else "Utama"

        scenes.append(sc_data)

    return {
        "narration_script": clean_text,
        "theme_palette": chosen_palette,
        "accent_hex": accent_hex,
        "scenes": scenes
    }


def _extract_dual_tone_title(words: List[str]) -> Tuple[str, str, str]:
    """Ekstrak judul regular, kata kunci miring (italic accent), dan trailing."""
    if not words:
        return "Insight", "Penting", "Hari Ini"
    if len(words) == 1:
        return words[0], "", ""
    if len(words) == 2:
        return words[0], words[1], ""

    # Ambil 3-6 kata pertama
    selected = words[:min(6, len(words))]

    # Cari kata non-stopword setelah kata pertama agar regular punya awal yang mantap
    accent_idx = -1
    for i in range(1, len(selected)):
        if selected[i].lower() not in STOP_WORDS and len(selected[i]) > 3:
            accent_idx = i
            break

    if accent_idx == -1:
        accent_idx = 1 if len(selected) > 1 else 0

    reg = " ".join(selected[:accent_idx]).strip()
    ita = selected[accent_idx].strip()
    tra = " ".join(selected[accent_idx + 1:]).strip()
    return reg, ita, tra


def direct_visual_storyboard(script_text: str, theme_hint: Optional[str] = None) -> Dict[str, Any]:
    """
    Bertindak sebagai Executive Art Director untuk menghasilkan storyboard visual berkualitas tinggi.
    Mencoba memanggil Otak AI (Gemini / AI Router) jika aktif, dan selalu jatuh kembali
    ke Dynamic Heuristic Parser yang menganalisis teks pengguna secara presisi.
    """
    sys_prompt = (
        "Kamu adalah AI Visual Art Director kelas dunia spesialis video motion graphics komersial modern "
        "(gaya Apple, AnyMotion by RootPixel, dan Linear App). "
        "Tugasmu: Menganalisis naskah input pengguna, memoles narasi naskah agar ritme bicaranya enak didengar, "
        "dan merancang STORYBOARD VISUAL DINAMIS yang memanjakan mata, elegan, dan profesional. "
        "\n\nPILIHAN PALET WARNA (theme_palette):\n"
        "- 'mint': Mint sage pastel & warm cream (Aesthetic AnyMotion Facts & Tech Modern)\n"
        "- 'obsidian': Deep luxury obsidian & neon glow (Dark mode premium)\n"
        "- 'cream': Warm ivory & gold amber (Islamic wisdom & edukasi hangat)\n"
        "- 'azure': Clean minimalist ice blue & white (SaaS & Enterprise corporate)\n"
        "- 'emerald': Deep forest emerald & gold (Pesantren, kajian, & berkah)\n"
        "\n\nPILIHAN KOMPONEN VISUAL (component_type) UNTUK SETIAP ADEGAN:\n"
        "1. 'phone_hero': Mockup smartphone 3D melayang dengan tampilan UI aplikasi / kartu data di layarnya.\n"
        "   Field: 'screen_title', 'screen_stat_title', 'screen_stat_value', 'screen_card2_title', 'screen_card2_value'.\n"
        "2. 'app_window': Jendela software desktop modern (gaya macOS dengan tombol merah, kuning, hijau).\n"
        "   Field: 'window_title', 'window_headline', 'window_subtext'.\n"
        "3. 'feature_list': 2-3 Kartu fitur minimalis bergaya Apple dengan icon & centang hijau.\n"
        "   Field: 'features' (array berisi 2-3 object: {'title': str, 'subtitle': str, 'icon': str}).\n"
        "4. 'stat_shock': Angka/statistik raksasa dengan label fakta pendukung.\n"
        "   Field: 'stat_number', 'stat_label'.\n"
        "5. 'metric_counter': Angka metrik yang menghitung naik animasi (misal: 0% -> 99.8% atau 0 -> 10.000) dengan progress bar.\n"
        "   Field: 'counter_target', 'counter_label', 'counter_sublabel'.\n"
        "6. 'tweet_quote': Kartu testimoni & review bintang 5 terverifikasi gaya Twitter/Apple.\n"
        "   Field: 'quote_author', 'quote_handle', 'quote_text', 'quote_role'.\n"
        "7. 'split_vs': Pertarungan dramatis VS antara Masalah Lama vs Solusi Baru dengan lencana emas VS di tengah.\n"
        "   Field: 'vs_left_title', 'vs_left_desc', 'vs_right_title', 'vs_right_desc'.\n"
        "8. 'code_terminal': Jendela terminal gelap dengan animasi ketikan kode dan status sinkronisasi cloud realtime.\n"
        "   Field: 'term_cmd', 'term_line1', 'term_line2', 'term_status'.\n"
        "9. 'floating_badge': Stempel lencana emas melayang resmi bintang 5 / garansi kepuasan.\n"
        "   Field: 'badge_title', 'badge_sub'.\n"
        "10. 'comparison': Dua kartu kontras berdampingan (SEBELUM vs SESUDAH / MASALAH vs SOLUSI).\n"
        "   Field: 'compare_before', 'compare_after'.\n"
        "11. 'cta_slam': Kartu penutup Call-to-Action dengan tombol aksi melayang.\n"
        "   Field: 'cta_headline', 'cta_button_text'.\n"
        "\n\nATURAN JUDUL DUA NADA (Dual-Tone Headline) PADA SETIAP ADEGAN:\n"
        "Setiap adegan harus memiliki judul atas yang terdiri dari 3 bagian: 'title_regular', 'title_italic' (kata aksen kunci bergaya miring elegan), dan 'title_trailing'.\n"
        "Contoh: 'Kamu pasti pernah' (regular) + 'lihat' (italic) + 'ini kan?' (trailing).\n"
        "\n\nATURAN KETAT:\n"
        "- Pastikan komponen visual BERBEDA-BEDA antar adegan berurutan (jangan gunakan komponen yang sama 2x berturut-turut).\n"
        "- Jika ada ajakan aksi di akhir naskah, adegan terakhir WAJIB ber-type 'cta_slam'.\n"
        "- Output WAJIB berupa JSON murni sesuai skema berikut:\n"
        "{\n"
        "  \"narration_script\": \"naskah lengkap narator suara\",\n"
        "  \"theme_palette\": \"mint\" | \"obsidian\" | \"cream\" | \"azure\" | \"emerald\",\n"
        "  \"accent_hex\": \"#10B981\",\n"
        "  \"scenes\": [\n"
        "    {\n"
        "      \"scene_num\": 1,\n"
        "      \"component_type\": \"phone_hero\" | \"app_window\" | \"feature_list\" | \"stat_shock\" | \"metric_counter\" | \"tweet_quote\" | \"split_vs\" | \"code_terminal\" | \"floating_badge\" | \"comparison\" | \"cta_slam\",\n"
        "      \"title_regular\": \"Bagian teks judul biasa\",\n"
        "      \"title_italic\": \"KataKunciMiring\",\n"
        "      \"title_trailing\": \"lanjutan teks biasa\",\n"
        "      \"narration_line\": \"kalimat narasi untuk adegan ini\"\n"
        "    }\n"
        "  ]\n"
        "}"
    )

    user_p = f"Naskah Pengguna:\n{script_text}"
    if theme_hint and theme_hint != "auto":
        user_p += f"\n\nCatatan Tema: Utamakan palet '{theme_hint}'."

    try:
        if ai_brain.is_ai_ready():
            res_str = ai_brain.generate_text(
                system_prompt=sys_prompt,
                user_prompt=user_p,
                json_mode=True,
                timeout=12
            )
            cleaned = res_str.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r"^```[a-zA-Z]*\n", "", cleaned)
                cleaned = re.sub(r"\n```$", "", cleaned)
            data = json.loads(cleaned)
            if data.get("scenes") and len(data["scenes"]) >= 2:
                if not data.get("narration_script"):
                    data["narration_script"] = script_text
                return data
    except Exception as e:
        print(f"[AI Visual Director] Model offline / error: {e}. Menggunakan Dynamic Heuristic Storyboard.")

    # Fallback ke Dynamic Heuristic Storyboard yang menganalisis teks pengguna secara dinamis
    return build_dynamic_heuristic_storyboard(script_text, theme_hint=theme_hint)
