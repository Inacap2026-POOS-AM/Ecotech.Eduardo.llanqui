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


if __name__ == "__main__":
    main()
    