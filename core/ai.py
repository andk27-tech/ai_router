import subprocess
from .test_policy import get_test_policy, TestMode

MODEL = "qwen2.5-coder:3b"

def ai_call(prompt: str, policy: str = None) -> str:
    """
    AI 호출 함수 - 테스트 정책에 따라 더미 또는 실제 AI 사용
    
    Args:
        prompt: AI에게 전달할 프롬프트
        policy: 에이전트 정책 (더미 응답 생성 시 사용)
    
    Returns:
        AI 응답 또는 더미 응답
    """
    test_policy = get_test_policy()
    
    # 더미 테스트 모드인 경우
    if test_policy.should_use_dummy():
        return test_policy.get_dummy_response(prompt, policy)
    
    # 로컬 AI 모드인 경우
    if test_policy.should_use_local_ai():
        result = subprocess.run(
            ["ollama", "run", MODEL],
            input=prompt,
            text=True,
            capture_output=True
        )
        return result.stdout.strip()
    
    # 기본적으로 로컬 AI 사용
    result = subprocess.run(
        ["ollama", "run", MODEL],
        input=prompt,
        text=True,
        capture_output=True
    )
    return result.stdout.strip()
