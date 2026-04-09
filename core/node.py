from core.ai import ai_call

def run_node(node: dict, input_data: str) -> str:
    prompt = f"""
[STRICT TASK]
반드시 입력을 변환해서 결과만 출력해라.
설명 금지. 원문 금지. 지시문 금지.

TASK:
{node["prompt"].format(input=input_data)}
""".strip()

    output = ai_call(prompt)

    if "[AI RESPONSE]" in output:
        output = output.split("[AI RESPONSE]")[-1].strip()

    return output.strip()
