#!/usr/bin/env python3
"""
Semantic Parser Test Script
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.semantic import SemanticParser, extract_semantic_meaning

def test_semantic_parser():
    print("=== Semantic Parser Test ===\n")
    
    parser = SemanticParser()
    
    # Test 1: Meaning extraction
    print("1. Meaning Extraction Test:")
    
    test_texts = [
        "Python 함수를 작성해서 데이터베이스에 연결하고 사용자 인증을 구현해줘",
        "이 코드에서 긴급한 보안 문제를 수정해야 해",
        "FastAPI 클래스를 만들고 테스트 코드도 작성해줘"
    ]
    
    for text in test_texts:
        meaning = parser.extract_meaning(text)
        print(f"\n   Text: {text[:40]}...")
        print(f"   → Concepts: {len(meaning.concepts)}")
        for c in meaning.concepts[:3]:
            print(f"      - {c.name} ({c.concept_type}, conf={c.confidence:.2f})")
        print(f"   → Relations: {len(meaning.relations)}")
        print(f"   → Intent: {meaning.intent}")
        print(f"   → Sentiment: {meaning.sentiment}")
        print(f"   → Urgency: {meaning.urgency:.2f}")
    
    # Test 2: Semantic similarity
    print("\n2. Semantic Similarity Test:")
    
    pairs = [
        ("Python 코드 작성해줘", "Python 함수 만들어줘"),
        ("데이터베이스 연결", "서버 설정"),
        ("보안 수정", "보안 고쳐줘")
    ]
    
    for text1, text2 in pairs:
        sim = parser.calculate_semantic_similarity(text1, text2)
        print(f"   '{text1}' vs '{text2}': {sim:.2f}")
    
    # Test 3: Knowledge graph
    print("\n3. Knowledge Graph Test:")
    
    texts = [
        "함수는 코드의 일부입니다",
        "클래스는 객체를 생성합니다",
        "모듈은 함수와 클래스를 포함합니다",
        "데이터베이스는 데이터를 저장합니다",
        "API는 서버와 통신합니다"
    ]
    
    graph = parser.build_knowledge_graph(texts)
    print(f"   Nodes: {graph['concept_count']}")
    print(f"   Edges: {graph['relation_count']}")
    print(f"   Statistics: {graph['statistics']}")
    
    # Test 4: Concept identification
    print("\n4. Concept Identification Test:")
    
    text = "사용자 인증 함수를 작성하고 데이터베이스에 연결하며 테스트를 수행합니다"
    concepts = parser.identify_concepts(text)
    
    print(f"   Text: {text}")
    print(f"   Found {len(concepts)} concepts:")
    for c in concepts:
        print(f"   - {c.name} ({c.concept_type}): {c.confidence:.2f}")
    
    # Test 5: Relationship mapping
    print("\n5. Relationship Mapping Test:")
    
    relations = parser.map_relationships(text, concepts)
    print(f"   Found {len(relations)} relations:")
    for r in relations[:5]:
        print(f"   - {r.source} --{r.relation_type}--> {r.target} (strength={r.strength:.2f})")
    
    # Test 6: Sentiment analysis
    print("\n6. Sentiment Analysis Test:")
    
    sentiment_texts = [
        "이 코드는 훌륭하고 성능이 우수합니다",
        "심각한 오류가 있고 문제가 많습니다",
        "긴급! 서버가 다운되었습니다",
        "그냥 테스트입니다"
    ]
    
    for text in sentiment_texts:
        sentiment = parser.analyze_sentiment(text)
        urgency = parser.calculate_urgency(text)
        print(f"   '{text[:30]}...' → {sentiment} (urgency: {urgency:.2f})")
    
    # Test 7: Convenience function
    print("\n7. Convenience Function Test:")
    
    result = extract_semantic_meaning("Python API를 구현하고 데이터베이스와 연결해줘")
    print(f"   Extracted meaning:")
    print(f"   - Concepts: {len(result['concepts'])}")
    print(f"   - Relations: {len(result['relations'])}")
    print(f"   - Intent: {result['intent']}")
    print(f"   - Sentiment: {result['sentiment']}")
    
    print("\n=== Semantic Parser Test Complete ===")

if __name__ == "__main__":
    test_semantic_parser()
