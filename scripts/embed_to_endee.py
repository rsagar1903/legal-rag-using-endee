"""
Embed chunks to Endee - FIXED VERSION
- Uses chunk IDs (not UUIDs)
- Stores only metadata in Endee (not full text)
- Full text stays in JSON files
"""
import sys
import os
import json
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from endee import Endee, Precision

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

ACTS_CONFIG = {
    "bns": "data/bns_chunks.json",
    "ipc": "data/ipc_chunks.json",
    "crpc": "data/crpc_chunks.json",
    "cpc": "data/cpc_chunks.json",
    "bsa": "data/bsa_chunks.json",
}

# Initialize
client = Endee()
# Use the same logic to support Docker networking
ENDEE_URL = os.getenv("ENDEE_HOST", "http://localhost:8080/api/v1")
client.set_base_url(ENDEE_URL)
model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_act(act_name, file_path):
    print(f"\n{'='*60}")
    print(f"Processing {act_name.upper()}")
    print(f"{'='*60}")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    index_name = f"{act_name}_sections"
    
    # Create index
    try:
        client.create_index(
            name=index_name,
            dimension=384,
            space_type="cosine",
            precision=Precision.INT8D
        )
        print(f"✅ Created index: {index_name}")
    except Exception as e:
        print(f"⚠️  Index exists or error: {e}")
    
    # Get index
    try:
        index = client.get_index(name=index_name)
    except Exception as e:
        print(f"❌ Failed to get index: {e}")
        return
    
    # Load chunks
    with open(file_path, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"📄 Loaded {len(chunks)} chunks")
    
    # Prepare batch
    batch_size = 50
    batch_payload = []
    total_embedded = 0
    
    print(f"🔄 Embedding chunks...")
    
    for idx, chunk in enumerate(tqdm(chunks)):
        # Generate embedding
        embedding = model.encode(chunk["content"])
        
        # Use chunk's ID or generate one
        chunk_id = chunk.get('id')
        if not chunk_id:
            chunk_id = f"{act_name}_{chunk.get('section', '0')}_{idx}"
        
        # Create item - ONLY METADATA, NO FULL TEXT
        item = {
            "id": chunk_id,
            "vector": embedding.tolist(),
            "meta": {
                "section": chunk.get("section", ""),
                "section_display": chunk.get("section_display", f"Section {chunk.get('section', '')}"),
                "heading": chunk.get("heading", ""),
                "chapter": chunk.get("chapter", ""),
                "act": act_name.upper()
                # NO 'document' or 'content' field!
            }
        }
        
        batch_payload.append(item)
        
        # Upsert batch
        if len(batch_payload) >= batch_size:
            try:
                index.upsert(batch_payload)
                total_embedded += len(batch_payload)
                batch_payload = []
            except Exception as e:
                print(f"\n❌ Batch upsert failed: {e}")
                batch_payload = []  # Skip this batch
    
    # Upsert remaining
    if batch_payload:
        try:
            index.upsert(batch_payload)
            total_embedded += len(batch_payload)
        except Exception as e:
            print(f"\n❌ Final batch failed: {e}")
    
    print(f"\n✅ {act_name.upper()} complete: {total_embedded}/{len(chunks)} chunks embedded")

def main():
    print("\n🚀 Starting Endee embedding process...\n")
    
    for act, path in ACTS_CONFIG.items():
        embed_act(act, path)
    
    print("\n" + "="*60)
    print("✅ ALL ACTS EMBEDDED SUCCESSFULLY!")
    print("="*60)

if __name__ == "__main__":
    main()