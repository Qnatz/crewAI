from objectbox.model import Entity, Id
from objectbox import String, Bytes, Float32List

@Entity
class EmbeddingEntry:
    id = Id()  # Auto-incremented ID
    text = String()  # Original input text
    embedding = Float32List()  # List of floats (embedding vector)
