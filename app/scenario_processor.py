"""Enhanced scenario analysis with structured element extraction"""
import openai
import json
from dotenv import load_dotenv
import os
from agent_router import detect_acts_from_query
from error_handler import logger, retry_on_failure

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

@retry_on_failure(max_retries=2)
def analyze_scenario(scenario: str) -> dict:
    """
    Enhanced scenario analysis with structured extraction
    
    Returns:
        {
            "primary_offense": str,
            "related_offenses": list,
            "relevant_acts": list,
            "actors": list,
            "actions": list,
            "objects": list,
            "intent_markers": list,
            "aggravating_factors": list,
            "mitigating_factors": list,
            "enhanced_query": str
        }
    """
    prompt = f"""Analyze this legal scenario and extract structured information:

Scenario: {scenario}

Extract the following in JSON format:
1. PRIMARY_OFFENSE: Most serious applicable criminal/civil offense (one phrase)
2. RELATED_OFFENSES: Other applicable charges (list of 2-3 phrases)
3. RELEVANT_ACTS: Which legal acts apply (choose from: BNS, IPC, CrPC, CPC, BSA)
4. ACTORS: People involved and their roles (e.g., ["perpetrator", "victim"])
5. ACTIONS: Key actions taken (verbs/phrases)
6. OBJECTS: Physical items or property involved
7. INTENT_MARKERS: Words indicating criminal intent (mens rea indicators)
8. AGGRAVATING_FACTORS: Circumstances that worsen the offense
9. MITIGATING_FACTORS: Circumstances that lessen the offense

Output format:
{{
    "primary_offense": "...",
    "related_offenses": ["...", "..."],
    "relevant_acts": ["bns", "ipc"],
    "actors": ["...", "..."],
    "actions": ["...", "..."],
    "objects": ["..."],
    "intent_markers": ["..."],
    "aggravating_factors": ["..."],
    "mitigating_factors": ["..."]
}}"""
    
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You are a legal analysis expert. Extract structured information from scenarios."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Fallback: if LLM doesn't specify acts, detect from scenario text
        if not result.get("relevant_acts"):
            result["relevant_acts"] = detect_acts_from_query(scenario)
        
        # Build enhanced search query from extracted elements
        search_components = []
        search_components.append(result.get("primary_offense", ""))
        search_components.extend(result.get("actions", [])[:3])  # Top 3 actions
        search_components.extend(result.get("intent_markers", [])[:2])  # Top 2 intent markers
        
        result["enhanced_query"] = " ".join(filter(None, search_components))
        
        logger.info(f"Scenario analysis: {result.get('primary_offense')} + {len(result.get('related_offenses', []))} related")
        
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed: {e}")
        # Return minimal fallback
        return {
            "primary_offense": scenario[:50],
            "related_offenses": [],
            "relevant_acts": detect_acts_from_query(scenario),
            "enhanced_query": scenario
        }
    except Exception as e:
        logger.error(f"Scenario analysis failed: {e}")
        raise