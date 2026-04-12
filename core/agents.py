from core.evaluator import evaluate
from core.policy import get_weight
from core.policy_evolve import next_generation
from core.ai import ai_call
from .test_policy import get_test_policy

def run_agents(fn, input_text):
    """
    다중 에이전트 경쟁 실행
    
    Args:
        fn: AI 호출 함수
        input_text: 입력 텍스트
    
    Returns:
        winner: 승자 에이전트 결과
        results: 모든 에이전트 결과 리스트
    """
    results = []
    test_policy = get_test_policy()

    policies = next_generation("expand")  # 🔥 seed

    for p in policies:
        # 테스트 정책에 따라 함수 호출
        if test_policy.should_use_dummy():
            out = fn(input_text, p)
        else:
            out = ai_call(f'''
정책: {p}
입력: {input_text}

위 정책에 따라 입력에 대한 응답을 생성해줘.
''', p)

        score, reason = evaluate(out, p)
        score = score * get_weight(p.split("_")[0])

        results.append({
            "policy": p,
            "output": out,
            "score": score,
            "reason": reason
        })

    winner = select_winner_with_tie_breaking(results)

    return winner, results

def select_winner_with_tie_breaking(results):
    """
    동점자 처리 로직 - 추가 평가 기준 도입
    
    Args:
        results: 모든 에이전트 결과 리스트
    
    Returns:
        winner: 승자 에이전트 결과
    """
    if not results:
        return None
    
    # 최고 점수 찾기
    max_score = max(result["score"] for result in results)
    top_candidates = [result for result in results if result["score"] == max_score]
    
    # 동점자가 없으면 바로 반환
    if len(top_candidates) == 1:
        return top_candidates[0]
    
    # 동점자 처리 로직
    print(f"[TIE] {len(top_candidates)}개 동점자 발생: {[r['policy'] for r in top_candidates]}")
    
    # 1차 기준: 응답 길이 (너무 짧은 응답 패널티)
    length_scores = []
    for result in top_candidates:
        output_length = len(result["output"])
        # 너무 짧으면 패널티, 적당하면 보너스
        if output_length < 50:
            length_penalty = -2.0
        elif output_length < 100:
            length_penalty = -1.0
        elif 100 <= output_length <= 500:
            length_penalty = 0.5  # 적당한 길이 보너스
        elif output_length <= 1000:
            length_penalty = 0.2
        else:
            length_penalty = -0.5  # 너무 길면 패널티
        
        length_scores.append((result, length_penalty))
    
    # 길이 점수로 정렬
    length_scores.sort(key=lambda x: x[1], reverse=True)
    best_by_length = length_scores[0][0]
    
    # 여전히 동점이면 2차 기준: 정책 다양성 보너스
    still_tied = len(length_scores) > 1 and length_scores[0][1] == length_scores[1][1]
    
    if still_tied:
        # 정책별 우선순위 (다양성 확보)
        policy_priority = {
            "refine": 3,
            "balance": 2, 
            "expand": 1,
            "expand_deep": 4
        }
        
        # 기본 정책 추출
        def get_base_policy(policy):
            return policy.split("_")[0] if "_" in policy else policy
        
        priority_scores = []
        for result in top_candidates:
            base_policy = get_base_policy(result["policy"])
            priority = policy_priority.get(base_policy, 0)
            priority_scores.append((result, priority))
        
        priority_scores.sort(key=lambda x: x[1], reverse=True)
        best_by_priority = priority_scores[0][0]
        
        print(f"[TIE] 정책 우선순위로 선택: {best_by_priority['policy']}")
        return best_by_priority
    
    print(f"[TIE] 응답 길이로 선택: {best_by_length['policy']}")
    return best_by_length
