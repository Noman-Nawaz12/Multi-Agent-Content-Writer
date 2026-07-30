📄 Multi-Agent AI: Writer + Editor (with Web Search & Revision Loop)

An intelligent content-generation system built using **LangGraph Multi-Agent Orchestration** and **Live Web Search (RAG-style grounding)**. Enter any topic, and the system automatically drafts, reviews, revises, and polishes an article — powered by **two collaborating AI agents**. The Writer researches and drafts; the Editor judges, sends revision feedback, and produces the final polished output.

---

## 🚀 Features

- 📝 Enter any topic and generate a full article automatically
- 🤖 **2-Agent Architecture** — Writer Agent + Editor Agent, each with a distinct role
- 🔍 **Live Web Search (Tavily)** — Writer grounds its draft in real, current information instead of relying only on static training knowledge
- 🔁 **Revision Loop** — Editor judges draft quality and can send it back to the Writer with feedback (up to 2 revision cycles) before finalizing
- ✅ **Quality Judgment Step** — Editor decides "GOOD" vs "REVISE" before polishing
- ✂️ **Final Polish Pass** — grammar, clarity, structure, and tone improvements
- 📊 **Side-by-side Comparison** — raw Writer draft vs. final Editor output shown together
- ⬇️ **Download Button** — save the final output as a `.txt` file
- 🖥️ Clean Streamlit web interface
- 🔐 Secure API key management via `.env`

---

## 🏗️ System Architecture

```
                     ┌───────────────────┐
                     │   User enters a     │
                     │      topic          │
                     └─────────┬──────────┘
                               │
                               ▼
                     ┌───────────────────┐
                     │   Streamlit UI      │
                     │  "Run Agents" click │
                     └─────────┬──────────┘
                               │
                               ▼
                ┌───────────────────────────────┐
                │        WRITER AGENT            │
                │  (LLM: Groq - gpt-oss-120b)     │
                │                                 │
                │  • First run → Tavily Web Search│
                │    fetches current info         │
                │  • Revision run → uses Editor's │
                │    feedback instead              │
                │  • Generates the draft           │
                └───────────────┬─────────────────┘
                                │
                                ▼
                ┌───────────────────────────────┐
                │        EDITOR AGENT             │
                │  (LLM: Groq - gpt-oss-120b)      │
                │                                  │
                │  Step 1: Judge draft quality      │
                │   → "GOOD" or "REVISE"            │
                └───────────────┬──────────────────┘
                                │
                 ┌──────────────┴───────────────┐
                 │                               │
          REVISE (feedback given)          GOOD (or max
                 │                         revisions reached)
                 ▼                               │
        ┌─────────────────┐                      ▼
        │  Loop back to    │           ┌───────────────────┐
        │  WRITER AGENT    │           │   Final Polish       │
        │  (max 2 times)   │           │   by Editor Agent     │
        └─────────────────┘           └──────────┬───────────┘
                                                   │
                                                   ▼
                                       ┌───────────────────────┐
                                       │   Final Output shown    │
                                       │   in Streamlit UI +     │
                                       │   Download button        │
                                       └───────────────────────┘
```

---

## 🧠 The Two Agents

### ✍️ Agent 1 — Writer
**Role:** Researcher + Drafter
**Responsibility:** Search the web for current facts on the topic, then write a clear, well-structured first draft. On revision rounds, rewrite based on the Editor's feedback instead of searching again.

### ✅ Agent 2 — Editor
**Role:** Critic + Finalizer
**Responsibility:** Judge whether the Writer's draft is good enough. If not, send specific feedback back to the Writer (revision loop, max 2 rounds). Once approved (or the revision limit is hit), perform a final polish pass — fixing grammar, tightening structure, removing repetition, and improving tone.

> Both agents use the same underlying LLM (Groq's `openai/gpt-oss-120b`) but behave completely differently because each has its own system prompt, role, and responsibility — this is what makes them distinct "agents" rather than one generic AI call.

---

## 🛠️ Tech Stack

| Component | Tool |
|---|---|
| LLM | Groq API (`openai/gpt-oss-120b`) |
| Agent Orchestration | LangGraph |
| LLM Integration | LangChain (`langchain-groq`, `langchain-core`) |
| Web Search | Tavily API |
| UI | Streamlit |
| Config/Secrets | python-dotenv |

---

## ⚙️ Setup Instructions

```bash
# 1. Create project folder & virtual environment
mkdir multi-agent-langgraph
cd multi-agent-langgraph
python -m venv venv
venv\Scripts\activate

# 2. Install dependencies
pip install langgraph langchain langchain-groq python-dotenv streamlit tavily-python

# 3. Add API keys to .env
echo GROQ_API_KEY=your_groq_key_here > .env
echo TAVILY_API_KEY=your_tavily_key_here >> .env

# 4. Run the app
streamlit run app.py
```

---

## 📂 Project Structure

```
multi-agent-langgraph/
├── venv/                # Virtual environment
├── .env                 # API keys (private, never share)
├── requirements.txt     # Installed packages list
├── main.py              # Early console-only test version (not actively used)
├── app.py               # Main Streamlit app - this is what actually runs
└── README.md            # This file
```

---

## 📊 Shared State Between Agents

| Field | Type | Purpose |
|---|---|---|
| `topic` | str | Topic entered by the user |
| `draft` | str | Writer's current draft |
| `final_output` | str | Editor's final polished version |
| `feedback` | str | Editor's revision notes for the Writer |
| `revision_count` | int | How many revision cycles have happened |
| `needs_revision` | bool | Controls whether the graph loops back to the Writer |

`MAX_REVISIONS = 2` — prevents the Writer to Editor loop from running forever.

---

## 📝 Example Run

**Topic:** "Prophet Muhammad (PBUH)"
**Revisions made by Editor:** 1

- Web search pulled in real references (Madinah Media, MuslimSG, Southern Equip), giving the draft cited facts and footnotes.
- Editor requested one revision before approving.
- Final polish removed draft-style labels (e.g., "Working Draft"), tightened section headings, smoothed sentence flow, and condensed table wording — while keeping all facts and structure intact.

---

## ⚠️ Notes & Limitations

- The Editor's "GOOD" vs "REVISE" judgment is an LLM decision, not a hard rule - it may occasionally be inconsistent.
- Without web search, the LLM would rely only on its static training knowledge, which can be outdated.
- API keys must stay private - regenerate immediately if ever exposed accidentally.

---

## 🔮 Possible Future Improvements

- Add a third agent (e.g., a Fact-Checker) between Writer and Editor
- Let the user choose a tone/style (formal, casual, persuasive)
- Stream output live instead of waiting for the full result
- Save run history to a local database
- Export final output as `.docx` or `.pdf`
