import os
import json

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI

# -----------------------------
# LOAD ENV
# -----------------------------

load_dotenv()

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

# -----------------------------
# LLM
# -----------------------------

llm = ChatOpenAI(

    base_url="https://openrouter.ai/api/v1",

    api_key=OPENROUTER_API_KEY,

    model="openai/gpt-4.1-mini",

    max_tokens=200
)

# -----------------------------
# PARSE HUMAN TIME
# -----------------------------

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

Query:
what happened between 12:10 and 12:30

Output:
{{
    "start_time": "12:10",
    "end_time": "12:30"
}}

Query:
show ssh attacks after 14:00

Output:
{{
    "start_time": "14:00",
    "end_time": null
}}

User Query:
{user_query}

"""

    response = llm.invoke(prompt)

    parsed = response.content

    parsed = parsed.replace(
        "```json",
        ""
    ).replace(
        "```",
        ""
    ).strip()

    return json.loads(parsed)