import openai
import os
from dotenv import load_dotenv
from typing import Literal

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
print(openai.api_key)

def classify_query(query: str) -> Literal["direct", "scenario", "section"]:
    """
    Enhanced classifier that also detects section-specific queries
    Returns: "direct", "scenario", or "section"
    """
    # First check if it's a section query
    if is_section_query(query):
        return "section"
    
    # Use existing classification logic
    examples = """
    Direct Queries:
    - "Explain theft in BNS"
    - "Definition of murder in IPC"
    - "What is evidence under BSA"
    
    Scenario Queries:
    - "A mob vandalized property during protest"
    - "My neighbor stole my bike and sold it"
    - "Someone committed fraud in business contract"
    
    Section Queries:
    - "Explain Section 302 of BNS"
    - "What is IPC section 378"
    - "BSA section 45 meaning\""""
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[{
            "role": "system",
            "content": f"Classify as 'direct', 'scenario', or 'section'. Examples:{examples}"
        },{
            "role": "user", 
            "content": query
        }],
        temperature=0
    )
    return response.choices[0].message.content.lower().strip()

def is_section_query(query: str) -> bool:
    """Check if query specifically mentions a section number"""
    import re
    section_patterns = [
        r'section\s+\d+',
        r'sec\.?\s*\d+',
        r'§\s*\d+',
        r'\b\d+\s+of\s+(bns|ipc|crpc|cpc|bsa)',
        r'(bns|ipc|crpc|cpc|bsa)\s+section\s+\d+'
    ]
    
    query_lower = query.lower()
    return any(re.search(pattern, query_lower) for pattern in section_patterns)

def detect_acts_from_query(query: str) -> list:
    """
    Detect which legal acts are relevant to the query
    Returns list of act names: ['bns', 'ipc', 'crpc', 'cpc', 'bsa']
    """
    query_lower = query.lower()
    relevant_acts = []
    
    # Act-specific detection
    act_keywords = {
        'bns': ['bns', 'nyaya', 'sanhita', 'bharatiya', 'new code', '2023'],
        'ipc': ['ipc', 'indian penal', 'penal code', 'old code', '1860'],
        'crpc': ['crpc', 'criminal procedure', 'procedure code', 'bail', 'arrest', 'trial'],
        'cpc': ['cpc', 'civil procedure', 'civil code', 'suit', 'plaint', 'decree'],
        'bsa': ['bsa', 'evidence', 'evidence act', 'proof', 'witness', 'exhibit']
    }
    
    for act, keywords in act_keywords.items():
        if any(keyword in query_lower for keyword in keywords):
            relevant_acts.append(act)
    
    # If no specific acts mentioned, return all acts
    if not relevant_acts:
        return ['bns', 'ipc', 'crpc', 'cpc', 'bsa']
    
    return relevant_acts