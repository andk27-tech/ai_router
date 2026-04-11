#!/usr/bin/env python3
"""
Decision Engine Test Script
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.decision import DecisionEngine, DecisionType, UncertaintyLevel, quick_decision

def test_decision_engine():
    print("=== Decision Engine Test ===\n")
    
    engine = DecisionEngine()
    
    # Test 1: Multi-criteria decision making
    print("1. Multi-Criteria Decision Test:")
    
    options = [
        {
            'name': 'expand_policy',
            'scores': {'performance': 0.9, 'reliability': 0.7, 'cost': 0.6, 'time': 0.8, 'quality': 0.85}
        },
        {
            'name': 'refine_policy',
            'scores': {'performance': 0.7, 'reliability': 0.9, 'cost': 0.8, 'time': 0.6, 'quality': 0.9}
        },
        {
            'name': 'balance_policy',
            'scores': {'performance': 0.8, 'reliability': 0.8, 'cost': 0.9, 'time': 0.9, 'quality': 0.75}
        }
    ]
    
    decision = engine.make_decision(
        options=options,
        decision_type=DecisionType.POLICY_SELECTION
    )
    
    print(f"   Selected: {decision.chosen_option}")
    print(f"   Confidence: {decision.confidence:.2f}")
    print(f"   Uncertainty: {decision.uncertainty_level.name}")
    print(f"   Criteria used: {len(decision.criteria)}")
    
    # Test 2: Uncertainty handling
    print("\n2. Uncertainty Handling Test:")
    
    # Create a low confidence decision
    low_conf_options = [
        {'name': 'option_a', 'scores': {'performance': 0.5, 'reliability': 0.5}},
        {'name': 'option_b', 'scores': {'performance': 0.48, 'reliability': 0.52}}
    ]
    
    uncertain_decision = engine.make_decision(
        options=low_conf_options,
        decision_type=DecisionType.ROUTING
    )
    
    uncertainty_result = engine.handle_uncertainty(
        uncertain_decision,
        fallback_strategy="conservative"
    )
    
    print(f"   Original: {uncertainty_result['original_decision']}")
    print(f"   Uncertainty level: {uncertainty_result['uncertainty_level']}")
    print(f"   Action: {uncertainty_result['action_taken']}")
    print(f"   Recommendations: {uncertainty_result['recommendations']}")
    
    # Test 3: Confidence scoring
    print("\n3. Confidence Scoring Test:")
    
    factors = {
        'historical_success': 0.8,
        'data_quality': 0.9,
        'model_accuracy': 0.75,
        'expert_validation': 0.85
    }
    
    weights = {
        'historical_success': 0.3,
        'data_quality': 0.2,
        'model_accuracy': 0.3,
        'expert_validation': 0.2
    }
    
    confidence = engine.calculate_confidence_score(factors, weights)
    print(f"   Calculated confidence: {confidence:.2f}")
    
    # Test 4: Explanation generation
    print("\n4. Explanation Generation Test:")
    
    for level in ["brief", "standard", "detailed"]:
        explanation = engine.generate_explanation(decision, detail_level=level)
        print(f"\n   {level.upper()}:")
        for line in explanation.split('\n')[:3]:
            print(f"   {line}")
    
    # Test 5: Decision logging
    print("\n5. Decision Logging Test:")
    
    # Create a few more decisions
    for i in range(3):
        engine.make_decision(
            options=[
                {'name': f'option_{i}_a', 'scores': {'x': 0.6, 'y': 0.7}},
                {'name': f'option_{i}_b', 'scores': {'x': 0.8, 'y': 0.5}}
            ],
            decision_type=DecisionType.EXECUTION
        )
    
    stats = engine.get_decision_statistics()
    print(f"   Total decisions: {stats['total_decisions']}")
    print(f"   Average confidence: {stats['average_confidence']:.2f}")
    print(f"   Type distribution: {stats.get('type_distribution', {})}")
    
    # Test 6: Recent decisions
    print("\n6. Recent Decisions Test:")
    recent = engine.get_recent_decisions(3)
    print(f"   Retrieved {len(recent)} recent decisions")
    for d in recent:
        print(f"   - {d.decision_id}: {d.chosen_option} ({d.decision_type.value})")
    
    # Test 7: Quick decision convenience function
    print("\n7. Quick Decision Test:")
    
    result = quick_decision(
        options=['policy_a', 'policy_b', 'policy_c'],
        scores=[
            {'performance': 0.7, 'cost': 0.8},
            {'performance': 0.9, 'cost': 0.6},
            {'performance': 0.8, 'cost': 0.7}
        ],
        decision_type='policy_selection'
    )
    
    print(f"   Chosen: {result['chosen']}")
    print(f"   Confidence: {result['confidence']:.2f}")
    print(f"   Explanation: {result['explanation']}")
    
    print("\n=== Decision Engine Test Complete ===")

if __name__ == "__main__":
    test_decision_engine()
