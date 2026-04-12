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
    
    def __init__(self, mode: TestMode = None):
        # 환경 변수에서 모드 읽기 (모듈 간 공유용)
        import os
        env_mode = os.environ.get('AI_ROUTER_TEST_MODE', 'dummy_1')
        if mode is None:
            mode = TestMode(env_mode)
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
        """더미 응답 생성 - 정책별 특성 강화"""
        self.test_count += 1
        
        # 프롬프트 분석으로 동적 응답 생성
        prompt_lower = prompt.lower()
        
        dummy_responses = {
            "expand": self._generate_expand_response(prompt_lower),
            "expand_deep": self._generate_expand_deep_response(prompt_lower),
            "balance": self._generate_balance_response(prompt_lower),
            "refine": self._generate_refine_response(prompt_lower)
        }
        
        # 1차와 2차 더미의 차이점
        if self.mode == TestMode.DUMMY_1:
            return dummy_responses.get(policy, f"더미 응답 1차 - {policy} 정책")
        else:  # DUMMY_2
            return dummy_responses.get(policy, f"더미 응답 2차 - {policy} 정책 (개선됨)")
    
    def _generate_expand_response(self, prompt_lower: str) -> str:
        """expand 정책용 확장성 응답 생성"""
        base_responses = [
            """AI 라우터 프로젝트의 확장성 기능은 다음과 같습니다:

🏗️ **아키텍처 확장성**
• 모듈형 설계: 각 컴포넌트 독립적 확장
• 플러그인 시스템: 새로운 기능 동적 추가
• 마이크로서비스: 수평적 확장 지원

📊 **데이터 확장성**
• 대용량 메모리: 200개 항목 학습 저장
• 분산 처리: 다중 서버 환경
• 실시간 학습: 지속적 정책 진화

🔌 **API 확장성**
• RESTful API: 외부 시스템 연동 용이
• 웹훅 지원: 실시간 이벤트 처리
• SDK 제공: 다양한 언어 지원

🧠 **지능 확장성**
• 다중 에이전트: 경쟁적 학습 시스템
• 정책 진화: 자가 수정 및 개선
• 평가 최적화: 정확도 향상 메커니즘""",
            
            """AI 라우터의 확장성은 다음 차원에서 구현됩니다:

**기술적 확장성**
- 컨테이너화된 배포: Docker/Kubernetes 지원
- 클라우드 네이티브: AWS/Azure/GCP 호환
- 오픈소스 생태계: 커뮤니티 기반 발전

**기능적 확장성**
- 멀티모달 처리: 텍스트/이미지/오디오
- 다국어 지원: 50+ 언어 처리
- 도메인 특화: 의료/금융/교육 등

**성능 확장성**
- 병렬 처리: GPU 가속 지원
- 캐싱 최적화: 응답 속도 10배 향상
- 로드 밸런싱: 트래픽 분산 처리

**생태계 확장성**
- 파트너 통합: third-party API 연동
- 마켓플레이스: 에이전트/정책 거래
- 개발자 포털: SDK/문서/툴 제공"""
        ]
        
        # 프롬프트에 따라 적절한 응답 선택
        if '기능' in prompt_lower or '핵심' in prompt_lower:
            return base_responses[0]
        elif '시스템' in prompt_lower or '아키텍처' in prompt_lower:
            return base_responses[1]
        else:
            return base_responses[0]
    
    def _generate_expand_deep_response(self, prompt_lower: str) -> str:
        """expand_deep 정책용 심층 분석 응답 생성"""
        return """AI 라우터 프로젝트의 확장성을 심층적으로 분석하면 다음과 같습니다:

## 🏗️ **아키텍처 확장성 상세 분석**

### **모듈형 설계의 핵심 원리**
- **느슨한 결합**: 각 컴포넌트가 독립적으로 동작하며 변경이 다른 모듈에 영향을 최소화
- **인터페이스 기반**: 표준화된 API를 통해 모듈 간 통신, 새로운 모듈 추가 용이
- **의존성 주입**: 런타임에 컴포넌트 교체 가능, 유연성 극대화

### **플러그인 아키텍처 구현**
- **동적 로딩**: 런타임 중 새로운 플러그인 추가, 시스템 중단 없음
- **핫 스왑**: 운영 중인 플러그인 교체, 가용성 99.9% 보장
- **버전 관리**: 플러그인 간 의존성 충돌 방지, 안정적인 업그레이드

## 📊 **데이터 처리 확장성**

### **분산 아키텍처**
- **샤딩**: 데이터를 여러 노드에 분산 저장, 수평적 확장 지원
- **복제**: 데이터 중복 저장으로 고가용성 및 장애 복구
- **로드 밸런싱**: 요청 분산 처리, 응답 시간 최적화

### **메모리 관리**
- **LRU 캐시**: 최근 사용 데이터 우선 저장, 효율적인 메모리 활용
- **가비지 컬렉션**: 불필요 데이터 자동 정리, 메모리 누수 방지
- **페이징**: 대용량 데이터의 효율적인 메모리 매핑

## 🔌 **API 생태계 확장**

### **게이트웨이 패턴**
- **API 게이트웨이**: 단일 진입점, 인증/로깅/모니터링 중앙화
- **서비스 메시**: 마이크로서비스 간 통신 관리, 관찰 가능성 향상
- **이벤트 버스**: 비동기 통신, 시스템 결합도 감소

이러한 심층적인 확장성 설계를 통해 AI 라우터는 엔터프라이즈급 요구사항을 충족합니다."""
    
    def _generate_balance_response(self, prompt_lower: str) -> str:
        """balance 정책용 균형성 응답 생성"""
        return """AI 라우터 프로젝트는 다음과 같은 균형을 추구합니다:

⚖️ **성능 vs 안정성**
- 빠른 응답 속도와 안정적인 시스템 운영
- 효율적인 자원 사용과 신뢰성 있는 결과
- 실시간 처리와 내결함성 있는 아키텍처

🔄 **확장성 vs 단순성**
- 모듈형 아키텍처로 확장성 확보
- 직관적인 인터페이스로 단순성 유지
- 복잡한 기능을 쉽게 사용할 수 있도록 설계

🎯 **자동화 vs 제어**
- 스마트한 자동 라우팅 시스템
- 사용자 제어 가능한 정책 설정
- 적응형 학습과 명시적 규칙의 조화

🌐 **다양성 vs 통일성**
- 여러 에이전트의 다양한 관점
- 일관된 평가 기준과 결과 형식
- 유연한 정책과 표준화된 프로토콜

🚀 **혁신 vs 안정**
- 실험적 기능의 안전한 테스트
- 검증된 기술의 안정적 운영
- 점진적 개선과 안정적인 배포

이러한 균형을 통해 프로젝트는 지속 가능한 발전을 이룹니다."""
    
    def _generate_refine_response(self, prompt_lower: str) -> str:
        """refine 정책용 정제성 응답 생성"""
        return """AI 라우터 프로젝트의 핵심 기능을 정리하면 다음과 같습니다:

🎯 **핵심 아키텍처**
• 모듈형 설계: 각 컴포넌트 독립 운영
• 정책 기반 라우팅: 최적 에이전트 선택
• 평가 시스템: 1-10점 척도로 품질 측정

📋 **주요 구성요소**
1. **에이전트**: refine/balance/expand 정책 실행
   - 경쟁적 학습 메커니즘
   - 정책별 특화된 응답 생성
   
2. **평가자**: 정책별 품질 평가
   - 다차원적 평가 기준
   - 동적 가중치 조정
   
3. **러너**: 전체 프로세스 오케스트레이션
   - 재시도 로직 및 보상 계산
   - 메모리 저장 연동
   
4. **메모리**: 학습 결과 저장 및 활용
   - 200개 항목까지 저장
   - 성공 사례 우선 조회

✨ **특징**
- 체계적인 구조
- 명확한 역할 분담
- 지속적인 학습 메커니즘
- 자가 수정 및 진화 능력

🔄 **동작 방식**
1. 사용자 입력 수신
2. 다중 에이전트 경쟁 실행
3. 평가자 품질 측정
4. 승자 선택 및 결과 반환
5. 학습 데이터 저장"""
    
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
    import os
    os.environ['AI_ROUTER_TEST_MODE'] = mode.value
    test_policy.set_test_mode(mode)

def get_current_mode():
    """현재 테스트 모드 반환"""
    return test_policy.get_test_mode()
