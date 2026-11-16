import os
import time
import requests
from dotenv import load_dotenv
from dominio.farmacia_turno import FarmaciaTurno
from infraestructura.farmacia_repositorio import FarmaciaRepositorio

load_dotenv()  # Carga las variables definidas en el archivo .env

TOKEN = os.getenv("API_TOKEN")
BASE_URL = "https://midas.minsal.cl/farmacia_v2/WS/getLocalesTurnos.php"

if not TOKEN:
    raise SystemExit("Error: Falta API_TOKEN en el .env")


class TokenExpiradoError(Exception):
    """Excepción interna para señalizar error 401."""


class TooManyRequestsError(Exception):
    """Excepción interna para señalizar error 429 con tiempo de espera."""
    def __init__(self, espera: int):
        self.espera = espera
        super().__init__(f"Límite de peticiones excedido (429). Esperar {espera}s.")


def renovar_token():
    global TOKEN
    nuevo = os.getenv("API_TOKEN_NUEVO")
    if nuevo:
        TOKEN = nuevo
    print("[Info] Proceso de renovación de credenciales ejecutado.")


def _obtener_espera_retry_after(resp) -> int:
    """Lee la cabecera Retry-After de una respuesta 429 (por defecto 5 segundos)."""
    valor = resp.headers.get("Retry-After", "5")
    try:
        return max(1, int(valor))
    except ValueError:
        return 5


def _ejecutar_peticion(timeout: int):
    """Realiza un intento único de petición y clasifica el código HTTP."""
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/json"
    }
    resp = requests.get(BASE_URL, headers=headers, timeout=timeout)

    if resp.status_code == 200:
        return resp.json()
    if resp.status_code == 401:
        raise TokenExpiradoError("Token expirado (401).")
    if resp.status_code == 429:
        raise TooManyRequestsError(_obtener_espera_retry_after(resp))
    if 400 <= resp.status_code < 500:
        raise ValueError(f"Error de cliente HTTP {resp.status_code}: No se reintentará.")
    if resp.status_code >= 500:
        raise requests.exceptions.HTTPError(f"Error del servidor externo ({resp.status_code}).")

    resp.raise_for_status()


def consultar_api(max_reintentos=3, timeout=10):
    """Orquesta reintentos acotados, HTTP 429 (Retry-After) y backoff exponencial."""
    token_renovado = False

    for intento in range(max_reintentos):
        try:
            print(f"[Info] Consultando API (Intento {intento + 1}/{max_reintentos})...")
            return _ejecutar_peticion(timeout)

        except TokenExpiradoError:
            if token_renovado:
                raise ConnectionError("El token renovado también fue rechazado (401).")
            print("[Aviso] Token expirado (401). Renovando credenciales...")
            renovar_token()
            token_renovado = True

        except TooManyRequestsError as e:
            print(f"[Aviso] {e}")
            if intento < max_reintentos - 1:
                time.sleep(e.espera)

        except ValueError as ve:
            raise ve  # Corta de inmediato ante otros errores 4xx

        except requests.exceptions.RequestException as e:
            print(f"[Aviso] Fallo de red o servidor: {e}")
            if intento < max_reintentos - 1:
                espera = 2 ** intento
                print(f"[Espera] Reintentando en {espera} segundos...")
                time.sleep(espera)

    raise ConnectionError(f"La API no respondió tras {max_reintentos} intentos.")


def obtener_datos_con_respaldo(max_reintentos=3, timeout=10) -> dict:
    """
    Intenta consumir y persistir datos frescos de la API en Oracle.
    Si falla, activa el Plan B leyendo desde Oracle e indicando su antigüedad (obtenido_en).
    """
    repo = FarmaciaRepositorio()

    try:
        datos_crudos = consultar_api(max_reintentos=max_reintentos, timeout=timeout)
        farmacias = FarmaciaTurno.deserializar_lista(datos_crudos)
        repo.reemplazar_lote(farmacias)
        print(f"[Persistencia] {len(farmacias)} registros guardados en Oracle.")
        return {
            "origen": "API_EN_VIVO",
            "antiguedad": "Actualizado ahora",
            "datos": farmacias
        }
    except Exception as e:
        print(f"\n[Degradación Activada] No se pudo conectar con la API ({e}).")
        try:
            farmacias_locales, antiguedad = repo.obtener_respaldo_local()
            print(f"[Plan B Oracle] Datos locales recuperados (obtenido_en: {antiguedad}).")
            return {
                "origen": "BASE_DE_DATOS_LOCAL",
                "antiguedad": antiguedad,
                "datos": farmacias_locales
            }
        except Exception as db_err:
            print(f"[Aviso Plan B] Base de datos no disponible ({db_err}). Operando con lista vacía controlada.")
            return {
                "origen": "SIN_DATOS_DISPONIBLES",
                "antiguedad": "N/A",
                "datos": []
            }