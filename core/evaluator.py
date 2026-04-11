def evaluate(output, policy=None):
    text = output.lower()

    base = 5

    # 길이 보너스 (최대 3점)
    base += min(len(text) / 50, 3)

    # 정책별 평가 기준
    if policy == "expand":
        # 확장성: 목록, 구분자, 다양한 측면
        list_indicators = text.count("|") + text.count("•") + text.count("-")
        base += min(list_indicators * 0.3, 2)
        # 다양한 키워드
        diversity_bonus = len(set(text.split())) / 10
        base += min(diversity_bonus, 1)
        
    elif policy == "expand_deep":
        # 깊이 있는 확장: 상세한 설명, 구조화
        depth_indicators = text.count("상세") + text.count("구체적") + text.count("분석")
        base += min(depth_indicators * 0.5, 2)
        # 길이 보너스 추가 (더 깊은 내용)
        base += min(len(text) / 100, 1)
        
    elif policy == "balance":
        # 균형성: 다양한 관점, 균형 키워드
        balance_keywords = ["균형", "조화", "다양", "여러", "모두", "각각"]
        balance_count = sum(1 for kw in balance_keywords if kw in text)
        base += min(balance_count * 0.5, 2)
        
    elif policy == "refine":
        # 정제성: 정리, 구조화, 명확성
        refine_keywords = ["정리", "정제", "명확", "체계", "구조"]
        refine_count = sum(1 for kw in refine_keywords if kw in text)
        base += min(refine_count * 0.5, 2)
        # 명확성 보너스
        clarity_bonus = text.count("1.") + text.count("2.") + text.count("3.")
        base += min(clarity_bonus * 0.2, 1)

    # 안정화 (1-10점)
    score = int(min(10, max(1, base)))

    return score, f"policy-aware-{policy}"
