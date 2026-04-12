#!/usr/bin/env python3
"""
현재 정책 상태 확인 및 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 테스트 모드 설정
from core.test_policy import set_test_mode, TestMode
set_test_mode(TestMode.DUMMY_1)

from core.policy import get_weight, update_weight, WEIGHTS
from core.policy_evolve import next_generation, evolve
from core.policy_gen import generate_policies
from core.agents import run_agents
from core.ai import ai_call

def test_current_policies():
    """현재 정책 상태 테스트"""
    print("=" * 60)
    print("🧪 현재 정책 상태 확인 및 테스트")
    print("=" * 60)
    
    # 1. 현재 가중치 확인
    print("1️⃣ 현재 정책 가중치:")
    for policy, weight in WEIGHTS.items():
        print(f"   {policy}: {weight:.2f}")
    
    # 2. 정책 진화 테스트
    print("\n2️⃣ 정책 진화 테스트:")
    winner = "expand"
    next_gen = next_generation(winner)
    print(f"   승자 정책: {winner}")
    print(f"   다음 세대: {next_gen}")
    
    # 3. 정책 생성 테스트
    print("\n3️⃣ 정책 생성 테스트:")
    generated = generate_policies("balance")
    print(f"   생성된 정책: {generated}")
    
    # 4. 가중치 업데이트 테스트
    print("\n4️⃣ 가중치 업데이트 테스트:")
    print("   업데이트 전:")
    for policy, weight in WEIGHTS.items():
        print(f"     {policy}: {weight:.2f}")
    
    update_weight("refine")  # refine이 승자라고 가정
    
    print("   업데이트 후:")
    for policy, weight in WEIGHTS.items():
        print(f"     {policy}: {weight:.2f}")
    
    # 5. 실제 에이전트 실행으로 정책 동작 확인
    print("\n5️⃣ 실제 에이전트 실행 테스트:")
    test_input = "다양한 정책으로 응답 생성 테스트"
    
    try:
        winner, all_results = run_agents(ai_call, test_input)
        
        print(f"   입력: {test_input}")
        print(f"   실행된 정책: {[r['policy'] for r in all_results]}")
        print(f"   승자: {winner['policy']} (점수: {winner['score']:.1f})")
        
        # 각 정책의 실제 결과 확인
        print("\n   정책별 결과:")
        for result in all_results:
            policy = result['policy']
            score = result['score']
            output = result['output'][:50] + "..."
            print(f"     {policy}: {score:.1f}점 - {output}")
        
    except Exception as e:
        print(f"   ❌ 에이전트 실행 오류: {e}")
    
    return True

if __name__ == "__main__":
    test_current_policies()
    print(f"\n🎯 정책 상태 테스트 완료")
