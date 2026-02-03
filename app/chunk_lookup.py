import json
import os

DATA_FILES = [
    "data/bns_chunks.json",
    "data/ipc_chunks.json",
    "data/crpc_chunks.json",
    "data/cpc_chunks.json",
    "data/bsa_chunks.json",
]

ID_MAP = {}

def load_chunks():
    global ID_MAP
    for file in DATA_FILES:
        with open(file, "r", encoding="utf-8") as f:
            chunks = json.load(f)
            for c in chunks:
                ID_MAP[c["id"]] = c

load_chunks()


def get_chunk_by_id(chunk_id: str):
    return ID_MAP.get(chunk_id)
