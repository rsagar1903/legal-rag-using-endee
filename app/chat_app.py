import streamlit as st
from sentence_transformers import SentenceTransformer
import openai
import os
import re
import json
from dotenv import load_dotenv
from agent_router import classify_query
from scenario_processor import analyze_scenario
from concept_expander import expand_offenses
from retriever import retrieve_direct

load_dotenv()


@st.cache_resource
def load_resources():
    model = SentenceTransformer('all-MiniLM-L6-v2')
    openai.api_key = os.getenv("OPENAI_API_KEY")
    return model


def normalize_section_query(query: str) -> str:
    match = re.search(r'(?:section|sec\.?)\s*(\d+)|^(\d+)$', query.lower())
    return (match.group(1) or match.group(2)) if match else None


def generate_response(prompt: str, context: str) -> str:
    try:
        messages = [
            {
                "role": "system",
                "content": f"""
You are a multi-act legal expert. Analyze using provisions from BNS, IPC, CrPC, CPC, and BSA.

Structure responses as:
1. Applicable Sections (mention which act they belong to)
2. Key Elements
3. Potential Defenses

Context:
{context}
""",
            },
            {"role": "user", "content": prompt},
        ]

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=messages,
            temperature=0.1,
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating response: {str(e)}"


def extract_section_numbers(text: str):
    matches = re.findall(r'BNS Section (\d+)|Section (\d+)', text)
    return {num for tup in matches for num in tup if num}


def display_referenced_sections(results, analysis_text=""):
    if not results.get("metadatas"):
        return False

    mentioned_sections = extract_section_numbers(analysis_text)
    st.markdown("**Referenced Sections**")

    sections_by_act = {}
    seen = set()

    for meta in results["metadatas"]:
        section_num = str(meta.get("section", ""))
        section_display = meta.get("section_display", f"Section {section_num}")
        heading = meta.get("heading", "")
        act = meta.get("act", "BNS")

        if (not mentioned_sections) or (section_num in mentioned_sections):
            text = f"{section_display}: {heading}".strip()
            if text and text not in seen:
                sections_by_act.setdefault(act, []).append(text)
                seen.add(text)

    for act, sections in sections_by_act.items():
        with st.expander(f"📚 {act}", expanded=True):
            for s in sections:
                st.write(f"- {s}")

    return True


def generate_context(results):
    if not results.get("documents"):
        return "No matching sections found"

    return "\n\n".join(results["documents"])

def safe_display_metadata(meta):
    """Safely extracts metadata for display, handling missing keys."""
    if not meta:
        return {}
    return {
        "section": meta.get("section", ""),
        "section_display": meta.get("section_display", f"Section {meta.get('section', '')}"),
        "heading": meta.get("heading", ""),
        "act": meta.get("act", "UNKNOWN").upper(),
        "chapter": meta.get("chapter", "")
    }

def query_all_acts(query, n_results=5):
    """Bridge function: Maps old UI call to new Endee retriever"""
    return retrieve_direct(query, n_results=n_results)

def search_section_all_acts(section_num):
    """Bridge function: Searches for a specific section number"""
    # We construct a query like "Section 302" to find it in the vector DB
    return retrieve_direct(f"Section {section_num}", n_results=5)


def main():
    st.set_page_config(page_title="Multi-Act Legal Advisor", layout="wide")
    st.title("⚖️ Multi-Act Legal Advisor")
    st.caption("Supporting BNS, IPC, CrPC, CPC, and BSA")

    model = load_resources()

    query = st.text_area("Describe your legal scenario or question:")

    if st.button("Analyze"):
        if not query.strip():
            st.warning("Please enter a query")
            return

        with st.spinner("Analyzing across legal acts..."):
            try:
                results = retrieve_direct(query, n_results=5)

                context = generate_context(results)
                analysis_text = generate_response(query, context)

                st.markdown("## Legal Analysis")
                st.markdown(analysis_text)

                display_referenced_sections(results, analysis_text)

            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")


if __name__ == "__main__":
    main()
