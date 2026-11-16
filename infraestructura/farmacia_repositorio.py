import oracledb
from dominio.farmacia_turno import FarmaciaTurno
from dominio.exepciones import ErrorBaseDeDatosException
from infraestructura.conexion import obtener_conexion


class FarmaciaRepositorio:
    """Persistencia en Oracle para farmacias de turno (caché y respaldo Plan B)."""

    def reemplazar_lote(self, farmacias: list[FarmaciaTurno]):
        """Actualiza la caché local en Oracle usando consultas parametrizadas."""
        if not farmacias:
            return

        sql_delete = "DELETE FROM farmacia_turno"
        sql_insert = """
            INSERT INTO farmacia_turno (
                local_id, local_nombre, comuna_nombre, direccion,
                hora_apertura, hora_cierre, telefono, obtenido_en
            ) VALUES (:1, :2, :3, :4, :5, :6, :7, :8)
        """
        filas = [
            (
                f.local_id,
                f.local_nombre,
                f.comuna_nombre,
                f.direccion,
                f.hora_apertura,
                f.hora_cierre,
                f.telefono,
                f.obtenido_en,
            )
            for f in farmacias
        ]

        try:
            with obtener_conexion() as conn, conn.cursor() as cursor:
                cursor.execute(sql_delete)
                cursor.executemany(sql_insert, filas)
        except oracledb.Error as e:
            raise ErrorBaseDeDatosException(f"Error al persistir farmacias en Oracle: {e}") from e

    def obtener_respaldo_local(self) -> tuple[list[FarmaciaTurno], str]:
        """
        Consulta los datos almacenados localmente en Oracle para el Plan B
        y devuelve la lista junto con la fecha/hora de antigüedad (obtenido_en).
        """
        sql = """
            SELECT local_id, local_nombre, comuna_nombre, direccion,
            hora_apertura, hora_cierre, telefono, obtenido_en
            FROM farmacia_turno
            ORDER BY comuna_nombre, local_nombre
        """
        try:
            with obtener_conexion() as conn, conn.cursor() as cursor:
                filas = cursor.execute(sql).fetchall()

            farmacias = [
                FarmaciaTurno(
                    local_id=fila[0],
                    local_nombre=fila[1],
                    comuna_nombre=fila[2],
                    direccion=fila[3],
                    hora_apertura=fila[4],
                    hora_cierre=fila[5],
                    telefono=fila[6],
                    obtenido_en=fila[7],
                )
                for fila in filas
            ]

            antiguedad = (
                farmacias[0].obtenido_en.strftime("%Y-%m-%d %H:%M:%S")
                if farmacias and farmacias[0].obtenido_en
                else "Sin registros previos"
            )
            return farmacias, antiguedad

        except oracledb.Error as e:
            raise ErrorBaseDeDatosException(f"Error al leer respaldo desde Oracle: {e}") from e