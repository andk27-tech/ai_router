#!/usr/bin/env python3
"""
AI Router with Log Integration
로그 및 시스템 상태 확인 기능이 통합된 AI Router
"""

from fastapi import FastAPI, Request
from core.rag import search, build_full_graph
from core.ai import ask_llm, ai_call
from core.intent import IntentParser, IntentType
from core.tools.log_integration_extended import SystemLogIntegration
from core.tools.system_tool import SystemTool
import uvicorn

app = FastAPI(title="AI Router with Log Support")

# 전역 객체 (초기화)
intent_parser = IntentParser()
log_integration = SystemLogIntegration()
system_tool = SystemTool()

# 권한 설정 (초기화 시)
log_integration.grant_permissions(
    agent_id='ai_router',
    log_types=['syslog', 'daemon', 'kern'],
    read_only=True,
    max_lines=200
)


def is_log_related_query(text: str) -> bool:
    """로그 관련 쿼리인지 확인"""
    log_keywords = ['로그', 'log', 'syslog', '에러', 'error', '로그인', '로그아웃',
                   '로그파일', '로그확인', '로그보여', '로그분석']
    return any(kw in text.lower() for kw in log_keywords)


def is_system_status_query(text: str) -> bool:
    """시스템 상태 관련 쿼리인지 확인"""
    status_keywords = ['상태', 'status', '시스템', 'system', 'cpu', '메모리', 'memory',
                      '디스크', 'disk', '프로세스', 'process', '부하', 'load',
                      '상태는', '어때', '확인해', '상태확인', '건강', 'health']
    return any(kw in text.lower() for kw in status_keywords)


async def handle_log_query(user_input: str) -> dict:
    """로그 관련 쿼리 처리"""
    # 로그 수집
    log_result = log_integration.get_system_log_access(
        agent_id='ai_router',
        log_types=['syslog'],
        lines=30
    )
    
    # 에러 분석
    error_result = log_integration.analyze_system_errors(
        agent_id='ai_router',
        hours=1,
        severity='error'
    )
    
    # 데이터 준비
    log_data = {
        'syslog_accessed': log_result.get('success', False),
        'recent_errors': error_result.get('total_errors', 0),
        'error_types': error_result.get('error_types', {}),
        'system_status': 'healthy' if error_result.get('total_errors', 0) < 5 else 'warning',
        'log_preview': log_result.get('logs_accessed', {}).get('syslog', {}).get('content_preview', '')[:300]
    }
    
    # AI 프롬프트
    prompt = f"""사용자가 시스템 로그를 확인하고 있습니다: "{user_input}"

수집된 정보:
- syslog 접근: {'성공' if log_data['syslog_accessed'] else '실패'}
- 최근 1시간 에러: {log_data['recent_errors']}개
- 에러 유형: {log_data['error_types']}
- 상태: {log_data['system_status']}

로그 미리보기:
{log_data['log_preview']}

사용자에게 친절하게 한국어로 설명해주세요."""
    
    try:
        ai_response = ai_call(prompt)
        return {
            "status": "success",
            "type": "log_check",
            "result": ai_response,
            "data": {
                "error_count": log_data['recent_errors'],
                "system_status": log_data['system_status']
            }
        }
    except Exception as e:
        return {
            "status": "success",
            "type": "log_check",
            "result": f"로그 분석 결과: 최근 에러 {log_data['recent_errors']}개, 상태: {log_data['system_status']}",
            "error": str(e)
        }


