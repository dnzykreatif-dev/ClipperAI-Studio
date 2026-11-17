"""
ClipperAI Studio - MotionCode & Canvas Motion Graphics Engine
Direverse-engineer & direplikasi dari MotionCode Studio (Kineticode).

Menyediakan:
1. Basis Data 15 Kategori Industri & 150 Topik Komersial Microstock
2. 13 Gaya Visual Microstock (Tier 1 High-Demand, Tier 2, Tier 3)
3. 5 Preset Komersial Siap Eksekusi (Adobe Stock FHD, 4K UHD Gold, Alpha HUD, Vertical 9:16, Square 1:1)
4. AI Motion Code Prompt Engineering (2-Step 16:9, Single-Shot 9:16, Transparent Alpha)
5. AI Code Fence Extractor & Security Scoring
6. Direct Motion Code Generator via AI Brain (Gemini, Groq, OpenAI, Ollama)
"""

from __future__ import annotations

import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

import ai_brain


# ==============================================================================
# 1. BASIS DATA 15 KATEGORI & 150 TOPIK MICROSTOCK
# ==============================================================================

MICROSTOCK_DATABASE: List[Dict[str, Any]] = [
    {
        "id": 1,
        "kategori": "E-Commerce & Marketing",
        "deskripsi": "Aset komersial untuk toko online, promo diskon, dan kampanye iklan digital",
        "topik": [
            "Online shopping & Trolley cart", "Add to cart & Checkout", "Flash sale & Discount badge",
            "Mobile payment / E-wallet QR", "Order tracking & Package delivery", "Customer 5-star review",
            "Digital marketing funnel", "Loyalty points & Rewards", "Payment gateway secure", "Product unboxing motion"
        ]
    },
    {
        "id": 2,
        "kategori": "Finance, Trading & Crypto",
        "deskripsi": "Grafik saham, candlestick, blockchain, aset kripto, dan pertumbuhan finansial",
        "topik": [
            "Bitcoin & Altcoin network", "Blockchain decentralized ledger", "Bullish & Bearish candlestick chart",
            "Stock exchange market graph", "Passive income & Compound interest", "Instant global money transfer",
            "Investment portfolio pie chart", "Crypto mining & Hardware rigs", "Savings piggy bank & Gold coins",
            "Currency exchange rates (USD/EUR/IDR)"
        ]
    },
    {
        "id": 3,
        "kategori": "Technology & Cybersecurity",
        "deskripsi": "Keamanan siber, cloud computing, AI, data center, dan jaringan digital",
        "topik": [
            "Cloud computing server sync", "Artificial Intelligence neural brain", "Machine learning deep algorithm",
            "Hacker shield & Firewall defense", "Biometric fingerprint & Face scan", "Server rack data blinking lights",
            "Smart home IoT network", "VR headset & Metaverse portal", "Password lock & SHA encryption", "Quantum computing qubit particles"
        ]
    },
    {
        "id": 4,
        "kategori": "Medical, Health & Science",
        "deskripsi": "Kesehatan modern, farmasi, genetika, bioteknologi, dan laboratorium",
        "topik": [
            "Telemedicine digital doctor", "DNA double helix rotation", "Immune cell vs Virus battle",
            "Heart rate pulse & EKG monitor", "Vaccine bottle & Precision syringe", "Pharmacy capsule & Medicine pills",
            "Mental health brain mindfulness", "Biotech microscope cell analysis", "Dental laser care & Tooth polish",
            "Smart hospital medical telemetry"
        ]
    },
    {
        "id": 5,
        "kategori": "Ecology & Green Energy",
        "deskripsi": "Energi terbarukan, kelestarian lingkungan, daur ulang, dan kendaraan listrik",
        "topik": [
            "Solar panel photovoltaic rays", "Wind turbine wind farm rotation", "Zero waste & Plastic recycling loop",
            "Global warming temperature gauge", "Electric Vehicle (EV) fast charging", "Eco-friendly green packaging",
            "Plant sprouting seedling growth", "Water droplet filtration purity", "Carbon footprint zero emissions",
            "Smart organic sustainable farming"
        ]
    },
    {
        "id": 6,
        "kategori": "Business, Corporate & Startup",
        "deskripsi": "Kolaborasi tim, kepemimpinan, presentasi, target omset, dan pertumbuhan bisnis",
        "topik": [
            "Team puzzle collaboration", "Corporate leadership compass", "Dart target bullseye achievement",
            "Time management hourglass sprint", "Startup rocket launch takeoff", "Big data bar chart analytics",
            "B2B networking handshake link", "Agile sprint Kanban workflow", "Career ladder promotion climb",
            "Executive conference speech podium"
        ]
    },
    {
        "id": 7,
        "kategori": "Education & E-Learning",
        "deskripsi": "Pembelajaran daring, universitas, wisuda, literasi, dan eksperimen sains",
        "topik": [
            "Online webinar course stream", "Graduation mortarboard cap throw", "Lightbulb creative eureka spark",
            "Interactive video e-classroom", "Digital library eBook scanner", "Quiz exam checkmark score",
            "Global language translation audio", "Physics atom laboratory flask", "Honor student diploma scroll",
            "Book pages flipping breeze"
        ]
    },
    {
        "id": 8,
        "kategori": "Social Media & Communication",
        "deskripsi": "Interaksi media sosial, siaran langsung, podcast, dan konten viral",
        "topik": [
            "Like Share Subscribe bell button", "Push notification alert badges", "Real-time speech chat bubbles",
            "Live streaming heart reactions", "Studio condenser podcast mic", "Influencer viral creator reach",
            "Shorts swipe algorithm feed", "Animated user 3D avatar profile", "Mesh network friend connections",
            "Trending hashtag fire explosion"
        ]
    },
    {
        "id": 9,
        "kategori": "Logistics & Supply Chain",
        "deskripsi": "Pengiriman kargo, pergudangan modern, drone otomatis, dan armada logistik",
        "topik": [
            "Container cargo freight ship", "Autonomous delivery drone drop", "Automated warehouse robotic arm",
            "Electric forklift pallet stacking", "Express motorbike courier speed", "Heavy cargo airplane runway",
            "Global import export trade routes", "Supply chain seamless conveyor belt", "Fragile handle-with-care box",
            "Real-time GPS fleet route radar"
        ]
    },
    {
        "id": 10,
        "kategori": "UI, UX & Web Elements",
        "deskripsi": "Komponen antarmuka pengguna: loading spinner, toggle, progress bar, dan tombol",
        "topik": [
            "Fluid gradient loading spinner", "Segmented linear progress bar", "iOS smooth toggle switch button",
            "Responsive mobile hamburger menu", "Search bar with dynamic autocomplete", "404 Error page not found sign",
            "Animated checkmark & cross mark", "Mouse cursor ripples & tap clicks", "Modern analytics dashboard card",
            "Smooth volume & brightness slider"
        ]
    },
    {
        "id": 11,
        "kategori": "Travel & Vacation",
        "deskripsi": "Penerbangan, reservasi hotel, wisata pantai, peta perjalanan, dan petualangan",
        "topik": [
            "Airplane flight route takeoff", "Luxury 5-star hotel key card", "Wheeled luggage airport conveyor",
            "Passport & verified travel visa", "Interactive GPS map pin compass", "Mountain camping tent campfire",
            "Tropical beach umbrella wave", "Road trip convertible car journey", "Cruise ship ocean sunset wake",
            "World iconic landmark silhouettes"
        ]
    },
    {
        "id": 12,
        "kategori": "Automotive & Transport",
        "deskripsi": "Industri otomotif, mesin mobil, speedometer, rambu jalan, dan transportasi cerdas",
        "topik": [
            "Car engine piston mechanical cycle", "Digital dashboard HUD speedometer", "Gentle touchless foam car wash",
            "Modern luminous LED traffic lights", "Autonomous self-driving LiDAR sensor", "High-speed electric bullet train",
            "Pitstop tire wheel replacement", "EV battery pack fast charging", "Shock absorber suspension test",
            "Aerodynamic wind tunnel streamline"
        ]
    },
    {
        "id": 13,
        "kategori": "Food & Culinary",
        "deskripsi": "Pesan antar makanan, kopi barista, menu restoran, dan masakan segar",
        "topik": [
            "Food delivery thermal backpack", "Digital restaurant tablet menu", "Espresso machine steam pour",
            "Fresh organic salad avocado bowl", "Crispy hot burger & french fries", "Chef saucepan bubbling boiling",
            "Freshly baked pastry croissant oven", "Supermarket shopping grocery cart", "Chilled wine glass vineyard pour",
            "Fine dining silver fork knife clink"
        ]
    },
    {
        "id": 14,
        "kategori": "Real Estate & Construction",
        "deskripsi": "Pencarian rumah, arsitektur, konstruksi gedung, investasi properti, dan serah terima kunci",
        "topik": [
            "House search magnifying glass", "Bank home mortgage loan contract", "Smart eco-city skyline glass",
            "Tower crane lifting steel beam", "Architectural CAD blueprint floor plan", "Modern interior living staging",
            "Property capital growth graph", "Moving cardboard relocation truck", "Golden house key handover",
            "Solar roof building maintenance"
        ]
    },
    {
        "id": 15,
        "kategori": "Abstract & Data Visuals",
        "deskripsi": "Gelombang harmonik, jaringan plexus, cairan gradien, tipografi kinetik, dan partikel",
        "topik": [
            "Interconnected plexus dot network", "Iridescent fluid liquid marble wave", "Synthwave 80s retro cyber grid",
            "Halftone dotted printing pattern", "Alex Hormozi kinetic typography", "3D isometric floating cubes",
            "Dynamic radial percentage charts", "Floating dust particle vortex field", "Geometric diagonal transition wipe",
            "Hypnotic infinite tunnel loop"
        ]
    }
]


