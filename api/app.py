"""API Flask para resultados del top 10 por ingreso de DataMart."""
import os
from decimal import Decimal, InvalidOperation

import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, jsonify, request

app = Flask(__name__)


def conectar():
    return psycopg2.connect(
        host=os.environ.get('DB_HOST', 'db'),
        port=os.environ.get('DB_PORT', '5432'),
        dbname=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        connect_timeout=5,
    )


def inicializar_tabla():
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS resultados (
                    producto VARCHAR(64) PRIMARY KEY,
                    ingreso_total NUMERIC(20,2) NOT NULL CHECK (ingreso_total >= 0)
                )
            """)


def convertir(fila):
    return {'producto': fila['producto'], 'ingreso_total': str(fila['ingreso_total'])}


@app.get('/health')
def health():
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT 1')
    return jsonify({'estado': 'ok', 'servicio': 'datamart-api'})


@app.get('/resultados')
def todos():
    with conectar() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('SELECT producto, ingreso_total FROM resultados ORDER BY ingreso_total DESC, producto ASC')
            filas = cur.fetchall()
    return jsonify([convertir(fila) for fila in filas])


@app.get('/resultados/<producto>')
def por_producto(producto):
    with conectar() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('SELECT producto, ingreso_total FROM resultados WHERE producto = %s', (producto,))
            fila = cur.fetchone()
    if fila is None:
        return jsonify({'error': 'Producto no encontrado'}), 404
    return jsonify(convertir(fila))


@app.post('/resultados')
def crear_o_actualizar():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'Se espera JSON con producto e ingreso_total'}), 400
    producto = data.get('producto', '')
    if not isinstance(producto, str) or not producto.strip() or len(producto.strip()) > 64:
        return jsonify({'error': 'Producto inválido (1 a 64 caracteres)'}), 400
    try:
        monto = Decimal(str(data['ingreso_total']))
        if not monto.is_finite() or monto < 0 or monto != monto.quantize(Decimal('0.01')):
            raise ValueError
    except (KeyError, ValueError, TypeError, InvalidOperation):
        return jsonify({'error': 'ingreso_total debe ser número no negativo con máximo 2 decimales'}), 400
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO resultados (producto, ingreso_total) VALUES (%s, %s)
                ON CONFLICT (producto) DO UPDATE SET ingreso_total = EXCLUDED.ingreso_total
            """, (producto.strip(), monto))
    return jsonify({'producto': producto.strip(), 'ingreso_total': str(monto)}), 201


@app.delete('/resultados/<producto>')
def borrar(producto):
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM resultados WHERE producto = %s', (producto,))
            eliminados = cur.rowcount
    if eliminados == 0:
        return jsonify({'error': 'Producto no encontrado'}), 404
    return jsonify({'eliminado': producto})


if __name__ == '__main__':
    inicializar_tabla()
    app.run(host='0.0.0.0', port=5000, debug=False)
