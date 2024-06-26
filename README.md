﻿#  Celis Test
## Andrés Fernando Aranguren Silva
- --
## Objetivo
Desarrollar un microservicio en Python que interactúe con un Datamart y proporcione una
interfaz para realizar consultas y operaciones específicas. Además, el microservicio deberá
integrar la autenticación con Firebase y tener un enfoque en pruebas unitarias y CI/CD.

## Solución
La idea básica fue hacer un microservicio usando FastAPI y los principios de APIRest para la elaboración de los endpoints, la arquitectura de la app se basa en en el siguiente diagrama:

![alt text](resources/arquitectura.png)

Donde para poder utilizar las vistas contenidas en controlador, para poder consultar la información dentro de los Parquet files se debe obtener un token de sesión válido que pertenezca a un usuario registrado en la base de datos de Firebase y debe ser enviado en la para cada petición deseada.

- --
## Instrucciones de ejecución

1. Se debe clonar el repositorio:

        git clone https://github.com/afarangurens/CelistEntrevista.git
        cd CelistEntrevista

2. Se debe tener el daemon de Docker corriendo para poder correr el contenedor utilizando el docker compose:

        docker-compose up --build

Y listo, ya está lista la aplicación para correr peticiones.

- --

## Flujo de la API:

1. Para poder realizar cualquier consulta es necesario primero contar con un token de 'sesion' JWT, para ello hay que realizar una petición curl con el email y el usuario:

        curl -X 'POST' \
            'http://127.0.0.1:8000/get_token' \
            -H 'accept: application/json' \
            -H 'Content-Type: application/json' \
            -d '{
                "email": "test@testing.com",
                "password": "ola12345"
            }'

    esto retornará un json con el token (En un entorno real este token se guarda en el cliente y por cada petición se envía en el header pero para este ejercicio al ser una API lo retorno como un json).

2. Una vez se tiene un token valido es momento de realizar las consultas. Para el caso de este ejercicio se pueden realizar 6 consultas, ventas en un periodo por empleado (KeyEmployee), ventas en un periodo por producto (KeyProduct) y ventas en un periodo por tienda (KeyStore), esto se puede hacer con el siguiente comando, donde start_date es la fecha inicial en formato "AAAA-MM-DD" y end_date la fecha final en el mismo formato. key_type se refiere al tipo de columna por la que se quiere consultar, (KeyProduct), (KeyEmployee), o (KeyStore)

        curl -X 'GET' \
            'http://127.0.0.1:8000/query_data/data_chunk000000000000.snappy.parquet?start_date=2023-01-01&end_date=2023-12-31&key_type=KeyProduct&cummulative=false' \
            -H 'accept: application/json' \
            -H 'Authorization: Bearer [TOKEN]'

3. También se puede ejecutar la consulta entre las ventas acumuladas entre dos fechas por cada tienda, producto o empleado:

        curl -X 'GET' \
            'http://127.0.0.1:8000/query_data/data_chunk000000000000.snappy.parquet?start_date=2023-01-01&end_date=2023-12-31&key_type=KeyProduct&cummulative=true' \
            -H 'accept: application/json' \
            -H 'Authorization: Bearer [TOKEN]'

- --
## Documentación

Con la aplicación corriendo, esta puede ser consultada en el siguiente enlace:

      http://127.0.0.1:8000/admin/docs