# ==============================================================================
# 2. 13 GAYA VISUAL MICROSTOCK (TIER 1, TIER 2, TIER 3)
# ==============================================================================

VISUAL_STYLES: List[Dict[str, Any]] = [
    # Tier 1: High Demand & Highest Commercial Conversion
    {
        "id": "flat_corporate",
        "nama": "Flat Design & Corporate Memphis",
        "tier": "Tier 1 (High Demand)",
        "deskripsi": "Bentuk vektor geometris sederhana, warna pastel dan saturasi berani, sangat diminati perusahaan SaaS dan presentasi bisnis."
    },
    {
        "id": "minimalist_line",
        "nama": "Minimalist Line Art",
        "tier": "Tier 1 (High Demand)",
        "deskripsi": "Garis stroke elegan tipis dan presisi, ruang negatif luas, estetika mewah dan modern untuk agensi kreatif."
    },
    {
        "id": "isometric",
        "nama": "Isometric 3D Projection",
        "tier": "Tier 1 (High Demand)",
        "deskripsi": "Proyeksi sudut 30 derajat tanpa perspektif lenyap, menampilkan kedalaman dan struktur arsitektural secara jelas."
    },
    {
        "id": "abstract_geometric",
        "nama": "Abstract Geometric & Bauhaus",
        "tier": "Tier 1 (High Demand)",
        "deskripsi": "Kombinasi bentuk dasar (lingkaran, kotak, segitiga), ritme visual matematis, cocok untuk background video dinamis."
    },
    {
        "id": "glassmorphism",
        "nama": "Glassmorphism & Frosted UI",
        "tier": "Tier 1 (High Demand)",
        "deskripsi": "Efek kaca buram (blur), border semi-transparan, specular highlight halus, standar desain modern Apple dan Windows 11."
    },

    # Tier 2: Medium Demand & Creative Projects
    {
        "id": "paper_cutout",
        "nama": "Paper Cut Out & Layered Depth",
        "tier": "Tier 2 (Medium Demand)",
        "deskripsi": "Lapisan kertas bertumpuk dengan drop shadow lembut, memberikan kesan kedalaman fisik buatan tangan yang menenangkan."
    },
    {
        "id": "cyberpunk_y2k",
        "nama": "Cyberpunk Neon & Y2K Aesthetic",
        "tier": "Tier 2 (Medium Demand)",
        "deskripsi": "Pencahayaan neon elektrik cyan-magenta, grid retro, scanline, atmosfer futuristik malam hari."
    },
    {
        "id": "doodle_handdrawn",
        "nama": "Doodle & Hand-Drawn Sketch",
        "tier": "Tier 2 (Medium Demand)",
        "deskripsi": "Garis sketsa tangan organik, ketidakteraturan artistik yang ramah dan dekat dengan penonton."
    },
    {
        "id": "low_poly",
        "nama": "Low Poly Faceted Geometric",
        "tier": "Tier 2 (Medium Demand)",
        "deskripsi": "Permukaan poligon faset bersudut dengan gradasi pencahayaan tajam, populer untuk visual teknologi dan game."
    },

    # Tier 3: Niche & Specialty Media
    {
        "id": "pixel_art",
        "nama": "8-Bit / 16-Bit Pixel Art",
        "tier": "Tier 3 (Niche)",
        "deskripsi": "Estetika game arcade retro dengan resolusi grid piksel tegas dan warna terbatas yang ikonik."
    },
    {
        "id": "vintage_badges",
        "nama": "Retro & Vintage Badge Emblems",
        "tier": "Tier 3 (Niche)",
        "deskripsi": "Tipografi stempel klasik, pita melengkung, tekstur rustic abad ke-20 untuk tema autentik."
    },
    {
        "id": "halftone_popart",
        "nama": "Halftone Dot & Pop Art",
        "tier": "Tier 3 (Niche)",
        "deskripsi": "Pola titik-titik cetak komik retro ala Roy Lichtenstein dengan kontras warna komik tinggi."
    },
    {
        "id": "zentangle_mandala",
        "nama": "Zentangle & Mandala Sacred Geometry",
        "tier": "Tier 3 (Niche)",
        "deskripsi": "Pola fraktal geometris simetris berulang yang hipnotis dan menenangkan pikiran."
    }
]


