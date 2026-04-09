def ai_call(text, policy="refine"):
    if policy == "expand":
        return f"processed: {text} | 확장모드 | 정보증폭"
    elif policy == "balance":
        return f"processed: {text} | 균형모드 | 구조정리"
    else:
        return f"processed: {text} | 정리모드 | 최소처리"
