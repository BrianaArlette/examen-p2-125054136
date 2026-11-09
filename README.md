# Examen Segundo Parcial — Pipeline DataMart

**Matrícula:** 125054136  
**Pregunta de negocio:** Top 10 productos por ingreso total durante 2025 (último dígito de matrícula: 6).  
**Cálculo:** ingreso por venta = cantidad × precio_unitario. Los importes se agrupan por producto y se ordenan de mayor a menor.  
**Tecnologías:** Docker Compose, Hadoop 3.3.6 en modo standalone, Hadoop Streaming, Python 3, PostgreSQL 16 y Flask.

## Descripción del pipeline

El archivo CSV contiene cinco millones de registros de ventas generados con la matrícula como semilla. El mapper obtiene el producto y calcula el ingreso de cada venta en centavos. Hadoop Streaming agrupa los registros por clave; el reducer suma los importes y produce los diez productos con mayor ingreso. Un script carga esos resultados en PostgreSQL y la API proporciona endpoints de consulta y escritura.

El monto se calcula en centavos enteros para evitar diferencias de precisión entre el procesamiento distribuido y el secuencial. Las filas vacías, el encabezado y los registros inválidos se omiten.

## Requisitos y configuración

El entorno de ejecución utiliza Windows con PowerShell, Python 3 y Docker Desktop. La construcción inicial requiere conexión a Internet para obtener las imágenes y los archivos de Hadoop. La configuración de la base de datos se define en `.env`, a partir de `.env.example`. El campo `POSTGRES_PASSWORD` debe contener una contraseña local antes de iniciar los servicios.

El CSV se genera en la carpeta `datos/` y se monta en el servicio Hadoop como volumen de solo lectura. No forma parte de la imagen Docker ni del repositorio Git.

## Reproducción del entorno

Desde la raíz del proyecto, el proceso comprende la configuración local, la generación del CSV y la creación de los tres servicios:

```powershell
Copy-Item .env.example .env
notepad .env
python .\scripts\prueba_local.py
python .\generar_dataset.py 125054136
Get-Item .\datos\ventas_125054136.csv | Select-Object Name,Length
docker compose up --build -d
docker compose ps
```

La primera construcción descarga Hadoop. El archivo se genera a partir de la semilla de nueve dígitos y permanece fuera del repositorio.

## Parte A. Infraestructura y Parte B. SSH

Los tres servicios (`hadoop`, `db` y `api`) comparten la red `datamart_red`. PostgreSQL conserva sus registros en el volumen nombrado `pgdata`. La API se conecta a PostgreSQL mediante el nombre de servicio `db`, y depende del estado saludable de la base de datos y del contenedor Hadoop.

Hadoop utiliza Debian, OpenJDK 17 y Python 3. El servicio SSH funciona con autenticación mediante llaves generadas en el arranque y almacenadas en el volumen `ssh_keys`, sin contraseñas incorporadas al Dockerfile.

Comandos de verificación:

```powershell
docker compose exec hadoop hadoop version
docker compose exec -u alumno hadoop ssh localhost hostname
docker compose exec api ssh -i /ssh/id_ed25519 -o BatchMode=yes -o StrictHostKeyChecking=accept-new alumno@hadoop hostname
```

## Parte C. Hadoop Streaming y comparativa

El trabajo MapReduce y el proceso secuencial responden la misma pregunta. El tiempo de Hadoop se registra alrededor de la ejecución del job; el tiempo secuencial se obtiene con `time.perf_counter()`. La comparación comprueba producto, orden e importe exacto del top 10.

```powershell
docker compose exec hadoop bash /workspace/scripts/ejecutar_job.sh
python .\mapreduce\secuencial.py .\datos\ventas_125054136.csv .\salidas\secuencial.tsv
python .\scripts\comparar.py
python .\scripts\actualizar_readme.py
```

### Tiempos de ejecución

