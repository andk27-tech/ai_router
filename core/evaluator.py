def evaluate(output, policy=None):
    """
    평가 시스템 고도화 - 정책별 차별화 강화
    
    Args:
        output: AI 응답 출력
        policy: 정책 타입
    
    Returns:
        tuple: (점수 1-10, 평가 이유)
    """
    text = output.lower()
    
    # 기본 점수 (모든 정책 공통)
    base = 4.0
    
    # 길이 평가 (정책별 다른 기준)
    length_score = evaluate_length(text, policy)
    base += length_score
    
    # 정책별 특화 평가
    if policy and policy.startswith("expand"):
        base += evaluate_expand_policy(text, policy)
    elif policy and policy.startswith("refine"):
        base += evaluate_refine_policy(text, policy)
    elif policy and policy.startswith("balance"):
        base += evaluate_balance_policy(text, policy)
    else:
        # 기본 평가
        base += evaluate_generic(text)
    
    # 품질 보너스/패널티
    quality_adjustment = evaluate_quality(text, policy)
    base += quality_adjustment
    
    # 최종 점수 (1-10점)
    score = max(1.0, min(10.0, base))
    
    return round(score, 1), f"enhanced-{policy or 'generic'}"

def evaluate_length(text, policy):
    """정책별 길이 평가"""
    length = len(text)
    
    if policy and policy.startswith("expand"):
        # expand: 길수록 높은 점수
        if length < 100:
            return -1.0
        elif length < 300:
            return 0.5
        elif length < 600:
            return 1.5
        elif length < 1000:
            return 2.0
        else:
            return 1.5  # 너무 길면 약간 패널티
            
    elif policy and policy.startswith("refine"):
        # refine: 적당한 길이 최적
        if length < 50:
            return -1.5
        elif length < 200:
            return 1.0
        elif length < 400:
            return 1.5
        elif length < 600:
            return 0.5
        else:
            return -0.5
            
    elif policy and policy.startswith("balance"):
        # balance: 중간 길이 선호
        if length < 80:
            return -1.0
        elif length < 250:
            return 1.0
        elif length < 500:
            return 1.5
        elif length < 800:
            return 0.5
        else:
            return -0.5
    
    # 기본
    return min(length / 200, 1.5)

def evaluate_expand_policy(text, policy):
    """expand 정책 평가"""
    score = 0
    
    # 확장성 키워드
    expand_keywords = [
        "확장", "확장성", "스케일", "규모", "성장", "발전", "진화",
        "모듈", "플러그인", "api", "연동", "통합", "분산",
        "다양", "여러", "각각", "다중", "여러 가지"
    ]
    keyword_count = sum(1 for kw in expand_keywords if kw in text)
    score += min(keyword_count * 0.3, 2.0)
    
    # 목록/구조화 지표
    list_indicators = text.count("|") + text.count("•") + text.count("-") + text.count("*")
    score += min(list_indicators * 0.2, 1.5)
    
    # 기술적 용어
    tech_terms = ["아키텍처", "시스템", "프레임워크", "플랫폼", "인프라"]
    tech_count = sum(1 for term in tech_terms if term in text)
    score += min(tech_count * 0.4, 1.0)
    
    # expand_deep 특화
    if policy == "expand_deep":
        deep_keywords = ["상세", "구체적", "분석", "심층", "깊이", "체계적"]
        deep_count = sum(1 for kw in deep_keywords if kw in text)
        score += min(deep_count * 0.5, 1.5)
    
    return score

def evaluate_refine_policy(text, policy):
    """refine 정책 평가"""
    score = 0
    
    # 정제/정리 키워드
    refine_keywords = [
        "정리", "정제", "명확", "체계", "구조", "정돈",
        "핵심", "요약", "요점", "중요", "필수", "기본"
    ]
    keyword_count = sum(1 for kw in refine_keywords if kw in text)
    score += min(keyword_count * 0.4, 2.0)
    
    # 번호 매기기/구조화
    numbered_items = text.count("1.") + text.count("2.") + text.count("3.") + text.count("4.")
    score += min(numbered_items * 0.3, 1.5)
    
    # 간결성
    sentences = text.count(".") + text.count("!") + text.count("?")
    if sentences > 0:
        avg_sentence_length = len(text) / sentences
        if 10 <= avg_sentence_length <= 30:  # 적당한 문장 길이
            score += 0.5
    
    return score

def evaluate_balance_policy(text, policy):
    """balance 정책 평가"""
    score = 0
    
    # 균형 키워드
    balance_keywords = [
        "균형", "조화", "균등", "평형", "안정", "안정성",
        "다양", "여러", "모두", "각각", "함께", "동시"
    ]
    keyword_count = sum(1 for kw in balance_keywords if kw in text)
    score += min(keyword_count * 0.3, 1.5)
    
    # 대조 표현
    contrast_words = ["vs", "반면", "동시에", "하지만", "그러나", "또한"]
    contrast_count = sum(1 for word in contrast_words if word in text)
    score += min(contrast_count * 0.2, 1.0)
    
    # 균형적 구조
    balance_patterns = ["a와 b", "a와 b의", "a와 b를", "a와 b는"]
    pattern_count = sum(1 for pattern in balance_patterns if pattern in text)
    score += min(pattern_count * 0.3, 1.0)
    
    return score

def evaluate_generic(text):
    """기본 평가"""
    score = 0
    
    # 기본 키워드 다양성
    words = text.split()
    unique_words = len(set(words))
    if len(words) > 0:
        diversity_ratio = unique_words / len(words)
        score += min(diversity_ratio * 2, 1.5)
    
    # 문장 구조
    sentences = text.count(".") + text.count("!") + text.count("?")
    if sentences >= 3:  # 최소 3개 문장
        score += 0.5
    
    return score

def evaluate_quality(text, policy):
    """품질 평가 (보너스/패널티)"""
    adjustment = 0
    
    # 반복 패널티
    words = text.lower().split()
    if len(words) > 10:
        repeated_ratio = (len(words) - len(set(words))) / len(words)
        if repeated_ratio > 0.3:  # 30% 이상 반복
            adjustment -= 1.0
        elif repeated_ratio > 0.2:  # 20% 이상 반복
            adjustment -= 0.5
    
    # 의미 있는 내용 보너스
    meaningful_patterns = ["핵심", "중요", "필수", "주요", "기본", "필요"]
    pattern_count = sum(1 for pattern in meaningful_patterns if pattern in text)
    adjustment += min(pattern_count * 0.2, 0.5)
    
    return adjustment
