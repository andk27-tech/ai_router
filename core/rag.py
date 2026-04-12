import os
import ast

IGNORE_DIRS = {
    "venv",
    ".venv",
    "__pycache__",
    "site-packages",
}

def search(query: str):
    """RAG 검색 - 코드베이스에서 관련 정보 찾기"""
    graph = build_full_graph()
    results = []
    
    query_lower = query.lower()
    query_keywords = query_lower.split()
    
    # 파일명과 함수 검색
    for file_path, functions in graph.items():
        file_name = os.path.basename(file_path).lower()
        
        # 파일명 매칭
        if any(keyword in file_name for keyword in query_keywords):
            results.append(f"File: {os.path.basename(file_path)} ({len(functions)} functions)")
        
        # 함수명 매칭
        matching_functions = [func for func in functions 
                             if any(keyword in func.lower() for keyword in query_keywords)]
        
        if matching_functions:
            results.append(f"Functions in {os.path.basename(file_path)}: {', '.join(matching_functions[:3])}")
    
    return {"query": query, "result": results[:5]}  # 상위 5개 결과만


def build_full_graph():
    graph = {}

    root = os.getcwd()

    for dirpath, dirnames, filenames in os.walk(root):

        # 🚫 디렉토리 필터링
        dirnames[:] = [
            d for d in dirnames
            if d not in IGNORE_DIRS and not d.startswith(".")
        ]

        for f in filenames:
            if not f.endswith(".py"):
                continue

            path = os.path.join(dirpath, f)

            try:
                with open(path, "r", encoding="utf-8") as fp:
                    code = fp.read()
            except:
                continue

            graph[path] = extract_api_flow(code)

    return graph


def extract_api_flow(code: str):
    class V(ast.NodeVisitor):
        def __init__(self):
            self.calls = []

        def visit_Call(self, node):
            if hasattr(node.func, "id"):
                self.calls.append(node.func.id)
            elif hasattr(node.func, "attr"):
                self.calls.append(node.func.attr)
            self.generic_visit(node)

    try:
        tree = ast.parse(code)
    except:
        return []

    v = V()
    v.visit(tree)

    return list(set(v.calls))