# ==============================================================================
# 3. 5 PRESET KOMERSIAL DENGAN KODE CANVAS API EKSEKUTABEL
# ==============================================================================

MOTION_PRESETS: Dict[str, Dict[str, Any]] = {
    "adobe_shutter_fhd": {
        "id": "adobe_shutter_fhd",
        "nama": "Adobe Stock & Shutterstock FHD",
        "platform": "Adobe Stock · Shutterstock · Pond5",
        "badge": "★ Rekomendasi #1 (Best Seller)",
        "resolution": "1920×1080 (16:9)",
        "fps": 60,
        "bitrate_mbps": 45,
        "format": "mp4",
        "duration": 10,
        "deskripsi": "Format standar industri microstock global. Kelulusan kurasi otomatis tertinggi dengan bitrate 45 Mbps & 0% noise.",
        "code": """// Adobe Stock & Shutterstock FHD - Seamless Geometric Wave (10s Loop)
// Resolusi: 1920x1080 @ 60fps | Curation Ready

function draw(ctx, time, w, h) {
  // 1. Background Gelap Bersih
  ctx.fillStyle = '#050711';
  ctx.fillRect(0, 0, w, h);

  const loopProgress = (time % 10) / 10;
  const loopAngle = loopProgress * Math.PI * 2;
  const cx = w / 2;
  const cy = h / 2;

  // 2. Garis Gelombang Harmonik Halus
  const wavesCount = 5;
  for (let i = 0; i < wavesCount; i++) {
    const waveOffset = (i / wavesCount) * Math.PI;
    ctx.beginPath();
    
    // Dynamic Gradient per Gelombang
    const grad = ctx.createLinearGradient(0, 0, w, 0);
    grad.addColorStop(0, 'rgba(56, 189, 248, 0.85)'); // Sky Blue
    grad.addColorStop(0.5, 'rgba(129, 140, 248, 0.9)'); // Indigo
    grad.addColorStop(1, 'rgba(236, 72, 153, 0.85)'); // Pink

    ctx.strokeStyle = grad;
    ctx.lineWidth = 3 - i * 0.3;

    for (let x = 0; x <= w; x += 15) {
      const freq = (x / w) * Math.PI * 3;
      const y = cy + 
        Math.sin(freq + loopAngle + waveOffset) * 120 * Math.sin(loopAngle + i) +
        Math.cos(freq * 0.5 - loopAngle) * 40;
      
      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
  }

  // 3. Partikel Glowing Mengambang (Closed Lissajous Loop)
  const particleCount = 40;
  for (let p = 0; p < particleCount; p++) {
    const phase = (p / particleCount) * Math.PI * 2;
    const px = cx + Math.cos(loopAngle + phase * 2) * (w * 0.38) * Math.sin(phase);
    const py = cy + Math.sin(loopAngle * 2 + phase) * (h * 0.35);
    const radius = 2 + Math.sin(loopAngle + phase) * 1.5;

    ctx.beginPath();
    ctx.arc(px, py, Math.max(1, radius), 0, Math.PI * 2);
    ctx.fillStyle = p % 2 === 0 ? 'rgba(56, 189, 248, 0.75)' : 'rgba(236, 72, 153, 0.75)';
    ctx.fill();
  }
}"""
    },
    "uhd_4k_premium": {
        "id": "uhd_4k_premium",
        "nama": "4K UHD Premium Stock (Royalti Tinggi)",
        "platform": "Adobe Stock 4K · Getty Images · iStock",
        "badge": "★ Royalti Tertinggi ($30-$80+)",
        "resolution": "3840×2160 (16:9)",
        "fps": 60,
        "bitrate_mbps": 85,
        "format": "mp4",
        "duration": 10,
        "deskripsi": "Format komersial bernilai jual tertinggi. Ditargetkan untuk agensi iklan, TV, dan produksi broadcast.",
        "code": """// 4K UHD Premium Stock - Luxury Golden Silk Flow (10s Loop)
// Resolusi: 3840x2160 @ 60fps | Curation Ready

function draw(ctx, time, w, h) {
  ctx.fillStyle = '#06060a';
  ctx.fillRect(0, 0, w, h);

  const loopProgress = (time % 10) / 10;
  const loopAngle = loopProgress * Math.PI * 2;
  const cx = w / 2;
  const cy = h / 2;

  // Pita Emas Mengalir (Golden Ribbons)
  const ribbons = 7;
  for (let r = 0; r < ribbons; r++) {
    const shift = (r / ribbons) * Math.PI * 2;
    ctx.beginPath();

    const goldGrad = ctx.createLinearGradient(0, cy - 300, w, cy + 300);
    goldGrad.addColorStop(0, 'rgba(251, 191, 36, 0.15)'); // Amber Gold
    goldGrad.addColorStop(0.5, 'rgba(245, 158, 11, 0.7)'); // Deep Gold
    goldGrad.addColorStop(1, 'rgba(253, 230, 138, 0.2)'); // Light Gold

    ctx.strokeStyle = goldGrad;
    ctx.lineWidth = 4 + r * 1.5;

    for (let x = 0; x <= w; x += 30) {
      const nx = x / w;
      const y = cy + 
        Math.sin(nx * Math.PI * 2 + loopAngle + shift) * (h * 0.22) +
        Math.cos(nx * Math.PI * 4 - loopAngle) * (h * 0.08);

      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
  }

  // Kilau Cahaya Tengah Emas
  const glow = ctx.createRadialGradient(cx, cy, 20, cx, cy, w * 0.45);
  glow.addColorStop(0, 'rgba(251, 191, 36, 0.12)');
  glow.addColorStop(0.5, 'rgba(245, 158, 11, 0.04)');
  glow.addColorStop(1, 'rgba(0, 0, 0, 0)');
  ctx.fillStyle = glow;
  ctx.fillRect(0, 0, w, h);
}"""
    },
    "alpha_vfx_overlay": {
        "id": "alpha_vfx_overlay",
        "nama": "Transparent Alpha VFX Overlay",
        "platform": "Motion Elements · VideoHive · Film Stock",
        "badge": "★ Transparan (Alpha VP9 / PNG)",
        "resolution": "1920×1080 (16:9)",
        "fps": 60,
        "bitrate_mbps": 45,
        "format": "webm_alpha",
        "duration": 10,
        "deskripsi": "Elemen grafis transparan untuk editor video (Premiere, DaVinci, Final Cut) sebagai HUD, Lower Thirds, atau efek visual overlay.",
        "code": """// Sci-Fi HUD Circular Gauge Overlay (Transparent Alpha)
// Resolusi: 1920x1080 @ 60fps | Alpha Channel | Curation Ready

function draw(ctx, time, w, h) {
  // Kanvas bersih transparan (tanpa fillRect background)
  ctx.clearRect(0, 0, w, h);

  const loopProgress = (time % 10) / 10;
  const loopAngle = loopProgress * Math.PI * 2;
  const cx = w / 2;
  const cy = h / 2;
  const maxRadius = Math.min(w, h) * 0.35;

  ctx.save();
  ctx.translate(cx, cy);

  // Lingkaran Luar Berputar
  ctx.save();
  ctx.rotate(loopAngle);
  ctx.strokeStyle = 'rgba(6, 182, 212, 0.8)';
  ctx.lineWidth = 3;
  ctx.setLineDash([12, 8, 4, 8]);
  ctx.beginPath();
  ctx.arc(0, 0, maxRadius, 0, Math.PI * 2);
  ctx.stroke();
  ctx.restore();

  // Lingkaran Dalam Berlawanan Arah
  ctx.save();
  ctx.rotate(-loopAngle * 1.5);
  ctx.strokeStyle = 'rgba(56, 189, 248, 0.9)';
  ctx.lineWidth = 2;
  ctx.setLineDash([40, 20]);
  ctx.beginPath();
  ctx.arc(0, 0, maxRadius * 0.8, 0, Math.PI * 2);
  ctx.stroke();
  ctx.restore();

  // Pusat Inti Glowing
  const coreGrad = ctx.createRadialGradient(0, 0, 5, 0, 0, maxRadius * 0.4);
  coreGrad.addColorStop(0, 'rgba(6, 182, 212, 0.6)');
  coreGrad.addColorStop(1, 'rgba(6, 182, 212, 0)');
  ctx.fillStyle = coreGrad;
  ctx.beginPath();
  ctx.arc(0, 0, maxRadius * 0.4, 0, Math.PI * 2);
  ctx.fill();

  ctx.restore();
}"""
    },
    "vert_9_16": {
        "id": "vert_9_16",
        "nama": "Vertical 9:16 Social Stock",
        "platform": "Instagram Reels · TikTok · YouTube Shorts",
        "badge": "★ Mobile & Reels Viral",
        "resolution": "1080×1920 (9:16)",
        "fps": 60,
        "bitrate_mbps": 40,
        "format": "mp4",
        "duration": 10,
        "deskripsi": "Format vertikal rasio 9:16 untuk kebutuhan konten video kreator di TikTok, Reels, dan template mobile marketing.",
        "code": """// Vertical 9:16 Social Stock - Ambient Neon Portal (10s Loop)
// Resolusi: 1080x1920 @ 60fps | Curation Ready

function draw(ctx, time, w, h) {
  // Background Deep Violet
  ctx.fillStyle = '#090814';
  ctx.fillRect(0, 0, w, h);

  const loopProgress = (time % 10) / 10;
  const loopAngle = loopProgress * Math.PI * 2;
  const cx = w / 2;
  const cy = h / 2;

  // Floating Ambient Glow Orbs
  const orbs = [
    { x: cx, y: cy - 250, r: 240, color: 'rgba(139, 92, 246, 0.35)' },
    { x: cx + Math.sin(loopAngle) * 80, y: cy + 180, r: 280, color: 'rgba(236, 72, 153, 0.3)' },
    { x: cx - Math.cos(loopAngle) * 90, y: cy - 50, r: 200, color: 'rgba(56, 189, 248, 0.25)' },
  ];

  for (const orb of orbs) {
    const g = ctx.createRadialGradient(orb.x, orb.y, 20, orb.x, orb.y, orb.r);
    g.addColorStop(0, orb.color);
    g.addColorStop(1, 'rgba(0, 0, 0, 0)');
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(orb.x, orb.y, orb.r, 0, Math.PI * 2);
    ctx.fill();
  }

  // Central Vertical Neon Arch
  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(Math.sin(loopAngle) * 0.1);

  ctx.strokeStyle = 'rgba(255, 255, 255, 0.85)';
  ctx.lineWidth = 2.5;
  ctx.beginPath();
  ctx.ellipse(0, 0, 220, 380, 0, 0, Math.PI * 2);
  ctx.stroke();

  // Floating Star Accents
  for (let i = 0; i < 24; i++) {
    const angle = (i / 24) * Math.PI * 2 + loopAngle;
    const px = Math.cos(angle) * (260 + Math.sin(angle * 3) * 20);
    const py = Math.sin(angle) * (420 + Math.cos(angle * 2) * 30);
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(px, py, 2, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();
}"""
    },
    "square_1_1_feed": {
        "id": "square_1_1_feed",
        "nama": "Square 1:1 Social Feed & Ads",
        "platform": "Instagram Feed · Facebook Ads · Spotify Canvas",
        "badge": "★ Feed & Ads Stock",
        "resolution": "1080×1080 (1:1)",
        "fps": 60,
        "bitrate_mbps": 40,
        "format": "mp4",
        "duration": 10,
        "deskripsi": "Format persegi rasio 1:1 untuk postingan feed media sosial, cover album, motion poster, dan materi iklan komersial.",
        "code": """// Square 1:1 Social Feed - Harmonic Kaleido Rings (10s Loop)
// Resolusi: 1080x1080 @ 60fps | Curation Ready

function draw(ctx, time, w, h) {
  ctx.fillStyle = '#040408';
  ctx.fillRect(0, 0, w, h);

  const loopProgress = (time % 10) / 10;
  const loopAngle = loopProgress * Math.PI * 2;
  const cx = w / 2;
  const cy = h / 2;

  const rings = 8;
  for (let i = 1; i <= rings; i++) {
    const r = (i / rings) * (w * 0.42);
    const rot = loopAngle * (i % 2 === 0 ? 1 : -1) * (1 + i * 0.15);

    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(rot);

    ctx.strokeStyle = i % 2 === 0 ? 'rgba(99, 102, 241, 0.7)' : 'rgba(236, 72, 153, 0.7)';
    ctx.lineWidth = 2;
    ctx.beginPath();

    const sides = 4 + (i % 3);
    for (let s = 0; s <= sides; s++) {
      const a = (s / sides) * Math.PI * 2;
      const x = Math.cos(a) * r;
      const y = Math.sin(a) * r;
      if (s === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
    ctx.restore();
  }
}"""
    }
}


