#!/usr/bin/env python3
"""
AI Router CLI - Full 1.x Integration
기존 AI Router의 모든 기능 통합 (다중 에이전트, 평가, 정책 진화, 자가 수정 등)

사용법:
  python3 cli_full_integration.py              # 기본: 더미 모드 (빠른 테스트)
  python3 cli_full_integration.py --local-ai   # 로컬 AI 사용 (실제 Ollama)
  python3 cli_full_integration.py --dummy-1    # 더미 응답 1
  python3 cli_full_integration.py --dummy-2    # 더미 응답 2
"""

import sys
import os
import argparse
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 테스트 모드 설정 (임포트 전에 설정)
from core.test_policy import set_test_mode, TestMode

# 명령줄 인자 파싱
parser = argparse.ArgumentParser(description='AI Router CLI')
parser.add_argument('--local-ai', action='store_true', help='로컬 AI 사용 (Ollama)')
parser.add_argument('--dummy-1', action='store_true', help='더미 모드 1')
parser.add_argument('--dummy-2', action='store_true', help='더미 모드 2')
parser.add_argument('--test', choices=['local-ai', 'dummy-1', 'dummy-2'], 
                    help='테스트 모드 선택 (local-ai, dummy-1, dummy-2)')
args = parser.parse_args()

# 테스트 모드 설정
if args.local_ai or args.test == 'local-ai':
    set_test_mode(TestMode.LOCAL_AI)
    print("🔧 테스트 모드: 로컬 AI (Ollama)")
elif args.dummy_1 or args.test == 'dummy-1':
    set_test_mode(TestMode.DUMMY_1)
    print("🔧 테스트 모드: 더미 응답 1")
elif args.dummy_2 or args.test == 'dummy-2':
    set_test_mode(TestMode.DUMMY_2)
    print("🔧 테스트 모드: 더미 응답 2")
else:
    set_test_mode(TestMode.LOCAL_AI)  # 기본: 로컬 AI
    print("🔧 테스트 모드: 로컬 AI (Ollama) - 기본값")

# 기존 1.x 코어 모듈 임포트
from core.agents import run_agents
from core.evaluator import evaluate
from core.memory import save, get_recent
from core.reward import calc_reward
from core.policy_evolve import next_generation
from core.rag import search, build_full_graph

# 새로운 지능/툴 레이어 임포트
from core.intent import IntentParser
from core.intent_integration import IntentBasedRouter
from core.decision import DecisionEngine, DecisionType
from core.context import ContextTracker
from core.tools.log_integration_extended import SystemLogIntegration
from core.tools.system_tool import SystemTool
from core.tools.file_tool import FileTool

from core.ai import ai_call
from core.test_policy import set_test_mode, TestMode

