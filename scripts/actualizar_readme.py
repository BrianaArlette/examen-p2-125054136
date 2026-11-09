"""Actualiza la comparativa del README con las mediciones registradas."""
from pathlib import Path
import re

base = Path(__file__).resolve().parents[1]
salida = base / 'salidas'

def leer_valor(ruta, nombre):
    if not ruta.is_file():
        raise SystemExit(f'Archivo de medición inexistente: {ruta}')
    for linea in ruta.read_text(encoding='utf-8').splitlines():
        if linea.startswith(nombre + '='):
            return linea.split('=', 1)[1]
    raise SystemExit(f'Falta {nombre} en {ruta}')

hadoop = leer_valor(salida/'tiempo_hadoop.txt', 'hadoop_segundos')
python = leer_valor(salida/'tiempo_secuencial.txt', 'secuencial_segundos')
comparacion = (salida/'comparacion.txt').read_text(encoding='utf-8').strip()
if not comparacion.startswith('COINCIDEN EXACTAMENTE'):
    raise SystemExit('Los resultados no coinciden. No se puede marcar la comparativa como válida.')

ruta = base/'README.md'
contenido = ruta.read_text(encoding='utf-8')
filas = [
    ('Hadoop Streaming standalone', f'{hadoop} s'),
    ('Python secuencial', f'{python} s'),
    ('Coincidencia de top 10', 'Sí, los 10 productos y montos son idénticos'),
]
for nombre, valor in filas:
    patron = r'(^\| ' + re.escape(nombre) + r' \| )[^\n|]+( \|)'
    contenido, cambios = re.subn(patron, lambda m: m.group(1) + valor + m.group(2),
                                contenido, count=1, flags=re.MULTILINE)
    if cambios != 1:
        raise SystemExit(f'No se encontró la fila de {nombre} en README.md')
ruta.write_text(contenido, encoding='utf-8')
print('Tabla de rendimiento actualizada en README.md.')
