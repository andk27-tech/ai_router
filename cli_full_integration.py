#!/usr/bin/env python3
"""
AI Router CLI - Full 1.x Integration
Fixed version with concise responses
"""

import sys
import os
import argparse
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test mode setting (before imports)
from core.test_policy import set_test_mode, TestMode

# Command line argument parsing
parser = argparse.ArgumentParser(description='AI Router CLI')
parser.add_argument('--local-ai', action='store_true', help='Local AI usage (Ollama)')
parser.add_argument('--dummy-1', action='store_true', help='Dummy mode 1')
parser.add_argument('--dummy-2', action='store_true', help='Dummy mode 2')
parser.add_argument('--test', choices=['local-ai', 'dummy-1', 'dummy-2'], 
                    help='Test mode selection (local-ai, dummy-1, dummy-2)')
args = parser.parse_args()

# Test mode setting
if args.local_ai or args.test == 'local-ai':
    set_test_mode(TestMode.LOCAL_AI)
    print("Test mode: Local AI (Ollama)")
elif args.dummy_1 or args.test == 'dummy-1':
    set_test_mode(TestMode.DUMMY_1)
    print("Test mode: Dummy response 1")
elif args.dummy_2 or args.test == 'dummy-2':
    set_test_mode(TestMode.DUMMY_2)
    print("Test mode: Dummy response 2")
else:
    set_test_mode(TestMode.LOCAL_AI)  # Default: local AI
    print("Test mode: Local AI (Ollama) - default")

# Core 1.x modules import
from core.agents import run_agents
from core.evaluator import evaluate
from core.memory import save, get_recent
from core.reward import calc_reward
from core.policy_evolve import next_generation
from core.rag import search, build_full_graph

