from core.memory import save
from core.self_mod import should_modify, apply_patch
from core.reward import calc_reward
from core.agents import run_agents
from core.policy import update_weight

def run_node(fn, input_data, threshold=8, max_retry=3):

    if should_modify():
        apply_patch()

    attempt = 0
    current_input = input_data

    while attempt < max_retry:

        winner, all_results = run_agents(fn, current_input)

        score = winner["score"]
        reward = calc_reward(score, threshold)

        print(f"[WINNER] {winner['policy']} score={score} reward={reward}")

        # 🔥 safe learning
        update_weight(winner["policy"])

        save({
            "input": current_input,
            "winner": winner,
            "reward": reward
        })

        if reward > 0:
            return winner["output"]

        current_input = current_input + " | retry boost"
        attempt += 1

    return winner["output"]
