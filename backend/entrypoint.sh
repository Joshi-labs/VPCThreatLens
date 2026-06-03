#!/bin/sh

echo "Starting VPCThreatLens Initialization..."

# 1. Run embedding script to ensure ChromaDB is populated
# This creates the collection and embeds the events from JSONL
echo "Step 1: Embedding events into ChromaDB..."
python embed_events.py

# 2. Start the FastAPI server
echo "Step 2: Starting FastAPI server..."
exec uvicorn server:app --host 0.0.0.0 --port 8000
