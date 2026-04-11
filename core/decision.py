#!/usr/bin/env python3
"""
Decision Engine Module
의사결정 엔진 - 다중 기준 의사결정, 불확실성 처리, 신뢰도 점수화, 설명 생성, 의사결정 로깅
"""

import json
import math
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import defaultdict


class DecisionType(Enum):
    """의사결정 타입"""
    POLICY_SELECTION = "policy_selection"
    AGENT_SELECTION = "agent_selection"
    ROUTING = "routing"
    EXECUTION = "execution"
    RETRY = "retry"
    RESOURCE_ALLOCATION = "resource_allocation"


class UncertaintyLevel(Enum):
    """불확실성 수준"""
    LOW = 0.2
    MEDIUM = 0.5
    HIGH = 0.8
    CRITICAL = 1.0


@dataclass
class Criterion:
    """의사결정 기준 데이터 클래스"""
    name: str
    weight: float
    score: float
    description: str
    evidence: List[str] = field(default_factory=list)


@dataclass
class Decision:
    """의사결정 데이터 클래스"""
    decision_id: str
    decision_type: DecisionType
    chosen_option: str
    confidence: float
    uncertainty_level: UncertaintyLevel
    criteria: List[Criterion]
    alternatives: List[Dict[str, Any]]
    explanation: str
    context: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    execution_time_ms: float = 0.0


