import sys
import os
import json
import uuid
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from endee import Endee, Precision # <--- Official SDK

# Fix path to see parent folders if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

ACTS_CONFIG = {
    "bns": "data/bns_chunks.json",
    "ipc": "data/ipc_chunks.json",
    "crpc": "data/crpc_chunks.json",
    "cpc": "data/cpc_chunks.json",
    "bsa": "data/bsa_chunks.json",
}

# Initialize Endee Client
client = Endee() 
model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_act(act_name, file_path):
    print(f"Processing {act_name.upper()}...")
    
    if not os.path.exists(file_path):
        print(f"Skipping {act_name}: File not found")
        return

    index_name = f"{act_name}_sections"

    # 1. Create Index (Official Way)
    # The SDK handles checking if it exists internally usually, 
    # or throws an error we can catch.
    try:
        client.create_index(
            name=index_name,
            dimension=384,
            space_type="cosine",
            precision=Precision.INT8D # Optimized storage
        )
        print(f"Created index: {index_name}")
    except Exception as e:
        # If it exists, we just proceed
        print(f"Index check ({index_name}): {e}")

    # 2. Get the Index Object
    index = client.get_index(name=index_name)

    # 3. Load Data
    with open(file_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    # 4. Prepare Batch
    batch_size = 50
    batch_payload = []

    print(f"Embedding {len(chunks)} chunks...")
    
    for chunk in tqdm(chunks):
        embedding = model.encode(chunk["content"])

        # Create Item structure for Endee SDK
        item = {
            "id": str(uuid.uuid4()), # Generate Unique ID
            "vector": embedding.tolist(),
            "meta": {
                "section": chunk.get("section", ""),
                "section_display": chunk.get("section_display", ""),
                "heading": chunk.get("heading", ""),
                "act": act_name.upper(),
                "document": chunk["content"] # Storing text!
            }
        }
        
        batch_payload.append(item)

        if len(batch_payload) >= batch_size:
            # Official SDK Upsert
            index.upsert(batch_payload)
            batch_payload = []

    # Send remaining
    if batch_payload:
        index.upsert(batch_payload)
        
    print(f"✅ {act_name} complete.")

def main():
    for act, path in ACTS_CONFIG.items():
        embed_act(act, path)

if __name__ == "__main__":
    main()