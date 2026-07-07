import time
from deepface import DeepFace
import config

class EmotionClassifier:

    def __init__(self, throttle_seconds: float = config.THROTTLE_SECONDS) -> None:

        self.throttle_seconds = throttle_seconds
        # cache: { face_id -> {'emotion': str, 'confidence': float, 'last_time': float} }
        self._cache: dict[int, dict] = {}
        self._emotion_mapping: dict[str, str] = config.EMOTION_MAPPING

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def classify_face_crop(
        self, face_crop, face_id: int
    ) -> tuple[str, float]:

        now = time.time()

        # 1. Devolver caché si el throttle aún está vigente
        cached = self._cache.get(face_id)
        if cached and (now - cached["last_time"]) < self.throttle_seconds:
            return cached["emotion"], cached["confidence"]

        # 2. Validar el recorte antes de llamar a DeepFace
        if face_crop is None or face_crop.size == 0 or face_crop.shape[0] < 10 or face_crop.shape[1] < 10:
            return "Aburrido", 1.0

        # 3. Clasificar con DeepFace
        try:
            objs = DeepFace.analyze(
                img_path=face_crop,
                actions=["emotion"],
                enforce_detection=False,
                detector_backend="opencv",
                silent=True,
            )

            if objs:
                result = objs[0]
                dominant_en: str = result["dominant_emotion"]
                confidence: float = result["emotion"][dominant_en] / 100.0
                dominant_es: str = self._emotion_mapping.get(dominant_en, "Aburrido")

                self._cache[face_id] = {
                    "emotion": dominant_es,
                    "confidence": confidence,
                    "last_time": now,
                }
                return dominant_es, confidence

        except Exception as exc:
            err_msg = str(exc).encode("ascii", "ignore").decode("ascii")
            print(f"[EmotionClassifier ERROR] ID {face_id}: {err_msg}")
            # Reutilizar caché anterior si existe
            if cached:
                return cached["emotion"], cached["confidence"]

        return "Aburrido", 1.0
