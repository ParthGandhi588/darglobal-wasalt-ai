---
title: DarGlobal & Wasalt Real Estate AI
emoji: 🏛️
colorFrom: yellow
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
---

# 🏛️ DarGlobal & Wasalt Real Estate AI Chatbot

[![Docker Image](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Streamlit App](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-Free%20Tier-6366F1)](https://openrouter.ai/)

An intelligent, full-stack AI Real Estate Advisory Chatbot developed for the **Junior AI Engineer – Applied AI** recruitment technical assessment for **DarGlobal**.

The application combines publicly scraped data from **DarGlobal** and **Wasalt**, indexes the portfolio into a local high-performance vector database, and uses Retrieval-Augmented Generation (RAG) powered by free models through **OpenRouter** to deliver authoritative real estate guidance, property comparisons, and verified direct links.

---

## 🌟 Key Capabilities

1. **Comprehensive Knowledge Base**:
   - **DarGlobal International Luxury Flagships**: *Tierra Viva by Automobili Lamborghini* (Spain), *DaVinci Tower by Pagani* (Dubai), *The Astera by Aston Martin* (Ras Al Khaimah), *AIDA by Trump & Fendi Casa* (Oman), *Trump International Hotel & Tower Dubai*, *Trump Plaza & Trump Tower Jeddah*, *Les Vagues by Elie Saab* (Qatar), and *Neptune Villas by Mouawad* (Riyadh).
   - **DarGlobal Corporate & Financial Intelligence**: London Stock Exchange listing (**LSE: DAR**), CEO Ziad El Chaar, 17.3% ROE, and core investment philosophies (**Return on Ego - ROE** & **Return on Legacy - ROL**).
   - **Dar Al Arkan Master Communities**: *Rayana Wadi Safar Diriyah*, *Upside Living Villas by Versace Home*, *Amaya Jeddah*, *Shams Ar-Riyadh*, *Parisiana*, etc.
   - **Wasalt Saudi Real Estate Portal**: 294+ real property listings across Riyadh, Jeddah, Al Khobar, Dammam, Makkah, and Madinah with exact prices in SAR, configurations, areas, and direct listing links.
   - **Market FAQs**: Saudi real estate buying, leasing, registration, and foreign ownership guidelines.

2. **Retrieval-Augmented Generation (RAG)**:
   - Embeddings: Local ONNX-optimized `BAAI/bge-small-en-v1.5` embeddings via **FastEmbed** (zero API cost, ultra-low latency).
   - Vector Database: **ChromaDB** with cosine distance metric.
   - Semantic + Metadata Filtering: Filter by developer / portal (`DarGlobal`, `Wasalt`, `All`).

3. **OpenRouter Free Tier Integration**:
   - Connects to high-performance free LLMs on OpenRouter:
     - `meta-llama/llama-3.3-70b-instruct:free`
     - `google/gemini-2.0-flash-exp:free`
     - `qwen/qwen-2.5-72b-instruct:free`
     - `meta-llama/llama-3.1-8b-instruct:free`
     - `mistralai/mistral-7b-instruct:free`
   - Automated model failover if any individual free model encounters rate limiting.
   - Interactive key configuration in the application sidebar or via `.env`.

4. **Production-Ready & Containerized**:
   - Packaged with **Docker** and **Docker Compose**.
   - Lean container footprint with pre-indexed vector store (boots in < 5 seconds).

---

## 🏗️ Architecture

```
                   ┌───────────────────────────────────────────┐
                   │               Public Sources              │
                   │  - DarGlobal (darglobal.co.uk)            │
                   │  - Wasalt (wasalt.com)                    │
                   │  - Dar Al Arkan (daralarkan.com)          │
                   └─────────────────────┬─────────────────────┘
                                         │ Scrape & Extract
                                         ▼
                   ┌───────────────────────────────────────────┐
                   │    Unified Knowledge Base (368 Assets)    │
                   │   data/processed/unified_knowledge_base   │
                   └─────────────────────┬─────────────────────┘
                                         │ FastEmbed (BGE-Small)
                                         ▼
                   ┌───────────────────────────────────────────┐
                   │        ChromaDB Vector Store (Disk)       │
                   │              data/chroma_db/              │
                   └─────────────────────┬─────────────────────┘
                                         │ Semantic Search
                                         ▼
   ┌──────────────────────┐       ┌────────────────────────────┐
   │    User Query        │──────►│    RAG Engine (Top-k Docs) │
   └──────────────────────┘       └──────────────┬─────────────┘
                                                 │ Context + Prompt
                                                 ▼
   ┌──────────────────────┐       ┌────────────────────────────┐
   │ Streamlit Luxury UI  │◄──────│   OpenRouter Free Tier     │
   │ (Streaming Response) │       │ (Llama 3.3 70B / Gemini)   │
   └──────────────────────┘       └────────────────────────────┘
```

---

## 🚀 Quick Start (Local Setup)

### Option A: Using Docker (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd DarGlobal
   ```

2. **Configure Environment Variable**:
   ```bash
   cp .env.example .env
   # Add your OPENROUTER_API_KEY inside .env
   ```

3. **Run with Docker Compose**:
   ```bash
   docker compose up --build
   ```

4. Open your browser at **`http://localhost:8501`**.

---

### Option B: Using Python Virtual Environment

1. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional) Re-run Scraper & Vector Indexing**:
   ```bash
   python scripts/scrape_wasalt.py
   python scripts/scrape_darglobal.py
   python scripts/scrape_daralarkan_portfolio.py
   python scripts/prepare_dataset.py
   python scripts/build_vectorstore.py
   ```
   *(Note: The repository already includes the pre-scraped and indexed database inside `data/chroma_db/`)*

