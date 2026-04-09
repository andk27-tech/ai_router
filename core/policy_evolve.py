import random

def evolve(policy):
    mutations = ["v2", "fast", "deep", "plus", "x"]

    if "_" in policy:
        base = policy.split("_")[0]
    else:
        base = policy

    return f"{base}_{random.choice(mutations)}"

def next_generation(winner_policy):
    return [
        winner_policy,
        evolve(winner_policy),
        random.choice(["refine", "balance", "expand"])
    ]
