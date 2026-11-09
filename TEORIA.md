# Parte E. Fundamentos teóricos

**1. Modos de Hadoop y uso de HDFS.**  
En standalone todo corre en una sola máquina como procesos locales, sin HDFS. En pseudo-distribuido los demonios funcionan en una sola máquina, simulando un clúster y normalmente usando HDFS. En totalmente distribuido los servicios se reparten entre varias máquinas y también se utiliza HDFS.

**2. Dataset como volumen, no COPY.**  
Un volumen evita agregar unos 400 MB a la imagen y permite cambiar el archivo sin volver a construirla. También mantiene separados los datos del código y facilita reutilizar la misma imagen con otro CSV. El montaje es de solo lectura para no modificar accidentalmente los datos de origen.

**3. docker compose down y down -v.**  
`docker compose down` elimina contenedores y la red creada, pero conserva los volúmenes nombrados; por eso PostgreSQL mantiene sus registros. `docker compose down -v` elimina además los volúmenes del proyecto, incluido el de PostgreSQL, y se pierde la información persistida ahí. El CSV y las salidas en carpetas locales no se borran.

**4. MapReduce frente a Python secuencial.**  
En un archivo de ~400 MB, Hadoop puede tardar más por arrancar Java, preparar tareas y gestionar el procesamiento. Una lectura secuencial simple tiene menor sobrecarga, especialmente en una sola máquina. MapReduce conviene más con archivos muy grandes, procesamiento distribuido en varios nodos o cálculos que se puedan paralelizar.

**5. CMD frente a ENTRYPOINT y COPY frente a ADD.**  
`CMD` define el comando o argumentos predeterminados, fáciles de sustituir al arrancar el contenedor; `ENTRYPOINT` define el ejecutable principal del contenedor. `COPY` solamente copia archivos al contexto de la imagen. `ADD` también permite funciones especiales, como extraer automáticamente archivos TAR locales, por lo que normalmente conviene preferir `COPY`.