4. **Launch the Streamlit app**:
   ```bash
   streamlit run src/app.py --server.port=8501
   ```

---

## ☁️ Deployment Instructions

### Deploy to Hugging Face Spaces (Docker Runtime)
1. Create a new Space on [Hugging Face](https://huggingface.co/new-space).
2. Select **Docker** as the Space SDK and choose **Blank** template.
3. Push this repository to your Space repository:
   ```bash
   git remote add space https://huggingface.co/spaces/<your-username>/<space-name>
   git push space main
   ```
4. In Space Settings -> **Variables and Secrets**, add `OPENROUTER_API_KEY`.
5. Hugging Face Spaces will automatically build the `Dockerfile` and expose your chatbot on a public HTTPS URL.

### Deploy to Render
1. Create a **New Web Service** from your GitHub repo.
2. Select **Docker** as the environment.
3. Under Environment Variables, add `OPENROUTER_API_KEY`.
4. Render will deploy and provide your working public URL.

---

## 💬 Sample Test Queries

Try querying the bot with these prompts:
- *"Tell me about Tierra Viva Lamborghini villas in Spain: prices, specifications, and villa types."*
- *"What are the prices, villa types, and residency perks for AIDA Trump Golf and Fendi Casa villas in Oman?"*
- *"Show me luxury apartments for sale in Riyadh from Wasalt, including price in SAR, area, and district."*
- *"Explain the DaVinci Tower by Pagani in Dubai: location, amenities, and interior finishes."*
- *"What is DarGlobal's background, London Stock Exchange listing, CEO, and Return on Ego (ROE) philosophy?"*
- *"What is Rayana in Wadi Safar Diriyah and what Trump amenities are planned there?"*

---

## 📁 Repository Structure

```
.
├── data/
│   ├── raw/                       # Scraped JSON files (DarGlobal, Wasalt, Dar Al Arkan)
│   ├── processed/                 # Unified knowledge base JSON
│   └── chroma_db/                 # Persistent ChromaDB vector database
├── scripts/
│   ├── scrape_wasalt.py           # Scrapes Wasalt properties & FAQs
│   ├── scrape_darglobal.py        # Extracts DarGlobal projects & corporate profile
│   ├── scrape_daralarkan_portfolio.py # Scrapes Dar Al Arkan master communities
│   ├── prepare_dataset.py         # Transforms and merges all assets into unified schema
│   └── build_vectorstore.py       # Embeds and builds ChromaDB vector store
├── src/
│   ├── __init__.py
│   ├── app.py                     # Streamlit frontend with luxury styling & filters
│   ├── rag_engine.py              # Semantic search retrieval & prompt formatting
│   └── openrouter_client.py       # OpenRouter LLM client with automated model fallback
├── Dockerfile                     # Optimized production Dockerfile
├── docker-compose.yml             # Single-command local orchestration
├── requirements.txt               # Pinned Python dependencies
├── .env.example                   # Environment configuration template
└── README.md                      # Complete system documentation
```
