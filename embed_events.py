import json
import chromadb

from sentence_transformers import SentenceTransformer

# -----------------------------
# LOAD EMBEDDING MODEL
# -----------------------------

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

# -----------------------------
# INITIALIZE CHROMADB
# -----------------------------

client = chromadb.PersistentClient(
    path="./chroma_db"
)

# Delete old collection if needed
try:
    client.delete_collection(
        name="network_events"
    )
except:
    pass

collection = client.get_or_create_collection(
    name="network_events"
)

# -----------------------------
# LOAD EVENTS
# -----------------------------

with open(
    "data/datasets/window_events.jsonl",
    "r"
) as f:

    for idx, line in enumerate(f):

        try:

            event = json.loads(line)

            # Skip normal activity
            if (
                event["event_type"]
                == "normal_activity"
            ):
                continue

            text = (

                f"Event Type: "
                f"{event['event_type']}. "

                f"Severity: "
                f"{event['severity']}. "

                f"Description: "
                f"{event['description']}"

            )

            embedding = model.encode(
                text
            ).tolist()

            collection.add(

                ids=[str(idx)],

                embeddings=[embedding],

                documents=[text],

                metadatas=[event]
            )

        except Exception as e:

            print(
                f"Error processing line {idx}: {e}"
            )

print(
    "Embeddings stored in ChromaDB."
)