import os
import sys
import time
import cv2
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Asegurar que se pueda importar los módulos locales desde el mismo directorio
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from centroid_tracker import CentroidTracker
from emotion_classifier import EmotionClassifier

# Configuración de página de Streamlit
st.set_page_config(
    page_title="Detector de Emociones del Público",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS personalizado para mejorar la estética
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    h1 {
        font-family: 'Outfit', 'Inter', sans-serif;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(45deg, #FF5252, #FFD740, #69F0AE, #40C4FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    h2, h3, h4 {
        font-family: 'Outfit', 'Inter', sans-serif;
        font-weight: 600;
    }
    .metric-card {
        background-color: #1e293b;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: bold;
        color: #60a5fa;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #94a3b8;
    }
    .event-log {
        background-color: #0f172a;
        border-left: 4px solid #10b981;
        padding: 8px 12px;
        border-radius: 4px;
        margin-top: 10px;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializar estados de la sesión de Streamlit
if 'counts' not in st.session_state:
    st.session_state.counts = {
        'Feliz': 0, 
        'Sorprendido': 0, 
        'Enojado': 0, 
        'Triste': 0, 
        'Miedo': 0, 
        'Asco': 0, 
        'Aburrido': 0
    }
if 'tracker' not in st.session_state:
    # max_disappeared=15 frames (aprox 1-2 segundos)
    st.session_state.tracker = CentroidTracker(max_disappeared=15, max_distance=0.15)
if 'classifier' not in st.session_state:
    st.session_state.classifier = EmotionClassifier(throttle_seconds=1.0)
if 'event_log' not in st.session_state:
    st.session_state.event_log = []
if 'running' not in st.session_state:
    st.session_state.running = False

# Sidebar de Configuración e Información
st.sidebar.title("🛠️ Configuración")
st.sidebar.markdown("---")
st.sidebar.markdown("### Info de Modelos")
st.sidebar.info(
    "Este sistema utiliza **MediaPipe FaceMesh** para el seguimiento ultra rápido de rostros "
    "y **DeepFace** para clasificar la emoción del rostro en 7 categorías en intervalos controlados."
)

st.sidebar.markdown("### Umbral de Throttling")
throttle_val = st.sidebar.slider(
    "Clasificación cada (segundos):", 
    min_value=0.2, 
    max_value=3.0, 
    value=1.0, 
    step=0.1,
    help="Define cada cuántos segundos se ejecuta DeepFace sobre una misma persona. A menor tiempo, más precisión pero mayor lag de video."
)
# Sincronizar el slider con el clasificador
st.session_state.classifier.throttle_seconds = throttle_val

st.sidebar.markdown("---")
st.sidebar.markdown("**Estado del Sistema:**")
if st.session_state.running:
    st.sidebar.success("Cámara Activa 🟢")
else:
    st.sidebar.warning("Cámara Detenida 🔴")

# Título de la aplicación
st.markdown("<h1>🎭 Detector de Emociones del Público en Tiempo Real</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size:1.1rem; color: #94a3b8;'>Detección y clasificación de emociones híbrida (MediaPipe + DeepFace) con seguimiento único para evitar conteo repetido.</p>", unsafe_allow_html=True)

# Configurar rutas del modelo de MediaPipe
MODEL_PATH = os.path.join(BASE_DIR, "face_landmarker.task")

if not os.path.exists(MODEL_PATH):
    st.error(f"No se encontró el modelo de MediaPipe en: {MODEL_PATH}")
    st.info("Descárgalo desde: https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task y colócalo en el directorio del proyecto.")
    st.stop()

# Controles en el Panel Principal
col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([1, 1, 2])

with col_ctrl1:
    if st.session_state.running:
        if st.button("🔴 Detener Cámara", use_container_width=True):
            st.session_state.running = False
            st.rerun()
    else:
        # Mostramos una alerta en el primer inicio por si DeepFace debe descargar sus pesos
        if st.button("🟢 Iniciar Cámara", use_container_width=True):
            st.session_state.running = True
            st.toast("Cargando DeepFace... (La primera vez puede tardar unos segundos)", icon="🤖")
            st.rerun()

with col_ctrl2:
    if st.button("🔄 Reiniciar Estadísticas", use_container_width=True):
        st.session_state.counts = {
            'Feliz': 0, 'Sorprendido': 0, 'Enojado': 0, 
            'Triste': 0, 'Miedo': 0, 'Asco': 0, 'Aburrido': 0
        }
        st.session_state.tracker = CentroidTracker(max_disappeared=15, max_distance=0.15)
        st.session_state.event_log = ["Estadísticas reiniciadas."]
        st.toast("Contadores reiniciados con éxito", icon="🔄")
        st.rerun()

# Layout Principal
col1, col2 = st.columns([1.1, 0.9])

with col1:
    st.subheader("Cámara en Vivo")
    image_placeholder = st.empty()
    if not st.session_state.running:
        image_placeholder.info("Presiona 'Iniciar Cámara' para comenzar a transmitir.")

with col2:
    st.subheader("Estadísticas del Público")
    chart_placeholder = st.empty()
    
    # Tarjeta métrica del aforo total
    metric_placeholder = st.empty()
    
    # Registro de eventos recientes
    st.markdown("#### Historial de Eventos")
    log_placeholder = st.empty()

# Función para renderizar el gráfico de Plotly
def draw_chart():
    df = pd.DataFrame([
        {"Emoción": k, "Cantidad": v} for k, v in st.session_state.counts.items()
    ])
    
    # Colores personalizados hermosos para las 7 emociones
    colors_map = {
        'Feliz': '#00E676',       # Verde neón
        'Sorprendido': '#00E5FF',  # Celeste neón
        'Enojado': '#FF1744',      # Rojo neón
        'Triste': '#2979FF',       # Azul neón
        'Miedo': '#FF9100',        # Naranja neón
        'Asco': '#8D6E63',         # Marrón
        'Aburrido': '#90A4AE'      # Gris pizarra (Neutral)
    }
    
    fig = px.bar(
        df,
        y="Emoción",
        x="Cantidad",
        color="Emoción",
        orientation="h",
        color_discrete_map=colors_map,
        text="Cantidad",
    )
    
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=10, b=20),
        xaxis=dict(showgrid=True, gridcolor="#334155", title="Número de Personas"),
        yaxis=dict(
            title="", 
            categoryorder="array", 
            categoryarray=['Aburrido', 'Asco', 'Miedo', 'Triste', 'Enojado', 'Sorprendido', 'Feliz']
        ),
        showlegend=False,
        height=350,
        font=dict(family="Inter, sans-serif", size=13)
    )
    
    fig.update_traces(
        textposition="outside",
        cliponaxis=False,
        marker=dict(line=dict(width=1.5, color='#ffffff'))
    )
    
    chart_placeholder.plotly_chart(fig, use_container_width=True, key=f"chart_{time.time()}")

# Función para actualizar las métricas y logs en Streamlit
def update_metrics_and_logs():
    total_personas = sum(st.session_state.counts.values())
    metric_placeholder.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_personas}</div>
            <div class="metric-label">Personas Registradas en Total</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Mostrar los últimos 5 eventos
    recent_logs = st.session_state.event_log[-5:]
    log_content = ""
    if not recent_logs:
        log_content = "<p style='color:#64748b;'>No hay eventos registrados aún.</p>"
    else:
        for log in reversed(recent_logs):
            log_content += f'<div class="event-log">{log}</div>'
    
    log_placeholder.markdown(log_content, unsafe_allow_html=True)

