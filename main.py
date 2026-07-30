import os
from dotenv import load_dotenv
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

# Load API key from .env file
load_dotenv()

# Initialize the Groq model (shared by both agents, different prompts used per agent)
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7,
)

# ---------------------------
# 1. Define the shared State
# ---------------------------
class AgentState(TypedDict):
    topic: str
    draft: str
    final_output: str


# ---------------------------
# 2. Writer Agent Node
# ---------------------------
def writer_node(state: AgentState) -> AgentState:
    system_prompt = (
        "You are a professional content Writer AI. "
        "Your job is to write a clear, well-structured, informative first draft "
        "on the given topic. Keep it engaging but factual. "
        "Do not worry about perfection — just produce a solid first draft."
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Write a draft article about: {state['topic']}")
    ]

    response = llm.invoke(messages)
    print("\n===== WRITER AGENT DRAFT =====\n")
    print(response.content)

    return {"topic": state["topic"], "draft": response.content, "final_output": ""}


# ---------------------------
# 3. Editor Agent Node
# ---------------------------
def editor_node(state: AgentState) -> AgentState:
    system_prompt = (
        "You are a sharp, detail-oriented Editor AI. "
        "You review drafts written by another AI (the Writer) and improve them. "
        "Fix grammar, improve clarity, remove repetition, tighten structure, "
        "add missing important points if needed, and make the tone more engaging. "
        "Return ONLY the improved final version, not commentary."
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Here is the draft to review and improve:\n\n{state['draft']}")
    ]

    response = llm.invoke(messages)
    print("\n===== EDITOR AGENT FINAL OUTPUT =====\n")
    print(response.content)

    return {"topic": state["topic"], "draft": state["draft"], "final_output": response.content}


# ---------------------------
# 4. Build the Graph
# ---------------------------
graph = StateGraph(AgentState)

graph.add_node("writer", writer_node)
graph.add_node("editor", editor_node)

graph.set_entry_point("writer")
graph.add_edge("writer", "editor")
graph.add_edge("editor", END)

app = graph.compile()


# ---------------------------
# 5. Run the pipeline
# ---------------------------
if __name__ == "__main__":
    topic = input("Enter a topic for the Writer agent: ")

    result = app.invoke({"topic": topic, "draft": "", "final_output": ""})

    print("\n\n===== COMPARISON =====")
    print("\n--- RAW WRITER DRAFT ---\n")
    print(result["draft"])
    print("\n--- FINAL EDITED OUTPUT ---\n")
    print(result["final_output"])