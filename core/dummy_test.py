from core.evaluator import score_output

TEST_CASES = [
    "AI는 산업을 변화시킨다",
    "자동화 시스템은 판단을 돕는다",
    "짧음",
    "AI AI AI AI AI",
    "산업 자동화 판단 시스템이 핵심이다",
]

for i, t in enumerate(TEST_CASES):
    score = score_output(t)
    print(f"[{i}] TEXT: {t}")
    print(f"[{i}] SCORE: {score}")
    print("-" * 40)
