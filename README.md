# ⚖️ Multi-Act Legal RAG using Endee Vector Database

An AI Legal Assistant that performs **semantic search across multiple Indian legal Acts** using **Endee Vector Database**, and generates structured legal analysis using **Retrieval Augmented Generation (RAG)**.

This project demonstrates a **real, production-style RAG system** where **vector search is the core engine** powering legal reasoning.

---

## 🚀 What this project demonstrates

This project fulfills the Endee Labs assignment requirement:

> *“Develop a well-defined AI/ML project using Endee as the vector database. Demonstrate Semantic Search / RAG where vector search is core.”*

### This project clearly implements:

- ✅ Semantic Search over legal sections using embeddings + Endee
- ✅ Retrieval Augmented Generation (RAG)
- ✅ Multi-index vector retrieval (one index per legal Act)
- ✅ Practical AI application (Legal assistant)
- ✅ Clean separation of vector store (Endee) and document store (JSON)
- ✅ Streamlit UI for interaction

---

## 🧠 Problem this solves

Indian legal queries often require searching across:

- Bharatiya Nyaya Sanhita (BNS)
- Indian Penal Code (IPC)
- Criminal Procedure Code (CrPC)
- Civil Procedure Code (CPC)
- Bharatiya Sakshya Adhiniyam (BSA)

Manual lookup is slow and keyword search fails to find contextually relevant sections.

This system uses **semantic vector search** to retrieve the **most relevant legal sections** and uses an LLM to produce structured legal analysis.

---

## 🏗️ Architecture Overview (RAG Pipeline)


User Query
↓
MiniLM Embedding
↓
Endee Vector Search (per Act index)
↓
Top Section IDs
↓
JSON Chunk Lookup (full legal text)
↓
LLM Legal Analysis
↓
Streamlit UI Output

---

## 🔥 Why Endee is core here

- Endee is used as a **high-performance HNSW vector index**
- One index per legal Act
- All retrieval happens through Endee `index.query()`
- LLM is never called without first retrieving context from Endee

> Endee is the foundation of this system.

---

## 📂 Project Structure


legal-rag-using-endee/
│
├── app/
│ ├── chat_app.py
│ ├── retriever.py
│ ├── endee_client.py
│ ├── chunk_lookup.py
│ ├── agent_router.py
│ ├── scenario_processor.py
│ └── concept_expander.py
│
├── scripts/
│ └── embed_to_endee.py
│
├── data/
│ └── *_chunks.json
│
├── docker-compose.yml
├── requirements.txt
└── README.md

---

## 📚 Data Preparation

Each legal Act is converted into structured chunks:

```json
{
  "id": "bns_303_12",
  "section": "303",
  "section_display": "Section 303",
  "heading": "Theft",
  "chapter": "Offences against property",
  "content": "Full legal text..."
}


🧩 Key Components Explained
embed_to_endee.py
  Converts each section into embeddings
  Inserts vectors into Endee indexes (bns_sections, ipc_sections, etc.)
  Stores only metadata in Endee (not full text)
endee_client.py
  Uses official Endee Python SDK:
  Create index
  Insert vectors
  Query vectors
chunk_lookup.py
  Loads all JSON chunks into memory
  Maps Endee result IDs → full legal text
agent_router.py
  Classifies query as direct / scenario / section
  Detects which Acts to search
concept_expander.py
  Expands legal terms (e.g., theft → larceny, stealing)
  Improves semantic recall
retriever.py
  Calls Endee search
  Fetches full text from JSON
  Boosts definition sections when needed
chat_app.py
  Streamlit UI
  Sends retrieved context to LLM
  Displays sections grouped by Act

🐳 Step 1 — Run Endee
docker compose up -d

Visit dashboard:
http://localhost:8080

🧪 Step 2 — Install dependencies
pip install -r requirements.txt


🧠 Step 3 — Embed legal data into Endee
python -m scripts.embed_to_endee

This populates all Act indexes.

💬 Step 4 — Run the app
streamlit run app/chat_app.py


🧠 Example Queries
What is punishment for theft?
Explain Section 302 IPC
A mob vandalized property during protest — what offenses apply?
What evidence is admissible in court?

🎯 Why this is a strong Endee use case
Feature
Implementation
Semantic Search
MiniLM embeddings + Endee cosine search
Multi-index vector DB
One index per legal Act
Real domain corpus
Structured Indian legal sections
RAG
Retrieved sections → LLM reasoning
Query intelligence
Router + synonym expansion
Production UI
Streamlit interface


🧠 RAG Definition (as implemented)
Retrieve → Endee vector search
Augment → Legal sections as context
Generate → LLM legal explanation

📦 requirements.txt
streamlit
openai
sentence-transformers
python-dotenv
endee
tqdm


🧭 How this satisfies the assignment
Assignment Requirement
Implementation
Use Endee as vector DB
All retrieval via Endee SDK
Demonstrate Semantic Search
Yes
Demonstrate RAG
Yes
Practical AI project
Legal multi-act assistant
GitHub hosted project
This repository
Clean README
This document


📌 Important Design Decision
Endee is used only for vectors.
JSON is the document store.
This matches best practices for scalable RAG systems.

👨‍💻 Author
Engineering project demonstrating applied RAG using Endee Vector Database.


