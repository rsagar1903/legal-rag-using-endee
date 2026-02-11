"""
Build ID maps from existing chunk files
Run this ONCE to create id_map.json files
"""
import json
import os

ACTS_CONFIG = {
    "bns": "../data/bns_chunks.json",
    "ipc": "../data/ipc_chunks.json",
    "crpc": "../data/crpc_chunks.json",
    "cpc": "../data/cpc_chunks.json",
    "bsa": "../data/bsa_chunks.json",
}

def build_id_map(act_name, chunks_file):
    """Build ID → chunk mapping"""
    print(f"Building ID map for {act_name.upper()}...")
    
    if not os.path.exists(chunks_file):
        print(f"❌ File not found: {chunks_file}")
        return
    
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    # Create ID map
    id_map = {}
    for chunk in chunks:
        chunk_id = chunk.get('id')
        if not chunk_id:
            # Generate ID if missing: act_section_index
            section = chunk.get('section', '0')
            chunk_id = f"{act_name}_{section}_{len(id_map)}"
            chunk['id'] = chunk_id
        
        id_map[chunk_id] = chunk
    
    # Save ID map
    output_path = f"../data/{act_name}_id_map.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(id_map, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Created {output_path} with {len(id_map)} entries")

def main():
    for act, chunks_file in ACTS_CONFIG.items():
        build_id_map(act, chunks_file)
    
    print("\n✅ All ID maps created successfully!")

if __name__ == "__main__":
    main()