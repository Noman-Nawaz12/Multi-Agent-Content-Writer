# 🤖 Multi-Agent AI: Writer + Editor

### Agentic AI Content Generation System with Web Search, Revision Loop & Change Tracking

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange)
![Groq](https://img.shields.io/badge/Groq-LLM%20API-green)
![Tavily](https://img.shields.io/badge/Tavily-Web%20Search-purple)

---

## 📌 Overview

Multi-Agent AI: Writer + Editor is an agentic content-generation system built to demonstrate real multi-agent orchestration using **LangGraph**. Instead of a single AI call producing one response, two specialized AI agents collaborate — one drafts, the other reviews, revises, and finalizes.

The system automatically:

✅ Searches the web for current, relevant information on any topic
✅ Drafts a full article using an AI Writer Agent
✅ Judges the draft's quality using an AI Editor Agent
✅ Sends the draft back for revision if it isn't good enough (autonomous feedback loop)
✅ Produces a final, polished version
✅ Tracks and displays exactly what the Editor changed

---

## 🖥️ Application Preview

### Input

* Topic Entry Field
* "Run Agents" Trigger Button

### Agent Pipeline

* Writer Agent Draft Generation
* Editor Agent Quality Judgment
* Automatic Revision Loop (up to 2 cycles)
* Editor Final Polish Pass

### Output

* Raw Writer Draft
* Final Edited Output
* Revision Count Display
* Side-by-Side Diff View (Editor's Changes)
* Downloadable Final Report

---

# 🚀 Key Features

## 🤖 Multi-Agent Architecture

The system runs on two distinct, specialized AI agents:

| Agent | Role | Supported |
| --- | --- | --- |
| Writer Agent | Research + Drafting | ✅ |
| Editor Agent | Quality Judgment | ✅ |
| Editor Agent | Revision Feedback | ✅ |
| Editor Agent | Final Polishing | ✅ |

---

## 🔍 Live Web Search Grounding (Tavily)

Instead of relying only on the LLM's static training knowledge, the Writer Agent performs a real-time web search before drafting.

Features:

* Current, Real-World Information Retrieval
* Source-Backed Draft Generation
* Reduces Outdated or Generic Content

Example:

```text
Search Query: "Prophet Muhammad (PBUH)"
Sources Retrieved: Madinah Media, MuslimSG, Southern Equip
```

---

## 🔁 Autonomous Revision Loop

The Editor Agent doesn't just polish blindly — it first **judges** the draft.

* If the draft has real issues → sends feedback back to the Writer
* Writer rewrites based on that feedback
* Process repeats up to 2 times (safety limit)
* Once approved, moves to final polishing

Example:

```text
Editor Judgment: REVISE
Feedback: "Introduction is too generic, needs more specific detail."
Revisions Made: 1
```

---

## 📊 Change Tracking (Diff View)

The dashboard provides a professional, side-by-side comparison of the Writer's draft vs. the Editor's final version.

* Line-by-Line Diff Table
* Color-Coded Additions, Removals, and Edits
* Scrollable, GitHub-style Diff Display

This helps users clearly see what the Editor Agent actually improved.

---

## 📈 Result Comparison

### Output Analysis

The application generates:

* Raw Writer Draft (last version before finalizing)
* Final Edited Output
* Revision Count Indicator
* Highlighted Diff Table

This helps users quickly understand how much the Editor Agent contributed.

---

## 📋 Example Run

```text
Topic: "Prophet Muhammad (PBUH)"

Revisions Made by Editor: 1

Editor's Final Polish Included:
- Removed draft-style labels ("Working Draft", "First Draft")
- Tightened section headings for conciseness
- Smoothed sentence phrasing and flow
- Condensed table wording
- Preserved all facts and structure
```

---

# 🏗️ System Workflow

```text
User Enters Topic
      │
      ▼
Streamlit UI ("Run Agents")
      │
      ▼
Writer Agent (Groq LLM)
      │
      ├── Fresh Topic → Tavily Web Search → Draft
      └── Revision Round → Uses Editor Feedback → Draft
      │
      ▼
Editor Agent (Groq LLM)
      │
      ├── Judges Draft: GOOD or REVISE
      │
      ├── REVISE → Feedback → Loop back to Writer (max 2x)
      │
      └── GOOD → Final Polish
      │
      ▼
Final Output + Diff View + Download Button
```

---

# 🧠 Technologies Used

## Artificial Intelligence

* Groq API (LLM: `openai/gpt-oss-120b`)
* LangGraph (Multi-Agent Orchestration)
* LangChain (LLM Message Handling)
* Tavily API (Web Search / Real-Time Grounding)

## Frontend

* Streamlit

## Utilities

* python-dotenv (Secure API Key Management)
* difflib (Change Tracking / Diff Generation)

---

# 📂 Project Structure

```text
multi-agent-langgraph/
│
├── app.py
├── main.py
├── requirements.txt
├── README.md
├── .env
│
└── venv/
```

---

# ⚙️ Installation

Clone repository:

```bash
git clone https://github.com/Noman-Nawaz12/Multi-Agent-Content-Writer.git
cd Multi-Agent-Content-Writer
```

Create virtual environment:

```bash
python -m venv venv
```

Activate environment:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Add API keys to `.env`:

```env
GROQ_API_KEY=your_groq_key_here
TAVILY_API_KEY=your_tavily_key_here
```

---

# ▶️ Run Application

```bash
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

---

# 🌐 Live Deployment

Deployed on **Streamlit Community Cloud**, connected via GitHub for continuous deployment.

API keys are securely managed using Streamlit Cloud's **Secrets** manager (TOML format), keeping them out of the public repository.

---

# 🎯 Future Enhancements

* Third Agent: Fact-Checker between Writer and Editor
* Selectable Writing Style/Tone (Formal, Casual, Persuasive)
* Live Streaming Output
* Run History Storage (Database)
* Export as PDF/DOCX
* n8n Visual Workflow Version (No-Code Alternative)

---

# 👨‍💻 Developer

### Noman Nawaz

Software Engineering Student
Foundation University Islamabad

GitHub:
[Noman Nawaz LinkedIn](https://www.linkedin.com/in/noman-nawaz-513182250)

---

# ⚠️ Disclaimer

This project is intended for educational and demonstration purposes, showcasing agentic AI and multi-agent orchestration concepts using LangGraph.

Generated content should be reviewed before use in any professional, academic, or publication context.