async def handle_system_status_query(user_input: str) -> dict:
    """시스템 상태 쿼리 처리"""
    # 시스템 정보 수집
    cpu_info = system_tool.get_cpu_info()
    memory_info = system_tool.get_memory_info()
    disk_info = system_tool.get_disk_info()
    
    # 데이터 준비
    cpu_data = cpu_info.get('cpu', {}) if cpu_info.get('success') else {}
    memory_data = memory_info.get('memory', {}) if memory_info.get('success') else {}
    disk_data = disk_info.get('root_partition', {}) if disk_info.get('success') else {}
    
    status_data = {
        'cpu_percent': cpu_data.get('percent', 0),
        'cpu_status': cpu_data.get('status', 'unknown'),
        'memory_percent': memory_data.get('percent_used', 0),
        'memory_available': memory_data.get('available_gb', 0),
        'disk_percent': disk_data.get('percent', 0),
        'disk_status': disk_data.get('status', 'unknown')
    }
    
    # AI 프롬프트
    prompt = f"""사용자가 시스템 상태를 묻고 있습니다: "{user_input}"

현재 시스템 상태:
- CPU 사용량: {status_data['cpu_percent']}% (상태: {status_data['cpu_status']})
- 메모리 사용량: {status_data['memory_percent']}% (사용 가능: {status_data['memory_available']} GB)
- 디스크 사용량: {status_data['disk_percent']}% (상태: {status_data['disk_status']})

이 정보를 바탕으로 시스템 상태를 한국어로 친절하게 설명해주세요.
문제가 있으면 해결책도 제안해주세요."""
    
    try:
        ai_response = ai_call(prompt)
        return {
            "status": "success",
            "type": "system_status",
            "result": ai_response,
            "data": status_data
        }
    except Exception as e:
        # AI 실패시 기본 응답
        status_summary = f"""시스템 상태:
- CPU: {status_data['cpu_percent']}% ({status_data['cpu_status']})
- 메모리: {status_data['memory_percent']}% 사용 중 ({status_data['memory_available']} GB 사용 가능)
- 디스크: {status_data['disk_percent']}% ({status_data['disk_status']})"""
        
        return {
            "status": "success",
            "type": "system_status",
            "result": status_summary,
            "error": str(e)
        }


@app.post("/api/run")
async def run(req: Request):
    """메인 API 엔드포인트 - 로그 및 상태 쿼리 지원"""
    body = await req.json()
    data = body.get("data", "")
    
    # 로그 관련 쿼리 감지
    if is_log_related_query(data):
        return await handle_log_query(data)
    
    # 시스템 상태 쿼리 감지
    if is_system_status_query(data):
        return await handle_system_status_query(data)
    
    # 일반 쿼리 - 기존 AI Router 로직
    graph = build_full_graph()
    ctx = search(data)
    
    result = ask_llm({
        "input": data,
        "context": ctx,
        "call_graph": graph
    })
    
    return {
        "status": "success",
        "type": "chat",
        "result": result
    }


@app.get("/api/health")
async def health_check():
    """시스템 건강 상태 API"""
    summary = system_tool.get_system_summary()
    
    if summary.get('success'):
        return {
            "status": "success",
            "overall_status": summary['overall_status'],
            "cpu_percent": summary['cpu'].get('percent', 0),
            "memory_percent": summary['memory'].get('percent_used', 0),
            "disk_percent": summary['disk'].get('percent', 0),
            "safe_to_execute": summary['overall_status'] == 'healthy'
        }
    
    return {
        "status": "error",
        "message": "시스템 상태를 확인할 수 없습니다"
    }


@app.post("/api/logs")
async def get_logs(req: Request):
    """로그 조회 API"""
    body = await req.json()
    log_type = body.get("log_type", "syslog")
    lines = body.get("lines", 50)
    
    result = log_integration.get_system_log_access(
        agent_id='ai_router',
        log_types=[log_type],
        lines=lines
    )
    
    return result


if __name__ == "__main__":
    print("🚀 AI Router with Log Support 시작...")
    print("📋 API 엔드포인트:")
    print("   - POST /api/run    : 일반 대화 + 로그/상태 쿼리")
    print("   - GET  /api/health : 시스템 건강 상태")
    print("   - POST /api/logs   : 로그 조회")
    print("\n💡 사용 예시:")
    print('   curl -X POST http://localhost:8000/api/run -H "Content-Type: application/json" -d \'{"data": "로그 보여줘"}\'')
    print('   curl -X POST http://localhost:8000/api/run -H "Content-Type: application/json" -d \'{"data": "시스템 상태 어때?"}\'')
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
