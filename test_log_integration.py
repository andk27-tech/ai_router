#!/usr/bin/env python3
"""
Log Integration Test Script
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.tools.log_integration import LogIntegration
from datetime import datetime, timedelta

def test_log_integration():
    print("=== Log Integration Test ===")
    
    # Create log integration instance
    log_int = LogIntegration()
    
    # Test 1: Agent log access
    print("\n1. Agent Log Access Test:")
    result = log_int.get_agent_log_access(
        agent_id="test_agent_001",
        log_types=['system', 'error', 'source']
    )
    if 'accessible_logs' in result:
        print(f"  Accessible logs: {len(result['accessible_logs'])}")
        for log in result['accessible_logs'][:3]:
            print(f"  - {log['type']}: {log['name']}")
    else:
        print(f"  Error: {result.get('error', 'Unknown')}")
    
    # Test 2: Historical analysis - error
    print("\n2. Historical Error Analysis Test:")
    result = log_int.analyze_historical_logs(hours=24, analysis_type='error')
    if 'analysis_type' in result:
        print(f"  Type: {result['analysis_type']}")
        print(f"  Total errors: {result.get('total_errors', 0)}")
        print(f"  Unique errors: {result.get('unique_errors', 0)}")
    else:
        print(f"  Error: {result.get('error', 'Unknown')}")
    
    # Test 3: Historical analysis - patterns
    print("\n3. Pattern Analysis Test:")
    result = log_int.analyze_historical_logs(hours=24, analysis_type='pattern')
    if 'pattern_counts' in result:
        print(f"  Pattern counts: {result['pattern_counts']}")
    else:
        print(f"  Error: {result.get('error', 'Unknown')}")
    
    # Test 4: Debugging support
    print("\n4. Debugging Support Test:")
    result = log_int.provide_debugging_support(
        error_signature="ERROR",
        session_id=None
    )
    if 'error_context' in result:
        print(f"  Found {result['error_context'].get('occurrence_count', 0)} matching errors")
        print(f"  Suggestions: {len(result['suggestions'])}")
        for suggestion in result['suggestions'][:3]:
            print(f"  - {suggestion}")
    else:
        print(f"  Error: {result.get('error', 'Unknown')}")
    
    # Test 5: Recent errors
    print("\n5. Recent Errors Test:")
    errors = log_int.get_recent_errors(limit=5)
    print(f"  Found {len(errors)} recent errors")
    for error in errors[:3]:
        if 'error' in error:
            print(f"  Error reading: {error['error']}")
        else:
            print(f"  - Line {error.get('line_number')}: {error.get('matched_text', '')[:50]}")
    
    # Test 6: Log search
    print("\n6. Log Search Test:")
    result = log_int.search_logs(
        query="test",
        log_types=['source'],
        time_range=None
    )
    if 'results' in result:
        print(f"  Query: {result['query']}")
        print(f"  Total matches: {result['total_matches']}")
    else:
        print(f"  Error: {result.get('error', 'Unknown')}")
    
    print("\n=== Log Integration Test Complete ===")

if __name__ == "__main__":
    test_log_integration()