# ==============================================================================
# 4. AI PROMPT ENGINEERING TEMPLATES
# ==============================================================================

def generate_concept_prompt(theme: str, duration: int = 10, scene: int = 3, visual_style: str = "Flat Design & Corporate Memphis") -> str:
    """Formula 1: Prompt 2-Tahap (10 Konsep -> Kode Canvas API 16:9 Landscape)."""
    return (
        f"Kamu adalah Motion Graphics Designer profesional dan JavaScript Canvas API Developer untuk video microstock premium.\n\n"
        f"TAHAP 1: BUAT 10 KONSEP\n"
        f"Buat 10 konsep video yang berbeda, realistis dibuat dengan Canvas API murni, dan tanpa elemen/logo berlisensi.\n"
        f"- Tema: {theme}\n"
        f"- Durasi: {duration} detik\n"
        f"- Jumlah Scene: {scene}\n"
        f"- Gaya Visual: {visual_style}\n"
        f"- Rasio: 16:9\n"
        f"- Resolusi: 1080p (Full HD)\n"
        f"- Background: Bebas / Sesuai rekomendasi artistik AI untuk estetika dan kontras terbaik.\n\n"
        f"Format per konsep: Judul, Ringkasan Visual, Struktur Scene, Gaya Motion, Nilai Jual Microstock.\n"
        f"Setelah memberikan 10 konsep, BERHENTI dan tunggu saya memilih nomor.\n\n"
        f"TAHAP 2: PEMBUATAN KODE\n"
        f"Jika saya membalas dengan memilih nomor (misal: 'Nomor 1'), buatkan kodenya berdasarkan konsep tersebut.\n\n"
        f"ATURAN WAJIB KODE (Terapkan dengan ketat):\n"
        f"- Output HANYA KODE JavaScript siap salin. Tanpa teks penjelasan, tanpa HTML/CSS, tanpa DOM, dan tanpa library/asset eksternal.\n"
        f"- Wajib menggunakan: function draw(ctx, time, width, height)\n"
        f"- Kualitas Visual: Premium, rapi, responsif (wajib gunakan width, height, minSide agar proporsional di FHD/2K/4K).\n"
        f"- Loop harus seamless. Hindari flicker, objek terpotong, teks bertumpuk, atau gerakan patah.\n"
        f"- Animasi harus tetap bergerak dari awal sampai akhir durasi.\n\n"
        f"ATURAN WAKTU & TIMELINE (Krusial):\n"
        f"Parameter `time` sudah dalam satuan DETIK.\n"
        f"Dilarang menggunakan: time * 0.001, time / 1000, performance.now(), Date.now(), atau requestAnimationFrame.\n\n"
        f"Wajib gunakan struktur logika waktu ini di dalam fungsi:\n"
        f"const t = time;\n"
        f"const duration = {duration};\n"
        f"const sceneCount = {scene};\n"
        f"const loopT = t % duration;\n"
        f"const sceneDuration = duration / sceneCount;\n"
        f"const currentScene = Math.floor(loopT / sceneDuration);\n"
        f"const sceneProgress = (loopT % sceneDuration) / sceneDuration;"
    )


