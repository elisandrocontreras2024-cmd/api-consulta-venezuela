from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import concurrent.futures

app = FastAPI(title="DRIEMX OSINT Engine", version="1.0")

# Habilitar CORS para conectar desde cualquier interfaz
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lista de plataformas para auditar
PLATAFORMAS = {
    "GitHub": "https://github.com/{}",
    "Instagram": "https://www.instagram.com/{}/",
    "TikTok": "https://www.tiktok.com/@{}",
    "Telegram": "https://t.me/{}",
    "Pinterest": "https://www.pinterest.com/{}/",
    "Reddit": "https://www.reddit.com/user/{}",
    "Steam": "https://steamcommunity.com/id/{}",
    "Twitch": "https://www.twitch.tv/{}",
    "SoundCloud": "https://soundcloud.com/{}",
    "Medium": "https://medium.com/@{}"
}

def verificar_red(nombre_red, url_template, username):
    url = url_template.format(username)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(url, headers=headers, timeout=3, allow_redirects=True)
        # Si devuelve status 200 OK, la cuenta existe
        existe = response.status_code == 200
        return {
            "plataforma": nombre_red,
            "url": url,
            "existe": existe,
            "status_code": response.status_code
        }
    except Exception:
        return {
            "plataforma": nombre_red,
            "url": url,
            "existe": False,
            "status_code": 0
        }

@app.get("/")
def home():
    return {"status": "Servidor DRIEMX OSINT activo"}

@app.get("/search/username")
def buscar_username(username: str):
    if not username or len(username) < 2:
        raise HTTPException(status_code=400, detail="Ingresa un usuario válido")

    resultados = []
    
    # Hilos en paralelo para que la búsqueda sea ultra rápida
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(verificar_red, red, template, username)
            for red, template in PLATAFORMAS.items()
        ]
        for future in concurrent.futures.as_completed(futures):
            resultados.append(future.result())

    encontrados = [r for r in resultados if r["existe"]]

    return {
        "target_username": username,
        "total_plataformas_escaneadas": len(PLATAFORMAS),
        "coincidencias_encontradas": len(encontrados),
        "resultados": resultados
    }
    
