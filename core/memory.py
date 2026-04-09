from collections import deque

MEMORY = deque(maxlen=200)  # 🔥 제한 걸기

def save(entry):
    MEMORY.append(entry)

def get_success():
    return [m for m in MEMORY if m["score"] >= 10]

def get_recent(n=10):
    return list(MEMORY)[-n:]
