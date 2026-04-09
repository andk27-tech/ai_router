from core.evaluator import evaluate
from core.memory import save, get_success
from core.policy import evolve_policy

def apply_memory(text):
    success = get_success()

    if not success:
        return text, "refine"

    best = success[-1]
    return f"{best['output']} >> {text}", evolve_policy()

def improve_input(text, reason, attempt, strategy):
    if strategy == "expand":
        return f"{text} | 확장{attempt} 깊게"
    if strategy == "balance":
        return f"{text} | 균형{attempt}"
    return f"{text} | 정리{attempt}"

def run_node(fn, input_data, threshold=10, max_retry=3):
    attempt = 0
    current_input = input_data

    while attempt < max_retry:
        current_input, strategy = apply_memory(current_input)

        output = fn(current_input)
        score, reason = evaluate(output)

        print(f"[try {attempt}] policy={strategy} input={current_input} score={score} reason={reason} -> {output}")

        save({
            "input": current_input,
            "output": output,
            "score": score,
            "reason": reason
        })

        if score >= threshold:
            return output

        attempt += 1
        current_input = improve_input(current_input, reason, attempt, strategy)

    return output
