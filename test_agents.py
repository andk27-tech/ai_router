#!/usr/bin/env python3
"""
에이전트 테스트 - refine/balance/expand 정책별 동작 확인
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 테스트 모드 설정
from core.test_policy import set_test_mode, TestMode
set_test_mode(TestMode.DUMMY_1)

from core.agents import run_agents
from core.ai import ai_call

def test_agents():
    """에이전트 테스트"""
    print("=" * 60)
    print("🧪 에이전트(agents) 테스트 시작")
    print("=" * 60)
    
    # 테스트 입력
    test_input = "AI 라우터 프로젝트의 핵심 기능을 설명해줘"
    
    print(f"📥 입력: {test_input}")
    print("\n🔄 run_agents() 실행 중...")
    
    try:
        # 에이전트 실행
        winner, all_results = run_agents(ai_call, test_input)
        
        print(f"\n✅ 에이전트 실행 완료")
        print(f"📊 총 {len(all_results)}개 에이전트 결과")
        
        # 각 에이전트 결과 확인
        print("\n📋 에이전트별 결과:")
        for i, result in enumerate(all_results, 1):
            policy = result['policy']
            score = result['score']
            output = result['output'][:50] + "..." if len(result['output']) > 50 else result['output']
            print(f"   {i}. {policy}: {score:.1f}점 - {output}")
        
        # 승자 정보
        print(f"\n🏆 승자 에이전트:")
        print(f"   정책: {winner['policy']}")
        print(f"   점수: {winner['score']:.1f}")
        print(f"   결과: {winner['output'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 에이전트 실행 오류: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_agents()
    print(f"\n🎯 테스트 결과: {'성공' if success else '실패'}")
