"""
ClipperAI Studio - Master AI Visual & Storyboard Presets Engine
Di-reverse-engineer & dikembangkan dari arsitektur commercial prompt engine ArmagicFlow.

Menyediakan generator master prompt tingkat lanjut untuk:
1. High-CTR Commercial Thumbnails (YouTube 16:9, Shorts/Reels 9:16, TikTok 3:4, IG 1:1)
2. Viral Hooks, Captions, CTAs, & Hashtags (10 variasi hook percakapan alami)
3. Storyboard Video Narration & Kinetic Typography (Multi-part naskah VO 26-28 kata + power words)
4. Commercial Product Studio (Marble podium, Zen stones, Cyberpunk dark mirror, Golden hour)
5. Indonesian Culinary & Menu Resto UMKM (Uap panas, mozzarella stretch, gerabah daun pisang, macro)
6. 3D Figurine & Designer Toy Studio (Pop Mart / Molly, Funko Pop, Action Figure, Nendoroid, Mecha)
7. Virtual Try-On & Mockup Apparel (Presisi identitas wajah 100%, fitting baju/aksesoris)
8. Banner Promo & Booth Bazaar UMKM (3D badges, Halal cert, promo warung kekinian)
9. Desain Interior & Rumah (Japandi, Scandinavian, Modern Tropical, Industrial)
10. Character Turnaround Sheet & Karikatur 3D (3 sudut pandang karakter konsisten)
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional


# ==============================================================================
# 1. HIGH-CTR THUMBNAIL ENGINE
# ==============================================================================

THUMBNAIL_RATIOS = {
    "16:9": "horizontal 16:9 widescreen aspect ratio (1920x1080), perfectly formatted for YouTube video desktop and mobile thumbnails",
    "9:16": "full vertical 9:16 aspect ratio (1080x1920), formatted for YouTube Shorts, TikTok Feed, and Instagram Reels full-screen cover",
    "3:4": "vertical 3:4 aspect ratio (1080x1440), perfectly formatted for official TikTok video cover thumbnail and FYP cards",
    "1:1": "square 1:1 aspect ratio (1080x1080), formatted for Instagram feed and square social posts"
}

THUMBNAIL_VISUAL_STYLES = {
    "high_ctr_commercial": "High-CTR commercial social media style with vivid lighting, crisp contrast, dynamic shadows, and scroll-stopping focal composition",
    "wealth_luxury": "Executive business and wealth luxury style with sleek dark navy and gold metallic accents, clean modern minimalism, and high-end commercial elegance",
    "cyberpunk_neon": "Dramatic cyberpunk esports style with glowing cyan and magenta neon rim lighting, energetic aura, volumetric smoke, and high contrast",
    "ecommerce_flash_sale": "E-Commerce Flash Sale style with 3D sale badges, bold discount tags, professional commercial product lighting, and explosive energetic composition",
    "educational_documentary": "Curiosity-inducing mystery and educational documentary thumbnail style with dramatic cinematic spotlight, intriguing dark background, and high curiosity tension",
    "islamic_cinematic": "Spiritual, calming Islamic cinematic aesthetic with soft golden amber glow, subtle geometric arabesque silhouettes, warm ambient depth, and emotional resonance"
}

THUMBNAIL_TYPOGRAPHY_STYLES = {
    "bold_3d_bevel": "Bold 3D high-CTR commercial typography with strong visual hierarchy, sharp polished bevels, realistic contact shadows, and vibrant studio lighting",
    "cyberpunk_extruded": "3D futuristic extruded cyberpunk typography with glowing neon laser rims (cyan/magenta), inner tube illumination, deep ambient glow, and metallic sides",
    "luxury_gold": "3D metallic polished gold typography with fine reflections, subtle precision drop shadow, sleek kerning, and understated elegance",
    "floating_glassmorphism": "3D translucent frosted glassmorphism typography pill badge with glossy specular edge highlights, soft ambient blur, and crisp inner glow",
    "neon_glow": "Vibrant glowing neon tube typography with realistic electric radiance, subtle tube reflections, and atmospheric color bleed"
}

def build_thumbnail_prompt(
    headline: str,
    subheadline: str = "",
    ratio: str = "16:9",
    visual_style: str = "high_ctr_commercial",
    typo_style: str = "bold_3d_bevel",
    subject_theme: str = ""
) -> str:
    """Menyusun master prompt thumbnail berstandar agency advertising."""
    ratio_desc = THUMBNAIL_RATIOS.get(ratio, THUMBNAIL_RATIOS["16:9"])
    vis_desc = THUMBNAIL_VISUAL_STYLES.get(visual_style, THUMBNAIL_VISUAL_STYLES["high_ctr_commercial"])
    typo_desc = THUMBNAIL_TYPOGRAPHY_STYLES.get(typo_style, THUMBNAIL_TYPOGRAPHY_STYLES["bold_3d_bevel"])
    theme_desc = subject_theme.strip() if subject_theme else "Compelling central human subject with expressive emotional hook and strong visual intrigue"

    headline_rule = f'Primary Big Headline 3D Text: "{headline.strip()}" (Render ONLY this exact headline in huge bold 3D letters)' if headline else 'Primary Big Headline: Create a catchy, high-CTR 2-4 word viral title matching the image theme.'
    sub_rule = f'Secondary Subheadline Badge Text: "{subheadline.strip()}" (Render in small sub-badge under the main headline)' if subheadline else 'NO secondary subheadline text. Do not invent extra subtitle banners.'

    return (
        f"Create an ultra-high quality, high-CTR social media commercial thumbnail in 8K UHD.\n\n"
        f"FORMAT & RATIO:\nGenerate ONE high-CTR commercial thumbnail in {ratio_desc}.\n\n"
        f"CENTRAL SUBJECT & THEME:\n{theme_desc}.\n\n"
        f"VISUAL AESTHETIC & THEME:\n{vis_desc}.\n\n"
        f"3D TEXT TYPOGRAPHY RENDERING STYLE:\n{typo_desc}.\n\n"
        f"EXACT TEXT TO RENDER:\n- {headline_rule}\n- {sub_rule}\n\n"
        f"CRITICAL RULES:\n"
        f"1. NEVER render the name of the style preset, font style name, or dropdown category names as text on the image.\n"
        f"2. Render ONLY the specified headline/subheadline text.\n"
        f"3. Ensure the text is 100% legible, beautifully integrated into the 3D scene, with stunning depth of field and premium commercial quality.\n"
        f"4. Strictly output an authentic photorealistic 8K UHD graphic masterpiece. Do NOT produce low-resolution, blurry, or distorted graphics."
    )


# ==============================================================================
# 2. VIRAL HOOK & CAPTION ENGINE
# ==============================================================================

HOOK_FORMULAS = {
    "campuran_terbaik": "Campuran Berbagai Gaya Hook (Penasaran, Problem-Solusi, FOMO, Pertanyaan Menantang, Debunking Mitos)",
    "penasaran": "Fokus pada Rasa Penasaran & Rahasia yang Membuat Penonton Wajib Nonton Sampai Habis",
    "problem_solusi": "Fokus pada Masalah Terbesar Audiens & Menawarkan Solusi Cepat/Mudah",
    "fomo_urgensi": "Fokus pada Urgensi, FOMO, Tren Viral, dan Kelangkaan Waktu/Stok",
    "opini_kontroversial": "Fokus pada Pernyataan Berlawanan Mitos / Opini Berbeda yang Memancing Diskusi & Komentar"
}

def build_hook_caption_system_prompt(topic: str, niche: str = "Umum", formula: str = "campuran_terbaik", tone: str = "Santai") -> str:
    """Menyusun system prompt AI Copywriting untuk 10 Hooks + Caption + CTA + Hashtags."""
    formula_desc = HOOK_FORMULAS.get(formula, HOOK_FORMULAS["campuran_terbaik"])
    return (
        f"Kamu adalah copywriter profesional dan pakar viral marketing untuk TikTok, Instagram Reels, dan YouTube Shorts.\n"
        f"Tugas: Buat 10 pilihan HOOK pembuka (3 detik pertama yang bikin penonton berhenti scroll) + CAPTION viral + CALL TO ACTION (CTA) + HASHTAGS populer berdasarkan input produk/topik.\n\n"
        f"Input:\n"
        f"- Topik / Produk: {topic}\n"
        f"- Niche / Kategori: {niche}\n"
        f"- Gaya / Formula Hook: {formula_desc}\n"
        f"- Tone of Voice: {tone}\n\n"
        f"Aturan KONTEN (WAJIB):\n"
        f"1. Buat TEPAT 10 variasi HOOK pembuka yang sangat menarik & memicu rasa penasaran sesuai gaya ({formula_desc}). Tulis kalimat percakapan yang alami, santai, dan gaul Bahasa Indonesia.\n"
        f"2. DILARANG KERAS menyelipkan kata/frasa 'Formula', 'Campuran Terbaik', 'Hook', atau nama instruksi ini di dalam teks Hook maupun Caption. Tulis murni kalimat yang diucapkan kreator di depan kamera!\n"
        f"3. Setiap Hook harus BERBEDA variasi sudut pandangnya (ada pertanyaan, pernyataan mengagetkan, problem-solusi, fakta unik, dll).\n"
        f"4. Buat 1 CAPTION lengkap Bahasa Indonesia yang terstruktur rapi (Hook singkat -> Penjelasan Value -> Call To Action / CTA).\n"
        f"5. Buat 1 CALL TO ACTION (CTA) singkat yang persuasif (contoh: 'Yuk klik keranjang kuning sekarang sebelum kehabisan!', 'Save video ini biar gak lupa!').\n"
        f"6. Buat 10-15 HASHTAGS relevan & trending (dipisah spasi).\n\n"
        f"Aturan OUTPUT (WAJIB):\n"
        f"1. Jawaban HANYA di dalam satu code block ```json ... ```.\n"
        f"2. Di luar code block JANGAN ada teks apapun.\n"
        f"3. Struktur JSON PERSIS seperti ini:\n"
        f'{{"hooks": ["Hook 1...", "Hook 2...", "Hook 3...", "Hook 4...", "Hook 5...", "Hook 6...", "Hook 7...", "Hook 8...", "Hook 9...", "Hook 10..."], "caption": "...", "cta": "...", "hashtags": "..."}}\n'
        f"4. Tulis JSON valid dalam format clean JSON."
    )


# ==============================================================================
# 3. STORYBOARD NARRATION & KINETIC SCRIPT ENGINE
# ==============================================================================

def build_storyboard_script_prompt(
    product_or_topic: str,
    duration_sec: int = 30,
    kinetic_style: str = "Bold Impact",
    niche: str = "Umum"
) -> str:
    """
    Menyusun prompt pembuatan naskah video per-scene (10 detik per part)
    lengkap dengan kata kunci Kinetic Typography untuk visual subtitle.
    """
    num_parts = max(2, min(12, duration_sec // 10))
    return (
        f"Kamu adalah sutradara video pendek & scriptwriter spesialis TikTok & Reels commercial ads.\n"
        f"Tugas: Buat naskah video berdurasi {duration_sec} detik yang dibagi menjadi TEPAT {num_parts} part (masing-masing part berdurasi 10 detik).\n\n"
        f"Input:\n"
        f"- Nama Produk / Topik: {product_or_topic}\n"
        f"- Niche: {niche}\n"
        f"- Gaya Kinetic Typography: {kinetic_style}\n"
        f"- Jumlah Part: {num_parts} part\n\n"
        f"Aturan Voice Over per Part (WAJIB):\n"
        f"1. SETIAP part WAJIB berisi TEPAT 24-28 kata (standar kecepatan bicara 10 detik agar pas & natural).\n"
        f"2. Struktur alur narasi berkesinambungan:\n"
        f"   - Part 1: HOOK / PEMBUKA (3 detik pertama memikat rasa penasaran)\n"
        f"   - Part 2-{num_parts-1}: PROBLEM, VALUE, & SOLUSI NYATA\n"
        f"   - Part {num_parts}: CALL TO ACTION (CTA) & PENUTUP KUAT\n"
        f"3. Tentukan delivery type untuk tiap part: 'Talking Head' atau 'B-Roll'.\n"
        f"4. Tentukan TEPAT 3-4 kata KINETIC TYPOGRAPHY per part (power words, angka/harga, atau frasa penegas) yang diambil PERSIS dari teks audio part tersebut.\n\n"
        f"Aturan Output (WAJIB):\n"
        f"Hasilkan HANYA satu code block ```json ... ``` dengan struktur:\n"
        f"{{\n"
        f'  "narasi": [\n'
        f'    {{\n'
        f'      "part_num": 1,\n'
        f'      "title": "HOOK / PEMBUKA",\n'
        f'      "audio": "Teks naskah Voice Over 24-28 kata...",\n'
        f'      "vo_delivery_type": "Talking Head",\n'
        f'      "visual_prompt": "Cinematic visual description in English..."\n'
        f'    }}\n'
        f'  ],\n'
        f'  "kinetic": [\n'
        f'    {{\n'
        f'      "part_num": 1,\n'
        f'      "words": ["KATA1", "KATA2", "KATA3", "KATA4"]\n'
        f'    }}\n'
        f'  ]\n'
        f"}}"
    )


# ==============================================================================
# 4. COMMERCIAL PRODUCT STUDIO ENGINE
# ==============================================================================

PRODUCT_STUDIO_BACKDROPS = {
    "white_marble": "Resting on an opulent white Carrara marble podium with delicate grey veining, flanked by gentle organic palm leaf shadow patterns and soft ambient reflections",
    "zen_stone_wood": "Positioned on a smooth, warm natural teak wood slab accompanied by dark polished river stones, fresh green bamboo leaves, and tranquil minimalist water ripples",
    "cyberpunk_mirror": "Standing on a sleek black glossy mirror surface with vibrant neon cyan and electric violet rim reflections, futuristic dark aesthetic, and volumetric mist",
    "concrete_golden_hour": "Set upon raw textured architectural concrete blocks, illuminated by warm low-angle golden hour sunset rays with dramatic elongated soft shadows",
    "granite_kitchen": "Set on a luxurious modern dark granite kitchen countertop with subtle blurred background bokeh and warm ambient morning lighting",
    "desert_dune": "Nestled in fine textured desert sand dune ripples with warm terracotta pottery tones and rich golden hour backlight"
}

PRODUCT_LIGHTING = {
    "softbox": "Illuminated by high-end commercial dual softbox lighting, providing ultra-clean specular highlights and silky smooth gradient shadows",
    "dramatic_spot": "Lit with an editorial single spotlight focusing directly on the product, deep moody falloff shadows, and high contrast luxury ambiance",
    "golden_hour": "Bathed in warm golden sunlight at a 45-degree angle, generating natural warm glow and luminous edge highlights",
    "rim_neon": "Enhanced with vibrant neon colored rim lights outlining the silhouette with sharp crisp highlights against a deep dark background"
}

def build_product_studio_prompt(
    product_name: str,
    backdrop: str = "white_marble",
    lighting: str = "softbox",
    extra_details: str = "",
    has_ref_image: bool = False
) -> str:
    """Menyusun master prompt fotografi produk komersial 8K UHD."""
    bg_desc = PRODUCT_STUDIO_BACKDROPS.get(backdrop, PRODUCT_STUDIO_BACKDROPS["white_marble"])
    lit_desc = PRODUCT_LIGHTING.get(lighting, PRODUCT_LIGHTING["softbox"])
    ref_instruction = "Faithfully preserve the exact branding, packaging, typography, colors, and bottle/box shape from the reference image." if has_ref_image else f"Featuring '{product_name}' as the hero commercial focal point."

    return (
        f"Create an ultra-detailed, photorealistic commercial product photograph in 8K UHD.\n\n"
        f"HERO SUBJECT:\n{ref_instruction}\n\n"
        f"STUDIO ENVIRONMENT & BACKDROP:\n{bg_desc}.\n\n"
        f"LIGHTING & ATMOSPHERE:\n{lit_desc}.\n\n"
        f"ADDITIONAL COMMERCIAL DETAILS:\n{extra_details or 'Glistening micro water droplets, pristine surface finish, crisp optical clarity, and award-winning advertising agency composition.'}\n\n"
        f"Strictly output a photorealistic masterpiece 8K UHD commercial product photograph with authentic reflections and depth of field. Do NOT generate CGI, cartoon, or illustration artifacts."
    )


# ==============================================================================
# 5. INDONESIAN CULINARY & RESTO UMKM ENGINE
# ==============================================================================

CULINARY_SERVING_EFFECTS = {
    "uap_panas": "Wisps of fresh hot steam rising gracefully off the piping hot food, with glistening chili sambal oil and crispy golden fried shallots (bawang goreng)",
    "mozzarella": "Featuring a mouthwatering stretch of melted gooey mozzarella cheese pulling away with rich generous savory toppings",
    "gerabah_daun_pisang": "Served authentically on traditional terracotta earthenware pottery (piring gerabah) lined with fresh glossy banana leaf and crisp fresh lalapan kemangi leaves",
    "meja_kafe_estetik": "Presented on a rustic warm wooden cafe tabletop beside aesthetic ceramic cups, linen napkin, and lush green indoor potted plants",
    "gelas_berembun": "Served with frosted sweating glass with crystal-clear ice cubes, condensation water droplets, and refreshing liquid splash"
}

CULINARY_CAMERA_ANGLES = {
    "hero_45": "Captured at a classic 45-degree hero diner eye-level angle with creamy soft background bokeh",
    "flatlay_90": "Captured in a flat-lay top-down 90-degree overhead composition with balanced side dishes, condiments, and rustic cutlery",
    "macro_closeup": "Captured in an extreme macro close-up focus highlighting the juicy, crispy, appetizing texture and glaze of the dish"
}

def build_kuliner_umkm_prompt(
    dish_name: str,
    serving_effect: str = "uap_panas",
    camera_angle: str = "hero_45",
    extra_details: str = "",
    has_ref_image: bool = False
) -> str:
    """Menyusun master prompt foto kuliner dan menu resto UMKM 8K UHD."""
    serv_desc = CULINARY_SERVING_EFFECTS.get(serving_effect, CULINARY_SERVING_EFFECTS["uap_panas"])
    cam_desc = CULINARY_CAMERA_ANGLES.get(camera_angle, CULINARY_CAMERA_ANGLES["hero_45"])
    ref_instruction = "Faithfully preserve the core Indonesian dish, food texture, spices, and ingredients from the reference image." if has_ref_image else f"Featuring a mouth-watering authentic Indonesian dish '{dish_name}'."

    return (
        f"Create a mouth-watering, ultra-delicious commercial food and culinary photograph in 8K UHD.\n\n"
        f"DISH & FOOD TEXTURE:\n{ref_instruction}\n\n"
        f"APPETIZING SERVING EFFECTS:\n{serv_desc}.\n\n"
        f"CAMERA ANGLE & COMPOSITION:\n{cam_desc}.\n\n"
        f"CULINARY DETAILS:\n{extra_details or 'Glistening glaze, vibrant fresh chili red sambal, golden brown crispiness, and five-star restaurant gourmet plating.'}\n\n"
        f"Strictly output an authentic photorealistic 8K UHD culinary studio masterpiece with appetizing warm golden lighting. Do NOT produce 3D CGI, illustrations, cartoons, or fake unappetizing graphics."
    )


# ==============================================================================
# 6. 3D FIGURINE & DESIGNER TOY ENGINE
# ==============================================================================

FIGURINE_STYLES = {
    "pop_mart": "Styled in authentic Pop Mart / Molly blind box designer toy aesthetic: cute chibi proportions, smooth rounded edges, large expressive glossy glass eyes, and delicate painted detailing",
    "funko_pop": "Styled as an authentic Funko Pop vinyl figure: oversized squarish head, iconic solid black circular button eyes, compact stylized body, and signature vinyl silhouette",
    "action_figure": "Styled as a highly-detailed 1/6 scale collectible action figure with realistic fabric textures, articulation seams, intricate accessories, and lifelike facial sculpting",
    "claymation": "Styled in charming claymation stop-motion aesthetic with subtle handcrafted thumbprint textures, tactile soft clay sheen, and playful whimsical anatomy",
    "crystal_acrylic": "Crafted from transparent crystal-clear colored acrylic and resin with vibrant internal light refractions, smooth polished facets, and glossy highlights",
    "cyberpunk_mecha": "Styled as a futuristic chibi cyberpunk mecha toy with mini robotic armor plates, LED glowing circuit trims, and metallic paneling",
    "nendoroid": "Styled as an authentic Nendoroid chibi anime figure with oversized head, swappable cheerful anime expression, and clear plastic display stand"
}

FIGURINE_PACKAGING = {
    "blister_box": "Packaged inside a pristine commercial blister pack toy box with custom illustrated backing card, clear plastic bubble dome, and Japanese/English typography badges",
    "acrylic_case": "Showcased inside a modern museum-grade clear acrylic display box on a matte black pedestal with miniature warm LED spotlight illumination",
    "creator_desk": "Displayed proudly on a clean aesthetic minimalist wooden creator desk next to a mechanical keyboard with warm ambient desk lamp lighting",
    "turntable": "Resting on a clean white motorized collector turntable inside a high-end designer toy gallery"
}

def build_figurine_3d_prompt(
    character_desc: str,
    toy_style: str = "pop_mart",
    packaging: str = "creator_desk",
    material: str = "Smooth matte vinyl with gloss highlights",
    extra_details: str = "",
    has_ref_image: bool = False
) -> str:
    """Menyusun master prompt 3D Figurine, Pop Mart & Chibi Toy."""
    style_desc = FIGURINE_STYLES.get(toy_style, FIGURINE_STYLES["pop_mart"])
    pack_desc = FIGURINE_PACKAGING.get(packaging, FIGURINE_PACKAGING["creator_desk"])
    ref_instruction = "Transform the person/character from the reference image into a collectible designer toy, preserving their key hairstyle, facial likeness, clothing colors, and iconic traits." if has_ref_image else f"Collectible designer toy character: {character_desc}."

    return (
        f"Create an ultra-detailed, photorealistic commercial product photograph of a collectible 3D designer toy figure in 8K UHD.\n\n"
        f"CHARACTER DESIGN & FIGURE:\n{ref_instruction}\n\n"
        f"TOY STYLE & AESTHETIC:\n{style_desc}.\n\n"
        f"PACKAGING & DISPLAY SETTING:\n{pack_desc}.\n\n"
        f"MATERIAL & FINISH:\n{material}.\n\n"
        f"EXTRA DETAILS:\n{extra_details or 'Crisp plastic seams, authentic toy scale depth of field, delicate miniature accessories, and warm studio lighting.'}\n\n"
        f"Strictly output a photorealistic masterpiece 8K UHD studio photograph of the physical toy with authentic plastic/resin material reflections and miniature depth of field. Do NOT generate 2D flat illustrations."
    )


# ==============================================================================
# 7. VIRTUAL TRY-ON & APPAREL ENGINE
# ==============================================================================

def build_virtual_tryon_prompt(
    garment_description: str,
    custom_notes: str = ""
) -> str:
    """
    Menyusun prompt Reference-to-Image (R2I) Virtual Try-On OOTD presisi.
    Gambar 1 = Foto Model / Orang Asli.
    Gambar 2 = Foto Produk Pakaian / Aksesoris.
    """
    return (
        f"Lakukan VIRTUAL TRY-ON (ganti pakaian & pasangkan aksesoris pada foto model) secara presisi.\n\n"
        f"SUMBER GAMBAR:\n"
        f"- Gambar 1 = Foto Model Utama / Subjek Orang.\n"
        f"- Gambar 2+ = Foto Produk / Pakaian / Aksesoris ({garment_description}).\n\n"
        f"INSTRUKSI UTAMA:\n"
        f"1. Pertahankan 100% bentuk wajah, identitas, warna kulit, ekspresi, postur tubuh, dan latar belakang asli dari Foto Model (Gambar 1).\n"
        f"2. Ganti pakaian & pasangkan SELURUH item produk dari Gambar 2+ pada tubuh/wajah model secara pas, presisi, dan realistis mengikuti lekuk tubuh dan lipatan kain alami.\n"
        f"3. Hasilkan 1 GAMBAR HASIL VIRTUAL TRY-ON OOTD BARU beresolusi tinggi, tajam, photorealistic, tanpa cacat visual pada sambungan leher, lengan, atau pinggang.\n"
        f"4. Catatan kustom tambahan: {custom_notes or 'Pencahayaan baju disesuaikan dengan lighting ruangan asli model, tekstur kain tampak nyata dan jatuh dengan luwes.'}\n\n"
        f"Strictly output a single seamless 8K UHD photorealistic image."
    )


# ==============================================================================
# 8. BANNER PROMO & UMKM BAZAAR ENGINE
# ==============================================================================

BANNER_FORMATS = {
    "social_square": "Square 1:1 format for Instagram & Facebook feed promo feeds",
    "story_portrait": "Vertical 9:16 format for TikTok, Instagram Stories, and WhatsApp status ads",
    "spanduk_landscape": "Ultra-wide panoramic horizontal landscape banner layout (specifically proportioned for physical street banners 3m x 1m)",
    "xbanner_standing": "Tall vertical standing X-banner / roll-up banner layout (proportioned 1:2.5 for 60x160cm physical indoor display)"
}

def build_banner_promo_prompt(
    business_name: str,
    promo_text: str,
    format_type: str = "social_square",
    color_scheme: str = "Kuning Merah Berani (High Contrast UMKM)",
    extra_details: str = "",
    has_ref_image: bool = False
) -> str:
    """Menyusun master prompt desain banner promosi komersial UMKM."""
    fmt_desc = BANNER_FORMATS.get(format_type, BANNER_FORMATS["social_square"])
    ref_inst = f"Incorporate the product photo and logo branding from the reference image cleanly into the banner focal point." if has_ref_image else f"Featuring product and branding for '{business_name}'."

    return (
        f"Design a vibrant, high-converting commercial promotional sales banner in 8K UHD for Indonesian local businesses (UMKM).\n\n"
        f"LAYOUT & FORMAT:\n{fmt_desc}.\n\n"
        f"BRAND & PROMOTIONAL FOCUS:\n{ref_inst}\n\n"
        f"PROMOTIONAL HEADLINE & OFFER:\n'{promo_text}'. Prominently designed with bold 3D typography badges, discount tags, and engaging promotional elements.\n\n"
        f"COLOR SCHEME & VIBE:\n{color_scheme} with high contrast and eye-catching modern advertising gradients.\n\n"
        f"ADDITIONAL BADGES:\n{extra_details or 'Include certified Halal logo accent, 100% Homemade badge, star rating icons, and clean contact/order icons.'}\n\n"
        f"Ensure modern graphic design layout, crisp 3D promo badges, clean shadows, and vibrant colors suitable for social media advertising."
    )


# ==============================================================================
# 9. ARCHITECTURAL & INTERIOR DESIGN ENGINE
# ==============================================================================

INTERIOR_STYLES = {
    "japandi": "Japandi aesthetic combining Japanese wabi-sabi minimalism with Scandinavian warmth: light oak wood, tatami textures, neutral off-white tones, and clean lines",
    "scandinavian": "Scandinavian modern style with airy open spaces, crisp white walls, warm blond wood accents, soft grey wool textiles, and gentle natural lighting",
    "industrial_loft": "Industrial loft design with exposed red brick walls, matte black steel frames, polished concrete floors, and warm Edison bulb lighting",
    "tropical_villa": "Bali-inspired modern tropical villa aesthetic with open-air concept, lush indoor monstera plants, natural stone accents, and pool reflections",
    "luxury_classic": "Modern luxury classical interior with white crown moldings, gold brass fixtures, crystal chandelier, and plush velvet furniture"
}

def build_desain_rumah_prompt(
    room_type: str = "Ruang Tamu (Living Room)",
    interior_style: str = "japandi",
    lighting: str = "Daylight natural sunlight pouring through large floor-to-ceiling windows",
    extra_details: str = ""
) -> str:
    """Menyusun master prompt arsitektur dan interior desain photorealistic 8K."""
    style_desc = INTERIOR_STYLES.get(interior_style, INTERIOR_STYLES["japandi"])

    return (
        f"Create an award-winning architectural interior design photograph in 8K UHD.\n\n"
        f"ROOM TYPE:\n{room_type}.\n\n"
        f"AESTHETIC STYLE:\n{style_desc}.\n\n"
        f"LIGHTING & ATMOSPHERE:\n{lighting}.\n\n"
        f"ARCHITECTURAL DETAILS:\n{extra_details or 'Architectural Digest feature quality, ultra-realistic textures, balanced perspective lines, and elegant spatial staging.'}\n\n"
        f"Strictly output a photorealistic 8K UHD architectural render with physically-based lighting and materials. Do NOT create cartoon or low-detail graphics."
    )


# ==============================================================================
# 10. CHARACTER TURNAROUND SHEET ENGINE
# ==============================================================================

def build_character_sheet_prompt(
    character_name: str,
    character_description: str,
    visual_style: str = "3D Pixar / Disney Cinematic Animation",
    costume: str = "Casual modern streetwear"
) -> str:
    """Menyusun master prompt Character Model Sheet / Turnaround (Front, Side, Close-up)."""
    return (
        f"You are an expert AI character design & prompt engineer.\n"
        f"Generate a complete, highly detailed character reference model sheet in 8K UHD based on:\n\n"
        f"- Character Name: {character_name}\n"
        f"- Description: {character_description}\n"
        f"- Visual Style: {visual_style}\n"
        f"- Costume & Outfits: {costume}\n\n"
        f"SHEET LAYOUT:\n"
        f"Character turnaround sheet format showing multiple angles side-by-side on a clean neutral light grey background:\n"
        f"1. Full-body Front View\n"
        f"2. Full-body 3/4 Perspective Angle\n"
        f"3. Full-body Side Profile View\n"
        f"4. Detailed Close-up Facial Expression Portrait\n\n"
        f"CRITICAL CONSISTENCY:\n"
        f"Ensure 100% visual consistency across all views: identical facial features, eye color, hairstyle, body proportions, clothing patterns, and color palette.\n\n"
        f"Strictly output a clean, high-resolution 8K character model sheet suitable for 3D modeling and animation production."
    )


# ==============================================================================
# PRESET REGISTRY & CATALOG
# ==============================================================================

STUDIO_CATALOG = {
    "thumbnail": {
        "title": "High-CTR Social Thumbnail",
        "description": "Thumbnail komersial berstandar agency (YouTube 16:9, Shorts/Reels 9:16, TikTok 3:4, IG 1:1)",
        "ratios": list(THUMBNAIL_RATIOS.keys()),
        "styles": list(THUMBNAIL_VISUAL_STYLES.keys()),
        "typo_styles": list(THUMBNAIL_TYPOGRAPHY_STYLES.keys())
    },
    "hook_caption": {
        "title": "Viral Hook & Caption Generator",
        "description": "10 Variasi Hook 3-detik pertama + Caption + CTA + Hashtags terstruktur",
        "formulas": list(HOOK_FORMULAS.keys())
    },
    "product_studio": {
        "title": "Commercial Product Studio AI",
        "description": "Foto produk e-commerce & affiliate mewah dengan podium marmer, zen stones, & cyberpunk glow",
        "backdrops": list(PRODUCT_STUDIO_BACKDROPS.keys()),
        "lightings": list(PRODUCT_LIGHTING.keys())
    },
    "kuliner_umkm": {
        "title": "Foto Kuliner Resto & UMKM AI",
        "description": "Foto makanan menggiurkan dengan uap panas, tarikan keju mozzarella, & piring gerabah tradisional",
        "effects": list(CULINARY_SERVING_EFFECTS.keys()),
        "angles": list(CULINARY_CAMERA_ANGLES.keys())
    },
    "figurine_3d": {
        "title": "3D Figurine & Pop Mart AI",
        "description": "Transformasi karakter/orang jadi mainan koleksi 3D (Pop Mart, Funko Pop, Action Figure, Nendoroid)",
        "styles": list(FIGURINE_STYLES.keys()),
        "packagings": list(FIGURINE_PACKAGING.keys())
    },
    "virtual_tryon": {
        "title": "Virtual Try-On & OOTD Fitting",
        "description": "Ganti baju & pasangkan aksesoris ke foto model dengan mempertahankan 100% wajah asli"
    },
    "banner_promo": {
        "title": "Banner Promo & Warung UMKM AI",
        "description": "Desain spanduk promosi, diskon warung, dan banner medsos dengan badge 3D dan logo Halal",
        "formats": list(BANNER_FORMATS.keys())
    },
    "desain_rumah": {
        "title": "Desain Rumah & Interior Japandi AI",
        "description": "Arsitektur ruangan modern photorealistic (Japandi, Scandinavian, Bali Villa, Industrial)",
        "styles": list(INTERIOR_STYLES.keys())
    },
    "character_sheet": {
        "title": "Character Turnaround Sheet AI",
        "description": "Model sheet karakter konsisten dari depan, samping, dan close-up untuk animasi/storyboard"
    }
}