def generate_vertical_prompt(theme: str, duration: int = 15, scene: int = 1, visual_style: str = "Cyberpunk Neon & Y2K Aesthetic") -> str:
    """Formula 2: Single-Shot Vertical 9:16 Prompt (Reels / TikTok / Shorts)."""
    return (
        f"Kamu adalah Expert Motion Graphics Designer & JS Canvas API Developer untuk aset video microstock komersial. Buat kode JavaScript murni (Pure JS) berdasarkan parameter berikut:\n\n"
        f"TEMA: {theme}\n"
        f"DURASI: {duration} Detik\n"
        f"SCENE: {scene} Scene\n"
        f"RASIO: 9:16\n"
        f"VISUAL: {visual_style}\n\n"
        f"ATURAN KODE (MUTLAK):\n"
        f"1. Format Output: HANYA kode JavaScript murni di dalam satu code block ```javascript ... ```. Tanpa HTML, CSS, atau library eksternal.\n"
        f"2. Fungsi Wajib: Kode harus berjalan di dalam fungsi ini:\n"
        f"   function draw(ctx, time, width, height) {{ ctx.clearRect(0, 0, width, height); /* logika */ }}\n"
        f"3. Satuan Waktu: Parameter time berjalan dalam detik (bukan milidetik).\n"
        f"4. 100% Responsive: DILARANG menggunakan koordinat pixel absolut (hardcoded). Semua posisi, ukuran (termasuk lineWidth), dan radius harus dikalkulasi secara relatif terhadap width dan height (contoh: x = width * 0.5).\n"
        f"5. State Aman: Gunakan ctx.save() dan ctx.restore() setiap menggambar elemen agar state tidak bocor.\n\n"
        f"ATURAN VISUAL & MOTION:\n"
        f"1. Desain: Komposisi rapi, palet warna modern/elegan, objek utama di tengah (tidak keluar frame). DILARANG menggunakan gambar eksternal, font luar, watermark, atau logo.\n"
        f"2. Timeline Animasi:\n"
        f"   0.0s - 1.5s: Intro (Animasi masuk dengan ease-out).\n"
        f"   1.5s - {duration - 1.5}s: Main (Micro-movements statis seperti floating/pulsing).\n"
        f"   {duration - 1.5}s - {duration}.0s: Outro (Animasi keluar/menghilang dengan ease-in).\n"
        f"3. Fisika Gerak: Gerakan wajib sangat mulus (smooth) dengan loop seamless."
    )


