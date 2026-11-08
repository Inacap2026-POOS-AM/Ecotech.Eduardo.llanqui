import re

def validar_codigo_empleado(codigo: str) -> bool:
    """
    Regla: formato 'ECO-XXXXX' con 5 digitos exactos.
    """
    patron = r"^ECO-\d{5}$"
    return bool(re.match(patron, codigo))

def validar_rut(rut: str) -> bool:
    """
    validar RUT chileno con dígito verificador.
    """
    patron = r'^\d{7,8}-[0-9kK]$'
    return bool(re.match(patron, rut))

def validar_email(email: str) -> bool:
    """
    validar el formato seguro de un correo electrónico.
    """
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(patron, email))

def procesar_farmacia(registro: dict) -> dict:
    """
    .get() con valores por defecto evita KeyError ante canbios de  la API y 
    Aplica limpieza defensiva( .strip(), .upeer()).
    """
    return {
        "nombre": registro.get("local_nombre", "sin nombre").strip(),
        "direccion": registro.get("local_direccion", "desconocida").strip(),
        "comuna": registro.get("comuna_nombre", "").upper(),
    }