#!/usr/bin/env python3
"""
AI Router CLI Chat - Standalone Version
서버 없이 직접 실행 (로컬 AI + 로그/시스템 통합)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.intent import IntentParser
from core.intent_integration import IntentBasedRouter
from core.tools.log_integration_extended import SystemLogIntegration
from core.tools.system_tool import SystemTool
from core.ai import ai_call
from core.test_policy import set_test_mode, TestMode

class AIChatBot:
    def __init__(self):
        # 실제 AI 사용하도록 설정
        set_test_mode(TestMode.LOCAL_AI)
        
        self.intent_parser = IntentParser()
        self.router = IntentBasedRouter()
        self.log_integration = SystemLogIntegration()
        self.system_tool = SystemTool()
        
        # 권한 설정
        self.log_integration.grant_permissions(
            agent_id='cli_user',
            log_types=['syslog', 'daemon', 'kern'],
            read_only=True,
            max_lines=100
        )
    
    def is_log_query(self, text):
        keywords = ['로그', 'log', 'syslog', '에러', 'error', '로그확인', '로그보여', '로그분석']
        return any(kw in text.lower() for kw in keywords)
    
    def is_status_query(self, text):
        keywords = ['상태', 'status', '시스템', 'system', 'cpu', '메모리', 'memory', '디스크', 'disk',
                   '프로세스', 'process', '부하', 'load', '어때', '확인', '건강', 'health']
        return any(kw in text.lower() for kw in keywords)
    
    def handle_log_query(self, user_input):
        print("   📝 로그 정보 수집 중...")
        
        # 로그 수집
        result = self.log_integration.get_system_log_access(
            agent_id='cli_user',
            log_types=['syslog'],
            lines=30
        )
        
        errors = self.log_integration.analyze_system_errors(
            agent_id='cli_user',
            hours=1,
            severity='error'
        )
        
        # AI 프롬프트
        log_data = {
            'accessed': result.get('success', False),
            'errors': errors.get('total_errors', 0),
            'types': errors.get('error_types', {}),
            'preview': result.get('logs_accessed', {}).get('syslog', {}).get('content_preview', '')[:300]
        }
        
        prompt = f"""사용자가 시스템 로그를 확인하고 있습니다: "{user_input}"

수집된 정보:
- syslog 접근: {'성공' if log_data['accessed'] else '실패'}
- 최근 1시간 에러: {log_data['errors']}개
- 에러 유형: {log_data['types']}

로그 미리보기:
{log_data['preview']}

한국어로 친절하게 설명해주세요."""
        
        try:
            print("   🤖 AI 분석 중...")
            response = ai_call(prompt)
            return response
        except Exception as e:
            return f"로그 분석 결과: 최근 에러 {log_data['errors']}개\n(오류: {e})"
    
    def handle_status_query(self, user_input):
        print("   🖥️ 시스템 정보 수집 중...")
        
        # 시스템 정보
        cpu = self.system_tool.get_cpu_info()
        memory = self.system_tool.get_memory_info()
        disk = self.system_tool.get_disk_info()
        
        cpu_data = cpu.get('cpu', {}) if cpu.get('success') else {}
        memory_data = memory.get('memory', {}) if memory.get('success') else {}
        disk_data = disk.get('root_partition', {}) if disk.get('success') else {}
        
        # AI 프롬프트
        status = {
            'cpu_percent': cpu_data.get('percent', 0),
            'cpu_status': cpu_data.get('status', 'unknown'),
            'memory_percent': memory_data.get('percent_used', 0),
            'memory_available': memory_data.get('available_gb', 0),
            'disk_percent': disk_data.get('percent', 0),
            'disk_status': disk_data.get('status', 'unknown')
        }
        
        prompt = f"""사용자가 시스템 상태를 묻고 있습니다: "{user_input}"

현재 시스템 상태:
- CPU 사용량: {status['cpu_percent']}% (상태: {status['cpu_status']})
- 메모리 사용량: {status['memory_percent']}% (사용 가능: {status['memory_available']} GB)
- 디스크 사용량: {status['disk_percent']}% (상태: {status['disk_status']})

한국어로 친절하게 설명하고, 문제가 있으면 해결책도 제안해주세요."""
        
        try:
            print("   🤖 AI 분석 중...")
            response = ai_call(prompt)
            return response
        except Exception as e:
            return f"""시스템 상태:
- CPU: {status['cpu_percent']}% ({status['cpu_status']})
- Memory: {status['memory_percent']}% ({status['memory_available']} GB 사용 가능)
- Disk: {status['disk_percent']}% ({status['disk_status']})
(오류: {e})"""
    
    def handle_chat(self, user_input):
        # 의도 파악
        intent = self.intent_parser.parse(user_input)
        
        # 로그 쿼리
        if self.is_log_query(user_input):
            return self.handle_log_query(user_input)
        
        # 상태 쿼리
        if self.is_status_query(user_input):
            return self.handle_status_query(user_input)
        
        # 일반 대화
        try:
            print("   🤖 AI 응답 생성 중...")
            response = ai_call(f"사용자: {user_input}\n한국어로 답변해주세요.")
            return response
        except Exception as e:
            return f"죄송합니다. 응답 생성 중 오류가 발생했습니다: {e}"
    
    def run(self):
        print("=" * 60)
        print("🤖 AI Router CLI Chat (Standalone)")
        print("=" * 60)
        print("💡 로그/상태 확인:")
        print("   '로그 보여줘', 'syslog 확인', '에러 있어?'")
        print("   '상태 어때?', 'CPU 확인', '메모리 상태'")
        print("   'quit' - 종료")
        print("=" * 60)
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 안녕히 가세요!")
                    break
                
                response = self.handle_chat(user_input)
                print(f"\n🤖 AI: {response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 안녕히 가세요!")
                break
            except EOFError:
                break

if __name__ == "__main__":
    bot = AIChatBot()
    bot.run()
