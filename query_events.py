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
# OLLAMA CONFIG
# -----------------------------
OLLAMA_BASE_URL = "http://192.168.1.10:11434"
OLLAMA_MODEL = "llama3.2:1b"

def ollama_chat(prompt):
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    response = requests.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload)
    return response.json()["message"]["content"]

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
analysis = ollama_chat(prompt)
print(analysis)
