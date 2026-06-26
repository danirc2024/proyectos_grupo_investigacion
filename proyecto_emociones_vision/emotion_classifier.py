import time
from deepface import DeepFace

class EmotionClassifier:
    def __init__(self, throttle_seconds=1.0):
        # Mapeo de emociones de DeepFace (en inglés) a español
        self.throttle_seconds = throttle_seconds
        self.cache = {}
        self.emotion_mapping = {
            'happy': 'Feliz',
            'surprise': 'Sorprendido',
            'angry': 'Enojado',
            'sad': 'Triste',
            'fear': 'Miedo',
            'disgust': 'Asco',
            'neutral': 'Aburrido'
        }

    def classify_face_crop(self, face_crop, face_id):
        now = time.time()
        
        # 1. Verificar si tenemos una clasificación reciente en caché
        if face_id in self.cache:
            cached_data = self.cache[face_id]
            if now - cached_data['last_time'] < self.throttle_seconds:
                return cached_data['emotion'], cached_data['confidence']
                
        # 2. Si no hay caché o ya venció el tiempo de throttling, clasificar con DeepFace
        # Si el face_crop está vacío o es inválido, retornar valores por defecto
        if face_crop is None or face_crop.size == 0 or face_crop.shape[0] < 10 or face_crop.shape[1] < 10:
            return 'Aburrido', 1.0

        try:
            # DeepFace.analyze con backend 'opencv' detecta y clasifica rostros en un solo paso
            # enforce_detection=True lanzará una excepción si no hay caras en el frame, lo que capturamos para retornar []
            objs = DeepFace.analyze(
                img_path=face_crop,
                actions=['emotion'],
                enforce_detection=False,
                detector_backend='opencv',
                silent=True
            )
            
            if objs and len(objs) > 0:
                result = objs[0]
                dominant_en = result['dominant_emotion']
                confidence_pct = result['emotion'][dominant_en] / 100.0 

                # Traducir emoción
                dominant_es = self.emotion_mapping.get(dominant_en, 'Aburrido')

                self.cache[face_id] = {
                    'emotion': dominant_es,
                    'confidence': confidence_pct,
                    'last_time': now
                }
                
                return dominant_es, confidence_pct

        except Exception as e:
            # En caso de error, imprimir el error de forma segura en Windows (evitando fallos de unicode/emoji)
            err_msg = str(e).encode('ascii', 'ignore').decode('ascii')
            print(f"[EmotionClassifier ERROR] Error clasificando ID {face_id}: {err_msg}")
            if face_id in self.cache:
                return self.cache[face_id]['emotion'], self.cache[face_id]['confidence']
                
        # Si falla y no hay caché anterior, retornar neutral
        return 'Aburrido', 1.0