| Método | Tiempo medido (segundos) | Evidencia |
| --- | ---: | --- |
| Hadoop Streaming standalone | 99.956 s | `salidas/tiempo_hadoop.txt` |
| Python secuencial | 38.496 s | `salidas/tiempo_secuencial.txt` |
| Coincidencia de top 10 | Sí, los 10 productos y montos son idénticos | `salidas/comparacion.txt` |

**Análisis de rendimiento:** En un equipo único y con un archivo de aproximadamente 400 MB, Hadoop Streaming puede tardar más que Python secuencial debido al inicio de Java y la preparación y coordinación del trabajo MapReduce. La lectura directa tiene un costo inicial menor. Hadoop ofrece mayores ventajas cuando el volumen requiere procesamiento distribuido y los trabajos se reparten entre varios nodos. La comparación concreta se determina con los tiempos registrados durante la ejecución.

## Parte D. PostgreSQL y API

El archivo generado por Hadoop se carga desde `salidas/resultado/part-00000` a la tabla `resultados`. La tabla utiliza `producto` como clave primaria e `ingreso_total` como valor numérico con dos decimales.

```powershell
docker compose exec api python /app/scripts/cargar_resultados.py
Invoke-RestMethod http://localhost:5051/health
Invoke-RestMethod http://localhost:5051/resultados
$producto = (Invoke-RestMethod http://localhost:5051/resultados)[0].producto
Invoke-RestMethod "http://localhost:5051/resultados/$producto"
```

Los endpoints disponibles son `GET /resultados`, `GET /resultados/<producto>`, `POST /resultados` y `DELETE /resultados/<producto>`. El endpoint POST inserta o actualiza un importe para un producto.

Verificación de escritura y eliminación:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:5051/resultados -ContentType 'application/json' -Body '{"producto":"PRUEBA-0001","ingreso_total":"100.50"}'
Invoke-RestMethod http://localhost:5051/resultados/PRUEBA-0001
Invoke-RestMethod -Method Delete http://localhost:5051/resultados/PRUEBA-0001
```

### Persistencia

El volumen nombrado `pgdata` mantiene la información después de eliminar y crear nuevamente los contenedores:

```powershell
docker compose down
docker compose up -d
Invoke-RestMethod http://localhost:5051/resultados
docker compose exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT COUNT(*) FROM resultados;"'
```

El comando `docker compose down -v`, a diferencia de `down`, elimina también los volúmenes nombrados del proyecto y, por tanto, los datos persistidos de PostgreSQL.

## Evidencias

Las capturas de las pruebas de Docker, Hadoop, SSH, MapReduce, PostgreSQL y la API se encuentran en el siguiente documento:

[Ver evidencias de ejecución](evidencias/evidencias.pdf)

Las respuestas teóricas se encuentran en [TEORIA.md](TEORIA.md).

## Estructura del repositorio

```text
examen-p2-125054136/
├── README.md
├── TEORIA.md
├── .gitignore
├── .dockerignore
├── .env.example
├── docker-compose.yml
├── generar_dataset.py
├── hadoop/
│   ├── Dockerfile
│   └── entrypoint.sh
├── mapreduce/
│   ├── mapper.py
│   ├── reducer.py
│   └── secuencial.py
├── api/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
├── scripts/
│   ├── ejecutar_job.sh
│   ├── cargar_resultados.py
│   ├── comparar.py
│   ├── actualizar_readme.py
│   └── prueba_local.py
├── datos/
├── salidas/
└── evidencias/
```

Los archivos `*.csv`, `.env`, `__pycache__/`, las llaves privadas y los resultados temporales se encuentran excluidos mediante `.gitignore`.

## Referencias

- [Apache Hadoop Streaming 3.3.6](https://hadoop.apache.org/docs/r3.3.6/hadoop-streaming/HadoopStreaming.html)
- [Docker Compose: orden de inicio y dependencias](https://docs.docker.com/compose/how-tos/startup-order/)
- [Documentación de Flask](https://flask.palletsprojects.com/)
- [Documentación de PostgreSQL](https://www.postgresql.org/docs/)
