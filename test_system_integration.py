#!/usr/bin/env python3
"""
System Integration Test Script
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.tools.system_integration import SystemIntegration, PermissionLevel, check_system_safety

def test_system_integration():
    print("=== System Integration Test ===\n")
    
    integration = SystemIntegration()
    
    # Test 1: Safe execution environment - command validation
    print("1. Command Safety Validation Test:")
    
    test_commands = [
        ("ls -la /home/lks/ai_router", True),
        ("python3 test.py", True),
        ("rm -rf /", False),  # Dangerous
        ("cat /etc/passwd", False),  # Forbidden path
        ("echo hello", True),
        ("`rm -rf /`", False),  # Shell injection
    ]
    
    for cmd, expected_safe in test_commands:
        result = integration.validate_command_safety(cmd)
        status = "✓" if result['safe'] == expected_safe else "✗"
        print(f"   {status} '{cmd[:40]}...' -> {result['risk_level']}")
    
    # Test 2: Path access validation
    print("\n2. Path Access Validation Test:")
    
    test_paths = [
        "/home/lks/ai_router/test.py",
        "/tmp/test.txt",
        "/etc/passwd",  # Forbidden
        "/root/secret",  # Forbidden
    ]
    
    for path in test_paths:
        result = integration.validate_path_access(path, 'read')
        status = "✓" if result['allowed'] else "✗"
        print(f"   {status} '{path}' -> {result['reason']}")
    
    # Test 3: Resource monitoring
    print("\n3. Resource Monitoring Test:")
    result = integration.monitor_resources()
    print(f"   Overall status: {result['overall_status']}")
    print(f"   Alert count: {result['alert_count']}")
    if result['alerts']:
        for alert in result['alerts'][:3]:
            print(f"   - {alert['resource_type']}: {alert['level']} - {alert['message']}")
    
    # Test 4: Permission check
    print("\n4. Permission Check Test:")
    
    test_actions = [
        'read_file',
        'write_file',
        'execute_command',
        'system_modify',
    ]
    
    for action in test_actions:
        check = integration.check_permission(action)
        print(f"   {action}: {check.allowed} (need: {check.required_permission}, have: {check.current_permission})")
    
    # Test 5: Permission elevation request
    print("\n5. Permission Elevation Test:")
    result = integration.request_elevation(
        action='system_modify',
        reason='Update system configuration',
        requester='ai_agent'
    )
    print(f"   Granted: {result.get('granted', False)}")
    print(f"   Reason: {result.get('reason', 'N/A')}")
    if result.get('pending_approval'):
        print(f"   Pending admin approval")
    
    # Test 6: System health for agents
    print("\n6. System Health for Agents Test:")
    health = integration.get_system_health_for_agents()
    print(f"   Safe to execute: {health.get('safe_to_execute', False)}")
    print(f"   Overall status: {health.get('overall_status', 'unknown')}")
    print(f"   Resource pressure: {health.get('resource_pressure', False)}")
    print(f"   Recommendation: {health.get('recommendation', 'N/A')}")
    
    # Test 7: Quick safety check
    print("\n7. Quick Safety Check Test:")
    safety = check_system_safety()
    print(f"   Safe to proceed: {safety.get('safe_to_proceed', False)}")
    print(f"   Resource status: {safety.get('resource_status', 'unknown')}")
    print(f"   Alerts: {safety.get('alerts', 0)}")
    print(f"   Recommendation: {safety.get('recommendation', 'N/A')}")
    
    # Test 8: Resource usage trend
    print("\n8. Resource Usage Trend Test:")
    trend = integration.get_resource_usage_trend(hours=1)
    print(f"   Current status: {trend.get('current_status', 'unknown')}")
    print(f"   Recent alerts: {trend.get('recent_alerts', 0)}")
    
    # Test 9: Execution statistics
    print("\n9. Execution Statistics Test:")
    stats = integration.get_execution_statistics()
    if 'message' in stats:
        print(f"   {stats['message']}")
    else:
        print(f"   Total executions: {stats.get('total_executions', 0)}")
        print(f"   Success rate: {stats.get('success_rate', 0):.1%}")
    
    print("\n=== System Integration Test Complete ===")

if __name__ == "__main__":
    test_system_integration()
