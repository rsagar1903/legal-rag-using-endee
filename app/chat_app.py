"""
Multi-Act Legal Advisor - INTEGRATED VERSION
Now uses the full intelligence pipeline
"""
import streamlit as st
from sentence_transformers import SentenceTransformer
import openai
import os
import re
import json
from dotenv import load_dotenv

# Import intelligence layer
from agent_router import classify_query, is_section_query
from scenario_processor import analyze_scenario
from concept_expander import expand_offenses, expand_offenses_hierarchical
from retriever import retrieve_with_intelligence, retrieve_direct
from confidence_scorer import calculate_confidence
from error_handler import logger

load_dotenv()

@st.cache_resource
def load_resources():
    """Load models and API keys"""
    model = SentenceTransformer('all-MiniLM-L6-v2')
    openai.api_key = os.getenv("OPENAI_API_KEY")
    logger.info("Resources loaded")
    return model

def normalize_section_query(query: str) -> str:
    """Extract section number from query"""
    match = re.search(r'(?:section|sec\.?)\s*(\d+)|^(\d+)$', query.lower())
    return (match.group(1) or match.group(2)) if match else None

def generate_response(prompt: str, context: str, confidence_level: str = "high") -> str:
    """
    Generate LLM response with confidence-aware prompting
    """
    # Adjust system prompt based on confidence
    if confidence_level == "low":
        confidence_note = """
NOTE: The retrieved information may be limited. If you cannot find clear answers 
in the context, acknowledge this and suggest what additional information would be needed.
"""
    else:
        confidence_note = ""
    
    try:
        messages = [
            {
                "role": "system",
                "content": f"""You are a multi-act legal expert for Indian law. 
Analyze using provisions from BNS, IPC, CrPC, CPC, and BSA.

{confidence_note}

Structure your response as:

**Applicable Sections:**
- [Act] Section [X]: [Brief description]

**Legal Analysis:**
[Explain key elements, requirements, and applicability]

**Potential Defenses/Considerations:**
[Mention possible defenses or important considerations]

**Important:** Only use the sections and information provided in the context below. 
Always mention which Act each section belongs to.

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
        logger.error(f"LLM generation failed: {e}")
        return f"Error generating response: {str(e)}"

def extract_section_numbers(text: str):
    """Extract section numbers mentioned in analysis"""
    matches = re.findall(r'Section (\d+)', text, re.IGNORECASE)
    return set(matches)

def display_referenced_sections(results, analysis_text=""):
    """Display sections grouped by Act"""
    if not results.get("metadatas"):
        return False

    mentioned_sections = extract_section_numbers(analysis_text)
    st.markdown("### 📚 Referenced Sections")

    sections_by_act = {}
    seen = set()

    for meta in results["metadatas"]:
        section_num = str(meta.get("section", ""))
        section_display = meta.get("section_display", f"Section {section_num}")
        heading = meta.get("heading", "")
        act = meta.get("act", "UNKNOWN")
        
        # Show if: no filtering OR section was mentioned OR is a definition
        is_definition = meta.get('is_definition', False)
        is_reference = meta.get('is_reference', False)
        
        if (not mentioned_sections) or (section_num in mentioned_sections) or is_definition:
            prefix = "📌 " if is_definition else ("🔗 " if is_reference else "")
            text = f"{prefix}{section_display}: {heading}".strip()
            
            if text and text not in seen:
                sections_by_act.setdefault(act, []).append(text)
                seen.add(text)

    for act, sections in sections_by_act.items():
        with st.expander(f"📖 {act}", expanded=True):
            for s in sections:
                st.write(f"- {s}")

    return True

def generate_context(results):
    """Build context from retrieved documents"""
    if not results.get("documents"):
        return "No matching sections found"
    return "\n\n---\n\n".join(results["documents"])

def display_confidence(confidence: dict):
    """Display confidence indicator"""
    level = confidence['level']
    score = confidence['score']
    
    color_map = {
        'high': '🟢',
        'medium': '🟡',
        'low': '🔴'
    }
    
    st.markdown(f"""
    **{color_map[level]} Confidence: {level.upper()}** ({score:.0%})
    """)
    
    with st.expander("📊 Confidence Factors"):
        for factor, value in confidence.get('factors', {}).items():
            st.write(f"- **{factor}:** {value}")

def run_enhanced_pipeline(query: str) -> dict:
    """
    THE MAIN INTEGRATION POINT
    This is where all intelligence layers come together
    """
    logger.info(f"Processing query: {query[:100]}...")
    
    # Step 1: Classify query
    query_type = classify_query(query)
    logger.info(f"Query type: {query_type}")
    
    # Step 2: Route based on type
    scenario_data = None
    
    if query_type == "section":
        # Direct section lookup
        section_num = normalize_section_query(query)
        if section_num:
            results = retrieve_direct(f"Section {section_num}", n_results=3)
        else:
            results = retrieve_direct(query, n_results=5)
    
    elif query_type == "scenario":
        # Enhanced scenario processing
        logger.info("Analyzing scenario...")
        scenario_data = analyze_scenario(query)
        
        logger.info(f"Primary offense: {scenario_data.get('primary_offense')}")
        logger.info(f"Related: {scenario_data.get('related_offenses')}")
        
        # Use intelligent retrieval
        results = retrieve_with_intelligence(
            query_text=query,
            query_type="scenario",
            scenario_data=scenario_data,
            n_results=5
        )
    
    else:  # direct query
        logger.info("Processing as direct query...")
        results = retrieve_with_intelligence(
            query_text=query,
            query_type="direct",
            n_results=5
        )
    
    # Step 3: Calculate confidence
    confidence = calculate_confidence(results, query, query_type)
    logger.info(f"Confidence: {confidence['level']} ({confidence['score']:.2f})")
    
    # Step 4: Generate LLM response
    context = generate_context(results)
    analysis = generate_response(query, context, confidence['level'])
    
    return {
        'analysis': analysis,
        'results': results,
        'confidence': confidence,
        'query_type': query_type,
        'scenario_data': scenario_data
    }

def main():
    st.set_page_config(page_title="Multi-Act Legal Advisor", layout="wide")
    st.title("⚖️ Multi-Act Legal Advisor")
    st.caption("AI-powered legal analysis across BNS, IPC, CrPC, CPC, and BSA")
    
    # Load resources
    model = load_resources()
    
    # Sidebar info
    with st.sidebar:
        st.header("ℹ️ About")
        st.write("""
        This system uses:
        - **Query Intelligence**: Automatic classification
        - **Scenario Analysis**: Structured extraction
        - **Concept Expansion**: Legal synonyms
        - **Vector Search**: Endee-powered retrieval
        - **Reranking**: Cross-encoder precision
        - **Confidence Scoring**: Reliability indicators
        """)
        
        st.header("📊 Debug Info")
        show_debug = st.checkbox("Show debug information")
    
    # Main query input
    query = st.text_area(
        "Describe your legal scenario or question:",
        placeholder="E.g., 'What is the punishment for theft?' or 'A person stole my bike and ran away'"
    )

    if st.button("🔍 Analyze", type="primary"):
        if not query.strip():
            st.warning("Please enter a query")
            return

        with st.spinner("Analyzing across legal acts..."):
            try:
                # Run enhanced pipeline
                result = run_enhanced_pipeline(query)
                
                # Display confidence
                st.markdown("---")
                display_confidence(result['confidence'])
                
                # Display analysis
                st.markdown("## 📝 Legal Analysis")
                st.markdown(result['analysis'])
                
                # Display referenced sections
                st.markdown("---")
                display_referenced_sections(
                    result['results'],
                    result['analysis']
                )
                
                # Debug information
                if show_debug:
                    st.markdown("---")
                    st.markdown("### 🐛 Debug Information")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Query Type:**", result['query_type'])
                        st.write("**Documents Retrieved:**", len(result['results']['documents']))
                        if 'scores' in result['results']:
                            st.write("**Avg Score:**", f"{sum(result['results']['scores'])/len(result['results']['scores']):.3f}")
                    
                    with col2:
                        if result['scenario_data']:
                            st.write("**Scenario Analysis:**")
                            st.json(result['scenario_data'])
                    
                    with st.expander("📄 Retrieved Context"):
                        st.text(generate_context(result['results'])[:1000] + "...")

            except Exception as e:
                logger.error(f"Analysis failed: {e}", exc_info=True)
                st.error(f"❌ Analysis failed: {str(e)}")
                st.error("Please try rephrasing your query or contact support.")

if __name__ == "__main__":
    main()