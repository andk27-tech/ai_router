#!/usr/bin/env python3
"""
Intent Integration Test Script
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.intent_integration import IntentBasedRouter, IntentContextManager, route_by_intent

def test_intent_integration():
    print("=== Intent Integration Test ===\n")
    
    # Test 1: Router intent recognition
    print("1. Router Intent Recognition Test:")
    router = IntentBasedRouter()
    
    test_cases = [
        "Python 함수 작성해줘",
        "이 코드에서 오류 디버그해줘",
        "코드 리뷰해줘",
        "FastAPI API 설명해줘"
    ]
    
    for test_input in test_cases:
        result = router.recognize_intent_and_route(test_input)
        print(f"\n   Input: {test_input}")
        print(f"   → Intent: {result['intent']['intent_type']}")
        print(f"   → Policy: {result['routing']['selected_policy']}")
        print(f"   → Confidence: {result['routing']['confidence']:.2f}")
        print(f"   → Reason: {result['routing']['reasoning']}")
    
    # Test 2: Intent-based policy selection
    print("\n2. Intent-Based Policy Selection Test:")
    policy_test_cases = [
        ("긴급! 서버가 다운되었어", "CRITICAL priority → should select refine"),
        ("새로운 기능 구현해줘", "code_generation → should select expand"),
        ("코드 리뷰해줘", "code_review → should select refine"),
        ("데이터 분석해줘", "analysis → should select expand_deep")
    ]
    
    for test_input, expected in policy_test_cases:
        result = router.recognize_intent_and_route(test_input)
        print(f"\n   Input: {test_input}")
        print(f"   → Selected: {result['routing']['selected_policy']}")
        print(f"   → Expected: {expected}")
    
    # Test 3: Context preservation
    print("\n3. Context Preservation Test:")
    context_manager = IntentContextManager()
    session_id = "test_session_001"
    
    # First interaction
    result1 = router.recognize_intent_and_route("Python 코드 작성해줘")
    context_manager.save_context(session_id, result1['context'])
    print(f"   Saved context 1: {result1['context']['intent_type']}")
    
    # Second interaction
    result2 = router.recognize_intent_and_route("그리고 테스트 코드도 작성해줘")
    context_manager.save_context(session_id, result2['context'])
    print(f"   Saved context 2: {result2['context']['intent_type']}")
    
    # Retrieve context
    chain = context_manager.get_context_chain(session_id)
    print(f"   Context chain length: {len(chain)}")
    
    # Test context enrichment
    enriched = context_manager.enrich_with_context("계속해서", session_id)
    print(f"   Enriched input has previous context: {enriched['has_previous_context']}")
    print(f"   Previous intent: {enriched['previous_intent']}")
    print(f"   Continuity score: {enriched['continuity_score']:.2f}")
    
    # Test 4: Routing statistics
    print("\n4. Routing Statistics Test:")
    stats = router.get_routing_statistics()
    print(f"   Total routings: {stats.get('total_routings', 0)}")
    print(f"   Policy distribution: {stats.get('policy_distribution', {})}")
    print(f"   Intent distribution: {stats.get('intent_distribution', {})}")
    
    # Test 5: Route by intent convenience function
    print("\n5. Route by Intent (with session) Test:")
    result = route_by_intent("Flask 앱 만들어줘", session_id="session_002")
    print(f"   Input: Flask 앱 만들어줘")
    print(f"   → Intent: {result['intent']['intent_type']}")
    print(f"   → Policy: {result['routing']['selected_policy']}")
    print(f"   → Session preserved: {result['context'].get('detected_frameworks', [])}")
    
    print("\n=== Intent Integration Test Complete ===")

if __name__ == "__main__":
    test_intent_integration()
