from app.endee_client import insert_vector

vec = [0.1, 0.2, 0.3, 0.4]
insert_vector(
    "test_idx",
    "py_v1",
    vec,
    {"a": 1},
    "hello from python"
)
