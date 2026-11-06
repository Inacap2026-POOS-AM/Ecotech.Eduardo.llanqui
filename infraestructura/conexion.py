# infraestructura/conexion.py
import os
import oracledb
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

class ErrorDeConexion(Exception):
    """La base de datos no está disponible."""

@contextmanager
def obtener_conexion():
    host = os.environ.get("DB_HOST")
    usuario = os.environ.get("DB_USUARIO")
    password = os.environ.get("DB_PASSWORD")

    if not host or not usuario or not password:
        raise ErrorDeConexion("Sin variables de entorno para Oracle. ¿Copiaste el .env.example?")

    conn = None
    try:
        # Modo thin de oracledb (no requiere Oracle Client instalado)
        conn = oracledb.connect(user=usuario, password=password, dsn=host)
        yield conn
        conn.commit()
    except oracledb.Error as e:
        if conn:
            conn.rollback()
        raise ErrorDeConexion(f"No se pudo operar sobre la base Oracle: {e}") from e
    finally:
        if conn:
            conn.close()