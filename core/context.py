#!/usr/bin/env python3
"""
Context Manager Module
컨텍스트 추적기 - 대화 기록, 세션 관리, 컨텍스트 관련성 점수화, 컨텍스트 정리, 세션 간 지속성
"""

import json
import time
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from collections import deque, defaultdict
import os


@dataclass
class ConversationTurn:
    """대화 턴 데이터 클래스"""
    turn_id: str
    timestamp: str
    user_input: str
    intent_type: str
    policy_used: str
    response_summary: str
    context_snapshot: Dict[str, Any]
    relevance_score: float = 0.0
    feedback: Optional[str] = None


@dataclass
class SessionContext:
    """세션 컨텍스트 데이터 클래스"""
    session_id: str
    created_at: str
    last_active: str
    conversation_history: List[ConversationTurn]
    accumulated_context: Dict[str, Any]
    metadata: Dict[str, Any]


class ContextTracker:
    """컨텍스트 추적기 클래스"""
    
    def __init__(self, max_history_per_session: int = 20, 
                 context_file_path: Optional[str] = None):
        self.max_history = max_history_per_session
        self.context_file_path = context_file_path or "/home/lks/ai_router/data/context_store.json"
        
        # 세션별 컨텍스트 저장
        self.sessions: Dict[str, SessionContext] = {}
        
        # 컨텍스트 관련성 설정
        self.relevance_config = {
            'time_decay_hours': 1.0,      # 시간 경과에 따른 감쇠 (시간)
            'keyword_weight': 0.3,        # 키워드 일치 가중치
            'intent_weight': 0.4,         # 의도 일치 가중치
            'recency_weight': 0.3,        # 최신성 가중치
            'min_relevance_threshold': 0.2  # 최소 관련성 임계값
        }
        
        # 저장된 컨텍스트 로드
        self._load_contexts()
    
    def create_session(self, session_id: Optional[str] = None) -> str:
        """
        새 세션 생성
        
        Args:
            session_id: 세션 ID (미제공 시 자동 생성)
            
        Returns:
            생성된 세션 ID
        """
        if session_id is None:
            # 타임스탬프 + 해시로 세션 ID 생성
            timestamp = datetime.now().isoformat()
            hash_input = f"{timestamp}_{time.time()}"
            session_id = hashlib.md5(hash_input.encode()).hexdigest()[:12]
        
        now = datetime.now().isoformat()
        self.sessions[session_id] = SessionContext(
            session_id=session_id,
            created_at=now,
            last_active=now,
            conversation_history=[],
            accumulated_context={},
            metadata={
                'turn_count': 0,
                'total_tokens': 0,
                'session_duration_minutes': 0
            }
        )
        
        return session_id
    
    def add_conversation_turn(self, session_id: str, 
                             user_input: str,
                             intent_type: str,
                             policy_used: str,
                             response_summary: str,
                             context_snapshot: Dict[str, Any]) -> ConversationTurn:
        """
        대화 턴 추가
        
        Args:
            session_id: 세션 ID
            user_input: 사용자 입력
            intent_type: 의도 타입
            policy_used: 사용된 정책
            response_summary: 응답 요약
            context_snapshot: 컨텍스트 스냅샷
            
        Returns:
            추가된 ConversationTurn
        """
        if session_id not in self.sessions:
            self.create_session(session_id)
        
        session = self.sessions[session_id]
        
        # 턴 ID 생성
        turn_number = len(session.conversation_history) + 1
        turn_id = f"{session_id}_{turn_number:04d}"
        
        # 현재 시간
        now = datetime.now()
        timestamp = now.isoformat()
        
        # 관련성 점수 계산 (이전 턴과의 연관성)
        relevance_score = self._calculate_relevance(
            session, user_input, intent_type
        )
        
        # 대화 턴 생성
        turn = ConversationTurn(
            turn_id=turn_id,
            timestamp=timestamp,
            user_input=user_input,
            intent_type=intent_type,
            policy_used=policy_used,
            response_summary=response_summary,
            context_snapshot=context_snapshot,
            relevance_score=relevance_score
        )
        
        # 히스토리에 추가 (최대 개수 유지)
        if len(session.conversation_history) >= self.max_history:
            session.conversation_history.pop(0)
        session.conversation_history.append(turn)
        
        # 세션 메타데이터 업데이트
        session.last_active = timestamp
        session.metadata['turn_count'] = len(session.conversation_history)
        
        # 누적 컨텍스트 업데이트
        self._update_accumulated_context(session, turn)
        
        return turn
    
    def get_conversation_history(self, session_id: str, 
                                 lookback: int = 5) -> List[ConversationTurn]:
        """
        대화 히스토리 조회
        
        Args:
            session_id: 세션 ID
            lookback: 조회할 최근 턴 수
            
        Returns:
        ConversationTurn 리스트
        """
        if session_id not in self.sessions:
            return []
        
        history = self.sessions[session_id].conversation_history
        return history[-lookback:] if len(history) > lookback else history
    
    def get_relevant_context(self, session_id: str, 
                            current_input: str,
                            current_intent: str,
                            top_k: int = 3) -> List[Tuple[ConversationTurn, float]]:
        """
        관련성 높은 컨텍스트 검색
        
        Args:
            session_id: 세션 ID
            current_input: 현재 입력
            current_intent: 현재 의도
            top_k: 반환할 상위 컨텍스트 수
            
        Returns:
            (ConversationTurn, relevance_score) 튜플 리스트
        """
        if session_id not in self.sessions:
            return []
        
        session = self.sessions[session_id]
        scored_contexts = []
        
        current_time = datetime.now()
        
        for turn in session.conversation_history[:-1]:  # 현재 턴 제외
            # 시간 감쇠 점수
            turn_time = datetime.fromisoformat(turn.timestamp)
            hours_diff = (current_time - turn_time).total_seconds() / 3600
            time_score = max(0, 1 - (hours_diff / self.relevance_config['time_decay_hours']))
            
            # 키워드 유사도
            keyword_score = self._calculate_keyword_similarity(
                current_input, turn.user_input
            )
            
            # 의도 일치도
            intent_score = 1.0 if turn.intent_type == current_intent else 0.0
            
            # 종합 관련성 점수
            relevance = (
                self.relevance_config['time_decay_hours'] * time_score +
                self.relevance_config['keyword_weight'] * keyword_score +
                self.relevance_config['intent_weight'] * intent_score
            )
            
            if relevance >= self.relevance_config['min_relevance_threshold']:
                scored_contexts.append((turn, relevance))
        
        # 점수 기준 정렬 및 상위 k개 반환
        scored_contexts.sort(key=lambda x: x[1], reverse=True)
        return scored_contexts[:top_k]
    
    def cleanup_context(self, session_id: Optional[str] = None,
                       max_age_hours: Optional[float] = None) -> Dict[str, Any]:
        """
        컨텍스트 정리
        
        Args:
            session_id: 특정 세션 ID (None이면 모든 세션)
            max_age_hours: 최대 보존 시간 (시간)
            
        Returns:
            정리 결과 정보
        """
        if max_age_hours is None:
            max_age_hours = 24.0  # 기본 24시간
        
        cleanup_info = {
            'sessions_cleaned': 0,
            'turns_removed': 0,
            'sessions_affected': []
        }
        
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=max_age_hours)
        
        if session_id:
            # 특정 세션만 정리
            if session_id in self.sessions:
                session = self.sessions[session_id]
                last_active = datetime.fromisoformat(session.last_active)
                
                if last_active < cutoff_time:
                    del self.sessions[session_id]
                    cleanup_info['sessions_cleaned'] += 1
                    cleanup_info['sessions_affected'].append(session_id)
        else:
            # 모든 세션 정리
            sessions_to_remove = []
            for sid, session in self.sessions.items():
                last_active = datetime.fromisoformat(session.last_active)
                
                if last_active < cutoff_time:
                    sessions_to_remove.append(sid)
                else:
                    # 세션은 유지하되 오래된 턴 제거
                    original_count = len(session.conversation_history)
                    cutoff_timestamp = cutoff_time.isoformat()
                    session.conversation_history = [
                        turn for turn in session.conversation_history
                        if turn.timestamp > cutoff_timestamp
                    ]
                    removed = original_count - len(session.conversation_history)
                    if removed > 0:
                        cleanup_info['turns_removed'] += removed
                        cleanup_info['sessions_affected'].append(sid)
            
            # 오래된 세션 삭제
            for sid in sessions_to_remove:
                del self.sessions[sid]
                cleanup_info['sessions_cleaned'] += 1
                cleanup_info['sessions_affected'].append(sid)
        
        return cleanup_info
    
    def save_session_persistence(self, session_id: Optional[str] = None) -> bool:
        """
        세션 지속성 저장
        
        Args:
            session_id: 특정 세션 ID (None이면 모든 세션)
            
        Returns:
            저장 성공 여부
        """
        try:
            # 저장 디렉토리 확인
            os.makedirs(os.path.dirname(self.context_file_path), exist_ok=True)
            
            # 저장할 데이터 준비
            if session_id:
                if session_id not in self.sessions:
                    return False
                data_to_save = {
                    session_id: self._session_to_dict(self.sessions[session_id])
                }
            else:
                data_to_save = {
                    sid: self._session_to_dict(session)
                    for sid, session in self.sessions.items()
                }
            
            # 기존 데이터 로드 및 병합
            existing_data = {}
            if os.path.exists(self.context_file_path):
                try:
                    with open(self.context_file_path, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except Exception:
                    pass
            
            # 병합 및 저장
            existing_data.update(data_to_save)
            with open(self.context_file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"세션 저장 오류: {e}")
            return False
    
    def load_session_persistence(self, session_id: Optional[str] = None) -> bool:
        """
        저장된 세션 로드
        
        Args:
            session_id: 특정 세션 ID (None이면 모든 세션)
            
        Returns:
            로드 성공 여부
        """
        try:
            if not os.path.exists(self.context_file_path):
                return False
            
            with open(self.context_file_path, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            
            if session_id:
                if session_id in saved_data:
                    self.sessions[session_id] = self._dict_to_session(saved_data[session_id])
                    return True
                return False
            else:
                for sid, session_dict in saved_data.items():
                    self.sessions[sid] = self._dict_to_session(session_dict)
                return True
                
        except Exception as e:
            print(f"세션 로드 오류: {e}")
            return False
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """세션 정보 조회"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        return {
            'session_id': session.session_id,
            'created_at': session.created_at,
            'last_active': session.last_active,
            'turn_count': len(session.conversation_history),
            'metadata': session.metadata,
            'accumulated_context_keys': list(session.accumulated_context.keys())
        }
    
    def list_sessions(self) -> List[str]:
        """모든 세션 ID 목록"""
        return list(self.sessions.keys())
    
    def delete_session(self, session_id: str) -> bool:
        """세션 삭제"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def _calculate_relevance(self, session: SessionContext,
                            current_input: str,
                            current_intent: str) -> float:
        """현재 입력과 세션의 관련성 계산"""
        if not session.conversation_history:
            return 0.0
        
        last_turn = session.conversation_history[-1]
        
        # 시간 경과
        last_time = datetime.fromisoformat(last_turn.timestamp)
        current_time = datetime.now()
        hours_diff = (current_time - last_time).total_seconds() / 3600
        
        if hours_diff > self.relevance_config['time_decay_hours']:
            return 0.0
        
        # 키워드 유사도
        keyword_sim = self._calculate_keyword_similarity(
            current_input, last_turn.user_input
        )
        
        # 의도 일치
        intent_match = 1.0 if last_turn.intent_type == current_intent else 0.3
        
        # 종합 점수
        relevance = (keyword_sim + intent_match) / 2
        return min(1.0, relevance)
    
    def _calculate_keyword_similarity(self, text1: str, text2: str) -> float:
        """두 텍스트 간 키워드 유사도 계산"""
        # 간단한 키워드 추출 (2글자 이상 단어)
        def extract_keywords(text):
            words = text.lower().split()
            return set(w for w in words if len(w) >= 2)
        
        keywords1 = extract_keywords(text1)
        keywords2 = extract_keywords(text2)
        
        if not keywords1 or not keywords2:
            return 0.0
        
        # 자카드 유사도
        intersection = len(keywords1 & keywords2)
        union = len(keywords1 | keywords2)
        
        return intersection / union if union > 0 else 0.0
    
    def _update_accumulated_context(self, session: SessionContext, 
                                    turn: ConversationTurn):
        """누적 컨텍스트 업데이트"""
        # 언어 정보 누적
        if 'detected_languages' in turn.context_snapshot:
            langs = turn.context_snapshot['detected_languages']
            current_langs = session.accumulated_context.get('languages', [])
            session.accumulated_context['languages'] = list(set(current_langs + langs))
        
        # 프레임워크 정보 누적
        if 'detected_frameworks' in turn.context_snapshot:
            frameworks = turn.context_snapshot['detected_frameworks']
            current_fws = session.accumulated_context.get('frameworks', [])
            session.accumulated_context['frameworks'] = list(set(current_fws + frameworks))
        
        # 자주 사용된 의도 추적
        intent = turn.intent_type
        intent_counts = session.accumulated_context.get('intent_counts', {})
        intent_counts[intent] = intent_counts.get(intent, 0) + 1
        session.accumulated_context['intent_counts'] = intent_counts
        session.accumulated_context['dominant_intent'] = max(
            intent_counts.items(), key=lambda x: x[1]
        )[0] if intent_counts else None
    
    def _load_contexts(self):
        """초기화 시 저장된 컨텍스트 로드"""
        self.load_session_persistence()
    
    def _session_to_dict(self, session: SessionContext) -> Dict[str, Any]:
        """SessionContext를 딕셔너리로 변환"""
        return {
            'session_id': session.session_id,
            'created_at': session.created_at,
            'last_active': session.last_active,
            'conversation_history': [
                {
                    'turn_id': turn.turn_id,
                    'timestamp': turn.timestamp,
                    'user_input': turn.user_input,
                    'intent_type': turn.intent_type,
                    'policy_used': turn.policy_used,
                    'response_summary': turn.response_summary,
                    'context_snapshot': turn.context_snapshot,
                    'relevance_score': turn.relevance_score,
                    'feedback': turn.feedback
                }
                for turn in session.conversation_history
            ],
            'accumulated_context': session.accumulated_context,
            'metadata': session.metadata
        }
    
    def _dict_to_session(self, data: Dict[str, Any]) -> SessionContext:
        """딕셔너리를 SessionContext로 변환"""
        return SessionContext(
            session_id=data['session_id'],
            created_at=data['created_at'],
            last_active=data['last_active'],
            conversation_history=[
                ConversationTurn(
                    turn_id=turn['turn_id'],
                    timestamp=turn['timestamp'],
                    user_input=turn['user_input'],
                    intent_type=turn['intent_type'],
                    policy_used=turn['policy_used'],
                    response_summary=turn['response_summary'],
                    context_snapshot=turn['context_snapshot'],
                    relevance_score=turn.get('relevance_score', 0.0),
                    feedback=turn.get('feedback')
                )
                for turn in data.get('conversation_history', [])
            ],
            accumulated_context=data.get('accumulated_context', {}),
            metadata=data.get('metadata', {})
        )


def build_context(query: str = "", payload: Dict = None, 
                 request: Dict = None, data: Dict = None) -> Dict[str, Any]:
    """
    기본 컨텍스트 빌더 (하위 호환성 유지)
    
    Args:
        query: 쿼리 문자열
        payload: 페이로드 데이터
        request: 요청 데이터
        data: 추가 데이터
        
    Returns:
        기본 컨텍스트 딕셔너리
    """
    return {
        "query": query or "test query",
        "payload": payload or {},
        "request": request or {},
        "data": data or {},
        "timestamp": datetime.now().isoformat()
    }