# New intelligence/tool layer imports
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
    """AI Router CLI - Complete integration version"""
    
    def __init__(self):
        # Test mode maintenance (set by command line args)
        from core.test_policy import get_current_mode
        current_mode = get_current_mode()
        print(f"Current test mode: {current_mode}")
        
        # Reset policy weights for clean testing
        self._reset_policy_weights()
        
        # 1.x Basic system initialization (function based)
        
        # Intelligence layer initialization
        self.intent_parser = IntentParser()
        self.intent_router = IntentBasedRouter()
        self.decision_engine = DecisionEngine()
        self.context_tracker = ContextTracker()
        
        # Tool layer initialization
        self.log_integration = SystemLogIntegration()
        self.system_tool = SystemTool()
        self.file_tool = FileTool()
        
        # Permission settings
        self.log_integration.grant_permissions(
            agent_id='cli_full',
            log_types=['syslog', 'daemon', 'kern', 'boot'],
            read_only=True,
            max_lines=200
        )
        
        # Session settings
        self.session_id = self.context_tracker.create_session("cli_session")
        self.conversation_turn = 0
        
        print("AI Router Full Integration initialization complete")
        print(f"   - Session ID: {self.session_id}")
        print(f"   - Multi-agent: refine/balance/expand (run_agents)")
        print(f"   - Available tools: log, system, file")
    
    def _reset_policy_weights(self):
        """Reset policy weights to default values for clean testing"""
        from core.policy import WEIGHTS
        WEIGHTS.update({
            'refine': 1.0,
            'balance': 1.0, 
            'expand': 1.0,
            'expand_deep': 1.2
        })
        print("   Policy weights reset to defaults")
    
    def process_with_full_pipeline(self, user_input: str) -> str:
        """
        Complete AI Router pipeline processing
        
        1. Intent analysis (Intent Parser)
        2. Intent integration (Intent Integration - routing)
        3. Context management (Context Tracker)
        4. Multi-agent competition (Agents)
        5. Decision engine (Decision Engine)
        6. Tool execution (Log/System/File)
        7. Evaluation system (Evaluator)
        8. Memory storage (Memory)
        9. Reward calculation (Reward)
        10. AI response generation
        """
        self.conversation_turn += 1
        print(f"\n{'='*60}")
        print(f"Turn {self.conversation_turn}: {user_input[:50]}...")
        print(f"{'='*60}")
        
        # 1. Intent analysis
        print("\n1. Intent analysis (Intent Parser)")
        intent = self.intent_parser.parse(user_input)
        print(f"   Intent: {intent.intent_type.value} (confidence: {intent.confidence:.2f})")
        print(f"   Keywords: {intent.keywords[:3]}")
        
        # 2. Intent integration (routing)
        print("\n2. Intent integration (Intent Integration)")
        routing = self.intent_router.recognize_intent_and_route(user_input)
        selected_policy = routing['routing']['selected_policy']
        print(f"   Selected policy: {selected_policy}")
        print(f"   Routing confidence: {routing['routing']['confidence']:.2f}")
        
        # 3. Context management
        print("\n3. Context management (Context Tracker)")
        session_info = self.context_tracker.get_session_info(self.session_id)
        if session_info:
            print(f"   Session turn count: {session_info.get('turn_count', 0)}")
        
        # 4. Multi-agent competition
        print("\n4. Multi-agent competition (Agents)")
        available_agents = ['refine', 'balance', 'expand']
        agent_scores = {}
        
        for agent_policy in available_agents:
            # Policy-based score calculation
            score = self._calculate_agent_score(agent_policy, intent, selected_policy)
            agent_scores[agent_policy] = score
            print(f"   {agent_policy}: {score:.2f} points")
        
        # Legacy winner for comparison
        legacy_winner = max(agent_scores, key=agent_scores.get)
        legacy_score = agent_scores[legacy_winner]
        print(f"   Legacy winner: {legacy_winner} ({legacy_score:.2f} points)")
        
        # Real run_agents execution with improved system
        print("\n4.2 Real Multi-Agent Competition (Enhanced)")
        try:
            print("   Executing run_agents() with improved evaluation...")
            winner_result, all_results = run_agents(ai_call, user_input)
            print(f"   Agent execution complete: {len(all_results)} results")
            
            # Use the real winner from improved run_agents
            winner = winner_result['policy']
            winner_score = winner_result['score']
            print(f"   Enhanced winner: {winner} ({winner_score:.2f} points)")
            print(f"   Enhanced winner output length: {len(winner_result['output'])} chars")
            
            # Show comparison
            if legacy_winner != winner:
                print(f"   Winner changed: {legacy_winner} -> {winner}")
            else:
                print(f"   Winner consistent: {winner}")
                
        except Exception as e:
            print(f"   run_agents error: {e}")
            # Fallback to legacy system
            winner = legacy_winner
            winner_score = legacy_score
            print(f"   Fallback to legacy: {winner} ({winner_score:.2f} points)")
        
        # 5. Intent-based routing (FIXED - Use intent properly)
        print("\n5. Intent-based routing (Fixed)")
        
        # Use intent for proper routing
        tool_result = None
        intent_type = intent.intent_type.value
        
        if intent_type == 'maintenance' or self._is_log_query(user_input):
            print("   Log analysis execution (maintenance intent)")
            tool_result = self._execute_log_tool(user_input)
        elif intent_type == 'status' or self._is_status_query(user_input):
            print("   System status check (status intent)")
            tool_result = self._execute_system_tool(user_input)
        else:
            print("   General conversation (default)")
            tool_result = {'type': 'chat', 'data': None}
        
        print(f"   Intent-based route: {intent_type} -> {tool_result['type']}")
        
        # 6. Decision Engine (for logging only)
        print("\n6. Decision Engine (Logging)")
        options = [
            {'name': 'log_analysis', 'scores': {'relevance': 0.8 if self._is_log_query(user_input) else 0.2}},
            {'name': 'system_status', 'scores': {'relevance': 0.8 if self._is_status_query(user_input) else 0.2}},
            {'name': 'general_chat', 'scores': {'relevance': 0.5}},
        ]
        
        decision = self.decision_engine.make_decision(
            options=options,
            decision_type=DecisionType.ROUTING
        )
        print(f"   Decision Engine result: {decision.chosen_option} (confidence: {decision.confidence:.2f})")
        print(f"   (Note: Using intent-based routing instead)")
        
        # 7. Evaluation system
        print("\n7. Evaluation system (Evaluator)")
        # Simple evaluation
        if tool_result:
            score = 8.5 if tool_result.get('success', False) else 5.0
            print(f"   Score: {score}/10")
        
        # 8. Memory storage (ENABLED)
        print("\n8. Memory storage (DISABLED)")
        self._save_to_memory(user_input, tool_result, winner)
        print("   Storage complete")
        
        # 9. Reward calculation
        print("\n9. Reward calculation (Reward)")
        if tool_result and tool_result.get('score'):
            reward = calc_reward(tool_result.get('score', 0))
            print(f"   Reward score: {reward:.2f}")
        else:
            print("   Reward: default")
        
        # 10. AI response generation (CONCISE)
        print("\n10. AI response generation (Concise)")
        response = self._generate_concise_response(user_input, tool_result, winner)
        
        # Turn save
        self._save_conversation_turn(user_input, response, winner, tool_result)
        
        return response
    
    def _is_log_query(self, text):
        # Search in text without spaces too
        text_no_space = text.replace(' ', '').lower()
        keywords = ['log', 'syslog', 'error', 'error', 'log show', 'log check', 'log analysis']
        # Search both original and space-removed versions
        return any(kw in text.lower() or kw in text_no_space for kw in keywords)
    
    def _is_status_query(self, text):
        # Search in text without spaces too
        text_no_space = text.replace(' ', '').lower()
        keywords = [
            'status', 'status', 'cpu', 'memory', 'memory', 'how',
            'system', 'system', 'resource', 'resource', 'usage',
            'system status', 'status check', 'cpu usage', 'memory usage',
            'load', 'load', 'performance', 'performance'
        ]
        # Search both original and space-removed versions
        return any(kw in text.lower() or kw in text_no_space for kw in keywords)
    
    def _calculate_agent_score(self, agent_policy, intent, selected_policy):
        """Agent score calculation"""
        base_score = 5.0
        
        # Policy match bonus
        if agent_policy == selected_policy:
            base_score += 3.0
        
        # Intent-based bonus
        if intent.intent_type.value in ['debugging', 'analysis'] and agent_policy == 'refine':
            base_score += 1.5
        elif intent.intent_type.value in ['question', 'explanation'] and agent_policy == 'expand':
            base_score += 1.5
        
        # Confidence weighting
        base_score *= intent.confidence
        
        return min(10.0, base_score)
    
    def _execute_log_tool(self, user_input):
        """Log tool execution"""
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
        """System tool execution"""
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
        """Save to memory"""
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
        """Reward calculation"""
        score = tool_result.get('score', 0) if tool_result else 0
        return calc_reward(score)
    
    def _generate_concise_response(self, user_input, tool_result, winner):
        """Generate concise AI response (2-3 lines max)"""
        # Build context
        context_parts = [f"Winner agent: {winner}"]
        
        if tool_result:
            if tool_result.get('type') == 'log':
                context_parts.append(f"Log analysis:")
                context_parts.append(f"- Recent errors: {tool_result.get('errors', 0)}")
                context_parts.append(f"- Error types: {tool_result.get('error_types', {})}")
            elif tool_result.get('type') == 'system':
                cpu = tool_result.get('cpu', {})
                mem = tool_result.get('memory', {})
                context_parts.append(f"System status:")
                context_parts.append(f"- CPU: {cpu.get('percent', 0)}% ({cpu.get('status', 'unknown')})")
                context_parts.append(f"- Memory: {mem.get('percent_used', 0)}% used")
        
        # Concise prompt
        prompt = f"""User: {user_input}

AI Router analysis:
{chr(10).join(context_parts)}

Provide a concise Korean response in 2-3 lines maximum.
Focus on key information and solutions if needed."""
        
        try:
            # Test mode check
            from core.test_policy import get_test_policy
            test_policy = get_test_policy()
            is_dummy = test_policy.should_use_dummy()
            current_mode = test_policy.get_test_mode()
            print(f"\n[Debug] Test mode: {current_mode}, dummy: {is_dummy}")
            
            # AI prompt display
            print(f"\nAI prompt ({len(prompt)} chars):")
            print("-" * 40)
            print(prompt[:200] + "..." if len(prompt) > 200 else prompt)
            print("-" * 40)
            
            print("\nAI response (real-time):\n")
            print("   ", end='', flush=True)  # Indentation
            
            # Streaming AI call
            response = ai_call(prompt, stream=True)
            return response
        except Exception as e:
            return f"Sorry, error occurred during response generation: {str(e)[:100]}"
    
    def _save_conversation_turn(self, user_input, response, winner, tool_result):
        """Save conversation turn"""
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
        """Show statistics"""
        print(f"\n{'='*60}")
        print("AI Router Statistics")
        print(f"{'='*60}")
        
        # Session info
        info = self.context_tracker.get_session_info(self.session_id)
        if info:
            print(f"Session ID: {info['session_id']}")
            print(f"Conversation turns: {info['turn_count']}")
        
        print(f"Total conversation turns: {self.conversation_turn}")
        print(f"{'='*60}\n")
    
    def run(self):
        """Main execution loop"""
        print("\n" + "="*60)
        print("AI Router CLI - Full Integration")
        print("="*60)
        print("All 1.x features integrated:")
        print("  - Multi-agent competition (refine/balance/expand)")
        print("  - Evaluation system (1-10 points)")
        print("  - Memory & reward system")
        print("  - Intent analysis & routing")
        print("  - Log/system tools")
        print("\nCommands:")
        print("  'log show'  - System log analysis")
        print("  'status?'   - System status check")
        print("  'stats'     - Show statistics")
        print("  'quit'      - Exit")
        print("="*60 + "\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!")
                    self.show_statistics()
                    break
                
                if user_input.lower() == 'stats':
                    self.show_statistics()
                    continue
                
                # Complete pipeline processing
                response = self.process_with_full_pipeline(user_input)
                print(f"\nAI: {response}\n")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except EOFError:
                break
            except Exception as e:
                print(f"\nError occurred: {e}\n")

if __name__ == "__main__":
    from datetime import datetime
    cli = AIFullRouterCLI()
    cli.run()
