def keyword_bonus(text):
    keywords = {
        "ai": 2,
        "산업": 1,
        "자동화": 1,
        "판단": 1,
        "시스템": 1,
    }

    score = 0
    t = text.lower()

    for k, v in keywords.items():
        if k in t:
            score += v

    return score
