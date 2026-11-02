# 🎸 Empório da Música — AI Customer Service Chatbot

An AI-powered customer service chatbot for **Empório da Música**, a fictional musical instruments store in Campo Grande, MS (Brazil). Built as a technical case for the AI Engineer position at Artefact.

## 🎯 Overview

The chatbot assists customers via text messages, handling:
- **Product queries**: catalog browsing, pricing, availability, specifications
- **Order tracking**: status, tracking codes, delivery estimates (with LGPD-compliant customer identification)
- **Store policies**: returns, warranties, payment options, business hours
- **Active promotions**: current discounts and promotional prices
- **Out-of-scope questions**: polite redirection when the query falls outside the store's domain

## 🏗️ Architecture & Technical Decisions

### Agent Approach: Hybrid Function Calling

The agent uses a **hybrid architecture** that separates two types of knowledge:

| Knowledge Type | How It's Accessed | Rationale |
|---|---|---|
| **Structured data** (products, orders, promotions, customers) | Function calling — the model decides which tool to invoke | Data changes frequently; queries need filtering, joins, and calculations |
| **Policies** (returns, payments, warranties, business hours) | Full text in the system prompt | The policy manual is ~4,000 tokens (~8 pages) — small enough to fit entirely in context without retrieval overhead |

**Why not RAG?** The policy document is small enough that embedding + vector search would add infrastructure complexity (embeddings model, vector DB) without proportional benefit. If the manual grew to hundreds of pages, RAG would be justified.

**Why not a SQL agent?** While the data could be queried via SQL, a direct SQL agent introduces risks (malformed queries, injection) and requires heavier compute. Function calling with pre-built, validated Python functions is safer and more predictable for a prototype.

### Model: Gemini Flash-Lite (Google AI Studio)

| Criterion | Choice | Reason |
|---|---|---|
| Model | `gemini-2.0-flash-lite` | Free tier, native function calling support |
| Provider | Google AI Studio | Zero cost; evaluator only needs a free API key |
| Alternative considered | GPT-4o-mini, Claude Haiku | Good quality but not free |
| Alternative considered | Local model (Ollama) | Zero API cost but harder to reproduce |

### Interface: Streamlit Chat Interface

The project features a clean, responsive conversational chat interface powered by Streamlit:
- **Focused Chat Experience**: Directly connects the customer to the virtual music concierge.
- **Session History**: Preserves context across multi-turn interactions.
- **Real-Time Data Grounding**: Answers are dynamically grounded in the store's inventory, promotions, and orders via tool calling.

### Conversation History: Last 8 Messages

The agent maintains a sliding window of the last 8 messages (4 user + 4 assistant turns) in the Streamlit session state. This covers the typical 5-step service flow (greeting → understanding → lookup → response → closing) without exceeding the model's efficient context range.

### Data Treatment

| Transformation | Reason |
|---|---|
| `specs` JSON parsing | The `specs` column stores JSON as a string; parsed via `json.loads()` on load |
| Numeric type enforcement | `price_brl` as float, `stock_quantity` as int, `discount_percent` as float |
| Date parsing | `order_date` parsed as datetime for date arithmetic (return eligibility) |
| Active promotion filtering | Only `is_active == 1` promotions are surfaced; historical promotions are excluded |
| Phone normalization | Digits-only comparison for customer lookup (handles formatting variations) |

### Customer Identification (LGPD Compliance)

- **General queries** (products, prices, policies): no identification required
- **Order queries** (status, returns): the agent asks for the customer's phone number or email before retrieving any order data
- This mirrors real-world WhatsApp behavior (where the phone number is inherently available) and satisfies LGPD requirements without excessive friction

### Reference Date for Policy Calculations

The `REFERENCE_DATE` environment variable allows setting a custom date for testing return/warranty eligibility. If unset, the system uses `datetime.now()`. This is necessary because all sample orders date from Oct 2025 – Mar 2026, and would be outside the 7-day return window under the current date.

## 📁 Project Structure

```
emporio-da-musica-chatbot/
├── app.py                  # Streamlit chat interface
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore
├── data/                   # Store data (CSVs + policy PDF)
│   ├── desafio_tecnico_ai_eng - categories.csv
│   ├── desafio_tecnico_ai_eng - customers.csv
│   ├── desafio_tecnico_ai_eng - orders.csv
│   ├── desafio_tecnico_ai_eng - order_items.csv
│   ├── desafio_tecnico_ai_eng - products.csv
│   ├── desafio_tecnico_ai_eng - promotions.csv
│   └── políticas_da_loja.pdf
├── src/
│   ├── __init__.py
│   ├── config.py           # Configuration & environment variables
│   ├── data_loader.py      # Data loading, cleaning & DataStore class
│   ├── tools.py            # Agent tools (function calling implementations)
│   └── agent.py            # Chatbot agent with Gemini integration
├── docs/
│   ├── relacao_instrumentos.md   # Reference list of all 65 products
│   └── registro_agentes.md      # Agent activity log
├── tests/
│   ├── test_order_return_eligibility.py  # Return window calculation tests
│   └── test_realtime_stock_sync.py       # Real-time stock sync tests
└── examples/               # Example conversations (5)
    ├── 01_catalog_query.md
    ├── 02_store_info.md
    ├── 03_price_and_promotion.md
    ├── 04_return_policy.md
    └── 05_out_of_scope.md
```

