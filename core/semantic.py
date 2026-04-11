#!/usr/bin/env python3
"""
Semantic Parser Module
의미론적 분석 - 의미 추출, 관계 매핑, 의미론적 유사성, 개념 식별, 지식 그래프 통합
"""

import re
import json
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import math


@dataclass
class Concept:
    """개념 데이터 클래스"""
    concept_id: str
    name: str
    concept_type: str  # entity, action, attribute, relation
    synonyms: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0


@dataclass
class SemanticRelation:
    """의미론적 관계 데이터 클래스"""
    source: str
    target: str
    relation_type: str  # is_a, part_of, uses, implements, depends_on, related_to
    strength: float = 0.5
    evidence: List[str] = field(default_factory=list)


@dataclass
class SemanticMeaning:
    """의미 데이터 클래스"""
    text: str
    concepts: List[Concept]
    relations: List[SemanticRelation]
    intent: Optional[str] = None
    sentiment: Optional[str] = None
    urgency: float = 0.0
    extracted_at: str = field(default_factory=lambda: datetime.now().isoformat())


class SemanticParser:
    """의미론적 파서 클래스"""
    
    def __init__(self):
        # 개념 사전
        self.concept_dictionary = self._build_concept_dictionary()
        
        # 관계 패턴
        self.relation_patterns = {
            'is_a': [
                r'(\w+)는?\s+(\w+)이다',
                r'(\w+)는?\s+(\w+)입니다',
                r'(\w+)\s+is\s+a\s+(\w+)',
                r'(\w+)\s+is\s+an\s+(\w+)',
            ],
            'part_of': [
                r'(\w+)의\s+일부',
                r'part\s+of\s+(\w+)',
                r'(\w+)에\s+포함',
            ],
            'uses': [
                r'(\w+)를?\s+사용',
                r'(\w+)를?\s+이용',
                r'uses?\s+(\w+)',
            ],
            'implements': [
                r'(\w+)를?\s+구현',
                r'(\w+)를?\s+구축',
                r'implements?\s+(\w+)',
            ],
            'depends_on': [
                r'(\w+)에\s+의존',
                r'(\w+)가\s+필요',
                r'depends?\s+on\s+(\w+)',
            ],
            'related_to': [
                r'(\w+)와\s+관련',
                r'(\w+)와\s+연관',
                r'related\s+to\s+(\w+)',
            ]
        }
        
        # 감정 키워드
        self.sentiment_keywords = {
            'positive': [
                '좋다', '좋은', '훌륭', '우수', '만족', '성공', '잘', '효과적',
                'good', 'great', 'excellent', 'success', 'well', 'effective'
            ],
            'negative': [
                '나쁘다', '불량', '실패', '문제', '오류', '에러', '심각',
                'bad', 'poor', 'fail', 'problem', 'error', 'serious', 'critical'
            ],
            'urgent': [
                '긴급', '즉시', '바로', '당장', '중요', '필수',
                'urgent', 'immediately', 'now', 'important', 'critical', 'must'
            ]
        }
        
        # 긴급도 패턴
        self.urgency_patterns = [
            r'긴급|urgent|critical|즉시|immediately|지금|now',
            r'중단|down|장애|broken|안됨|not working',
            r'필수|must|필요|need|반드시',
        ]
    
    def extract_meaning(self, text: str, context: Optional[Dict] = None) -> SemanticMeaning:
        """
        텍스트에서 의미 추출
        
        Args:
            text: 입력 텍스트
            context: 컨텍스트 정보
            
        Returns:
            추출된 의미 정보
        """
        # 1. 개념 식별
        concepts = self.identify_concepts(text)
        
        # 2. 관계 매핑
        relations = self.map_relationships(text, concepts)
        
        # 3. 감정 분석
        sentiment = self.analyze_sentiment(text)
        
        # 4. 긴급도 분석
        urgency = self.calculate_urgency(text)
        
        # 5. 의도 추정
        intent = self.infer_intent(text, concepts)
        
        return SemanticMeaning(
            text=text,
            concepts=concepts,
            relations=relations,
            intent=intent,
            sentiment=sentiment,
            urgency=urgency
        )
    
    def identify_concepts(self, text: str) -> List[Concept]:
        """
        텍스트에서 개념 식별
        
        Args:
            text: 입력 텍스트
            
        Returns:
            식별된 개념 리스트
        """
        identified_concepts = []
        text_lower = text.lower()
        
        for concept_type, concepts in self.concept_dictionary.items():
            for concept_name, synonyms in concepts.items():
                # 직접 매칭
                if concept_name.lower() in text_lower:
                    confidence = self._calculate_concept_confidence(
                        concept_name, text, True
                    )
                    identified_concepts.append(Concept(
                        concept_id=f"{concept_type}_{concept_name}_{hash(text) % 10000}",
                        name=concept_name,
                        concept_type=concept_type,
                        synonyms=synonyms,
                        confidence=confidence
                    ))
                else:
                    # 동의어 매칭
                    for synonym in synonyms:
                        if synonym.lower() in text_lower:
                            confidence = self._calculate_concept_confidence(
                                synonym, text, False
                            )
                            identified_concepts.append(Concept(
                                concept_id=f"{concept_type}_{concept_name}_{hash(text) % 10000}",
                                name=concept_name,
                                concept_type=concept_type,
                                synonyms=synonyms,
                                confidence=confidence * 0.8  # 동의어는 신뢰도 감소
                            ))
                            break
        
        # 중복 제거 (가장 높은 신뢰도만 유지)
        unique_concepts = {}
        for concept in identified_concepts:
            key = f"{concept.concept_type}_{concept.name}"
            if key not in unique_concepts or unique_concepts[key].confidence < concept.confidence:
                unique_concepts[key] = concept
        
        return list(unique_concepts.values())
    
    def map_relationships(self, text: str, 
                         concepts: List[Concept]) -> List[SemanticRelation]:
        """
        개념 간 관계 매핑
        
        Args:
            text: 입력 텍스트
            concepts: 식별된 개념 리스트
            
        Returns:
            매핑된 관계 리스트
        """
        relations = []
        concept_names = [c.name for c in concepts]
        
        # 패턴 기반 관계 추출
        for relation_type, patterns in self.relation_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    if len(match.groups()) >= 2:
                        source = match.group(1)
                        target = match.group(2)
                        
                        # 추출된 개념과 매칭
                        if source in concept_names or target in concept_names:
                            evidence = [match.group(0)]
                            strength = self._calculate_relation_strength(
                                source, target, text, evidence
                            )
                            
                            relations.append(SemanticRelation(
                                source=source,
                                target=target,
                                relation_type=relation_type,
                                strength=strength,
                                evidence=evidence
                            ))
        
        # 개념 간 거리 기반 관계 추출 (간접 관계)
        for i, concept1 in enumerate(concepts):
            for concept2 in concepts[i+1:]:
                distance = self._calculate_concept_distance(
                    concept1.name, concept2.name, text
                )
                if distance < 50:  # 가까운 거리
                    strength = max(0.1, 1.0 - (distance / 50))
                    relations.append(SemanticRelation(
                        source=concept1.name,
                        target=concept2.name,
                        relation_type='related_to',
                        strength=strength,
                        evidence=['proximity_based']
                    ))
        
        return relations
    
    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """
        두 텍스트 간 의미론적 유사성 계산
        
        Args:
            text1: 첫 번째 텍스트
            text2: 두 번째 텍스트
            
        Returns:
            유사성 점수 (0.0 ~ 1.0)
        """
        # 개념 기반 유사성
        concepts1 = self.identify_concepts(text1)
        concepts2 = self.identify_concepts(text2)
        
        concept_sim = self._calculate_concept_similarity(concepts1, concepts2)
        
        # 키워드 기반 유사성
        keywords1 = set(self._extract_keywords(text1))
        keywords2 = set(self._extract_keywords(text2))
        
        if not keywords1 or not keywords2:
            keyword_sim = 0.0
        else:
            intersection = len(keywords1 & keywords2)
            union = len(keywords1 | keywords2)
            keyword_sim = intersection / union if union > 0 else 0.0
        
        # 가중 조합
        similarity = (concept_sim * 0.6) + (keyword_sim * 0.4)
        return min(1.0, similarity)
    
    def build_knowledge_graph(self, texts: List[str]) -> Dict[str, Any]:
        """
        텍스트 리스트로부터 지식 그래프 구축
        
        Args:
            texts: 텍스트 리스트
            
        Returns:
            지식 그래프 정보
        """
        all_concepts = {}
        all_relations = []
        
        for text in texts:
            meaning = self.extract_meaning(text)
            
            # 개념 수집
            for concept in meaning.concepts:
                key = f"{concept.concept_type}_{concept.name}"
                if key in all_concepts:
                    # 신뢰도 업데이트
                    all_concepts[key].confidence = max(
                        all_concepts[key].confidence, concept.confidence
                    )
                else:
                    all_concepts[key] = concept
            
            # 관계 수집
            all_relations.extend(meaning.relations)
        
        # 그래프 구조 생성
        nodes = []
        edges = []
        
        for concept in all_concepts.values():
            nodes.append({
                'id': concept.concept_id,
                'name': concept.name,
                'type': concept.concept_type,
                'confidence': concept.confidence
            })
        
        for relation in all_relations:
            edges.append({
                'source': relation.source,
                'target': relation.target,
                'type': relation.relation_type,
                'strength': relation.strength
            })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'concept_count': len(nodes),
            'relation_count': len(edges),
            'statistics': self._calculate_graph_statistics(nodes, edges)
        }
    
    def analyze_sentiment(self, text: str) -> Optional[str]:
        """
        텍스트 감정 분석
        
        Args:
            text: 입력 텍스트
            
        Returns:
            감정 라벨
        """
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self.sentiment_keywords['positive'] if word in text_lower)
        negative_count = sum(1 for word in self.sentiment_keywords['negative'] if word in text_lower)
        urgent_count = sum(1 for word in self.sentiment_keywords['urgent'] if word in text_lower)
        
        # 긴급도가 높으면 negative로 분류 가능
        if urgent_count > 0:
            if negative_count > 0:
                return 'negative_urgent'
            return 'urgent'
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def calculate_urgency(self, text: str) -> float:
        """
        텍스트 긴급도 계산
        
        Args:
            text: 입력 텍스트
            
        Returns:
            긴급도 점수 (0.0 ~ 1.0)
        """
        urgency_score = 0.0
        text_lower = text.lower()
        
        # 긴급 패턴 매칭
        for pattern in self.urgency_patterns:
            matches = len(re.findall(pattern, text_lower))
            urgency_score += matches * 0.3
        
        # 특수 문자 (!!!!)
        urgency_score += len(re.findall(r'!{2,}', text)) * 0.1
        
        # 대문자 비율 (샤우팅)
        words = text.split()
        if words:
            caps_ratio = sum(1 for w in words if w.isupper() and len(w) > 1) / len(words)
            urgency_score += caps_ratio * 0.2
        
        return min(1.0, urgency_score)
    
    def infer_intent(self, text: str, concepts: List[Concept]) -> Optional[str]:
        """
        텍스트로부터 의도 추정
        
        Args:
            text: 입력 텍스트
            concepts: 식별된 개념 리스트
            
        Returns:
            추정된 의도
        """
        text_lower = text.lower()
        
        # 액션 개념 확인
        action_concepts = [c for c in concepts if c.concept_type == 'action']
        if action_concepts:
            return action_concepts[0].name
        
        # 패턴 기반 의도 추정
        intent_patterns = {
            'create': r'만들|생성|작성|create|make|build',
            'analyze': r'분석|analyze|검토|review',
            'fix': r'고치|수정|fix|repair|debug',
            'explain': r'설명|explain|알려|tell',
            'test': r'테스트|test|검증|verify',
            'deploy': r'배포|deploy|릴리스|release'
        }
        
        for intent, pattern in intent_patterns.items():
            if re.search(pattern, text_lower):
                return intent
        
        return 'unknown'
    
    def _build_concept_dictionary(self) -> Dict[str, Dict[str, List[str]]]:
        """개념 사전 구축"""
        return {
            'entity': {
                'function': ['함수', 'method', 'procedure', 'func'],
                'class': ['클래스', 'class', '객체', 'object'],
                'module': ['모듈', 'module', '패키지', 'package', '라이브러리', 'library'],
                'database': ['데이터베이스', 'database', 'DB', 'db', '스토리지'],
                'api': ['API', 'api', '인터페이스', 'interface'],
                'server': ['서버', 'server', '호스트', 'host'],
                'client': ['클라이언트', 'client', '프론트', 'frontend'],
                'user': ['사용자', 'user', '유저', '고객'],
            },
            'action': {
                'create': ['생성', '만들기', '작성', 'create', 'make', 'build'],
                'read': ['읽기', '조회', '검색', 'read', 'fetch', 'get'],
                'update': ['수정', '업데이트', '갱신', 'update', 'modify'],
                'delete': ['삭제', '제거', 'delete', 'remove', 'drop'],
                'test': ['테스트', '검증', 'test', 'verify', 'validate'],
                'deploy': ['배포', '릴리스', 'deploy', 'release', 'publish'],
                'analyze': ['분석', 'analytics', 'analyze', 'inspect'],
            },
            'attribute': {
                'performance': ['성능', '속도', 'performance', 'speed'],
                'security': ['보안', '안전', 'security', 'safety'],
                'quality': ['품질', 'quality', '신뢰성', 'reliability'],
                'scalability': ['확장성', 'scalability', '규모'],
                'maintainability': ['유지보수성', 'maintainability', '가독성'],
            },
            'relation': {
                'dependency': ['의존', 'dependency', '필요', 'need'],
                'implementation': ['구현', 'implementation', '구축', 'build'],
                'usage': ['사용', 'usage', '이용', 'use'],
                'inheritance': ['상속', 'inheritance', '확장', 'extends'],
                'composition': ['구성', 'composition', '포함', 'include'],
            }
        }
    
    def _calculate_concept_confidence(self, concept_name: str, 
                                     text: str, is_direct: bool) -> float:
        """개념 신뢰도 계산"""
        base_confidence = 0.8 if is_direct else 0.6
        
        # 빈도 기반 조정
        count = text.lower().count(concept_name.lower())
        frequency_boost = min(0.15, count * 0.05)
        
        # 대문자 (고유명사일 가능성)
        if concept_name[0].isupper():
            base_confidence += 0.05
        
        return min(1.0, base_confidence + frequency_boost)
    
    def _calculate_relation_strength(self, source: str, target: str,
                                    text: str, evidence: List[str]) -> float:
        """관계 강도 계산"""
        base_strength = 0.5
        
        # 증거 개수
        evidence_boost = len(evidence) * 0.1
        
        # 거리 기반 (가까울수록 강함)
        distance = self._calculate_concept_distance(source, target, text)
        distance_factor = max(0.1, 1.0 - (distance / 100))
        
        strength = base_strength + evidence_boost
        return min(1.0, strength * distance_factor)
    
    def _calculate_concept_distance(self, concept1: str, 
                                   concept2: str, text: str) -> float:
        """텍스트 내 두 개념 간 거리 계산"""
        pos1 = text.lower().find(concept1.lower())
        pos2 = text.lower().find(concept2.lower())
        
        if pos1 == -1 or pos2 == -1:
            return float('inf')
        
        return abs(pos1 - pos2)
    
    def _calculate_concept_similarity(self, concepts1: List[Concept],
                                     concepts2: List[Concept]) -> float:
        """개념 리스트 간 유사성 계산"""
        if not concepts1 or not concepts2:
            return 0.0
        
        names1 = {c.name.lower() for c in concepts1}
        names2 = {c.name.lower() for c in concepts2}
        
        # 타입별 가중치
        type_weights = {
            'entity': 1.0,
            'action': 0.9,
            'attribute': 0.7,
            'relation': 0.6
        }
        
        weighted_matches = 0.0
        total_weight = 0.0
        
        for c1 in concepts1:
            weight = type_weights.get(c1.concept_type, 0.5)
            total_weight += weight
            
            if c1.name.lower() in names2:
                weighted_matches += weight
        
        return weighted_matches / total_weight if total_weight > 0 else 0.0
    
    def _extract_keywords(self, text: str) -> List[str]:
        """키워드 추출"""
        # 2글자 이상 단어만 추출
        words = re.findall(r'\b\w{2,}\b', text.lower())
        
        # 불용어 필터링
        stopwords = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can',
                    'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has',
                    'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see',
                    'two', 'who', 'boy', 'did', 'she', 'use', 'her', 'way', 'many',
                    'oil', 'sit', 'set', 'run', 'eat', 'far', 'sea', 'eye', 'ago',
                    'off', 'too', 'any', 'say', 'man', 'try', 'ask', 'end', 'why',
                    'let', 'put', 'say', 'she', 'try', 'way', 'own', 'say', 'too',
                    '이는', '그리고', '하지만', '또한', '그리고', '그런데', '그래서'}
        
        return [w for w in words if w not in stopwords]
    
    def _calculate_graph_statistics(self, nodes: List[Dict], 
                                   edges: List[Dict]) -> Dict[str, Any]:
        """지식 그래프 통계 계산"""
        if not nodes:
            return {}
        
        # 타입 분포
        type_distribution = defaultdict(int)
        for node in nodes:
            type_distribution[node['type']] += 1
        
        # 관계 타입 분포
        relation_types = defaultdict(int)
        for edge in edges:
            relation_types[edge['type']] += 1
        
        # 평균 연결 수 (평균 degree)
        avg_connections = len(edges) / len(nodes) if nodes else 0
        
        return {
            'type_distribution': dict(type_distribution),
            'relation_type_distribution': dict(relation_types),
            'average_connections_per_node': avg_connections,
            'density': len(edges) / (len(nodes) * (len(nodes) - 1)) if len(nodes) > 1 else 0
        }


def extract_semantic_meaning(text: str) -> Dict[str, Any]:
    """
    의미 추출 편의 함수
    
    Args:
        text: 입력 텍스트
        
    Returns:
        의미 정보 딕셔너리
    """
    parser = SemanticParser()
    meaning = parser.extract_meaning(text)
    
    return {
        'text': meaning.text,
        'concepts': [
            {
                'name': c.name,
                'type': c.concept_type,
                'confidence': c.confidence,
                'synonyms': c.synonyms
            }
            for c in meaning.concepts
        ],
        'relations': [
            {
                'source': r.source,
                'target': r.target,
                'type': r.relation_type,
                'strength': r.strength
            }
            for r in meaning.relations
        ],
        'intent': meaning.intent,
        'sentiment': meaning.sentiment,
        'urgency': meaning.urgency
    }
