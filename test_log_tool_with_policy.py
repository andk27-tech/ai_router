#!/usr/bin/env python3
"""
Log Tool Test with Policy Integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.tools.log_tool import LogTool
from core.test_policy import TestPolicy, TestMode
from datetime import datetime

def test_log_tool_with_policy():
    print("=== Log Tool Test with Policy ===")
    
    # Create log tool and test policy instances
    log_tool = LogTool()
    test_policy = TestPolicy()
    
    # Test with dummy policy
    print("\n1. Testing with Dummy Policy:")
    test_policy.set_test_mode(TestMode.DUMMY_1)
    print(f"  Current mode: {test_policy.get_test_mode()}")
    
    # Simulate AI call for log analysis
    from core.ai import ai_call
    dummy_prompt = "Analyze this log: ERROR: Database connection failed"
    response = ai_call(dummy_prompt)
    print(f"  Dummy response: {response}")
    
    # Test with local AI policy
    print("\n2. Testing with Local AI Policy:")
    test_policy.set_test_mode(TestMode.LOCAL_AI)
    print(f"  Current mode: {test_policy.get_test_mode()}")
    
    # Note: This would require actual Ollama to be running
    # For now, we'll just show the mode change
    print("  Local AI mode set (requires Ollama to be running)")
    
    # Test log tool functionality in different modes
    print("\n3. Log Tool Functionality Test:")
    
    # Create test log
    test_log_path = "/home/lks/ai_router/log/policy_test.log"
    test_content = """
2026-04-11 20:00:00 INFO Application starting
2026-04-11 20:00:01 ERROR Database connection failed
2026-04-11 20:00:02 WARNING Retrying connection
2026-04-11 20:00:03 INFO Connection established
2026-04-11 20:00:04 ERROR Query execution failed
"""
    
    with open(test_log_path, 'w') as f:
        f.write(test_content)
    
    # Test log parsing
    result = log_tool.parse_log_file("policy_test.log", max_lines=10)
    if 'error' not in result:
        print(f"  Parsed {len(result['lines'])} lines")
    
    # Test error extraction
    errors = log_tool.extract_errors("policy_test.log")
    if 'errors' in errors:
        print(f"  Found {len(errors['errors'])} errors")
    
    # Test log summarization
    summary = log_tool.summarize_log("policy_test.log")
    if 'summary' in summary:
        s = summary['summary']
        print(f"  Summary: {s.get('total_lines')} lines, {s.get('error_count')} errors")
    
    print("\n=== Log Tool Policy Test Complete ===")

if __name__ == "__main__":
    test_log_tool_with_policy()
