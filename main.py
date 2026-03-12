import yt_dlp  # စာလုံးအသေး ဖြစ်ရပါမယ်
import whisper
import subprocess
import os
from openai import OpenAI

# =========================
# CONFIG
# =========================

# API Key ကို os.environ ကနေ ဖတ်တာက GitHub တင်ရင် ပိုလုံခြုံပါတယ်
# ဒါမှမဟုတ် "YOUR_KEY" နေရာမှာ တိုက်ရိုက်ထည့်ပါ
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY"))

TECH_TERMS = ["Python", "API", "Machine Learning", "AI", "Deep Learning", "JavaScript", "HTML", "CSS"]

# =========================
# FUNCTIONS
# =========================

def download_video(url):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]', # MP4 format သေချာစေရန်
        'outtmpl': 'input_video.mp4'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return "input_video.mp4"

def extract_audio(video):
    audio = "audio.mp3"
    command = ["ffmpeg", "-i", video, "-q:a", "0", "-map", "a", audio, "-y"]
    subprocess.run(command)
    return audio

def transcribe(audio):
    print("Loading Whisper model (base)...")
    model = whisper.load_model("base")
    result = model.transcribe(audio)
    return result["segments"]

def translate(text):
    # Technical terms တွေကို preserve လုပ်တဲ့ အဆင့်
    for term in TECH_TERMS:
        text = text.replace(term, f"[{term}]")

    prompt = f"Translate this to natural Myanmar language. Keep terms in brackets like [AI] as they are: \n{text}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are a professional translator."},
                  {"role": "user", "content": prompt}]
    )
    mm = response.choices[0].message.content
    return mm.replace("[", "").replace("]", "")

def format_time(seconds):
    td = float(seconds)
    h = int(td // 3600)
    m = int((td % 3600) // 60)
    s = td % 60
    return f"{h:02}:{m:02}:{s:06.3f}".replace('.', ',')

def generate_srt(segments):
    srt_content = ""
    for i, seg in enumerate(segments, 1):
        start = format_time(seg['start'])
        end = format_time(seg['end'])
        mm_text = translate(seg['text'])
        srt_content += f"{i}\n{start} --> {end}\n{mm_text}\n\n"
        print(f"Processed segment {i}")

    with open("subtitle.srt", "w", encoding="utf-8") as f:
        f.write(srt_content)

def embed_subtitle(video):
    output = "final_output_mm.mp4"
    # မြန်မာစာ Font ပေါ်စေရန် Pyidaungsu သို့မဟုတ် Unicode font တစ်ခုခု သတ်မှတ်ပေးရန် လိုအပ်နိုင်သည်
    command = [
        "ffmpeg", "-i", video,
        "-vf", "subtitles=subtitle.srt",
        "-c:a", "copy",
        output, "-y"
    ]
    subprocess.run(command)
    return output

# =========================
# MAIN
# =========================

def main():
    url = input("Paste YouTube URL: ")
    try:
        video = download_video(url)
        audio = extract_audio(video)
        segments = transcribe(audio)
        generate_srt(segments)
        output = embed_subtitle(video)
        print(f"အောင်မြင်စွာ ပြီးဆုံးပါပြီ။ ဖိုင်အမည် - {output}")
    except Exception as e:
        print(f"Error တက်သွားပါတယ်: {e}")

if __name__ == "__main__":
    main()
