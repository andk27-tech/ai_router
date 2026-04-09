import random

BASE = ["refine", "balance", "expand"]

def generate_policies(seed):
    # 🔥 안정형: 기존 구조 유지 + 약간 변형만 허용
    return list(set([
        seed,
        random.choice(BASE),
        seed  # fallback 유지
    ]))
