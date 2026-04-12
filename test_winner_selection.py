#!/usr/bin/env python3
"""
승자 선택 로직 테스트 - 최고 정책 결과 선택 확인
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 테스트 모드 설정
from core.test_policy import set_test_mode, TestMode
set_test_mode(TestMode.DUMMY_1)

from core.agents import run_agents
from core.ai import ai_call

def test_winner_selection():
    """승자 선택 로직 테스트"""
    print("=" * 60)
    print("🧪 승자 선택 로직 테스트 시작")
    print("=" * 60)
    
    # 테스트 입력
    test_input = "AI 라우터 프로젝트의 핵심 기능을 설명해줘"
    
    print(f"📥 입력: {test_input}")
    print("\n🔄 에이전트 실행 및 승자 선택 테스트...")
    
    try:
        # 에이전트 실행
        winner, all_results = run_agents(ai_call, test_input)
        
        print(f"\n✅ 에이전트 실행 완료")
        print(f"📊 총 {len(all_results)}개 에이전트 결과")
        
        # 모든 결과 상세 분석
        print("\n📋 모든 에이전트 결과:")
        results_with_scores = []
        
        for i, result in enumerate(all_results, 1):
            policy = result['policy']
            score = result['score']
            output = result['output']
            output_length = len(output)
            output_preview = output[:30] + "..." if len(output) > 30 else output
            
            result_dict = {
                'index': i,
                'policy': policy,
                'score': score,
                'output_length': output_length,
                'output_preview': output_preview
            }
            
            results_with_scores.append(result_dict)
            
            print(f"   {i}. {policy}")
            print(f"      점수: {score:.1f}")
            print(f"      길이: {output_length} 글자")
            print(f"      미리보기: {output_preview}")
        
        # 점수 순으로 정렬
        results_with_scores.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"\n🏆 점수 순위:")
        for i, result in enumerate(results_with_scores, 1):
            print(f"   {i}. {result['policy']}: {result['score']:.1f}점")
        
        # 승자 확인
        print(f"\n🎯 선택된 승자:")
        print(f"   정책: {winner['policy']}")
        print(f"   점수: {winner['score']:.1f}")
        print(f"   실제 최고 점수: {results_with_scores[0]['score']:.1f}")
        
        # 승자 선택이 올바른지 확인
        expected_winner = results_with_scores[0]
        if winner['policy'] == expected_winner['policy'] and winner['score'] == expected_winner['score']:
            print(f"   ✅ 승자 선택 올바름!")
        else:
            print(f"   ❌ 승자 선택 오류!")
            print(f"   기대: {expected_winner['policy']} ({expected_winner['score']:.1f}점)")
            print(f"   실제: {winner['policy']} ({winner['score']:.1f}점)")
        
        # 동점자 처리 확인
        top_score = results_with_scores[0]['score']
        tie_candidates = [r for r in results_with_scores if r['score'] == top_score]
        
        if len(tie_candidates) > 1:
            print(f"\n⚠️ 동점자 발견 ({len(tie_candidates)}개):")
            for candidate in tie_candidates:
                print(f"   - {candidate['policy']}: {candidate['score']:.1f}점")
            print(f"   선택된: {winner['policy']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 승자 선택 테스트 오류: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_winner_selection()
    print(f"\n🎯 승자 선택 테스트 결과: {'성공' if success else '실패'}")
