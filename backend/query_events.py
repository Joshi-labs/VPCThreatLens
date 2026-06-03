import os
import json
import chromadb
from dotenv import load_dotenv
import requests

# -----------------------------
# LOAD ENV
# -----------------------------
load_dotenv()

# -----------------------------
# OPENROUTER CONFIG
# -----------------------------
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = "google/gemini-2.5-flash-lite"

def openrouter_chat(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    if response.status_code != 200:
        return f"Error: {response.status_code} - {response.text}"
    return response.json()["choices"][0]["message"]["content"]

# -----------------------------
# CHROMADB
# -----------------------------
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection(name="network_events")

# -----------------------------
# USER INPUT
# -----------------------------
query = input("Enter query: ")
severity = input("Severity filter (optional): ").strip()
event_type = input("Event type filter (optional): ").strip()
start_time = input("Start timestamp (optional): ").strip()

# -----------------------------
# BUILD FILTER
# -----------------------------
where_filter = {}
if severity:
    where_filter["severity"] = severity
if event_type:
    where_filter["event_type"] = event_type
if start_time:
    where_filter["event_time_start"] = {"$gte": int(start_time)}

# -----------------------------
# VECTOR SEARCH
# -----------------------------
if len(where_filter) == 0:
    results = collection.query(query_texts=[query], n_results=5)
else:
    results = collection.query(query_texts=[query], n_results=5, where=where_filter)

# -----------------------------
# EXTRACT RESULTS
# -----------------------------
documents = results["documents"][0]
metadatas = results["metadatas"][0]
context = ""
for doc, meta in zip(documents, metadatas):
    context += f"\nEvent: {doc}\nMetadata: {meta}\n"

# -----------------------------
# PROMPT
# -----------------------------
prompt = f"""
You are a cybersecurity analyst. Analyze the retrieved network security events.
User Query: {query}
Retrieved Events: {context}
Explain: what is happening, attack patterns, severity, suspicious behavior, recommended actions.
"""

# -----------------------------
# LLM CALL
# -----------------------------
print("\n========== ANALYSIS ==========\n")
analysis = openrouter_chat(prompt)
print(analysis)
