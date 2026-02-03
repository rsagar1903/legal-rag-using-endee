import streamlit as st
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
from chat_app import (
    load_resources,
    normalize_section_query,
    generate_response,
    generate_context,
    display_referenced_sections,
    extract_section_numbers,
    safe_display_metadata,
    query_all_acts,  # NEW: Import multi-act functions
    search_section_all_acts
)
from agent_router import classify_query
from scenario_processor import analyze_scenario
from concept_expander import expand_offenses
from retriever import retrieve_parallel

# --- App Configuration ---
st.set_page_config(
    page_title="Multi-Act Legal Advisor Pro",  # CHANGED: Updated title
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Session State Setup ---
def init_session_state():
    """Initialize all session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "recent_queries" not in st.session_state:
        st.session_state.recent_queries = []
    if "show_context" not in st.session_state:
        st.session_state.show_context = False
    if "resources" not in st.session_state:
        st.session_state.resources = load_resources()

# --- UI Components ---
def render_sidebar():
    """All sidebar controls and tools"""
    with st.sidebar:
        st.title("⚙️ Control Panel")
        
        # Chat Management
        st.header("Chat")
        if st.button("🆕 New Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        # Display Options
        st.header("Display")
        st.session_state.show_context = st.toggle(
            "Show retrieval context",
            help="Reveal the exact legal text passages used for generating answers"
        )
        
        # Recent Queries
        if st.session_state.recent_queries:
            st.header("Recent Queries")
            cols = st.columns(2)
            for i, query in enumerate(st.session_state.recent_queries[-6:]):
                with cols[i % 2]:
                    if st.button(
                        f"↩️ {query[:20]}...",
                        key=f"recent_{i}",
                        use_container_width=True
                    ):
                        process_query(query)
        
        # Export Tools
        st.header("Export")
        export_format = st.radio(
            "Format",
            ["Markdown", "JSON"],
            horizontal=True
        )
        export_conversation(export_format)

def export_conversation(format: str):
    """Generate downloadable conversation exports"""
    if not st.session_state.messages:
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"multi_act_conversation_{timestamp}"  # CHANGED: Updated filename
    
    if format == "Markdown":
        content = ["# Multi-Act Legal Advisor Conversation\n"]  # CHANGED: Updated title
        for msg in st.session_state.messages:
            role = "User" if msg["role"] == "user" else "Legal Advisor"
            content.append(f"## {role}\n{msg['content']}\n")
        
        st.download_button(
            label="💾 Download Markdown",
            data="\n".join(content),
            file_name=f"{filename}.md",
            use_container_width=True
        )
    else:
        st.download_button(
            label="💾 Download JSON",
            data=json.dumps(st.session_state.messages),
            file_name=f"{filename}.json",
            use_container_width=True
        )

# --- Core Pipeline ---
# In app/chat_ui.py

def run_legal_analysis(query: str) -> Dict:
    """
    Enhanced RAG pipeline - Fixed for flat list structure
    """
    # Unpack resources correctly
    # Note: load_resources() returns 'model' based on your chat_app.py
    # If it returns a tuple, unpack it. If just model, assign it.
    resources = st.session_state.resources
    
    start_time = time.time()
    
    # 1. Query Processing
    section_num = normalize_section_query(query)
    
    # 2. Document Retrieval
    results = {"documents": [], "metadatas": []}
    try:
        if section_num:
            # Search section across all acts
            results = search_section_all_acts(section_num)
            if not results["documents"]:
                results = query_all_acts(query, n_results=3)
        else:
            if classify_query(query) == "direct":
                results = query_all_acts(query, n_results=5)
            else:
                scenario_data = analyze_scenario(query)
                # Handle case where scenario_data might fail or be empty
                if not scenario_data:
                     results = query_all_acts(query, n_results=4)
                else:
                    offenses = [scenario_data.get("primary_offense", query)] + scenario_data.get("related_offenses", [])
                    results = query_all_acts(" ".join(offenses), n_results=4)
    except Exception as e:
        st.error(f"Retrieval error: {str(e)}")
        # Provide empty results to prevent crash later
        results = {"documents": [], "metadatas": []}
    
    retrieval_time = time.time() - start_time
    
    # 3. Response Generation
    context = generate_context(results)
    analysis = generate_response(query, context)
    gen_time = time.time() - start_time - retrieval_time
    
    # 4. Section Extraction (THE FIX IS HERE)
    sections = []
    
    # Get the list of metadatas
    meta_list = results.get("metadatas", [])
    
    # FIX: Handle nested lists if they exist (legacy support), or flat lists (new support)
    if meta_list and isinstance(meta_list[0], list):
        meta_list = meta_list[0]
        
    if meta_list:
        mentioned_sections = extract_section_numbers(analysis)
        for meta in meta_list:
            # Ensure meta is a dictionary before trying to read it
            if not isinstance(meta, dict):
                continue
                
            # Use the safe display function we added to chat_app
            from chat_app import safe_display_metadata
            meta = safe_display_metadata(meta)
            
            section_num = str(meta.get("section", ""))
            # If AI mentions it, OR if we retrieved it directly via section number
            if (not mentioned_sections) or (section_num in mentioned_sections):
                sections.append({
                    "section": section_num,
                    "display": meta.get("section_display", f"Section {section_num}"),
                    "heading": meta.get("heading", ""),
                    "act": meta.get("act", "UNKNOWN")
                })
    
    # 5. Context Preview (Safety Fix)
    context_preview = []
    if results.get("documents"):
        # Handle flat list vs nested list
        docs = results["documents"]
        if docs and isinstance(docs[0], list):
            docs = docs[0]
            
        context_preview = [str(doc)[:200] + "..." for doc in docs[:3]]
    
    return {
        "analysis": analysis,
        "sections": sections,
        "context_preview": context_preview,
        "timing": {
            "retrieval": round(retrieval_time * 1000),
            "generation": round(gen_time * 1000)
        }
    }
# --- Message Handling ---
def render_message(role: str, content: str, **kwargs):
    """Render a chat message with optional metadata"""
    with st.chat_message(role):
        st.markdown(content)
        
        if role == "assistant":
            # Display referenced sections - ENHANCED: Group by act
            if kwargs.get("sections"):
                st.divider()
                st.markdown("**📌 Referenced Sections**")
                
                # Group sections by act
                sections_by_act = {}
                for sec in kwargs["sections"]:
                    act = sec.get("act", "UNKNOWN")
                    if act not in sections_by_act:
                        sections_by_act[act] = []
                    sections_by_act[act].append(f"{sec['display']}: {sec['heading']}")
                
                # Display grouped by act
                for act, sections in sections_by_act.items():
                    with st.expander(f"📚 {act}", expanded=False):
                        for section_text in sections:
                            st.write(f"- {section_text}")
            
            # Show context preview if enabled
            if st.session_state.show_context and kwargs.get("context_preview"):
                with st.expander("🔍 View Retrieved Context"):
                    for doc in kwargs["context_preview"]:
                        st.caption(doc)
                        st.divider()
            
            # Show performance metrics
            with st.expander("⏱️ Performance Metrics", expanded=False):
                if kwargs.get("timing"):
                    st.metric("Retrieval Time", f"{kwargs['timing']['retrieval']}ms")
                    st.metric("Generation Time", f"{kwargs['timing']['generation']}ms")

def process_query(query: str):
    """Handle a new user query end-to-end"""
    if not query.strip():
        st.warning("Please enter a valid question")
        return
    
    # Add to recent queries (deduplicated)
    if (not st.session_state.recent_queries or 
        st.session_state.recent_queries[-1] != query):
        if len(st.session_state.recent_queries) >= 10:
            st.session_state.recent_queries.pop(0)
        st.session_state.recent_queries.append(query)
    
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": query})
    
    # Generate and display response
    with st.spinner("🔍 Analyzing across legal acts..."):  # CHANGED: Updated message
        try:
            response = run_legal_analysis(query)
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": response["analysis"],
                "sections": response["sections"],
                "context_preview": response["context_preview"],
                "timing": response["timing"]
            })
            
        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": "I couldn't process that request. Please try rephrasing or ask about a different legal topic."
            })

# --- Main App ---
def main():
    # Initialize app state
    init_session_state()
    
    # Header with disclaimer - CHANGED: Updated for multi-act
    st.title("⚖️ Multi-Act Legal Advisor Pro")
    st.caption("""
        This AI assistant helps analyze multiple legal acts: BNS, IPC, CrPC, CPC, and BSA. 
        **Disclaimer:** Not a substitute for professional legal advice.
    """)
    
    # Sidebar controls
    render_sidebar()
    
    # Chat history
    for msg in st.session_state.messages:
        render_message(
            msg["role"],
            msg["content"],
            sections=msg.get("sections"),
            context_preview=msg.get("context_preview"),
            timing=msg.get("timing")
        )
    
    # Input for new messages - CHANGED: Updated placeholder
    if prompt := st.chat_input("Ask about any legal section or scenario..."):
        process_query(prompt)
        st.rerun()

if __name__ == "__main__":
    main()