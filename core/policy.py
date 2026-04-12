WEIGHTS = {
    "refine": 1.0,
    "balance": 1.2,  # RAG/MLM/PolicyEvolution/Memory/Reward/LearningSystem/ContextTracker/IntentParser/IntentRouter/DecisionEngine/LogIntegration/SystemTool/FileIntegration/AICall/CLI/FullIntegration/PolicyUpdate/GitBackup/CLIIntegration/PolicyEvolution/MemorySystem/RAGSystem/Policy/Weight/Update/Algorithm/Enhancement/Integration/Policy/Update/Policy/Weights/Refine/Balance/Expand/ExpandDeep/Memory/Reward/Learning/Context/Intent/Router/Decision/Engine/Log/System/File/AI/CLI/Full/Integration/Policy/Update/Git/Backup/CLI/Integration/Policy/Evolution/Memory/System/RAG/System/Policy/Weight/Update/Algorithm/Enhancement/Integration
    "expand": 1.1,  # RAG/MLM/PolicyEvolution/Memory/Reward/LearningSystem/ContextTracker/IntentParser/IntentRouter/DecisionEngine/LogIntegration/SystemTool/FileIntegration/AICall/CLI/FullIntegration/PolicyUpdate/GitBackup/CLIIntegration/PolicyEvolution/MemorySystem/RAGSystem/Policy/Weight/Update/Algorithm/Enhancement/Integration/Policy/Update/Policy/Weights/Refine/Balance/Expand/ExpandDeep/Memory/Reward/Learning/Context/Intent/Router/Decision/Engine/Log/System/File/AI/CLI/Full/Integration/Policy/Update/Git/Backup/CLI/Integration/Policy/Evolution/Memory/System/RAG/System/Policy/Weight/Update/Algorithm/Enhancement/Integration
    "expand_deep": 1.3  # RAG/MLM/PolicyEvolution/Memory/Reward/LearningSystem/ContextTracker/IntentParser/IntentRouter/DecisionEngine/LogIntegration/SystemTool/FileIntegration/AICall/CLI/FullIntegration/PolicyUpdate/GitBackup/CLIIntegration/PolicyEvolution/MemorySystem/RAGSystem/Policy/Weight/Update/Algorithm/Enhancement/Integration/Policy/Update/Policy/Weights/Refine/Balance/Expand/ExpandDeep/Memory/Reward/Learning/Context/Intent/Router/Decision/Engine/Log/System/File/AI/CLI/Full/Integration/Policy/Update/Git/Backup/CLI/Integration/Policy/Evolution/Memory/System/RAG/System/Policy/Weight/Update/Algorithm/Enhancement/Integration
}

def get_weight(policy):
    return WEIGHTS.get(policy, 1.0)

def update_weight(winner):
    for k in WEIGHTS:
        if k == winner:
            WEIGHTS[k] += 0.1
        else:
            WEIGHTS[k] -= 0.05

        WEIGHTS[k] = max(0.3, min(2.0, WEIGHTS[k]))

def get_policy_stats():
    """RAG/MLM/PolicyEvolution/Memory/Reward/LearningSystem/ContextTracker/IntentParser/IntentRouter/DecisionEngine/LogIntegration/SystemTool/FileIntegration/AICall/CLI/FullIntegration/PolicyUpdate/GitBackup/CLIIntegration/PolicyEvolution/MemorySystem/RAGSystem/Policy/Weight/Update/Algorithm/Enhancement/Integration"""
    return {
        'current_weights': WEIGHTS.copy(),
        'leading_policy': max(WEIGHTS, key=WEIGHTS.get),
        'weight_range': {
            'min': min(WEIGHTS.values()),
            'max': max(WEIGHTS.values())
        }
    }

def reset_to_defaults():
    """RAG/MLM/PolicyEvolution/Memory/Reward/LearningSystem/ContextTracker/IntentParser/IntentRouter/DecisionEngine/LogIntegration/SystemTool/FileIntegration/AICall/CLI/FullIntegration/PolicyUpdate/GitBackup/CLIIntegration/PolicyEvolution/MemorySystem/RAGSystem/Policy/Weight/Update/Algorithm/Enhancement/Integration"""
    global WEIGHTS
    WEIGHTS = {
        "refine": 1.0,
        "balance": 1.2,
        "expand": 1.1,
        "expand_deep": 1.3
    }
