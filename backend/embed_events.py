import json
import chromadb
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# INITIALIZE OPENAI EMBEDDINGS
# -----------------------------
embeddings_model = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

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

print("Embeddings stored in ChromaDB using OpenAI.")
