import numpy as np

class CentroidTracker:
    def __init__(self, max_disappeared=15, max_distance=0.15):
        """
        Inicializa el seguidor de centroides.
        :param max_disappeared: Número de frames consecutivos que un objeto puede estar "desaparecido" antes de ser eliminado.
        :param max_distance: Distancia máxima en coordenadas normalizadas (0.0 a 1.0) para asociar un rostro existente.
        """
        self.next_object_id = 0
        self.objects = {}             # ID -> centroid (x, y)
        self.disappeared = {}         # ID -> count of consecutive frames disappeared
        self.counted_emotions = {}    # ID -> bool (si ya se contó la emoción de este rostro)
        self.emotions_history = {}    # ID -> lista de emociones detectadas
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance

    def register(self, centroid):
        """Registra un nuevo objeto con el centroide dado."""
        self.objects[self.next_object_id] = centroid
        self.disappeared[self.next_object_id] = 0
        self.counted_emotions[self.next_object_id] = False
        self.emotions_history[self.next_object_id] = []
        self.next_object_id += 1
        return self.next_object_id - 1

    def deregister(self, object_id):
        """Elimina un objeto del seguimiento."""
        if object_id in self.objects:
            del self.objects[object_id]
        if object_id in self.disappeared:
            del self.disappeared[object_id]
        if object_id in self.counted_emotions:
            del self.counted_emotions[object_id]
        if object_id in self.emotions_history:
            del self.emotions_history[object_id]

    def update(self, input_centroids):
        """
        Actualiza el estado de los objetos basados en los nuevos centroides detectados.
        :param input_centroids: Lista de tuplas (x, y) que representan los centroides de los rostros en el frame actual.
        :return: Diccionario de objetos activos {ID: (x, y)}
        """
        # Si no se detectaron centroides, incrementar el contador de "desaparecido" para todos
        if len(input_centroids) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return self.objects

        # Si no hay objetos en seguimiento, registrar todos los centroides nuevos
        if len(self.objects) == 0:
            for centroid in input_centroids:
                self.register(centroid)
        else:
            object_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())

            # Calcular la matriz de distancias euclidianas entre centroides guardados y nuevos
            D = np.zeros((len(object_centroids), len(input_centroids)))
            for i, oc in enumerate(object_centroids):
                for j, ic in enumerate(input_centroids):
                    D[i, j] = np.sqrt((oc[0] - ic[0])**2 + (oc[1] - ic[1])**2)

            # Encontrar el menor en cada fila y ordenarlos por cercanía
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]

            used_rows = set()
            used_cols = set()

            for row, col in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue

                # Si la distancia es mayor al umbral, considerarlo un nuevo rostro
                if D[row, col] > self.max_distance:
                    continue

                object_id = object_ids[row]
                self.objects[object_id] = input_centroids[col]
                self.disappeared[object_id] = 0

                used_rows.add(row)
                used_cols.add(col)

            # Registrar los nuevos rostros (columnas no asociadas)
            for col in range(D.shape[1]):
                if col not in used_cols:
                    self.register(input_centroids[col])

            # Incrementar contador y eliminar los rostros viejos que no se asociaron
            unused_rows = set(range(D.shape[0])) - used_rows
            for row in unused_rows:
                object_id = object_ids[row]
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)

        return self.objects
