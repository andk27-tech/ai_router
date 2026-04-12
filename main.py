import os
# 로컬 AI 모드 설정 (더미 모드가 아닌 실제 AI 사용) - import 전에 설정!
os.environ['AI_ROUTER_TEST_MODE'] = 'local_ai'

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
from core.rag import search, build_full_graph
from core.ai import ai_call

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

    graph = build_full_graph()
    ctx = search(data)

    # Build prompt for AI
    prompt = f"Input: {data}\nContext: {ctx}\nCall Graph: {graph}"
    
    # 비동기 호출 with 30초 타임아웃 (Ollama가 느림)
    result = await ai_call_async(prompt, policy="balance", timeout=30)

    return {
        "status": "success",
        "type": "chat",
        "result": result
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
