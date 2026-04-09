import os
from core.memory import MEMORY
import core.config as config

HISTORY = []

def should_modify():
    if len(MEMORY) < 5:
        return False

    recent = MEMORY[-5:]
    avg = sum(m["score"] for m in recent) / len(recent)

    return avg > 11  # 진입 조건

def propose_patch():
    recent = MEMORY[-5:]
    avg = sum(m["score"] for m in recent) / len(recent)

    if avg > 13:
        return 1.3
    if avg < 9:
        return 0.8
    return 1.0

def apply_patch():
    global HISTORY

    new_weight = config.EXPAND_WEIGHT * propose_patch()

    # 🔥 clamp (안전장치)
    new_weight = max(config.MIN_WEIGHT, min(config.MAX_WEIGHT, new_weight))

    HISTORY.append(config.EXPAND_WEIGHT)

    config.EXPAND_WEIGHT = new_weight

    print(f"[SELF-MOD] EXPAND_WEIGHT -> {new_weight}")

def rollback():
    global HISTORY

    if HISTORY:
        config.EXPAND_WEIGHT = HISTORY.pop()
        print("[ROLLBACK] restored previous weight")
