from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import concurrent.futures

app = FastAPI(title="DRIEMX OSINT Engine", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Endpoint principal para búsqueda de usernames
@app.get("/search/username")
@app.get("/consultar")
def buscar_username(username: str = None, numero: str = None, tipo: str = None):
    # Toma 'username' o 'numero' por si el frontend envía 'numero'
    target = username or numero
    if not target or len(target) < 2:
        raise HTTPException(status_code=400, detail="Ingresa un usuario válido")

    resultados = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(verificar_red, red, template, target)
            for red, template in PLATAFORMAS.items()
        ]
        for future in concurrent.futures.as_completed(futures):
            resultados.append(future.result())

    encontrados = [r for r in resultados if r["existe"]]

    return {
        "target_username": target,
        "total_plataformas_escaneadas": len(PLATAFORMAS),
        "coincidencias_encontradas": len(encontrados),
        "resultados": resultados
    }
    