class AIFullRouterCLI:
    """AI Router CLI - 완전 통합 버전"""
    
    def __init__(self):
        # 테스트 모드 유지 (명령줄 인자에서 설정된 모드)
        from core.test_policy import get_current_mode
        current_mode = get_current_mode()
        print(f"✅ 현재 테스트 모드: {current_mode}")
        
        # 1.x 기초 시스템 초기화 (함수 기반)
        
        # 지능 레이어 초기화
        self.intent_parser = IntentParser()
        self.intent_router = IntentBasedRouter()
        self.decision_engine = DecisionEngine()
        self.context_tracker = ContextTracker()
        
        # 툴 레이어 초기화
        self.log_integration = SystemLogIntegration()
        self.system_tool = SystemTool()
        self.file_tool = FileTool()
        
        # 권한 설정
        self.log_integration.grant_permissions(
            agent_id='cli_full',
            log_types=['syslog', 'daemon', 'kern', 'boot'],
            read_only=True,
            max_lines=200
        )
        
        # 세션 설정
        self.session_id = self.context_tracker.create_session("cli_session")
        self.conversation_turn = 0
        
        print("✅ AI Router Full Integration 초기화 완료")
        print(f"   - 세션 ID: {self.session_id}")
        print(f"   - 다중 에이전트: refine/balance/expand (run_agents)")
        print(f"   - 사용 가능 툴: 로그, 시스템, 파일")
    
    def process_with_full_pipeline(self, user_input: str) -> str:
        """
        완전한 AI Router 파이프라인으로 처리
        
        1. 의도 분석 (Intent Parser)
        2. 의도 통합 (Intent Integration - 라우팅)
        3. 컨텍스트 관리 (Context Tracker)
        4. 다중 에이전트 경쟁 (Agents)
        5. 의사결정 엔진 (Decision Engine)
        6. 툴 실행 (Log/System/File)
        7. 평가 시스템 (Evaluator)
        8. 메모리 저장 (Memory)
        9. 보상 계산 (Reward)
        10. AI 응답 생성
        """
        self.conversation_turn += 1
        print(f"\n{'='*60}")
        print(f"🔄 턴 {self.conversation_turn}: {user_input[:50]}...")
        print(f"{'='*60}")
        
        # 1. 의도 분석
        print("\n1️⃣ 의도 분석 (Intent Parser)")
        intent = self.intent_parser.parse(user_input)
        print(f"   의도: {intent.intent_type.value} (신뢰도: {intent.confidence:.2f})")
        print(f"   키워드: {intent.keywords[:3]}")
        
        # 2. 의도 통합 (라우팅)
        print("\n2️⃣ 의도 통합 (Intent Integration)")
        routing = self.intent_router.recognize_intent_and_route(user_input)
        selected_policy = routing['routing']['selected_policy']
        print(f"   선택된 정책: {selected_policy}")
        print(f"   라우팅 신뢰도: {routing['routing']['confidence']:.2f}")
        
        # 3. 컨텍스트 관리
        print("\n3️⃣ 컨텍스트 관리 (Context Tracker)")
        # 세션 정보 표시
        session_info = self.context_tracker.get_session_info(self.session_id)
        if session_info:
            print(f"   세션 턴 수: {session_info.get('turn_count', 0)}")
        
        # 4. 다중 에이전트 경쟁
        print("\n4️⃣ 다중 에이전트 경쟁 (Agents)")
        available_agents = ['refine', 'balance', 'expand']
        agent_scores = {}
        
        for agent_policy in available_agents:
            # 정책별 점수 계산
            score = self._calculate_agent_score(agent_policy, intent, selected_policy)
            agent_scores[agent_policy] = score
            print(f"   {agent_policy}: {score:.2f}점")
        
        winner = max(agent_scores, key=agent_scores.get)
        winner_score = agent_scores[winner]
        print(f"   🏆 승자: {winner} ({winner_score:.2f}점)")
        
        # 실제 run_agents 함수 사용 (핵심 1.x 기능)
        try:
            print("   🔄 run_agents() 실행 중...")
            winner_result, all_results = run_agents(ai_call, user_input)
            print(f"   ✅ 에이전트 실행 완료: {len(all_results)}개 결과")
        except Exception as e:
            print(f"   ⚠️ run_agents 오류: {e}")
        
        # 5. 의사결정 엔진
        print("\n5️⃣ 의사결정 엔진 (Decision Engine)")
        options = [
            {'name': 'log_analysis', 'scores': {'relevance': 0.8 if self._is_log_query(user_input) else 0.2}},
            {'name': 'system_status', 'scores': {'relevance': 0.8 if self._is_status_query(user_input) else 0.2}},
            {'name': 'general_chat', 'scores': {'relevance': 0.5}},
        ]
        
        decision = self.decision_engine.make_decision(
            options=options,
            decision_type=DecisionType.ROUTING
        )
        print(f"   결정: {decision.chosen_option} (신뢰도: {decision.confidence:.2f})")
        
        # 6. 툴 실행
        print("\n6️⃣ 툴 실행 (Tool Layer)")
        tool_result = None
        
        if decision.chosen_option == 'log_analysis' or self._is_log_query(user_input):
            print("   📋 로그 분석 실행")
            tool_result = self._execute_log_tool(user_input)
        elif decision.chosen_option == 'system_status' or self._is_status_query(user_input):
            print("   🖥️ 시스템 상태 확인")
            tool_result = self._execute_system_tool(user_input)
        else:
            print("   💬 일반 대화")
            tool_result = {'type': 'chat', 'data': None}
        
        # 7. 평가 시스템
        print("\n7️⃣ 평가 시스템 (Evaluator)")
        # 간단한 평가
        if tool_result:
            score = 8.5 if tool_result.get('success', False) else 5.0
            print(f"   점수: {score}/10")
        
        # 8. 메모리 저장
        print("\n8️⃣ 메모리 저장 (Memory)")
        self._save_to_memory(user_input, tool_result, winner)
        print("   저장 완료")
        
        # 9. 보상 계산
        print("\n9️⃣ 보상 계산 (Reward)")
        if tool_result and tool_result.get('score'):
            reward = calc_reward(tool_result.get('score', 0))
            print(f"   보상 점수: {reward:.2f}")
        else:
            print("   보상: 기본값")
        
        # 10. AI 응답 생성
        print("\n🔟 AI 응답 생성 (Ollama)")
        response = self._generate_ai_response(user_input, tool_result, winner)
        
        # 턴 저장
        self._save_conversation_turn(user_input, response, winner, tool_result)
        
        return response
    
    def _is_log_query(self, text):
        # 공백 제거한 텍스트에서도 검색
        text_no_space = text.replace(' ', '').lower()
        keywords = ['로그', 'log', 'syslog', '에러', 'error', '로그보여', '로그확인', '로그분석']
        # 공백 있는 원본과 제거한 버전 모두 검색
        return any(kw in text.lower() or kw in text_no_space for kw in keywords)
    
    def _is_status_query(self, text):
        # 공백 제거한 텍스트에서도 검색
        text_no_space = text.replace(' ', '').lower()
        keywords = [
            '상태', 'status', 'cpu', '메모리', 'memory', '어때',
            '시스템', 'system', '리소스', 'resource', '사용량',
            '시스템상태', '상태확인', 'cpu사용량', '메모리사용량',
            '부하', 'load', '성능', 'performance'
        ]
        # 공백 있는 원본과 제거한 버전 모두 검색
        return any(kw in text.lower() or kw in text_no_space for kw in keywords)
    
    def _calculate_agent_score(self, agent_policy, intent, selected_policy):
        """에이전트 점수 계산"""
        base_score = 5.0
        
        # 정책 일치 보너스
        if agent_policy == selected_policy:
            base_score += 3.0
        
        # 의도 기반 보너스
        if intent.intent_type.value in ['debugging', 'analysis'] and agent_policy == 'refine':
            base_score += 1.5
        elif intent.intent_type.value in ['question', 'explanation'] and agent_policy == 'expand':
            base_score += 1.5
        
        # 신뢰도 가중치
        base_score *= intent.confidence
        
        return min(10.0, base_score)
    
    def _execute_log_tool(self, user_input):
        """로그 툴 실행"""
        result = self.log_integration.get_system_log_access(
            agent_id='cli_full',
            log_types=['syslog'],
            lines=30
        )
        
        errors = self.log_integration.analyze_system_errors(
            agent_id='cli_full',
            hours=1,
            severity='error'
        )
        
        return {
            'success': result.get('success', False),
            'type': 'log',
            'logs': result.get('logs_accessed', {}),
            'errors': errors.get('total_errors', 0),
            'error_types': errors.get('error_types', {})
        }
    
    def _execute_system_tool(self, user_input):
        """시스템 툴 실행"""
        cpu = self.system_tool.get_cpu_info()
        memory = self.system_tool.get_memory_info()
        disk = self.system_tool.get_disk_info()
        
        return {
            'success': True,
            'type': 'system',
            'cpu': cpu.get('cpu', {}),
            'memory': memory.get('memory', {}),
            'disk': disk.get('root_partition', {})
        }
    
    def _save_to_memory(self, user_input, result, winner):
        """메모리에 저장"""
        try:
            from datetime import datetime
            entry = {
                'timestamp': datetime.now().isoformat(),
                'input': user_input[:100],
                'winner': winner,
                'score': result.get('score', 0) if result else 0,
                'success': result.get('success', False) if result else False
            }
            save(entry)
        except:
            pass
    
    def _calculate_reward(self, tool_result):
        """보상 계산"""
        score = tool_result.get('score', 0) if tool_result else 0
        return calc_reward(score)
    
    def _generate_ai_response(self, user_input, tool_result, winner):
        """AI 응답 생성 (스트리밍)"""
        # 프롬프트 구성
        context_parts = [f"승자 에이전트: {winner}"]
        
        if tool_result:
            if tool_result.get('type') == 'log':
                context_parts.append(f"로그 분석 결과:")
                context_parts.append(f"- 최근 에러: {tool_result.get('errors', 0)}개")
                context_parts.append(f"- 에러 유형: {tool_result.get('error_types', {})}")
            elif tool_result.get('type') == 'system':
                cpu = tool_result.get('cpu', {})
                mem = tool_result.get('memory', {})
                context_parts.append(f"시스템 상태:")
                context_parts.append(f"- CPU: {cpu.get('percent', 0)}% ({cpu.get('status', 'unknown')})")
                context_parts.append(f"- 메모리: {mem.get('percent_used', 0)}% 사용 중")
        
        prompt = f"""사용자: {user_input}

AI Router 분석 결과:
{chr(10).join(context_parts)}

위 정보를 바탕으로 사용자에게 한국어로 친절하게 답변해주세요.
시스템 문제가 있으면 해결책도 제안해주세요."""
        
        try:
            # 테스트 모드 확인
            from core.test_policy import get_test_policy
            test_policy = get_test_policy()
            is_dummy = test_policy.should_use_dummy()
            current_mode = test_policy.get_test_mode()
            print(f"\n🔍 [디버그] 테스트 모드: {current_mode}, 더미모드: {is_dummy}")
            
            # AI에 전달되는 프롬프트 표시
            print(f"\n📤 AI에 전달되는 프롬프트 ({len(prompt)} 글자):")
            print("-" * 60)
            print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
            print("-" * 60)
            
            print("\n🤖 AI 응답 (실시간):\n")
            print("   ", end='', flush=True)  # 들여쓰기
            
            # 스트리밍 모드로 AI 호출
            response = ai_call(prompt, stream=True)
            return response
        except Exception as e:
            return f"죄송합니다. 응답 생성 중 오류가 발생했습니다: {str(e)[:100]}"
    
    def _save_conversation_turn(self, user_input, response, winner, tool_result):
        """대화 턴 저장"""
        try:
            from datetime import datetime
            self.context_tracker.add_conversation_turn(
                session_id=self.session_id,
                user_input=user_input,
                intent_type='interaction',
                policy_used=winner,
                response_summary=response[:100],
                context_snapshot={
                    'tool_type': tool_result.get('type', 'none') if tool_result else 'none',
                    'success': tool_result.get('success', False) if tool_result else False
                }
            )
        except:
            pass
    
    def show_statistics(self):
        """통계 표시"""
        print(f"\n{'='*60}")
        print("📊 AI Router 통계")
        print(f"{'='*60}")
        
        # 세션 정보
        info = self.context_tracker.get_session_info(self.session_id)
        if info:
            print(f"세션 ID: {info['session_id']}")
            print(f"대화 턴: {info['turn_count']}")
        
        print(f"총 대화 턴: {self.conversation_turn}")
        print(f"{'='*60}\n")
    
    def run(self):
        """메인 실행 루프"""
        print("\n" + "="*60)
        print("🤖 AI Router CLI - Full Integration")
        print("="*60)
        print("모든 1.x 기능 통합:")
        print("  - 다중 에이전트 경쟁 (refine/balance/expand)")
        print("  - 평가 시스템 (1-10점)")
        print("  - 메모리 & 보상 시스템")
        print("  - 의도 분석 및 라우팅")
        print("  - 로그/시스템 툴")
        print("\n명령어:")
        print("  '로그 보여줘'  - 시스템 로그 분석")
        print("  '상태 어때?'   - 시스템 상태 확인")
        print("  'stats'        - 통계 보기")
        print("  'quit'         - 종료")
        print("="*60 + "\n")
        
        while True:
            try:
                user_input = input("👤 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 안녕히 가세요!")
                    self.show_statistics()
                    break
                
                if user_input.lower() == 'stats':
                    self.show_statistics()
                    continue
                
                # 완전 파이프라인으로 처리
                response = self.process_with_full_pipeline(user_input)
                print(f"\n🤖 AI: {response}\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 안녕히 가세요!")
                break
            except EOFError:
                break
            except Exception as e:
                print(f"\n❌ 오류 발생: {e}\n")

if __name__ == "__main__":
    from datetime import datetime
    cli = AIFullRouterCLI()
    cli.run()