class DecisionEngine:
    """의사결정 엔진 클래스"""
    
    def __init__(self, log_file_path: Optional[str] = None):
        self.log_file_path = log_file_path or "/home/lks/ai_router/log/decision_log.json"
        self.decision_history: List[Decision] = []
        self.criteria_weights_cache: Dict[str, Dict[str, float]] = {}
        
        # 기본 다중 기준 가중치
        self.default_criteria = {
            'performance': 0.25,
            'reliability': 0.20,
            'cost': 0.15,
            'time': 0.20,
            'quality': 0.20
        }
        
        # 불확실성 처리 설정
        self.uncertainty_config = {
            'confidence_threshold_high': 0.8,
            'confidence_threshold_medium': 0.5,
            'confidence_threshold_low': 0.3,
            'uncertainty_boost_factor': 0.1
        }
    
    def make_decision(self,
                     options: List[Dict[str, Any]],
                     decision_type: DecisionType,
                     custom_criteria: Optional[Dict[str, float]] = None,
                     context: Optional[Dict[str, Any]] = None) -> Decision:
        """
        다중 기준 의사결정 수행
        
        Args:
            options: 선택 옵션 리스트 (각 옵션은 점수 딕셔너리 포함)
            decision_type: 의사결정 타입
            custom_criteria: 사용자 정의 기준 가중치
            context: 추가 컨텍스트
            
        Returns:
            의사결정 결과
        """
        start_time = datetime.now()
        
        # 1. 기준 설정
        criteria_weights = custom_criteria or self.default_criteria
        
        # 2. 각 옵션 평가
        evaluated_options = []
        for option in options:
            scores = option.get('scores', {})
            total_score = self._calculate_weighted_score(scores, criteria_weights)
            
            evaluated_options.append({
                'option': option,
                'total_score': total_score,
                'scores': scores
            })
        
        # 3. 최고 점수 옵션 선택
        best_option = max(evaluated_options, key=lambda x: x['total_score'])
        
        # 4. 기준 상세 생성
        criteria_details = []
        for criterion_name, weight in criteria_weights.items():
            score = best_option['scores'].get(criterion_name, 0.5)
            criteria_details.append(Criterion(
                name=criterion_name,
                weight=weight,
                score=score,
                description=f"기준 '{criterion_name}'에 대한 평가",
                evidence=[f"점수: {score:.2f}, 가중치: {weight:.2f}"]
            ))
        
        # 5. 신뢰도 계산
        confidence = self._calculate_confidence(best_option, evaluated_options)
        
        # 6. 불확실성 수준 판단
        uncertainty = self._assess_uncertainty(confidence, best_option['scores'])
        
        # 7. 대안 정보 구성
        alternatives = [
            {
                'name': opt['option'].get('name', f"option_{i}"),
                'score': opt['total_score'],
                'confidence': self._calculate_confidence(opt, evaluated_options)
            }
            for i, opt in enumerate(evaluated_options)
            if opt['option'] != best_option['option']
        ]
        
        # 8. 설명 생성
        explanation = self._generate_explanation(
            best_option, criteria_details, confidence, uncertainty
        )
        
        # 9. 의사결정 생성
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        decision = Decision(
            decision_id=self._generate_decision_id(),
            decision_type=decision_type,
            chosen_option=best_option['option'].get('name', 'unknown'),
            confidence=confidence,
            uncertainty_level=uncertainty,
            criteria=criteria_details,
            alternatives=alternatives,
            explanation=explanation,
            context=context or {},
            execution_time_ms=execution_time
        )
        
        # 10. 로깅
        self._log_decision(decision)
        self.decision_history.append(decision)
        
        return decision
    
    def handle_uncertainty(self, 
                          decision: Decision,
                          fallback_strategy: str = "conservative") -> Dict[str, Any]:
        """
        불확실성 처리
        
        Args:
            decision: 의사결정 결과
            fallback_strategy: 폴백 전략 (conservative, optimistic, random)
            
        Returns:
            불확실성 처리 결과
        """
        uncertainty_level = decision.uncertainty_level
        
        result = {
            'original_decision': decision.chosen_option,
            'uncertainty_level': uncertainty_level.name,
            'confidence': decision.confidence,
            'action_taken': 'proceed',
            'recommendations': []
        }
        
        # 높은 불확실성 처리
        if uncertainty_level in [UncertaintyLevel.HIGH, UncertaintyLevel.CRITICAL]:
            if fallback_strategy == "conservative":
                # 가장 안전한 대안 선택
                if decision.alternatives:
                    safest = min(decision.alternatives, 
                               key=lambda x: abs(x['confidence'] - 0.5))
                    result['action_taken'] = 'use_fallback'
                    result['fallback_option'] = safest['name']
                    result['recommendations'].append(
                        f"높은 불확실성으로 인해 대안 '{safest['name']}'을(를) 권장"
                    )
                else:
                    result['action_taken'] = 'request_more_info'
                    result['recommendations'].append(
                        "추가 정보 수집이 필요합니다"
                    )
            
            elif fallback_strategy == "optimistic":
                # 원래 결정 유지하되 모니터링 강화
                result['action_taken'] = 'proceed_with_caution'
                result['recommendations'].extend([
                    "원래 결정을 진행하되 밀접 모니터링 필요",
                    "빠른 롤백 계획 준비"
                ])
            
            elif fallback_strategy == "random":
                # 무작위 선택 (테스트용)
                import random
                all_options = [decision.chosen_option] + [a['name'] for a in decision.alternatives]
                result['action_taken'] = 'random_selection'
                result['selected_option'] = random.choice(all_options)
        
        # 중간 수준 불확실성
        elif uncertainty_level == UncertaintyLevel.MEDIUM:
            result['recommendations'].extend([
                "의사결정을 진행하되 리스크 완화 조치 적용",
                "단계적 접근 권장"
            ])
        
        return result
    
    def calculate_confidence_score(self, 
                                 factors: Dict[str, float],
                                 weights: Optional[Dict[str, float]] = None) -> float:
        """
        신뢰도 점수화
        
        Args:
            factors: 신뢰도 요인 (0.0 ~ 1.0)
            weights: 요인별 가중치
            
        Returns:
            종합 신뢰도 점수
        """
        if not factors:
            return 0.5
        
        if weights is None:
            weights = {k: 1.0 / len(factors) for k in factors.keys()}
        
        # 가중 평균 계산
        weighted_sum = sum(
            factors.get(k, 0) * weights.get(k, 0.1)
            for k in set(factors.keys()) | set(weights.keys())
        )
        
        total_weight = sum(weights.values())
        
        confidence = weighted_sum / total_weight if total_weight > 0 else 0.5
        return min(1.0, max(0.0, confidence))
    
    def generate_explanation(self, 
                           decision: Decision,
                           detail_level: str = "standard") -> str:
        """
        의사결정 설명 생성
        
        Args:
            decision: 의사결정 결과
            detail_level: 상세 수준 (brief, standard, detailed)
            
        Returns:
            설명 텍스트
        """
        if detail_level == "brief":
            return f"'{decision.chosen_option}' 선택됨 (신뢰도: {decision.confidence:.1%})"
        
        lines = [
            f"의사결정: {decision.decision_type.value}",
            f"선택: {decision.chosen_option}",
            f"신뢰도: {decision.confidence:.1%}",
            f"불확실성: {decision.uncertainty_level.name}",
            ""
        ]
        
        if detail_level == "detailed":
            lines.extend([
                "평가 기준:",
                *[f"  - {c.name}: {c.score:.2f} (가중치: {c.weight:.2f})" 
                  for c in decision.criteria],
                ""
            ])
            
            if decision.alternatives:
                lines.extend([
                    "고려된 대안:",
                    *[f"  - {a['name']}: {a['score']:.2f}" for a in decision.alternatives],
                    ""
                ])
        
        lines.extend([
            f"실행 시간: {decision.execution_time_ms:.1f}ms",
            f"설명: {decision.explanation}"
        ])
        
        return "\n".join(lines)
    
    def get_decision_statistics(self) -> Dict[str, Any]:
        """
        의사결정 통계 반환
        
        Returns:
            통계 정보
        """
        if not self.decision_history:
            return {'message': '의사결정 기록이 없습니다'}
        
        total_decisions = len(self.decision_history)
        
        # 타입별 분포
        type_distribution = defaultdict(int)
        for d in self.decision_history:
            type_distribution[d.decision_type.value] += 1
        
        # 평균 신뢰도
        avg_confidence = sum(d.confidence for d in self.decision_history) / total_decisions
        
        # 불확실성 분포
        uncertainty_distribution = defaultdict(int)
        for d in self.decision_history:
            uncertainty_distribution[d.uncertainty_level.name] += 1
        
        # 평균 실행 시간
        avg_execution_time = sum(d.execution_time_ms for d in self.decision_history) / total_decisions
        
        return {
            'total_decisions': total_decisions,
            'type_distribution': dict(type_distribution),
            'average_confidence': avg_confidence,
            'uncertainty_distribution': dict(uncertainty_distribution),
            'average_execution_time_ms': avg_execution_time,
            'high_confidence_rate': sum(1 for d in self.decision_history if d.confidence > 0.8) / total_decisions
        }
    
    def get_recent_decisions(self, count: int = 5) -> List[Decision]:
        """최근 의사결정 반환"""
        return self.decision_history[-count:]
    
    def export_decisions(self, file_path: Optional[str] = None) -> bool:
        """의사결정 기록보내기"""
        try:
            path = file_path or self.log_file_path
            data = [self._decision_to_dict(d) for d in self.decision_history]
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"의사결정보내기 오류: {e}")
            return False
    
    def _calculate_weighted_score(self, 
                                 scores: Dict[str, float], 
                                 weights: Dict[str, float]) -> float:
        """가중 점수 계산"""
        if not scores or not weights:
            return 0.0
        
        weighted_sum = sum(
            scores.get(criterion, 0) * weight
            for criterion, weight in weights.items()
        )
        
        total_weight = sum(
            weight for criterion, weight in weights.items()
            if criterion in scores
        )
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _calculate_confidence(self, 
                            best_option: Dict,
                            all_options: List[Dict]) -> float:
        """신뢰도 계산"""
        best_score = best_option['total_score']
        
        if len(all_options) == 1:
            return 0.8  # 대안이 없으면 중간 신뢰도
        
        # 2위와의 점수 차이
        sorted_options = sorted(all_options, key=lambda x: x['total_score'], reverse=True)
        if len(sorted_options) >= 2:
            second_score = sorted_options[1]['total_score']
            score_diff = best_score - second_score
            
            # 점수 차이가 클수록 신뢰도 상승
            base_confidence = 0.5
            diff_boost = min(0.4, score_diff * 2)
            
            return min(1.0, base_confidence + diff_boost)
        
        return 0.6
    
    def _assess_uncertainty(self, 
                          confidence: float,
                          scores: Dict[str, float]) -> UncertaintyLevel:
        """불확실성 수준 판단"""
        # 점수 분산도 계산
        if scores:
            variance = sum((s - 0.5) ** 2 for s in scores.values()) / len(scores)
            consistency = 1.0 - (variance * 4)  # 높은 분산 = 낮은 일관성
        else:
            consistency = 0.5
        
        # 종합 불확실성
        effective_confidence = confidence * consistency
        
        if effective_confidence >= 0.8:
            return UncertaintyLevel.LOW
        elif effective_confidence >= 0.5:
            return UncertaintyLevel.MEDIUM
        elif effective_confidence >= 0.3:
            return UncertaintyLevel.HIGH
        else:
            return UncertaintyLevel.CRITICAL
    
    def _generate_explanation(self,
                            best_option: Dict,
                            criteria: List[Criterion],
                            confidence: float,
                            uncertainty: UncertaintyLevel) -> str:
        """설명 생성"""
        option_name = best_option['option'].get('name', '선택된 옵션')
        
        # 핵심 기준 추출
        top_criteria = sorted(criteria, key=lambda c: c.score * c.weight, reverse=True)[:2]
        
        reasons = []
        for c in top_criteria:
            if c.score >= 0.7:
                reasons.append(f"{c.name}에서 우수한 성능")
            elif c.score >= 0.5:
                reasons.append(f"{c.name}에서 양호한 성능")
        
        explanation = f"{option_name}은(는) "
        if reasons:
            explanation += ", ".join(reasons) + "을(를) 보였습니다."
        else:
            explanation += "전반적으로 균형 잡힌 평가를 받았습니다."
        
        if uncertainty == UncertaintyLevel.HIGH:
            explanation += " 그러나 불확실성이 높으므로 주의가 필요합니다."
        elif uncertainty == UncertaintyLevel.LOW:
            explanation += " 높은 신뢰도로 선택되었습니다."
        
        return explanation
    
    def _log_decision(self, decision: Decision):
        """의사결정 로깅"""
        try:
            import os
            os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)
            
            # 기존 로그 로드
            existing_logs = []
            if os.path.exists(self.log_file_path):
                try:
                    with open(self.log_file_path, 'r', encoding='utf-8') as f:
                        existing_logs = json.load(f)
                except Exception:
                    pass
            
            # 새 로그 추가
            existing_logs.append(self._decision_to_dict(decision))
            
            # 저장
            with open(self.log_file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_logs, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"의사결정 로깅 오류: {e}")
    
    def _generate_decision_id(self) -> str:
        """의사결정 ID 생성"""
        import hashlib
        timestamp = datetime.now().isoformat()
        hash_input = f"{timestamp}_{len(self.decision_history)}"
        return f"dec_{hashlib.md5(hash_input.encode()).hexdigest()[:8]}"
    
    def _decision_to_dict(self, decision: Decision) -> Dict[str, Any]:
        """Decision을 딕셔너리로 변환"""
        return {
            'decision_id': decision.decision_id,
            'decision_type': decision.decision_type.value,
            'chosen_option': decision.chosen_option,
            'confidence': decision.confidence,
            'uncertainty_level': decision.uncertainty_level.name,
            'criteria': [
                {
                    'name': c.name,
                    'weight': c.weight,
                    'score': c.score,
                    'description': c.description,
                    'evidence': c.evidence
                }
                for c in decision.criteria
            ],
            'alternatives': decision.alternatives,
            'explanation': decision.explanation,
            'context': decision.context,
            'timestamp': decision.timestamp,
            'execution_time_ms': decision.execution_time_ms
        }


def quick_decision(options: List[str],
                  scores: List[Dict[str, float]],
                  decision_type: str = "general") -> Dict[str, Any]:
    """
    빠른 의사결정 편의 함수
    
    Args:
        options: 옵션 이름 리스트
        scores: 각 옵션의 점수 딕셔너리 리스트
        decision_type: 의사결정 타입
        
    Returns:
        의사결정 결과 요약
    """
    engine = DecisionEngine()
    
    option_dicts = [
        {'name': name, 'scores': score}
        for name, score in zip(options, scores)
    ]
    
    decision = engine.make_decision(
        options=option_dicts,
        decision_type=DecisionType(decision_type)
    )
    
    return {
        'chosen': decision.chosen_option,
        'confidence': decision.confidence,
        'explanation': decision.explanation,
        'uncertainty': decision.uncertainty_level.name
    }
