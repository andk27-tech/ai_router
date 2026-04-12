#!/usr/bin/env python3
"""
개선된 시스템 재테스트 - 정책 다양성, 동점자 처리, 더미 응답 개선 검증
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 테스트 모드 설정
from core.test_policy import set_test_mode, TestMode
set_test_mode(TestMode.DUMMY_1)

from core.runner import run_node
from core.agents import run_agents
from core.ai import ai_call

def test_improved_system():
    """개선된 시스템 재테스트"""
    print("=" * 60)
    print("🧪 개선된 시스템 재테스트 시작")
    print("=" * 60)
    
    # 다양한 테스트 케이스
    test_cases = [
        {
            "name": "기능 설명 요청 (expand 기대)",
            "input": "AI 라우터 프로젝트의 핵심 기능을 설명해줘",
            "expected_policies": ["expand", "expand_deep", "expand_wide"]
        },
        {
            "name": "상태 확인 요청 (balance 기대)",
            "input": "시스템 상태가 어떤지 알려줘",
            "expected_policies": ["balance", "balance_stable", "balance_harmony"]
        },
        {
            "name": "정리 요청 (refine 기대)",
            "input": "코드를 정리하고 구조화해줘",
            "expected_policies": ["refine", "refine_clean", "refine_structured"]
        },
        {
            "name": "복잡한 분석 요청 (expand_deep 기대)",
            "input": "프로젝트의 확장성과 성능을 깊이 있게 분석해줘",
            "expected_policies": ["expand_deep", "expand_thorough", "expand_intensive"]
        }
    ]
    
    success_count = 0
    total_count = len(test_cases)
    policy_diversity_score = 0
    tie_breaking_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*50}")
        print(f"🧪 테스트 케이스 {i}: {test_case['name']}")
        print(f"{'='*50}")
        
        input_text = test_case['input']
        expected_policies = test_case['expected_policies']
        
        print(f"📥 입력: {input_text}")
        print(f"🎯 기대 정책 타입: {expected_policies}")
        
        try:
            # 1. 에이전트 실행 테스트
            print("\n🔄 에이전트 실행 테스트...")
            winner, all_results = run_agents(ai_call, input_text)
            
            print(f"✅ 에이전트 실행 완료")
            print(f"📊 총 {len(all_results)}개 에이전트 결과")
            
            # 실행된 정책 확인
            executed_policies = [r['policy'] for r in all_results]
            print(f"📋 실행된 정책: {executed_policies}")
            
            # 정책 다양성 평가
            policy_types = set()
            for policy in executed_policies:
                base_policy = policy.split("_")[0] if "_" in policy else policy
                policy_types.add(base_policy)
            
            diversity_score = len(policy_types) / 4 * 100  # 4개 기본 정책 기준
            policy_diversity_score += diversity_score
            
            print(f"🎭 정책 다양성: {len(policy_types)}/4 유형 ({diversity_score:.0f}%)")
            
            # 승자 정보
            winner_policy = winner['policy']
            winner_score = winner['score']
            winner_base = winner_policy.split("_")[0] if "_" in winner_policy else winner_policy
            
            print(f"\n🏆 승자 정보:")
            print(f"   정책: {winner_policy}")
            print(f"   기본 타입: {winner_base}")
            print(f"   점수: {winner_score:.1f}")
            
            # 기대 정책과 일치 여부
            expected_base = expected_policies[0].split("_")[0]
            if winner_base == expected_base:
                print(f"   ✅ 기대 정책과 일치!")
                success_count += 1
            else:
                print(f"   ⚠️ 기대: {expected_base}, 실제: {winner_base}")
            
            # 동점자 처리 확인
            top_score = max(r['score'] for r in all_results)
            top_candidates = [r for r in all_results if r['score'] == top_score]
            
            if len(top_candidates) > 1:
                tie_breaking_count += 1
                print(f"   🔀 동점자 처리: {len(top_candidates)}개 동점자")
                print(f"   최종 선택: {winner_policy}")
            
            # 모든 결과 상세 보기
            print(f"\n📋 모든 에이전트 결과:")
            for j, result in enumerate(all_results, 1):
                policy = result['policy']
                score = result['score']
                output_length = len(result['output'])
                output_preview = result['output'][:50] + "..." if len(result['output']) > 50 else result['output']
                
                status = "🏆" if result == winner else "  "
                print(f"   {status} {j}. {policy}")
                print(f"      점수: {score:.1f}, 길이: {output_length}")
                print(f"      미리보기: {output_preview}")
            
            # 2. 전체 파이프라인 테스트
            print(f"\n🔄 전체 파이프라인 테스트...")
            pipeline_result = run_node(ai_call, input_text, threshold=6, max_retry=2)
            
            print(f"✅ 파이프라인 실행 완료")
            print(f"📤 결과 길이: {len(pipeline_result)} 글자")
            print(f"📤 결과 미리보기: {pipeline_result[:100]}...")
            
        except Exception as e:
            print(f"❌ 테스트 오류: {e}")
            import traceback
            traceback.print_exc()
    
    # 최종 결과 요약
    print(f"\n{'='*60}")
    print("📊 개선된 시스템 테스트 결과 요약")
    print(f"{'='*60}")
    
    success_rate = success_count / total_count * 100
    avg_diversity = policy_diversity_score / total_count
    
    print(f"✅ 정책 일치율: {success_count}/{total_count} ({success_rate:.0f}%)")
    print(f"🎭 평균 정책 다양성: {avg_diversity:.0f}%")
    print(f"🔀 동점자 처리 발생: {tie_breaking_count}회")
    
    # 개선 전후 비교
    print(f"\n📈 개선 효과:")
    print(f"   이전 성공률: 25% → 현재: {success_rate:.0f}%")
    print(f"   정책 다양성: 이전 25% → 현재: {avg_diversity:.0f}%")
    print(f"   동점자 처리: 이전 없음 → 현재 {tie_breaking_count}회 처리")
    
    # 최종 평가
    if success_rate >= 75 and avg_diversity >= 50:
        print(f"\n🎉 훌륭! 시스템 개선 성공!")
        return True
    elif success_rate >= 50 and avg_diversity >= 35:
        print(f"\n✅ 좋음! 상당한 개선 achieved!")
        return True
    else:
        print(f"\n⚠️ 개선 필요: 일부 성공 but 추가 개선 required")
        return False

if __name__ == "__main__":
    success = test_improved_system()
    print(f"\n🎯 최종 테스트 결과: {'성공' if success else '개선 필요'}")
