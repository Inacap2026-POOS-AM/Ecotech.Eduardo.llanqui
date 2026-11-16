from dominio.empleado import Empleado
from dominio.departamento import Departamento
from dominio.registro_tiempo import RegistroTiempo
from api_cliente import obtener_datos_con_respaldo

def main():
    # prueba de modelos de dominio
    dep = Departamento("Operaciones")
    nelson = Empleado("15000321-9", "Nelson Llanquileo", "2024-03-01", 950_000)
    dep.agregar_empleado(nelson)

    reg1 = RegistroTiempo("R01", "2024-04-01", 8.0, "Desarrollo de modulo")
    reg2 = RegistroTiempo("R02", "2024-04-02", 7.5, "Reunion de avance")
    nelson.registrar_hora(reg1)
    nelson.registrar_hora(reg2)

    print(dep)
    print(nelson)
    print(f"Horas registradas para {nelson.nombre}: {nelson.total_horas()} hrs")

    # prueba de integracion con la API (endurecer + degradar)
    print("\nConsultando servicio externo de farmacias")
    resultado = obtener_datos_con_respaldo(max_reintentos=3, timeout=10)
    print(f"Origen de los datos : {resultado['origen']}")
    print(f"Antiguedad (obtenido_en): {resultado['antiguedad']}")
    print(f"Cantidad de registros obtenidos: {len(resultado['datos'])}")
    
if __name__ == "__main__":
    main()
    