from fastapi import FastAPI, Request
from core.rag import search, build_full_graph
from core.ai import ask_llm

app = FastAPI()


@app.post("/api/run")
async def run(req: Request):
    body = await req.json()
    data = body.get("data", "")

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
