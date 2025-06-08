# src/crewai/utilities/embedding_configurator.py

import sqlite3
import numpy as np

class EmbeddingConfigurator:
    """
    Simple embedding store using SQLite for persistence
    and NumPy arrays for vector math.
    """

    def __init__(self, db_path: str = "embeddings.db", table: str = "embeddings"):
        # connect (creates file if not exists)
        self.conn = sqlite3.connect(db_path)
        self.table = table
        self._create_table()

    def _create_table(self):
        cur = self.conn.cursor()
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table} (
                id TEXT PRIMARY KEY,
                embedding BLOB
            )
        """)
        self.conn.commit()

    def add_embedding(self, id: str, vector: np.ndarray):
        """Store or replace an embedding."""
        blob = vector.astype(np.float32).tobytes()
        self.conn.execute(
            f"INSERT OR REPLACE INTO {self.table}(id, embedding) VALUES (?, ?)",
            (id, blob)
        )
        self.conn.commit()

    def get_embedding(self, id: str) -> np.ndarray | None:
        """Retrieve an embedding by ID."""
        cur = self.conn.cursor()
        row = cur.execute(
            f"SELECT embedding FROM {self.table} WHERE id = ?",
            (id,)
        ).fetchone()
        if not row:
            return None
        return np.frombuffer(row[0], dtype=np.float32)

    def search_similar(self, vector: np.ndarray, top_k: int = 5) -> list[tuple[str, float]]:
        """
        Naïve similarity search: loads all and ranks by Euclidean distance.
        Returns list of (id, distance).
        """
        cur = self.conn.cursor()
        rows = cur.execute(f"SELECT id, embedding FROM {self.table}").fetchall()
        candidates = []
        for doc_id, blob in rows:
            emb = np.frombuffer(blob, dtype=np.float32)
            dist = np.linalg.norm(emb - vector.astype(np.float32))
            candidates.append((doc_id, dist))
        candidates.sort(key=lambda x: x[1])
        return candidates[:top_k]
