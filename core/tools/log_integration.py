#!/usr/bin/env python3
"""
Log Integration Module
로그 통합 - 에이전트 로그 접근, 과거 분석, 디버깅 지원
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from collections import defaultdict

from .log_tool import LogTool


class LogIntegration:
    """로그 통합 관리 클래스"""
    
    def __init__(self, log_base_path: str = "/home/lks/ai_router/log"):
        self.log_tool = LogTool(log_base_path)
        self.log_base_path = Path(log_base_path)
        self.session_logs = []
        self.agent_access_log = []
        
    def get_agent_log_access(self, agent_id: str, 
                              time_range: Optional[tuple] = None,
                              log_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        에이전트 로그 접근 권한 관리
        
        Args:
            agent_id: 에이전트 ID
            time_range: (시작시간, 종료시간) 튜플
            log_types: 접근할 로그 타입 리스트 ['system', 'error', 'debug', 'source']
            
        Returns:
            에이전트 접근 가능한 로그 정보
        """
        try:
            accessible_logs = []
            
            # 기본 로그 타입
            if log_types is None:
                log_types = ['system', 'error', 'source']
            
            # 각 로그 타입별 접근
            for log_type in log_types:
                log_dir = self.log_base_path / f"{log_type}_log"
                
                if log_dir.exists():
                    # 시간 범위 필터링
                    for log_file in log_dir.glob("*.log"):
                        file_time = self._extract_time_from_filename(log_file.name)
                        
                        if time_range and file_time:
                            start_time, end_time = time_range
                            if not (start_time <= file_time <= end_time):
                                continue
                        
                        accessible_logs.append({
                            'type': log_type,
                            'path': str(log_file),
                            'name': log_file.name,
                            'timestamp': file_time.isoformat() if file_time else None
                        })
            
            # 접근 로그 기록
            self._record_agent_access(agent_id, 'log_access', {
                'time_range': time_range,
                'log_types': log_types,
                'accessed_count': len(accessible_logs)
            })
            
            return {
                'agent_id': agent_id,
                'accessible_logs': accessible_logs,
                'total_count': len(accessible_logs),
                'access_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f'에이전트 로그 접근 오류: {str(e)}'}
    
    def analyze_historical_logs(self, 
                              hours: int = 24,
                              analysis_type: str = 'error') -> Dict[str, Any]:
        """
        과거 로그 분석
        
        Args:
            hours: 분석할 과거 시간 (기본: 24시간)
            analysis_type: 분석 타입 ('error', 'pattern', 'trend', 'summary')
            
        Returns:
            과거 분석 결과
        """
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # 해당 시간 범위의 로그 파일 수집
            log_files = self._collect_logs_in_timeframe(start_time, end_time)
            
            if analysis_type == 'error':
                return self._analyze_error_history(log_files, hours)
            elif analysis_type == 'pattern':
                return self._analyze_log_patterns(log_files)
            elif analysis_type == 'trend':
                return self._analyze_log_trends(log_files, hours)
            elif analysis_type == 'summary':
                return self._generate_historical_summary(log_files, hours)
            else:
                return {'error': f'지원하지 않는 분석 타입: {analysis_type}'}
                
        except Exception as e:
            return {'error': f'과거 로그 분석 오류: {str(e)}'}
    
    def provide_debugging_support(self, 
                                 error_signature: Optional[str] = None,
                                 session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        디버깅 지원
        
        Args:
            error_signature: 특정 에러 시그니처 검색
            session_id: 세션 ID로 디버깅 정보 검색
            
        Returns:
            디버깅 지원 정보
        """
        try:
            debug_info = {
                'timestamp': datetime.now().isoformat(),
                'error_context': {},
                'related_logs': [],
                'suggestions': []
            }
            
            # 에러 시그니처로 검색
            if error_signature:
                matching_errors = self._search_error_by_signature(error_signature)
                debug_info['error_context'] = {
                    'signature': error_signature,
                    'matching_errors': matching_errors,
                    'occurrence_count': len(matching_errors)
                }
                
                # 자동 제안 생성
                debug_info['suggestions'] = self._generate_debug_suggestions(
                    error_signature, matching_errors
                )
            
            # 세션 ID로 관련 로그 검색
            if session_id:
                session_logs = self._get_session_logs(session_id)
                debug_info['related_logs'] = session_logs
            
            return debug_info
            
        except Exception as e:
            return {'error': f'디버깅 지원 오류: {str(e)}'}
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """최근 에러 목록 조회"""
        try:
            error_log_dir = self.log_base_path / "error_log"
            errors = []
            
            if error_log_dir.exists():
                # 최신 로그 파일부터 확인
                log_files = sorted(error_log_dir.glob("*.log"), 
                                 key=lambda x: x.stat().st_mtime, 
                                 reverse=True)
                
                for log_file in log_files[:3]:  # 최근 3개 파일만
                    result = self.log_tool.parse_log_file(
                        str(log_file.relative_to(self.log_base_path)), 
                        max_lines=100
                    )
                    
                    if 'lines' in result:
                        error_matches = self.log_tool.match_patterns(
                            result['lines'], 
                            self.log_tool.error_patterns
                        )
                        errors.extend(error_matches[:limit])
                        
                        if len(errors) >= limit:
                            break
            
            return errors[:limit]
            
        except Exception as e:
            return [{'error': str(e)}]
    
    def search_logs(self, 
                   query: str,
                   log_types: Optional[List[str]] = None,
                   time_range: Optional[tuple] = None) -> Dict[str, Any]:
        """로그 검색"""
        try:
            results = []
            
            if log_types is None:
                log_types = ['system', 'error', 'source', 'debug']
            
            for log_type in log_types:
                log_dir = self.log_base_path / f"{log_type}_log"
                
                if log_dir.exists():
                    for log_file in log_dir.glob("*.log"):
                        # 시간 범위 필터링
                        if time_range:
                            file_time = self._extract_time_from_filename(log_file.name)
                            if file_time:
                                start, end = time_range
                                if not (start <= file_time <= end):
                                    continue
                        
                        # 파일 내 검색
                        try:
                            with open(log_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if query.lower() in content.lower():
                                    # 매칭 라인 찾기
                                    matching_lines = []
                                    for i, line in enumerate(content.split('\n'), 1):
                                        if query.lower() in line.lower():
                                            matching_lines.append({
                                                'line_number': i,
                                                'content': line[:200]  # 처음 200자만
                                            })
                                    
                                    if matching_lines:
                                        results.append({
                                            'file': str(log_file),
                                            'type': log_type,
                                            'matching_lines': matching_lines[:5]  # 처음 5개만
                                        })
                        except Exception:
                            continue
            
            return {
                'query': query,
                'total_matches': len(results),
                'results': results,
                'search_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f'로그 검색 오류: {str(e)}'}
    
    def _extract_time_from_filename(self, filename: str) -> Optional[datetime]:
        """파일명에서 타임스탬프 추출"""
        try:
            # 형식: YYYY-MM-DD_HH-MM-SS_*.log
            match = re.match(r'(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{2})', filename)
            if match:
                year, month, day, hour, minute, second = match.groups()
                return datetime(int(year), int(month), int(day), 
                              int(hour), int(minute), int(second))
            return None
        except Exception:
            return None
    
    def _record_agent_access(self, agent_id: str, action: str, details: Dict):
        """에이전트 접근 기록"""
        self.agent_access_log.append({
            'agent_id': agent_id,
            'action': action,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    def _collect_logs_in_timeframe(self, start: datetime, end: datetime) -> List[Path]:
        """시간 범위 내 로그 파일 수집"""
        log_files = []
        
        for log_dir in self.log_base_path.glob("*_log"):
            if log_dir.is_dir():
                for log_file in log_dir.glob("*.log"):
                    file_time = self._extract_time_from_filename(log_file.name)
                    if file_time and start <= file_time <= end:
                        log_files.append(log_file)
        
        return sorted(log_files, key=lambda x: x.stat().st_mtime)
    
    def _analyze_error_history(self, log_files: List[Path], hours: int) -> Dict[str, Any]:
        """에러 히스토리 분석"""
        error_counts = defaultdict(int)
        error_types = defaultdict(list)
        
        for log_file in log_files:
            try:
                result = self.log_tool.parse_log_file(
                    str(log_file.relative_to(self.log_base_path)),
                    max_lines=500
                )
                
                if 'lines' in result:
                    errors = self.log_tool.extract_errors(
                        str(log_file.relative_to(self.log_base_path))
                    )
                    
                    if 'errors' in errors:
                        for error in errors['errors']:
                            error_text = error.get('matched_text', '')
                            error_counts[error_text[:50]] += 1  # 처음 50자로 그룹화
                            error_types[error_text[:50]].append({
                                'file': str(log_file),
                                'line': error.get('line_number'),
                                'time': error.get('timestamp')
                            })
            except Exception:
                continue
        
        return {
            'analysis_type': 'error_history',
            'time_range_hours': hours,
            'total_errors': sum(error_counts.values()),
            'unique_errors': len(error_counts),
            'top_errors': sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            'error_details': dict(error_types)
        }
    
    def _analyze_log_patterns(self, log_files: List[Path]) -> Dict[str, Any]:
        """로그 패턴 분석"""
        all_patterns = defaultdict(int)
        
        for log_file in log_files[:10]:  # 처음 10개 파일만
            try:
                result = self.log_tool.parse_log_file(
                    str(log_file.relative_to(self.log_base_path)),
                    max_lines=200
                )
                
                if 'lines' in result:
                    # 기본 패턴 매칭
                    patterns = {
                        'error': self.log_tool.match_patterns(
                            result['lines'], self.log_tool.error_patterns
                        ),
                        'warning': self.log_tool.match_patterns(
                            result['lines'], self.log_tool.warning_patterns
                        ),
                        'info': self.log_tool.match_patterns(
                            result['lines'], self.log_tool.info_patterns
                        )
                    }
                    
                    for pattern_type, matches in patterns.items():
                        all_patterns[pattern_type] += len(matches)
                        
            except Exception:
                continue
        
        return {
            'analysis_type': 'patterns',
            'pattern_counts': dict(all_patterns),
            'analyzed_files': len(log_files[:10])
        }
    
    def _analyze_log_trends(self, log_files: List[Path], hours: int) -> Dict[str, Any]:
        """로그 트렌드 분석"""
        hourly_counts = defaultdict(lambda: defaultdict(int))
        
        for log_file in log_files:
            try:
                file_time = self._extract_time_from_filename(log_file.name)
                if file_time:
                    hour_key = file_time.strftime('%H:00')
                    
                    result = self.log_tool.summarize_log(
                        str(log_file.relative_to(self.log_base_path)),
                        max_lines=100
                    )
                    
                    if 'summary' in result:
                        summary = result['summary']
                        hourly_counts[hour_key]['errors'] += summary.get('error_count', 0)
                        hourly_counts[hour_key]['warnings'] += summary.get('warning_count', 0)
                        hourly_counts[hour_key]['info'] += summary.get('info_count', 0)
                        
            except Exception:
                continue
        
        return {
            'analysis_type': 'trends',
            'time_range_hours': hours,
            'hourly_data': dict(hourly_counts),
            'trend_summary': {
                'peak_error_hour': max(hourly_counts.items(), 
                                      key=lambda x: x[1]['errors'])[0] if hourly_counts else None,
                'total_hours_with_data': len(hourly_counts)
            }
        }
    
    def _generate_historical_summary(self, log_files: List[Path], hours: int) -> Dict[str, Any]:
        """과거 요약 생성"""
        total_stats = {
            'total_files': len(log_files),
            'total_lines': 0,
            'total_errors': 0,
            'total_warnings': 0,
            'total_info': 0
        }
        
        for log_file in log_files[:20]:  # 처음 20개 파일만
            try:
                result = self.log_tool.summarize_log(
                    str(log_file.relative_to(self.log_base_path)),
                    max_lines=100
                )
                
                if 'summary' in result:
                    summary = result['summary']
                    total_stats['total_lines'] += summary.get('total_lines', 0)
                    total_stats['total_errors'] += summary.get('error_count', 0)
                    total_stats['total_warnings'] += summary.get('warning_count', 0)
                    total_stats['total_info'] += summary.get('info_count', 0)
                    
            except Exception:
                continue
        
        return {
            'analysis_type': 'summary',
            'time_range_hours': hours,
            'statistics': total_stats,
            'health_assessment': self._assess_health(total_stats)
        }
    
    def _search_error_by_signature(self, signature: str) -> List[Dict[str, Any]]:
        """에러 시그니처로 검색"""
        matches = []
        
        error_log_dir = self.log_base_path / "error_log"
        if error_log_dir.exists():
            for log_file in error_log_dir.glob("*.log"):
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if signature.lower() in content.lower():
                            lines = content.split('\n')
                            for i, line in enumerate(lines, 1):
                                if signature.lower() in line.lower():
                                    matches.append({
                                        'file': str(log_file),
                                        'line_number': i,
                                        'content': line[:200],
                                        'timestamp': self._extract_time_from_filename(log_file.name)
                                    })
                except Exception:
                    continue
        
        return matches[:20]  # 처음 20개만 반환
    
    def _get_session_logs(self, session_id: str) -> List[Dict[str, Any]]:
        """세션 로그 조회"""
        logs = []
        
        for log_dir in self.log_base_path.glob("*_log"):
            if log_dir.is_dir():
                for log_file in log_dir.glob("*session*.log"):
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if session_id in content:
                                logs.append({
                                    'file': str(log_file),
                                    'session_mentioned': True,
                                    'preview': content[:500]
                                })
                    except Exception:
                        continue
        
        return logs
    
    def _generate_debug_suggestions(self, error_signature: str, 
                                   matching_errors: List[Dict]) -> List[str]:
        """디버깅 제안 생성"""
        suggestions = []
        
        # 빈도 기반 제안
        if len(matching_errors) > 5:
            suggestions.append(f"이 에러가 {len(matching_errors)}번 발생했습니다. 반복적인 문제로 보입니다.")
        
        # 패턴 기반 제안
        if 'connection' in error_signature.lower() or 'connect' in error_signature.lower():
            suggestions.append("네트워크 연결 문제일 수 있습니다. 연결 설정을 확인하세요.")
        
        if 'file' in error_signature.lower() or 'not found' in error_signature.lower():
            suggestions.append("파일 경로나 존재 여부를 확인하세요.")
        
        if 'permission' in error_signature.lower() or 'denied' in error_signature.lower():
            suggestions.append("권한 문제입니다. 파일/디렉토리 권한을 확인하세요.")
        
        if 'memory' in error_signature.lower():
            suggestions.append("메모리 부족 문제일 수 있습니다. 리소스 사용량을 확인하세요.")
        
        if 'timeout' in error_signature.lower():
            suggestions.append("타임아웃 문제입니다. 처리 시간이나 네트워크 지연을 확인하세요.")
        
        if not suggestions:
            suggestions.append("로그 파일을 상세히 검토하여 문제의 근본 원인을 파악하세요.")
            suggestions.append("관련된 다른 에러 로그도 함께 확인하세요.")
        
        return suggestions
    
    def _assess_health(self, stats: Dict[str, int]) -> str:
        """건강 상태 평가"""
        total_lines = stats.get('total_lines', 0)
        total_errors = stats.get('total_errors', 0)
        
        if total_lines == 0:
            return 'unknown'
        
        error_rate = (total_errors / total_lines) * 100
        
        if error_rate > 10:
            return 'critical'
        elif error_rate > 5:
            return 'warning'
        elif error_rate > 1:
            return 'caution'
        else:
            return 'healthy'
