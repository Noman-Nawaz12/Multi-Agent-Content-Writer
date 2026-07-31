import os
import difflib
import streamlit as st
from dotenv import load_dotenv
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from tavily import TavilyClient

# Load API key
load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7,
)

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def web_search(query: str) -> str:
    """Search the web using Tavily and return a compact text summary of results."""
    try:
        response = tavily_client.search(query=query, max_results=4)
        results = response.get("results", [])
        if not results:
            return "No search results found."
        combined = ""
        for r in results:
            combined += f"- {r['title']}: {r['content'][:300]}\n"
        return combined
    except Exception as e:
        return f"Search failed: {e}"


def generate_diff_html(old_text: str, new_text: str) -> str:
    """Compare old (draft) vs new (final) text and return a clean side-by-side HTML diff table."""
    old_lines = [line for line in old_text.splitlines() if line.strip() != ""]
    new_lines = [line for line in new_text.splitlines() if line.strip() != ""]

    differ = difflib.HtmlDiff(wrapcolumn=70)
    raw_table = differ.make_table(
        old_lines, new_lines,
        fromdesc="Writer Draft", todesc="Final Edited Output",
        context=True, numlines=1
    )
    return raw_table


DIFF_CSS = """
<style>
.diff-wrapper table.diff {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Source Code Pro', monospace;
    font-size: 13px;
    background-color: #0e1117;
    color: #e0e0e0;
}
.diff-wrapper table.diff td, .diff-wrapper table.diff th {
    padding: 4px 8px;
    vertical-align: top;
}
.diff-wrapper table.diff th {
    background-color: #1c1f26;
    color: #9aa5b1;
    text-align: left;
    border-bottom: 1px solid #333;
}
.diff-wrapper .diff_header {
    background-color: #1c1f26;
    color: #6c7686;
    text-align: right;
    padding-right: 6px;
}
.diff-wrapper .diff_next {
    background-color: #1c1f26;
}
.diff-wrapper .diff_add {
    background-color: #163b1f;
    color: #8fe39a;
}
.diff-wrapper .diff_sub {
    background-color: #3b1616;
    color: #f28b8b;
}
.diff-wrapper .diff_chg {
    background-color: #3b3316;
    color: #f2d98b;
}
.diff-wrapper {
    max-height: 600px;
    overflow-y: auto;
    border: 1px solid #333;
    border-radius: 8px;
}
</style>
"""


# ---------------------------
# State
# ---------------------------
class AgentState(TypedDict):
    topic: str
    draft: str
    final_output: str
    feedback: str
    revision_count: int
    needs_revision: bool

MAX_REVISIONS = 2  # safety limit so it doesn't loop forever


# ---------------------------
# Writer Agent Node
# ---------------------------
def writer_node(state: AgentState) -> AgentState:
    system_prompt = (
        "You are a professional content Writer AI. "
        "Your job is to write a clear, well-structured, informative first draft "
        "on the given topic, using the provided search results as factual reference. "
        "Keep it engaging but factual. "
        "Do not worry about perfection — just produce a solid first draft."
    )

    # If this is a revision (feedback exists), tell the Writer what to fix
    if state.get("feedback"):
        user_message = (
            f"Here is your previous draft:\n\n{state['draft']}\n\n"
            f"The Editor gave this feedback:\n{state['feedback']}\n\n"
            f"Please rewrite/improve the draft based on this feedback."
        )
    else:
        # Fresh draft: search the web first for current info
        search_results = web_search(state["topic"])
        user_message = (
            f"Topic: {state['topic']}\n\n"
            f"Here are recent web search results to use as reference:\n{search_results}\n\n"
            f"Now write a draft article about this topic, using relevant facts from above."
        )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]
    response = llm.invoke(messages)

    return {
        "topic": state["topic"],
        "draft": response.content,
        "final_output": "",
        "feedback": "",
        "revision_count": state.get("revision_count", 0),
        "needs_revision": False,
    }


