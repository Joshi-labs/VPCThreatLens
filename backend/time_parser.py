import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load env
load_dotenv()

# Initialize LLM with OpenRouter
llm = ChatOpenAI(
    model="google/gemini-2.5-flash-lite",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0
)

def parse_time_query(user_query):
    prompt = f"""
You are a time extraction engine.
Extract:
- start_time
- end_time
from the query.
Return ONLY valid JSON.

Time format:
HH:MM

Examples:
Query: what happened between 12:10 and 12:30
Output: {{"start_time": "12:10", "end_time": "12:30"}}

Query: show ssh attacks after 14:00
Output: {{"start_time": "14:00", "end_time": null}}

User Query: {user_query}
"""
    response = llm.invoke(prompt)
    content = response.content.strip()
    
    # Simple JSON extraction cleanup
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()
        
    try:
        return json.loads(content)
    except:
        return {"start_time": None, "end_time": None}
