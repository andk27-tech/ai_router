#!/usr/bin/env python3
"""
AI Router CLI Chat
터미널에서 대화하면서 로그/상태 확인
"""

import sys
import requests
import json

API_BASE = "http://localhost:8000"

def chat():
    print("=" * 60)
    print("🤖 AI Router CLI Chat")
    print("=" * 60)
    print("명령어:")
    print("  '로그 보여줘' - 시스템 로그 확인")
    print("  '상태 어때?'  - 시스템 상태 확인")
    print("  'health'      - 건강 상태 빠른 확인")
    print("  'quit'        - 종료")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'health':
                # 빠른 건강 체크
                try:
                    resp = requests.get(f"{API_BASE}/api/health", timeout=5)
                    data = resp.json()
                    print(f"\n🤖 AI: 시스템 상태: {data.get('overall_status', 'unknown')}")
                    print(f"   CPU: {data.get('cpu_percent', 0)}%")
                    print(f"   Memory: {data.get('memory_percent', 0)}%")
                except Exception as e:
                    print(f"\n❌ 오류: {e}")
                continue
            
            # 일반 대화/로그/상태 쿼리
            try:
                resp = requests.post(
                    f"{API_BASE}/api/run",
                    json={"data": user_input},
                    timeout=30
                )
                data = resp.json()
                
                print(f"\n🤖 AI: {data.get('result', '응답 없음')}")
                
                # 추가 데이터 표시
                if data.get('type') == 'log_check' and 'data' in data:
                    print(f"   [에러 수: {data['data'].get('error_count', 0)}]")
                elif data.get('type') == 'system_status' and 'data' in data:
                    d = data['data']
                    print(f"   [CPU: {d.get('cpu_percent', 0)}% | Memory: {d.get('memory_percent', 0)}% | Disk: {d.get('disk_percent', 0)}%]")
                    
            except requests.exceptions.ConnectionError:
                print(f"\n❌ 서버 연결 실패. 서버가 실행 중인지 확인하세요:")
                print(f"   python3 main_with_logs.py")
            except Exception as e:
                print(f"\n❌ 오류: {e}")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except EOFError:
            break

if __name__ == "__main__":
    chat()
