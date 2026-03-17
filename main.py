import yt_dlp
import whisper
import subprocess
import os
import google.generativeai as genai

# =========================
# CONFIG (Using Secret)
# =========================

# Secret Name ကို 'GEMINI_API_KEY' လို့ ပေးထားပေးပါ
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    print("Warning: GEMINI_API_KEY not found in environment variables.")

# =========================
# FUNCTIONS
# =========================

def download_video(url):
    print("Downloading video from YouTube...")
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'outtmpl': 'input_video.mp4'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return "input_video.mp4"

def extract_audio(video):
    print("Extracting audio...")
    audio = "audio.mp3"
    # FFmpeg သုံးပြီး အသံထုတ်ယူခြင်း
    subprocess.run(["ffmpeg", "-i", video, "-q:a", "0", "-map", "a", audio, "-y"])
    return audio

def translate_to_myanmar(text):
    if not GOOGLE_API_KEY:
        return "Translation Error (No API Key)"
        
    prompt = f"Translate the following English sentence into natural, conversational Myanmar: '{text}'. Output only the Myanmar text."
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Translation error: {e}")
        return ""

def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02}:{m:02}:{s:06.3f}".replace('.', ',')

# =========================
# DUAL SUBTITLE GENERATION
# =========================

def generate_dual_srt(segments):
    print("Translating and generating Dual Subtitles (EN+MM)...")
    srt_content = ""
    for i, seg in enumerate(segments, 1):
        start = format_time(seg['start'])
        end = format_time(seg['end'])
        en_text = seg['text'].strip()
        
        # English ကို Gemini နဲ့ မြန်မာပြန်ခြင်း
        mm_text = translate_to_myanmar(en_text)
        
        # SRT Format: အပေါ်က English၊ အောက်က မြန်မာ
        srt_content += f"{i}\n{start} --> {end}\n{en_text}\n{mm_text}\n\n"

    with open("dual_subtitles.srt", "w", encoding="utf-8") as f:
        f.write(srt_content)
    return "dual_subtitles.srt"

# =========================
# MAIN PROCESS
# =========================

def main():
    url = input("YouTube Video URL ကို ထည့်ပါ: ")
    if not url:
        print("URL မရှိပါ။")
        return

    try:
        video_file = download_video(url)
        audio_file = extract_audio(video_file)
        
        print("Transcribing with Whisper (Loading model...)...")
        # Whisper model အသေး (base) ကို သုံးထားပါတယ် (မြန်ဆန်ဖို့အတွက်)
        whisper_model = whisper.load_model("base")
        result = whisper_model.transcribe(audio_file)
        
        srt_file = generate_dual_srt(result["segments"])
        
        print("\n" + "="*20)
        print(f"အောင်မြင်စွာ ပြီးဆုံးပါပြီ!")
        print(f"Subtitle ဖိုင်အမည်: {srt_file}")
        print("="*20)
        
    except Exception as e:
        print(f"Error တစ်ခု ဖြစ်ပွားခဲ့သည်: {e}")

if __name__ == "__main__":
    main()
