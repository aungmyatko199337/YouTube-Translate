import yt_dlp
import whisper
import subprocess
import os
import google.generativeai as genai

# =========================
# CONFIG
# =========================

# Google AI Studio ကရတဲ့ API Key ကို ဒီမှာထည့်ပါ
GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"
genai.configure(api_key=GOOGLE_API_KEY)

# Gemini 1.5 Flash က မြန်ဆန်ပြီး Free Tier အတွက် အဆင်ပြေပါတယ်
model = genai.GenerativeModel('gemini-1.5-flash')

TECH_TERMS = ["Python", "API", "Machine Learning", "AI", "Deep Learning", "JavaScript", "HTML", "CSS"]

# =========================
# YOUTUBE DOWNLOAD
# =========================

def download_video(url):
    print("Downloading video...")
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'outtmpl': 'input_video.mp4'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return "input_video.mp4"

# =========================
# AUDIO EXTRACT
# =========================

def extract_audio(video):
    print("Extracting audio...")
    audio = "audio.mp3"
    command = ["ffmpeg", "-i", video, "-q:a", "0", "-map", "a", audio, "-y"]
    subprocess.run(command)
    return audio

# =========================
# WHISPER TRANSCRIBE
# =========================

def transcribe(audio):
    print("Loading Whisper model (base)...")
    whisper_model = whisper.load_model("base")
    result = whisper_model.transcribe(audio)
    return result["segments"]

# =========================
# GEMINI TRANSLATION
# =========================

def translate_text(text):
    # Technical terms တွေကို ကွင်းစကွင်းပိတ်နဲ့ ခဏခွဲထားမယ်
    for term in TECH_TERMS:
        text = text.replace(term, f"[{term}]")

    prompt = f"""
    You are a professional English to Myanmar translator. 
    Translate the following sentence into natural-sounding, conversational Myanmar language.
    Keep technical terms inside brackets like [AI] or [API] in English.
    
    Sentence: {text}
    """
    
    try:
        response = model.generate_content(prompt)
        mm_text = response.text.strip()
        # ကွင်းစကွင်းပိတ်တွေ ပြန်ဖြုတ်မယ်
        return mm_text.replace("[", "").replace("]", "")
    except Exception as e:
        print(f"Translation error: {e}")
        return text

# =========================
# SRT GENERATION & EMBED
# =========================

def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02}:{m:02}:{s:06.3f}".replace('.', ',')

def generate_srt(segments):
    print("Translating and generating SRT...")
    srt_content = ""
    for i, seg in enumerate(segments, 1):
        start = format_time(seg['start'])
        end = format_time(seg['end'])
        mm_text = translate_text(seg['text'])
        srt_content += f"{i}\n{start} --> {end}\n{mm_text}\n\n"
    
    with open("subtitle.srt", "w", encoding="utf-8") as f:
        f.write(srt_content)

def embed_subtitle(video):
    print("Embedding subtitles into video...")
    output = "final_output_mm.mp4"
    # FFmpeg သုံးပြီး Hardcode subtitle ထိုးခြင်း
    command = [
        "ffmpeg", "-i", video,
        "-vf", "subtitles=subtitle.srt",
        output, "-y"
    ]
    subprocess.run(command)
    return output

# =========================
# MAIN PROCESS
# =========================

def main():
    url = input("Paste YouTube URL: ")
    
    try:
        video = download_video(url)
        audio = extract_audio(video)
        segments = transcribe(audio)
        generate_srt(segments)
        final_video = embed_subtitle(video)
        
        print("\n--- DONE! ---")
        print(f"Your subtitled video is ready: {final_video}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
