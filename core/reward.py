def calc_reward(score, threshold=10):
    if score >= threshold + 2:
        return 1.0
    if score >= threshold:
        return 0.5
    if score >= 8:
        return 0.1
    return -1.0
