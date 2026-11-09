#!/bin/bash
# Configuración del procesamiento Hadoop Streaming
set -euo pipefail
cd /tmp
MATRICULA=125054136
ENTRADA="/data/input/ventas_${MATRICULA}.csv"
SALIDA="/data/output/resultado"
if [ ! -f "$ENTRADA" ]; then
    echo "ERROR: falta el dataset: $ENTRADA" >&2
    exit 1
fi
mkdir -p /data/output
rm -rf "$SALIDA"
INICIO=$(date +%s%N)
STREAMING_JAR="$HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-${HADOOP_VERSION}.jar"
hadoop jar "$STREAMING_JAR" \
  -D mapreduce.framework.name=local \
  -D fs.defaultFS=file:/// \
  -D mapreduce.job.reduces=1 \
  -input "file://${ENTRADA}" \
  -output "file://${SALIDA}" \
  -mapper 'python3 mapper.py' \
  -reducer 'python3 reducer.py' \
  -file /workspace/mapreduce/mapper.py \
  -file /workspace/mapreduce/reducer.py
FIN=$(date +%s%N)
SEGUNDOS=$(awk -v a="$INICIO" -v b="$FIN" 'BEGIN {printf "%.3f", (b-a)/1000000000}')
printf 'hadoop_segundos=%s\n' "$SEGUNDOS" > /data/output/tiempo_hadoop.txt
printf '\nTIEMPO HADOOP STREAMING: %s segundos\n' "$SEGUNDOS"
printf 'RESULTADO (TOP 10):\n'
cat "$SALIDA"/part-*
