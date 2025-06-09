from objectbox.model import ModelBuilder, Entity, Id, Property, FloatVector, IndexType

# 1) Build schema
builder = ModelBuilder()

class MemoryEntry(Entity):
    id = Id()
    content = Property(str)
    vector = FloatVector(dimension=384, index=IndexType.HNSW)
    metadata = Property(str)  # JSON-encoded dict

builder.entity(MemoryEntry)
model = builder.finish()

# 2) Open or create a store in Termux
from objectbox import Store

# Define the store path, ensuring the directory exists.
# The actual store creation will be handled by the memory adapter or main application logic.
STORE_PATH = "/data/data/com.termux/files/home/crewAI/db"

# It's good practice to ensure the directory for the store exists when the application starts.
# However, just defining the schema doesn't require the store to be opened here.
# store = Store(model, STORE_PATH)
# box = store.box(MemoryEntry)
