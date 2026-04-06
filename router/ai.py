import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5-coder:3b"

def ask_llm(prompt: str):
    try:
        res = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        })
        return res.json().get("response", "")
    except Exception as e:
        return f"LLM error: {str(e)}"
