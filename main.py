import os
import asyncio
from fastapi import FastAPI, Request
import uvicorn
import httpx

app = FastAPI()

TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"
PORT = int(os.environ.get("PORT", 10000))

PLATAFORMAS = {
    "GitHub": "https://github.com/{}",
    "Instagram": "https://instagram.com/{}",
    "TikTok": "https://tiktok.com/@{}",
    "X (Twitter)": "https://x.com/{}",
    "Telegram": "https://t.me/{}",
    "Reddit": "https://reddit.com/user/{}",
    "Pinterest": "https://pinterest.com/{}",
    "SoundCloud": "https://soundcloud.com/{}",
    "Steam": "https://steamcommunity.com/id/{}",
    "Spotify": "https://open.spotify.com/user/{}"
}

@app.get("/")
def read_root():
    return {"status": "Bot de Telegram activo y operativo"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        
        if text == "/start":
            await enviar_teclado(chat_id)
        else:
            await procesar_busqueda(chat_id, text)
            
    elif "callback_query" in data:
        query = data["callback_query"]
        chat_id = query["message"]["chat"]["id"]
        data_val = query["data"]
        
        if data_val == "buscar_redes":
            await enviar_mensaje(chat_id, "✍️ Envía el **nombre de usuario** que deseas escanear:")
            
    return {"ok": True}

async def enviar_teclado(chat_id):
    async with httpx.AsyncClient() as client:
        await client.post(f"{TELEGRAM_API}/sendMessage", json={
            "chat_id": chat_id,
            "text": "⚡ Sistema OSINT Activo.\nPresiona el botón para iniciar la búsqueda:",
            "reply_markup": {
                "inline_keyboard": [[{"text": "🔍 Buscar Nombre de Usuario", "callback_data": "buscar_redes"}]]
            }
        })

async def enviar_mensaje(chat_id, texto):
    async with httpx.AsyncClient() as client:
        await client.post(f"{TELEGRAM_API}/sendMessage", json={
            "chat_id": chat_id,
            "text": texto,
            "parse_mode": "Markdown"
        })

async def procesar_busqueda(chat_id, usuario):
    usuario = usuario.strip()
    await enviar_mensaje(chat_id, f"🔍 Escaneando plataformas para **{usuario}**...")
    
    resultados = []
    async with httpx.AsyncClient(follow_redirects=True, timeout=4.0) as client:
        for plataforma, url_template in PLATAFORMAS.items():
            url = url_template.format(usuario)
            try:
                resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
                if resp.status_code == 200:
                    resultados.append(f"✅ **{plataforma}:** {url}")
                else:
                    resultados.append(f"❌ **{plataforma}:** No encontrado")
            except Exception:
                resultados.append(f"⚠️ **{plataforma}:** Error de conexión")

    texto_final = f"Resultados del análisis para **{usuario}**:\n\n" + "\n".join(resultados)
    await enviar_mensaje(chat_id, texto_final)

if __name__ == "__main__":
    uvicorn.run("bot:app", host="0.0.0.0", port=PORT)
                
