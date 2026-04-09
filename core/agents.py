from core.evaluator import evaluate
from core.policy import get_weight
from core.policy_evolve import next_generation

def run_agents(fn, input_text):
    results = []

    policies = next_generation("expand")  # 🔥 seed

    for p in policies:
        out = fn(input_text, p)

        score, reason = evaluate(out, p)
        score = score * get_weight(p.split("_")[0])

        results.append({
            "policy": p,
            "output": out,
            "score": score,
            "reason": reason
        })

    winner = max(results, key=lambda x: x["score"])

    return winner, results
