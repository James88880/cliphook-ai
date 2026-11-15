import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import re
import base64
import os
import subprocess
import tempfile
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont
import textwrap
import random

st.set_page_config(page_title="ClipHook AI | TikTok GTA Video Engine", page_icon="🎮", layout="wide")

def get_base64_bg(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

bg_base64 = get_base64_bg("GTA6.jpg") or get_base64_bg("gta6.jpg") or get_base64_bg("gta6.png")

if bg_base64:
    bg_css = f'url("data:image/jpeg;base64,{bg_base64}")'
else:
    bg_css = 'url("https://unsplash.com")'

# Custom GTA 6 Wallpaper & Neon Gaming CSS
st.markdown(f"""
<style>
@import url('https://googleapis.com');

.stApp {{
    background-image: linear-gradient(rgba(9, 10, 18, 0.58), rgba(14, 7, 26, 0.74)),
                      {bg_css};
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    color: #f0f0f5;
    font-family: 'Inter', sans-serif;
}}

#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}

section[data-testid="stSidebar"] {{
    background-color: rgba(10, 12, 22, 0.88) !important;
    backdrop-filter: blur(12px);
    border-right: 1px solid rgba(255, 0, 128, 0.35);
}}

.hero-box {{
    background: rgba(15, 12, 28, 0.74);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 0, 128, 0.55);
    border-radius: 16px;
    padding: 26px 32px;
    margin-bottom: 24px;
    box-shadow: 0 0 30px rgba(255, 0, 128, 0.25);
}}

.hero-title {{
    font-family: 'Orbitron', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(90deg, #ff2a85, #ff9a00, #00f0ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    letter-spacing: 1.5px;
}}

.hero-sub {{
    color: #e2e6f5;
    font-size: 1.05rem;
    margin-top: 8px;
}}

.badge-row {{
    display: flex;
    gap: 12px;
    margin-top: 14px;
    flex-wrap: wrap;
}}

.badge {{
    background: rgba(0, 240, 255, 0.16);
    border: 1px solid rgba(0, 240, 255, 0.55);
    color: #00f0ff;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

div.stButton > button:first-child {{
    background: linear-gradient(90deg, #ff007f, #ff7b00);
    color: white;
    font-family: 'Orbitron', sans-serif;
    font-weight: 600;
    letter-spacing: 1px;
    border: none;
    border-radius: 10px;
    padding: 0.85rem 1.5rem;
    width: 100%;
    box-shadow: 0 0 22px rgba(255, 0, 128, 0.55);
    transition: all 0.2s ease-in-out;
}}

div.stButton > button:first-child:hover {{
    transform: translateY(-2px);
    box-shadow: 0 0 32px rgba(0, 240, 255, 0.8);
}}

.stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] {{
    background-color: rgba(14, 16, 28, 0.88) !important;
    border: 1px solid rgba(255, 0, 128, 0.4) !important;
    color: #ffffff !important;
    border-radius: 10px !important;
}}

.glass-card {{
    background: rgba(14, 16, 28, 0.82);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(0, 240, 255, 0.4);
    border-radius: 14px;
    padding: 22px;
    margin-top: 10px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
}}
</style>
""", unsafe_allow_html=True)

HOOK_TEMPLATES = {
    "GTA 6 / Vice City Chaos": [
        "HE THOUGHT HE ESCAPED A 5-STAR CHASE...",
        "NOBODY EXPECTED THIS ENDING IN VICE CITY...",
        "99% OF PLAYERS FAIL THIS GTA JUMP...",
        "WAIT UNTIL THE COPS SEE WHAT HE DID...",
        "THIS GTA 6 PHYSICS MOMENT BROKE THE LOBBY..."
    ],
    "GTA Roleplay / FiveM": [
        "THE ADMIN WAS WATCHING THE WHOLE TIME...",
        "HE ROBBED THE WRONG GANG IN FIVEM...",
        "THIS RP PLOT TWIST HAD THE WHOLE SERVER CRYING...",
        "BRO REALLY THOUGHT HE COULD OUTSMART THE LSPD...",
        "INSTANT KARMA IN GTA RP..."
    ],
    "Faceless Gaming Story": [
        "THE RAREST MOMENT EVER CAUGHT ON STREAM...",
        "HOW DID HE ACTUALLY SURVIVE THIS...",
        "WATCH CLOSELY AT THE 10-SECOND MARK...",
        "THIS ONE MISTAKE COST HIM EVERYTHING...",
        "ONLY TRUE GAMERS WILL UNDERSTAND THIS..."
    ],
    "Streamer Rage / Podcast Clip": [
        "HE INSTANTLY REGRETTED SAYING THAT LIVE...",
        "CHAT LOST THEIR MINDS WHEN THIS HAPPENED...",
        "HIS REACTION AT THE END IS PRICELESS...",
        "BRO ALMOST BROKE HIS SETUP OVER THIS...",
        "THE FUNNIEST STREAM MOMENT THIS WEEK..."
    ]
}

def create_hook_banner(hook_text, output_png):
    """Creates a transparent 1080x1920 PNG overlay with a bold TikTok hook box at the top."""
    img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 54)
    except Exception:
        try:
            font = ImageFont.truetype("arialbd.ttf", 54)
        except Exception:
            font = ImageFont.load_default()

    wrapped = textwrap.fill(hook_text.upper(), width=24)
    lines = wrapped.split("\n")
    box_height = 70 + len(lines) * 68
    draw.rectangle([70, 220, 1010, 220 + box_height], fill=(255, 255, 255, 245))
    y_text = 248
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        draw.text(((1080 - w) / 2, y_text), line, font=font, fill=(10, 10, 15, 255))
        y_text += 68
    img.save(output_png)

