import re

def validar_codigo_empleado(codigo: str) -> bool:
    """
    Regla: formato 'ECO-XXXXX' con 5 digitos exactos.
    Rechaza entradas maliciosas o mal formateadas antes de procesarlas
    """
    patron = r"^ECO-\d{5}$"
    return bool(re.match(patron, codigo))

def procesar_farmacia(registro: dict) -> dict:
    """
    get .get() con valores por defecto evita KeyError ante canbios de  la API
    Aplica limpieza defensiva( .strip(), .upeer()).
    """
    return {
        "nombre": registro.get("local_nombre", "sin nombre").strip(),
        "direccion": registro.get("local_direccion", "desconocida").strip(),
        "comuna": registro.get("comuna_nombre", "desconocida").upper(),
    }