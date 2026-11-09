"""Prueba breve sin Docker para confirmar mapper, reducer y cálculos."""
import io
import subprocess
import sys
from pathlib import Path

carpeta = Path(__file__).resolve().parents[1] / 'mapreduce'
entrada = """id,fecha_hora,tienda,categoria,producto,cantidad,precio_unitario,metodo_pago
1,2025-01-01 00:00:00,T001,Electronica,ELE-0001,2,10.25,Tarjeta
2,2025-01-01 00:00:01,T002,Electronica,ELE-0001,1,5.10,Efectivo
3,2025-01-01 00:00:02,T002,Ropa,ROP-0001,3,12.50,Efectivo
malformada
"""
mapa = subprocess.run([sys.executable, str(carpeta / 'mapper.py')],
    input=entrada, text=True, capture_output=True, check=True).stdout
assert mapa.splitlines() == ['ELE-0001\t2050', 'ELE-0001\t510', 'ROP-0001\t3750'], mapa
reduce = subprocess.run([sys.executable, str(carpeta / 'reducer.py')],
    input=mapa, text=True, capture_output=True, check=True).stdout
assert reduce.splitlines() == ['ROP-0001\t37.50', 'ELE-0001\t25.60'], reduce
print('Prueba local correcta: encabezado, fila inválida, montos exactos y orden por ingreso.')
