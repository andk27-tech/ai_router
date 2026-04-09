from core.ai import ai_call

def score_output(text: str) -> int:
    prompt = f"""
0~10 점수만 숫자로 줘라.
내용 품질 기준: 정확성, 간결성

{text}
""".strip()

    res = ai_call(prompt)

    for c in res:
        if c.isdigit():
            return int(c)

    return 5
