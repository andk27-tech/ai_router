#!/usr/bin/env python3
"""
러너 테스트 - 더미 데이터로 각 단계 확인
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 테스트 모드 설정
from core.test_policy import set_test_mode, TestMode
set_test_mode(TestMode.DUMMY_1)

from core.runner import run_node
from core.ai import ai_call

def test_runner():
    """러너 테스트"""
    print("=" * 60)
    print("🧪 러너(orchestrator) 테스트 시작")
    print("=" * 60)
    
    # 테스트 입력
    test_input = "AI 라우터 프로젝트의 핵심 기능을 설명해줘"
    
    print(f"📥 입력: {test_input}")
    print("\n🔄 run_node() 실행 중...")
    
    try:
        # 러너 실행
        result = run_node(ai_call, test_input, threshold=5, max_retry=2)
        
        print(f"\n✅ 러너 실행 완료")
        print(f"📤 결과: {result[:100]}...")
        print(f"📏 결과 길이: {len(result)} 글자")
        
        return True
        
    except Exception as e:
        print(f"❌ 러너 실행 오류: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_runner()
    print(f"\n🎯 테스트 결과: {'성공' if success else '실패'}")
