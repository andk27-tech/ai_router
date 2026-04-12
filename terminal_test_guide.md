# 터미널 테스트 가이드

## 🚀 빠른 테스트 방법

### 1. 기본 CLI 테스트
```bash
# AI 라우터 디렉토리로 이동
cd /home/lks/ai_router

# 더미 모드 1로 테스트 (가장 빠름)
python3 cli_full_integration.py --dummy-1

# 더미 모드 2로 테스트
python3 cli_full_integration.py --dummy-2

# 로컬 AI 모드 (Ollama 필요)
python3 cli_full_integration.py --local-ai
```

### 2. 개별 컴포넌트 테스트
```bash
# 에이전트 테스트
python3 test_agents.py

# 전체 파이프라인 테스트
python3 test_full_pipeline.py

# 개선된 시스템 테스트
python3 test_improved_system.py
```

### 3. 대화형 테스트 예시
```
👤 You: AI 라우터 프로젝트의 핵심 기능을 설명해줘

🤖 AI: [expand 정책으로 응답]
AI 라우터 프로젝트의 확장성 기능은 다음과 같습니다:
🏗️ **아키텍처 확장성**
• 모듈형 설계: 각 컴포넌트 독립적 확장
• 플러그인 시스템: 새로운 기능 동적 추가
...

👤 You: 시스템 상태가 어떤지 알려줘

🤖 AI: [balance 정책으로 응답]
AI 라우터 프로젝트는 다음과 같은 균형을 추구합니다:
⚖️ **성능 vs 안정성**
- 빠른 응답 속도와 안정적인 시스템 운영
...
```

## 🎯 테스트 시나리오

### 시나리오 1: 정책 다양성 확인
```bash
python3 cli_full_integration.py --dummy-1
```
테스트할 입력들:
- "AI 라우터 프로젝트의 핵심 기능을 설명해줘" (expand 기대)
- "시스템 상태가 어떤지 알려줘" (balance 기대)  
- "코드를 정리하고 구조화해줘" (refine 기대)
- "프로젝트를 깊이 있게 분석해줘" (expand_deep 기대)

### 시나리오 2: 동점자 처리 확인
```bash
python3 test_winner_selection.py
```
동점자가 발생하는 경우 처리 로직 확인

### 시나리오 3: 전체 파이프라인 테스트
```bash
python3 test_full_pipeline.py
```
다양한 입력에 대한 전체 시스템 동작 확인

## 🔍 디버깅 팁

### 로그 확인
```bash
# 디버그 모드로 실행
python3 cli_full_integration.py --dummy-1 2>&1 | grep -E "(DEBUG|TIE|WINNER)"
```

### 정책 생성 확인
```bash
python3 test_current_policies.py
```

### 개선된 평가 시스템 테스트
```bash
python3 test_evaluator.py
```

## 📝 직접 테스트 스크립트

간단한 테스트를 위해 직접 파이썬 스크립트 실행:
```bash
python3 -c "
from core.agents import run_agents
from core.ai import ai_call
from core.test_policy import set_test_mode, TestMode
set_test_mode(TestMode.DUMMY_1)

winner, results = run_agents(ai_call, '테스트 입력')
print(f'승자: {winner[\"policy\"]} ({winner[\"score\"]:.1f}점)')
for r in results:
    print(f'{r[\"policy\"]}: {r[\"score\"]:.1f}점')
"
```

## 🎮 재미있는 테스트

### 1. 정책 경쟁 관찰
```bash
python3 cli_full_integration.py --dummy-1
# 같은 입력을 여러 번 해보며 어떤 정책이 이기는지 관찰
```

### 2. 동점자 상황 만들기
```bash
python3 test_winner_selection.py
# 의도적으로 동점자를 만들어 처리 로직 확인
```

### 3. 성능 비교
```bash
# 더미 모드 vs 로컬 AI 모드 속도 비교
time python3 cli_full_integration.py --dummy-1
time python3 cli_full_integration.py --local-ai
```

## ⚠️ 주의사항

1. **로컬 AI 모드**는 Ollama가 설치되어 있어야 함
2. **더미 모드**는 항상 동일한 응답 패턴을 보임
3. **메모리**는 세션 동안만 유지됨
4. **가중치**는 테스트 중에 계속 업데이트됨

## 🔧 문제 해결

### 응답이 이상하다면?
```bash
# 캐시된 가중치 초기화
python3 -c "from core.policy import WEIGHTS; WEIGHTS.clear()"

# 테스트 정책 초기화  
python3 -c "from core.test_policy import test_policy; test_policy.test_count = 0"
```

### 에러가 발생하면?
```bash
# 파이썬 경로 확인
python3 -c "import sys; print(sys.path)"

# 모듈 임포트 테스트
python3 -c "from core.agents import run_agents; print('OK')"
```

즐겁게 테스트해보세요! 🎉
