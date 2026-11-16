from datetime import datetime

class FarmaciaTurno:
    def __init__ (
        self, 
        local_id: str, 
        local_nombre: str, 
        comuna_nombre: str, 
        direccion: str="", 
        hora_apertura: str="", 
        hora_cierre: str="", 
        telefono: str="",
        obtenido_en: datetime | None = None,
    ):
        self.local_id = str(local_id).strip()
        self.local_nombre = str(local_nombre).strip()   
        self.comuna_nombre = str(comuna_nombre).strip()
        self.direccion = str(direccion or "").strip()
        self.hora_apertura = str(hora_apertura or "").strip()
        self.hora_cierre = str(hora_cierre or "").strip()
        self.telefono = str(telefono or "").strip()
        self.obtenido_en = obtenido_en or datetime.now()

    @classmethod
    def desde_json(cls, data: dict) -> "FarmaciaTurno":
        if not isinstance(data, dict):
            raise ValueError("El registro JSON debe ser un diccionario.")

        local_id = data.get("local_id")
        nombre = data.get("local_nombre")
        comuna = data.get("comuna_nombre")

        if not local_id or not nombre or not comuna:
            raise ValueError("registro JSON incompleto: faltan campos obligatorios(local_id, local_nombre, comuna_nombre).")

        return cls(
            local_id= local_id,
            local_nombre= nombre,
            comuna_nombre= comuna,
            direccion= data.get("local_direccion", ""),
            hora_apertura= data.get("Funcionamiento_hora_apertura", ""),
            hora_cierre= data.get("Funcionamiento_hora_cierre", ""),
            telefono= data.get("local_telefono", ""),
            obtenido_en= datetime.now()
        )

    @classmethod
    def deserializar_lista(cls, lista_json: list) -> list["FarmaciaTurno"]:
        if  not isinstance(lista_json, list):
            raise ValueError("la respuesta de la API debe ser una lista de registros.")
        
        resultado = []
        for item in lista_json:
            try:
                resultado.append(cls.desde_json(item))
            except ValueError:
                continue
        return resultado

    def __repr__(self):
        return f"FarmaciaTurno({self.local_nombre} - {self.comuna_nombre} | obtenido_en={self.obtenido_en})"
