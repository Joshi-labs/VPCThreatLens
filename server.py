from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import chromadb
from datetime import datetime
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from time_parser import parse_time_query

# Load environment variables
load_dotenv()

app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM and ChromaDB (same as agentic_query.py)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    model="openai/gpt-4.1-mini",
    max_tokens=400  # Reduced from 1000
)

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection(name="network_events")

REFERENCE_DATE = datetime(2026, 5, 28)

def hhmm_to_unix(hhmm):
    try:
        dt = datetime.strptime(hhmm, "%H:%M")
        combined = REFERENCE_DATE.replace(hour=dt.hour, minute=dt.minute, second=0)
        return int(combined.timestamp())
    except:
        return None

class QueryRequest(BaseModel):
    query: str

@app.post("/api/investigate")
async def investigate(request: QueryRequest):
    user_query = request.query
    
    try:
        # 1. Parse Time
        time_data = parse_time_query(user_query)
        start_unix = hhmm_to_unix(time_data.get("start_time")) if time_data.get("start_time") else None
        end_unix = hhmm_to_unix(time_data.get("end_time")) if time_data.get("end_time") else None

        # 2. Parse Query with LLM
        parser_prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are a cybersecurity query parser. Convert the user query into JSON.
            Allowed event types: coordinated_ssh_activity, port_scan, traffic_spike, rejected_activity.
            Extract: event_type, severity, intent. Return ONLY valid JSON.
            """),
            ("human", "{query}")
        ])
        
        parser_chain = parser_prompt | llm
        response = parser_chain.invoke({"query": user_query})
        parsed = response.content.replace("```json", "").replace("```", "").strip()
        
        try:
            parsed_json = json.loads(parsed)
        except:
            parsed_json = {}

        # 3. Build Filters
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

        # 4. Vector Search
        if where_filter is None:
            results = collection.query(query_texts=[user_query], n_results=5)
        else:
            results = collection.query(query_texts=[user_query], n_results=5, where=where_filter)

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        
        context = ""
        retrieved_events = []
        for doc, meta in zip(documents, metadatas):
            retrieved_events.append(meta)
            context += f"\nEvent Type: {meta.get('event_type')}\nSeverity: {meta.get('severity')}\nSource IP: {meta.get('src_ip')}\nDescription: {meta.get('description')}\n"

        # 5. Final Analysis
        analysis_prompt = f"""
        You are a SOC analyst. Analyze ONLY the retrieved events below.
        User Query: {user_query}
        Retrieved Events: {context}
        Explain: what happened, attack patterns, suspicious activity, possible causes, recommendations.
        """
        
        analysis_response = llm.invoke(analysis_prompt)
        
        return {
            "query": user_query,
            "parsed_query": parsed_json,
            "events": retrieved_events,
            "analysis": analysis_response.content
        }
    except Exception as e:
        print(f"Error during investigation: {str(e)}")
        # Return a structured error response that doesn't break CORS
        return {
            "query": user_query,
            "parsed_query": {},
            "events": [],
            "analysis": f"INVESTIGATION_FAILED: {str(e)}"
        }

@app.get("/api/stats")
async def get_stats():
    # Return some mock or real stats for the dashboard
    return {
        "total_events": collection.count(),
        "threats_detected": 42, # Mock
        "critical_alerts": 7,    # Mock
        "avg_response_time": "1.2s"
    }

@app.get("/api/raw-logs")
async def list_raw_logs():
    raw_dir = "data/raw"
    if not os.path.exists(raw_dir):
        return {"files": []}
    files = [f for f in os.listdir(raw_dir) if f.endswith(".gz")]
    return {"files": files}

@app.get("/api/raw-logs/{filename}")
async def preview_raw_log(filename: str):
    import gzip
    file_path = os.path.join("data/raw", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        with gzip.open(file_path, 'rt') as f:
            content = [f.readline() for _ in range(20)]
        return {"content": "".join(content)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/events")
async def preview_events():
    dataset_path = "data/datasets/events.jsonl"
    if not os.path.exists(dataset_path):
        return {"events": []}
    
    events = []
    try:
        with open(dataset_path, 'r') as f:
            for i, line in enumerate(f):
                events.append(json.loads(line))
                if i >= 49: # Limit to 50 for preview
                    break
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
