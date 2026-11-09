#!/usr/bin/env python3
"""Map: venta CSV -> producto TAB ingreso_en_centavos. Ignora registros inválidos."""
import csv
import sys
from decimal import Decimal, InvalidOperation


def parsear_venta(linea):
    try:
        fila = next(csv.reader([linea]))
        if len(fila) != 8 or fila[0].strip().lower() == 'id':
            return None
        producto = fila[4].strip()
        cantidad = int(fila[5])
        precio = Decimal(fila[6])
        centavos_precio = precio * 100
        if (not producto or cantidad < 0 or precio < 0 or
                not precio.is_finite() or
                centavos_precio != centavos_precio.to_integral_value()):
            return None
        return producto, cantidad * int(centavos_precio)
    except (ValueError, InvalidOperation, csv.Error, StopIteration, IndexError):
        return None


def main():
    for linea in sys.stdin:
        dato = parsear_venta(linea)
        if dato is not None:
            producto, ingreso_centavos = dato
            print(f'{producto}\t{ingreso_centavos}')


if __name__ == '__main__':
    main()
