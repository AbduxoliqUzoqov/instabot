from fastapi import FastAPI, Request, BackgroundTasks
import asyncio, requests, yt_dlp

BOT_TOKEN = "8403694475:AAHYzvDudxyNHthxueWAoRSIgu3OCigzwZc"
API = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = FastAPI()

# 🔥 BIR VAQTDA NECHTA VIDEO ISHLASHI
semaphore = asyncio.Semaphore(5)  # 5 ta parallel

def send_message(chat_id, text):
    requests.post(f"{API}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

def process_video(chat_id, url):
    async def _task():
        async with semaphore:
            try:
                send_message(chat_id, "⏳ Navbatda, video tayyorlanmoqda...")

                ydl_opts = {
                    "format": "best[ext=mp4]/best",
                    "quiet": True,
                    "noplaylist": True,
                    "cookiefile": "cookies.txt"
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    video_url = info["url"]
                    
                requests.post(f"{API}/sendVideo", json={
                    "chat_id": chat_id,
                    "video": video_url,
                    "caption": "✅ Tayyor"
                })

            except Exception as e:
                send_message(chat_id, f"❌ Xatolik: {e}")

    asyncio.run(_task())

@app.post("/webhook")
async def webhook(req: Request, bg: BackgroundTasks):
    data = await req.json()

    if "message" not in data:
        return {"ok": True}

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    if "instagram.com" not in text:
        send_message(chat_id, "Instagram link yubor 📥")
        return {"ok": True}

    bg.add_task(process_video, chat_id, text)
    return {"ok": True}
