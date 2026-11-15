import streamlit as st
import base64
import os
import subprocess
import tempfile
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont
import textwrap
import random

st.set_page_config(page_title="ClipHook AI | TikTok GTA Video Engine", page_icon="🎮", layout="wide")

bg_file = "GTA6.jpg" if os.path.exists("GTA6.jpg") else ("gta6.jpg" if os.path.exists("gta6.jpg") else ("gta6.png" if os.path.exists("gta6.png") else None))
bg_b64 = base64.b64encode(open(bg_file, "rb").read()).decode() if bg_file else None
bg_css = f'url("data:image/jpeg;base64,{bg_b64}")' if bg_b64 else 'url("https://unsplash.com")'

custom_css = (
    "<style>"
    "@import url('https://googleapis.com');"
    f".stApp {{ background-image: linear-gradient(rgba(9, 10, 18, 0.58), rgba(14, 7, 26, 0.74)), {bg_css}; background-size: cover; background-position: center; background-attachment: fixed; color: #f0f0f5; font-family: 'Inter', sans-serif; }}"
    "#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}"
    "section[data-testid='stSidebar'] { background-color: rgba(10, 12, 22, 0.88) !important; backdrop-filter: blur(12px); border-right: 1px solid rgba(255, 0, 128, 0.35); }"
    ".hero-box { background: rgba(15, 12, 28, 0.74); backdrop-filter: blur(14px); border: 1px solid rgba(255, 0, 128, 0.55); border-radius: 16px; padding: 26px 32px; margin-bottom: 24px; box-shadow: 0 0 30px rgba(255, 0, 128, 0.25); }"
    ".hero-title { font-family: 'Orbitron', sans-serif; font-size: 2.4rem; font-weight: 800; background: linear-gradient(90deg, #ff2a85, #ff9a00, #00f0ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; letter-spacing: 1.5px; }"
    ".hero-sub { color: #e2e6f5; font-size: 1.05rem; margin-top: 8px; }"
    ".badge-row { display: flex; gap: 12px; margin-top: 14px; flex-wrap: wrap; }"
    ".badge { background: rgba(0, 240, 255, 0.16); border: 1px solid rgba(0, 240, 255, 0.55); color: #00f0ff; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }"
    "div.stButton > button:first-child { background: linear-gradient(90deg, #ff007f, #ff7b00); color: white; font-family: 'Orbitron', sans-serif; font-weight: 600; letter-spacing: 1px; border: none; border-radius: 10px; padding: 0.85rem 1.5rem; width: 100%; box-shadow: 0 0 22px rgba(255, 0, 128, 0.55); }"
    ".stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb='select'] { background-color: rgba(14, 16, 28, 0.88) !important; border: 1px solid rgba(255, 0, 128, 0.4) !important; color: #ffffff !important; border-radius: 10px !important; }"
    ".glass-card { background: rgba(14, 16, 28, 0.82); backdrop-filter: blur(14px); border: 1px solid rgba(0, 240, 255, 0.4); border-radius: 14px; padding: 22px; margin-top: 10px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5); }"
    "</style>"
)
st.markdown(custom_css, unsafe_allow_html=True)

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

st.sidebar.markdown("### 🎮 CLIPPER STUDIO")
st.sidebar.success("🟢 Engine Online — Ready to Render")
st.sidebar.markdown("---")
st.sidebar.markdown("**📱 TikTok Auto-Editor Specs:**")
st.sidebar.caption("• Outputs 9:16 vertical TikTok MP4.")
st.sidebar.caption("• Blurred gameplay fill + viral hook banner.")
st.sidebar.caption("• Auto-trims up to 60 seconds for TikTok & Shorts.")
st.sidebar.caption("• Generates instant CapCut .SRT captions.")

hero_html = (
    '<div class="hero-box">'
    '<div class="hero-title">🌴 CLIPHOOK AI — TIKTOK STUDIO</div>'
    '<div class="hero-sub">Turn raw GTA 6 & FiveM clips into ready-to-post 9:16 vertical TikTok videos with viral hooks & CapCut captions.</div>'
    '<div class="badge-row">'
    '<span class="badge">📱 9:16 TikTok Auto-Format</span>'
    '<span class="badge">🔥 Viral Hook Overlay</span>'
    '<span class="badge">🎬 Ready-to-Post .MP4</span>'
    '</div></div>'
)
st.markdown(hero_html, unsafe_allow_html=True)

col1, col2 = st.columns([1.1, 1.3], gap="large")

