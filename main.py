# =========================================================
# 🎬 Reelify Pro - Merged Version (Your + Friend's Features)
# =========================================================

import os, shutil, subprocess, tempfile, json, hashlib, certifi
import streamlit as st
import yt_dlp
import whisper
import cv2

# ---------------------------
# FFmpeg Setup
# ---------------------------
FFMPEG = r"C:/ffmpeg/ffmpeg-7.1.1-essentials_build/bin/ffmpeg.exe"
os.environ["FFMPEG_BINARY"] = FFMPEG
if not shutil.which("ffmpeg"):
    os.environ["PATH"] += os.pathsep + os.path.dirname(FFMPEG)

# ---------------------------
# Directories
# ---------------------------
VIDEO_DIR = "videos"
AUDIO_DIR = "audios"
RESIZED_DIR = "resized"
REELS_DIR = "reels"
UPLOAD_DIR = "uploads"
USER_FILE = "users.json"

for folder in [VIDEO_DIR, AUDIO_DIR, RESIZED_DIR, REELS_DIR, UPLOAD_DIR]:
    os.makedirs(folder, exist_ok=True)

# ---------------------------
# User Authentication
# ---------------------------
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({"admin": "admin123"}, f)

with open(USER_FILE, "r") as f:
    USERS = json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

def login():
    st.title("🔐 Login or Sign Up")
    choice = st.radio("Account Action", ["Login", "Sign Up"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if choice == "Login":
        if st.button("Login"):
            if username in USERS and USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
            else:
                st.error("Invalid credentials")
    elif choice == "Sign Up":
        if st.button("Create Account"):
            if username in USERS:
                st.warning("Username already exists")
            elif not username.strip() or not password.strip():
                st.warning("Username and password cannot be empty")
            else:
                USERS[username] = password
                save_users(USERS)
                st.success("Account created! Please login.")

# ---------------------------
# Helper Functions
# ---------------------------
def run(cmd: list[str]):
    """Run a subprocess command and raise error if it fails."""
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode:
        raise RuntimeError(res.stderr.strip())

def download_youtube(url: str) -> str:
    """Download YouTube video using yt_dlp."""
    ydl_opts = {
        "format": "best[ext=mp4][acodec!=none][vcodec!=none]",
        "outtmpl": os.path.join(VIDEO_DIR, "%(title)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "http_headers": {"User-Agent": "Mozilla/5.0"},
        "merge_output_format": "mp4",
        "ca_certificates": certifi.where(),
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

def save_uploaded_video(uploaded_file):
    """Save uploaded video file."""
    ext = uploaded_file.name.split(".")[-1]
    if ext.lower() not in ["mp4", "mov", "avi", "mkv"]:
        st.error("Unsupported format")
        return None
    path = os.path.join(VIDEO_DIR, uploaded_file.name)
    with open(path, "wb") as f:
        f.write(uploaded_file.read())
    return path

def resize_to_reel(inp: str) -> str:
    """Convert video to vertical 1080x1920 format."""
    out = os.path.join(RESIZED_DIR, f"resized_{os.path.basename(inp)}")
    vf = "scale=1080:-2,pad=1080:1920:(ow-iw)/2:(oh-ih)/2"
    run([FFMPEG, "-y", "-i", inp, "-vf", vf, "-c:v", "libx264", "-c:a", "copy", out])
    return out

def extract_audio(video_path):
    """Extract audio from video."""
    audio_path = os.path.join(AUDIO_DIR, os.path.basename(video_path).rsplit(".", 1)[0] + ".wav")
    run([FFMPEG, "-y", "-i", video_path, "-q:a", "0", "-map", "a", audio_path])
    return audio_path

def transcribe_audio(audio_path):
    """Transcribe audio using Whisper."""
    model = whisper.load_model("base")
    result = model.transcribe(audio_path, fp16=False, word_timestamps=True)
    return result['segments']

def export_ass(segments, filename):
    """Export captions in ASS format."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write("""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default, Arial, 22, &H00FFFFFF, &H80000000, 0, 0, 1, 1, 0, 2, 10, 10, 40, 1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""")
        for seg in segments:
            start = seg['start']
            end = seg['end']
            text = seg['text'].strip().replace("\n", " ")

            def ass_time(t):
                h = int(t // 3600)
                m = int((t % 3600) // 60)
                s = int(t % 60)
                cs = int((t - int(t)) * 100)
                return f"{h:01}:{m:02}:{s:02}.{cs:02}"

            f.write(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Default,,0,0,0,,{text}\n")

def select_highlights(segments):
    """Select highlight clips (30–60 seconds)."""
    highlights = []
    group = []
    start_time = None
    for seg in segments:
        if not group:
            start_time = seg['start']
        group.append(seg)
        group_duration = seg['end'] - start_time
        if 30 <= group_duration <= 60:
            highlights.append(group)
            group = []
        elif group_duration > 60:
            group = []
    return highlights

def generate_reels(video_path, segments):
    """Generate highlight reels with captions."""
    highlights = select_highlights(segments)
    reel_paths = []
    for idx, group in enumerate(highlights):
        start = group[0]['start']
        end = group[-1]['end']
        ass_file = f"temp_{idx}.ass"
        export_ass(group, ass_file)
        out_path = os.path.join(REELS_DIR, f"highlight_{idx}.mp4")
        run([FFMPEG, "-y", "-i", video_path, "-ss", str(start), "-to", str(end), "-vf", f"ass={ass_file}", "-c:a", "copy", out_path])
        os.remove(ass_file)
        reel_paths.append(out_path)
    return reel_paths

def evaluate_reel(reel_path: str, expected_duration=30, tolerance=2) -> dict:
    """Evaluate reel duration and resolution."""
    cap = cv2.VideoCapture(reel_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = frames / fps if fps else 0
    cap.release()
    return {
        "duration_ok": abs(duration - expected_duration) <= tolerance,
        "resolution_ok": width == 1080 and height == 1920,
        "duration": duration,
        "resolution": f"{width}x{height}"
    }

# ---------------------------
# Streamlit App
# ---------------------------
if 'logged_in' not in st.session_state:
    login()
else:
    st.title(f"🎬 Reelify Pro - Welcome {st.session_state.username}")

    input_method = st.radio("Input Method", ["Upload Video", "YouTube URL"])
    video_path = None

    if input_method == "Upload Video":
        uploaded = st.file_uploader("Choose a video", type=["mp4", "mov", "avi", "mkv"])
        if uploaded and st.button("Process Video"):
            video_path = save_uploaded_video(uploaded)
    else:
        url = st.text_input("Enter YouTube URL")
        if st.button("Download & Process") and url:
            video_path = download_youtube(url)

    if video_path:
        st.success("Video ready.")
        resized_path = resize_to_reel(video_path)
        st.success("Resized to 1080x1920.")

        audio_path = extract_audio(video_path)
        st.success("Audio extracted.")

        segments = transcribe_audio(audio_path)
        st.success("Transcription complete.")

        reels = generate_reels(resized_path, segments)

        if reels:
            st.subheader("📽 Auto-Generated Highlight Reels")
            for i