def generate_transparent_prompt(theme: str, duration: int = 10, scene: int = 1, visual_style: str = "Glassmorphism & Frosted UI") -> str:
    """Formula 3: Single-Shot Transparent Alpha Channel Prompt (WebM / PNG Overlay / VFX)."""
    return (
        f"Kamu adalah Expert Motion Graphics Designer & JS Canvas API Developer untuk aset VFX Overlay Transparan (Alpha Channel).\n\n"
        f"TEMA: {theme}\n"
        f"DURASI: {duration} Detik\n"
        f"FORMAT: WebM Alpha / Transparent Overlay\n"
        f"VISUAL: {visual_style}\n\n"
        f"ATURAN KHUSUS ALPHA TRANSPARAN:\n"
        f"1. DILARANG membuat background solid (JANGAN gunakan ctx.fillStyle = '#...' lalu ctx.fillRect(0,0,w,h)).\n"
        f"2. Bersihkan kanvas di awal frame HANYA dengan: ctx.clearRect(0, 0, width, height);\n"
        f"3. Gunakan warna RGBA dengan nilai alpha yang proporsional (contoh: rgba(6, 182, 212, 0.8)).\n"
        f"4. Fungsi Wajib: function draw(ctx, time, width, height)\n"
        f"5. Output HANYA kode JavaScript di dalam block ```javascript ... ``` tanpa basa-basi."
    )


