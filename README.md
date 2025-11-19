# AstraFoundry™ - The Autonomous AI Startup Builder

> **Generate investor-ready startup blueprints in minutes, not weeks**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-34%20passing-brightgreen.svg)](tests/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Kaggle Agents Intensive Capstone - Freestyle Track**

---

## 🌟 What is AstraFoundry?

AstraFoundry is a **multi-agent autonomous system** that acts as your AI co-founder. Give it a startup domain, and it generates a complete, investor-ready blueprint including:

- 📊 **Market Research** - TAM/SAM/SOM analysis with competitor insights
- 🎨 **Product Design** - User person
This project demonstrates **multi-agent orchestration**, **tool usage**, **memory**, **stateful context**, **observability**, and **structured agent-to-agent communication**.

---

## 🚨 Problem

Launching a startup requires:
- Ideation
- Market analysis
- Competitor analysis
- Roadmapping
- Financial forecasting
- Pitch creation

Founders typically spend **50–100 hours** doing this manually. There is no single system today that can handle all these tasks end-to-end autonomously.

---

## 🚀 Solution

**AstraFoundry™** is a coordinated multi-agent pipeline that generates an entire startup plan using 6 specialized agents:

1. **Idea Agent** — Generates and scores 3-5 startup ideas
2. **Research Agent** — Performs market sizing and competitor analysis
3. **Product Designer Agent** — Creates personas, features (RICE scoring), and UX flows
4. **Roadmap Agent** — Generates 30/60/90-day engineering plans
5. **Financial Modeling Agent** — Calculates costs, unit economics, and projections
6. **Pitch Deck Agent** — Produces 10-slide investor pitch content

Each agent outputs structured JSON, which becomes context for the next agent—forming a seamless autonomous workflow.

---

## 🧠 Architecture

```
User Prompt
    ↓
[1] Idea Agent ──→ Idea Selection
    ↓
[2] Market Research Agent ──→ Competitors, SWOT, Trends
    ↓
[3] Product Designer Agent ──→ Features, Personas, UX Flows
    ↓
[4] Roadmap Agent ──→ 30/60/90 Day Engineering Plan
    ↓
[5] Finance Agent ──→ Cost Model, Unit Economics, Projections
    ↓
[6] Pitch Deck Agent ──→ 10-slide Investor Pitch
    ↓
Final Startup Blueprint (JSON + Text Summary)
```

---

## 🔑 Key Features

### ✔ Multi-Agent System
- 6 specialized agents
- Sequential execution with structured communication
- Agent-to-agent (A2A) JSON messaging
- Error handling and partial results

### ✔ Tools Integration
- **Google Search Tool** — Market research and trend validation
- **Code Execution Tool** — Financial calculations
- **Optional MCP Tools** — Extensible tool integration

### ✔ Sessions & Memory
- Session state via InMemorySessionService
- Long-term memory (Memory Bank) for user preferences
- Context compaction for large outputs
- PII filtering and credential protection

### ✔ Observability
- Structured JSON logging
- Agent latency and quality metrics
- Performance alerts (>60s threshold)
- Metrics store for analysis

### ✔ Security
- Environment-based API key management
- No credentials in logs or version control
- Input validation and sanitization
- PII filtering in memory storage

---

## 📁 Repository Structure

```
astra-foundry/
│
├── src/
│   ├── agents/
│   │   ├── base_agent.py          # Abstract base class
│   │   ├── idea_agent.py          # Idea generation & scoring
│   │   ├── research_agent.py      # Market & competitor research
│   │   ├── product_agent.py       # Product design & features
│   │   ├── roadmap_agent.py       # Engineering roadmap
│   │   ├── finance_agent.py       # Financial modeling
│   │   └── pitch_agent.py         # Pitch deck generation
│   │
│   ├── tools/
│   │   ├── google_search_adapter.py    # Search tool with retry
│   │   ├── code_execution_adapter.py   # Code execution
│   │   └── mcp_tool_adapter.py         # MCP integration
│   │
│   ├── memory/
│   │   ├── session_service.py     # Short-term session state
│   │   └── memory_bank.py         # Long-term user memory
│   │
│   ├── utils/
│   │   ├── config.py              # Configuration management
│   │   ├── logger.py              # Structured logging
│   │   └── metrics.py             # Metrics collection
│   │
│   ├── models.py                  # Data models & schemas
│   ├── orchestrator.py            # Central pipeline controller
│   └── main.py                    # CLI entry point
│
├── .kiro/specs/astra-foundry/     # Spec documents
│   ├── requirements.md
│   ├── design.md
│   └── tasks.md
│
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
├── .gitignore
└── README.md
```

---

## ▶️ How to Run

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Google Search API
GOOGLE_SEARCH_API_KEY=your_search_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
```

### 3. Run AstraFoundry

**Interactive mode:**
```bash
python src/main.py
```

**With prompt:**
```bash
python src/main.py --prompt "Build a climate-tech startup for India"
```

**With options:**
```bash
python src/main.py \
  --prompt "Create a healthcare AI platform" \
  --user-id john_doe \
  --output my_blueprints/ \
  --timeout 300
```

### 4. View Output

AstraFoundry generates two files:
- `blueprint_YYYYMMDD_HHMMSS_<run_id>.json` — Complete structured data
- `blueprint_YYYYMMDD_HHMMSS_<run_id>_summary.txt` — Human-readable summary

---

## 🧪 Example Output

```
Startup: Climate-Tech Grid Analytics

Problem: 30% power loss in developing-market grids
Solution: AI-driven grid anomaly prediction and load forecasting
Market: $3.2B TAM, 18% CAGR
Roadmap: MVP in 90 days
Revenue: SaaS per substation
Year 1 Revenue: $600,000
Pitch Deck: 10-slide outline generated
```

---

## 🏗️ Tech Stack

- **Language**: Python 3.9+
- **LLMs**: Google Gemini (via Agent Development Kit)
- **Tools**: Google Search API, Code Execution
- **State Management**: Session Service + Memory Bank
- **Orchestration**: Sequential multi-agent pipeline
- **Testing**: pytest, pytest-asyncio, pytest-mock

---

## 🧩 Agent Details

### Idea Agent
- Generates 3-5 diverse startup ideas
- Scores on novelty, feasibility, market fit (0-1 scale)
- Uses Google Search for trend validation
- Selects best idea using weighted formula: `0.4*novelty + 0.3*feasibility + 0.3*market_fit`

### Research Agent
- Estimates TAM/SAM/SOM
- Identifies 2+ competitors via search
- Generates SWOT analysis
- Provides evidence citations for all claims

### Product Designer Agent
- Creates 2+ user personas
- Generates 10-15 features with RICE scoring
- Prioritizes top 5-7 features for MVP
- Designs 2-3 core UX flows

### Roadmap Agent
- Designs system architecture
- Creates 30/60/90-day milestone plans
- Identifies risks and dependencies
- Optional MCP tool integration

### Finance Agent
- Uses code execution for precise calculations
- Calculates OPEX, CAPEX, CAC, LTV
- Generates 3 revenue scenarios (conservative, base, optimistic)
- Estimates runway in months

### Pitch Deck Agent
- Generates exactly 10 slides
- Includes talking points and visual suggestions
- Synthesizes all previous agent outputs
- Investor-focused narrative

---

## 📊 Observability & Metrics

Every run generates metrics including:
- Total execution time
- Per-agent latency
- Quality scores (idea quality, market strength, product viability)
- Tool invocation counts
- Errors and alerts

Example metrics output:
```json
{
  "run_id": "abc123",
  "total_duration_ms": 14200,
  "agent_durations": {
    "idea_agent": 3200,
    "research_agent": 4100,
    ...
  },
  "quality_scores": {
    "idea_quality": 0.79,
    "market_strength": 0.73,
    "product_viability": 0.68
  }
}
```

---

## 🔒 Security Best Practices

- ✅ API keys loaded from environment variables
- ✅ No credentials in logs (masked as `abc...xyz`)
- ✅ PII filtering (emails, phones, addresses)
- ✅ Credential detection and exclusion
- ✅ `.gitignore` protects `.env` files
- ✅ Input validation and sanitization

---

## 🧪 Testing

**Test Coverage**: 34 tests, 100% passing

Run tests with pytest:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term

# Run specific test file
pytest tests/test_agents.py -v
```

**Test Suite**:
- Number Parser: 14 tests (all formats, currencies, edge cases)
- Agents: 15 tests (personas, features, RICE, milestones, projections, slides)
- Orchestrator: 5 tests (initialization, fallbacks, validation)

---

## 🚀 Future Enhancements

- **Streaming Output**: Real-time agent progress updates
- **Multi-language Support**: Generate blueprints in different languages
- **Visual Generation**: Auto-generate pitch deck slides with images
- **Collaboration**: Multi-user sessions for team ideation
- **Export Formats**: PDF, PowerPoint, Google Docs
- **Cloud Deployment**: Deploy to Vertex AI Agent Engine or Cloud Run

---

## 📝 Example Prompts

Try these prompts to explore different industries:

```bash
# Climate Tech
python src/main.py --prompt "Build a climate-tech startup for carbon tracking"

# Healthcare
python src/main.py --prompt "Create an AI-powered telemedicine platform"

# FinTech
python src/main.py --prompt "Develop a blockchain-based payment solution for SMBs"

# EdTech
python src/main.py --prompt "Build an adaptive learning platform for K-12 students"

# AgTech
python src/main.py --prompt "Create a precision agriculture platform using IoT"
```

---

## 🏁 Conclusion

AstraFoundry demonstrates:
- ✅ End-to-end multi-agent autonomy
- ✅ Real-world tool usage (Search, Code Execution)
- ✅ Mature engineering practices (logging, metrics, testing)
- ✅ Practical, innovative application of agent technology

It is a fully working, extensible system showcasing the future of **Autonomous Startup Creation**.

---

## 📄 License

This project is created for the Kaggle Agents Intensive Capstone.

---

## 🙏 Acknowledgments

- Google & Kaggle for the Agents Intensive program
- Gemini API for powering the agents
- The open-source community for inspiration

---

**Built with ❤️ for the Kaggle Agents Intensive Capstone**
