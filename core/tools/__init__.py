"""
툴 레이어 패키지
AI 에이전트가 사용할 수 있는 다양한 툴 제공
"""

from .file_tool import get_file_tool, FileTool

# 사용 가능한 툴 레지스트리
AVAILABLE_TOOLS = {
    'file': get_file_tool(),
}

def get_tool(tool_name: str):
    """툴 이름으로 툴 인스턴스 반환"""
    return AVAILABLE_TOOLS.get(tool_name)

def list_available_tools():
    """사용 가능한 툴 목록 반환"""
    return list(AVAILABLE_TOOLS.keys())

def get_tool_info(tool_name: str = None):
    """툴 정보 반환"""
    if tool_name:
        tool = get_tool(tool_name)
        return tool.get_tool_info() if tool else None
    else:
        return {name: tool.get_tool_info() for name, tool in AVAILABLE_TOOLS.items()}
