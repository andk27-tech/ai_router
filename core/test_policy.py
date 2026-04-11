"""
테스트 정책 관리 모듈
1차/2차 더미 테스트, 최종 로컬 AI 테스트 지원
"""

import os
from enum import Enum

class TestMode(Enum):
    DUMMY_1 = "dummy_1"      # 1차 더미 테스트
    DUMMY_2 = "dummy_2"      # 2차 더미 테스트  
    LOCAL_AI = "local_ai"      # 최종 로컬 AI 테스트

class TestPolicy:
    """테스트 정책 관리 클래스"""
    
    def __init__(self, mode: TestMode = TestMode.DUMMY_1):
        self.mode = mode
        self.test_count = 0
        
    def get_test_mode(self):
        """현재 테스트 모드 반환"""
        return self.mode.value
    
    def set_test_mode(self, mode: TestMode):
        """테스트 모드 설정"""
        self.mode = mode
        self.test_count = 0
        
    def should_use_dummy(self):
        """더미 테스트 사용 여부"""
        return self.mode in [TestMode.DUMMY_1, TestMode.DUMMY_2]
    
    def should_use_local_ai(self):
        """로컬 AI 사용 여부"""
        return self.mode == TestMode.LOCAL_AI
    
    def get_dummy_response(self, prompt: str, policy: str = None):
        """더미 응답 생성"""
        self.test_count += 1
        
        dummy_responses = {
            "expand": f"""AI 라우터 프로젝트의 확장성 기능은 다음과 같습니다:
1. 모듈형 아키텍처 | 각 구성요소가 독립적으로 확장 가능
2. 플러그인 시스템 | 새로운 기능을 쉽게 추가할 수 있는 구조
3. 수평적 확장 | 다중 서버 환경에서의 분산 처리
4. API 확장 | 외부 시스템과의 연동 용이성""",
            
            "expand_deep": f"""AI 라우터 프로젝트의 확장성을 상세하게 분석하면 다음과 같습니다:

1. **모듈형 아키텍처 설계**: 
   - 각 구성요소(에이전트, 평가자, 러너)가 독립적으로 동작
   - 인터페이스 기반 설계로 새로운 모듈 추가 용이
   - 의존성 최소화로 유지보수성 향상

2. **플러그인 시스템 구현**:
   - 동적 플러그인 로딩 지원
   - 핫 스왑 기능으로 런타임 중 확장 가능
   - 표준화된 플러그인 API 제공""",
            
            "balance": f"""AI 라우터 프로젝트는 다양한 측면의 균형을 고려합니다:
1. 성능과 안정성의 균형
2. 확장성과 단순성의 조화  
3. 자동화와 제어의 균형
4. 모든 구성 요소의 균형 있는 발전""",
            
            "refine": f"""AI 라우터 프로젝트의 핵심 기능을 정리하면 다음과 같습니다:
1. 체계적인 에이전트 관리
2. 정제된 평가 시스템
3. 구조화된 학습 메커니즘
4. 명확한 정책 진화 과정"""
        }
        
        # 1차와 2차 더미의 차이점
        if self.mode == TestMode.DUMMY_1:
            return dummy_responses.get(policy, f"더미 응답 1차 - {policy} 정책")
        else:  # DUMMY_2
            return dummy_responses.get(policy, f"더미 응답 2차 - {policy} 정책 (개선됨)")
    
    def get_test_info(self):
        """테스트 정보 반환"""
        return {
            "mode": self.mode.value,
            "test_count": self.test_count,
            "is_dummy": self.should_use_dummy(),
            "is_local_ai": self.should_use_local_ai()
        }

# 전역 테스트 정책 인스턴스
test_policy = TestPolicy()

def get_test_policy():
    """전역 테스트 정책 인스턴스 반환"""
    return test_policy

def set_test_mode(mode: TestMode):
    """테스트 모드 설정"""
    test_policy.set_test_mode(mode)

def get_current_mode():
    """현재 테스트 모드 반환"""
    return test_policy.get_test_mode()
