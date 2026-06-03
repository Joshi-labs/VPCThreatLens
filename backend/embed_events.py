import json
import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# INITIALIZE LOCAL EMBEDDINGS
# -----------------------------
embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# -----------------------------
# INITIALIZE CHROMADB
# -----------------------------
client = chromadb.PersistentClient(path="./chroma_db")

# Delete old collection to reset with new embedding dimension
try:
    client.delete_collection(name="network_events")
except:
    pass

collection = client.create_collection(name="network_events")

# -----------------------------
# LOAD EVENTS
# -----------------------------
with open("data/datasets/window_events.jsonl", "r") as f:
    for idx, line in enumerate(f):
        try:
            event = json.loads(line)
            if event["event_type"] == "normal_activity":
                continue

            text = f"Event Type: {event['event_type']}. Severity: {event['severity']}. Description: {event['description']}"

            # Sanitize metadata: ChromaDB doesn't allow lists in metadata
            sanitized_meta = {}
            for k, v in event.items():
                if isinstance(v, list):
                    sanitized_meta[k] = ", ".join(map(str, v))
                else:
                    sanitized_meta[k] = v

            # Get embedding from Ollama
            embedding = embeddings_model.embed_query(text)

            collection.add(
                ids=[str(idx)],
                embeddings=[embedding],
                documents=[text],
                metadatas=[sanitized_meta]
            )
        except Exception as e:
            print(f"Error processing line {idx}: {e}")

print("Embeddings stored in ChromaDB using local HuggingFace model.")
