import os
import json
import chromadb

from datetime import datetime

from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from time_parser import parse_time_query

# -----------------------------
# LOAD ENV
# -----------------------------

load_dotenv()

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

# -----------------------------
# OPENROUTER LLM
# -----------------------------

llm = ChatOpenAI(

    base_url="https://openrouter.ai/api/v1",

    api_key=OPENROUTER_API_KEY,

    model="openai/gpt-4.1-mini",

    max_tokens=500
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
# REFERENCE DATE
# -----------------------------

REFERENCE_DATE = datetime(
    2026,
    5,
    28
)

# -----------------------------
# HH:MM -> UNIX
# -----------------------------

def hhmm_to_unix(hhmm):

    dt = datetime.strptime(
        hhmm,
        "%H:%M"
    )

    combined = REFERENCE_DATE.replace(

        hour=dt.hour,

        minute=dt.minute,

        second=0
    )

    return int(
        combined.timestamp()
    )

# -----------------------------
# QUERY PARSER PROMPT
# -----------------------------

parser_prompt = ChatPromptTemplate.from_messages([

    ("system",
     """
You are a cybersecurity query parser.

Convert the user query into JSON.

Allowed event types:
- coordinated_ssh_activity
- port_scan
- traffic_spike
- rejected_activity

Map user phrases intelligently.

Examples:
"ssh attacks" -> coordinated_ssh_activity
"port scanning" -> port_scan
"traffic anomalies" -> traffic_spike
"rejected traffic" -> rejected_activity

Extract:
- event_type
- severity
- intent

Return ONLY valid JSON.

If field missing:
use null.
"""
     ),

    ("human", "{query}")
])

# -----------------------------
# USER QUERY
# -----------------------------

user_query = input(
    "\nEnter investigation query: "
)

# -----------------------------
# TIME EXTRACTION
# -----------------------------

time_data = parse_time_query(
    user_query
)

print("\n========== TIME PARSED ==========\n")

print(time_data)

# -----------------------------
# TIME -> UNIX
# -----------------------------

start_unix = None
end_unix = None

if time_data.get("start_time"):

    start_unix = hhmm_to_unix(
        time_data["start_time"]
    )

if time_data.get("end_time"):

    end_unix = hhmm_to_unix(
        time_data["end_time"]
    )

print("\n========== UNIX TIME ==========\n")

print("START:", start_unix)

print("END:", end_unix)

# -----------------------------
# PARSE QUERY
# -----------------------------

parser_chain = parser_prompt | llm

response = parser_chain.invoke({

    "query": user_query
})

parsed = response.content

# Remove markdown wrappers
parsed = parsed.replace(
    "```json",
    ""
).replace(
    "```",
    ""
).strip()

print("\n========== PARSED QUERY ==========\n")

print(parsed)

# -----------------------------
# CONVERT TO JSON
# -----------------------------

try:

    parsed_json = json.loads(parsed)

except Exception as e:

    print("\nFailed to parse JSON")

    print(e)

    exit()

# -----------------------------
# BUILD FILTERS
# -----------------------------

filters = []

# Severity
if parsed_json.get("severity"):

    filters.append({

        "severity":
        parsed_json["severity"]

    })

# Event Type
if parsed_json.get("event_type"):

    filters.append({

        "event_type":
        parsed_json["event_type"]

    })

# -----------------------------
# TIME FILTERS
# -----------------------------
if start_unix and end_unix:

    filters.append({

        "$and": [

            {
                "event_time_start": {
                    "$gte": start_unix
                }
            },

            {
                "event_time_start": {
                    "$lte": end_unix
                }
            }
        ]
    })

elif start_unix:

    filters.append({

        "event_time_start": {
            "$gte": start_unix
        }
    })

elif end_unix:

    filters.append({

        "event_time_start": {
            "$lte": end_unix
        }
    })

# -----------------------------
# FINAL WHERE FILTER
# -----------------------------

where_filter = None

if len(filters) == 1:

    where_filter = filters[0]

elif len(filters) > 1:

    where_filter = {

        "$and": filters

    }

print("\n========== WHERE FILTER ==========\n")

print(where_filter)

# -----------------------------
# VECTOR SEARCH
# -----------------------------

if where_filter is None:

    results = collection.query(

        query_texts=[user_query],

        n_results=5
    )

else:

    results = collection.query(

        query_texts=[user_query],

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

Event Type:
{meta.get('event_type')}

Severity:
{meta.get('severity')}

Source IP:
{meta.get('src_ip')}

Start Time:
{meta.get('event_time_start')}

End Time:
{meta.get('event_time_end')}

Description:
{meta.get('description')}

"""

# -----------------------------
# ANALYSIS PROMPT
# -----------------------------

analysis_prompt = f"""

You are a SOC analyst.

Analyze ONLY the retrieved events below.

Do NOT assume screenshots,
dashboards,
missing logs,
or external information.

Use ONLY provided events.

User Query:
{user_query}

Retrieved Events:
{context}

Explain:
- what happened
- attack patterns
- suspicious activity
- possible causes
- recommendations

"""

# -----------------------------
# FINAL ANALYSIS
# -----------------------------

analysis_response = llm.invoke(
    analysis_prompt
)

# -----------------------------
# OUTPUT
# -----------------------------

print("\n========== ANALYSIS ==========\n")

print(
    analysis_response.content
)