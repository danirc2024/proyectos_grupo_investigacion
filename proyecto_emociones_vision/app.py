import os
import sys
import logging
import warnings

import streamlit as st

# Reducir ruido de logs de librerías externas sin ocultar errores reales.
os.environ.setdefault("GLOG_minloglevel", "2")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("ABSL_LOGGING_LEVEL", "3")
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

logging.getLogger("streamlit").setLevel(logging.ERROR)
logging.getLogger("streamlit.runtime").setLevel(logging.ERROR)
logging.getLogger("absl").setLevel(logging.ERROR)
logging.getLogger("tensorflow").setLevel(logging.ERROR)
logging.getLogger("mediapipe").setLevel(logging.ERROR)
logging.getLogger("google").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)

# Asegurar que los módulos locales sean importables
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

import config
from styles import CSS
from centroid_tracker import CentroidTracker
from emotion_classifier import EmotionClassifier
from video_processor import procesar_video
from ui_components import render_chart, render_metric_card, render_event_log


# Configuración de página y estilos
st.set_page_config(
    page_title="Detector de Emociones del Público",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CSS, unsafe_allow_html=True)

# Verificar existencia del modelo de MediaPipe
MODEL_PATH = os.path.join(BASE_DIR, config.MODEL_FILENAME)
if not os.path.exists(MODEL_PATH):
    st.error(f"No se encontró el modelo de MediaPipe en: {MODEL_PATH}")
    st.info(
        "Descárgalo desde: https://storage.googleapis.com/mediapipe-models/"
        "face_landmarker/face_landmarker/float16/latest/face_landmarker.task "
        "y colócalo en el directorio del proyecto."
    )
    st.stop()

# Inicialización del estado de sesión
if "counts" not in st.session_state:
    st.session_state.counts = dict(config.INITIAL_COUNTS)

if "tracker" not in st.session_state:
    st.session_state.tracker = CentroidTracker(
        max_disappeared=config.MAX_DISAPPEARED,
        max_distance=config.MAX_DISTANCE,
    )

if "classifier" not in st.session_state:
    st.session_state.classifier = EmotionClassifier()

if "event_log" not in st.session_state:
    st.session_state.event_log = []

if "running" not in st.session_state:
    st.session_state.running = False

# Sidebar — solo controles esenciales
st.sidebar.title("🛠️ Controles")
st.sidebar.markdown("---")

# Estado de la cámara
if st.session_state.running:
    st.sidebar.success("Cámara Activa 🟢")
else:
    st.sidebar.warning("Cámara Detenida 🔴")

st.sidebar.markdown("---")

# Botones de control
if st.session_state.running:
    if st.sidebar.button("🔴 Detener Cámara", width="stretch"):
        st.session_state.running = False
        st.rerun()
else:
    if st.sidebar.button("🟢 Iniciar Cámara", width="stretch"):
        st.session_state.running = True
        st.toast("Cargando DeepFace… (La primera vez puede tardar unos segundos)", icon="🤖")
        st.rerun()

if st.sidebar.button("🔄 Reiniciar Estadísticas", width="stretch"):
    st.session_state.counts = dict(config.INITIAL_COUNTS)
    st.session_state.tracker = CentroidTracker(
        max_disappeared=config.MAX_DISAPPEARED,
        max_distance=config.MAX_DISTANCE,
    )
    st.session_state.classifier = EmotionClassifier()
    st.session_state.event_log = ["Estadísticas reiniciadas."]
    st.session_state.running = False
    st.toast("Contadores reiniciados con éxito", icon="🔄")
    st.rerun()

# Encabezado principal
st.markdown(
    "<h1>🎭 Detector de Emociones en Tiempo Real</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center; font-size:1.1rem; color:#94a3b8;'>"
    "Detección y clasificación de emociones híbrida (MediaPipe + DeepFace) ",
    unsafe_allow_html=True,
)

# Layout principal: columna de video | columna de estadísticas
col_video, col_stats = st.columns([1.1, 0.9])

with col_video:
    st.subheader("Cámara en Vivo")
    image_placeholder = st.empty()
    if not st.session_state.running:
        image_placeholder.info("Presiona 'Iniciar Cámara' para comenzar a transmitir.")

with col_stats:
    st.subheader("Estadísticas del Público")
    chart_placeholder = st.empty()
    metric_placeholder = st.empty()
    st.markdown("#### Historial de Eventos")
    log_placeholder = st.empty()

# Renderizado inicial (estado estático antes de iniciar la cámara)
render_chart(st.session_state.counts, chart_placeholder)
render_metric_card(st.session_state.counts, metric_placeholder)
render_event_log(st.session_state.event_log, log_placeholder)

# Bucle principal de orquestación
if st.session_state.running:
    # running_flag: lista mutable de un elemento para señalizar detención
    running_flag = [True]

    try:
        for frame_rgb, nuevos_eventos in procesar_video(
            tracker=st.session_state.tracker,
            classifier=st.session_state.classifier,
            counts=st.session_state.counts,
            model_path=MODEL_PATH,
            running_flag=running_flag,
        ):
            # Extender el log de eventos con los nuevos del frame
            if nuevos_eventos:
                st.session_state.event_log.extend(nuevos_eventos)
                render_chart(st.session_state.counts, chart_placeholder)
                render_metric_card(st.session_state.counts, metric_placeholder)
                render_event_log(st.session_state.event_log, log_placeholder)

            # Mostrar el frame procesado
            image_placeholder.image(frame_rgb, channels="RGB", width="stretch")

            # Verificar si el usuario pulsó "Detener" (session_state cambia entre reruns)
            if not st.session_state.running:
                running_flag[0] = False
                break

    except RuntimeError as exc:
        st.error(str(exc))
        st.session_state.running = False
        st.rerun()
