import os
# 로컬 AI 모드 설정 (더미 모드가 아닌 실제 AI 사용) - import 전에 설정!
os.environ['AI_ROUTER_TEST_MODE'] = 'local_ai'

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
from core.rag import search, build_full_graph
from core.ai import ai_call
from core.memory import save as memory_save, get_success, get_recent
from core.reward import calc_reward
from core.policy_evolve import next_generation

app = FastAPI(title="AI Router API", version="1.0")

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse('static/index.html')


@app.get("/api")
async def api_info():
    return {
        "message": "AI Router API",
        "version": "1.0",
        "endpoints": {
            "/": "Chat UI",
            "/api/run": "POST - AI processing endpoint",
            "/docs": "API documentation (Swagger UI)"
        }
    }


import asyncio

async def ai_call_async(prompt: str, policy: str = "balance", timeout: int = 10) -> str:
    """비동기 AI 호출 with 타임아웃"""
    try:
        # asyncio.to_thread로 동기 함수를 비동기로 실행
        result = await asyncio.wait_for(
            asyncio.to_thread(ai_call, prompt, policy),
            timeout=timeout
        )
        return result
    except asyncio.TimeoutError:
        return "[AI 응답 시간 초과 - 잠시 후 다시 시도해주세요]"
    except Exception as e:
        return f"[AI 오류: {str(e)}]"


@app.post("/api/run")
async def run(req: Request):
    body = await req.json()
    data = body.get("data", "")

    # Build simplified prompt for faster response
    ctx = search(data)
    # Limit context to 200 characters for speed
    limited_ctx = ctx[:200] if len(ctx) > 200 else ctx
    prompt = f"User: {data}\n{limited_ctx}"
    
    # 15s timeout (reduced from 30s)
    result = await ai_call_async(prompt, policy="balance", timeout=15)
    
    # 학습 시스템: 결과 저장
    memory_save({
        "input": data,
        "output": result,
        "score": 10,  # 기본 점수
        "policy": "balance",
        "timestamp": __import__('datetime').datetime.now().isoformat()
    })
    
    # 성공 사례 확인
    success_cases = get_success()
    
    # 정책 진화 준비 (다음 요청 시 사용)
    if success_cases:
        latest_winner = success_cases[-1].get("policy", "balance")
        next_policies = next_generation(latest_winner)

    return {
        "status": "success",
        "type": "chat",
        "result": result,
        "learning": {
            "memory_saved": True,
            "success_cases": len(success_cases),
            "latest_policy": "balance"
        }
    }


@app.get("/api/memory")
async def get_memory():
    """메모리 상태 확인 엔드포인트"""
    recent = get_recent(5)
    success = get_success()
    
    return {
        "status": "success",
        "recent_entries": len(recent),
        "success_cases": len(success),
        "recent_data": recent[-3:] if recent else []
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