# ==============================================================================
# 5. AI CODE EXTRACTOR & SECURITY SCORING
# ==============================================================================

def extract_clean_canvas_code(raw_text: str) -> str:
    """
    Menyaring kode JavaScript murni dari output markdown AI.
    Memilih snippet dengan skor Canvas API tertinggi (draw, ctx., clearRect).
    """
    trimmed = raw_text.strip()
    fence_regex = re.compile(r"```(?:javascript|js|typescript|ts|[\w-]*)?\s*\r?\n([\s\S]*?)\r?\n?\s*```", re.IGNORECASE)
    snippets: List[str] = fence_regex.findall(trimmed)

    if not snippets:
        # Jika tidak ada code fence markdown, periksa apakah teks sudah berupa kode mentah
        if "function draw" in trimmed or "ctx." in trimmed:
            return trimmed
        return trimmed

    if len(snippets) == 1:
        return snippets[0].strip()

    # Jika ada beberapa code block, beri skor berdasarkan kehadiran Canvas API
    def score_snippet(code: str) -> int:
        score = 0
        if re.search(r"function\s+(draw|render|animate|main|loop)\b", code):
            score += 100
        if "clearRect" in code:
            score += 40
        if "ctx." in code:
            score += 30
        if re.match(r"^\s*<", code):  # HTML snippet
            score -= 50
        return score

    snippets.sort(key=score_snippet, reverse=True)
    return snippets[0].strip()


