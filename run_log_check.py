#!/usr/bin/env python3
"""
AI Router Log Check - 통합 실행 파일
로컬 AI(Ollama) + 의도 분석 + 실제 로그 확인
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.intent import IntentParser
from core.intent_integration import IntentBasedRouter
from core.tools.log_integration_extended import SystemLogIntegration, quick_system_log_check
from core.tools.system_tool import SystemTool
from core.ai import ai_call
from core.test_policy import set_test_mode, TestMode

def check_logs_with_ai(user_input: str, agent_id: str = "user"):
    """
    사용자 입력을 받아서 AI가 로그를 확인하고 답변
    
    Args:
        user_input: 사용자 입력 (예: "syslog 에러 확인해줘")
        agent_id: 사용자/에이전트 ID
        
    Returns:
        AI 응답
    """
    # 실제 Ollama AI 사용하도록 설정
    set_test_mode(TestMode.LOCAL_AI)
    
    print(f"📝 입력: {user_input}")
    print("-" * 50)
    
    # 1. 의도 파악
    print("1️⃣ 의도 분석 중...")
    intent_parser = IntentParser()
    intent = intent_parser.parse(user_input)
    print(f"   의도: {intent.intent_type.value} (신뢰도: {intent.confidence:.2f})")
    
    # 2. 라우팅 결정
    print("2️⃣ 라우팅 중...")
    router = IntentBasedRouter()
    routing = router.recognize_intent_and_route(user_input)
    print(f"   선택된 정책: {routing['routing']['selected_policy']}")
    
    # 3. 로그 수집 (실제 시스템 데이터)
    print("3️⃣ 실제 시스템 로그 수집 중...")
    log_integration = SystemLogIntegration()
    
    # 권한 부여
    log_integration.grant_permissions(
        agent_id=agent_id,
        log_types=['syslog', 'daemon', 'kern'],
        read_only=True,
        max_lines=100
    )
    
    # 로그 수집
    log_result = log_integration.get_system_log_access(
        agent_id=agent_id,
        log_types=['syslog'],
        lines=50
    )
    
    # 에러 분석
    error_result = log_integration.analyze_system_errors(
        agent_id=agent_id,
        hours=1,
        severity='error'
    )
    
    # 프로세스 정보
    proc_result = log_integration.get_process_log(
        agent_id=agent_id,
        lines=10
    )
    
    # CPU 및 메모리 정보 수집
    print("   CPU 및 메모리 정보 수집 중...")
    system_tool = SystemTool()
    cpu_info = system_tool.get_cpu_info()
    memory_info = system_tool.get_memory_info()
    
    cpu_data = cpu_info.get('cpu', {}) if cpu_info.get('success') else {}
    memory_data = memory_info.get('memory', {}) if memory_info.get('success') else {}
    
    # 4. AI에 분석 요청
    print("4️⃣ AI(Ollama) 분석 중...")
    
    # 로그 데이터 준비
    log_data = {
        'syslog_accessed': log_result.get('success', False),
        'recent_errors': error_result.get('total_errors', 0),
        'error_types': error_result.get('error_types', {}),
        'system_status': 'healthy' if error_result.get('total_errors', 0) < 5 else 'warning',
        'log_preview': log_result.get('logs_accessed', {}).get('syslog', {}).get('content_preview', '')[:500],
        'cpu_percent': cpu_data.get('percent', 0),
        'cpu_status': cpu_data.get('status', 'unknown'),
        'memory_percent': memory_data.get('percent_used', 0),
        'memory_available_gb': memory_data.get('available_gb', 0)
    }
    
    # AI 프롬프트 생성
    prompt = f"""당신은 시스템 관리자입니다. 다음 로그 정보를 분석하고 한국어로 설명해주세요.

사용자 질문: {user_input}

수집된 시스템 정보:
- syslog 접근: {'성공' if log_data['syslog_accessed'] else '실패'}
- 최근 1시간 에러 수: {log_data['recent_errors']}개
- 에러 유형: {log_data['error_types']}
- 시스템 상태: {log_data['system_status']}
- CPU 사용량: {log_data['cpu_percent']}% (상태: {log_data['cpu_status']})
- 메모리 사용량: {log_data['memory_percent']}% (사용 가능: {log_data['memory_available_gb']} GB)

syslog 미리보기 (처음 500자):
{log_data['log_preview']}

간결하고 이해하기 쉽게 설명해주세요."""
    
    # AI 호출 (Ollama)
    try:
        ai_response = ai_call(prompt)
        print(f"\n🤖 AI 응답:\n{ai_response}")
        return ai_response
    except Exception as e:
        print(f"❌ AI 호출 실패: {e}")
        # AI 실패시 기본 응답
        return f"시스템 로그 분석 결과:\n- 최근 에러: {log_data['recent_errors']}개\n- 상태: {log_data['system_status']}"

if __name__ == "__main__":
    # 명령줄 인자로 입력 받기
    if len(sys.argv) > 1:
        user_input = ' '.join(sys.argv[1:])
    else:
        # 기본 테스트 입력
        user_input = "syslog 최근 에러 확인해줘"
    
    print("=" * 60)
    print("🚀 AI Router 로그 확인 시스템")
    print("=" * 60)
    
    result = check_logs_with_ai(user_input)
    
    print("\n" + "=" * 60)
    print("✅ 분석 완료")
    print("=" * 60)
