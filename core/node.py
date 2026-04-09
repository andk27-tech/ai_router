import random

def ai_call(text):
    variants = [
        f"processed: {text}",
        f"analyzed: {text}",
        f"refined: {text}",
    ]
    return random.choice(variants)
