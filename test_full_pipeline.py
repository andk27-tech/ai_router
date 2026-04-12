#!/usr/bin/env python3
"""
전체 파이프라인 통합 테스트 - 완전한 라우터 시스템 확인
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 테스트 모드 설정
from core.test_policy import set_test_mode, TestMode
set_test_mode(TestMode.DUMMY_1)

from core.runner import run_node
from core.ai import ai_call

def test_full_pipeline():
    """전체 파이프라인 테스트"""
    print("=" * 60)
    print("🧪 전체 파이프라인 통합 테스트 시작")
    print("=" * 60)
    
    # 다양한 테스트 케이스
    test_cases = [
        {
            "name": "기능 설명 요청",
            "input": "AI 라우터 프로젝트의 핵심 기능을 설명해줘",
            "expected_policy": "expand",
            "min_score": 7.0
        },
        {
            "name": "상태 확인 요청", 
            "input": "시스템 상태가 어떤지 알려줘",
            "expected_policy": "balance",
            "min_score": 6.0
        },
        {
            "name": "정리 요청",
            "input": "코드를 정리하고 구조화해줘",
            "expected_policy": "refine", 
            "min_score": 6.0
        },
        {
            "name": "복잡한 분석 요청",
            "input": "프로젝트의 확장성과 성능을 깊이 있게 분석해줘",
            "expected_policy": "expand_deep",
            "min_score": 8.0
        }
    ]
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*40}")
        print(f"🧪 테스트 케이스 {i}: {test_case['name']}")
        print(f"{'='*40}")
        
        input_text = test_case['input']
        expected_policy = test_case['expected_policy']
        min_score = test_case['min_score']
        
        print(f"📥 입력: {input_text}")
        print(f"🎯 기대 정책: {expected_policy} (최소 {min_score}점)")
        
        try:
            # 전체 파이프라인 실행
            print("\n🔄 run_node() 실행 중...")
            result = run_node(ai_call, input_text, threshold=6, max_retry=2)
            
            print(f"\n✅ 파이프라인 실행 완료")
            print(f"📤 결과 길이: {len(result)} 글자")
            print(f"📤 결과 미리보기: {result[:100]}...")
            
            # 결과 분석
            print(f"\n📊 결과 분석:")
            
            # 키워드 기반 정책 추론
            result_lower = result.lower()
            if '확장' in result_lower or '모듈' in result_lower:
                detected_policy = "expand"
            elif '균형' in result_lower or '다양' in result_lower:
                detected_policy = "balance"
            elif '정리' in result_lower or '체계' in result_lower:
                detected_policy = "refine"
            elif '상세' in result_lower or '분석' in result_lower:
                detected_policy = "expand_deep"
            else:
                detected_policy = "unknown"
            
            print(f"   감지된 정책: {detected_policy}")
            
            # 정책 일치 확인
            if detected_policy == expected_policy:
                print(f"   ✅ 정책 일치!")
                success_count += 1
            else:
                print(f"   ⚠️ 정책 불일치 (기대: {expected_policy}, 실제: {detected_policy})")
            
            # 품질 평가
            if len(result) >= 50:
                print(f"   ✅ 충분한 내용 길이")
            else:
                print(f"   ⚠️ 내용이 너무 짧음")
            
            # 응답 품질 점수 (간단한 휴리스틱)
            quality_score = 0
            if len(result) > 100:
                quality_score += 2
            if '1.' in result or '•' in result or '|' in result:
                quality_score += 2
            if any(keyword in result_lower for keyword in ['기능', '시스템', '프로젝트', '구조']):
                quality_score += 1
            
            print(f"   품질 점수: {quality_score}/5")
            
        except Exception as e:
            print(f"❌ 파이프라인 실행 오류: {e}")
            import traceback
            traceback.print_exc()
    
    # 최종 결과 요약
    print(f"\n{'='*60}")
    print("📊 전체 파이프라인 테스트 결과 요약")
    print(f"{'='*60}")
    print(f"성공한 테스트: {success_count}/{total_count}")
    print(f"성공률: {success_count/total_count*100:.1f}%")
    
    if success_count == total_count:
        print("🎉 모든 테스트 통과! 라우터가 정상 작동합니다.")
        return True
    elif success_count >= total_count * 0.7:
        print("✅ 대부분 테스트 통과! 라우터가 양호하게 작동합니다.")
        return True
    else:
        print("⚠️ 일부 테스트 실패! 라우터 개선이 필요합니다.")
        return False

if __name__ == "__main__":
    success = test_full_pipeline()
    print(f"\n🎯 최종 테스트 결과: {'성공' if success else '실패'}")
