import os
import time
from typing import Generator

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

import config
from centroid_tracker import CentroidTracker
from emotion_classifier import EmotionClassifier


def procesar_video(
    tracker: CentroidTracker,
    classifier: EmotionClassifier,
    counts: dict[str, int],
    model_path: str,
    running_flag: list[bool],
) -> Generator[tuple[np.ndarray, list[str]], None, None]:
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("No se pudo acceder a la cámara web.")

    base_options = python.BaseOptions(
        model_asset_buffer=open(model_path, "rb").read()
    )
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        output_face_blendshapes=False,
        num_faces=config.NUM_FACES,
    )

    with vision.FaceLandmarker.create_from_options(options) as detector:
        while cap.isOpened() and running_flag[0]:
            ret, frame = cap.read()
            if not ret:
                break

            # Espejo horizontal (efecto natural para el usuario)
            frame = cv2.flip(frame, 1)
            alto, ancho = frame.shape[:2]
            nuevos_eventos: list[str] = []


            frame_rgb_input = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_imagen = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb_input)
            timestamp_ms = int(time.time() * 1000)
            resultados = detector.detect_for_video(mp_imagen, timestamp_ms)

            current_centroids: list[tuple[float, float]] = []
            frame_faces_raw: list[dict] = []

            if resultados.face_landmarks:
                for rostro_landmarks in resultados.face_landmarks:
                    cx = sum(p.x for p in rostro_landmarks) / len(rostro_landmarks)
                    cy = sum(p.y for p in rostro_landmarks) / len(rostro_landmarks)
                    current_centroids.append((cx, cy))

                    x_coords = [int(p.x * ancho) for p in rostro_landmarks]
                    y_coords = [int(p.y * alto) for p in rostro_landmarks]
                    xmin = max(0, min(x_coords))
                    xmax = min(ancho, max(x_coords))
                    ymin = max(0, min(y_coords))
                    ymax = min(alto, max(y_coords))

                    frame_faces_raw.append({
                        "centroid":   (cx, cy),
                        "bbox":       (xmin, ymin, xmax, ymax),
                        "landmarks":  rostro_landmarks,
                    })


            old_ids = set(tracker.objects.keys())
            tracker.update(current_centroids)
            new_ids = set(tracker.objects.keys())
            removed_ids = old_ids - new_ids

            for r_id in removed_ids:
                if not tracker.counted_emotions.get(r_id, True):
                    history = tracker.emotions_history.get(r_id, [])
                    dominant_final = (
                        max(set(history), key=history.count) if history else "Aburrido"
                    )
                    counts[dominant_final] += 1
                    tracker.counted_emotions[r_id] = True
                    t_str = time.strftime("%H:%M:%S")
                    nuevos_eventos.append(
                        f"[{t_str}] Persona #{r_id} se retiró. Clasificación final: {dominant_final}"
                    )


            for face_raw in frame_faces_raw:
                cx, cy = face_raw["centroid"]
                xmin, ymin, xmax, ymax = face_raw["bbox"]

                # Encontrar el ID del tracker más cercano al centroide
                face_id: int | None = None
                min_dist = float("inf")
                for obj_id, obj_centroid in tracker.objects.items():
                    dist = np.sqrt((cx - obj_centroid[0]) ** 2 + (cy - obj_centroid[1]) ** 2)
                    if dist < min_dist:
                        min_dist = dist
                        face_id = obj_id

                if face_id is None or min_dist > tracker.max_distance:
                    continue

                # Recortar rostro con margen para mejorar clasificación
                pad_x = int((xmax - xmin) * config.PAD_RATIO)
                pad_y = int((ymax - ymin) * config.PAD_RATIO)
                crop_xmin = max(0, xmin - pad_x)
                crop_ymin = max(0, ymin - pad_y)
                crop_xmax = min(ancho, xmax + pad_x)
                crop_ymax = min(alto, ymax + pad_y)
                face_crop = frame[crop_ymin:crop_ymax, crop_xmin:crop_xmax]

                emotion, confidence = classifier.classify_face_crop(face_crop, face_id)

                # Acumular emoción en el historial del tracker
                tracker.emotions_history[face_id].append(emotion)

                # Conteo inmediato si la emoción es clara y no se contó aún
                if not tracker.counted_emotions[face_id]:
                    if emotion != "Aburrido" and confidence > config.CONFIDENCE_THRESHOLD:
                        counts[emotion] += 1
                        tracker.counted_emotions[face_id] = True
                        t_str = time.strftime("%H:%M:%S")
                        nuevos_eventos.append(
                            f"[{t_str}] ¡Persona #{face_id} expresó {emotion} ({int(confidence * 100)}%)!"
                        )

                # ---- Dibujo sobre el frame ----
                draw_color = config.COLORS_BGR.get(emotion, (0, 255, 0))

                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), draw_color, 2)

                for pt in face_raw["landmarks"]:
                    lx = int(pt.x * ancho)
                    ly = int(pt.y * alto)
                    cv2.circle(frame, (lx, ly), 1, draw_color, -1)

                label = f"ID {face_id}: {emotion} ({int(confidence * 100)}%)"
                cv2.putText(
                    frame, label, (xmin, ymin - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, draw_color, 2,
                )

            frame_rgb_out = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            yield frame_rgb_out, nuevos_eventos

            time.sleep(config.LOOP_DELAY_SECONDS)

    cap.release()
