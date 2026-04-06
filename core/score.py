def score_node(node: str):
    score = 0

    if "ask_llm" in node:
        score += 10
    if "search" in node:
        score += 8
    if "rag" in node:
        score += 7
    if "json" in node:
        score -= 10

    return score
