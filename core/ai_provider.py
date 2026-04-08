import os

def mock_llm(prompt):
    return f"[MOCK] {prompt}"


def openai_llm(prompt):
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return res.choices[0].message.content

    except Exception as e:
        return None


def local_llm(prompt):
    # 나중에 Ollama 붙일 자리
    return None


def ai_call(prompt):
    # 1순위 local
    r = local_llm(prompt)
    if r:
        return r

    # 2순위 openai
    r = openai_llm(prompt)
    if r:
        return r

    # 3순위 mock
    return mock_llm(prompt)
