import os
import json
import chromadb
from datetime import datetime
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from time_parser import parse_time_query

# -----------------------------
# LOAD ENV
# -----------------------------
load_dotenv()

# -----------------------------
# OLLAMA LLM
# -----------------------------
llm = ChatOllama(
    model="llama3.2:1b",
    base_url="http://192.168.1.10:11434",
    temperature=0
)

# -----------------------------
# CHROMADB
# -----------------------------
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection(name="network_events")

# -----------------------------
# REFERENCE DATE
# -----------------------------
REFERENCE_DATE = datetime(2026, 5, 28)

# -----------------------------
# HH:MM -> UNIX
# -----------------------------
def hhmm_to_unix(hhmm):
    dt = datetime.strptime(hhmm, "%H:%M")
    combined = REFERENCE_DATE.replace(hour=dt.hour, minute=dt.minute, second=0)
    return int(combined.timestamp())

# -----------------------------
# QUERY PARSER PROMPT
# -----------------------------
parser_prompt = ChatPromptTemplate.from_messages([
    ("system",
     """
You are a cybersecurity query parser.
Convert the user query into JSON.
Allowed event types: coordinated_ssh_activity, port_scan, traffic_spike, rejected_activity.
Map user phrases intelligently.
Extract: event_type, severity, intent. Return ONLY valid JSON.
"""
     ),
    ("human", "{query}")
])

# -----------------------------
# USER QUERY
# -----------------------------
user_query = input("\nEnter investigation query: ")

# -----------------------------
# TIME EXTRACTION
# -----------------------------
time_data = parse_time_query(user_query)
print("\n========== TIME PARSED ==========\n")
print(time_data)

# -----------------------------
# TIME -> UNIX
# -----------------------------
start_unix = None
end_unix = None
if time_data.get("start_time"):
    start_unix = hhmm_to_unix(time_data["start_time"])
if time_data.get("end_time"):
    end_unix = hhmm_to_unix(time_data["end_time"])

# -----------------------------
# PARSE QUERY
# -----------------------------
parser_chain = parser_prompt | llm
response = parser_chain.invoke({"query": user_query})
content = response.content.strip()

# Cleanup JSON
if "```json" in content:
    content = content.split("```json")[1].split("```")[0].strip()
elif "```" in content:
    content = content.split("```")[1].split("```")[0].strip()

try:
    parsed_json = json.loads(content)
except Exception as e:
    print("\nFailed to parse JSON")
    exit()

# -----------------------------
# BUILD FILTERS
# -----------------------------
filters = []
if parsed_json.get("severity"):
    filters.append({"severity": parsed_json["severity"]})
if parsed_json.get("event_type"):
    filters.append({"event_type": parsed_json["event_type"]})

if start_unix and end_unix:
    filters.append({"$and": [{"event_time_start": {"$gte": start_unix}}, {"event_time_start": {"$lte": end_unix}}]})
elif start_unix:
    filters.append({"event_time_start": {"$gte": start_unix}})
elif end_unix:
    filters.append({"event_time_start": {"$lte": end_unix}})

where_filter = None
if len(filters) == 1:
    where_filter = filters[0]
elif len(filters) > 1:
    where_filter = {"$and": filters}

# -----------------------------
# VECTOR SEARCH
# -----------------------------
if where_filter is None:
    results = collection.query(query_texts=[user_query], n_results=5)
else:
    results = collection.query(query_texts=[user_query], n_results=5, where=where_filter)

# -----------------------------
# EXTRACT RESULTS
# -----------------------------
documents = results["documents"][0]
metadatas = results["metadatas"][0]
context = ""
for doc, meta in zip(documents, metadatas):
    context += f"\nEvent Type: {meta.get('event_type')}\nSeverity: {meta.get('severity')}\nSource IP: {meta.get('src_ip')}\nDescription: {meta.get('description')}\n"

# -----------------------------
# ANALYSIS PROMPT
# -----------------------------
analysis_prompt = f"""
You are a SOC analyst. Analyze ONLY the retrieved events below.
User Query: {user_query}
Retrieved Events: {context}
Explain: what happened, attack patterns, suspicious activity, possible causes, recommendations.
"""

# -----------------------------
# FINAL ANALYSIS (STREAMING)
# -----------------------------
print("\n========== ANALYSIS ==========\n")
for chunk in llm.stream(analysis_prompt):
    print(chunk.content, end="", flush=True)
print("\n")
