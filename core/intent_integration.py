#!/usr/bin/env python3
"""
Intent Integration Module
의도 통합 - 라우터 의도 인식, 의도 기반 정책 선택, 컨텍스트 보존
"""

import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict, deque

from .intent import IntentParser, IntentType, Priority, Intent


@dataclass
class RoutingDecision:
    """라우팅 결정 데이터 클래스"""
    selected_policy: str
    confidence: float
    reasoning: str
    context_preservation: Dict[str, Any]
    fallback_policies: List[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class IntentBasedRouter:
    """의도 기반 라우터 클래스"""
    
    def __init__(self):
        self.intent_parser = IntentParser()
        
        # 의도 타입별 정책 매핑
        self.intent_policy_map = {
            IntentType.CODE_GENERATION: {
                'primary': 'expand',
                'fallback': ['expand_deep', 'balance'],
                'reason': '코드 생성은 확장 정책이 적합'
            },
            IntentType.CODE_REVIEW: {
                'primary': 'refine',
                'fallback': ['balance', 'expand'],
                'reason': '코드 리뷰는 정제 정책이 적합'
            },
            IntentType.DEBUGGING: {
                'primary': 'refine',
                'fallback': ['balance', 'expand_deep'],
                'reason': '디버깅은 정제 및 분석 정책이 적합'
            },
            IntentType.REFACTORING: {
                'primary': 'refine',
                'fallback': ['balance', 'expand'],
                'reason': '리팩토링은 정제 정책이 적합'
            },
            IntentType.EXPLANATION: {
                'primary': 'expand',
                'fallback': ['balance', 'expand_deep'],
                'reason': '설명은 확장 정책이 적합'
            },
            IntentType.QUESTION: {
                'primary': 'expand',
                'fallback': ['balance', 'expand_deep'],
                'reason': '질문 답변은 확장 정책이 적합'
            },
            IntentType.COMMAND: {
                'primary': 'balance',
                'fallback': ['refine', 'expand'],
                'reason': '명령 실행은 균형 정책이 적합'
            },
            IntentType.ANALYSIS: {
                'primary': 'expand_deep',
                'fallback': ['expand', 'balance'],
                'reason': '분석은 심층 확장 정책이 적합'
            },
            IntentType.TESTING: {
                'primary': 'balance',
                'fallback': ['refine', 'expand'],
                'reason': '테스트는 균형 및 검증 정책이 적합'
            },
            IntentType.DOCUMENTATION: {
                'primary': 'expand',
                'fallback': ['balance', 'refine'],
                'reason': '문서화는 확장 정책이 적합'
            },
            IntentType.INTEGRATION: {
                'primary': 'balance',
                'fallback': ['expand', 'refine'],
                'reason': '통합은 균형 정책이 적합'
            },
            IntentType.DEPLOYMENT: {
                'primary': 'balance',
                'fallback': ['refine', 'expand'],
                'reason': '배포는 균형 정책이 적합'
            },
            IntentType.MAINTENANCE: {
                'primary': 'refine',
                'fallback': ['balance', 'expand'],
                'reason': '유지보수는 정제 정책이 적합'
            },
            IntentType.UNKNOWN: {
                'primary': 'balance',
                'fallback': ['expand', 'refine'],
                'reason': '알 수 없는 의도는 기본 균형 정책'
            }
        }
        
        # 우선순위별 정책 조정
        self.priority_policy_boost = {
            Priority.CRITICAL: {'boost': 0.3, 'require_fast_policy': True},
            Priority.HIGH: {'boost': 0.2, 'require_fast_policy': False},
            Priority.MEDIUM: {'boost': 0.0, 'require_fast_policy': False},
            Priority.LOW: {'boost': -0.1, 'require_fast_policy': False},
            Priority.TRIVIAL: {'boost': -0.2, 'require_fast_policy': False}
        }
        
        # 라우팅 히스토리
        self.routing_history = deque(maxlen=100)
    
    def recognize_intent_and_route(self, user_input: str, 
                                   context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        사용자 입력의 의도를 인식하고 라우팅 결정
        
        Args:
            user_input: 사용자 입력 텍스트
            context: 추가 컨텍스트
            
        Returns:
            라우팅 결과 딕셔너리
        """
        # 1. 의도 파싱
        intent = self.intent_parser.parse(user_input, context)
        
        # 2. 정책 선택
        routing_decision = self._select_policy(intent)
        
        # 3. 컨텍스트 보존
        preserved_context = self._preserve_context(intent, routing_decision)
        
        # 4. 결과 조합
        result = {
            'intent': intent.to_dict(),
            'routing': {
                'selected_policy': routing_decision.selected_policy,
                'confidence': routing_decision.confidence,
                'reasoning': routing_decision.reasoning,
                'fallback_policies': routing_decision.fallback_policies
            },
            'context': preserved_context,
            'timestamp': datetime.now().isoformat()
        }
        
        # 히스토리 저장
        self.routing_history.append({
            'input': user_input[:100],
            'intent_type': intent.intent_type.value,
            'policy': routing_decision.selected_policy,
            'timestamp': result['timestamp']
        })
        
        return result
    
    def _select_policy(self, intent: Intent) -> RoutingDecision:
        """
        의도에 기반하여 정책 선택
        
        Args:
            intent: 파싱된 의도
            
        Returns:
            라우팅 결정
        """
        # 의도 타입별 기본 정책 매핑
        policy_config = self.intent_policy_map.get(
            intent.intent_type,
            self.intent_policy_map[IntentType.UNKNOWN]
        )
        
        primary_policy = policy_config['primary']
        fallback_policies = policy_config['fallback']
        reasoning = policy_config['reason']
        
        # 우선순위에 따른 조정
        priority_boost = self.priority_policy_boost.get(intent.priority, {'boost': 0.0})
        
        # 긴급 상황 처리
        if priority_boost.get('require_fast_policy') and intent.priority == Priority.CRITICAL:
            # 긴급 상황에서는 빠른 정책 우선
            reasoning += f" (긴급 상황: {intent.priority.name} 우선순위 적용)"
            # refine 정책이 가장 빠르므로 긴급 상황에서는 refine 우선
            if primary_policy != 'refine':
                fallback_policies = [primary_policy] + fallback_policies
                primary_policy = 'refine'
        
        # 신뢰도 계산
        base_confidence = intent.confidence
        adjusted_confidence = min(1.0, base_confidence + priority_boost['boost'])
        
        # 컨텍스트 보존 정보
        context_preservation = {
            'original_intent': intent.intent_type.value,
            'detected_keywords': intent.keywords,
            'goal': intent.goal,
            'priority': intent.priority.name,
            'confidence': intent.confidence
        }
        
        return RoutingDecision(
            selected_policy=primary_policy,
            confidence=adjusted_confidence,
            reasoning=reasoning,
            context_preservation=context_preservation,
            fallback_policies=fallback_policies[:2]  # 최대 2개 폴백
        )
    
    def _preserve_context(self, intent: Intent, decision: RoutingDecision) -> Dict[str, Any]:
        """
        컨텍스트 보존 처리
        
        Args:
            intent: 의도 정보
            decision: 라우팅 결정
            
        Returns:
            보존된 컨텍스트
        """
        preserved = {
            # 기본 의도 정보
            'intent_type': intent.intent_type.value,
            'intent_confidence': intent.confidence,
            'intent_keywords': intent.keywords,
            'goal': intent.goal,
            'priority': intent.priority.name,
            
            # 라우팅 정보
            'selected_policy': decision.selected_policy,
            'routing_confidence': decision.confidence,
            'fallback_policies': decision.fallback_policies,
            
            # 컨텍스트 추출 정보
            'detected_languages': intent.context.get('detected_languages', []),
            'detected_frameworks': intent.context.get('detected_frameworks', []),
            'detected_files': intent.context.get('detected_files', []),
            'has_code_snippet': intent.context.get('has_code_snippet', False),
            'has_file_path': intent.context.get('has_file_path', False),
            
            # 다중 의도 정보
            'has_multiple_intents': len(intent.sub_intents) > 0,
            'sub_intent_count': len(intent.sub_intents),
            'sub_intent_types': [si.intent_type.value for si in intent.sub_intents],
            
            # 원본 입력 보존
            'raw_input': intent.raw_input,
            'timestamp': datetime.now().isoformat()
        }
        
        return preserved
    
    def get_routing_statistics(self) -> Dict[str, Any]:
        """
        라우팅 통계 반환
        
        Returns:
            통계 정보
        """
        if not self.routing_history:
            return {'message': '라우팅 기록이 없습니다'}
        
        policy_counts = defaultdict(int)
        intent_counts = defaultdict(int)
        
        for record in self.routing_history:
            policy_counts[record['policy']] += 1
            intent_counts[record['intent_type']] += 1
        
        return {
            'total_routings': len(self.routing_history),
            'policy_distribution': dict(policy_counts),
            'intent_distribution': dict(intent_counts),
            'recent_routings': list(self.routing_history)[-10:]
        }
    
    def suggest_policy_adjustment(self, intent_type: IntentType, 
                                 current_policy: str,
                                 success_rate: float) -> Optional[str]:
        """
        정책 조정 제안
        
        Args:
            intent_type: 의도 타입
            current_policy: 현재 정책
            success_rate: 성공률
            
        Returns:
            제안 메시지 또는 None
        """
        recommended = self.intent_policy_map.get(intent_type, {}).get('primary', 'balance')
        
        if success_rate < 0.5 and current_policy != recommended:
            return f"의도 '{intent_type.value}'에 대해 '{recommended}' 정책을 권장합니다 (현재: {current_policy}, 성공률: {success_rate:.1%})"
        
        if success_rate > 0.8 and current_policy == recommended:
            return f"현재 '{current_policy}' 정책이 '{intent_type.value}'에 매우 효과적입니다 (성공률: {success_rate:.1%})"
        
        return None


class IntentContextManager:
    """의도 컨텍스트 관리 클래스"""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        # 세션별 컨텍스트 저장
        self.session_contexts: Dict[str, deque] = {}
    
    def save_context(self, session_id: str, context: Dict[str, Any]):
        """
        세션 컨텍스트 저장
        
        Args:
            session_id: 세션 ID
            context: 저장할 컨텍스트
        """
        if session_id not in self.session_contexts:
            self.session_contexts[session_id] = deque(maxlen=self.max_history)
        
        context['saved_at'] = datetime.now().isoformat()
        self.session_contexts[session_id].append(context)
    
    def get_context(self, session_id: str, lookback: int = 1) -> Optional[Dict[str, Any]]:
        """
        세션 컨텍스트 조회
        
        Args:
            session_id: 세션 ID
            lookback: 몇 번째 전 컨텍스트 (1=최근, 2=직전, ...)
            
        Returns:
            컨텍스트 또는 None
        """
        if session_id not in self.session_contexts:
            return None
        
        history = self.session_contexts[session_id]
        if len(history) < lookback:
            return None
        
        return list(history)[-lookback]
    
    def get_context_chain(self, session_id: str) -> List[Dict[str, Any]]:
        """
        세션의 전체 컨텍스트 체인 조회
        
        Args:
            session_id: 세션 ID
            
        Returns:
            컨텍스트 리스트
        """
        if session_id not in self.session_contexts:
            return []
        
        return list(self.session_contexts[session_id])
    
    def clear_session(self, session_id: str):
        """세션 컨텍스트 초기화"""
        if session_id in self.session_contexts:
            del self.session_contexts[session_id]
    
    def enrich_with_context(self, user_input: str, 
                          session_id: str) -> Dict[str, Any]:
        """
        사용자 입력에 이전 컨텍스트를 보강
        
        Args:
            user_input: 사용자 입력
            session_id: 세션 ID
            
        Returns:
            보강된 입력 정보
        """
        current_context = self.get_context(session_id)
        
        enriched = {
            'input': user_input,
            'session_id': session_id,
            'has_previous_context': current_context is not None,
            'previous_intent': current_context.get('intent_type') if current_context else None,
            'previous_policy': current_context.get('selected_policy') if current_context else None,
            'previous_goal': current_context.get('goal') if current_context else None,
            'context_chain_length': len(self.session_contexts.get(session_id, []))
        }
        
        # 연속된 동일 의도 감지
        if current_context:
            # 같은 목표나 의도가 반복되는지 확인
            similar_keywords = set(current_context.get('intent_keywords', [])) & set(user_input.lower().split())
            enriched['continuity_score'] = len(similar_keywords) / max(len(user_input.split()), 1)
        else:
            enriched['continuity_score'] = 0.0
        
        return enriched


def route_by_intent(user_input: str, 
                   session_id: Optional[str] = None,
                   previous_context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    의도 기반 라우팅 편의 함수
    
    Args:
        user_input: 사용자 입력
        session_id: 세션 ID (선택)
        previous_context: 이전 컨텍스트 (선택)
        
    Returns:
        라우팅 결과
    """
    router = IntentBasedRouter()
    
    # 컨텍스트 보강 (세션 ID 제공된 경우)
    if session_id:
        context_manager = IntentContextManager()
        enriched = context_manager.enrich_with_context(user_input, session_id)
        
        # 이전 컨텍스트가 있으면 함께 전달
        if previous_context:
            enriched.update(previous_context)
        
        result = router.recognize_intent_and_route(user_input, enriched)
        
        # 컨텍스트 저장
        context_manager.save_context(session_id, result['context'])
        
        return result
    else:
        return router.recognize_intent_and_route(user_input, previous_context)