def render_tiktok_mp4(input_video, hook_text, output_video):
    """Converts horizontal 16:9 gameplay into 9:16 TikTok MP4 with blurred background + top hook banner."""
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    banner_png = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
    create_hook_banner(hook_text, banner_png)

    filter_complex = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg];"
        "[0:v]scale=1080:-2[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2[vid];"
        "[vid][1:v]overlay=0:0[out]"
    )
    cmd = [
        ffmpeg_exe, "-y",
        "-i", input_video,
        "-i", banner_png,
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-map", "0:a?",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-t", "60",
        output_video
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if os.path.exists(banner_png):
        os.remove(banner_png)

# Sidebar Control Panel (No API Key!)
with st.sidebar:
    st.markdown("### 🎮 CLIPPER STUDIO")
    st.success("🟢 Engine Online — Ready to Render")
    st.markdown("---")
    st.markdown("**📱 TikTok Auto-Editor Specs:**")
    st.caption("• Outputs 1080x1920 (9:16) vertical MP4.")
    st.caption("• Blurred gameplay fill + viral hook banner.")
    st.caption("• Auto-trims up to 60 seconds for TikTok & Shorts.")
    st.caption("• Generates instant CapCut .SRT captions.")

# Hero Header
st.markdown("""
<div class="hero-box">
    <div class="hero-title">🌴 CLIPHOOK AI — TIKTOK STUDIO</div>
    <div class="hero-sub">Turn raw GTA 6 & FiveM clips into ready-to-post 9:16 vertical TikTok videos with viral hooks & CapCut captions.</div>
    <div class="badge-row">
        <span class="badge">📱 9:16 TikTok Auto-Format</span>
        <span class="badge">🔥 Viral Hook Overlay</span>
        <span class="badge">🎬 Ready-to-Post .MP4</span>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1.1, 1.3], gap="large")

with col1:
    st.markdown("#### 🕹️ 1. UPLOAD CLIP OR PASTE LINK")
    uploaded_video = st.file_uploader("Upload Raw GTA Clip (.MP4 / .MOV):", type=["mp4", "mov", "mkv"])
    niche = st.selectbox(
        "Target Content Mode:",
        list(HOOK_TEMPLATES.keys())
    )
    custom_hook = st.text_input(
        "Top Video Hook Text (Leave blank for auto-viral hook):",
        placeholder="e.g., HE THOUGHT HE ESCAPED A 5-STAR CHASE..."
    )
    url_or_text = st.text_area(
        "YouTube URL or Clip Dialogue (Optional for .SRT Captions):",
        height=110,
        placeholder="Paste spoken dialogue or a YouTube link to generate CapCut .SRT captions..."
    )
    generate_clicked = st.button("🚀 CREATE TIKTOK VIDEO & HOOKS")

def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

def generate_srt(script_text):
    words = script_text.split()
    chunks = [" ".join(words[i:i+5]) for i in range(0, len(words), 5)]
    srt_lines = []
    for idx, chunk in enumerate(chunks, start=1):
        start_sec = (idx - 1) * 2
        end_sec = idx * 2
        start_time = f"00:{start_sec//60:02d}:{start_sec%60:02d},000"
        end_time = f"00:{end_sec//60:02d}:{end_sec%60:02d},000"
        srt_lines.append(f"{idx}\n{start_time} --> {end_time}\n{chunk}\n")
    return "\n".join(srt_lines)

with col2:
    st.markdown("#### 🏆 2. TIKTOK VIDEO & VIRAL LOOT")
    if generate_clicked:
        if not uploaded_video and not url_or_text.strip():
            st.warning("⚠️ Upload a raw GTA video (.MP4) OR paste dialogue/YouTube link first.")
        else:
            preset_hooks = HOOK_TEMPLATES[niche]
            chosen_hook = custom_hook.strip() if custom_hook.strip() else random.choice(preset_hooks)
            clean_script = url_or_text.strip()

            if url_or_text.strip():
                vid_id = extract_video_id(url_or_text)
                if vid_id:
                    try:
