from fastapi import FastAPI, Request
import uvicorn
from core.rag import search, build_full_graph
from core.ai import ai_call

app = FastAPI(title="AI Router API", version="1.0")


@app.get("/")
async def root():
    return {
        "message": "AI Router API",
        "version": "1.0",
        "endpoints": {
            "/api/run": "POST - AI processing endpoint",
            "/docs": "API documentation (Swagger UI)",
            "/redoc": "API documentation (ReDoc)"
        }
    }


@app.post("/api/run")
async def run(req: Request):
    body = await req.json()
    data = body.get("data", "")

    graph = build_full_graph()
    ctx = search(data)

    # Build prompt for AI
    prompt = f"Input: {data}\nContext: {ctx}\nCall Graph: {graph}"
    result = ai_call(prompt, policy="balance")

    return {
        "status": "success",
        "type": "chat",
        "result": result
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
