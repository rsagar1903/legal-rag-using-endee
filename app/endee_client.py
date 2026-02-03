from endee import Endee, Precision

# Connect once
client = Endee()
client.set_base_url("http://localhost:8080/api/v1")


def create_index(index_name: str, dim: int = 384):
    client.create_index(
        name=index_name,
        dimension=dim,
        space_type="cosine",
        precision=Precision.INT8D
    )


def insert_vector(index_name: str, vec_id: str, embedding, metadata):
    index = client.get_index(name=index_name)

    index.upsert([
        {
            "id": vec_id,
            "vector": [float(x) for x in embedding],
            "meta": metadata
        }
    ])


def search_vector(index_name: str, embedding, top_k: int = 5):
    index = client.get_index(name=index_name)

    results = index.query(
        vector=[float(x) for x in embedding],
        top_k=top_k
    )

    # SDK already returns clean Python objects
    formatted = []
    for r in results:
        formatted.append({
            "score": r.score,
            "id": r.id,
            "meta": r.meta
        })

    return formatted
