#!/usr/bin/env python3
"""
Simple CLI Test - 기본 기능만 테스트
"""

import sys
sys.path.append('/home/lks/ai_router')

print("🧪 AI Router CLI 기능 테스트\n")

# Test 1: Intent Parser
print("1️⃣ Intent Parser 테스트")
try:
    from core.intent import IntentParser
    parser = IntentParser()
    result = parser.parse("로그 보여줘")
    print(f"   ✅ 의도: {result.intent_type.value}")
except Exception as e:
    print(f"   ❌ 오류: {e}")

# Test 2: System Tool
print("\n2️⃣ System Tool 테스트")
try:
    from core.tools.system_tool import SystemTool
    tool = SystemTool()
    result = tool.get_system_summary()
    if result.get('success'):
        print(f"   ✅ 시스템 상태: {result['overall_status']}")
        print(f"   CPU: {result['cpu']['percent']}%")
    else:
        print(f"   ⚠️ 결과: {result}")
except Exception as e:
    print(f"   ❌ 오류: {e}")

# Test 3: Log Integration
print("\n3️⃣ Log Integration 테스트")
try:
    from core.tools.log_integration_extended import SystemLogIntegration
    log_int = SystemLogIntegration()
    log_int.grant_permissions('test', ['syslog'], True, 10)
    result = log_int.get_system_log_access('test', ['syslog'], 5)
    if result.get('success'):
        print(f"   ✅ 로그 접근 성공: {result['total_logs']}개")
    else:
        print(f"   ⚠️ 접근 실패: {result.get('error', 'unknown')}")
except Exception as e:
    print(f"   ❌ 오류: {e}")

# Test 4: Memory
print("\n4️⃣ Memory 테스트")
try:
    from core.memory import save, get_recent
    save({'test': 'data', 'score': 10})
    recent = get_recent(1)
    print(f"   ✅ 메모리 저장/조회 성공: {len(recent)}개")
except Exception as e:
    print(f"   ❌ 오류: {e}")

# Test 5: Agents
print("\n5️⃣ Agents (run_agents) 테스트")
try:
    from core.agents import run_agents
    from core.ai import ai_call
    from core.test_policy import set_test_mode, TestMode
    
    # 더미 모드로 테스트
    set_test_mode(TestMode.DUMMY_1)
    
    winner, results = run_agents(ai_call, "테스트")
    print(f"   ✅ 에이전트 실행: {len(results)}개 결과")
    print(f"   승자: {winner['policy']} (점수: {winner['score']:.1f})")
except Exception as e:
    print(f"   ❌ 오류: {e}")

print("\n✅ 테스트 완료!")
