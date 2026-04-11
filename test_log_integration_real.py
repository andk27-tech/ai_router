#!/usr/bin/env python3
"""
Log Integration Real Data Test
실제 시스템 로그 및 프로세스 로그 접근 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.tools.log_integration_extended import SystemLogIntegration, quick_system_log_check

def test_real_log_access():
    print("=== Real System Log Access Test ===\n")
    
    integration = SystemLogIntegration(allow_system_logs=True)
    
    # Test 1: Grant permissions to agent
    print("1. Grant Permissions Test:")
    result = integration.grant_permissions(
        agent_id='test_agent_001',
        log_types=['syslog', 'daemon', 'kern', 'boot'],
        read_only=True,
        max_lines=500
    )
    print(f"   Agent: {result['agent_id']}")
    print(f"   Granted logs: {result['granted_permissions']['log_types']}")
    print(f"   Read only: {result['granted_permissions']['read_only']}")
    
    # Test 2: Access system logs with permission
    print("\n2. System Log Access Test:")
    result = integration.get_system_log_access(
        agent_id='test_agent_001',
        log_types=['syslog', 'daemon', 'boot'],
        lines=30
    )
    
    if result.get('success'):
        print(f"   ✓ Successfully accessed {result['total_logs']} log types")
        for log_type, info in result['logs_accessed'].items():
            if 'error' not in info:
                print(f"   - {log_type}: {info.get('lines_read', 0)} lines from {info.get('path', 'N/A')}")
                print(f"     Size: {info.get('size_bytes', 0):,} bytes, Modified: {info.get('modified', 'N/A')}")
            else:
                print(f"   - {log_type}: Error - {info['error']}")
    else:
        print(f"   ✗ Failed: {result.get('error', 'Unknown error')}")
    
    # Test 3: Try accessing without permission
    print("\n3. Permission Denial Test:")
    result = integration.get_system_log_access(
        agent_id='unauthorized_agent',
        log_types=['auth', 'secure'],
        lines=50
    )
    print(f"   Access allowed: {result.get('success', False)}")
    if not result.get('success'):
        print(f"   Reason: {result.get('error', 'Permission denied')}")
    
    # Test 4: Process log access
    print("\n4. Process Log Access Test:")
    result = integration.get_process_log(
        agent_id='test_agent_001',
        process_name='python',
        lines=10
    )
    
    if result.get('success'):
        proc_logs = result.get('process_logs', {})
        if proc_logs.get('summary'):
            print(f"   System processes summary:")
            print(f"   - Top CPU: {proc_logs['top_cpu'][:3]}")
            print(f"   - Top Memory: {proc_logs['top_memory'][:3]}")
            print(f"   - Total processes: {proc_logs['total_processes']}")
        else:
            for pid, info in list(proc_logs.items())[:3]:
                if 'error' not in info:
                    print(f"   - PID {pid}: {info.get('name', 'N/A')}")
                    print(f"     CPU: {info.get('cpu_percent', 0)}%, Memory: {info.get('memory_mb', 0)} MB")
                    if info.get('inferred_logs'):
                        print(f"     Log paths: {info['inferred_logs'][:2]}")
    
    # Test 5: System error analysis
    print("\n5. System Error Analysis Test:")
    result = integration.analyze_system_errors(
        agent_id='test_agent_001',
        hours=1,
        severity='error'
    )
    
    if result.get('success'):
        print(f"   Analysis period: {result['analysis_period_hours']} hours")
        print(f"   Total errors found: {result['total_errors']}")
        print(f"   Error types: {result['error_types']}")
        if result['recent_errors']:
            print(f"   Recent error samples:")
            for err in result['recent_errors'][:3]:
                print(f"   - [{err.get('timestamp', 'N/A')}] {err.get('message', 'N/A')[:60]}...")
    else:
        print(f"   Analysis failed: {result.get('error', 'Unknown error')}")
    
    # Test 6: Quick system check
    print("\n6. Quick System Log Check Test:")
    result = quick_system_log_check(agent_id='debugger')
    print(f"   Log accessible: {result['log_accessible']}")
    print(f"   Recent errors: {result['recent_errors']}")
    print(f"   Error types: {result['error_types']}")
    print(f"   Status: {result['status']}")
    
    # Test 7: Access statistics
    print("\n7. Access Statistics Test:")
    stats = integration.get_access_statistics()
    if 'message' in stats:
        print(f"   {stats['message']}")
    else:
        print(f"   Total accesses: {stats['total_accesses']}")
        print(f"   Access types: {stats['access_types']}")
        print(f"   Recent accesses: {len(stats['recent_accesses'])}")
    
    # Test 8: Different permission levels
    print("\n8. Different Permission Levels Test:")
    
    # Admin permission
    admin_result = integration.get_system_log_access(
        agent_id='admin',
        log_types=['syslog', 'auth', 'kern', 'daemon'],
        lines=10
    )
    print(f"   Admin access: {'✓' if admin_result.get('success') else '✗'} (all logs)")
    
    # Monitor permission (limited)
    monitor_result = integration.get_system_log_access(
        agent_id='monitor',
        log_types=['syslog', 'auth'],  # auth not allowed for monitor
        lines=10
    )
    print(f"   Monitor access: {'✓' if monitor_result.get('success') else '✗'} (syslog, daemon, cron only)")
    if not monitor_result.get('success'):
        print(f"     Allowed types: {monitor_result.get('allowed_types', [])}")
    
    print("\n=== Real System Log Access Test Complete ===")

if __name__ == "__main__":
    test_real_log_access()
