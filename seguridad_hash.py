import bcrypt

def preparar_registro_usuario(nombre_usuario, password_plana):
    """
    Prepara los datos de un usuario para ser insertados de forma segura 
    en una tabla de Oracle Database.
    """
    password_bytes = password_plana.encode('utf-8')
    sal = bcrypt.gensalt()
    hash_seguro = bcrypt.hashpw(password_bytes, sal)

    hash_str = hash_seguro.decode('utf-8')
    
    datos_usuario = {
        "username": nombre_usuario,
        "password_hash": hash_str
    }
    
    print(f"[Oracle Ready] Usuario: {nombre_usuario}")
    print(f"[Oracle Ready] Hash a guardar en BD: {hash_str}")
    
    return datos_usuario

if __name__ == "__main__":
    usuario_prueba = "edu_admin"
    password_prueba = "ClaveSecretaInacap2026"
    
    registro = preparar_registro_usuario(usuario_prueba, password_prueba)