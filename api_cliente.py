import os
import requests
from dotenv import load_dotenv

load_dotenv() # Carga las variables definidas en el archivo .env

# obtiene el token de la variable de entorno
TOKEN = os.getenv("API_TOKEN")
BASE_URL = "https://midas.minsal.cl/farmacia_v2/WS/getLocalesTurnos.php"

# Valida que la clave exista
if not TOKEN:
    raise SystemExit("Error: Falta TOKEN en el .env")

def renovar_token():
    global TOKEN
    # Simulamos la obtención de un nuevo token o credencial
    TOKEN = os.getenv("API_TOKEN_NUEVO","token_para_prueba")  
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

if __name__ == "__main__":
    try:
        datos = consultar_api(reintentos=1)
        print("Datos obtenidos:", datos)
    except Exception as e:
        print(f"\n[Fallo controlado detectado]: {e}")
        