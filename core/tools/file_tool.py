"""
파일 작업 툴
AI 에이전트가 파일 시스템을 안전하게 조작할 수 있는 기능 제공
"""

import os
import json
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

class FileTool:
    """안전한 파일 작업을 위한 툴 클래스"""
    
    def __init__(self, base_path: str = "/home/lks/ai_router"):
        self.base_path = Path(base_path).resolve()
        self.allowed_extensions = {
            '.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.yaml', '.yml',
            '.log', '.csv', '.xml', '.ini', '.cfg', '.conf', '.env'
        }
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.restricted_dirs = {
            '__pycache__', '.git', 'venv', '.venv', 'node_modules',
            '.pytest_cache', '.mypy_cache', 'site-packages'
        }
        
    def _is_safe_path(self, path: str) -> bool:
        """경로 안전성 검증"""
        try:
            resolved_path = Path(path).resolve()
            
            # 기본 경로 내에 있는지 확인
            if not str(resolved_path).startswith(str(self.base_path)):
                return False
                
            # 제한된 디렉토리 확인
            for restricted in self.restricted_dirs:
                if restricted in resolved_path.parts:
                    return False
                    
            return True
        except Exception:
            return False
    
    def _is_allowed_file(self, file_path: str) -> bool:
        """허용된 파일 확장자 확인"""
        ext = Path(file_path).suffix.lower()
        return ext in self.allowed_extensions
    
    def read_file(self, file_path: str, encoding: str = 'utf-8') -> Dict[str, Union[str, int]]:
        """
        파일 읽기
        
        Args:
            file_path: 읽을 파일 경로
            encoding: 파일 인코딩 (기본: utf-8)
            
        Returns:
            성공: {'content': 파일 내용, 'size': 파일 크기, 'encoding': 사용된 인코딩}
            실패: {'error': 에러 메시지}
        """
        try:
            full_path = self.base_path / file_path
            
            # 안전성 검증
            if not self._is_safe_path(str(full_path)):
                return {'error': f'안전하지 않은 경로: {file_path}'}
            
            if not full_path.exists():
                return {'error': f'파일을 찾을 수 없음: {file_path}'}
            
            if not self._is_allowed_file(str(full_path)):
                return {'error': f'허용되지 않은 파일 형식: {file_path}'}
            
            # 파일 크기 확인
            file_size = full_path.stat().st_size
            if file_size > self.max_file_size:
                return {'error': f'파일 크기 초과: {file_size} > {self.max_file_size}'}
            
            # 파일 읽기
            with open(full_path, 'r', encoding=encoding) as f:
                content = f.read()
                
            return {
                'content': content,
                'size': file_size,
                'encoding': encoding,
                'path': str(full_path.relative_to(self.base_path))
            }
            
        except UnicodeDecodeError:
            return {'error': f'파일 인코딩 오류: {file_path}'}
        except Exception as e:
            return {'error': f'파일 읽기 오류: {str(e)}'}
    
    def write_file(self, file_path: str, content: str, encoding: str = 'utf-8', 
                 create_dirs: bool = True) -> Dict[str, Union[str, bool]]:
        """
        파일 쓰기
        
        Args:
            file_path: 쓸 파일 경로
            content: 파일 내용
            encoding: 파일 인코딩 (기본: utf-8)
            create_dirs: 디렉토리 자동 생성 (기본: True)
            
        Returns:
            성공: {'success': True, 'path': 생성된 파일 경로, 'size': 파일 크기}
            실패: {'error': 에러 메시지}
        """
        try:
            full_path = self.base_path / file_path
            
            # 안전성 검증
            if not self._is_safe_path(str(full_path)):
                return {'error': f'안전하지 않은 경로: {file_path}'}
            
            if not self._is_allowed_file(str(full_path)):
                return {'error': f'허용되지 않은 파일 형식: {file_path}'}
            
            # 디렉토리 생성
            if create_dirs:
                full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 파일 쓰기
            with open(full_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            file_size = full_path.stat().st_size
            
            return {
                'success': True,
                'path': str(full_path.relative_to(self.base_path)),
                'size': file_size,
                'encoding': encoding
            }
            
        except Exception as e:
            return {'error': f'파일 쓰기 오류: {str(e)}'}
    
    def list_directory(self, dir_path: str = ".", show_hidden: bool = False, 
                    recursive: bool = False) -> Dict[str, Union[List[Dict], str]]:
        """
        디렉토리 목록 조회
        
        Args:
            dir_path: 조회할 디렉토리 경로 (기본: 현재 디렉토리)
            show_hidden: 숨김 파일 표시 (기본: False)
            recursive: 재귀적 조회 (기본: False)
            
        Returns:
            성공: {'files': 파일/디렉토리 정보 리스트}
            실패: {'error': 에러 메시지}
        """
        try:
            full_path = self.base_path / dir_path
            
            # 안전성 검증
            if not self._is_safe_path(str(full_path)):
                return {'error': f'안전하지 않은 경로: {dir_path}'}
            
            if not full_path.exists():
                return {'error': f'디렉토리를 찾을 수 없음: {dir_path}'}
            
            if not full_path.is_dir():
                return {'error': f'디렉토리가 아님: {dir_path}'}
            
            items = []
            
            if recursive:
                pattern = "**/*"
            else:
                pattern = "*"
            
            for item in full_path.glob(pattern):
                try:
                    # 숨김 파일 필터
                    if not show_hidden and item.name.startswith('.'):
                        continue
                    
                    # 제한된 디렉토리 필터
                    if item.is_dir() and item.name in self.restricted_dirs:
                        continue
                    
                    stat = item.stat()
                    item_info = {
                        'name': item.name,
                        'path': str(item.relative_to(self.base_path)),
                        'type': 'directory' if item.is_dir() else 'file',
                        'size': stat.st_size if item.is_file() else 0,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'extension': item.suffix.lower() if item.is_file() else None
                    }
                    
                    # MIME 타입 추가 (파일인 경우)
                    if item.is_file():
                        item_info['mime_type'] = mimetypes.guess_type(str(item))[0]
                    
                    items.append(item_info)
                    
                except (OSError, PermissionError):
                    # 접근 권한이 없는 파일/디렉토리 건너뛰기
                    continue
            
            return {'files': sorted(items, key=lambda x: (x['type'], x['name']))}
            
        except Exception as e:
            return {'error': f'디렉토리 조회 오류: {str(e)}'}
    
    def get_file_metadata(self, file_path: str) -> Dict[str, Union[Dict, str]]:
        """
        파일 메타데이터 추출
        
        Args:
            file_path: 메타데이터를 추출할 파일 경로
            
        Returns:
            성공: {'metadata': 메타데이터 정보}
            실패: {'error': 에러 메시지}
        """
        try:
            full_path = self.base_path / file_path
            
            # 안전성 검증
            if not self._is_safe_path(str(full_path)):
                return {'error': f'안전하지 않은 경로: {file_path}'}
            
            if not full_path.exists():
                return {'error': f'파일을 찾을 수 없음: {file_path}'}
            
            stat = full_path.stat()
            
            metadata = {
                'name': full_path.name,
                'path': str(full_path.relative_to(self.base_path)),
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'accessed': datetime.fromtimestamp(stat.st_atime).isoformat(),
                'extension': full_path.suffix.lower(),
                'mime_type': mimetypes.guess_type(str(full_path))[0] if full_path.is_file() else None,
                'is_readable': os.access(full_path, os.R_OK),
                'is_writable': os.access(full_path, os.W_OK),
                'is_executable': os.access(full_path, os.X_OK)
            }
            
            return {'metadata': metadata}
            
        except Exception as e:
            return {'error': f'메타데이터 추출 오류: {str(e)}'}
    
    def validate_path(self, path: str) -> Dict[str, Union[bool, str]]:
        """
        경로 유효성 검증
        
        Args:
            path: 검증할 경로
            
        Returns:
            {'valid': 유효성, 'path': 정규화된 경로, 'message': 설명}
        """
        try:
            full_path = self.base_path / path
            
            # 안전성 검증
            if not self._is_safe_path(str(full_path)):
                return {
                    'valid': False,
                    'path': str(full_path),
                    'message': '안전하지 않은 경로입니다'
                }
            
            # 존재 여부 확인
            exists = full_path.exists()
            
            return {
                'valid': True,
                'path': str(full_path.relative_to(self.base_path)),
                'exists': exists,
                'type': 'directory' if full_path.is_dir() else 'file' if full_path.is_file() else 'unknown',
                'message': '유효한 경로입니다'
            }
            
        except Exception as e:
            return {
                'valid': False,
                'path': path,
                'message': f'경로 검증 오류: {str(e)}'
            }
    
    def get_tool_info(self) -> Dict[str, Union[str, List]]:
        """툴 정보 반환"""
        return {
            'name': 'FileTool',
            'version': '1.0.0',
            'description': '안전한 파일 작업을 위한 툴',
            'base_path': str(self.base_path),
            'allowed_extensions': list(self.allowed_extensions),
            'max_file_size': self.max_file_size,
            'restricted_dirs': list(self.restricted_dirs),
            'features': [
                'read_file',
                'write_file', 
                'list_directory',
                'get_file_metadata',
                'validate_path'
            ]
        }

# 전역 파일 툴 인스턴스
file_tool = FileTool()

def get_file_tool():
    """전역 파일 툴 인스턴스 반환"""
    return file_tool
