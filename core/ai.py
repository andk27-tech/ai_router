import subprocess

MODEL = "qwen2.5-coder:3b"

def ai_call(prompt: str) -> str:
    result = subprocess.run(
        ["ollama", "run", MODEL],
        input=prompt,
        text=True,
        capture_output=True
    )

    return result.stdout.strip()
