"""
Lee los datos que el ESP32 imprime por USB (Monitor Serial) y los reenvía
al backend Flask. NO requiere WiFi ni configurar ninguna IP: solo el cable
USB que ya están usando.

El ESP32 (con el código original de tu compañera, SIN modificar) imprime:
    Soil PH: 7.1
    Temperatura: 21.81 °C

Este script "escucha" ese mismo puerto y cada vez que junta un par
(pH + temperatura) lo manda al backend.

Uso:
    pip install -r requirements.txt
    python serial_reader.py

Si no sabes qué puerto usar, corre primero:
    python serial_reader.py --listar
"""

import argparse
import re
import time
import requests
import serial
import serial.tools.list_ports

BACKEND_URL = "http://localhost:5000/api/lectura"
BAUDRATE = 9600  # debe coincidir con Serial.begin(9600) del ESP32


def listar_puertos():
    puertos = serial.tools.list_ports.comports()
    if not puertos:
        print("No se encontraron puertos seriales conectados.")
        return
    print("Puertos disponibles:")
    for p in puertos:
        print(f"  {p.device}  -  {p.description}")


def leer_y_enviar(puerto: str):
    ph_actual = None
    temp_actual = None

    print(f"Conectando a {puerto} @ {BAUDRATE} baudios...")
    with serial.Serial(puerto, BAUDRATE, timeout=2) as ser:
        print("Conectado. Esperando datos del ESP32 (Ctrl+C para salir)...")
        while True:
            try:
                linea = ser.readline().decode("utf-8", errors="ignore").strip()
                if not linea:
                    continue

                print("Serial ->", linea)

                match_ph = re.search(r"Soil PH:\s*([\d.]+)", linea)
                match_temp = re.search(r"Temperatura:\s*([\d.]+)", linea)

                if match_ph:
                    ph_actual = float(match_ph.group(1))
                if match_temp:
                    temp_actual = float(match_temp.group(1))

                if ph_actual is not None and temp_actual is not None:
                    enviar_al_backend(ph_actual, temp_actual)
                    ph_actual, temp_actual = None, None

            except KeyboardInterrupt:
                print("\nDeteniendo lectura serial.")
                break
            except Exception as e:
                print("Error leyendo serial:", e)
                time.sleep(1)


def enviar_al_backend(ph: float, temp: float):
    try:
        r = requests.post(
            BACKEND_URL,
            json={"ph": ph, "temperatura": temp},
            timeout=3,
        )
        print(f"  -> Enviado al dashboard: pH={ph} temp={temp} | respuesta {r.status_code}")
    except Exception as e:
        print("  -> No se pudo enviar al backend:", e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--puerto", help="Ej: COM3 (Windows) o /dev/ttyUSB0 (Linux/Mac)")
    parser.add_argument("--listar", action="store_true", help="Muestra los puertos disponibles y sale")
    args = parser.parse_args()

    if args.listar:
        listar_puertos()
    elif args.puerto:
        leer_y_enviar(args.puerto)
    else:
        print("Falta indicar el puerto. Ejemplo:\n")
        print("  python serial_reader.py --listar        (para ver los puertos)")
        print("  python serial_reader.py --puerto COM3   (para empezar a leer)")