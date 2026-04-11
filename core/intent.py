#!/usr/bin/env python3
"""
Intent Parser Module
의도 분석 - 입력 분류, 컨텍스트 추출, 목표 식별, 우선순위 할당, 다중 의도 처리
"""

import re
import json
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any, Tuple
from collections import defaultdict
from datetime import datetime


class IntentType(Enum):
    """의도 타입 열거형"""
    CODE_GENERATION = "code_generation"      # 코드 생성
    CODE_REVIEW = "code_review"              # 코드 리뷰
    DEBUGGING = "debugging"                  # 디버깅
    REFACTORING = "refactoring"              # 리팩토링
    EXPLANATION = "explanation"              # 설명 요청
    QUESTION = "question"                    # 질문
    COMMAND = "command"                      # 명령
    ANALYSIS = "analysis"                    # 분석 요청
    TESTING = "testing"                      # 테스트 요청
    DOCUMENTATION = "documentation"          # 문서화
    INTEGRATION = "integration"              # 통합/연동
    DEPLOYMENT = "deployment"                # 배포
    MAINTENANCE = "maintenance"              # 유지보수
    UNKNOWN = "unknown"                      # 알 수 없음


class Priority(Enum):
    """우선순위 열거형"""
    CRITICAL = 1      # 긴급/중요
    HIGH = 2          # 높음
    MEDIUM = 3        # 중간
    LOW = 4           # 낮음
    TRIVIAL = 5       # 사소함


