# ⚖️ Multi-Act Legal RAG System

An advanced AI-powered legal research assistant for Indian law, featuring multi-act analysis, intelligent query routing, and semantic search capabilities across BNS, IPC, CrPC, CPC, and BSA.

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Docker](https://img.shields.io/badge/docker-enabled-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## 🌟 Features

### **Core Capabilities**
- 🧠 **Multi-Act Intelligence**: Seamlessly searches across 5 major Indian legal acts
- 🎯 **Query Classification**: Automatically detects query type (section-specific, scenario-based, or conceptual)
- 🔍 **Hybrid Retrieval**: Combines exact section lookup with semantic vector search
- 📊 **Confidence Scoring**: Multi-factor reliability indicators for all responses
- 🌐 **Scenario Analysis**: Structured extraction of legal elements from narrative descriptions
- 🔄 **Concept Expansion**: Legal synonym and hierarchical relationship mapping

### **Technical Features**
- ⚡ **Endee Vector Database**: High-performance similarity search with INT8 quantization
- 🤖 **GPT-3.5 Integration**: Advanced legal reasoning and analysis
- 🏗️ **Production-Ready**: Fully containerized with Docker
- 📈 **Scalable Architecture**: Modular design for easy extensions

---

## 📋 Table of Contents

- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [System Components](#-system-components)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface                          │
│                   (Streamlit Web App)                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                 Intelligence Layer                          │
├─────────────────────────────────────────────────────────────┤
│  • Agent Router     (Query Classification)                  │
│  • Scenario Processor (Element Extraction)                  │
│  • Concept Expander  (Legal Synonyms)                       │
│  • Confidence Scorer (Reliability Metrics)                  │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  Retrieval Layer                            │
├─────────────────────────────────────────────────────────────┤
│  • Section Lookup    (Exact Match)                          │
│  • Vector Search     (Semantic Similarity)                  │
│  • Cross-References  (Related Sections)                     │
│  • Definition Booster (Base Concepts)                       │
└───────┬───────────────────────────────────┬─────────────────┘
        │                                   │
        ▼                                   ▼
┌──────────────────┐            ┌──────────────────────┐
│  Endee Vector DB │            │  JSON Chunk Lookup   │
│  (Embeddings)    │            │  (Full Legal Text)   │
└──────────────────┘            └──────────────────────┘
        │                                   │
        └───────────────┬───────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    LLM Analysis Layer                       │
│              (GPT-3.5 with Legal Prompts)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### **Prerequisites**
- Docker Desktop (20.10+)
- 4GB RAM minimum
- OpenAI API Key

### **30-Second Setup**

```bash
# 1. Clone the repository
git clone https://github.com/rsagar1903/legal-rag-using-endee.git
cd legal-rag-using-endee

# 2. Configure API key
cp .env.example .env
nano .env  # Add your OpenAI API key

# 3. Start the system
docker-compose up -d --build

# 4. Build ID maps (first time only - in a new terminal)
docker-compose exec app python scripts/build_id_maps.py

# 5. Run embeddings (first time only - takes 5-10 minutes)
docker-compose exec app python scripts/embed_to_endee.py

# 6. Open browser
# http://localhost:8501
```

---

## 💻 Installation

### **Detailed Setup Instructions**

#### **Step 1: Clone Repository**
```bash
git clone https://github.com/rsagar1903/legal-rag-using-endee.git
cd legal-rag-using-endee
```

#### **Step 2: Configure Environment**
```bash
# Copy environment template
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```env
OPENAI_API_KEY=sk-your-actual-openai-key-here
```

#### **Step 3: Start Docker Services**
```bash
docker-compose up -d --build
```

This will:
- Pull/build Docker images
- Start Endee vector database
- Start the Streamlit application
- Expose UI at `http://localhost:8501`

#### **Step 4: Initialize Data (First Time Only)**

**Open a new terminal** and run:

```bash
# Step 4a: Build ID maps (creates fast lookup files)
docker-compose exec app python scripts/build_id_maps.py
```

Expected output:
```
Building ID map for BNS
✅ Created data/bns_id_map.json
   Total entries: 2765

Building ID map for IPC
✅ Created data/ipc_id_map.json
   Total entries: 1890
...
```

```bash
# Step 4b: Embed legal acts into vector database
docker-compose exec app python scripts/embed_to_endee.py
```

Expected output:
```
Processing BNS...
✅ Created index: bns_sections
📄 Loaded 2765 chunks
✅ BNS complete: 2765/2765 chunks embedded
...
✅ ALL ACTS EMBEDDED SUCCESSFULLY!
```

This takes **5-10 minutes** depending on your machine.

#### **Step 5: Verify Installation**

```bash
# Verify vectors were embedded
docker-compose exec app python scripts/verify_vectors.py
```

Expected output:
```
Checking bns_sections...
  ✅ bns_sections: Found 5 results
  
Checking ipc_sections...
  ✅ ipc_sections: Found 5 results
...
✅ All indices verified - vectors are present!
```

#### **Step 6: Access the Application**

Open your browser and go to:
```
http://localhost:8501
```

You should see the **Multi-Act Legal Advisor** interface!

---

## 📖 Usage

### **Query Examples**

#### **1. Section-Specific Queries**

```
"What is section 303 of BNS?"
"Explain IPC section 378"
"BNS 270 meaning"
```

**Response:**
- ✅ Exact section text
- ✅ Chapter/heading context
- ✅ Related provisions
- 🟢 Confidence: HIGH (95%+)

---

#### **2. Conceptual Queries**

```
"What is the punishment for theft?"
"Legal consequences of public nuisance"
"How is evidence presented in court?"
```

**Response:**
- ✅ Applicable sections from multiple acts
- ✅ Legal analysis
- ✅ Potential defenses
- 🟡 Confidence: MEDIUM-HIGH (65-85%)

---

#### **3. Scenario-Based Queries**

```
"A person stole my bike and sold it to someone else"
"My neighbor blocks my driveway every day causing inconvenience"
"Someone threatened me with violence during a property dispute"
```

**Response:**
- ✅ All applicable sections
- ✅ Multi-act analysis (BNS + IPC + CrPC)
- ✅ Procedural guidance
- ✅ Defenses and considerations
- 🟢 Confidence: HIGH (85%+)

---

## 🔧 System Components

### **Directory Structure**

```
legal-rag-using-endee/
├── app/
│   ├── agent_router.py           # Query classification
│   ├── chat_app.py                # Main Streamlit app
│   ├── chunk_lookup.py            # ID-based text retrieval
│   ├── concept_expander.py        # Legal synonym expansion
│   ├── confidence_scorer.py       # Reliability scoring
│   ├── cross_references.py        # Related section expansion
│   ├── error_handler.py           # Centralized error handling
│   ├── reranker.py                # Cross-encoder precision
│   ├── retriever.py               # Vector search orchestration
│   ├── scenario_processor.py      # Element extraction
│   └── section_retrieval_fix.py   # Exact section lookup
│
├── data/
│   ├── bns_chunks.json            # Bharatiya Nyaya Sanhita
│   ├── ipc_chunks.json            # Indian Penal Code
│   ├── crpc_chunks.json           # Criminal Procedure Code
│   ├── cpc_chunks.json            # Civil Procedure Code
│   ├── bsa_chunks.json            # Bharatiya Sakshya Adhiniyam
│   ├── bns_id_map.json            # Fast lookup maps
│   ├── ipc_id_map.json
│   ├── crpc_id_map.json
│   ├── cpc_id_map.json
│   └── bsa_id_map.json
│
├── scripts/
│   ├── build_id_maps.py           # Create lookup files
│   ├── embed_to_endee.py          # Embed acts to vector DB
│   ├── verify_vectors.py          # Check embeddings
│   └── test_endee_direct.py       # Direct Endee test
│
├── docker-compose.yml             # Docker services config
├── Dockerfile                     # App container definition
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
├── start.sh                       # Start script
├── stop.sh                        # Stop script
└── README.md                      # This file
```

---

## 🐛 Troubleshooting

### **1. No Vectors in Endee**

**Symptoms:** All queries return "couldn't find information", LOW confidence

**Solution:**
```bash
# Re-run embedding
docker-compose exec app python scripts/embed_to_endee.py

# Verify
docker-compose exec app python scripts/verify_vectors.py
```

---

### **2. OpenAI API Error**

**Symptoms:** "Error generating response", authentication failure

**Solution:**
```bash
# Check .env file
cat .env | grep OPENAI_API_KEY

# Should show: OPENAI_API_KEY=sk-...

# If wrong/missing, edit
nano .env

# Restart app
docker-compose restart app
```

---

### **3. Port Already in Use**

**Symptoms:** "Bind for 0.0.0.0:8501 failed: port is already allocated"

**Solution:**
```bash
# Edit docker-compose.yml
# Change: "8501:8501" to "8502:8501"

# Restart
docker-compose down
docker-compose up -d

# Access at http://localhost:8502
```

---

### **4. Low Confidence on Section Queries**

**Symptoms:** "What is section 303 of BNS" returns LOW confidence

**Solution:**
```bash
# Check if section fix is present
docker-compose exec app ls app/section_retrieval_fix.py

# If missing, copy it
docker cp section_retrieval_fix.py legal-rag-app:/app/app/

# Restart
docker-compose restart app
```

---

### **5. Docker Container Exits**

**Symptoms:** Container starts then immediately stops

**Solution:**
```bash
# Check logs
docker-compose logs app

# Common causes:
# - Missing .env file → Copy .env.example to .env
# - Invalid API key → Check .env
# - Python error → Check logs for traceback

# Rebuild if needed
docker-compose build --no-cache
docker-compose up -d
```

---

## 🔌 Useful Commands

### **Docker Management**

```bash
# Start services
./start.sh
# or
docker-compose up -d

# Stop services
./stop.sh
# or
docker-compose down

# View logs (live)
docker-compose logs -f

# View logs for specific service
docker-compose logs -f app

# Restart app only
docker-compose restart app

# Rebuild image
docker-compose build --no-cache app

# Enter app container
docker-compose exec app bash

# Remove everything (including volumes)
docker-compose down -v
```

---

### **Embedding Management**

```bash
# Build ID maps
docker-compose exec app python scripts/build_id_maps.py

# Embed all acts
docker-compose exec app python scripts/embed_to_endee.py

# Verify embeddings
docker-compose exec app python scripts/verify_vectors.py

# Re-embed specific act (if needed)
docker-compose exec app python -c "
from scripts.embed_to_endee import embed_act
embed_act('bns', 'data/bns_chunks.json', rebuild=True)
"
```

---

### **Testing**

```bash
# Test direct Endee retrieval
docker-compose exec app python scripts/test_endee_direct.py

# Run debug UI (detailed pipeline view)
docker-compose exec app streamlit run app/chat_app_debug.py

# Access debug UI at http://localhost:8501
```

---

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| **Query Latency** | 2-5 seconds |
| **Embedding Time** | 5-10 minutes (all acts) |
| **Memory Usage** | ~2GB |
| **Accuracy (sections)** | 95%+ |
| **Accuracy (concepts)** | 85%+ |
| **Vector Dimensions** | 384 |
| **Total Legal Sections** | ~6,500 |

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- **Endee Labs** for the high-performance vector database
- **OpenAI** for GPT-3.5 API
- **Sentence Transformers** for embedding models
- **Indian Legal Framework** for structured legal data

---

## 📞 Support

For issues or questions:

- 🐛 **Report bugs:** [GitHub Issues](https://github.com/rsagar1903/legal-rag-using-endee/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/rsagar1903/legal-rag-using-endee/discussions)

---

**Made with ⚖️ for Indian Legal Research**
