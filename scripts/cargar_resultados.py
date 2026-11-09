"""Lee resultado Hadoop y reemplaza la tabla de Postgres por el top 10."""
import os
from decimal import Decimal
from pathlib import Path

import psycopg2

RUTA = Path('/data/output/resultado/part-00000')


def main():
    if not RUTA.is_file():
        raise SystemExit(f'Archivo de resultado no disponible: {RUTA}')
    datos = []
    with RUTA.open(encoding='utf-8') as archivo:
        for numero_linea, linea in enumerate(archivo, 1):
            if not linea.strip():
                continue
            try:
                producto, importe = linea.strip().split('\t')
                datos.append((producto, Decimal(importe)))
            except (ValueError, ArithmeticError) as error:
                raise SystemExit(f'Línea inválida {numero_linea}: {linea!r}') from error
    if len(datos) != 10:
        raise SystemExit(f'Cantidad inesperada: {len(datos)} productos; se requieren 10.')
    with psycopg2.connect(
        host=os.environ['DB_HOST'], port=os.environ.get('DB_PORT', '5432'),
        dbname=os.environ['DB_NAME'], user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("""CREATE TABLE IF NOT EXISTS resultados (
                producto VARCHAR(64) PRIMARY KEY,
                ingreso_total NUMERIC(20,2) NOT NULL CHECK (ingreso_total >= 0))""")
            cur.execute('DELETE FROM resultados')
            cur.executemany("""
                INSERT INTO resultados (producto, ingreso_total) VALUES (%s, %s)
            """, datos)
    print(f'Cargados {len(datos)} productos en PostgreSQL (db).')


if __name__ == '__main__':
    main()