# Renderizar el estado inicial del gráfico y las métricas
draw_chart()
update_metrics_and_logs()

# Bucle principal de procesamiento de cámara
if st.session_state.running:
    # 1. Configurar opciones del detector de MediaPipe
    base_options = python.BaseOptions(model_asset_buffer=open(MODEL_PATH, "rb").read())
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        output_face_blendshapes=False,  # Ya no usamos blendshapes manuales de MediaPipe
        num_faces=5
    )

    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        st.error("No se pudo acceder a la cámara web. Asegúrate de que no esté en uso por otra aplicación.")
        st.session_state.running = False
        st.rerun()

    # Usar el Administrador de Contexto para crear el detector
    with vision.FaceLandmarker.create_from_options(options) as detector:
        tracker = st.session_state.tracker
        classifier = st.session_state.classifier
        
        while cap.isOpened() and st.session_state.running:
            ret, frame = cap.read()
            if not ret:
                st.warning("No se pudo leer el cuadro de la cámara web.")
                break

            # Invertir el feed horizontalmente para efecto espejo natural
            frame = cv2.flip(frame, 1)
            alto, ancho, _ = frame.shape

            # Convertir a RGB ya que MediaPipe requiere RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_imagen = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

            # Obtener timestamp preciso en ms
            timestamp_ms = int(time.time() * 1000)

            # Detectar landmarks usando MediaPipe
            resultados = detector.detect_for_video(mp_imagen, timestamp_ms)

            current_centroids = []
            frame_faces_raw = []  # Datos crudos de los rostros en este frame

            if resultados.face_landmarks:
                for rostro_landmarks in resultados.face_landmarks:
                    # Calcular el centroide promedio del rostro
                    cx = sum(p.x for p in rostro_landmarks) / len(rostro_landmarks)
                    cy = sum(p.y for p in rostro_landmarks) / len(rostro_landmarks)
                    current_centroids.append((cx, cy))

                    # Guardar coordenadas de caja delimitadora
                    x_coords = [int(p.x * ancho) for p in rostro_landmarks]
                    y_coords = [int(p.y * alto) for p in rostro_landmarks]
                    xmin, xmax = max(0, min(x_coords)), min(ancho, max(x_coords))
                    ymin, ymax = max(0, min(y_coords)), min(alto, max(y_coords))

                    frame_faces_raw.append({
                        'centroid': (cx, cy),
                        'bbox': (xmin, ymin, xmax, ymax),
                        'landmarks': rostro_landmarks
                    })

            # Guardar el set de IDs actual antes de actualizar el tracker
            old_ids = set(tracker.objects.keys())
            
            # Actualizar el Tracker de Centroides
            tracker.update(current_centroids)
            
            # Buscar rostros eliminados/deregistrados para contar su emoción dominante final
            new_ids = set(tracker.objects.keys())
            removed_ids = old_ids - new_ids
            
            for r_id in removed_ids:
                if not tracker.counted_emotions.get(r_id, True):
                    history = tracker.emotions_history.get(r_id, [])
                    if history:
                        dominant_final = max(set(history), key=history.count)
                    else:
                        dominant_final = 'Aburrido'
                    
                    st.session_state.counts[dominant_final] += 1
                    tracker.counted_emotions[r_id] = True
                    t_str = time.strftime('%H:%M:%S')
                    st.session_state.event_log.append(f"[{t_str}] Persona #{r_id} se retiró. Clasificación final: {dominant_final}")
                    draw_chart()
                    update_metrics_and_logs()

            # Clasificar y estructurar los rostros procesados
            frame_faces_data = []

            for face_raw in frame_faces_raw:
                cx, cy = face_raw['centroid']
                xmin, ymin, xmax, ymax = face_raw['bbox']

                # Encontrar el ID correspondiente buscando el centroide más cercano
                face_id = None
                min_dist = float('inf')
                for obj_id, obj_centroid in tracker.objects.items():
                    dist = np.sqrt((cx - obj_centroid[0])**2 + (cy - obj_centroid[1])**2)
                    if dist < min_dist:
                        min_dist = dist
                        face_id = obj_id

                # Validar que coincida con un ID activo a distancia corta
                if face_id is not None and min_dist <= tracker.max_distance:
                    # Recortar el rostro del frame original (en formato BGR ya que DeepFace espera BGR)
                    # Añadimos un pequeño margen para mejorar la detección de DeepFace
                    pad_x = int((xmax - xmin) * 0.1)
                    pad_y = int((ymax - ymin) * 0.1)
                    crop_xmin = max(0, xmin - pad_x)
                    crop_ymin = max(0, ymin - pad_y)
                    crop_xmax = min(ancho, xmax + pad_x)
                    crop_ymax = min(alto, ymax + pad_y)

                    face_crop = frame[crop_ymin:crop_ymax, crop_xmin:crop_xmax]
                    
                    # Clasificar con DeepFace (usando caching interno para evitar lentitud)
                    emotion, confidence = classifier.classify_face_crop(face_crop, face_id)

                    frame_faces_data.append({
                        'face_id': face_id,
                        'bbox': (xmin, ymin, xmax, ymax),
                        'landmarks': face_raw['landmarks'],
                        'emotion': emotion,
                        'confidence': confidence
                    })

            # Dibujar los rostros y procesar conteo inmediato
            for face_data in frame_faces_data:
                face_id = face_data['face_id']
                xmin, ymin, xmax, ymax = face_data['bbox']
                emotion = face_data['emotion']
                confidence = face_data['confidence']

                # Registrar la emoción actual en el historial de este rostro
                tracker.emotions_history[face_id].append(emotion)
                
                # Si aún no ha sido contabilizado y muestra una emoción clara (distinta de Aburrido/Neutral)
                if not tracker.counted_emotions[face_id]:
                    # Umbral de confianza del 50% para activar el conteo rápido de emoción expresada
                    if emotion != 'Aburrido' and confidence > 0.50:
                        st.session_state.counts[emotion] += 1
                        tracker.counted_emotions[face_id] = True
                        t_str = time.strftime('%H:%M:%S')
                        st.session_state.event_log.append(f"[{t_str}] ¡Persona #{face_id} expresó {emotion} ({int(confidence*100)}%)!")
                        draw_chart()
                        update_metrics_and_logs()

                # Elegir color del cuadro dependiendo de la emoción (OpenCV usa BGR)
                colors_bgr = {
                    'Feliz': (100, 230, 0),       # Verde neón
                    'Sorprendido': (255, 229, 0),  # Celeste neón
                    'Enojado': (68, 23, 255),      # Rojo neón
                    'Triste': (255, 100, 0),       # Azul neón
                    'Miedo': (0, 145, 255),        # Naranja neón
                    'Asco': (30, 105, 30),         # Verde oliva
                    'Aburrido': (174, 164, 144)    # Gris pizarra
                }
                draw_color = colors_bgr.get(emotion, (0, 255, 0))

                # Dibujar caja delimitadora y el ID con la emoción en el frame
                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), draw_color, 2)
                
                # Dibujar landmarks de MediaPipe
                for pt in face_data['landmarks']:
                    lx = int(pt.x * ancho)
                    ly = int(pt.y * alto)
                    cv2.circle(frame, (lx, ly), 1, draw_color, -1)

                # Agregar texto en pantalla
                lbl = f"ID {face_id}: {emotion} ({int(confidence*100)}%)"
                cv2.putText(frame, lbl, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, draw_color, 2)

            # Mostrar la imagen procesada en Streamlit convertida a RGB
            frame_disp = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_placeholder.image(frame_disp, channels="RGB", use_container_width=True)

            # Pequeño delay de control del loop
            time.sleep(0.015)

        cap.release()
