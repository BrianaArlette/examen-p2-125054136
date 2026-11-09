#!/usr/bin/env python3
"""Reduce: suma por producto y obtiene el top 10 global (1 solo reducer)."""
import sys
from collections import defaultdict


def dinero(centavos):
    return f'{centavos // 100}.{centavos % 100:02d}'


def calcular_top10(lineas):
    totales = defaultdict(int)
    for linea in lineas:
        try:
            producto, monto = linea.rstrip('\n').split('\t', 1)
            if producto:
                totales[producto] += int(monto)
        except (ValueError, TypeError):
            continue
    return sorted(totales.items(), key=lambda p: (-p[1], p[0]))[:10]


def main():
    for producto, total_centavos in calcular_top10(sys.stdin):
        print(f'{producto}\t{dinero(total_centavos)}')


if __name__ == '__main__':
    main()
