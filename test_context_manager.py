#!/usr/bin/env python3
"""
Context Manager Test Script
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.context import ContextTracker, ConversationTurn, build_context

def test_context_manager():
    print("=== Context Manager Test ===\n")
    
    # Test 1: Session creation
    print("1. Session Creation Test:")
    tracker = ContextTracker(max_history_per_session=10)
    
    # Auto-generated session ID
    session1 = tracker.create_session()
    print(f"   Auto-generated session: {session1}")
    
    # Custom session ID
    session2 = tracker.create_session("my_custom_session_001")
    print(f"   Custom session: {session2}")
    
    # Test 2: Add conversation turns
    print("\n2. Conversation History Test:")
    
    turns_data = [
        {
            'input': 'Python 함수 작성해줘',
            'intent': 'code_generation',
            'policy': 'expand',
            'response': '함수 코드 생성 완료'
        },
        {
            'input': '그리고 테스트 코드도 작성해줘',
            'intent': 'testing',
            'policy': 'balance',
            'response': '테스트 코드 생성 완료'
        },
        {
            'input': '코드 리뷰해줘',
            'intent': 'code_review',
            'policy': 'refine',
            'response': '코드 리뷰 완료'
        }
    ]
    
    for i, turn_data in enumerate(turns_data, 1):
        turn = tracker.add_conversation_turn(
            session_id=session1,
            user_input=turn_data['input'],
            intent_type=turn_data['intent'],
            policy_used=turn_data['policy'],
            response_summary=turn_data['response'],
            context_snapshot={'detected_languages': ['python'], 'has_code_snippet': True}
        )
        print(f"   Turn {i}: {turn.turn_id} - {turn.intent_type} (relevance: {turn.relevance_score:.2f})")
    
    # Test 3: Retrieve history
    print("\n3. Retrieve History Test:")
    history = tracker.get_conversation_history(session1, lookback=2)
    print(f"   Retrieved {len(history)} turns (lookback=2)")
    for turn in history:
        print(f"   - {turn.turn_id}: {turn.user_input[:30]}...")
    
    # Test 4: Relevant context search
    print("\n4. Relevant Context Search Test:")
    relevant = tracker.get_relevant_context(
        session_id=session1,
        current_input='Python 코드를 계속 작성하고 싶어',
        current_intent='code_generation',
        top_k=2
    )
    print(f"   Found {len(relevant)} relevant contexts")
    for turn, score in relevant:
        print(f"   - {turn.turn_id}: relevance={score:.2f}")
    
    # Test 5: Session info
    print("\n5. Session Info Test:")
    info = tracker.get_session_info(session1)
    if info:
        print(f"   Session ID: {info['session_id']}")
        print(f"   Created at: {info['created_at']}")
        print(f"   Turn count: {info['turn_count']}")
        print(f"   Accumulated context: {info['accumulated_context_keys']}")
    
    # Test 6: Persistence
    print("\n6. Session Persistence Test:")
    
    # Save
    saved = tracker.save_session_persistence(session1)
    print(f"   Save session: {'SUCCESS' if saved else 'FAILED'}")
    
    # Create new tracker and load
    tracker2 = ContextTracker(max_history_per_session=10)
    loaded = tracker2.load_session_persistence(session1)
    print(f"   Load session: {'SUCCESS' if loaded else 'FAILED'}")
    
    if loaded:
        loaded_history = tracker2.get_conversation_history(session1)
        print(f"   Loaded {len(loaded_history)} turns from disk")
    
    # Test 7: Cleanup
    print("\n7. Context Cleanup Test:")
    
    # Add old session
    old_session = tracker.create_session("old_session_test")
    tracker.add_conversation_turn(
        session_id=old_session,
        user_input='Old message',
        intent_type='unknown',
        policy_used='balance',
        response_summary='Old response',
        context_snapshot={}
    )
    
    # Manually set old timestamp
    tracker.sessions[old_session].last_active = "2026-04-10T10:00:00"
    tracker.sessions[old_session].conversation_history[0].timestamp = "2026-04-10T10:00:00"
    
    # Cleanup with 1 hour max age
    cleanup_result = tracker.cleanup_context(max_age_hours=1.0)
    print(f"   Cleaned sessions: {cleanup_result['sessions_cleaned']}")
    print(f"   Removed turns: {cleanup_result['turns_removed']}")
    print(f"   Affected sessions: {cleanup_result['sessions_affected']}")
    
    # Test 8: List sessions
    print("\n8. List Sessions Test:")
    sessions = tracker.list_sessions()
    print(f"   Active sessions: {len(sessions)}")
    for sid in sessions:
        print(f"   - {sid}")
    
    print("\n=== Context Manager Test Complete ===")

if __name__ == "__main__":
    test_context_manager()
