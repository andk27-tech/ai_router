import subprocess
import sys
from typing import Optional, Callable
from .test_policy import get_test_policy, TestMode

MODEL = "qwen2.5-coder:3b"

def ai_call(prompt: str, policy: str = None, stream: bool = False, 
            callback: Optional[Callable[[str], None]] = None) -> str:
    """
    AI 호출 함수 - 테스트 정책에 따라 더미 또는 실제 AI 사용
    
    Args:
        prompt: AI에게 전달할 프롬프트
        policy: 에이전트 정책 (더미 응답 생성 시 사용)
        stream: 실시간 스트리밍 여부
        callback: 스트리밍 시 각 청크 처리 콜백 함수
    
    Returns:
        AI 응답 또는 더미 응답
    """
    test_policy = get_test_policy()
    
    # 더미 테스트 모드인 경우
    if test_policy.should_use_dummy():
        response = test_policy.get_dummy_response(prompt, policy)
        if stream and callback:
            callback(response)
        return response
    
    # 스트리밍 모드
    if stream:
        return _ai_call_streaming(prompt, callback)
    
    # 기본 동기 모드
    result = subprocess.run(
        ["ollama", "run", MODEL],
        input=prompt,
        text=True,
        capture_output=True
    )
    return result.stdout.strip()

def _ai_call_streaming(prompt: str, callback: Optional[Callable[[str], None]] = None) -> str:
    """
    스트리밍 모드로 AI 호출 - 실시간 출력 (UTF-8 안전)
    """
    full_response = []
    byte_buffer = bytearray()
    
    # Ollama 실행
    process = subprocess.Popen(
        ["ollama", "run", MODEL],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0,
        universal_newlines=False
    )
    
    # 프롬프트 전송
    process.stdin.write(prompt.encode('utf-8'))
    process.stdin.flush()
    process.stdin.close()
    
    # UTF-8 안전한 스트리밍
    while True:
        byte = process.stdout.read(1)
        if not byte:
            break
        
        byte_buffer.extend(byte)
        
        # 완전한 UTF-8 문자가 있는지 확인
        try:
            text = byte_buffer.decode('utf-8')
            # 성공적으로 디코딩되면 출력
            for char in text:
                full_response.append(char)
                if callback:
                    callback(char)
                else:
                    print(char, end='', flush=True)
            byte_buffer = bytearray()  # 버퍼 비우기
        except UnicodeDecodeError:
            # 아직 불완전한 UTF-8 시퀀스, 더 바이트 필요
            continue
    
    # 남은 버퍼 처리
    if byte_buffer:
        try:
            remaining = byte_buffer.decode('utf-8', errors='replace')
            for char in remaining:
                if callback:
                    callback(char)
                else:
                    print(char, end='', flush=True)
                full_response.append(char)
        except:
            pass
    
    process.wait()
    return ''.join(full_response)
