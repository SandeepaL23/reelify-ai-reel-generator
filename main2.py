import streamlit as st
from modules.ui import login_register_ui, video_processing_ui

# -------------------------
# Streamlit Page Setup
# -------------------------
st.set_page_config(page_title="🎬 Reelify", page_icon="🎥", layout="centered")
st.title("🎬 Reelify - Smart Reel Generator & Transcription")

# -------------------------
# Session State Initialization
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "video" not in st.session_state:
    st.session_state.video = None

# -------------------------
# Authentication & UI Routing
# -------------------------
if not st.session_state.logged_in:
    # Show login & register form
    login_register_ui()
else:
    # Sidebar for logged-in users
    st.sidebar.write(f"👋 Welcome, **{st.session_state.user_email}**")
    if st.sidebar.button("Logout"):
        # Reset session on logout
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.session_state.video = None
        st.experimental_rerun()

    # Show the video processing interface
    video_processing_ui()
