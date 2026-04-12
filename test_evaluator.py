#!/usr/bin/env python3
"""
평가자 테스트 - 점수 평가 로직 확인
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.evaluator import evaluate

def test_evaluator():
    """평가자 테스트"""
    print("=" * 60)
    print("🧪 평가자(evaluator) 테스트 시작")
    print("=" * 60)
    
    # 테스트용 응답들
    test_cases = [
        {
            "policy": "expand",
            "output": """AI 라우터 프로젝트의 확장성 기능은 다음과 같습니다:
1. 모듈형 아키텍처 | 각 구성요소가 독립적으로 확장 가능
2. 플러그인 시스템 | 새로운 기능을 쉽게 추가할 수 있는 구조
3. 수평적 확장 | 다중 서버 환경에서의 분산 처리
4. API 확장 | 외부 시스템과의 연동 용이성""",
            "expected": "높은 점수 (8-10점)"
        },
        {
            "policy": "balance", 
            "output": """AI 라우터 프로젝트는 다양한 측면의 균형을 고려합니다:
1. 성능과 안정성의 균형
2. 확장성과 단순성의 조화  
3. 자동화와 제어의 균형
4. 모든 구성 요소의 균형 있는 발전""",
            "expected": "중간 점수 (6-8점)"
        },
        {
            "policy": "refine",
            "output": """AI 라우터 프로젝트의 핵심 기능을 정리하면 다음과 같습니다:
1. 체계적인 에이전트 관리
2. 정제된 평가 시스템
3. 구조화된 학습 메커니즘
4. 명확한 정책 진화 과정""",
            "expected": "중간 점수 (6-8점)"
        },
        {
            "policy": "expand_deep",
            "output": """AI 라우터 프로젝트의 확장성을 상세하게 분석하면 다음과 같습니다:

1. **모듈형 아키텍처 설계**: 
   - 각 구성요소(에이전트, 평가자, 러너)가 독립적으로 동작
   - 인터페이스 기반 설계로 새로운 모듈 추가 용이
   - 의존성 최소화로 유지보수성 향상

2. **플러그인 시스템 구현**:
   - 동적 플러그인 로딩 지원
   - 핫 스왑 기능으로 런타임 중 확장 가능
   - 표준화된 플러그인 API 제공""",
            "expected": "높은 점수 (9-10점)"
        },
        {
            "policy": "expand",
            "output": "간단한 응답",
            "expected": "낮은 점수 (1-5점)"
        }
    ]
    
    print("📊 테스트 케이스 평가:")
    
    total_score = 0
    for i, case in enumerate(test_cases, 1):
        policy = case["policy"]
        output = case["output"]
        expected = case["expected"]
        
        score, reason = evaluate(output, policy)
        total_score += score
        
        print(f"\n{i}. 정책: {policy}")
        print(f"   출력: {output[:50]}...")
        print(f"   예상: {expected}")
        print(f"   실제 점수: {score}/10")
        print(f"   이유: {reason}")
        
        # 점수 분석
        if score >= 8:
            analysis = "✅ 높은 점수"
        elif score >= 6:
            analysis = "⚠️ 중간 점수"
        else:
            analysis = "❌ 낮은 점수"
        print(f"   분석: {analysis}")
    
    print(f"\n📈 평균 점수: {total_score/len(test_cases):.1f}/10")
    
    return True

if __name__ == "__main__":
    test_evaluator()
    print(f"\n🎯 평가자 테스트 완료")
