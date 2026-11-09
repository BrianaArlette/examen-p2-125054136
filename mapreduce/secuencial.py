#!/usr/bin/env python3
"""Misma agregación sin Hadoop. Recibe CSV y ruta TSV de salida."""
import csv
import sys
import time
from collections import defaultdict
from pathlib import Path
from mapper import parsear_venta
from reducer import dinero


def ejecutar(ruta_csv, ruta_resultado):
    inicio = time.perf_counter()
    totales = defaultdict(int)
    registros_validos = 0
    with open(ruta_csv, 'r', encoding='utf-8', newline='') as archivo:
        for linea in archivo:
            dato = parsear_venta(linea)
            if dato is None:
                continue
            producto, centavos = dato
            totales[producto] += centavos
            registros_validos += 1
    top10 = sorted(totales.items(), key=lambda p: (-p[1], p[0]))[:10]
    ruta_resultado = Path(ruta_resultado)
    ruta_resultado.parent.mkdir(parents=True, exist_ok=True)
    with ruta_resultado.open('w', encoding='utf-8', newline='') as salida:
        for producto, centavos in top10:
            salida.write(f'{producto}\t{dinero(centavos)}\n')
    segundos = time.perf_counter() - inicio
    (ruta_resultado.parent / 'tiempo_secuencial.txt').write_text(
        f'secuencial_segundos={segundos:.3f}\nregistros_validos={registros_validos}\n', encoding='utf-8')
    print(f'Tiempo Python secuencial: {segundos:.3f} segundos')
    print(f'Registros válidos: {registros_validos}')
    print(f'Resultado: {ruta_resultado}')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit('Uso: python mapreduce/secuencial.py datos/ventas_125054136.csv salidas/secuencial.tsv')
    ejecutar(sys.argv[1], sys.argv[2])
