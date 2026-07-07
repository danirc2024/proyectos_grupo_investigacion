"""
Backend simple para el proyecto de sensor de pH.
Recibe lecturas (del serial_reader.py) y las guarda en SQLite.
El dashboard de Streamlit consulta este servidor por HTTP GET.

Ejecutar:
    pip install -r requirements.txt
    python app.py

Quedará escuchando en http://0.0.0.0:5000
"""

from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "lecturas.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS lecturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ph REAL NOT NULL,
            temperatura REAL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.route("/api/lectura", methods=["POST"])
def recibir_lectura():
    data = request.get_json(force=True, silent=True)
    if not data or "ph" not in data:
        return jsonify({"error": "falta el campo 'ph'"}), 400

    ph = float(data["ph"])
    temperatura = float(data.get("temperatura", 0))
    timestamp = datetime.now().isoformat()

    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO lecturas (ph, temperatura, timestamp) VALUES (?, ?, ?)",
        (ph, temperatura, timestamp),
    )
    conn.commit()
    conn.close()

    return jsonify({"status": "ok", "ph": ph, "temperatura": temperatura})


@app.route("/api/lecturas", methods=["GET"])
def obtener_lecturas():
    """Devuelve las últimas N lecturas (por defecto 100) para el dashboard."""
    limite = int(request.args.get("limite", 100))

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    filas = conn.execute(
        "SELECT ph, temperatura, timestamp FROM lecturas ORDER BY id DESC LIMIT ?",
        (limite,),
    ).fetchall()
    conn.close()

    lecturas = [dict(f) for f in reversed(filas)]  # orden cronológico
    return jsonify(lecturas)


@app.route("/api/ultima", methods=["GET"])
def ultima_lectura():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    fila = conn.execute(
        "SELECT ph, temperatura, timestamp FROM lecturas ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()

    if fila is None:
        return jsonify({"error": "sin datos aún"}), 404
    return jsonify(dict(fila))


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)