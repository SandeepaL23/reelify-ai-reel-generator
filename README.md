# Reelify – Smart Reel Generator & Transcription

## Project Overview

Creating short, engaging reels from long videos is time-consuming. This project solves that by building an AI-powered reel generation system.

Reelify automatically extracts key moments from videos, converts them into short vertical clips, and adds subtitles using speech recognition. It supports both video uploads and YouTube links, making content creation faster and smarter.

## Objectives
1. Automatically generate short highlight reels (30–60 seconds)
2. Convert videos into vertical (1080x1920) reel format
3. Transcribe speech and generate captions using AI
4. Support both uploaded videos and YouTube URLs
5. Provide a simple user interface using Streamlit

## Technologies Used
1. Python
2. Streamlit
3. OpenCV
4. FFmpeg
5. Whisper (Speech-to-Text)
6. yt-dlp (YouTube downloader)

## How the System Works
1. User provides input:
2. Upload a video OR
3. Enter a YouTube URL
4. Video is downloaded (if URL is provided)
5. Video is resized to vertical reel format (1080x1920)
6. Audio is extracted from the video
7. Speech is transcribed using Whisper
8. Important segments are identified (30–60 sec highlights)
9. Captions are generated and embedded into video
10. Final reels are exported automatically

## Key Features
1. Automatic reel generation from long videos
2. Vertical video formatting for social media
3. AI-based speech transcription
4. Auto subtitle generation
5. YouTube video support
6. Fast and efficient processing

## Results
1. Successfully generates short, engaging highlight clips
2. Accurate transcription using Whisper
3. Clean subtitle rendering with ASS format
4. Works for different video formats

## Future Improvements
1. Add AI-based highlight detection (emotion/action-based)
2. Support multiple subtitle styles and languages
3. Deploy as a web application
4. Add direct sharing to social media platforms

## Requirements
1. Python 3.8+
2. FFmpeg installed and configured

### Reelify simplifies content creation by turning long videos into engaging short-form content automatically.
