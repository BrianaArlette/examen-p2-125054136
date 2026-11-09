"""Compara EXACTAMENTE los diez productos, orden e importes de ambas salidas."""
from pathlib import Path

carpeta = Path('salidas')
archivo_hadoop = carpeta / 'resultado' / 'part-00000'
archivo_python = carpeta / 'secuencial.tsv'
for archivo in (archivo_hadoop, archivo_python):
    if not archivo.is_file():
        raise SystemExit(f'No existe {archivo}')

hadoop = archivo_hadoop.read_text(encoding='utf-8').strip().splitlines()
python = archivo_python.read_text(encoding='utf-8').strip().splitlines()
iguales = hadoop == python and len(hadoop) == 10
mensaje = (
    'COINCIDEN EXACTAMENTE: los 10 productos, el orden y los ingresos.'
    if iguales else
    'NO COINCIDEN: resultado/part-00000 y secuencial.tsv.'
)
print(mensaje)
(carpeta / 'comparacion.txt').write_text(mensaje + '\n', encoding='utf-8')
if not iguales:
    for i, (a, b) in enumerate(zip(hadoop, python), 1):
        if a != b:
            print(f'Posición {i}: Hadoop={a!r}; Python={b!r}')
    raise SystemExit(1)
