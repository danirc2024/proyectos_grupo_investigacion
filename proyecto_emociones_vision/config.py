
# ---------------------------------------------------------------------------
# Parámetros del tracker de centroides
# ---------------------------------------------------------------------------
MAX_DISAPPEARED: int = 15

MAX_DISTANCE: float = 0.15
# ---------------------------------------------------------------------------
# Parámetros del clasificador de emociones (DeepFace)
# ---------------------------------------------------------------------------
THROTTLE_SECONDS: float = 1.0

CONFIDENCE_THRESHOLD: float = 0.50

# ---------------------------------------------------------------------------
# Parámetros de MediaPipe FaceLandmarker
# ---------------------------------------------------------------------------
NUM_FACES: int = 5

MODEL_FILENAME: str = "face_landmarker.task"

# ---------------------------------------------------------------------------
# Parámetros del bucle de video
# ---------------------------------------------------------------------------
LOOP_DELAY_SECONDS: float = 0.015

PAD_RATIO: float = 0.10
# ---------------------------------------------------------------------------
# Mapeo de emociones (inglés DeepFace → español)
# ---------------------------------------------------------------------------
EMOTION_MAPPING: dict[str, str] = {
    "happy":    "Feliz",
    "surprise": "Sorprendido",
    "angry":    "Enojado",
    "sad":      "Triste",
    "fear":     "Miedo",
    "disgust":  "Asco",
    "neutral":  "Aburrido",
}

# Lista canónica de las 7 emociones en español (orden de inserción del dict).
EMOTION_LABELS: list[str] = list(EMOTION_MAPPING.values())

# Contadores iniciales vacíos para session_state.
INITIAL_COUNTS: dict[str, int] = {emocion: 0 for emocion in EMOTION_LABELS}

# ---------------------------------------------------------------------------
# Paleta de colores para el gráfico de Plotly (hex)
# ---------------------------------------------------------------------------
COLORS_HEX: dict[str, str] = {
    "Feliz":       "#00E676",  # Verde neón
    "Sorprendido": "#00E5FF",  # Celeste neón
    "Enojado":     "#FF1744",  # Rojo neón
    "Triste":      "#2979FF",  # Azul neón
    "Miedo":       "#FF9100",  # Naranja neón
    "Asco":        "#8D6E63",  # Marrón
    "Aburrido":    "#90A4AE",  # Gris pizarra
}

# ---------------------------------------------------------------------------
# Paleta de colores para dibujo en frame con OpenCV (BGR)
# ---------------------------------------------------------------------------
COLORS_BGR: dict[str, tuple[int, int, int]] = {
    "Feliz":       (100, 230,   0),  # Verde neón
    "Sorprendido": (255, 229,   0),  # Celeste neón
    "Enojado":     ( 68,  23, 255),  # Rojo neón
    "Triste":      (255, 100,   0),  # Azul neón
    "Miedo":       (  0, 145, 255),  # Naranja neón
    "Asco":        ( 30, 105,  30),  # Verde oliva
    "Aburrido":    (174, 164, 144),  # Gris pizarra
}

# ---------------------------------------------------------------------------
# Orden de categorías en el eje Y del gráfico de Plotly
# ---------------------------------------------------------------------------
CHART_CATEGORY_ORDER: list[str] = [
    "Aburrido", "Asco", "Miedo", "Triste", "Enojado", "Sorprendido", "Feliz"
]
