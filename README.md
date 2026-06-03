# 🛡️ VPCThreatLens: AI-Powered SOC Analyst for Disaster Response

[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen?style=for-the-badge)](https://threat-lens.vpjoshi.in/)
[![Portfolio](https://img.shields.io/badge/Portfolio-vpjoshi.in-blue?style=for-the-badge)](https://vpjoshi.in)

**VPCThreatLens** is an advanced, AI-driven Security Operations Center (SOC) analysis tool specifically engineered for high-velocity disaster response and threat hunting within AWS environments. It transforms raw, cryptic VPC Flow Logs into actionable security intelligence using Agentic RAG (Retrieval-Augmented Generation).

---

## 🚀 The Architecture: Real-Time Security Intelligence

VPCThreatLens is tested and proven on a robust cloud-native pipeline:
`AWS VPC Flow Logs` ➡️ `S3` ➡️ `Event Notifications` ➡️ `EventBridge` ➡️ `Webhook` ➡️ `EC2/K8s` ➡️ `Real-time AI Embedding`

### Key Features:
- **Agentic RAG Chain**: Utilizes a specialized agent that understands security context and retrieves relevant network events from a vector store.
- **Gemini 2.0 Flash Lite Integration**: Optimized for speed and precision using the latest LLM models via OpenRouter.
- **Smart Caching Layer**: High-performance local caching with simulated processing delays to optimize API usage and responsiveness.
- **Lightweight Vector Search**: Powered by **FastEmbed** and **ChromaDB** for rapid semantic retrieval without the bloat of heavy deep-learning frameworks.
- **Disaster Analysis Focus**: Specifically tuned to identify:
    - Coordinated SSH brute-force activity.
    - Port scanning and reconnaissance patterns.
    - Traffic spikes and data exfiltration anomalies.
    - Rejected activity clusters.

---

## 🏗️ Deployment

VPCThreatLens is containerized and ready for production-grade orchestration.

### 🐳 Running with Docker

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Joshi-labs/VPCThreatLens.git
   cd VPCThreatLens
   ```

2. **Configure Environment:**
   Create a `.env` file in the root directory:
   ```env
   OPENROUTER_API_KEY=your_key_here
   ```

3. **Build and Start:**
   ```bash
   docker build -t vpcthreatlens .
   docker run -p 8000:8000 vpcthreatlens
   ```

### ☸️ Running on Kubernetes

The system is deployed in a K8s cluster for high availability.

1. **Create Secrets:**
   ```bash
   kubectl create secret generic threatlens-secrets \
     --from-literal=OPENROUTER_API_KEY='your_api_key' \
     -n apps-prod
   ```

2. **Apply Manifests:**
   ```bash
   kubectl apply -f k8s/
   ```

---

## 📥 Data Management

### Where to place your logs?
Place your raw AWS VPC Flow Logs (`.log.gz`) in the following directory structure within the container or backend folder:
- `backend/data/raw/`: Place your raw `.log.gz` files here.

### Generating Security Events
VPCThreatLens includes a built-in event generator to simulate or process logs into enriched security datasets.
```bash
python backend/event_generator.py
```
This will populate `backend/data/datasets/window_events.jsonl`, which is then used by the embedding engine.

### Re-indexing the Vector Store
To re-embed your data after adding new logs:
```bash
python backend/embed_events.py
```

---

## 🛠️ Project Structure
- `/backend`: FastAPI server, LLM Client, and Agentic RAG logic.
- `/frontend`: React + TypeScript dashboard.
- `/k8s`: Kubernetes deployment and service manifests.
- `/data`: Storage for raw logs and processed datasets.

---

## 👨‍💻 About the Author

Developed with ❤️ by **V P Joshi**.

- **Portfolio**: [vpjoshi.in](https://vpjoshi.in)
- **Live Project**: [threat-lens.vpjoshi.in](https://threat-lens.vpjoshi.in/)

*VPCThreatLens is not just a tool; it's your AI-powered SOC companion for the modern cloud.*
