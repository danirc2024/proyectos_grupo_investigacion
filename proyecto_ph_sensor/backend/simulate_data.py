"""
Simula datos de pH y temperatura SIN necesidad de tener el ESP32 conectado.
Sirve para probar el backend y el dashboard mientras no tengas el hardware
a mano, o para practicar antes de la demo con el sensor real.

Uso:
    python simulate_data.py
"""

import random
import time
import requests

BACKEND_URL = "http://localhost:5000/api/lectura"

# Empezamos con un pH "normal" y lo vamos moviendo un poco cada vez,
# como si alguien le fuera echando sal/limón/tierra de a poco.
ph_actual = 7.0

print("Enviando datos simulados cada 3 segundos (Ctrl+C para detener)...")

while True:
    try:
        # pequeña variación aleatoria para simular el sensor "moviéndose"
        ph_actual += random.uniform(-0.3, 0.3)
        ph_actual = max(2.0, min(12.0, ph_actual))  # limitar rango realista

        temp_simulada = round(random.uniform(20.0, 23.0), 2)

        r = requests.post(
            BACKEND_URL,
            json={"ph": round(ph_actual, 2), "temperatura": temp_simulada},
            timeout=3,
        )
        print(f"Enviado: pH={ph_actual:.2f} temp={temp_simulada} | respuesta {r.status_code}")

    except Exception as e:
        print("Error enviando dato (¿está corriendo app.py?):", e)

    time.sleep(3)