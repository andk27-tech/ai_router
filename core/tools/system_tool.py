#!/usr/bin/env python3
"""
System Tool Module
시스템 툴 - 프로세스 관리, 메모리 사용량 모니터링, 네트워크 상태, 시스템 정보, 자원 제한
"""

import os
import sys
import psutil
import platform
import subprocess
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ProcessStatus(Enum):
    """프로세스 상태"""
    RUNNING = "running"
    SLEEPING = "sleeping"
    STOPPED = "stopped"
    ZOMBIE = "zombie"
    UNKNOWN = "unknown"


@dataclass
class ProcessInfo:
    """프로세스 정보 데이터 클래스"""
    pid: int
    name: str
    status: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    create_time: str
    username: str
    cmdline: List[str]


@dataclass
class MemoryInfo:
    """메모리 정보 데이터 클래스"""
    total_gb: float
    available_gb: float
    used_gb: float
    percent_used: float
    swap_total_gb: float
    swap_used_gb: float
    swap_percent: float


@dataclass
class NetworkInfo:
    """네트워크 정보 데이터 클래스"""
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errors_in: int
    errors_out: int
    interfaces: Dict[str, Any]
    connections: List[Dict[str, Any]]


@dataclass
class SystemInfo:
    """시스템 정보 데이터 클래스"""
    platform: str
    platform_version: str
    architecture: str
    processor: str
    cpu_count: int
    cpu_frequency_mhz: float
    boot_time: str
    hostname: str
    python_version: str


@dataclass
class ResourceLimits:
    """자원 제한 데이터 클래스"""
    max_cpu_percent: float
    max_memory_mb: float
    max_disk_usage_percent: float
    max_network_connections: int
    current_cpu: float
    current_memory: float
    current_disk: float
    current_connections: int


