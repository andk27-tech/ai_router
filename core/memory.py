MEMORY = []

def save(record):
    record.setdefault("weight", 1.0)
    record.setdefault("strategy", "refine")
    MEMORY.append(record)

def get_memory():
    return MEMORY[-10:]

def get_success():
    return [m for m in MEMORY if m["score"] >= 10]

def best_strategy():
    if not MEMORY:
        return "refine"

    # 최근 성공 기준으로 전략 선택
    success = [m for m in MEMORY if m["score"] >= 10]
    if not success:
        return "refine"

    # 가장 많이 성공한 strategy 선택
    counts = {}
    for s in success:
        st = s.get("strategy", "refine")
        counts[st] = counts.get(st, 0) + 1

    return max(counts, key=counts.get)
