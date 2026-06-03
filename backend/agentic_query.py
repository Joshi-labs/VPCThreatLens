import os
import json
import chromadb
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from time_parser import parse_time_query
from llm_client import client

# -----------------------------
# INITIALIZE
# -----------------------------
embeddings_model = client.get_embeddings()

# -----------------------------
# CHROMADB
# -----------------------------
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection(name="network_events")

# -----------------------------
# REFERENCE DATE
# -----------------------------
REFERENCE_DATE = datetime(2026, 5, 28)

def hhmm_to_unix(hhmm):
    dt = datetime.strptime(hhmm, "%H:%M")
    combined = REFERENCE_DATE.replace(hour=dt.hour, minute=dt.minute, second=0)
    return int(combined.timestamp())

user_query = input("\nEnter investigation query: ")

time_data = parse_time_query(user_query)
start_unix = hhmm_to_unix(time_data["start_time"]) if time_data.get("start_time") else None
end_unix = hhmm_to_unix(time_data["end_time"]) if time_data.get("end_time") else None

# -----------------------------
# PARSE QUERY
# -----------------------------
parser_prompt = f"""
You are a cybersecurity query parser. Convert the user query into JSON. 
Map user phrases intelligently. Return ONLY valid JSON.

Query: {user_query}
"""

content = client.chat(parser_prompt)
content = content.strip()

if "```json" in content: content = content.split("```json")[1].split("```")[0].strip()
elif "```" in content: content = content.split("```")[1].split("```")[0].strip()

try:
    parsed_json = json.loads(content)
except:
    print("\nFailed to parse JSON")
    exit()

# -----------------------------
# BUILD FILTERS
# -----------------------------
filters = []
if parsed_json.get("severity"): filters.append({"severity": parsed_json["severity"]})
if parsed_json.get("event_type"): filters.append({"event_type": parsed_json["event_type"]})

if start_unix and end_unix:
    filters.append({"$and": [{"event_time_start": {"$gte": start_unix}}, {"event_time_start": {"$lte": end_unix}}]})
elif start_unix:
    filters.append({"event_time_start": {"$gte": start_unix}})
elif end_unix:
    filters.append({"event_time_start": {"$lte": end_unix}})

where_filter = None
if len(filters) == 1: where_filter = filters[0]
elif len(filters) > 1: where_filter = {"$and": filters}

# -----------------------------
# VECTOR SEARCH
# -----------------------------
query_embedding = embeddings_model.embed_query(user_query)

if where_filter is None:
    results = collection.query(query_embeddings=[query_embedding], n_results=5)
else:
    results = collection.query(query_embeddings=[query_embedding], n_results=5, where=where_filter)

documents = results["documents"][0]
metadatas = results["metadatas"][0]
context = ""
for doc, meta in zip(documents, metadatas):
    context += f"\nEvent Type: {meta.get('event_type')}\nSeverity: {meta.get('severity')}\nSource IP: {meta.get('src_ip')}\nDescription: {meta.get('description')}\n"

# -----------------------------
# ANALYSIS PROMPT
# -----------------------------
analysis_prompt = f"Analyze these events for query: {user_query}\nEvents: {context}"

print("\n========== ANALYSIS ==========\n")
analysis_result = client.chat(analysis_prompt)
print(analysis_result)
print("\n")