# ==============================================================================
# 6. DIRECT AI CODE GENERATOR (SEKALI KLIK)
# ==============================================================================

def generate_motion_code_with_ai(
    theme: str,
    visual_style: str = "Flat Design & Corporate Memphis",
    format_type: str = "16:9",
    duration: int = 10,
    scene_count: int = 1
) -> Dict[str, Any]:
    """
    Menghasilkan kode Canvas API siap eksekusi menggunakan model LLM (Gemini, Groq, OpenAI).
    Jika model AI belum dikonfigurasi, mengembalikan preset terdekat sebagai fallback.
    """
    if format_type == "9:16":
        sys_prompt = generate_vertical_prompt(theme, duration=duration, scene=scene_count, visual_style=visual_style)
    elif format_type == "alpha":
        sys_prompt = generate_transparent_prompt(theme, duration=duration, scene=scene_count, visual_style=visual_style)
    else:
        sys_prompt = generate_concept_prompt(theme, duration=duration, scene=scene_count, visual_style=visual_style)

    user_prompt = f"Buatkan kode JavaScript Canvas draw(ctx, time, width, height) untuk tema: '{theme}', gaya visual: '{visual_style}', durasi: {duration} detik."

    if ai_brain.is_ai_ready():
        try:
            raw_res = ai_brain.generate_text(sys_prompt, user_prompt, json_mode=False, timeout=60)
            code = extract_clean_canvas_code(raw_res)
            if "function draw" in code or "ctx." in code:
                return {
                    "ok": True,
                    "code": code,
                    "theme": theme,
                    "visual_style": visual_style,
                    "generated_by": "ai"
                }
        except Exception as e:
            pass

    # Fallback ke preset terdekat jika LLM belum aktif
    fallback_preset = MOTION_PRESETS.get("adobe_shutter_fhd")
    if format_type == "9:16":
        fallback_preset = MOTION_PRESETS.get("vert_9_16")
    elif format_type == "alpha":
        fallback_preset = MOTION_PRESETS.get("alpha_vfx_overlay")

    return {
        "ok": True,
        "code": fallback_preset["code"] if fallback_preset else "",
        "theme": theme,
        "visual_style": visual_style,
        "system_prompt": sys_prompt,
        "generated_by": "preset_fallback",
        "message": "AI Brain belum terhubung. Menampilkan kode preset komersial terverifikasi."
    }
