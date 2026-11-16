CREATE TABLE farmacia_turno (
    local_id VARCHAR(20) PRIMARY KEY,
    local_nombre VARCHAR(150) NOT NULL,
    comuna_nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(250) NOT NULL,
    hora_apertura VARCHAR(20),
    hora_cierre VARCHAR(20),
    telefono VARCHAR(50),
    obtenido_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);