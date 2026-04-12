import random

def evolve(policy):
    """정책 진화 - 다양한 변형 생성"""
    # 기본 변형
    basic_mutations = ["v2", "fast", "deep", "plus", "x", "pro", "max", "ultra"]
    
    # 정책별 특화 변형
    policy_specific_mutations = {
        "refine": ["clean", "precise", "structured", "minimal", "focused"],
        "balance": ["harmony", "stable", "moderate", "equal", "symmetric"],
        "expand": ["wide", "broad", "comprehensive", "detailed", "extensive"],
        "expand_deep": ["thorough", "intensive", "profound", "exhaustive", "systematic"]
    }
    
    if "_" in policy:
        base = policy.split("_")[0]
    else:
        base = policy
    
    # 70% 확률로 정책별 특화 변형, 30% 확률로 기본 변형
    if base in policy_specific_mutations and random.random() < 0.7:
        mutation = random.choice(policy_specific_mutations[base])
    else:
        mutation = random.choice(basic_mutations)
    
    return f"{base}_{mutation}"

def next_generation(winner_policy):
    """다음 세대 정책 생성 - 다양성 강화"""
    # 기존 정책 유지
    policies = [winner_policy]
    
    # 진화된 정책 추가
    evolved_policy = evolve(winner_policy)
    policies.append(evolved_policy)
    
    # 대조 정책 추가 (승자와 다른 특성)
    base_policies = ["refine", "balance", "expand", "expand_deep"]
    
    if "_" in winner_policy:
        winner_base = winner_policy.split("_")[0]
    else:
        winner_base = winner_policy
    
    # 승자와 다른 특성의 정책 선택
    contrast_policies = [p for p in base_policies if p != winner_base]
    if contrast_policies:
        contrast_policy = random.choice(contrast_policies)
        policies.append(contrast_policy)
    
    # 때로는 완전히 새로운 조합 시도 (30% 확률)
    if random.random() < 0.3:
        hybrid_base1 = random.choice(base_policies)
        hybrid_base2 = random.choice([p for p in base_policies if p != hybrid_base1])
        hybrid_policy = f"{hybrid_base1}_{hybrid_base2}_hybrid"
        policies.append(hybrid_policy)
    
    # 중복 제거하고 최소 3개 보장
    unique_policies = list(set(policies))
    while len(unique_policies) < 3:
        fallback = random.choice(base_policies)
        if fallback not in unique_policies:
            unique_policies.append(fallback)
    
    return unique_policies[:4]  # 최대 4개 정책 반환
