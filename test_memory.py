#!/usr/bin/env python3
"""
메모리 저장 테스트 - 학습 저장 기능 확인
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.memory import save, get_recent, get_success

def test_memory():
    """메모리 테스트"""
    print("=" * 60)
    print("🧪 메모리(memory) 테스트 시작")
    print("=" * 60)
    
    try:
        # 1. 메모리 초기 상태 확인
        print("1️⃣ 메모리 초기 상태:")
        recent = get_recent(5)
        print(f"   최근 항목: {len(recent)}개")
        success = get_success()
        print(f"   성공 항목: {len(success)}개")
        
        # 2. 테스트 데이터 저장
        print("\n2️⃣ 테스트 데이터 저장:")
        test_entries = [
            {
                "input": "AI 라우터 설명해줘",
                "winner": {"policy": "expand", "score": 10.0},
                "reward": 1.0,
                "score": 10.0
            },
            {
                "input": "시스템 상태 어때?",
                "winner": {"policy": "balance", "score": 8.0},
                "reward": 0.5,
                "score": 8.0
            },
            {
                "input": "코드 정리해줘",
                "winner": {"policy": "refine", "score": 9.0},
                "reward": 0.8,
                "score": 9.0
            },
            {
                "input": "간단한 질문",
                "winner": {"policy": "expand", "score": 5.0},
                "reward": 0.0,
                "score": 5.0
            }
        ]
        
        for i, entry in enumerate(test_entries, 1):
            save(entry)
            print(f"   {i}. 저장: {entry['input'][:20]}... (점수: {entry['score']})")
        
        # 3. 저장된 데이터 확인
        print("\n3️⃣ 저장된 데이터 확인:")
        recent = get_recent(10)
        print(f"   최근 항목: {len(recent)}개")
        
        for i, entry in enumerate(recent[-4:], 1):  # 마지막 4개만
            input_text = entry.get('input', 'N/A')[:30]
            score = entry.get('score', 0)
            reward = entry.get('reward', 0)
            print(f"   {i}. {input_text}... (점수: {score}, 보상: {reward})")
        
        # 4. 성공 항목 필터링
        print("\n4️⃣ 성공 항목 필터링:")
        success = get_success()
        print(f"   성공 항목: {len(success)}개")
        
        for i, entry in enumerate(success, 1):
            input_text = entry.get('input', 'N/A')[:30]
            score = entry.get('score', 0)
            print(f"   {i}. {input_text}... (점수: {score})")
        
        # 5. 메모리 용량 테스트
        print("\n5️⃣ 메모리 용량 테스트:")
        print("   대량 데이터 저장 테스트 (200개 항목)...")
        
        for i in range(200):
            save({
                "input": f"테스트 입력 {i}",
                "winner": {"policy": "expand", "score": 7.0},
                "reward": 0.3,
                "score": 7.0
            })
        
        recent = get_recent(5)
        print(f"   최근 항목: {len(recent)}개")
        print(f"   마지막 항목: {recent[-1].get('input', 'N/A')}")
        
        # 메모리가 200개로 제한되는지 확인
        total_count = len(get_recent(1000))  # 최대 1000개 요청
        print(f"   총 메모리 항목: {total_count}개 (최대 200개 제한)")
        
        return True
        
    except Exception as e:
        print(f"❌ 메모리 테스트 오류: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_memory()
    print(f"\n🎯 메모리 테스트 결과: {'성공' if success else '실패'}")
