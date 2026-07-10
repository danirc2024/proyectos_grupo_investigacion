# Proyecto Emociones Vision - Detector de emociones en tiempo real

Aplicacion en tiempo real para detectar rostros en una webcam, seguir cada persona con un tracker de centroides y clasificar su emocion predominante con DeepFace.
Luego muestra las estadisticas en una interfaz hecha con Streamlit.

## Que hace el proyecto

- Detecta rostros en video en vivo con MediaPipe.
- Asigna un ID temporal a cada rostro para seguirlo entre frames.
- Clasifica emociones como `Feliz`, `Triste`, `Enojado`, `Sorprendido`, `Miedo`, `Asco` y `Aburrido`.
- Muestra un contador general, una grafica de barras y un registro de eventos.
- Permite iniciar, detener y reiniciar las estadisticas desde la barra lateral.

## Arquitectura

```
Webcam --> video_processor.py --> CentroidTracker + EmotionClassifier --> Streamlit app.py
                                      |                               |
                                      |                               +--> ui_components.py (grafica, metricas, log)
                                      +--> MediaPipe + DeepFace + OpenCV
```

La aplicacion corre localmente y no necesita servidor externo. Todo el procesamiento se hace en la misma maquina.

## Estructura de carpetas

```
proyecto_emociones_vision/
├── README.md
├── app.py                   # interfaz principal de Streamlit
├── video_processor.py       # captura la camara y procesa cada frame
├── emotion_classifier.py    # clasificacion de emociones con DeepFace
├── centroid_tracker.py      # seguimiento de rostros por centroides
├── ui_components.py         # grafica, metricas y log de eventos
├── styles.py                # estilos CSS de la interfaz
├── config.py                # parametros de configuracion del proyecto
└── face_landmarker.task     # modelo de MediaPipe para deteccion facial
```

## Herramientas utilizadas

- `streamlit`: interfaz web interactiva.
- `opencv-python`: captura de camara y dibujo sobre frames.
- `mediapipe`: deteccion facial y landmarks.
- `deepface`: clasificacion de emociones.
- `tf-keras`: backend requerido por DeepFace.
- `pandas` y `plotly`: construccion de graficas.
- `numpy`: calculos numericos y distancias entre centroides.

## Requisitos

- Python 3.12 o anterior. En este repo algunas dependencias dan problemas con Python 3.13.
- Una webcam funcional.
- Tener el archivo `face_landmarker.task` en la carpeta del proyecto.

## Como ejecutarlo

### Paso 0: instalar dependencias

Desde la raiz del repositorio (`proyectos_grupo_investigacion`):

```powershell
pip install -r requirements.txt
```

### Paso 1: entrar al proyecto

```powershell
cd proyecto_emociones_vision
```

### Paso 2: correr la app

```powershell
streamlit run app.py
```

Se abre en el navegador, normalmente en `http://localhost:8501`.

## Como usarlo

1. Abrir la aplicacion.
2. Presionar `Iniciar Camara`.
3. Permitir acceso a la webcam si el navegador lo solicita.
4. Observar como se detectan rostros, se asigna una emocion y se actualizan las estadisticas.
5. Usar `Detener Camara` para pausar el proceso.
6. Usar `Reiniciar Estadisticas` para limpiar contadores y log.

## Problemas comunes

- **La app no abre la camara**: revisa que ninguna otra aplicacion este usando la webcam.
- **Error con `face_landmarker.task`**: confirma que el archivo exista en `proyecto_emociones_vision/`.
- **Mensajes de TensorFlow o MediaPipe en terminal**: son avisos de las dependencias nativas; no suelen romper la app.
- **Aparece `__pycache__` en la carpeta**: es normal en Python. Ya esta ignorado por Git con `.gitignore`, asi que no hace falta subirlo.
- **La terminal muestra muchos logs**: algunos avisos vienen del stack nativo de TensorFlow/MediaPipe y no se pueden eliminar por completo desde Python.

## Nota sobre el modelo

El archivo `face_landmarker.task` es el modelo que usa MediaPipe para detectar la geometria del rostro. Si se borra, la aplicacion no puede iniciar correctamente hasta volver a colocarlo en la carpeta del proyecto.
