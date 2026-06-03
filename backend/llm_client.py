import os
import time
import json
import hashlib
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

load_dotenv()

# --- CONFIGURATION ---
MODEL_NAME = "google/gemini-2.5-flash-lite" # Updated to Flash Lite
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MAX_TOKENS = 1000
CACHE_DIR = "cache"

# Ensure cache directory exists
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
        
        self.llm = ChatOpenAI(
            model=MODEL_NAME,
            openai_api_key=self.api_key,
            openai_api_base=OPENROUTER_BASE_URL,
            max_tokens=MAX_TOKENS,
            temperature=0
        )
        
        self.embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")

    def _get_cache_path(self, prompt):
        hash_val = hashlib.md5(prompt.encode()).hexdigest()
        return os.path.join(CACHE_DIR, f"{hash_val}.json")

    def chat(self, prompt, use_cache=True):
        if use_cache:
            cache_path = self._get_cache_path(prompt)
            if os.path.exists(cache_path):
                print(f"DEBUG: Cache hit for query. Waiting 3 seconds...")
                time.sleep(3) # Simulate processing as requested
                with open(cache_path, "r") as f:
                    return json.load(f)["content"]

        # Call API
        response = self.llm.invoke(prompt)
        content = response.content

        if use_cache:
            with open(cache_path, "w") as f:
                json.dump({"prompt": prompt, "content": content}, f)
        
        return content

    def get_embeddings(self):
        return self.embeddings

# Singleton instance
client = LLMClient()
