#!/usr/bin/env python3
"""
노드 테스트 - AI 처리 로직 확인 (충돌 테스트)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 테스트 모드 설정
from core.test_policy import set_test_mode, TestMode
set_test_mode(TestMode.DUMMY_1)

def test_node_conflict():
    """노드 충돌 테스트"""
    print("=" * 60)
    print("🧪 노드(node) 충돌 테스트 시작")
    print("=" * 60)
    
    # 1. core/node.py의 ai_call 테스트
    print("1️⃣ core/node.py의 ai_call 테스트:")
    try:
        from core.node import ai_call as node_ai_call
        
        test_text = "테스트 입력"
        result_expand = node_ai_call(test_text, "expand")
        result_balance = node_ai_call(test_text, "balance")
        result_refine = node_ai_call(test_text, "refine")
        
        print(f"   expand: {result_expand}")
        print(f"   balance: {result_balance}")
        print(f"   refine: {result_refine}")
        
    except Exception as e:
        print(f"   ❌ node.py ai_call 오류: {e}")
    
    print("\n2️⃣ core/ai.py의 ai_call 테스트:")
    try:
        from core.ai import ai_call as core_ai_call
        
        test_text = "테스트 입력"
        result_expand = core_ai_call(test_text, "expand")
        result_balance = core_ai_call(test_text, "balance")
        result_refine = core_ai_call(test_text, "refine")
        
        print(f"   expand: {result_expand[:50]}...")
        print(f"   balance: {result_balance[:50]}...")
        print(f"   refine: {result_refine[:50]}...")
        
    except Exception as e:
        print(f"   ❌ core/ai.py ai_call 오류: {e}")
    
    print("\n3️⃣ import 순서에 따른 충돌 테스트:")
    try:
        # agents.py에서의 import 순서 시뮬레이션
        from core.node import ai_call  # 이것이 먼저 임포트되면?
        from core.ai import ai_call    # 이것이 덮어쓰나?
        
        test_text = "테스트 입력"
        result = ai_call(test_text, "expand")
        print(f"   최종 ai_call 결과: {result[:50]}...")
        print(f"   결과 타입: {type(result)}")
        
    except Exception as e:
        print(f"   ❌ 충돌 테스트 오류: {e}")
    
    return True

if __name__ == "__main__":
    test_node_conflict()
    print(f"\n🎯 노드 충돌 테스트 완료")
