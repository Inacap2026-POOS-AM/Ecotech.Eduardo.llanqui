from datetime import date
import oracledb
import re
import bcrypt
from dominio.empleado import Empleado
from dominio.exepciones import EmpleadoYaExisteException, ErrorBaseDeDatosException
from infraestructura.conexion import obtener_conexion
from validador import validar_rut, validar_email

class EmpleadoRepositorio:
    def __init__(self):
        self.db = obtener_conexion()
    
    def guardar_empleado_seguro(self, rut, email, password_plana):
        if not validar_rut(rut):
            raise ValueError("Error de seguridad: el RUT '{rut}' no cumple con el formato valido ")

        if not validar_email(email):
            raise ValueError("Error de seguridad: el email '{email}' no cumple con el formato valido ")
        
        password_bytes = password_plana.encode('utf-8')
        sal = bcrypt.gensalt(rounds=12)
        password_hash = bcrypt.hashpw(password_bytes, sal).decode('utf-8')

        cursor = None
        try:
            cursor = self.db.cursor()

            sql = "INSERT INTO empleados (rut, email, password_hash) VALUES (:1, :2, :3)"
            cursor.execute(sql, (rut, email, password_hash))

            self.db.commit()
            print(f"[Exito] Empleado con RUT {rut} guardado con seguridad en oracle.")

        except EmpleadoYaExisteException:
            print(f"[Error] El empleado con RUT {rut} ya existe en la base de datos.")

        except Exception as e:
            self.conexion.rollback()
            print(f"[Error en Oracle]: {e}")
        finally:
            if cursor:
                cursor.close()

    def cerrar_conexion(self):
        if self.db:
            self.db.close() 

    @staticmethod
    def _fila_a_empleado(fila):
        fecha = fila[2]
        if isinstance(fecha, str):
            fecha_obj = date.fromisoformat(fecha[:10])
        else:
            fecha_obj = fecha.date() if hasattr(fecha, 'date') else fecha
            
        return Empleado(
            rut=fila[0],
            nombre=fila[1],
            fecha_ingreso=fecha_obj,
            sueldo_base=fila[3],
            activo=fila[4] if len(fila) > 4 else 1
        )

    def obtener(self, rut: str):
        try:
            with obtener_conexion() as conn, conn.cursor() as cursor:
                fila = cursor.execute(
            """SELECT p.rut, p.nombre, e.fecha_ingreso, e.sueldo_base, e.activo 
            FROM empleado e JOIN persona p ON p.rut = e.rut 
            WHERE e.rut = :1""",
            (rut,),
            ).fetchone()
            return self._fila_a_empleado(fila) if fila else None
        except oracledb.DatabaseError as e:
            error, = e.args
            raise ErrorBaseDeDatosException(f"Error al obtener el empleado: {error.message}") from e

    def listar(self, nombre_contiene=None):
        sql = """SELECT p.rut, p.nombre, e.fecha_ingreso, e.sueldo_base, e.activo 
            FROM empleado e JOIN persona p ON p.rut = e.rut 
            WHERE e.activo = 1"""
        params = []
        if nombre_contiene:
            sql += " AND UPPER(p.nombre) LIKE UPPER(:1)"
            params.append(f"%{nombre_contiene}%")
        try:
            with obtener_conexion() as conn, conn.cursor() as cursor:
                filas = cursor.execute(sql, params).fetchall()
            return [self._fila_a_empleado(f) for f in filas]
        except oracledb.DatabaseError as e:
            error, = e.args
            raise ErrorBaseDeDatosException(f"Error al listar empleados: {error.message}") from e
        
    def actualizar(self, empleado: Empleado):
        try:
            with obtener_conexion() as conn, conn.cursor() as cursor:
                cursor.execute("UPDATE empleado SET sueldo_base = :1 WHERE rut = :2",
                (empleado.sueldo_base, empleado.rut),
                )
                conn.commit()
                return cursor.rowcount
        except oracledb.DatabaseError as e:
            error, = e.args
            raise ErrorBaseDeDatosException(f"Error al actualizar el empleado: {error.message}") from e


    def eliminar(self, rut: str):
        try:
            with obtener_conexion() as conn, conn.cursor() as cursor:
                cursor.execute("UPDATE empleado SET activo = 0 WHERE rut = :1", (rut,))
                conn.commit()
                return cursor.rowcount > 0
        except oracledb.DatabaseError as e:
            error, = e.args
            raise ErrorBaseDeDatosException(f"Error al eliminar el empleado: {error.message}") from e