# ---------------------------
# Editor Agent Node
# ---------------------------
def editor_node(state: AgentState) -> AgentState:
    revision_count = state.get("revision_count", 0)

    # First, ask Editor to judge quality (only if we haven't hit the revision limit)
    if revision_count < MAX_REVISIONS:
        judge_prompt = (
            "You are a strict Editor AI judging a draft's quality. "
            "Reply with ONLY one word: 'GOOD' if the draft is well-written, clear, and complete. "
            "Reply 'REVISE' if it has real problems (unclear, repetitive, missing key info, poor structure). "
            "Then on a new line, if you said REVISE, briefly explain (1-2 sentences) what needs fixing."
        )
        judge_messages = [
            SystemMessage(content=judge_prompt),
            HumanMessage(content=f"Draft:\n\n{state['draft']}")
        ]
        judge_response = llm.invoke(judge_messages).content.strip()

        if judge_response.upper().startswith("REVISE"):
            feedback_text = judge_response.split("\n", 1)[1] if "\n" in judge_response else "Please improve overall quality."
            return {
                "topic": state["topic"],
                "draft": state["draft"],
                "final_output": "",
                "feedback": feedback_text,
                "revision_count": revision_count + 1,
                "needs_revision": True,
            }

    # If GOOD, or revision limit reached, do the final polish
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
    return {
        "topic": state["topic"],
        "draft": state["draft"],
        "final_output": response.content,
        "feedback": "",
        "revision_count": revision_count,
        "needs_revision": False,
    }


# ---------------------------
# Routing function: decides Writer (revise) or END
# ---------------------------
def route_after_editor(state: AgentState) -> str:
    if state.get("needs_revision"):
        return "writer"
    return END


# ---------------------------
# Build Graph
# ---------------------------
graph = StateGraph(AgentState)
graph.add_node("writer", writer_node)
graph.add_node("editor", editor_node)
graph.set_entry_point("writer")
graph.add_edge("writer", "editor")
graph.add_conditional_edges("editor", route_after_editor, {"writer": "writer", END: END})
app_graph = graph.compile()


# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config(page_title="Multi-Agent Writer & Editor", layout="wide")

st.title("🤖 Multi-Agent AI: Writer + Editor")
st.write("Enter a topic. Agent 1 (Writer) drafts it, Agent 2 (Editor) refines it.")

topic = st.text_input("Enter a topic:")

if st.button("Run Agents"):
    if not topic.strip():
        st.warning("Please enter a topic first.")
    else:
        with st.spinner("Agents working (Writer ↔ Editor)..."):
            result = app_graph.invoke({
                "topic": topic,
                "draft": "",
                "final_output": "",
                "feedback": "",
                "revision_count": 0,
                "needs_revision": False,
            })
        # Save result in session_state so it doesn't disappear on button clicks
        st.session_state["result"] = result

if "result" in st.session_state:
    result = st.session_state["result"]

    st.info(f"🔁 Revisions made by Editor: {result.get('revision_count', 0)}")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("✍️ Raw Writer Draft (last version)")
        st.write(result["draft"])

    with col2:
        st.subheader("✅ Final Edited Output")
        st.write(result["final_output"])

    st.download_button(
        label="⬇️ Download Final Output",
        data=result["final_output"],
        file_name="final_output.txt",
        mime="text/plain",
    )

    # ---------------------------
    # Diff View: show what the Editor changed
    # ---------------------------
    st.subheader("🔍 What the Editor Changed")
    st.caption("🟢 Green = added by Editor | 🔴 Red = removed by Editor | 🟡 Yellow = changed line")

    diff_table_html = generate_diff_html(result["draft"], result["final_output"])
    st.markdown(DIFF_CSS, unsafe_allow_html=True)
    st.markdown(f'<div class="diff-wrapper">{diff_table_html}</div>', unsafe_allow_html=True)
