from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import concurrent.futures

app = FastAPI(title="DRIEMX OSINT Engine Pro", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Diccionario masivo de plataformas agrupadas por categoría
PLATAFORMAS = {
    # Redes Sociales & Video
    "YouTube": "https://www.youtube.com/@{}",
    "TikTok": "https://www.tiktok.com/@{}",
    "Instagram": "https://www.instagram.com/{}/",
    "Facebook": "https://www.facebook.com/{}",
    "Twitter / X": "https://x.com/{}",
    "Telegram": "https://t.me/{}",
    "Pinterest": "https://www.pinterest.com/{}/",
    "Reddit": "https://www.reddit.com/user/{}",
    "Snapchat": "https://www.snapchat.com/add/{}",

    # Música & Audio
    "Spotify": "https://open.spotify.com/user/{}",
    "SoundCloud": "https://soundcloud.com/{}",
    "Bandcamp": "https://bandcamp.com/{}",
    "Last.fm": "https://www.last.fm/user/{}",

    # Desarrollo, Código & Tech
    "GitHub": "https://github.com/{}",
    "GitLab": "https://gitlab.com/{}",
    "Replit": "https://replit.com/@{}",
    "Dev.to": "https://dev.to/{}",
    "Docker Hub": "https://hub.docker.com/u/{}",
    "Pypi (Python)": "https://pypi.org/user/{}/",

    # Gaming & Streaming
    "Twitch": "https://www.twitch.tv/{}",
    "Steam": "https://steamcommunity.com/id/{}",
    "Roblox": "https://www.roblox.com/user.aspx?username={}",
    "Chess.com": "https://www.chess.com/member/{}",

    # Blogs & Contenido
    "Medium": "https://medium.com/@{}",
    "Blogger": "https://{}.blogspot.com/",
    "WordPress": "https://{}.wordpress.com/",
    "Patreon": "https://www.patreon.com/{}"
}

def verificar_red(nombre_red, url_template, username):
    url = url_template.format(username)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=3.5, allow_redirects=True)
        # Verificación inteligente de respuesta
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
    return {"status": "Motor DRIEMX OSINT Pro Activo"}

@app.get("/search/username")
@app.get("/consultar")
def buscar_username(username: str = None, numero: str = None):
    target = username or numero
    if not target or len(target) < 2:
        raise HTTPException(status_code=400, detail="Ingresa un nombre de usuario válido")

    resultados = []
    
    # Aumentamos los hilos en paralelo a 20 para mantener velocidad relámpago
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [
            executor.submit(verificar_red, red, template, target)
            for red, template in PLATAFORMAS.items()
        ]
        for future in concurrent.futures.as_completed(futures):
            resultados.append(future.result())

    # Ordenar alfabéticamente por nombre de plataforma
    resultados.sort(key=lambda x: x["plataforma"])
    encontrados = [r for r in resultados if r["existe"]]

    return {
        "target_username": target,
        "total_plataformas_escaneadas": len(PLATAFORMAS),
        "coincidencias_encontradas": len(encontrados),
        "resultados": resultados
    }
    