col1.markdown("#### 🕹️ 1. UPLOAD CLIP & CUSTOMIZE")
uploaded_video = col1.file_uploader("Upload Raw GTA Clip (.MP4 / .MOV):", type=["mp4", "mov", "mkv"])
niche = col1.selectbox("Target Content Mode:", list(HOOK_TEMPLATES.keys()))
custom_hook = col1.text_input("Top Video Hook Text (Leave blank for auto-viral hook):", placeholder="e.g., HE THOUGHT HE ESCAPED A 5-STAR CHASE...")
dialogue_text = col1.text_area("Clip Dialogue (Optional for CapCut .SRT Captions):", height=90, placeholder="Paste spoken words here if you also want a downloadable .SRT caption file...")
generate_clicked = col1.button("🚀 CREATE TIKTOK VIDEO & HOOKS")

has_input = bool(uploaded_video or dialogue_text.strip())
_ = st.warning("⚠️ Please upload a raw `.MP4` video clip on the left first!") if (generate_clicked and not has_input) else None

ready_to_run = bool(generate_clicked and has_input)
preset_hooks = HOOK_TEMPLATES[niche]
chosen_hook = (custom_hook.strip() if custom_hook.strip() else random.choice(preset_hooks)) if ready_to_run else st.session_state.get("chosen_hook")

st.session_state["preset_hooks"] = preset_hooks if ready_to_run else st.session_state.get("preset_hooks", preset_hooks)
st.session_state["chosen_hook"] = chosen_hook
st.session_state["niche"] = niche if ready_to_run else st.session_state.get("niche", niche)
st.session_state["clean_script"] = dialogue_text.strip() if ready_to_run else st.session_state.get("clean_script", "")

should_render = bool(ready_to_run and uploaded_video)

font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
banner_font = ImageFont.truetype(font_path, 36) if os.path.exists(font_path) else ImageFont.load_default()

in_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name if should_render else ""
out_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name if should_render else ""
banner_png = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name if should_render else ""

_ = open(in_tmp, "wb").write(uploaded_video.getvalue()) if should_render else None

img = Image.new("RGBA", (720, 1280), (0, 0, 0, 0)) if should_render else None
draw = ImageDraw.Draw(img) if should_render else None
lines = textwrap.fill((chosen_hook or "").upper(), width=24).split("\n") if should_render else []
box_h = 46 + len(lines) * 48
_ = draw.rectangle([45, 140, 675, 140 + box_h], fill=(255, 255, 255, 245)) if should_render else None
_ = [draw.text(((720 - draw.textlength(line, font=banner_font)) / 2, 160 + i * 48), line, font=banner_font, fill=(10, 10, 15, 255)) for i, line in enumerate(lines)] if should_render else None
_ = img.save(banner_png) if should_render else None

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe() if should_render else ""
fc = "[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,boxblur=15:3[bg];[0:v]scale=720:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2[vid];[vid][1:v]overlay=0:0[out]"
cmd = [ffmpeg_exe, "-y", "-i", in_tmp, "-i", banner_png, "-filter_complex", fc, "-map", "[out]", "-map", "0:a?", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "24", "-c:a", "aac", "-b:a", "128k", "-t", "60", out_tmp]
res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) if should_render else None

rendered_ok = bool(should_render and res and res.returncode == 0 and os.path.exists(out_tmp))
st.session_state["video_bytes"] = open(out_tmp, "rb").read() if rendered_ok else (None if ready_to_run else st.session_state.get("video_bytes"))
err_tail = res.stderr.decode("utf-8", errors="ignore")[-300:] if (should_render and not rendered_ok and res) else ""
_ = st.error(f"FFmpeg error: {err_tail}") if err_tail else None

_ = [os.remove(p) for p in [in_tmp, out_tmp, banner_png] if p and os.path.exists(p)]

col2.markdown("#### 🏆 2. TIKTOK VIDEO & VIRAL LOOT")
has_result = bool(st.session_state.get("chosen_hook"))

ready_html = '<div class="glass-card" style="text-align: center; padding: 60px 20px; color: #d0d7eb;"><h3>📱 TikTok Video Engine Ready</h3><p>Upload any raw GTA clip (<b>.MP4</b>) on the left and click <b>CREATE TIKTOK VIDEO & HOOKS</b> to render your vertical video.</p></div>'
_ = col2.markdown(ready_html, unsafe_allow_html=True) if not has_result else None

tab1, tab2, tab3 = col2.tabs(["📱 TikTok Video (.MP4)", "🔥 Viral Hook Ideas", "🎬 CapCut .SRT"]) if has_result else (col2.empty(), col2.empty(), col2.empty())

has_vid = bool(has_result and st.session_state.get("video_bytes"))
_ = tab1.success(f"✅ Rendered with Hook: **{st.session_state.get('chosen_hook')}**") if has_vid else None
_ = tab1.video(st.session_state["video_bytes"]) if has_vid else None
