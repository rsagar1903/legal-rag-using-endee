"""Enhanced legal concept expansion with hierarchical relationships"""
import openai
from dotenv import load_dotenv
import os
import json
from error_handler import logger, retry_on_failure

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Expanded offense cache
OFFENSE_CACHE = {
    "theft": ["larceny", "stealing", "misappropriation"],
    "murder": ["homicide", "culpable homicide", "causing death", "killing"],
    "riot": ["unlawful assembly", "mob violence", "affray"],
    "fraud": ["cheating", "deception", "forgery", "criminal breach of trust"],
    "assault": ["hurt", "grievous hurt", "battery", "criminal force"],
    "rape": ["sexual assault", "sexual violence", "outraging modesty"],
    "kidnapping": ["abduction", "wrongful confinement", "illegal detention"],
    "robbery": ["dacoity", "armed robbery", "extortion with violence"],
    "defamation": ["libel", "slander", "injuring reputation"],
    "criminal breach of trust": ["misappropriation", "embezzlement", "breach of fiduciary duty"],
}

# Hierarchical relationships
OFFENSE_HIERARCHY = {
    "theft": {
        "parent": "offences_against_property",
        "children": ["petty_theft", "grand_theft", "aggravated_theft"],
        "related": ["robbery", "dacoity", "criminal_breach_of_trust", "extortion"]
    },
    "murder": {
        "parent": "offences_affecting_life",
        "children": ["first_degree", "second_degree", "culpable_homicide"],
        "related": ["attempt_to_murder", "causing_death", "abetment_of_suicide"]
    },
    "assault": {
        "parent": "offences_affecting_body",
        "children": ["simple_hurt", "grievous_hurt", "assault_with_weapon"],
        "related": ["criminal_force", "wrongful_restraint", "wrongful_confinement"]
    }
}

def expand_offenses(offense_list: list) -> list:
    """
    Generate legal synonyms for offenses (simple version)
    Returns: Flat list of expanded terms
    """
    expanded = set()
    
    for offense in offense_list:
        offense_lower = offense.lower().strip()
        expanded.add(offense_lower)  # Add original
        
        # Check cache first
        if offense_lower in OFFENSE_CACHE:
            expanded.update(OFFENSE_CACHE[offense_lower])
            logger.info(f"Expanded '{offense}' from cache")
            continue
        
        # Fallback to LLM
        try:
            llm_expansions = _expand_via_llm(offense_lower)
            expanded.update(llm_expansions)
        except Exception as e:
            logger.warning(f"LLM expansion failed for '{offense}': {e}")
    
    return list(expanded)

def expand_offenses_hierarchical(offense_list: list) -> dict:
    """
    Advanced expansion with hierarchical structure
    
    Returns:
        {
            "primary": [...],
            "synonyms": [...],
            "related": [...],
            "broader": [...]
        }
    """
    result = {
        "primary": [],
        "synonyms": [],
        "related": [],
        "broader": []
    }
    
    for offense in offense_list:
        offense_lower = offense.lower().strip()
        result["primary"].append(offense_lower)
        
        # Get synonyms
        if offense_lower in OFFENSE_CACHE:
            result["synonyms"].extend(OFFENSE_CACHE[offense_lower])
        
        # Get hierarchical relationships
        if offense_lower in OFFENSE_HIERARCHY:
            hierarchy = OFFENSE_HIERARCHY[offense_lower]
            result["related"].extend(hierarchy.get("related", []))
            if hierarchy.get("parent"):
                result["broader"].append(hierarchy["parent"])
    
    # Remove duplicates
    for key in result:
        result[key] = list(set(result[key]))
    
    return result

@retry_on_failure(max_retries=2)
def _expand_via_llm(offense: str) -> list:
    """Use LLM to generate synonyms for unknown offenses"""
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[{
            "role": "system",
            "content": f"Generate 2-3 alternative legal terms for '{offense}'. Return only the terms, one per line."
        }],
        temperature=0.3,
        max_tokens=50
    )
    
    variations = [
        v.strip().strip('"').strip('-').strip() 
        for v in response.choices[0].message.content.split("\n") 
        if v.strip()
    ]
    
    # Add to cache for future use
    OFFENSE_CACHE[offense] = variations
    logger.info(f"Added LLM expansion for '{offense}': {variations}")
    
    return [offense] + variations

def save_cache_to_file(filepath: str = "data/offense_cache.json"):
    """Save current cache to file"""
    try:
        with open(filepath, 'w') as f:
            json.dump(OFFENSE_CACHE, f, indent=2)
        logger.info(f"Saved offense cache to {filepath}")
    except Exception as e:
        logger.error(f"Failed to save cache: {e}")