from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI(title="API Consulta & OSINT Venezuela", version="2.0")

# Permitir peticiones desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Servidor OSINT activo y funcionando correctamente"}

# 1. Módulo de Consultas de Venezuela
@app.get("/consultar")
def consultar_datos(tipo: str, numero: str):
    if not numero or len(numero) < 4:
        raise HTTPException(status_code=400, detail="Número de documento o parámetro inválido")

    if tipo == "cne":
        return {
            "nombre": "ELISANDRO JOSE CONTRERAS",
            "estado_consulta": "Activo",
            "centro_electoral": "E.U. FRANCISCO DE MIRANDA - GUARICO",
            "cedula": numero,
            "tipo": "Registro Electoral (CNE)"
        }
    elif tipo == "rif":
        return {
            "nombre": "INVERSIONES DRIEMX C.A.",
            "estado_consulta": "Contribuyente Ordinario",
            "rif": f"J-{numero}-9",
            "tipo": "Registro Fiscal (SENIAT)"
        }
    elif tipo == "veh":
        return {
            "nombre": "TITULAR ASOCIADO A PLACA",
            "estado_consulta": "Registrado en INTT",
            "detalle": f"Vehículo / Placa {numero}",
            "tipo": "Registro Vehicular"
        }
    elif tipo == "jud":
        return {
            "nombre": "REGISTRO JUDICIAL",
            "estado_consulta": "Sin requisitorias activas",
            "detalle": "No presenta expedientes pendientes registrados.",
            "tipo": "Judicial / Antecedentes"
        }
    else:
        raise HTTPException(status_code=404, detail="Tipo de consulta no válido")

# 2. Módulo OSINT: Búsqueda de Usuario en Plataformas
@app.get("/osint/username")
def osint_username(username: str):
    if not username:
        raise HTTPException(status_code=400, detail="Debes ingresar un nombre de usuario")
    
    # Redes a verificar
    plataformas = {
        "GitHub": f"https://github.com/{username}",
        "Instagram": f"https://instagram.com/{username}",
        "TikTok": f"https://tiktok.com/@{username}",
        "Telegram": f"https://t.me/{username}",
        "Pinterest": f"https://pinterest.com/{username}"
    }
    
    resultados = []
    for red, url in plataformas.items():
        try:
            # Hacer petición rápida con timeout corto
            res = requests.get(url, timeout=3, headers={"User-Agent": "Mozilla/5.0"})
            existe = res.status_code == 200
            resultados.append({
                "plataforma": red,
                "url": url,
                "existe": existe,
                "estado": "Encontrado" if existe else "No detectado / Privado"
            })
        except Exception:
            resultados.append({
                "plataforma": red,
                "url": url,
                "existe": False,
                "estado": "Error de conexión"
            })
            
    return {
        "username": username,
        "total_plataformas": len(plataformas),
        "resultados": resultados
    }

# 3. Módulo OSINT: Verificación de Brechas (Leaks)
@app.get("/osint/breach")
def osint_breach(query: str):
    if not query:
        raise HTTPException(status_code=400, detail="Ingresa un correo o teléfono")
    
    # Análisis simulado de exposición de credenciales
    is_leaked = "@" in query or len(query) >= 10
    
    return {
        "objetivo": query,
        "riesgo": "ALTO" if is_leaked else "BAJO",
        "filtraciones_detectadas": 2 if is_leaked else 0,
        "fuentes_afectadas": ["Breach_Collection_2024", "ComboListDB"] if is_leaked else [],
        "recomendacion": "Cambiar contraseña e implementar 2FA inmediatamente" if is_leaked else "Sin filtraciones críticas asociadas"
    }
    