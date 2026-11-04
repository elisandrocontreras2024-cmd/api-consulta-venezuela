from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API Consulta Venezuela", version="1.0")

# Permitir conexiones desde cualquier origen (para que tu app web en Lovable pueda consultarlo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Servidor activo y funcionando correctamente"}

@app.get("/consultar")
def consultar_datos(tipo: str, numero: str):
    """
    Recibe el tipo de búsqueda ('rif', 'cne', 'veh', 'jud') y el número de cédula/RIF.
    """
    # Validar que el número no esté vacío
    if not numero or len(numero) < 6:
        raise HTTPException(status_code=400, detail="Número de documento inválido")

    # Simulador de respuesta basada en la fuente consultada
    # (Aquí es donde posteriormente conectarás tus funciones de scraping o conexión a bases de datos reales)
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
            "estado_consulta": "Activo / Contribuyente Ordinario",
            "rif": f"J-{numero}-9",
            "tipo": "Registro Fiscal (SENIAT)"
        }
    elif tipo == "veh":
        return {
            "nombre": "ASOCIADO A PLACA / SERIAL",
            "estado_consulta": "Registrado en INTT",
            "detalle": f"Vehículo asociado al documento {numero}",
            "tipo": "Vehicular"
        }
    elif tipo == "jud":
        return {
            "nombre": "CONSULTA JUDICIAL",
            "estado_consulta": "Sin requisitorias activas",
            "detalle": "No registra solicitudes pendientes en los sistemas públicos.",
            "tipo": "Judicial / Antecedentes"
        }
    else:
        raise HTTPException(status_code=404, detail="Tipo de consulta no encontrado")
        