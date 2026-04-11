#!/usr/bin/env python3
"""
System Tool Test Script
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.tools.system_tool import SystemTool, get_system_health

def test_system_tool():
    print("=== System Tool Test ===\n")
    
    tool = SystemTool()
    
    # Test 1: Process management - list processes
    print("1. Process List Test:")
    result = tool.list_processes(limit=5, order_by='cpu')
    if result.get('success'):
        print(f"   Total processes: {result['total_processes']}")
        print(f"   Showing top {len(result['processes'])} by CPU:")
        for proc in result['processes'][:3]:
            print(f"   - PID {proc['pid']}: {proc['name']} (CPU: {proc['cpu_percent']}%)")
    else:
        print(f"   Error: {result.get('error')}")
    
    # Test 2: Memory monitoring
    print("\n2. Memory Info Test:")
    result = tool.get_memory_info()
    if result.get('success'):
        mem = result['memory']
        print(f"   Total: {mem['total_gb']} GB")
        print(f"   Used: {mem['used_gb']} GB ({mem['percent_used']}%)")
        print(f"   Status: {mem['status']}")
    else:
        print(f"   Error: {result.get('error')}")
    
    # Test 3: Network status
    print("\n3. Network Info Test:")
    result = tool.get_network_info()
    if result.get('success'):
        print(f"   Interfaces: {len(result['interfaces'])}")
        print(f"   Active connections: {result['active_connections']}")
        print(f"   Bytes sent: {result['io_counters']['bytes_sent']:,}")
        print(f"   Bytes recv: {result['io_counters']['bytes_recv']:,}")
    else:
        print(f"   Error: {result.get('error')}")
    
    # Test 4: System information
    print("\n4. System Info Test:")
    result = tool.get_system_info()
    if result.get('success'):
        sys = result['system']
        print(f"   Platform: {sys['platform']}")
        print(f"   CPU count: {sys['cpu_count']}")
        print(f"   Hostname: {sys['hostname']}")
        print(f"   Python: {sys['python_version']}")
    else:
        print(f"   Error: {result.get('error')}")
    
    # Test 5: CPU info
    print("\n5. CPU Info Test:")
    result = tool.get_cpu_info()
    if result.get('success'):
        cpu = result['cpu']
        print(f"   Usage: {cpu['percent']}%")
        print(f"   Logical cores: {cpu['count_logical']}")
        print(f"   Status: {cpu['status']}")
    else:
        print(f"   Error: {result.get('error')}")
    
    # Test 6: Disk info
    print("\n6. Disk Info Test:")
    result = tool.get_disk_info()
    if result.get('success'):
        disk = result['root_partition']
        print(f"   Total: {disk['total_gb']} GB")
        print(f"   Used: {disk['used_gb']} GB ({disk['percent']}%)")
        print(f"   Status: {disk['status']}")
        print(f"   Partitions: {len(result['partitions'])}")
    else:
        print(f"   Error: {result.get('error')}")
    
    # Test 7: Resource limits
    print("\n7. Resource Limits Test:")
    result = tool.check_resource_limits()
    if result.get('success'):
        print(f"   CPU: {result['current']['cpu_percent']}% / {result['limits']['max_cpu_percent']}%")
        print(f"   Memory: {result['current']['memory_percent']}% / 80%")
        print(f"   Disk: {result['current']['disk_percent']}% / {result['limits']['max_disk_usage_percent']}%")
        print(f"   Within limits: {result['within_limits']}")
    else:
        print(f"   Error: {result.get('error')}")
    
    # Test 8: System summary
    print("\n8. System Summary Test:")
    result = tool.get_system_summary()
    if result.get('success'):
        print(f"   Overall status: {result['overall_status']}")
        print(f"   Top CPU process: {result['top_cpu_processes'][0]['name'] if result['top_cpu_processes'] else 'N/A'}")
        print(f"   Top Memory process: {result['top_memory_processes'][0]['name'] if result['top_memory_processes'] else 'N/A'}")
    else:
        print(f"   Error: {result.get('error')}")
    
    # Test 9: Convenience function
    print("\n9. System Health Test:")
    health = get_system_health()
    print(f"   Status: {health.get('status', 'unknown')}")
    print(f"   CPU: {health.get('cpu_percent', 0)}%")
    print(f"   Memory: {health.get('memory_percent', 0)}%")
    print(f"   Within limits: {health.get('within_limits', False)}")
    
    print("\n=== System Tool Test Complete ===")

if __name__ == "__main__":
    test_system_tool()
