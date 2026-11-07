import os
import requests
from dotenv import load_dotenv

load_dotenv() # Carga las variables definidas en el archivo .env

# Obtiene el valor de API_KEY desde el entorno
API_KEY = os.environ.get("API_KEY")

# Valida que la clave exista
if not API_KEY:
    raise SystemExit("Error: Falta API_KEY en el .env")

headers = {"Authorization": f"Bearer {API_KEY}"}

TOKEN = os.getenv("API_TOKEN")
BASE_URL = "https://midas.minsal.cl/farmacia_v2/WS/getLocalesTurnos.php"

def renovar_token():
    global TOKEN
    # Simulamos la obtención de un nuevo token o credencial
    TOKEN = "token_nuevo_simulado"
    print("[Info] Token renovado con éxito.")

def consultar_api(reintentos=1):
    headers = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/json"}
    try:
        resp = requests.get(BASE_URL, headers=headers, timeout=10)
        if resp.status_code == 401 and reintentos > 0:
            print("[Aviso] Token expirado. Renovando credenciales...")
            renovar_token()
            return consultar_api(reintentos - 1)
        resp.raise_for_status()  # Lanza error si llega 404, 500, etc.
        return resp.json()
    except requests.exceptions.Timeout:
        raise TimeoutError("El servidor externo tardó más de 10s en responder.")