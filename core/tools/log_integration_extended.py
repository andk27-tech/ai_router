#!/usr/bin/env python3
"""
Log Integration Extended Module
로그 통합 확장 - 실제 시스템 로그 접근, 프로세스 로그, 권한 관리
"""

import os
import re
import glob
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Set
from collections import defaultdict

from .log_tool import LogTool


class SystemLogIntegration:
    """시스템 로그 통합 관리 클래스"""
    
    def __init__(self, 
                 log_base_path: str = "/home/lks/ai_router/log",
                 allow_system_logs: bool = True):
        self.log_tool = LogTool(log_base_path)
        self.log_base_path = Path(log_base_path)
        self.allow_system_logs = allow_system_logs
        
        # 시스템 로그 경로 정의
        self.system_log_paths = {
            'syslog': ['/var/log/syslog', '/var/log/messages'],
            'auth': ['/var/log/auth.log', '/var/log/secure'],
            'kern': ['/var/log/kern.log'],
            'daemon': ['/var/log/daemon.log'],
            'cron': ['/var/log/cron.log'],
            'boot': ['/var/log/boot.log'],
            'dpkg': ['/var/log/dpkg.log'],
            'apt': ['/var/log/apt'],
            'apache': ['/var/log/apache2', '/var/log/httpd'],
            'nginx': ['/var/log/nginx'],
            'mysql': ['/var/log/mysql', '/var/log/mariadb'],
            'postgresql': ['/var/log/postgresql'],
            'redis': ['/var/log/redis'],
            'docker': ['/var/log/docker'],
            'journal': ['/var/log/journal'],
        }
        
        # 에이전트별 로그 접근 권한
        self.agent_permissions = defaultdict(lambda: {
            'allowed_system_logs': ['syslog', 'daemon', 'boot'],
            'allowed_processes': [],
            'read_only': True,
            'max_lines': 1000
        })
        
        # 특정 에이전트 권한 설정
        self.agent_permissions['admin'] = {
            'allowed_system_logs': list(self.system_log_paths.keys()),
            'allowed_processes': [],
            'read_only': False,
            'max_lines': 10000
        }
        
        self.agent_permissions['debugger'] = {
            'allowed_system_logs': ['syslog', 'kern', 'daemon', 'boot', 'dpkg'],
            'allowed_processes': [],
            'read_only': True,
            'max_lines': 5000
        }
        
        self.agent_permissions['monitor'] = {
            'allowed_system_logs': ['syslog', 'daemon', 'cron'],
            'allowed_processes': [],
            'read_only': True,
            'max_lines': 500
        }
        
        # 프로세스 로그 매핑
        self.process_log_mapping = {}
        
        # 접근 로그
        self.access_log = []
    
    def get_system_log_access(self, agent_id: str,
                              log_types: Optional[List[str]] = None,
                              lines: int = 100) -> Dict[str, Any]:
        """
        시스템 로그 접근
        
        Args:
            agent_id: 에이전트 ID
            log_types: 접근할 로그 타입 (None이면 권한 내 전체)
            lines: 읽을 라인 수
            
        Returns:
            시스템 로그 접근 결과
        """
        try:
            # 권한 확인
            perms = self.agent_permissions.get(agent_id, self.agent_permissions['default'])
            
            # 요청된 로그 타입이 권한 내인지 확인
            allowed_types = perms['allowed_system_logs']
            if log_types is None:
                log_types = allowed_types
            else:
                log_types = [lt for lt in log_types if lt in allowed_types]
            
            if not log_types:
                return {
                    'success': False,
                    'error': f'에이전트 {agent_id}는 시스템 로그에 접근할 권한이 없습니다',
                    'allowed_types': allowed_types
                }
            
            # 라인 수 제한
            max_lines = min(lines, perms['max_lines'])
            
            results = {}
            total_logs = 0
            
            for log_type in log_types:
                log_paths = self.system_log_paths.get(log_type, [])
                
                for log_path in log_paths:
                    if os.path.exists(log_path):
                        try:
                            # 파일 읽기
                            content = self._read_log_file(log_path, max_lines)
                            
                            results[log_type] = {
                                'path': log_path,
                                'lines_read': len(content.split('\n')),
                                'content_preview': content[:2000],  # 처음 2000자
                                'size_bytes': os.path.getsize(log_path),
                                'modified': datetime.fromtimestamp(
                                    os.path.getmtime(log_path)
                                ).isoformat()
                            }
                            total_logs += 1
                            break  # 해당 타입의 첫 번째 존재하는 파일만
                            
                        except PermissionError:
                            results[log_type] = {
                                'path': log_path,
                                'error': '읽기 권한 없음'
                            }
                        except Exception as e:
                            results[log_type] = {
                                'path': log_path,
                                'error': str(e)
                            }
            
            # 접근 로그 기록
            self._record_access(agent_id, 'system_log', {
                'log_types': log_types,
                'lines_requested': lines,
                'results_count': total_logs
            })
            
            return {
                'success': True,
                'agent_id': agent_id,
                'logs_accessed': results,
                'total_logs': total_logs,
                'read_only': perms['read_only'],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_process_log(self, agent_id: str,
                       process_name: Optional[str] = None,
                       pid: Optional[int] = None,
                       lines: int = 50) -> Dict[str, Any]:
        """
        프로세스 로그 접근
        
        Args:
            agent_id: 에이전트 ID
            process_name: 프로세스 이름
            pid: 프로세스 ID
            lines: 읽을 라인 수
            
        Returns:
            프로세스 로그 정보
        """
        try:
            import psutil
            
            results = {}
            
            if pid:
                # 특정 PID의 로그
                try:
                    proc = psutil.Process(pid)
                    proc_info = self._get_process_log_info(proc, lines)
                    results[pid] = proc_info
                except psutil.NoSuchProcess:
                    return {'success': False, 'error': f'프로세스 {pid}를 찾을 수 없습니다'}
                    
            elif process_name:
                # 이름으로 검색
                matching_procs = []
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if process_name.lower() in proc.info['name'].lower():
                            matching_procs.append(proc)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                for proc in matching_procs[:5]:  # 최대 5개 프로세스
                    try:
                        proc_info = self._get_process_log_info(proc, lines)
                        results[proc.pid] = proc_info
                    except Exception:
                        continue
            
            else:
                # 전체 프로세스 요약
                top_cpu = []
                top_memory = []
                
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                    try:
                        info = proc.info
                        top_cpu.append((info['pid'], info['name'], info.get('cpu_percent', 0)))
                        top_memory.append((info['pid'], info['name'], info.get('memory_percent', 0)))
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                top_cpu.sort(key=lambda x: x[2], reverse=True)
                top_memory.sort(key=lambda x: x[2], reverse=True)
                
                results = {
                    'summary': True,
                    'top_cpu': [{'pid': p[0], 'name': p[1], 'cpu': round(p[2], 2)} for p in top_cpu[:5]],
                    'top_memory': [{'pid': p[0], 'name': p[1], 'memory': round(p[2], 2)} for p in top_memory[:5]],
                    'total_processes': len(list(psutil.process_iter()))
                }
            
            # 접근 로그 기록
            self._record_access(agent_id, 'process_log', {
                'process_name': process_name,
                'pid': pid,
                'results_count': len(results) if not results.get('summary') else 0
            })
            
            return {
                'success': True,
                'agent_id': agent_id,
                'process_logs': results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_process_log_info(self, proc, lines: int) -> Dict[str, Any]:
        """프로세스 로그 정보 수집"""
        try:
            with proc.oneshot():
                info = {
                    'pid': proc.pid,
                    'name': proc.name(),
                    'status': proc.status(),
                    'cpu_percent': round(proc.cpu_percent(), 2),
                    'memory_mb': round(proc.memory_info().rss / (1024 * 1024), 2),
                    'memory_percent': round(proc.memory_percent(), 2),
                    'create_time': datetime.fromtimestamp(proc.create_time()).isoformat(),
                    'username': proc.username(),
                    'cmdline': ' '.join(proc.cmdline())[:200] if proc.cmdline() else '',
                    'num_threads': proc.num_threads(),
                    'open_files_count': len(proc.open_files()) if hasattr(proc, 'open_files') else -1,
                    'connections_count': len(proc.connections()) if hasattr(proc, 'connections') else -1,
                }
                
                # 프로세스별 로그 파일 추론
                inferred_logs = self._infer_process_logs(proc)
                if inferred_logs:
                    info['inferred_logs'] = inferred_logs
                
                return info
                
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {'error': '접근 불가'}
    
    def _infer_process_logs(self, proc) -> List[str]:
        """프로세스에서 로그 파일 경로 추론"""
        logs = []
        
        try:
            # 실행 파일 경로에서 로그 디렉토리 추론
            exe = proc.exe()
            if exe:
                base_dir = os.path.dirname(exe)
                possible_logs = [
                    os.path.join(base_dir, 'logs'),
                    os.path.join(base_dir, '..', 'logs'),
                    os.path.join(base_dir, 'log'),
                ]
                for log_dir in possible_logs:
                    if os.path.exists(log_dir):
                        logs.append(log_dir)
            
            # 열린 파일 중 로그 파일 찾기
            try:
                for file in proc.open_files():
                    if 'log' in file.path.lower() and file.path.endswith(('.log', '.txt')):
                        logs.append(file.path)
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass
                
        except Exception:
            pass
        
        return list(set(logs))[:5]  # 중복 제거, 최대 5개
    
    def analyze_system_errors(self, agent_id: str,
                             hours: int = 24,
                             severity: str = 'error') -> Dict[str, Any]:
        """
        시스템 에러 분석
        
        Args:
            agent_id: 에이전트 ID
            hours: 분석할 시간 범위
            severity: 심각도 (error, warning, critical)
            
        Returns:
            에러 분석 결과
        """
        try:
            # syslog 접근 권한 확인
            perms = self.agent_permissions.get(agent_id, self.agent_permissions['default'])
            if 'syslog' not in perms['allowed_system_logs']:
                return {
                    'success': False,
                    'error': 'syslog 접근 권한이 없습니다'
                }
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            errors = []
            
            # syslog 분석
            for log_path in self.system_log_paths.get('syslog', []):
                if os.path.exists(log_path):
                    try:
                        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                            for line_num, line in enumerate(f, 1):
                                # 타임스탬프 파싱
                                line_time = self._parse_syslog_timestamp(line)
                                if line_time and line_time < cutoff_time:
                                    continue
                                
                                # 에러 패턴 매칭
                                if self._is_error_line(line, severity):
                                    errors.append({
                                        'source': log_path,
                                        'line_number': line_num,
                                        'timestamp': line_time.isoformat() if line_time else None,
                                        'message': line.strip()[:200],
                                        'severity': severity
                                    })
                                    
                                if len(errors) >= perms['max_lines']:
                                    break
                                    
                    except PermissionError:
                        continue
                    except Exception:
                        continue
            
            # 에러 유형 분류
            error_types = defaultdict(int)
            for error in errors:
                error_type = self._classify_error(error['message'])
                error_types[error_type] += 1
            
            return {
                'success': True,
                'analysis_period_hours': hours,
                'severity_filter': severity,
                'total_errors': len(errors),
                'error_types': dict(error_types),
                'recent_errors': errors[:20],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _parse_syslog_timestamp(self, line: str) -> Optional[datetime]:
        """syslog 타임스탬프 파싱"""
        # syslog 형식: "Apr 11 20:30:45" 또는 "2026-04-11T20:30:45"
        patterns = [
            r'^(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})',
            r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})',
        ]
        
        current_year = datetime.now().year
        
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                ts_str = match.group(1)
                try:
                    if '-' in ts_str:
                        return datetime.fromisoformat(ts_str)
                    else:
                        # syslog 형식에 연도 추가
                        return datetime.strptime(f"{current_year} {ts_str}", "%Y %b %d %H:%M:%S")
                except ValueError:
                    continue
        
        return None
    
    def _is_error_line(self, line: str, severity: str) -> bool:
        """에러 라인 판단"""
        patterns = {
            'critical': [r'CRITICAL', r'FATAL', r'EMERG', r'ALERT'],
            'error': [r'ERROR', r'ERR', r'FAILED', r'FAILURE', r'EXCEPTION', r'TRACEBACK'],
            'warning': [r'WARNING', r'WARN', r'NOTICE']
        }
        
        checks = patterns.get(severity, patterns['error'])
        return any(re.search(p, line, re.IGNORECASE) for p in checks)
    
    def _classify_error(self, message: str) -> str:
        """에러 메시지 분류"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['permission', 'denied', 'access', 'unauthorized']):
            return 'permission_error'
        elif any(word in message_lower for word in ['memory', 'oom', 'allocation', 'out of memory']):
            return 'memory_error'
        elif any(word in message_lower for word in ['disk', 'space', 'no space', 'filesystem']):
            return 'disk_error'
        elif any(word in message_lower for word in ['network', 'connection', 'timeout', 'refused']):
            return 'network_error'
        elif any(word in message_lower for word in ['process', 'killed', 'terminated', 'signal']):
            return 'process_error'
        else:
            return 'general_error'
    
    def _read_log_file(self, path: str, max_lines: int) -> str:
        """로그 파일 읽기 (끝에서부터)"""
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                return ''.join(lines[-max_lines:])
        except Exception as e:
            return f"[파일 읽기 오류: {e}]"
    
    def _record_access(self, agent_id: str, access_type: str, details: Dict):
        """접근 기록"""
        self.access_log.append({
            'timestamp': datetime.now().isoformat(),
            'agent_id': agent_id,
            'access_type': access_type,
            'details': details
        })
        
        # 최근 1000개만 유지
        self.access_log = self.access_log[-1000:]
    
    def get_access_statistics(self) -> Dict[str, Any]:
        """접근 통계"""
        if not self.access_log:
            return {'message': '접근 기록이 없습니다'}
        
        stats = defaultdict(int)
        for entry in self.access_log:
            stats[entry['access_type']] += 1
        
        return {
            'total_accesses': len(self.access_log),
            'access_types': dict(stats),
            'recent_accesses': self.access_log[-10:]
        }
    
    def grant_permissions(self, agent_id: str, 
                         log_types: List[str],
                         read_only: bool = True,
                         max_lines: int = 1000) -> Dict[str, Any]:
        """
        에이전트 권한 부여
        
        Args:
            agent_id: 에이전트 ID
            log_types: 허용할 로그 타입
            read_only: 읽기 전용 여부
            max_lines: 최대 읽기 라인 수
            
        Returns:
            권한 부여 결과
        """
        self.agent_permissions[agent_id] = {
            'allowed_system_logs': log_types,
            'allowed_processes': [],
            'read_only': read_only,
            'max_lines': max_lines
        }
        
        return {
            'success': True,
            'agent_id': agent_id,
            'granted_permissions': {
                'log_types': log_types,
                'read_only': read_only,
                'max_lines': max_lines
            },
            'timestamp': datetime.now().isoformat()
        }


def quick_system_log_check(agent_id: str = 'monitor') -> Dict[str, Any]:
    """
    빠른 시스템 로그 체크 편의 함수
    
    Returns:
        시스템 로그 요약
    """
    integration = SystemLogIntegration()
    
    # syslog 확인
    result = integration.get_system_log_access(
        agent_id=agent_id,
        log_types=['syslog'],
        lines=50
    )
    
    # 에러 분석
    errors = integration.analyze_system_errors(agent_id, hours=1, severity='error')
    
    return {
        'log_accessible': result.get('success', False),
        'recent_errors': errors.get('total_errors', 0),
        'error_types': errors.get('error_types', {}),
        'status': 'healthy' if errors.get('total_errors', 0) < 5 else 'warning'
    }
