# Bitácora de Auditoría Técnica con IA — Proyecto Ecotechk (Unidad 3)

Este documento registra el proceso de revisión, auditoría y refactorización asistida por IA sobre el consumo de servicios externos, persistencia en Oracle y seguridad de credenciales del proyecto `Ecotechk`.

---

## 1. Auditoría de las 5 Señales de Riesgo

| # | Señal de Riesgo Auditada | Archivos Revisados | Hallazgo y Acción Tomada | Justificación Técnica |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **`f-strings` o concatenación en SQL** | `infraestructura/empleado_repositorio.py`, `infraestructura/farmacia_repositorio.py` | **Verificado / Corregido:** Todas las consultas utilizan marcadores posicionales de Oracle (`:1, :2, :3...`) y `executemany`. | Previene ataques de **Inyección SQL (SQLi)** al separar la estructura de la consulta de los datos ingresados por el usuario o provenientes de la API externa. |
| **2** | **`verify=False` en peticiones HTTPS** | `api_cliente.py` | **Descartado / Prohibido:** Ninguna llamada a `requests.get(...)` desactiva la validación de certificados TLS/SSL. | Mantener la verificación de certificados por defecto (`verify=True`) evita ataques *Man-in-the-Middle* (MitM) y garantiza la autenticidad del servidor externo (`midas.minsal.cl`). |
| **3** | **Silenciamiento de errores (`except: pass`)** | `api_cliente.py`, `dominio/farmacia_turno.py`, `infraestructura/conexion.py` | **Modificado / Rechazado:** Se eliminaron bloques genéricos sin trazabilidad; se capturan excepciones específicas (`Timeout`, `ConnectionError`, `HTTPError`, `oracledb.Error`, `ValueError`) con registro explícito o degradación controlada. | Ocultar fallos con `except: pass` impide diagnosticar caídas de red, errores de autenticación (`401`) o fallos de base de datos, provocando estados inconsistentes difíciles de depurar. |
| **4** | **Llamadas HTTP sin `timeout`** | `api_cliente.py` | **Aceptado e implementado:** Se estableció `timeout=10` obligatorio en `requests.get(BASE_URL, headers=headers, timeout=timeout)`. | Sin un tiempo límite explícito, una caída o lentitud en el servidor externo dejaría el hilo de ejecución bloqueado indefinidamente, agotando recursos del sistema. |
| **5** | **Librerías inexistentes en PyPI (Alucinaciones)** | `requirements.txt`, `api_cliente.py`, `infraestructura/conexion.py`, `infraestructura/empleado_repositorio.py` | **Auditado y validado:** Todas las dependencias utilizadas (`requests`, `python-dotenv`, `oracledb`, `bcrypt`) existen en PyPI, están declaradas en `requirements.txt` y probadas en el entorno virtual `.venv`. | Verificar cada paquete contra PyPI evita errores de instalación (`ModuleNotFoundError`) y previene riesgos de seguridad asociados a paquetes falsos (*typosquatting*). |

---

## 2. Resumen de Decisiones de Arquitectura y Refactorización

* **Aceptado (Manejo diferenciado de códigos HTTP y Reintentos):** Se implementó una política de reintentos acotada (`max_reintentos=3`) con *Exponential Backoff* (`1s`, `2s`, `4s`) exclusivamente para errores recuperables de red o servidor (`5xx`). Ante `429 Too Many Requests` se respeta la cabecera `Retry-After`; ante `401` se renueva el token una única vez; ante errores definitivos de cliente (`4xx`) se abortan los reintentos de inmediato.
* **Modificado (Complejidad Cognitiva — SonarQube):** La función original `consultar_api` superaba el límite permitido de complejidad cognitiva (20 frente a un máximo de 15). Se refactorizó extrayendo `_ejecutar_peticion` y `_obtener_espera_retry_after` para mantener funciones pequeñas con responsabilidad única.
* **Aceptado (Deserialización y Degradación Controlada / Plan B):** Se creó la clase `FarmaciaTurno` en `dominio/farmacia_turno.py` para validar y transformar el JSON antes de persistirlo en Oracle (`farmacia_turno`). Si la API externa falla o no hay conexión a internet, `obtener_datos_con_respaldo` consulta automáticamente los registros almacenados localmente en Oracle e informa su marca de tiempo (`obtenido_en`).
* **Aceptado (Gestión de Secretos y Hashing):** Las credenciales de la API (`API_TOKEN`) y de Oracle (`DB_HOST`, `DB_USUARIO`, `DB_PASSWORD`) se cargan desde `.env` (excluido en `.gitignore`), y las contraseñas de empleados se almacenan hasheadas con sal mediante `bcrypt`.