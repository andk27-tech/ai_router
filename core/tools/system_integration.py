#!/usr/bin/env python3
"""
System Integration Module
시스템 통합 - 안전한 실행 환경, 자원 모니터링, 권한 관리
"""

import os
import re
import pwd
import grp
import stat
import subprocess
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import defaultdict

from .system_tool import SystemTool


class PermissionLevel(Enum):
    """권한 수준"""
    NONE = 0
    READ = 1
    WRITE = 2
    EXECUTE = 4
    ADMIN = 8


class ResourceAlertLevel(Enum):
    """자원 알림 수준"""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class SafeExecutionContext:
    """안전한 실행 컨텍스트"""
    allowed_directories: List[str]
    blocked_commands: List[str]
    max_execution_time: int
    max_memory_mb: int
    user_permissions: int
    chroot_path: Optional[str] = None


@dataclass
class ResourceAlert:
    """자원 알림"""
    alert_id: str
    resource_type: str
    alert_level: ResourceAlertLevel
    current_value: float
    threshold: float
    message: str
    timestamp: str


@dataclass
class PermissionCheck:
    """권한 체크 결과"""
    allowed: bool
    required_permission: str
    current_permission: str
    reason: str
    escalation_needed: bool


class SystemIntegration:
    """시스템 통합 클래스"""
    
    def __init__(self):
        self.system_tool = SystemTool()
        
        # 안전한 실행 환경 설정
        self.safe_execution_config = {
            'allowed_directories': [
                '/home/lks/ai_router',
                '/tmp',
                '/var/tmp'
            ],
            'blocked_commands': [
                'rm -rf /', 'mkfs', 'dd if=/dev/zero',
                ':(){ :|:& };:', 'shutdown', 'reboot', 'init 0',
                'del /', 'format', 'fdisk'
            ],
            'max_execution_time': 300,  # 5분
            'max_memory_mb': 512,
            'forbidden_paths': [
                '/etc/passwd', '/etc/shadow', '/root',
                '/bin/sh', '/bin/bash'
            ]
        }
        
        # 권한 설정
        self.permission_config = {
            'default_level': PermissionLevel.READ,
            'agent_user': 'ai_agent',
            'allowed_groups': ['users', 'ai_agents'],
            'admin_commands': ['sudo', 'su', 'passwd', 'usermod']
        }
        
        # 자원 모니터링 설정
        self.monitoring_config = {
            'cpu_warning': 70.0,
            'cpu_critical': 90.0,
            'memory_warning': 75.0,
            'memory_critical': 90.0,
            'disk_warning': 80.0,
            'disk_critical': 95.0,
            'check_interval': 30  # seconds
        }
        
        # 알림 히스토리
        self.alert_history = []
        self.execution_log = []
    
    # ==================== 안전한 실행 환경 ====================
    
    def validate_command_safety(self, command: str) -> Dict[str, Any]:
        """
        명령어 안전성 검증
        
        Args:
            command: 검증할 명령어
            
        Returns:
            안전성 검증 결과
        """
        command_lower = command.lower().strip()
        
        # 위험한 명령어 패턴 체크
        for blocked in self.safe_execution_config['blocked_commands']:
            if blocked.lower() in command_lower:
                return {
                    'safe': False,
                    'reason': f'차단된 명령어 패턴 감지: {blocked}',
                    'risk_level': 'critical',
                    'suggestion': '이 명령어는 시스템 안전을 위해 차단되었습니다'
                }
        
        # 경로 접근 체크
        for forbidden in self.safe_execution_config['forbidden_paths']:
            if forbidden in command:
                return {
                    'safe': False,
                    'reason': f'금지된 경로 접근 시도: {forbidden}',
                    'risk_level': 'high',
                    'suggestion': '해당 경로에 접근할 권한이 없습니다'
                }
        
        # 쉘 메타문자 체크
        dangerous_patterns = [
            r'[`;|&]',  # 쉘 메타문자
            r'\$\(.*\)',  # 명령어 치환
            r'<\s*/dev/',  # 디바이스 파일 리디렉션
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, command):
                return {
                    'safe': False,
                    'reason': f'위험한 쉘 패턴 감지: {pattern}',
                    'risk_level': 'medium',
                    'suggestion': '쉘 메타문자를 사용하지 마세요'
                }
        
        return {
            'safe': True,
            'reason': '명령어가 안전합니다',
            'risk_level': 'low',
            'suggestion': None
        }
    
    def create_safe_execution_context(self, 
                                     custom_config: Optional[Dict] = None) -> SafeExecutionContext:
        """
        안전한 실행 컨텍스트 생성
        
        Args:
            custom_config: 사용자 정의 설정
            
        Returns:
            안전한 실행 컨텍스트
        """
        config = custom_config or {}
        
        return SafeExecutionContext(
            allowed_directories=config.get(
                'allowed_directories',
                self.safe_execution_config['allowed_directories']
            ),
            blocked_commands=config.get(
                'blocked_commands',
                self.safe_execution_config['blocked_commands']
            ),
            max_execution_time=config.get(
                'max_execution_time',
                self.safe_execution_config['max_execution_time']
            ),
            max_memory_mb=config.get(
                'max_memory_mb',
                self.safe_execution_config['max_memory_mb']
            ),
            user_permissions=config.get('user_permissions', PermissionLevel.READ.value),
            chroot_path=config.get('chroot_path')
        )
    
    def execute_in_sandbox(self, 
                          command: str,
                          context: Optional[SafeExecutionContext] = None) -> Dict[str, Any]:
        """
        샌드박스 환경에서 명령어 실행
        
        Args:
            command: 실행할 명령어
            context: 실행 컨텍스트
            
        Returns:
            실행 결과
        """
        # 안전성 검증
        safety_check = self.validate_command_safety(command)
        if not safety_check['safe']:
            return {
                'success': False,
                'error': safety_check['reason'],
                'risk_level': safety_check['risk_level'],
                'suggestion': safety_check['suggestion']
            }
        
        ctx = context or self.create_safe_execution_context()
        
        try:
            # 타임아웃 및 메모리 제한으로 실행
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=ctx.max_execution_time,
                # 메모리 제한은 리소스 제한으로 구현 (Linux)
                preexec_fn=self._set_memory_limit if os.name != 'nt' else None
            )
            
            # 실행 로그 기록
            self._log_execution(command, True, result.returncode)
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout[:1000],  # 처음 1000자만
                'stderr': result.stderr[:500] if result.stderr else '',
                'execution_time': None,  # TODO: 측정
                'memory_used': None  # TODO: 측정
            }
            
        except subprocess.TimeoutExpired:
            self._log_execution(command, False, None, 'timeout')
            return {
                'success': False,
                'error': f'실행 시간 초과 ({ctx.max_execution_time}초)',
                'risk_level': 'warning'
            }
            
        except Exception as e:
            self._log_execution(command, False, None, str(e))
            return {
                'success': False,
                'error': str(e),
                'risk_level': 'error'
            }
    
    def _set_memory_limit(self):
        """메모리 제한 설정 (Linux)"""
        try:
            import resource
            soft, hard = resource.getrlimit(resource.RLIMIT_AS)
            max_memory_bytes = self.safe_execution_config['max_memory_mb'] * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (max_memory_bytes, hard))
        except Exception:
            pass
    
    def validate_path_access(self, path: str, 
                            required_permission: str = 'read') -> Dict[str, Any]:
        """
        경로 접근 권한 검증
        
        Args:
            path: 검증할 경로
            required_permission: 필요한 권한 (read/write/execute)
            
        Returns:
            접근 권한 검증 결과
        """
        # 금지된 경로 체크
        for forbidden in self.safe_execution_config['forbidden_paths']:
            if path.startswith(forbidden) or forbidden in path:
                return {
                    'allowed': False,
                    'reason': f'금지된 경로: {forbidden}',
                    'risk_level': 'critical'
                }
        
        # 허용된 디렉토리 체크
        allowed = False
        for allowed_dir in self.safe_execution_config['allowed_directories']:
            if path.startswith(allowed_dir):
                allowed = True
                break
        
        if not allowed:
            return {
                'allowed': False,
                'reason': '허용되지 않은 디렉토리 접근',
                'allowed_directories': self.safe_execution_config['allowed_directories'],
                'risk_level': 'medium'
            }
        
        # 파일 존재 및 권한 체크
        if os.path.exists(path):
            if required_permission == 'write':
                if not os.access(path, os.W_OK):
                    return {
                        'allowed': False,
                        'reason': '쓰기 권한 없음',
                        'risk_level': 'low'
                    }
            elif required_permission == 'read':
                if not os.access(path, os.R_OK):
                    return {
                        'allowed': False,
                        'reason': '읽기 권한 없음',
                        'risk_level': 'low'
                    }
        
        return {
            'allowed': True,
            'reason': '접근 허용',
            'risk_level': 'none'
        }
    
    # ==================== 자원 모니터링 ====================
    
    def monitor_resources(self) -> Dict[str, Any]:
        """
        시스템 자원 모니터링
        
        Returns:
            자원 상태 및 알림
        """
        alerts = []
        
        # CPU 체크
        cpu_info = self.system_tool.get_cpu_info()
        if cpu_info.get('success'):
            cpu_percent = cpu_info['cpu'].get('percent', 0)
            
            if cpu_percent > self.monitoring_config['cpu_critical']:
                alerts.append(self._create_alert(
                    'cpu', ResourceAlertLevel.CRITICAL,
                    cpu_percent, self.monitoring_config['cpu_critical'],
                    f'CPU 사용량 위험: {cpu_percent}%'
                ))
            elif cpu_percent > self.monitoring_config['cpu_warning']:
                alerts.append(self._create_alert(
                    'cpu', ResourceAlertLevel.WARNING,
                    cpu_percent, self.monitoring_config['cpu_warning'],
                    f'CPU 사용량 경고: {cpu_percent}%'
                ))
        
        # 메모리 체크
        memory_info = self.system_tool.get_memory_info()
        if memory_info.get('success'):
            mem_percent = memory_info['memory'].get('percent_used', 0)
            
            if mem_percent > self.monitoring_config['memory_critical']:
                alerts.append(self._create_alert(
                    'memory', ResourceAlertLevel.CRITICAL,
                    mem_percent, self.monitoring_config['memory_critical'],
                    f'메모리 사용량 위험: {mem_percent}%'
                ))
            elif mem_percent > self.monitoring_config['memory_warning']:
                alerts.append(self._create_alert(
                    'memory', ResourceAlertLevel.WARNING,
                    mem_percent, self.monitoring_config['memory_warning'],
                    f'메모리 사용량 경고: {mem_percent}%'
                ))
        
        # 디스크 체크
        disk_info = self.system_tool.get_disk_info()
        if disk_info.get('success'):
            disk_percent = disk_info['root_partition'].get('percent', 0)
            
            if disk_percent > self.monitoring_config['disk_critical']:
                alerts.append(self._create_alert(
                    'disk', ResourceAlertLevel.CRITICAL,
                    disk_percent, self.monitoring_config['disk_critical'],
                    f'디스크 사용량 위험: {disk_percent}%'
                ))
            elif disk_percent > self.monitoring_config['disk_warning']:
                alerts.append(self._create_alert(
                    'disk', ResourceAlertLevel.WARNING,
                    disk_percent, self.monitoring_config['disk_warning'],
                    f'디스크 사용량 경고: {disk_percent}%'
                ))
        
        # 알림 저장
        for alert in alerts:
            self.alert_history.append(alert)
        
        # 최근 알림만 유지
        self.alert_history = self.alert_history[-100:]
        
        return {
            'timestamp': datetime.now().isoformat(),
            'alerts': [
                {
                    'alert_id': a.alert_id,
                    'resource_type': a.resource_type,
                    'level': a.alert_level.value,
                    'current_value': a.current_value,
                    'threshold': a.threshold,
                    'message': a.message
                }
                for a in alerts
            ],
            'alert_count': len(alerts),
            'overall_status': 'critical' if any(a.alert_level == ResourceAlertLevel.CRITICAL for a in alerts) else \
                            ('warning' if any(a.alert_level == ResourceAlertLevel.WARNING for a in alerts) else 'normal')
        }
    
    def _create_alert(self, resource_type: str, level: ResourceAlertLevel,
                     current: float, threshold: float, message: str) -> ResourceAlert:
        """자원 알림 생성"""
        return ResourceAlert(
            alert_id=f"alert_{resource_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            resource_type=resource_type,
            alert_level=level,
            current_value=current,
            threshold=threshold,
            message=message,
            timestamp=datetime.now().isoformat()
        )
    
    def get_resource_usage_trend(self, hours: int = 1) -> Dict[str, Any]:
        """
        자원 사용량 추이 조회
        
        Args:
            hours: 조회할 시간 범위
            
        Returns:
            자원 사용 추이
        """
        # 현재 자원 상태
        current = self.system_tool.get_system_summary()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'hours': hours,
            'current_status': current.get('overall_status', 'unknown'),
            'current_cpu': current.get('cpu', {}).get('percent', 0),
            'current_memory': current.get('memory', {}).get('percent_used', 0),
            'current_disk': current.get('disk', {}).get('percent', 0),
            'recent_alerts': len([a for a in self.alert_history 
                                if (datetime.now() - datetime.fromisoformat(a.timestamp)).seconds < hours * 3600])
        }
    
    # ==================== 권한 관리 ====================
    
    def check_permission(self, 
                        action: str,
                        user: Optional[str] = None) -> PermissionCheck:
        """
        권한 체크
        
        Args:
            action: 수행하려는 작업
            user: 사용자 (None이면 현재 사용자)
            
        Returns:
            권한 체크 결과
        """
        user = user or os.getlogin()
        
        # 작업별 필요 권한 정의
        action_permissions = {
            'read_file': PermissionLevel.READ,
            'write_file': PermissionLevel.WRITE,
            'execute_command': PermissionLevel.EXECUTE,
            'system_modify': PermissionLevel.ADMIN,
            'user_manage': PermissionLevel.ADMIN,
            'process_kill': PermissionLevel.EXECUTE
        }
        
        required = action_permissions.get(action, PermissionLevel.READ)
        
        # 현재 사용자 권한 확인
        current_level = self._get_user_permission_level(user)
        
        # 권한 비교
        if current_level.value >= required.value:
            return PermissionCheck(
                allowed=True,
                required_permission=required.name,
                current_permission=current_level.name,
                reason='권한 있음',
                escalation_needed=False
            )
        else:
            return PermissionCheck(
                allowed=False,
                required_permission=required.name,
                current_permission=current_level.name,
                reason=f'{required.name} 권한 필요, 현재 {current_level.name}',
                escalation_needed=required.value > PermissionLevel.WRITE.value
            )
    
    def _get_user_permission_level(self, user: str) -> PermissionLevel:
        """사용자 권한 수준 조회"""
        try:
            # 현재 사용자가 ai_agent인 경우
            if user == self.permission_config['agent_user']:
                return self.permission_config['default_level']
            
            # root 체크
            if user == 'root':
                return PermissionLevel.ADMIN
            
            # sudo 그룹 체크
            user_groups = [g.gr_name for g in grp.getgrall() if user in g.gr_mem]
            if 'sudo' in user_groups or 'admin' in user_groups:
                return PermissionLevel.ADMIN
            
            # 허용된 그룹 체크
            for allowed_group in self.permission_config['allowed_groups']:
                if allowed_group in user_groups:
                    return PermissionLevel.WRITE
            
            return PermissionLevel.READ
            
        except Exception:
            return PermissionLevel.READ
    
    def request_elevation(self, 
                         action: str,
                         reason: str,
                         requester: str) -> Dict[str, Any]:
        """
        권한 상승 요청
        
        Args:
            action: 수행하려는 작업
            reason: 요청 사유
            requester: 요청자
            
        Returns:
            권한 상승 요청 결과
        """
        # 권한 체크
        check = self.check_permission(action, requester)
        
        if check.allowed:
            return {
                'granted': True,
                'reason': '이미 권한이 있습니다',
                'temporary_elevation': False
            }
        
        if not check.escalation_needed:
            return {
                'granted': False,
                'reason': check.reason,
                'suggestion': '기본 권한 요청을 진행하세요',
                'temporary_elevation': False
            }
        
        # 상승 필요한 경우 - 관리자 승인 대기
        return {
            'granted': False,
            'pending_approval': True,
            'reason': check.reason,
            'request_details': {
                'action': action,
                'reason': reason,
                'requester': requester,
                'required_permission': check.required_permission
            },
            'suggestion': '관리자 승인이 필요합니다',
            'temporary_elevation': False
        }
    
    def get_system_health_for_agents(self) -> Dict[str, Any]:
        """
        에이전트용 시스템 건강 상태
        
        Returns:
            에이전트에 제공할 시스템 상태
        """
        # 안전한 정보만 제공
        summary = self.system_tool.get_system_summary()
        
        if summary.get('success'):
            return {
                'safe_to_execute': summary['overall_status'] == 'healthy',
                'overall_status': summary['overall_status'],
                'resource_pressure': any([
                    summary.get('cpu', {}).get('status') == 'high_load',
                    summary.get('memory', {}).get('status') == 'critical'
                ]),
                'cpu_percent': summary['cpu'].get('percent', 0),
                'memory_percent': summary['memory'].get('percent_used', 0),
                'recommendation': '시스템 부하가 높습니다, 작업을 지연하세요' 
                    if summary['overall_status'] != 'healthy' else '시스템 정상, 작업 진행 가능'
            }
        
        return {
            'safe_to_execute': False,
            'error': '시스템 상태를 확인할 수 없습니다'
        }
    
    def _log_execution(self, command: str, success: bool, 
                      returncode: Optional[int], error: Optional[str] = None):
        """실행 로그 기록"""
        self.execution_log.append({
            'timestamp': datetime.now().isoformat(),
            'command': command[:100],
            'success': success,
            'returncode': returncode,
            'error': error
        })
        
        # 최근 로그만 유지
        self.execution_log = self.execution_log[-1000:]
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """실행 통계 반환"""
        if not self.execution_log:
            return {'message': '실행 기록이 없습니다'}
        
        total = len(self.execution_log)
        successful = sum(1 for e in self.execution_log if e['success'])
        
        return {
            'total_executions': total,
            'successful': successful,
            'failed': total - successful,
            'success_rate': successful / total if total > 0 else 0,
            'recent_failures': [
                e for e in self.execution_log[-10:] 
                if not e['success']
            ]
        }


# 편의 함수
def check_system_safety() -> Dict[str, Any]:
    """시스템 안전성 빠른 체크"""
    integration = SystemIntegration()
    
    # 자원 모니터링
    resources = integration.monitor_resources()
    
    # 시스템 건강
    health = integration.get_system_health_for_agents()
    
    return {
        'safe_to_proceed': resources['overall_status'] == 'normal' and health['safe_to_execute'],
        'resource_status': resources['overall_status'],
        'system_status': health.get('overall_status', 'unknown'),
        'alerts': resources['alert_count'],
        'recommendation': health.get('recommendation', '상태를 확인하세요')
    }
