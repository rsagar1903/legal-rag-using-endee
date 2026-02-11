"""ID-based chunk lookup system (source of truth for legal text)"""
import json
import os
from typing import Dict, Optional
from error_handler import logger

class ChunkLookup:
    """Manages ID-based lookup for full legal text"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.id_maps: Dict[str, Dict[str, str]] = {}
        self._load_id_maps()
    
    def _load_id_maps(self):
        """Load all ID maps into memory"""
        acts = ["bns", "ipc", "crpc", "cpc", "bsa"]
        
        for act in acts:
            map_path = os.path.join(self.data_dir, f"{act}_id_map.json")
            
            if os.path.exists(map_path):
                with open(map_path, 'r', encoding='utf-8') as f:
                    self.id_maps[act] = json.load(f)
                logger.info(f"Loaded {len(self.id_maps[act])} chunks for {act.upper()}")
            else:
                logger.warning(f"ID map not found: {map_path}")
                self.id_maps[act] = {}
    
    def get_chunk(self, chunk_id: str) -> Optional[Dict]:
        """Get chunk by ID (e.g., 'bns_303_12')"""
        try:
            act = chunk_id.split('_')[0]
            if act in self.id_maps:
                return self.id_maps[act].get(chunk_id)
        except Exception as e:
            logger.error(f"Error fetching chunk {chunk_id}: {e}")
        return None
    
    def get_chunks_by_section(self, act: str, section: str) -> list:
        """Get all chunks for a specific section"""
        if act not in self.id_maps:
            return []
        
        return [
            chunk for chunk_id, chunk in self.id_maps[act].items()
            if chunk.get('section') == section
        ]
    
    def search_by_keyword(self, act: str, keyword: str) -> list:
        """Simple keyword search within an act"""
        if act not in self.id_maps:
            return []
        
        keyword_lower = keyword.lower()
        results = []
        
        for chunk_id, chunk in self.id_maps[act].items():
            if keyword_lower in chunk.get('content', '').lower():
                results.append(chunk)
        
        return results

# Global instance
_lookup = None

def get_lookup() -> ChunkLookup:
    """Get singleton ChunkLookup instance"""
    global _lookup
    if _lookup is None:
        _lookup = ChunkLookup()
    return _lookup