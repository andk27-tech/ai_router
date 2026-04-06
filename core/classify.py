def classify(text: str) -> str:
    t = text.lower()

    # 키워드 기반 1차 분류
    if any(k in t for k in ["검색", "찾아", "search"]):
        return "search"

    if any(k in t for k in ["수정", "고쳐", "실행", "run"]):
        return "act"

    if any(k in t for k in ["읽어", "파일", "로그"]):
        return "read"

    # 기본값
    return "chat"