class SystemTool:
    """시스템 툴 클래스"""
    
    def __init__(self):
        self.default_limits = {
            'max_cpu_percent': 80.0,
            'max_memory_mb': 1024.0,
            'max_disk_usage_percent': 85.0,
            'max_network_connections': 100
        }
        self.process_cache = {}
    
    # ==================== 프로세스 관리 ====================
    
    def list_processes(self, limit: int = 20, 
                      order_by: str = 'cpu') -> Dict[str, Any]:
        """
        프로세스 목록 조회
        
        Args:
            limit: 반환할 프로세스 수
            order_by: 정렬 기준 ('cpu', 'memory', 'pid')
            
        Returns:
            프로세스 목록 정보
        """
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'status', 
                                            'cpu_percent', 'memory_percent',
                                            'create_time', 'username', 'cmdline']):
                try:
                    pinfo = proc.info
                    memory_mb = 0
                    
                    # 메모리 사용량 계산
                    try:
                        proc_obj = psutil.Process(pinfo['pid'])
                        memory_mb = proc_obj.memory_info().rss / (1024 * 1024)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                    
                    processes.append(ProcessInfo(
                        pid=pinfo['pid'],
                        name=pinfo['name'] or 'unknown',
                        status=pinfo['status'] or 'unknown',
                        cpu_percent=pinfo['cpu_percent'] or 0.0,
                        memory_percent=pinfo['memory_percent'] or 0.0,
                        memory_mb=memory_mb,
                        create_time=datetime.fromtimestamp(
                            pinfo['create_time']
                        ).isoformat() if pinfo['create_time'] else '',
                        username=pinfo['username'] or 'unknown',
                        cmdline=pinfo['cmdline'] or []
                    ))
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # 정렬
            if order_by == 'cpu':
                processes.sort(key=lambda x: x.cpu_percent, reverse=True)
            elif order_by == 'memory':
                processes.sort(key=lambda x: x.memory_percent, reverse=True)
            elif order_by == 'pid':
                processes.sort(key=lambda x: x.pid)
            
            limited_processes = processes[:limit]
            
            return {
                'success': True,
                'total_processes': len(processes),
                'returned_processes': len(limited_processes),
                'processes': [
                    {
                        'pid': p.pid,
                        'name': p.name,
                        'status': p.status,
                        'cpu_percent': round(p.cpu_percent, 2),
                        'memory_percent': round(p.memory_percent, 2),
                        'memory_mb': round(p.memory_mb, 2),
                        'username': p.username
                    }
                    for p in limited_processes
                ]
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_process_details(self, pid: int) -> Dict[str, Any]:
        """
        특정 프로세스 상세 정보
        
        Args:
            pid: 프로세스 ID
            
        Returns:
            프로세스 상세 정보
        """
        try:
            proc = psutil.Process(pid)
            
            with proc.oneshot():
                info = {
                    'pid': pid,
                    'name': proc.name(),
                    'status': proc.status(),
                    'cpu_percent': round(proc.cpu_percent(), 2),
                    'memory_info': {
                        'rss_mb': round(proc.memory_info().rss / (1024 * 1024), 2),
                        'vms_mb': round(proc.memory_info().vms / (1024 * 1024), 2),
                        'percent': round(proc.memory_percent(), 2)
                    },
                    'create_time': datetime.fromtimestamp(
                        proc.create_time()
                    ).isoformat(),
                    'username': proc.username(),
                    'cmdline': proc.cmdline(),
                    'cpu_times': {
                        'user': proc.cpu_times().user,
                        'system': proc.cpu_times().system
                    },
                    'num_threads': proc.num_threads(),
                    'num_fds': proc.num_fds() if hasattr(proc, 'num_fds') else -1,
                    'io_counters': {
                        'read_bytes': proc.io_counters().read_bytes,
                        'write_bytes': proc.io_counters().write_bytes
                    } if hasattr(proc, 'io_counters') else {}
                }
            
            return {'success': True, 'process': info}
            
        except psutil.NoSuchProcess:
            return {'success': False, 'error': f'프로세스 {pid}를 찾을 수 없습니다'}
        except psutil.AccessDenied:
            return {'success': False, 'error': f'프로세스 {pid}에 접근 권한이 없습니다'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def kill_process(self, pid: int, force: bool = False) -> Dict[str, Any]:
        """
        프로세스 종료
        
        Args:
            pid: 종료할 프로세스 ID
            force: 강제 종료 여부
            
        Returns:
            종료 결과
        """
        try:
            proc = psutil.Process(pid)
            name = proc.name()
            
            if force:
                proc.kill()
                signal_name = 'SIGKILL'
            else:
                proc.terminate()
                signal_name = 'SIGTERM'
            
            return {
                'success': True,
                'message': f'프로세스 {name} (PID: {pid})에 {signal_name} 신호를 보냈습니다',
                'pid': pid,
                'signal': signal_name
            }
            
        except psutil.NoSuchProcess:
            return {'success': False, 'error': f'프로세스 {pid}를 찾을 수 없습니다'}
        except psutil.AccessDenied:
            return {'success': False, 'error': f'프로세스 {pid} 종료 권한이 없습니다'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def find_processes_by_name(self, name: str) -> Dict[str, Any]:
        """
        이름으로 프로세스 검색
        
        Args:
            name: 검색할 프로세스 이름
            
        Returns:
            검색된 프로세스 목록
        """
        try:
            matching = []
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if name.lower() in proc.info['name'].lower():
                        matching.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {
                'success': True,
                'search_term': name,
                'matches': matching,
                'count': len(matching)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ==================== 메모리 모니터링 ====================
    
    def get_memory_info(self) -> Dict[str, Any]:
        """
        메모리 사용량 정보
        
        Returns:
            메모리 정보
        """
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            memory_info = MemoryInfo(
                total_gb=round(mem.total / (1024**3), 2),
                available_gb=round(mem.available / (1024**3), 2),
                used_gb=round(mem.used / (1024**3), 2),
                percent_used=mem.percent,
                swap_total_gb=round(swap.total / (1024**3), 2),
                swap_used_gb=round(swap.used / (1024**3), 2),
                swap_percent=swap.percent
            )
            
            return {
                'success': True,
                'memory': {
                    'total_gb': memory_info.total_gb,
                    'available_gb': memory_info.available_gb,
                    'used_gb': memory_info.used_gb,
                    'percent_used': memory_info.percent_used,
                    'status': self._assess_memory_status(memory_info.percent_used)
                },
                'swap': {
                    'total_gb': memory_info.swap_total_gb,
                    'used_gb': memory_info.swap_used_gb,
                    'percent': memory_info.swap_percent
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_top_memory_processes(self, limit: int = 10) -> Dict[str, Any]:
        """
        메모리 사용량 상위 프로세스
        
        Args:
            limit: 반환할 프로세스 수
            
        Returns:
            상위 메모리 사용 프로세스
        """
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'memory_info']):
                try:
                    pinfo = proc.info
                    memory_mb = pinfo['memory_info'].rss / (1024 * 1024) if pinfo['memory_info'] else 0
                    
                    processes.append({
                        'pid': pinfo['pid'],
                        'name': pinfo['name'],
                        'memory_percent': round(pinfo['memory_percent'] or 0, 2),
                        'memory_mb': round(memory_mb, 2)
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # 메모리 사용량 기준 정렬
            processes.sort(key=lambda x: x['memory_percent'], reverse=True)
            
            return {
                'success': True,
                'processes': processes[:limit]
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ==================== 네트워크 상태 ====================
    
    def get_network_info(self) -> Dict[str, Any]:
        """
        네트워크 상태 정보
        
        Returns:
            네트워크 정보
        """
        try:
            # IO 카운터
            io_counters = psutil.net_io_counters()
            
            # 인터페이스 정보
            interfaces = {}
            for iface_name, iface_addrs in psutil.net_if_addrs().items():
                interfaces[iface_name] = {
                    'addresses': [
                        {
                            'family': addr.family.name,
                            'address': addr.address,
                            'netmask': addr.netmask,
                            'broadcast': addr.broadcast
                        }
                        for addr in iface_addrs
                    ]
                }
            
            # 인터페이스 통계
            for iface_name, stats in psutil.net_if_stats().items():
                if iface_name in interfaces:
                    interfaces[iface_name]['stats'] = {
                        'is_up': stats.isup,
                        'speed_mbps': stats.speed,
                        'mtu': stats.mtu
                    }
            
            # 연결 정보
            connections = []
            for conn in psutil.net_connections(kind='inet')[:20]:  # 상위 20개만
                try:
                    connections.append({
                        'fd': conn.fd,
                        'family': conn.family.name if hasattr(conn.family, 'name') else str(conn.family),
                        'type': conn.type.name if hasattr(conn.type, 'name') else str(conn.type),
                        'local_addr': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                        'remote_addr': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                        'status': conn.status
                    })
                except:
                    continue
            
            network_info = NetworkInfo(
                bytes_sent=io_counters.bytes_sent,
                bytes_recv=io_counters.bytes_recv,
                packets_sent=io_counters.packets_sent,
                packets_recv=io_counters.packets_recv,
                errors_in=io_counters.errin,
                errors_out=io_counters.errout,
                interfaces=interfaces,
                connections=connections
            )
            
            return {
                'success': True,
                'io_counters': {
                    'bytes_sent': network_info.bytes_sent,
                    'bytes_recv': network_info.bytes_recv,
                    'packets_sent': network_info.packets_sent,
                    'packets_recv': network_info.packets_recv,
                    'errors_in': network_info.errors_in,
                    'errors_out': network_info.errors_out
                },
                'interfaces': network_info.interfaces,
                'active_connections': len(network_info.connections),
                'connections_sample': network_info.connections[:5]
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_network_connectivity(self, host: str = "8.8.8.8", 
                                 timeout: int = 3) -> Dict[str, Any]:
        """
        네트워크 연결 테스트 (ping)
        
        Args:
            host: 테스트할 호스트
            timeout: 타임아웃 (초)
            
        Returns:
            연결 테스트 결과
        """
        try:
            # ping 명령어 실행
            result = subprocess.run(
                ['ping', '-c', '1', '-W', str(timeout), host],
                capture_output=True,
                text=True
            )
            
            success = result.returncode == 0
            
            # 응답 시간 추출 (Linux)
            response_time = None
            if success:
                match = __import__('re').search(r'time=([\d.]+)', result.stdout)
                if match:
                    response_time = float(match.group(1))
            
            return {
                'success': success,
                'host': host,
                'reachable': success,
                'response_time_ms': response_time,
                'output': result.stdout if success else result.stderr
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ==================== 시스템 정보 ====================
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        시스템 기본 정보
        
        Returns:
            시스템 정보
        """
        try:
            cpu_freq = psutil.cpu_freq()
            boot_time = psutil.boot_time()
            
            system_info = SystemInfo(
                platform=platform.system(),
                platform_version=platform.version(),
                architecture=platform.architecture()[0],
                processor=platform.processor(),
                cpu_count=psutil.cpu_count(),
                cpu_frequency_mhz=round(cpu_freq.current, 2) if cpu_freq else 0.0,
                boot_time=datetime.fromtimestamp(boot_time).isoformat(),
                hostname=platform.node(),
                python_version=platform.python_version()
            )
            
            return {
                'success': True,
                'system': {
                    'platform': system_info.platform,
                    'version': system_info.platform_version,
                    'architecture': system_info.architecture,
                    'processor': system_info.processor,
                    'cpu_count': system_info.cpu_count,
                    'cpu_frequency_mhz': system_info.cpu_frequency_mhz,
                    'boot_time': system_info.boot_time,
                    'hostname': system_info.hostname,
                    'python_version': system_info.python_version
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """
        CPU 정보 및 사용량
        
        Returns:
            CPU 정보
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_count_physical = psutil.cpu_count(logical=False)
            cpu_freq = psutil.cpu_freq()
            
            # 코어별 사용량
            per_cpu = psutil.cpu_percent(interval=1, percpu=True)
            
            return {
                'success': True,
                'cpu': {
                    'percent': cpu_percent,
                    'count_logical': cpu_count,
                    'count_physical': cpu_count_physical,
                    'frequency_mhz': round(cpu_freq.current, 2) if cpu_freq else 0,
                    'per_cpu_percent': [round(p, 2) for p in per_cpu],
                    'status': self._assess_cpu_status(cpu_percent)
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_disk_info(self) -> Dict[str, Any]:
        """
        디스크 사용량 정보
        
        Returns:
            디스크 정보
        """
        try:
            disk_usage = psutil.disk_usage('/')
            
            # 파티션 정보
            partitions = []
            for part in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    partitions.append({
                        'device': part.device,
                        'mountpoint': part.mountpoint,
                        'fstype': part.fstype,
                        'total_gb': round(usage.total / (1024**3), 2),
                        'used_gb': round(usage.used / (1024**3), 2),
                        'free_gb': round(usage.free / (1024**3), 2),
                        'percent': usage.percent
                    })
                except PermissionError:
                    continue
            
            return {
                'success': True,
                'root_partition': {
                    'total_gb': round(disk_usage.total / (1024**3), 2),
                    'used_gb': round(disk_usage.used / (1024**3), 2),
                    'free_gb': round(disk_usage.free / (1024**3), 2),
                    'percent': disk_usage.percent,
                    'status': self._assess_disk_status(disk_usage.percent)
                },
                'partitions': partitions
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ==================== 자원 제한 ====================
    
    def check_resource_limits(self, 
                             custom_limits: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        자원 제한 확인
        
        Args:
            custom_limits: 사용자 정의 제한값
            
        Returns:
            자원 상태 및 제한 정보
        """
        try:
            limits = custom_limits or self.default_limits
            
            # 현재 사용량 수집
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # 연결 수 (근사치)
            try:
                connections = len(psutil.net_connections())
            except:
                connections = 0
            
            resource_limits = ResourceLimits(
                max_cpu_percent=limits.get('max_cpu_percent', 80.0),
                max_memory_mb=limits.get('max_memory_mb', 1024.0),
                max_disk_usage_percent=limits.get('max_disk_usage_percent', 85.0),
                max_network_connections=limits.get('max_network_connections', 100),
                current_cpu=cpu_percent,
                current_memory=memory.percent,
                current_disk=disk.percent,
                current_connections=connections
            )
            
            # 상태 평가
            cpu_status = 'normal' if cpu_percent < resource_limits.max_cpu_percent else 'warning'
            memory_status = 'normal' if memory.percent < 80 else 'warning'
            disk_status = 'normal' if disk.percent < resource_limits.max_disk_usage_percent else 'warning'
            
            return {
                'success': True,
                'limits': {
                    'max_cpu_percent': resource_limits.max_cpu_percent,
                    'max_memory_mb': resource_limits.max_memory_mb,
                    'max_disk_usage_percent': resource_limits.max_disk_usage_percent,
                    'max_network_connections': resource_limits.max_network_connections
                },
                'current': {
                    'cpu_percent': round(resource_limits.current_cpu, 2),
                    'memory_percent': round(resource_limits.current_memory, 2),
                    'disk_percent': round(resource_limits.current_disk, 2),
                    'network_connections': resource_limits.current_connections
                },
                'status': {
                    'cpu': cpu_status,
                    'memory': memory_status,
                    'disk': disk_status
                },
                'within_limits': all([
                    cpu_status == 'normal',
                    memory_status == 'normal',
                    disk_status == 'normal'
                ])
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def set_resource_limits(self, limits: Dict[str, float]) -> Dict[str, Any]:
        """
        자원 제한 설정
        
        Args:
            limits: 제한값 딕셔너리
            
        Returns:
            설정 결과
        """
        try:
            valid_keys = ['max_cpu_percent', 'max_memory_mb', 
                         'max_disk_usage_percent', 'max_network_connections']
            
            for key, value in limits.items():
                if key in valid_keys:
                    self.default_limits[key] = float(value)
            
            return {
                'success': True,
                'message': '자원 제한이 업데이트되었습니다',
                'current_limits': self.default_limits
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ==================== 유틸리티 메소드 ====================
    
    def _assess_memory_status(self, percent: float) -> str:
        """메모리 상태 평가"""
        if percent < 60:
            return 'normal'
        elif percent < 80:
            return 'caution'
        else:
            return 'critical'
    
    def _assess_cpu_status(self, percent: float) -> str:
        """CPU 상태 평가"""
        if percent < 50:
            return 'normal'
        elif percent < 80:
            return 'busy'
        else:
            return 'high_load'
    
    def _assess_disk_status(self, percent: float) -> str:
        """디스크 상태 평가"""
        if percent < 70:
            return 'normal'
        elif percent < 85:
            return 'caution'
        else:
            return 'critical'
    
    def get_system_summary(self) -> Dict[str, Any]:
        """
        시스템 종합 요약
        
        Returns:
            시스템 요약 정보
        """
        try:
            # 각 항목 수집
            system = self.get_system_info()
            cpu = self.get_cpu_info()
            memory = self.get_memory_info()
            disk = self.get_disk_info()
            network = self.get_network_info()
            resources = self.check_resource_limits()
            
            # 상위 프로세스
            top_cpu = self.list_processes(limit=5, order_by='cpu')
            top_memory = self.get_top_memory_processes(limit=5)
            
            return {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'system': system.get('system', {}),
                'cpu': cpu.get('cpu', {}),
                'memory': memory.get('memory', {}),
                'disk': disk.get('root_partition', {}),
                'network_summary': {
                    'interfaces': len(network.get('interfaces', {})),
                    'connections': network.get('active_connections', 0)
                },
                'resources': {
                    'within_limits': resources.get('within_limits', False),
                    'status': resources.get('status', {})
                },
                'top_cpu_processes': top_cpu.get('processes', [])[:3],
                'top_memory_processes': top_memory.get('processes', [])[:3],
                'overall_status': self._calculate_overall_status(
                    cpu.get('cpu', {}),
                    memory.get('memory', {}),
                    disk.get('root_partition', {}),
                    resources.get('within_limits', False)
                )
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _calculate_overall_status(self, cpu, memory, disk, within_limits) -> str:
        """전체 시스템 상태 계산"""
        critical_count = 0
        warning_count = 0
        
        if cpu.get('status') == 'high_load':
            critical_count += 1
        elif cpu.get('status') == 'busy':
            warning_count += 1
        
        if memory.get('status') == 'critical':
            critical_count += 1
        elif memory.get('status') == 'caution':
            warning_count += 1
        
        if disk.get('status') == 'critical':
            critical_count += 1
        elif disk.get('status') == 'caution':
            warning_count += 1
        
        if not within_limits:
            warning_count += 1
        
        if critical_count >= 2:
            return 'critical'
        elif critical_count == 1 or warning_count >= 2:
            return 'warning'
        elif warning_count == 1:
            return 'caution'
        else:
            return 'healthy'


def get_system_health() -> Dict[str, Any]:
    """
    시스템 건강 상태 편의 함수
    
    Returns:
        시스템 건강 정보
    """
    tool = SystemTool()
    summary = tool.get_system_summary()
    
    if summary.get('success'):
        return {
            'status': summary['overall_status'],
            'cpu_percent': summary['cpu'].get('percent', 0),
            'memory_percent': summary['memory'].get('percent_used', 0),
            'disk_percent': summary['disk'].get('percent', 0),
            'within_limits': summary['resources']['within_limits']
        }
    
    return {'status': 'unknown', 'error': summary.get('error', 'Unknown error')}
