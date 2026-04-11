#!/usr/bin/env python3
"""
Intent Parser Test Script
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.intent import IntentParser, IntentType, Priority, parse_intent

def test_intent_parser():
    print("=== Intent Parser Test ===\n")
    
    parser = IntentParser()
    
    # Test inputs
    test_cases = [
        "Python 코드 작성해줘 - 사용자 인증 함수",
        "이 코드에서 오류를 디버그해줘 - connection failed가 뜨네",
        "이 함수가 어떻게 동작하는지 설명해줄래?",
        "리팩토링해줘 - 중복된 코드가 많아",
        "긴급! 서버가 다운되었어, 지금 바로 고쳐야 해",
        "FastAPI로 REST API를 만들고 싶어, 그리고 데이터베이스는 PostgreSQL을 사용할거야",
        "이 코드를 리뷰해줘 - 개선점이 있을까?",
        "pytest로 테스트 코드 작성해줘",
        "README 문서를 작성하고 싶어",
        "git으로 배포하는 방법을 알려줘"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"{i}. Input: {test_input}")
        intent = parser.parse(test_input)
        
        print(f"   → Type: {intent.intent_type.value}")
        print(f"   → Confidence: {intent.confidence:.2f}")
        print(f"   → Keywords: {intent.keywords[:3]}")
        print(f"   → Goal: {intent.goal}")
        print(f"   → Priority: {intent.priority.name}")
        
        if intent.sub_intents:
            print(f"   → Sub-intents: {len(intent.sub_intents)}")
            for sub in intent.sub_intents:
                print(f"      - {sub.intent_type.value}")
        
        if intent.context.get('detected_languages'):
            print(f"   → Languages: {intent.context['detected_languages']}")
        
        print()
    
    # Statistics
    print("=== Statistics ===")
    stats = parser.get_intent_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_intent_parser()
