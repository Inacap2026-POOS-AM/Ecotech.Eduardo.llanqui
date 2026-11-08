from datetime import date
import oracledb
from dominio.empleado import Empleado
from dominio.exepciones import EmpleadoYaExisteException, ErrorBaseDeDatosException
from infraestructura.conexion import obtener_conexion
from seguridad_hash import registrar_usuario_hash

class EmpleadoRepositorio:
    def __init__(self):
        self.db = obtener_conexion()
    
    def guardar_empleado_seguro(self, rut, nombre, password_plana):
        cursor = self.db.cursor()

        password_hash = registrar_usuario_hash(nombre, password_plana)
        
        try:
            sql = "INSERT INTO empleados (rut, nombre, password_hash) VALUES (:1, :2, :3)"
            cursor.execute(sql, (rut, nombre, password_hash))
            self.db.commit()
            print(f"[Exito] Empleado {nombre} con RUT {rut} guardado con seguridad en oracle.")
        except EmpleadoYaExisteException:
            print(f"[Error] El empleado con RUT {rut} ya existe en la base de datos.")
        except Exception as e:
            print(f"[Error] No se pudo guardar el empleado {nombre} con RUT {rut}: {e}")
        finally:
            cursor.close()

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