## 🚀 How to Run

### Prerequisites

- Python 3.10+
- A free [Google AI Studio](https://aistudio.google.com/) API key

### Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/emporio-da-musica-chatbot.git
cd emporio-da-musica-chatbot

# Create and activate a virtual environment (recommended)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Running

```bash
streamlit run app.py
```

The chatbot will open in your browser at `http://localhost:8501`.

### Testing with a Custom Reference Date

To test return/warranty scenarios with the sample data:

```bash
# In .env, set:
REFERENCE_DATE=2026-03-25
```

This places the reference date near the most recent orders, allowing demonstration of return eligibility.

## ⚠️ Assumptions & Ambiguities

The following ambiguities were identified in the provided materials. For each, a reasonable assumption was adopted:

| ID | Ambiguity | Assumption |
|---|---|---|
| I-01 | Product 136 (Ibanez Bass 2X) is discontinued but has stock = 13 | Positive stock does not imply availability. The agent treats it as discontinued and suggests alternatives. |
| I-02 | Product 130 (Kala KA-ABP-CTG) has status "coming_soon" but appears in a delivered order (#3) | Test data inconsistency. The agent treats the product according to its current status. |
| I-03 | Product 96 (Giannini GF-3D) is "active" with stock = 0 | Temporarily out of stock. The agent informs and suggests alternatives. |
| I-04 | Two different phone numbers in the policy manual: (67) 3341-4444 and (67) 3321-4500 | The first is the store's landline; the second is the WhatsApp number. |
| I-05 | Payment table says "minimum installment R\$100" but detailed rules specify ranges | The detailed rules (3x, 4-6x, 7-12x) are used as the primary source. |
| I-06 | Case instructions say "reply to the email with the repo link"; HR email mentions Google Forms + PDF | Both delivery methods were used to ensure receipt. |

## 🔍 Known Limitations & Future Improvements

### Current Limitations

- **No real-time stock updates**: stock data is loaded from CSV at startup; a production system would query a live database
- **No actual WhatsApp integration**: the prototype uses a Streamlit UI; in production, it would connect to the WhatsApp Business API
- **Simple customer identification**: uses phone/email lookup; a production system would use authenticated sessions
- **No order creation**: the agent can only query existing orders, not create new ones
- **Single language**: the agent responds in Portuguese (pt-BR) as appropriate for the store's customer base

### What I Would Do With More Time

- **Integrate with a database** (PostgreSQL/SQLite) instead of CSVs for proper CRUD operations
- **Add unit and integration tests** for all tools and edge cases
- **Implement escalation to human agents** when the chatbot can't resolve an issue (the policy manual mentions "consult management")
- **Add product recommendations** based on customer purchase history and similar products
- **Implement proper session management** with user authentication
- **Add observability** (logging, metrics, traces) for monitoring agent behavior in production
- **Multi-turn tool usage analytics** to understand common customer journeys

## 🤖 Use of AI Assistants

This project was developed with the assistance of AI coding tools, as encouraged by the assignment:

| Tool | Model | How It Was Used |
|---|---|---|
| **Claude** (consultant agent) | Sonnet 5.5 | Initial scope analysis: mapping requirements (R1–R11), analyzing data files (CSVs and PDFs), identifying inconsistencies, structuring technical decisions. No code was generated. |
| **Antigravity** (development agent) | Claude Opus 4.6 | Code implementation, data treatment, file generation, testing, README writing. All code was reviewed and understood by the author. |
| **Hermes** (Antigravity review subagent) | Antigravity / Claude | Internal validation subagent: reviewed return policy eligibility logic, corrected date calculation to use `estimated_delivery` instead of `order_date` (aligning with the CDC 7-day rule), and added 5 regression tests. Decisions and scope recorded in [`docs/registro_agentes.md`](docs/registro_agentes.md). |

### Agent Activity Record

For coordination with Antigravity, consult [`docs/registro_agentes.md`](docs/registro_agentes.md) before resuming edits. It records each agent's scope, concise technical rationale, changed files, and verification status; it does not contain private chain-of-thought.

### Workflow

1. **Phase 0 — Planning** (Claude Sonnet 5.5): comprehensive analysis of the challenge requirements, data files, and store policies before writing any code. This produced a requirements checklist (R1–R11), data inconsistency catalog, and a structured list of 8 technical decisions.

2. **Phase 1+ — Implementation** (Antigravity/Claude Opus 4.6): architecture design and code implementation based on the decisions made in Phase 0. Every piece of generated code was reviewed, tested, and adjusted by the author.

The decision to start with a thorough planning phase before coding was deliberate: the assignment evaluates *how* you solve problems and *how* you make decisions, not just the final output.
