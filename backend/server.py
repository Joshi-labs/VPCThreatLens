from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
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


# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from langchain_community.embeddings import HuggingFaceEmbeddings

# Initialize OpenRouter LLM (via LangChain OpenAI adapter)
llm = ChatOpenAI(
    model="google/gemini-flash-1.5",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0
)

# Use a local embedding model to remove OpenAI dependency entirely
embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="network_events")

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
            ("system", "You are a cybersecurity query parser. Convert the user query into JSON. Allowed event types: coordinated_ssh_activity, port_scan, traffic_spike, rejected_activity. Extract: event_type, severity, intent. Return ONLY valid JSON."),
            ("human", "{query}")
        ])
        
        parser_chain = parser_prompt | llm
        response = parser_chain.invoke({"query": user_query})
        
        content = response.content.strip()
        if "```json" in content: content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content: content = content.split("```")[1].split("```")[0].strip()
            
        try:
            parsed_json = json.loads(content)
        except:
            parsed_json = {}

        # 3. Build Filters
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

        # 4. Vector Search (Manual Embedding via Ollama)
        print(f"DEBUG: Vectorizing user query: {user_query}")
        query_embedding = embeddings_model.embed_query(user_query)
        
        if where_filter is None:
            results = collection.query(query_embeddings=[query_embedding], n_results=5)
        else:
            print(f"DEBUG: Applying filter: {where_filter}")
            results = collection.query(query_embeddings=[query_embedding], n_results=5, where=where_filter)

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        
        print(f"DEBUG: Retrieved {len(documents)} events from ChromaDB")
        
        context = ""
        retrieved_events = []
        for doc, meta in zip(documents, metadatas):
            retrieved_events.append(meta)
            context += f"\nEvent Type: {meta.get('event_type')}\nSeverity: {meta.get('severity')}\nSource IP: {meta.get('src_ip')}\nDescription: {meta.get('description')}\n"

        # 5. Final Analysis
        if not context.strip():
            print("DEBUG: NO CONTEXT RETRIEVED. LLM will have no data to analyze.")
        
        analysis_prompt = f"You are a SOC analyst. Analyze ONLY the retrieved events below.\nUser Query: {user_query}\nRetrieved Events: {context}\n"
        print(f"DEBUG: Sending prompt to LLM (length: {len(analysis_prompt)})")
        analysis_response = llm.invoke(analysis_prompt)
        
        return {
            "query": user_query,
            "parsed_query": parsed_json,
            "events": retrieved_events,
            "analysis": analysis_response.content
        }
    except Exception as e:
        print(f"Error during investigation: {str(e)}")
        return {"query": user_query, "parsed_query": {}, "events": [], "analysis": f"INVESTIGATION_FAILED: {str(e)}"}

@app.get("/api/stats")
async def get_stats():
    return {"total_events": collection.count(), "threats_detected": 42, "critical_alerts": 7, "avg_response_time": "1.2s"}

@app.get("/api/raw-logs")
async def list_raw_logs():
    raw_dir = "data/raw"
    if not os.path.exists(raw_dir): return {"files": []}
    files = [f for f in os.listdir(raw_dir) if f.endswith(".gz")]
    return {"files": files}

@app.get("/api/raw-logs/{filename}")
async def preview_raw_log(filename: str):
    import gzip
    file_path = os.path.join("data/raw", filename)
    if not os.path.exists(file_path): raise HTTPException(status_code=404, detail="File not found")
    try:
        with gzip.open(file_path, 'rt') as f:
            content = [f.readline() for _ in range(20)]
        return {"content": "".join(content)}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/events")
async def preview_events():
    dataset_path = "data/datasets/events.jsonl"
    if not os.path.exists(dataset_path): return {"events": []}
    events = []
    try:
        with open(dataset_path, 'r') as f:
            for i, line in enumerate(f):
                events.append(json.loads(line))
                if i >= 49: break
        return {"events": events}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

static_path = "frontend/dist"
if os.path.exists(static_path):
    print(f"Serving static files from: {os.path.abspath(static_path)}")
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")

@app.exception_handler(404)
async def not_found(request, exc):
    index_path = os.path.join(static_path, "index.html")
    if os.path.exists(index_path): return FileResponse(index_path)
    return JSONResponse({"detail": "Not Found"}, status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
