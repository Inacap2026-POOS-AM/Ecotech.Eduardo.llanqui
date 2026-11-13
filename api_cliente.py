import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("API_TOKEN")
BASE_URL = "https://midas.minsal.cl/farmacia_v2/WS/getLocalesTurnos.php"
ARCHIVO_RESPALDO = "respaldo_farmacias.json"

if not TOKEN:
    raise SystemExit("Error: Falta TOKEN en el .env")

class TokenExpiradoError(Exception):
    """Excepcion interna para indicar que el token ha expirado y necesita ser renovado."""

def renovar_token():
    global TOKEN
    TOKEN = os.getenv("API_TOKEN_NUEVO","token_para_prueba")  
    print("[Info] Token renovado con éxito.")

def guardar_respaldo_local(datos):
    try:
        with open(ARCHIVO_RESPALDO, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=2)
        print(f"[Info] Respaldo local guardado en {ARCHIVO_RESPALDO}.")
    except OSError as e:
        print(f"[Error] No se pudo guardar el respaldo local: {e}")

def cargar_respaldo_local():
    if os.path.exists(ARCHIVO_RESPALDO):
        try:
            with open(ARCHIVO_RESPALDO, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
            print(f"[Info] Respaldo local cargado desde {ARCHIVO_RESPALDO}.")
            return datos
        except (OSError, json.JSONDecodeError) as e:
            print(f"[Error] No se pudo cargar el respaldo local: {e}")

    print("[plan B] usando datos minimos de emergencia en memoria")
    return [
        {
        "local_nombre": "Farmacia de Turno", 
        "comuna_nombre": "Santiago", 
        "local_direccion": "Av. Providencia 1234", 
        "Hora_apertura": "20:00:00",
        "hora_cierre": "08:00:00"
        }
        ]

def _ejecutar_peticion(timeout):
    headers = {"Authorization": f"Bearer {TOKEN}",
            "Accept": "application/json"}
    resp = requests.get(BASE_URL, headers=headers, timeout=timeout)

    if resp.status_code == 200:
        return resp.json()
    if resp.status_code == 401:
        raise TokenExpiradoError("Token expirado (401).")
    if 400 <= resp.status_code < 500:
        raise ValueError(f"Error de cliente HTTP: {resp.status_code}")
    if resp.status_code >= 500:
        raise ConnectionError(f"Error de servidor externo: {resp.status_code}")

    resp.raise_for_status()  # Lanza una excepción para otros códigos de estado HTTP inesperados

def consultar_api(max_reintentos=3, timeout=10):
    
    token_renovado = False

    for intento in range(max_reintentos):
        try:
            print(f"[Info] Intentando consultar la API (Intento {intento + 1}/{max_reintentos})...")
            return _ejecutar_peticion(timeout)
        
        except TokenExpiradoError:
            if token_renovado:
                raise ConnectionError("Error: El token ha expirado nuevamente después de la renovación.")
            print("[Aviso] Token expirado (401). Renovando token...")
            renovar_token()
            token_renovado = True

        except ValueError as ve:
            raise ve # corta de inmediato ante errores 4xx

        except requests.exceptions.RequestException as e:
            print(f"[Aviso] Fallo en la peticion: {e}")
            if intento < max_reintentos - 1:
                espera = 2 ** intento
                print(f"[Espera] Reintentando en {espera} segundos...")
                time.sleep(espera)

    raise ConnectionError(f"Error: No se pudo obtener una respuesta válida de la API después de {max_reintentos} intentos.")

def obtener_datos_con_respaldo(max_reintentos=3, timeout=10):
    try:
        datos = consultar_api(max_reintentos=max_reintentos, timeout=timeout)
        guardar_respaldo_local(datos)
        return datos
    except Exception as e:
        print(f"[Error] No se pudo obtener datos de la API: {e}")
        print("[Info] Intentando cargar respaldo local...")
        return cargar_respaldo_local()
        
if __name__ == "__main__":
    resultado = obtener_datos_con_respaldo(max_reintentos=3, timeout=10)
    print(f"[Resultado] Datos obtenidos: {resultado}")
    print(f"[Info] Respaldo local guardado en {ARCHIVO_RESPALDO}.")
        