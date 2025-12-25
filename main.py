from fastapi import FastAPI, Request, BackgroundTasks
import asyncio, requests, yt_dlp

BOT_TOKEN = "8403694475:AAHYzvDudxyNHthxueWAoRSIgu3OCigzwZc"

API = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = FastAPI()
semaphore = asyncio.Semaphore(1)  # Fly free uchun 1 ta parallel

def send(chat_id, text):
    requests.post(f"{API}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

def worker(chat_id, url):
    async def job():
        async with semaphore:
            try:
                send(chat_id, "⏳ Video tayyorlanmoqda...")

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
                send(chat_id, f"❌ Xatolik: {e}")

    asyncio.run(job())

@app.post("/webhook")
async def webhook(req: Request, bg: BackgroundTasks):
    data = await req.json()

    if "message" not in data:
        return {"ok": True}

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    if "instagram.com" not in text:
        send(chat_id, "Instagram link yubor 📥")
        return {"ok": True}

    bg.add_task(worker, chat_id, text)
    return {"ok": True}
