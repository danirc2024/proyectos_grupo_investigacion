
# Parámetros del tracker de centroides
MAX_DISAPPEARED: int = 15

MAX_DISTANCE: float = 0.15
# Parámetros del clasificador de emociones (DeepFace)
THROTTLE_SECONDS: float = 1.0

CONFIDENCE_THRESHOLD: float = 0.50

# Parámetros de MediaPipe FaceLandmarker
NUM_FACES: int = 5

MODEL_FILENAME: str = "face_landmarker.task"

# Parámetros del bucle de video
LOOP_DELAY_SECONDS: float = 0.015

PAD_RATIO: float = 0.10
# Mapeo de emociones (inglés DeepFace → español)
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

# Paleta de colores para el gráfico de Plotly (hex)
COLORS_HEX: dict[str, str] = {
    "Feliz":       "#00E676",  
    "Sorprendido": "#00E5FF",  
    "Enojado":     "#FF1744",  
    "Triste":      "#2979FF",  
    "Miedo":       "#FF9100",  
    "Asco":        "#8D6E63",  
    "Aburrido":    "#90A4AE",  
}

# Paleta de colores para dibujo en frame con OpenCV 
COLORS_BGR: dict[str, tuple[int, int, int]] = {
    "Feliz":       (100, 230,   0),  
    "Sorprendido": (255, 229,   0),  
    "Enojado":     ( 68,  23, 255),  
    "Triste":      (255, 100,   0),  
    "Miedo":       (  0, 145, 255),  
    "Asco":        ( 30, 105,  30),  
    "Aburrido":    (174, 164, 144),  
}

# Orden de categorías en el eje Y del gráfico de Plotly
CHART_CATEGORY_ORDER: list[str] = [
    "Aburrido", "Asco", "Miedo", "Triste", "Enojado", "Sorprendido", "Feliz"
]
