import os
import requests
from dotenv import load_dotenv

# Carga las variables definidas en el archivo .env
load_dotenv()

# Obtiene el valor de API_KEY desde el entorno
API_KEY = os.environ.get("API_KEY")

# Valida que la clave exista
if not API_KEY:
    raise SystemExit("Error: Falta API_KEY en el .env")

headers = {"Authorization": f"Bearer {API_KEY}"}