@dataclass
class Intent:
    """의도 데이터 클래스"""
    intent_type: IntentType
    confidence: float                           # 신뢰도 (0.0 ~ 1.0)
    keywords: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    goal: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    sub_intents: List['Intent'] = field(default_factory=list)
    raw_input: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리 변환"""
        return {
            'intent_type': self.intent_type.value,
            'confidence': self.confidence,
            'keywords': self.keywords,
            'context': self.context,
            'goal': self.goal,
            'priority': self.priority.name,
            'sub_intents': [si.to_dict() for si in self.sub_intents],
            'raw_input': self.raw_input,
            'timestamp': self.timestamp
        }


class IntentParser:
    """의도 파서 클래스"""
    
    def __init__(self):
        # 의도별 키워드 패턴 정의
        self.intent_patterns = {
            IntentType.CODE_GENERATION: [
                r'코드.*작성|생성.*코드|만들어|구현|implement|create.*code|generate.*code',
                r'함수.*만들|클래스.*만들|모듈.*만들|작성해|코드.*줘'
            ],
            IntentType.CODE_REVIEW: [
                r'리뷰|검토|review|check.*code|코드.*확인|검사|코드.*보여',
                r'개선점|문제점|버그.*있|개선|최적화|refactor|리팩터'
            ],
            IntentType.DEBUGGING: [
                r'디버그|debug|오류|에러|error|bug|잡아|고쳐|fix|troubleshoot',
                r'안.*돼|안됨|실패|fail|exception|traceback|왜.*안'
            ],
            IntentType.REFACTORING: [
                r'리팩토링|refactor|구조.*변경|개선|정리|clean.*up|restructure',
                r'중복.*제거|최적화|optimize|성능.*개선|가독성'
            ],
            IntentType.EXPLANATION: [
                r'설명|explain|어떻게|동작|원리|무엇인|what.*is|how.*work',
                r'의미|뜻|왜|이유|이해|모르겠|궁금|알려'
            ],
            IntentType.QUESTION: [
                r'\?|질문|question|어떻게|how.*to|무엇|what|언제|when',
                r'어디|where|누가|who|왜|why|맞나|올바르|정확'
            ],
            IntentType.COMMAND: [
                r'실행|run|시작|start|중지|stop|재시작|restart|삭제|remove|생성|create',
                r'설치|install|업데이트|update|설정|configure|변경|change|수정|modify'
            ],
            IntentType.ANALYSIS: [
                r'분석|analyze|검사|inspect|측정|measure|평가|evaluate|비교|compare',
                r'통계|stat|성능|performance|품질|quality|복잡도|complexity'
            ],
            IntentType.TESTING: [
                r'테스트|test|검증|verify|단위.*테스트|unit.*test|통합.*테스트',
                r'테스트.*코드|테스트.*작성|test.*case|assert'
            ],
            IntentType.DOCUMENTATION: [
                r'문서|document|docstring|주석|comment|README|설명서|매뉴얼|manual',
                r'가이드|guide|위키|wiki|API.*문서|swagger'
            ],
            IntentType.INTEGRATION: [
                r'통합|integrate|연동|connect|연결|결합|merge|합치|import|사용',
                r'라이브러리|library|패키지|package|모듈.*사용|외부.*연동'
            ],
            IntentType.DEPLOYMENT: [
                r'배포|deploy|릴리스|release|운영|production|서버.*올|빌드|build',
                r'설치|install|배치|distribution|publish|go.*live'
            ],
            IntentType.MAINTENANCE: [
                r'유지보수|maintenance|업데이트|update|패치|patch|보안.*수정|security',
                r'모니터링|monitoring|로그.*확인|백업|backup|복구|restore'
            ]
        }
        
        # 우선순위 키워드
        self.priority_keywords = {
            Priority.CRITICAL: [
                '긴급', 'urgent', 'critical', '심각', '중대', '지금.*바로', '즉시',
                'hotfix', '장애', 'down', '중단', '안됨', '막힘', 'blocking'
            ],
            Priority.HIGH: [
                '중요', 'important', 'high', '필수', 'required', 'must', 'need.*now',
                '빨리', '빠르게', 'fast', 'asap', '곧', 'soon'
            ],
            Priority.LOW: [
                '나중', 'later', 'low', '낮음', '여유', 'when.*possible', '시간.*될',
                '천천히', 'ゆっくり', '언제.*되'
            ],
            Priority.TRIVIAL: [
                '사소', 'trivial', 'minor', '미미', '작은', 'small', '간단',
                'easy', 'trivial', ' cosmetic'
            ]
        }
        
        # 컨텍스트 키워드
        self.context_patterns = {
            'language': r'(python|java|javascript|js|typescript|ts|go|rust|java|c\+\+|c#|ruby|php)',
            'framework': r'(django|flask|fastapi|spring|react|vue|angular|express|rails|laravel)',
            'file_type': r'(\.py|\.js|\.ts|\.java|\.go|\.rs|\.cpp|\.h|\.html|\.css|\.json|\.yaml)',
            'database': r'(mysql|postgresql|postgres|sqlite|mongodb|redis|elasticsearch)',
            'tool': r'(git|docker|kubernetes|k8s|aws|gcp|azure|jenkins|github|gitlab)',
            'test_framework': r'(pytest|unittest|jest|mocha|junit|testng)'
        }
        
        self.history = []
    
    def parse(self, user_input: str, context: Optional[Dict] = None) -> Intent:
        """
        사용자 입력을 파싱하여 의도를 추출
        
        Args:
            user_input: 사용자 입력 텍스트
            context: 추가 컨텍스트 정보
            
        Returns:
            추출된 Intent 객체
        """
        if not user_input or not user_input.strip():
            return Intent(
                intent_type=IntentType.UNKNOWN,
                confidence=0.0,
                raw_input=user_input,
                context={'error': '빈 입력'}
            )
        
        # 입력 전처리
        processed_input = user_input.lower().strip()
        
        # 1. 의도 분류 (공백 제거 버전도 함께 체크)
        intent_type, confidence, keywords = self._classify_intent(processed_input)
        
        # 공백 제거한 입력에서도 체크 (연결된 한국어 처리)
        if intent_type == IntentType.UNKNOWN:
            no_space_input = processed_input.replace(' ', '')
            intent_type2, confidence2, keywords2 = self._classify_intent(no_space_input)
            if intent_type2 != IntentType.UNKNOWN:
                intent_type, confidence, keywords = intent_type2, confidence2, keywords2
        
        # 2. 컨텍스트 추출
        extracted_context = self._extract_context(processed_input)
        if context:
            extracted_context.update(context)
        
        # 3. 목표 식별
        goal = self._identify_goal(processed_input, intent_type)
        
        # 4. 우선순위 할당
        priority = self._assign_priority(processed_input)
        
        # 5. 다중 의도 처리
        sub_intents = self._detect_multiple_intents(processed_input)
        
        # Intent 생성
        intent = Intent(
            intent_type=intent_type,
            confidence=confidence,
            keywords=keywords,
            context=extracted_context,
            goal=goal,
            priority=priority,
            sub_intents=sub_intents,
            raw_input=user_input
        )
        
        # 히스토리 저장
        self.history.append(intent)
        
        return intent
    
    def _classify_intent(self, text: str) -> Tuple[IntentType, float, List[str]]:
        """
        입력 텍스트의 의도를 분류
        
        Returns:
            (의도타입, 신뢰도, 매칭된키워드)
        """
        scores = defaultdict(lambda: {'count': 0, 'keywords': []})
        
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    scores[intent_type]['count'] += len(matches)
                    scores[intent_type]['keywords'].extend(matches)
        
        if not scores:
            return IntentType.UNKNOWN, 0.0, []
        
        # 가장 높은 점수의 의도 선택
        best_intent = max(scores.items(), key=lambda x: x[1]['count'])
        intent_type = best_intent[0]
        count = best_intent[1]['count']
        keywords = list(set(best_intent[1]['keywords']))  # 중복 제거
        
        # 신뢰도 계산 (0.0 ~ 1.0)
        confidence = min(0.3 + (count * 0.15), 1.0)
        
        return intent_type, confidence, keywords
    
    def _extract_context(self, text: str) -> Dict[str, Any]:
        """
        입력에서 컨텍스트 정보 추출
        
        Returns:
            추출된 컨텍스트 딕셔너리
        """
        context = {
            'detected_languages': [],
            'detected_frameworks': [],
            'detected_files': [],
            'detected_databases': [],
            'detected_tools': [],
            'mentioned_modules': [],
            'has_code_snippet': False,
            'has_url': False,
            'has_file_path': False
        }
        
        # 언어 감지
        for match in re.finditer(self.context_patterns['language'], text, re.IGNORECASE):
            context['detected_languages'].append(match.group(0))
        
        # 프레임워크 감지
        for match in re.finditer(self.context_patterns['framework'], text, re.IGNORECASE):
            context['detected_frameworks'].append(match.group(0))
        
        # 파일 타입 감지
        for match in re.finditer(self.context_patterns['file_type'], text, re.IGNORECASE):
            context['detected_files'].append(match.group(0))
        
        # 데이터베이스 감지
        for match in re.finditer(self.context_patterns['database'], text, re.IGNORECASE):
            context['detected_databases'].append(match.group(0))
        
        # 도구 감지
        for match in re.finditer(self.context_patterns['tool'], text, re.IGNORECASE):
            context['detected_tools'].append(match.group(0))
        
        # 코드 스니펫 감지 (``` 또는 들여쓰기)
        if '```' in text or re.search(r'\n    |\n\t', text):
            context['has_code_snippet'] = True
        
        # URL 감지
        if re.search(r'https?://\S+|www\.\S+', text):
            context['has_url'] = True
        
        # 파일 경로 감지
        if re.search(r'(/[\w\-\.]+)+|\.\./|\.\\', text):
            context['has_file_path'] = True
        
        # 모듈/함수 멘션 (괄호나 점이 있는 단어)
        modules = re.findall(r'(\w+\([^)]*\)|[\w]+\.[\w]+)', text)
        context['mentioned_modules'] = modules[:5]  # 처음 5개만
        
        # 중복 제거
        context['detected_languages'] = list(set(context['detected_languages']))
        context['detected_frameworks'] = list(set(context['detected_frameworks']))
        context['detected_files'] = list(set(context['detected_files']))
        
        return context
    
    def _identify_goal(self, text: str, intent_type: IntentType) -> Optional[str]:
        """
        사용자의 목표를 식별
        
        Returns:
            식별된 목표 문자열
        """
        # 명확한 목표 문장 패턴
        goal_patterns = [
            r'(?:하고 싶은 것은|목표는|원하는 것은|원하는건|해야할 것은)\s*:?\s*([^\n.]+)',
            r'(?:결과|목적|결과물)\s*:?\s*([^\n.]+)',
            r'(?:결론적으로|최종적으로|결국)\s*:?\s*([^\n.]+)',
        ]
        
        for pattern in goal_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # 의도 타입별 기본 목표
        default_goals = {
            IntentType.CODE_GENERATION: "코드 생성 및 구현",
            IntentType.CODE_REVIEW: "코드 품질 개선",
            IntentType.DEBUGGING: "오류 해결",
            IntentType.REFACTORING: "코드 구조 개선",
            IntentType.EXPLANATION: "이해 및 학습",
            IntentType.QUESTION: "질문에 대한 답변",
            IntentType.COMMAND: "명령 실행",
            IntentType.ANALYSIS: "데이터 분석 및 통찰",
            IntentType.TESTING: "품질 보장 및 검증",
            IntentType.DOCUMENTATION: "지식 문서화",
            IntentType.INTEGRATION: "시스템 통합",
            IntentType.DEPLOYMENT: "서비스 배포",
            IntentType.MAINTENANCE: "시스템 유지보수",
            IntentType.UNKNOWN: "의도 파악 필요"
        }
        
        return default_goals.get(intent_type)
    
    def _assign_priority(self, text: str) -> Priority:
        """
        입력에서 우선순위를 할당
        
        Returns:
            할당된 Priority
        """
        # 각 우선순위별 키워드 체크
        for priority, keywords in self.priority_keywords.items():
            for keyword in keywords:
                if re.search(keyword, text, re.IGNORECASE):
                    return priority
        
        # 기본값: MEDIUM
        return Priority.MEDIUM
    
    def _detect_multiple_intents(self, text: str) -> List[Intent]:
        """
        다중 의도 감지
        
        Returns:
            감지된 하위 의도 리스트
        """
        sub_intents = []
        
        # 연결어로 분리 ("그리고", "또한", "추가로" 등)
        separators = r'(그리고|또한|추가로|그리고나서|다음에|plus|and\s+then|additionally|also|and)'
        parts = re.split(separators, text, flags=re.IGNORECASE)
        
        if len(parts) > 1:
            for part in parts:
                if part and not re.match(separators, part, re.IGNORECASE):
                    part = part.strip()
                    if len(part) > 10:  # 최소 길이 체크
                        intent_type, confidence, keywords = self._classify_intent(part)
                        if intent_type != IntentType.UNKNOWN and confidence > 0.4:
                            sub_intents.append(Intent(
                                intent_type=intent_type,
                                confidence=confidence,
                                keywords=keywords,
                                raw_input=part[:100],
                                goal=self._identify_goal(part, intent_type)
                            ))
        
        return sub_intents[:3]  # 최대 3개 하위 의도만
    
    def get_intent_statistics(self) -> Dict[str, Any]:
        """
        의도 파싱 통계 반환
        
        Returns:
            통계 정보 딕셔너리
        """
        if not self.history:
            return {'message': '아직 파싱 기록이 없습니다'}
        
        stats = defaultdict(int)
        for intent in self.history:
            stats[intent.intent_type.value] += 1
        
        return {
            'total_parsed': len(self.history),
            'intent_distribution': dict(stats),
            'average_confidence': sum(i.confidence for i in self.history) / len(self.history),
            'multi_intent_count': sum(1 for i in self.history if i.sub_intents)
        }
    
    def get_recent_intents(self, count: int = 5) -> List[Intent]:
        """
        최근 파싱된 의도 반환
        
        Args:
            count: 반환할 개수
            
        Returns:
            최근 Intent 리스트
        """
        return self.history[-count:]
    
    def clear_history(self):
        """히스토리 초기화"""
        self.history = []


def parse_intent(text: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    의도 파싱 편의 함수
    
    Args:
        text: 사용자 입력
        context: 컨텍스트 정보
        
    Returns:
        의도 분석 결과 딕셔너리
    """
    parser = IntentParser()
    intent = parser.parse(text, context)
    return intent.to_dict()
