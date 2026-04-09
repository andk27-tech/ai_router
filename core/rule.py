def quality_score(text, base_score):
    words = text.split()
    penalty = 0

    # 반복 패턴 (강하게)
    if words:
        max_repeat = max(words.count(w) for w in set(words))
        if max_repeat >= 3:
            penalty += 15

    # 다양성 부족
    if len(set(words)) <= 2:
        penalty += 10

    # 문자 다양성 부족
    if len(set(text.replace(" ", ""))) < 4:
        penalty += 8

    return max(base_score - penalty, 0)
