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

    winner = max(results, key=lambda x: x["score"])

    return winner, results
