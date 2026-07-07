"""
Dashboard del proyecto "Sensor pH - Agua".
Consulta el backend Flask cada pocos segundos y muestra:
 - Valor actual de pH y temperatura
 - Semáforo visual (verde / amarillo / rojo) según el pH
 - Gráfico histórico en tiempo real

Ejecutar:
    pip install -r requirements.txt
    streamlit run streamlit_app.py
"""

import streamlit as st
import requests
import pandas as pd
import time

BACKEND_URL = "http://localhost:5000"
REFRESCO_SEGUNDOS = 2

PH_MIN_SEGURO = 6.5
PH_MAX_SEGURO = 8.5
PH_MIN_MARGINAL = 5.5
PH_MAX_MARGINAL = 9.5

st.set_page_config(page_title="Sensor de pH - Dashboard", layout="wide")


def clasificar_ph(ph: float):
    if PH_MIN_SEGURO <= ph <= PH_MAX_SEGURO:
        return "SEGURA", "#2ecc71"
    elif PH_MIN_MARGINAL <= ph <= PH_MAX_MARGINAL:
        return "MARGINAL", "#f1c40f"
    else:
        return "CONTAMINADA", "#e74c3c"


def obtener_lecturas(limite=100):
    try:
        r = requests.get(f"{BACKEND_URL}/api/lecturas", params={"limite": limite}, timeout=3)
        r.raise_for_status()
        return pd.DataFrame(r.json())
    except Exception:
        return pd.DataFrame(columns=["ph", "temperatura", "timestamp"])


st.title("💧 Dashboard - Monitoreo de pH del agua")
st.caption("Prueba en vivo: agrega sal, tierra o limón al agua y observa el cambio")

placeholder = st.empty()

while True:
    df = obtener_lecturas()

    with placeholder.container():
        if df.empty:
            st.warning("Esperando datos del ESP32... revisa que serial_reader.py esté corriendo.")
        else:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            ultima = df.iloc[-1]
            estado, color = clasificar_ph(ultima["ph"])

            col1, col2, col3 = st.columns([1, 1, 1.3])

            with col1:
                st.metric("pH actual", f"{ultima['ph']:.2f}")

            with col2:
                st.metric("Temperatura", f"{ultima['temperatura']:.1f} °C")

            with col3:
                st.markdown(
                    f"""
                    <div style="background-color:{color};
                                padding:18px; border-radius:12px;
                                text-align:center; color:white;
                                font-size:22px; font-weight:bold;">
                        AGUA {estado}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("### Historial de pH")
            st.line_chart(df.set_index("timestamp")["ph"])

            st.markdown("### Historial de temperatura")
            st.line_chart(df.set_index("timestamp")["temperatura"])

            with st.expander("Ver datos crudos"):
                st.dataframe(df.tail(20), use_container_width=True)

    time.sleep(REFRESCO_SEGUNDOS)