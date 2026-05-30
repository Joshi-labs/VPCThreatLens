import os
import chromadb

from dotenv import load_dotenv
from openai import OpenAI

# -----------------------------
# LOAD ENV
# -----------------------------

load_dotenv()

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

# -----------------------------
# OPENROUTER CLIENT
# -----------------------------

client = OpenAI(

    base_url="https://openrouter.ai/api/v1",

    api_key=OPENROUTER_API_KEY
)

# -----------------------------
# CHROMADB
# -----------------------------

chroma_client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = chroma_client.get_collection(
    name="network_events"
)

# -----------------------------
# USER INPUT
# -----------------------------

query = input("Enter query: ")

severity = input(
    "Severity filter (optional): "
).strip()

event_type = input(
    "Event type filter (optional): "
).strip()

start_time = input(
    "Start timestamp (optional): "
).strip()

# -----------------------------
# BUILD FILTER
# -----------------------------

where_filter = {}

if severity:

    where_filter["severity"] = severity

if event_type:

    where_filter["event_type"] = event_type

if start_time:

    where_filter["event_time_start"] = {
        "$gte": int(start_time)
    }

# -----------------------------
# VECTOR SEARCH
# -----------------------------

if len(where_filter) == 0:

    results = collection.query(

        query_texts=[query],

        n_results=5
    )

else:

    results = collection.query(

        query_texts=[query],

        n_results=5,

        where=where_filter
    )

# -----------------------------
# EXTRACT RESULTS
# -----------------------------

documents = results["documents"][0]

metadatas = results["metadatas"][0]

context = ""

for doc, meta in zip(
    documents,
    metadatas
):

    context += f"""

Event:
{doc}

Metadata:
{meta}

"""

# -----------------------------
# PROMPT
# -----------------------------

prompt = f"""

You are a cybersecurity analyst.

Analyze the retrieved network security events.

User Query:
{query}

Retrieved Events:
{context}

Explain:
- what is happening
- attack patterns
- severity
- suspicious behavior
- recommended actions

"""

# -----------------------------
# LLM CALL
# -----------------------------

response = client.chat.completions.create(

    model="openai/gpt-4.1-mini",

    max_tokens=500,

    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

# -----------------------------
# OUTPUT
# -----------------------------

print("\n========== ANALYSIS ==========\n")

print(
    response.choices[0].message.content
)