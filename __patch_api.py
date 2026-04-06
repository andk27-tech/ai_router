from core.rag import search

def wrap(data):
    ctx = search(data)

    return {
        "status": "success",
        "type": "chat",
        "result": ctx
    }
