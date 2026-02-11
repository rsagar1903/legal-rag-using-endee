"""Cross-reference expansion for related sections"""
from typing import Dict, List, Set
from chunk_lookup import get_lookup
from error_handler import logger

# Definition sections that should always be included
DEFINITION_SECTIONS = {
    "theft": ["bns_303", "ipc_378"],
    "murder": ["bns_100", "ipc_300", "ipc_302"],
    "evidence": ["bsa_45", "bsa_5"],
    "criminal breach of trust": ["bns_316", "ipc_405"],
    "cheating": ["bns_318", "ipc_415"],
    "assault": ["bns_115", "ipc_351"],
    "defamation": ["bns_356", "ipc_499"],
    # Add more as needed
}

def expand_with_definitions(
    query: str,
    results: Dict,
    max_definitions: int = 2
) -> Dict:
    """
    Add definition sections if query mentions key concepts
    """
    lookup = get_lookup()
    query_lower = query.lower()
    
    # Track what we already have
    existing_ids = set()
    if results.get('metadatas'):
        for meta in results['metadatas']:
            chunk_id = f"{meta.get('act', '').lower()}_{meta.get('section', '')}"
            existing_ids.add(chunk_id)
    
    # Check for definition sections
    definitions_added = 0
    for concept, section_ids in DEFINITION_SECTIONS.items():
        if concept in query_lower and definitions_added < max_definitions:
            for section_id in section_ids:
                if section_id not in existing_ids:
                    chunk = lookup.get_chunk(section_id)
                    if chunk:
                        # Prepend to results (definitions come first)
                        results['documents'].insert(0, chunk['content'])
                        results['metadatas'].insert(0, {
                            'section': chunk['section'],
                            'section_display': chunk.get('section_display', f"Section {chunk['section']}"),
                            'heading': chunk.get('heading', ''),
                            'act': section_id.split('_')[0].upper(),
                            'is_definition': True
                        })
                        existing_ids.add(section_id)
                        definitions_added += 1
                        logger.info(f"Added definition: {section_id}")
                        
                        if definitions_added >= max_definitions:
                            break
    
    return results

def expand_with_references(
    results: Dict,
    max_expand: int = 2
) -> Dict:
    """
    Add cross-referenced sections (if chunk data has 'references' field)
    This requires your chunks to have a 'references' field
    """
    lookup = get_lookup()
    
    # Track existing to avoid duplicates
    existing_ids = set()
    if results.get('metadatas'):
        for meta in results['metadatas']:
            chunk_id = f"{meta.get('act', '').lower()}_{meta.get('section', '')}"
            existing_ids.add(chunk_id)
    
    # Collect references
    references_to_add = []
    
    for meta in results.get('metadatas', []):
        chunk_id = f"{meta.get('act', '').lower()}_{meta.get('section', '')}"
        chunk = lookup.get_chunk(chunk_id)
        
        if chunk and 'references' in chunk:
            for ref_id in chunk['references'][:max_expand]:
                if ref_id not in existing_ids:
                    ref_chunk = lookup.get_chunk(ref_id)
                    if ref_chunk:
                        references_to_add.append({
                            'content': ref_chunk['content'],
                            'meta': {
                                'section': ref_chunk['section'],
                                'section_display': ref_chunk.get('section_display', f"Section {ref_chunk['section']}"),
                                'heading': ref_chunk.get('heading', ''),
                                'act': ref_id.split('_')[0].upper(),
                                'is_reference': True
                            }
                        })
                        existing_ids.add(ref_id)
    
    # Add references to results
    for ref in references_to_add:
        results['documents'].append(ref['content'])
        results['metadatas'].append(ref['meta'])
    
    if references_to_add:
        logger.info(f"Added {len(references_to_add)} cross-referenced sections")
    
    return results