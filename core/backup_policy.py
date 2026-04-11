"""
자동 백업 정책 관리 모듈
각 기능 완료 시 자동 git 백업 실행
"""

import subprocess
import os
from datetime import datetime
from typing import Dict, List, Optional

class BackupPolicy:
    """자동 백업 정책 관리 클래스"""
    
    def __init__(self, repo_path: str = "/home/lks/ai_router"):
        self.repo_path = repo_path
        self.auto_backup_enabled = True
        self.backup_branch = "main"
        self.commit_prefix = "Auto-backup"
        
    def is_git_repo(self) -> bool:
        """Git 저장소인지 확인"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def get_git_status(self) -> Dict[str, List[str]]:
        """Git 상태 확인"""
        try:
            # 변경된 파일 목록
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            changed_files = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    status = line[:2]
                    file_path = line[3:]
                    changed_files.append({
                        'status': status,
                        'file': file_path
                    })
            
            return {
                'has_changes': len(changed_files) > 0,
                'changed_files': changed_files
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'has_changes': False,
                'error': str(e),
                'changed_files': []
            }
    
    def create_backup_commit(self, feature_name: str, description: str = "") -> Dict[str, str]:
        """
        기능 완료 시 자동 백업 커밋 생성
        
        Args:
            feature_name: 완료된 기능 이름
            description: 추가 설명 (선택)
            
        Returns:
            성공: {'success': True, 'commit_hash': 커밋 해시}
            실패: {'success': False, 'error': 에러 메시지}
        """
        try:
            if not self.auto_backup_enabled:
                return {'success': False, 'error': '자동 백업 비활성화'}
            
            if not self.is_git_repo():
                return {'success': False, 'error': 'Git 저장소가 아님'}
            
            # 현재 시간
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 커밋 메시지 생성
            commit_message = f"{self.commit_prefix}: {feature_name} 완료 - {timestamp}"
            if description:
                commit_message += f"\n\n{description}"
            
            # 모든 변경사항 스테이징
            subprocess.run(
                ["git", "add", "."],
                cwd=self.repo_path,
                capture_output=True,
                check=True
            )
            
            # 커밋 생성
            result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            # 커밋 해시 가져오기
            hash_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            commit_hash = hash_result.stdout.strip()
            
            return {
                'success': True,
                'commit_hash': commit_hash,
                'commit_message': commit_message,
                'timestamp': timestamp
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': f'Git 커밋 실패: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'백업 실패: {str(e)}'
            }
    
    def auto_backup_feature(self, feature_name: str, description: str = "") -> bool:
        """
        기능 완료 시 자동 백업 실행
        
        Args:
            feature_name: 완료된 기능 이름
            description: 추가 설명
            
        Returns:
            성공 여부
        """
        if not self.auto_backup_enabled:
            print("자동 백업 비활성화 상태")
            return False
        
        # 변경사항 확인
        status = self.get_git_status()
        if not status['has_changes']:
            print("백업할 변경사항이 없습니다")
            return True
        
        # 백업 실행
        result = self.create_backup_commit(feature_name, description)
        
        if result['success']:
            print(f"✅ 자동 백업 완료: {feature_name}")
            print(f"   커밋: {result['commit_hash'][:8]}")
            print(f"   시간: {result['timestamp']}")
            return True
        else:
            print(f"❌ 자동 백업 실패: {result['error']}")
            return False
    
    def set_auto_backup(self, enabled: bool):
        """자동 백업 활성화/비활성화"""
        self.auto_backup_enabled = enabled
        print(f"자동 백업 {'활성화' if enabled else '비활성화'}")
    
    def get_backup_info(self) -> Dict[str, any]:
        """백업 정책 정보 반환"""
        return {
            'auto_backup_enabled': self.auto_backup_enabled,
            'repo_path': self.repo_path,
            'backup_branch': self.backup_branch,
            'commit_prefix': self.commit_prefix,
            'is_git_repo': self.is_git_repo(),
            'git_status': self.get_git_status()
        }

# 전역 백업 정책 인스턴스
backup_policy = BackupPolicy()

def get_backup_policy():
    """전역 백업 정책 인스턴스 반환"""
    return backup_policy

def auto_backup_feature(feature_name: str, description: str = "") -> bool:
    """기능 완료 시 자동 백업 실행"""
    return backup_policy.auto_backup_feature(feature_name, description)

def set_auto_backup(enabled: bool):
    """자동 백업 설정"""
    backup_policy.set_auto_backup(enabled)
