from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import re
import requests
import concurrent.futures

app = FastAPI(title="DRIEMX OSINT Engine Pro", version="5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PLATAFORMAS_USERNAME = {
    "GitHub": "https://github.com/{}",
    "Instagram": "https://www.instagram.com/{}/",
    "TikTok": "https://www.tiktok.com/@{}",
    "Telegram": "https://t.me/{}",
    "Pinterest": "https://www.pinterest.com/{}/",
    "Reddit": "https://www.reddit.com/user/{}",
    "Steam": "https://steamcommunity.com/id/{}",
    "Twitch": "https://www.twitch.tv/{}"
}

def verificar_red(nombre_red, url_template, username):
    url = url_template.format(username)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(url, headers=headers, timeout=3.5, allow_redirects=True)
        return {
            "plataforma": nombre_red,
            "url": url,
            "existe": response.status_code == 200,
            "status_code": response.status_code
        }
    except Exception:
        return {"plataforma": nombre_red, "url": url, "existe": False, "status_code": 0}

@app.get("/")
def home():
    return {"status": "Motor DRIEMX OSINT Pro Activo"}

@app.get("/search/username")
def buscar_username(username: str):
    if not username or len(username) < 2:
        raise HTTPException(status_code=400, detail="Ingresa un usuario válido")

    resultados = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(verificar_red, red, template, username)
            for red, template in PLATAFORMAS_USERNAME.items()
        ]
        for future in concurrent.futures.as_completed(futures):
            resultados.append(future.result())

    resultados.sort(key=lambda x: x["plataforma"])
    encontrados = [r for r in resultados if r["existe"]]

    return {
        "target_username": username,
        "total_plataformas_escaneadas": len(PLATAFORMAS_USERNAME),
        "coincidencias_encontradas": len(encontrados),
        "resultados": resultados
    }

@app.get("/search/phone")
def buscar_telefono(phone: str):
    if not phone:
        raise HTTPException(status_code=400, detail="Debes ingresar un número de teléfono")

    # Asegurar el prefijo '+' para análisis E.164
    formatted_input = phone if phone.startswith("+") else f"+{phone}"

    try:
        parsed_number = phonenumbers.parse(formatted_input, None)
    except phonenumbers.NumberParseException:
        raise HTTPException(status_code=400, detail="El formato del número de teléfono es inválido")

    if not phonenumbers.is_possible_number(parsed_number):
        raise HTTPException(status_code=400, detail="El número no coincide con la longitud estándar del país")

    es_valido = phonenumbers.is_valid_number(parsed_number)
    
    # Análisis de ubicación y proveedor de telefonía
    region = geocoder.description_for_number(parsed_number, "es") or "Desconocida"
    operadora = carrier.name_for_number(parsed_number, "es") or "Operadora desconocida / Línea fija"
    zonas_horarias = list(timezone.time_zones_for_number(parsed_number))
    
    # Formatos de salida estandarizados
    e164_format = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
    national_format = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL)
    international_format = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    
    clean_digits = re.sub(r'\D', '', e164_format)

    return {
        "valido": es_valido,
        "numero_ingresado": phone,
        "formatos": {
            "e164": e164_format,
            "nacional": national_format,
            "internacional": international_format
        },
        "geolocalizacion": {
            "pais_region": region,
            "codigo_pais": parsed_number.country_code,
            "zonas_horarias": zonas_horarias
        },
        "telefonia": {
            "operadora": operadora,
            "tipo_linea": "Móvil / Celular" if phonenumbers.number_type(parsed_number) == phonenumbers.PhoneNumberType.MOBILE else "Fija / OTRO"
        },
        "vectores_mensajeria": {
            "whatsapp_direct": f"https://wa.me/{clean_digits}",
            "telegram_direct": f"https://t.me/+{clean_digits}"
        }
    }
    
