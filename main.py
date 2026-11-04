from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI(title="API Consulta Real Venezuela", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar y crear la base de datos local SQLite al arrancar el servidor
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personas (
            cedula TEXT PRIMARY KEY,
            nombre TEXT,
            estado TEXT,
            centro_electoral TEXT,
            rif TEXT
        )
    """)
    # Insertar registros de prueba iniciales (puedes agregar o modificar los que quieras aquí)
    registros_iniciales = [
        ('12345678', 'JUAN PEREZ (Registro Real)', 'Activo', 'U.E. Simon Bolívar - Guárico', 'V-12345678-9'),
        ('87654321', 'MARIA RODRIGUEZ (Registro Real)', 'Activo', 'E.B. Jose Antonio Páez', 'V-87654321-0')
    ]
    cursor.executemany("INSERT OR IGNORE INTO personas VALUES (?, ?, ?, ?, ?)", registros_iniciales)
    conn.commit()
    conn.close()

# Ejecutar la creación de la base de datos
init_db()

@app.get("/")
def home():
    return {"status": "Servidor con Base de Datos Activo"}

# Módulo de consulta conectado a la Base de Datos
@app.get("/consultar")
def consultar_datos(tipo: str, numero: str):
    if not numero or len(numero) < 6:
        raise HTTPException(status_code=400, detail="Número de documento inválido")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    # Consulta SQL exacta por número de cédula
    cursor.execute("SELECT nombre, estado, centro_electoral, rif FROM personas WHERE cedula = ?", (numero,))
    row = cursor.fetchone()
    conn.close()

    # Si la cédula no está registrada en la base de datos, devuelve 404 real
    if not row:
        raise HTTPException(status_code=404, detail="No se encontraron registros para este número")

    return {
        "cedula": numero,
        "nombre": row[0],
        "estado_consulta": row[1],
        "centro_electoral": row[2] if row[2] else "No aplica",
        "rif": row[3] if row[3] else "No asignado",
        "tipo_consulta": tipo.upper()
    }

# Endpoint auxiliar para insertar nuevos registros reales a tu base de datos vía POST o script
@app.post("/agregar")
def agregar_registro(cedula: str, nombre: str, estado: str, centro: str, rif: str):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO personas VALUES (?, ?, ?, ?, ?)", (cedula, nombre, estado, centro, rif))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="La cédula ya existe en la base de datos")
    finally:
        conn.close()
    return {"status": "Registro agregado exitosamente", "cedula": cedula}
    
