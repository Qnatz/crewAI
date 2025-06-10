from objectbox.model import Entity, Id, Property, Float32Vector, HnswIndex, Model # Added Model
from objectbox import Store

# 1) Define schema by defining the entity class
@Entity() # Calling the decorator
class MemoryEntry:
    id = Id()
    content = Property(str)
    vector = Float32Vector(index=HnswIndex(dimensions=384)) # dimensions moved to HnswIndex
    metadata = Property(str)  # JSON-encoded dict

# Create a Model object and add entities to it
_model_instance = Model()
_model_instance.entity(MemoryEntry)
model = _model_instance

# 2) Open or create a store in Termux

# Define the store path, ensuring the directory exists.
# The actual store creation will be handled by the memory adapter or main application logic.
STORE_PATH = "/data/data/com.termux/files/home/crewAI/db"

# It's good practice to ensure the directory for the store exists when the application starts.
# However, just defining the schema doesn't require the store to be opened here.
# store = Store(model, STORE_PATH)
# box = store.box(MemoryEntry)
