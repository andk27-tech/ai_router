"""
로그 분석 툴
AI 에이전트가 로그 파일을 효과적으로 분석하고 모니터링할 수 있는 기능 제공
"""

import os
import re
import json
import glob
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple
from collections import defaultdict, Counter

class LogTool:
    """로그 분석 및 모니터링을 위한 툴 클래스"""
    
    def __init__(self, log_base_path: str = "/home/lks/ai_router/log"):
        self.log_base_path = Path(log_base_path).resolve()
        self.supported_formats = ['.log', '.txt', '.out', '.err']
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.encoding = 'utf-8'
        
        # 일반적인 로그 패턴
        self.error_patterns = [
            r'error|exception|traceback|failed|failure',
            r'critical|fatal|panic',
            r'timeout|connection.*refused|permission denied'
        ]
        
        self.warning_patterns = [
            r'warning|warn|deprecated',
            r'retry|attempt.*failed|fallback'
        ]
        
        self.info_patterns = [
            r'info|started|completed|success',
            r'initialized|ready|listening'
        ]
    
    def _is_safe_log_path(self, log_path: str) -> bool:
        """로그 파일 경로 안전성 검증"""
        try:
            resolved_path = Path(log_path).resolve()
            
            # 로그 기본 경로 내에 있는지 확인
            if not str(resolved_path).startswith(str(self.log_base_path)):
                return False
                
            return True
        except Exception:
            return False
    
    def parse_log_file(self, log_file_path: str, 
                     max_lines: int = 10000) -> Dict[str, Union[List, str]]:
        """
        로그 파일 파싱
        
        Args:
            log_file_path: 파싱할 로그 파일 경로
            max_lines: 최대 읽을 라인 수
            
        Returns:
            성공: {'lines': 라인 리스트, 'total_lines': 전체 라인 수, 'file_info': 파일 정보}
            실패: {'error': 에러 메시지}
        """
        try:
            full_path = self.log_base_path / log_file_path
            
            # 안전성 검증
            if not self._is_safe_log_path(str(full_path)):
                return {'error': f'안전하지 않은 로그 경로: {log_file_path}'}
            
            if not full_path.exists():
                return {'error': f'로그 파일을 찾을 수 없음: {log_file_path}'}
            
            if not full_path.is_file():
                return {'error': f'로그 파일이 아님: {log_file_path}'}
            
            # 파일 크기 확인
            file_size = full_path.stat().st_size
            if file_size > self.max_file_size:
                return {'error': f'로그 파일 크기 초과: {file_size} > {self.max_file_size}'}
            
            # 로그 파일 읽기
            lines = []
            with open(full_path, 'r', encoding=self.encoding, errors='ignore') as f:
                for i, line in enumerate(f):
                    if i >= max_lines:
                        break
                    lines.append(line.strip())
            
            # 파일 정보
            file_info = {
                'name': full_path.name,
                'path': str(full_path.relative_to(self.log_base_path)),
                'size': file_size,
                'modified': datetime.fromtimestamp(full_path.stat().st_mtime).isoformat(),
                'lines_read': len(lines)
            }
            
            return {
                'lines': lines,
                'total_lines': len(lines),
                'file_info': file_info
            }
            
        except Exception as e:
            return {'error': f'로그 파일 파싱 오류: {str(e)}'}
    
    def match_patterns(self, log_lines: List[str], 
                    patterns: List[str]) -> List[Dict[str, Union[str, int]]]:
        """
        로그 라인에서 패턴 매칭
        
        Args:
            log_lines: 로그 라인 리스트
            patterns: 정규식 패턴 리스트
            
        Returns:
            매칭된 라인 정보 리스트
        """
        matches = []
        
        for line_num, line in enumerate(log_lines, 1):
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    matches.append({
                        'line_number': line_num,
                        'line_content': line,
                        'pattern': pattern,
                        'matched_text': re.search(pattern, line, re.IGNORECASE).group()
                    })
        
        return matches
    
    def extract_errors(self, log_file_path: str, 
                    max_lines: int = 10000) -> Dict[str, Union[List, Dict]]:
        """
        로그에서 오류 추출
        
        Args:
            log_file_path: 로그 파일 경로
            max_lines: 최대 읽을 라인 수
            
        Returns:
            성공: {'errors': 오류 리스트, 'error_count': 오류 수, 'file_info': 파일 정보}
            실패: {'error': 에러 메시지}
        """
        # 로그 파일 파싱
        parse_result = self.parse_log_file(log_file_path, max_lines)
        if 'error' in parse_result:
            return parse_result
        
        lines = parse_result['lines']
        
        # 오류 패턴 매칭
        error_matches = self.match_patterns(lines, self.error_patterns)
        
        # 오류 유형 분류
        error_types = defaultdict(list)
        for match in error_matches:
            error_type = self._classify_error(match['matched_text'])
            error_types[error_type].append(match)
        
        return {
            'errors': error_matches,
            'error_count': len(error_matches),
            'error_types': dict(error_types),
            'file_info': parse_result['file_info']
        }
    
    def _classify_error(self, error_text: str) -> str:
        """오류 유형 분류"""
        error_text = error_text.lower()
        
        if any(keyword in error_text for keyword in ['traceback', 'exception']):
            return 'exception'
        elif any(keyword in error_text for keyword in ['failed', 'failure']):
            return 'failure'
        elif any(keyword in error_text for keyword in ['timeout', 'time out']):
            return 'timeout'
        elif any(keyword in error_text for keyword in ['connection', 'refused']):
            return 'connection'
        elif any(keyword in error_text for keyword in ['permission', 'denied']):
            return 'permission'
        elif any(keyword in error_text for keyword in ['critical', 'fatal']):
            return 'critical'
        else:
            return 'other'
    
    def summarize_log(self, log_file_path: str, 
                   max_lines: int = 10000) -> Dict[str, Union[Dict, str]]:
        """
        로그 요약 생성
        
        Args:
            log_file_path: 로그 파일 경로
            max_lines: 최대 읽을 라인 수
            
        Returns:
            성공: {'summary': 요약 정보, 'file_info': 파일 정보}
            실패: {'error': 에러 메시지}
        """
        # 로그 파일 파싱
        parse_result = self.parse_log_file(log_file_path, max_lines)
        if 'error' in parse_result:
            return parse_result
        
        lines = parse_result['lines']
        
        # 로그 레벨별 카운트
        error_matches = self.match_patterns(lines, self.error_patterns)
        warning_matches = self.match_patterns(lines, self.warning_patterns)
        info_matches = self.match_patterns(lines, self.info_patterns)
        
        # 시간대별 로그 분석 (타임스탬프가 있는 경우)
        timeline = self._analyze_timeline(lines)
        
        # 가장 빈번한 메시지
        message_frequency = Counter([line for line in lines if line.strip()])
        
        summary = {
            'total_lines': len(lines),
            'error_count': len(error_matches),
            'warning_count': len(warning_matches),
            'info_count': len(info_matches),
            'error_types': self._count_error_types(error_matches),
            'timeline': timeline,
            'top_messages': message_frequency.most_common(10),
            'log_health': self._assess_log_health(len(lines), len(error_matches))
        }
        
        return {
            'summary': summary,
            'file_info': parse_result['file_info']
        }
    
    def _count_error_types(self, error_matches: List[Dict]) -> Dict[str, int]:
        """오류 유형별 카운트"""
        error_types = Counter()
        for match in error_matches:
            error_type = self._classify_error(match['matched_text'])
            error_types[error_type] += 1
        return dict(error_types)
    
    def _analyze_timeline(self, lines: List[str]) -> List[Dict]:
        """시간대별 로그 분석"""
        timeline = []
        
        # 간단한 타임스탬프 패턴 (다양한 형식 지원)
        timestamp_patterns = [
            r'(\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2})',  # ISO 형식
            r'(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})',  # US 형식
            r'(\d{2}:\d{2}:\d{2})',  # 시간만
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in timestamp_patterns:
                match = re.search(pattern, line)
                if match:
                    timestamp_str = match.group(1)
                    try:
                        # 타임스탬프 파싱
                        if '-' in timestamp_str and ':' in timestamp_str:
                            dt = datetime.fromisoformat(timestamp_str.replace(' ', 'T'))
                        elif '/' in timestamp_str:
                            dt = datetime.strptime(timestamp_str, '%m/%d/%Y %H:%M:%S')
                        else:
                            dt = datetime.strptime(timestamp_str, '%H:%M:%S')
                        
                        timeline.append({
                            'line_number': line_num,
                            'timestamp': dt.isoformat(),
                            'message': line
                        })
                        break
                    except ValueError:
                        continue
        
        return timeline
    
    def _assess_log_health(self, total_lines: int, error_count: int) -> str:
        """로그 상태 평가"""
        if total_lines == 0:
            return 'empty'
        
        error_rate = (error_count / total_lines) * 100
        
        if error_rate > 10:
            return 'critical'
        elif error_rate > 5:
            return 'warning'
        elif error_rate > 1:
            return 'info'
        else:
            return 'good'
    
    def monitor_real_time(self, log_file_path: str, 
                        callback=None) -> Dict[str, Union[str, bool]]:
        """
        실시간 로그 모니터링 설정
        
        Args:
            log_file_path: 모니터링할 로그 파일 경로
            callback: 새 로그 라인 발생 시 호출할 콜백 함수
            
        Returns:
            성공: {'monitoring': True, 'file_path': 모니터링 파일 경로}
            실패: {'error': 에러 메시지}
        """
        try:
            full_path = self.log_base_path / log_file_path
            
            # 안전성 검증
            if not self._is_safe_log_path(str(full_path)):
                return {'error': f'안전하지 않은 로그 경로: {log_file_path}'}
            
            # 실시간 모니터링 설정 정보
            monitor_info = {
                'monitoring': True,
                'file_path': str(full_path.relative_to(self.log_base_path)),
                'callback': callback,
                'start_time': datetime.now().isoformat()
            }
            
            return monitor_info
            
        except Exception as e:
            return {'error': f'실시간 모니터링 설정 오류: {str(e)}'}
    
    def get_log_files(self, pattern: str = "*") -> Dict[str, Union[List, str]]:
        """
        사용 가능한 로그 파일 목록 조회
        
        Args:
            pattern: 파일 패턴 (기본: "*")
            
        Returns:
            성공: {'files': 파일 정보 리스트}
            실패: {'error': 에러 메시지}
        """
        try:
            files = []
            
            # 패턴으로 파일 검색
            search_pattern = f"{pattern}.log"
            for file_path in self.log_base_path.rglob(search_pattern):
                if file_path.is_file():
                    stat = file_path.stat()
                    files.append({
                        'name': file_path.name,
                        'path': str(file_path.relative_to(self.log_base_path)),
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
            
            return {'files': sorted(files, key=lambda x: x['modified'], reverse=True)}
            
        except Exception as e:
            return {'error': f'로그 파일 목록 조회 오류: {str(e)}'}
    
    def get_tool_info(self) -> Dict[str, Union[str, List]]:
        """툴 정보 반환"""
        return {
            'name': 'LogTool',
            'version': '1.0.0',
            'description': '로그 분석 및 모니터링을 위한 툴',
            'base_path': str(self.log_base_path),
            'supported_formats': self.supported_formats,
            'max_file_size': self.max_file_size,
            'features': [
                'parse_log_file',
                'match_patterns',
                'extract_errors',
                'summarize_log',
                'monitor_real_time',
                'get_log_files'
            ]
        }

# 전역 로그 툴 인스턴스
log_tool = LogTool()

def get_log_tool():
    """전역 로그 툴 인스턴스 반환"""
    return log_tool
