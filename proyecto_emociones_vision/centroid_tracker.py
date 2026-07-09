from collections import defaultdict
import numpy as np

class CentroidTracker:

    def __init__(self, max_disappeared: int = 15, max_distance: float = 0.15) -> None:

        self.next_object_id: int = 0
        self.objects: dict[int, tuple[float, float]] = {}
        self.disappeared: dict[int, int] = {}
        self.counted_emotions: dict[int, bool] = {}
        self.emotions_history: dict[int, list[str]] = defaultdict(list)
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance

    # Registro / eliminación de objetos

    def register(self, centroid: tuple[float, float]) -> int:
        oid = self.next_object_id
        self.objects[oid] = centroid
        self.disappeared[oid] = 0
        self.counted_emotions[oid] = False
        self.emotions_history[oid] = []
        self.next_object_id += 1
        return oid

    def deregister(self, object_id: int) -> None:
        self.objects.pop(object_id, None)
        self.disappeared.pop(object_id, None)
        self.counted_emotions.pop(object_id, None)
        if object_id in self.emotions_history:
            del self.emotions_history[object_id]

    # Actualización por frame

    def update(self, input_centroids: list[tuple[float, float]]) -> dict[int, tuple[float, float]]:

        if not input_centroids:
            for oid in list(self.disappeared):
                self.disappeared[oid] += 1
                if self.disappeared[oid] > self.max_disappeared:
                    self.deregister(oid)
            return self.objects

        # Sin objetos previos: registrar todos los centroides nuevos
        if not self.objects:
            for centroid in input_centroids:
                self.register(centroid)
            return self.objects

        object_ids = list(self.objects.keys())
        object_centroids = list(self.objects.values())

        # Matriz de distancias euclidianas (objetos × detecciones)
        D = np.zeros((len(object_centroids), len(input_centroids)))
        for i, oc in enumerate(object_centroids):
            for j, ic in enumerate(input_centroids):
                D[i, j] = np.sqrt((oc[0] - ic[0]) ** 2 + (oc[1] - ic[1]) ** 2)

        # Greedy matching: emparejar por distancia mínima
        rows = D.min(axis=1).argsort()
        cols = D.argmin(axis=1)[rows]

        used_rows: set[int] = set()
        used_cols: set[int] = set()

        for row, col in zip(rows, cols):
            if row in used_rows or col in used_cols:
                continue
            if D[row, col] > self.max_distance:
                continue

            oid = object_ids[row]
            self.objects[oid] = input_centroids[col]
            self.disappeared[oid] = 0
            used_rows.add(row)
            used_cols.add(col)

        # Registrar detecciones sin pareja (columnas sin usar)
        for col in range(D.shape[1]):
            if col not in used_cols:
                self.register(input_centroids[col])

        # Incrementar desaparición para objetos sin pareja (filas sin usar)
        for row in set(range(D.shape[0])) - used_rows:
            oid = object_ids[row]
            self.disappeared[oid] += 1
            if self.disappeared[oid] > self.max_disappeared:
                self.deregister(oid)

        return self.objects
