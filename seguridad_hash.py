import bcrypt

def preparar_registro_usuario(nombre_usuario, password_plana):
    """
    Prepara los datos de un usuario para ser insertados de forma segura 
    en una tabla de Oracle Database.
    """
    # 1. Hashear la contraseña con sal usando bcrypt
    password_bytes = password_plana.encode('utf-8')
    sal = bcrypt.gensalt()
    hash_seguro = bcrypt.hashpw(password_bytes, sal)
    
    # Decodificamos a string para poder guardarlo limpiamente en VARCHAR2 de Oracle
    hash_str = hash_seguro.decode('utf-8')
    
    # 2. Datos listos para tu sentencia SQL INSERT hacia Oracle
    datos_usuario = {
        "username": nombre_usuario,
        "password_hash": hash_str
    }
    
    print(f"[Oracle Ready] Usuario: {nombre_usuario}")
    print(f"[Oracle Ready] Hash a guardar en BD: {hash_str}")
    
    return datos_usuario

if __name__ == "__main__":
    # Prueba del generador de hash para Oracle
    usuario_prueba = "edu_admin"
    password_prueba = "ClaveSecretaInacap2026"
    
    registro = preparar_registro_usuario(usuario_prueba, password_prueba)
    
    # Ejemplo de la consulta SQL que usarías con tu conector de Oracle (oracledb):
    # sql = "INSERT INTO usuarios (username, password_hash) VALUES (:1, :2)"
    # cursor.execute(sql, (registro["username"], registro["password_hash"]))