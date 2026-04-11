#!/usr/bin/env python3
"""
Log Tool Test Script
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.tools.log_tool import LogTool
from datetime import datetime

def test_log_tool():
    print("=== Log Tool Test ===")
    
    # Create log tool instance
    log_tool = LogTool()
    
    # Test 1: Get tool info
    print("\n1. Tool Info:")
    info = log_tool.get_tool_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Test 2: List log files
    print("\n2. Listing log files:")
    result = log_tool.get_log_files("*")
    log_files = result.get('files', [])
    print(f"  Found {len(log_files)} log files")
    for file in log_files[:3]:  # Show first 3
        print(f"  - {file['name']} ({file['size']} bytes)")
    
    # Test 3: Parse a sample log file
    print("\n3. Parsing sample log file:")
    sample_log = "/home/lks/ai_router/log/source_log/2026-04-11_19-03-00_.log"
    if os.path.exists(sample_log):
        parsed = log_tool.parse_log_file(sample_log, max_lines=20)
        print(f"  Parsed {len(parsed['entries'])} entries")
        print(f"  Time range: {parsed['time_range']}")
        print(f"  Total lines: {parsed['total_lines']}")
    else:
        print(f"  Sample log file not found: {sample_log}")
    
    # Test 4: Pattern matching
    print("\n4. Pattern matching test:")
    test_content = """
2026-04-11 19:00:00 INFO Starting application
2026-04-11 19:00:01 ERROR Failed to connect to database
2026-04-11 19:00:02 WARNING Memory usage high
2026-04-11 19:00:03 INFO User login successful
2026-04-11 19:00:04 ERROR File not found
"""
    lines = test_content.strip().split('\n')
    patterns = ['ERROR', 'WARNING', 'INFO']
    matches = log_tool.match_patterns(lines, patterns)
    print(f"  Found {len(matches)} matches")
    for match in matches[:3]:  # Show first 3
        print(f"  - Line {match['line_number']}: {match['matched_text']}")
    
    # Test 5: Error extraction
    print("\n5. Error extraction test:")
    # Create a log file in valid path for error extraction test
    test_log_path = "/home/lks/ai_router/log/test_sample.log"
    with open(test_log_path, 'w') as f:
        f.write(test_content)
    error_result = log_tool.extract_errors("test_sample.log")
    if 'errors' in error_result:
        errors = error_result['errors']
        print(f"  Found {len(errors)} errors")
        for error in errors[:3]:  # Show first 3
            print(f"  - {error['line_number']}: {error['matched_text']}")
    else:
        print(f"  Error: {error_result.get('error', 'Unknown error')}")
    
    # Test 6: Log summarization
    print("\n6. Log summarization test:")
    summary_result = log_tool.summarize_log("test_sample.log")
    if 'summary' in summary_result:
        summary = summary_result['summary']
        print(f"  Total lines: {summary.get('total_lines', 0)}")
        print(f"  Error count: {summary.get('error_count', 0)}")
        print(f"  Warning count: {summary.get('warning_count', 0)}")
        print(f"  Info count: {summary.get('info_count', 0)}")
    else:
        print(f"  Error: {summary_result.get('error', 'Unknown error')}")
    
    print("\n=== Log Tool Test Complete ===")

if __name__ == "__main__":
    test_log_tool()
