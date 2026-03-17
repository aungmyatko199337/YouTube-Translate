# YouTube Dual Subtitle Generator (EN + MM)

A Python-based tool that downloads YouTube videos, transcribes speech using Whisper AI, and generates dual subtitles (English and Myanmar) using Google's Gemini 1.5 Flash API.

## Features
- **Dual Subtitles**: Shows both English and Myanmar text simultaneously.
- **AI Powered**: High-quality transcription with Whisper and natural translation with Gemini.
- **Cost Effective**: Uses Gemini API Free Tier and Whisper's open-source model.

## Setup
1. Add your `GEMINI_API_KEY` to your environment variables/secrets.
2. Install requirements: `pip install -r requirements.txt`
3. Run: `python main.py`
